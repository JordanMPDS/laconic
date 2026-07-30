#!/usr/bin/env python3
"""Generation pass: run every (case, arm, model, rep) and append to a snapshot.

Resumable: a key already in the snapshot is skipped, so an interrupted
two-hour run continues instead of restarting. Failures are recorded with
ok=False and excluded from every statistic - a failed call silently scored as
a very short answer would read as excellent compression.
"""
import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
SNAPSHOT = ROOT / "evals" / "snapshots" / "results.json"

WORD_COMPRESSION = (
    "Answer concisely. Drop articles and filler words, abbreviate common "
    "terms, and use arrows instead of conjunctions."
)

# The laconic entry is a placeholder here and is replaced at runtime with the
# real hook output, so the benchmark cannot drift from what ships.
ARMS = {
    "baseline": None,
    "terse-control": "Answer concisely.",
    "word-compression": WORD_COMPRESSION,
    "laconic": "",
}


def laconic_rules(root, level):
    """Build the treatment arm from the real hook, never from a copy."""
    tmp = tempfile.mkdtemp()
    try:
        (Path(tmp) / ".laconic-level").write_text(level)
        env = dict(os.environ, CLAUDE_CONFIG_DIR=tmp)
        env.pop("LACONIC_DEFAULT", None)
        out = subprocess.run(
            ["bash", str(root / "hooks" / "laconic.sh"), "start"],
            capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL,
        )
        return out.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def parse_cli_json(raw):
    blank = {"ok": False, "text": "", "output_tokens": 0, "input_tokens": 0,
             "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
             "total_cost_usd": 0.0, "duration_ms": 0, "num_turns": 0}
    try:
        d = json.loads(raw)
    except (ValueError, TypeError):
        return blank
    if not isinstance(d, dict) or d.get("is_error"):
        return blank
    u = d.get("usage") or {}
    return {
        "ok": True,
        "text": d.get("result", ""),
        "output_tokens": u.get("output_tokens", 0),
        "input_tokens": u.get("input_tokens", 0),
        "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
        "total_cost_usd": d.get("total_cost_usd", 0.0),
        "duration_ms": d.get("duration_ms", 0),
        "num_turns": d.get("num_turns", 0),
    }


def run_key(case, arm, model, rep):
    return (case, arm, model, rep)


def completed_keys(snap):
    return set(run_key(r["case"], r["arm"], r["model"], r["rep"])
               for r in snap.get("runs", []) if r.get("ok"))


def usable(runs):
    return [r for r in runs if r.get("ok")]


def new_snapshot(reps, models, level, rules_cksum, arms):
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "claude_cli_version": _cli_version(),
            "git_commit": _git_commit(),
            "laconic_level": level,
            "rules_cksum": rules_cksum,
            "reps": reps,
            "models": models,
        },
        "arms": {k: {"system_prompt": v} for k, v in arms.items()},
        "runs": [],
    }


def _cli_version():
    try:
        return subprocess.run(["claude", "--version"], capture_output=True,
                              text=True).stdout.strip()
    except OSError:
        return "unknown"


def _git_commit():
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return "unknown"


def load_snapshot(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None


def save_snapshot(path, snap):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n")


def call(claude_bin, model, prompt, system_prompt, cwd):
    cmd = [claude_bin, "-p", "--model", model, "--output-format", "json"]
    if system_prompt:
        cmd += ["--append-system-prompt", system_prompt]
    env = dict(os.environ, CLAUDE_CODE_SAFE_MODE="1")
    env.pop("LACONIC_DEFAULT", None)
    try:
        out = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                             cwd=cwd, env=env, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return {"ok": False}
    if out.returncode != 0:
        return {"ok": False}
    return parse_cli_json(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="full")
    ap.add_argument("--models", default="haiku,sonnet")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--cases", default="*")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--claude-bin", default="claude")
    args = ap.parse_args()

    # Resolve claude-bin to absolute path so it works with subprocess cwd changes
    claude_bin = str(Path(args.claude_bin).resolve())

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    arm_names = [a.strip() for a in args.arms.split(",") if a.strip()]
    cases = sorted(d for d in CASES.iterdir()
                   if (d / "prompt.md").exists() and fnmatch.fnmatch(d.name, args.cases))
    if not cases:
        sys.exit("no cases matched: %s" % args.cases)

    arms = dict(ARMS)
    arms["laconic"] = laconic_rules(ROOT, args.level)
    if not arms["laconic"].strip():
        sys.exit("hook produced no rules for level %s" % args.level)
    cksum = str(zlib.crc32(arms["laconic"].encode()))

    snap = load_snapshot(args.snapshot)
    if snap is None:
        snap = new_snapshot(args.reps, models, args.level, cksum, arms)
    elif snap["metadata"].get("rules_cksum") != cksum:
        sys.exit("snapshot was generated from different rules (cksum %s vs %s); "
                 "move it aside before regenerating"
                 % (snap["metadata"].get("rules_cksum"), cksum))
    done = completed_keys(snap)

    total = len(cases) * len(arm_names) * len(models) * args.reps
    n = 0
    for rep in range(args.reps):
        for case_dir in cases:
            case = case_dir.name
            prompt = (case_dir / "prompt.md").read_text()
            for model in models:
                for arm in arm_names:  # innermost: arms sampled at adjacent moments
                    n += 1
                    if run_key(case, arm, model, rep) in done:
                        continue
                    scratch = tempfile.mkdtemp()
                    fixture = case_dir / "fixture"
                    if fixture.is_dir():
                        shutil.copytree(fixture, scratch, dirs_exist_ok=True)
                    res = call(claude_bin, model, prompt, arms[arm], scratch)
                    shutil.rmtree(scratch, ignore_errors=True)
                    if not res.get("ok"):  # one retry before recording a failure
                        scratch = tempfile.mkdtemp()
                        if fixture.is_dir():
                            shutil.copytree(fixture, scratch, dirs_exist_ok=True)
                        res = call(claude_bin, model, prompt, arms[arm], scratch)
                        shutil.rmtree(scratch, ignore_errors=True)
                    res.update({"case": case, "arm": arm, "model": model, "rep": rep})
                    snap["runs"].append(res)
                    save_snapshot(args.snapshot, snap)
                    print("[%d/%d] %-14s %-16s %-7s rep%d %s"
                          % (n, total, case, arm, model, rep,
                             "ok" if res.get("ok") else "FAILED"))

    bad = len([r for r in snap["runs"] if not r.get("ok")])
    print("\nwrote %s (%d runs, %d failed)" % (args.snapshot, len(snap["runs"]), bad))


if __name__ == "__main__":
    main()
