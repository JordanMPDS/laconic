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


def resolve_claude_bin(arg):
    """Bare command names resolve via PATH; path-like arguments resolve to
    absolute, because call() runs with cwd set to a scratch dir."""
    if os.sep in arg or (os.altsep and os.altsep in arg):
        return str(Path(arg).resolve())
    return shutil.which(arg) or arg


def claude_bin_usable(claude_bin):
    """The fail-fast guard's condition, factored out so tests exercise the
    real thing instead of re-deriving it. Rejects missing paths, directories,
    and non-executable files - shutil.which() already handles all three."""
    return bool(shutil.which(claude_bin))


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
    result = d.get("result")
    if not isinstance(result, str):
        return blank
    u = d.get("usage") or {}
    return {
        "ok": True,
        "text": result,
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


def dedupe(runs):
    """One record per (arm, case, model, rep), a successful one winning.

    A resume re-runs the keys that failed, and before #61 it appended the
    retry beside the failure instead of replacing it: round-08.json carries
    740 records for 700 cells, every duplicate a (failed, succeeded) pair.
    usable() filters failures so no published number ever moved, but the
    invariant is worth holding rather than relying on - len(snap["runs"]) is
    otherwise a lie, and any consumer reading runs directly double-counts.

    Order is preserved by first appearance, so a repaired file still reads in
    generation order.
    """
    at, out = {}, []
    for r in runs:
        key = run_key(r.get("case"), r.get("arm"), r.get("model"), r.get("rep"))
        if key not in at:
            at[key] = len(out)
            out.append(r)
        elif not out[at[key]].get("ok"):
            out[at[key]] = r
    return out


def carry_arms(snap, source, keep_arms):
    """Copy every usable run whose arm is not being regenerated.

    A rule edit changes only the treatment arm - no control carries rules in
    its system prompt - so regenerating the controls each round pays three
    times over for runs that cannot have moved. The provenance stamp names the
    source and its rules_cksum, so a snapshot built this way carries its own
    mixed-snapshot disclosure instead of relying on someone remembering it.
    """
    carried = [dict(r) for r in usable(source.get("runs", []))
               if r["arm"] not in keep_arms]
    snap["runs"].extend(carried)
    snap["metadata"]["carried_arms_from"] = {
        "path": source.get("__path", ""),
        "rules_cksum": source.get("metadata", {}).get("rules_cksum"),
        "arms": sorted(set(r["arm"] for r in carried)),
    }
    return snap


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_snapshot(reps, models, level, rules_cksum, arms, claude_bin="claude"):
    arms_dict = {}
    for k, v in arms.items():
        entry = {"system_prompt": v}
        if k == "laconic":
            entry["source"] = "hooks/laconic.sh start @ %s" % level
        arms_dict[k] = entry
    return {
        "metadata": {
            "generated_at": _now(),
            "claude_cli_version": _cli_version(claude_bin),
            "git_commit": _git_commit(),
            "laconic_level": level,
            "rules_cksum": rules_cksum,
            "reps": reps,
            "models": models,
        },
        "arms": arms_dict,
        "runs": [],
    }


def _cli_version(claude_bin):
    try:
        out = subprocess.run([claude_bin, "--version"], capture_output=True,
                             text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return out.stdout.strip() if out.returncode == 0 else "unknown"


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
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n")
    os.replace(str(tmp), str(p))


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
    ap.add_argument("--cases-dir", default=str(CASES),
                    help="case directory to glob; evals/holdout for the reserved set")
    ap.add_argument("--carry-arms-from",
                    help="snapshot to copy the arms this run is not regenerating from")
    args = ap.parse_args()

    claude_bin = resolve_claude_bin(args.claude_bin)
    if not claude_bin_usable(claude_bin):
        sys.exit("claude binary not found or not executable: %s "
                 "(set --claude-bin or fix PATH)" % args.claude_bin)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    arm_names = [a.strip() for a in args.arms.split(",") if a.strip()]
    bad_arms = [a for a in arm_names if a not in ARMS]
    if bad_arms:
        sys.exit("unknown arm(s): %s (valid: %s)" % (", ".join(bad_arms), ", ".join(ARMS)))
    cases_dir = Path(args.cases_dir)
    if not cases_dir.is_dir():
        sys.exit("no such case directory: %s" % args.cases_dir)
    cases = sorted(d for d in cases_dir.iterdir()
                   if (d / "prompt.md").exists() and fnmatch.fnmatch(d.name, args.cases))
    if not cases:
        sys.exit("no cases matched: %s" % args.cases)

    # Resolved once, then stamped onto every run below. The snapshot-level
    # stamp is written when the file is created and never again, so a round
    # assembled into a pre-seeded file inherits that file's provenance:
    # round-12.json carries round-01-n10-v2.json's CLI and date for runs made
    # three days later on a different CLI (#80). A per-run stamp cannot be
    # inherited, and it can represent a round that legitimately spans hours.
    cli_version = _cli_version(claude_bin)

    arms = dict(ARMS)
    arms["laconic"] = laconic_rules(ROOT, args.level)
    if not arms["laconic"].strip():
        sys.exit("hook produced no rules for level %s" % args.level)
    cksum = str(zlib.crc32(arms["laconic"].encode()))

    snap = load_snapshot(args.snapshot)
    if snap is None:
        snap = new_snapshot(args.reps, models, args.level, cksum, arms, claude_bin)
        if args.carry_arms_from:
            source = load_snapshot(args.carry_arms_from)
            if source is None:
                sys.exit("no snapshot to carry arms from: %s" % args.carry_arms_from)
            source["__path"] = args.carry_arms_from
            carry_arms(snap, source, arm_names)
    elif snap["metadata"].get("rules_cksum") != cksum:
        sys.exit("snapshot was generated from different rules (cksum %s vs %s); "
                 "move it aside before regenerating"
                 % (snap["metadata"].get("rules_cksum"), cksum))
    # Collapse duplicates a pre-#61 resume appended, so a file written by the
    # old code repairs itself the first time it is touched.
    dropped = len(snap["runs"]) - len(dedupe(snap["runs"]))
    if dropped:
        snap["runs"] = dedupe(snap["runs"])
        save_snapshot(args.snapshot, snap)
        print("repaired %d duplicate run record(s) left by an earlier resume "
              "(#61); no usable run was affected" % dropped)
    at = {run_key(r.get("case"), r.get("arm"), r.get("model"), r.get("rep")): i
          for i, r in enumerate(snap["runs"])}
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
                    res.update({"case": case, "arm": arm, "model": model, "rep": rep,
                                "generated_at": _now(),
                                "claude_cli_version": cli_version})
                    # Replace the failed record for this cell rather than
                    # appending beside it (#61): a resume is a second attempt
                    # at one cell, not a second cell.
                    key = run_key(case, arm, model, rep)
                    if key in at:
                        snap["runs"][at[key]] = res
                    else:
                        at[key] = len(snap["runs"])
                        snap["runs"].append(res)
                    save_snapshot(args.snapshot, snap)
                    print("[%d/%d] %-14s %-16s %-7s rep%d %s"
                          % (n, total, case, arm, model, rep,
                             "ok" if res.get("ok") else "FAILED"))

    bad = len([r for r in snap["runs"] if not r.get("ok")])
    print("\nwrote %s (%d runs, %d failed)" % (args.snapshot, len(snap["runs"]), bad))


if __name__ == "__main__":
    main()
