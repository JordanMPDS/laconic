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
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concurrency  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
SNAPSHOT = ROOT / "evals" / "snapshots" / "results.json"

# Identifies this invocation, stamped onto every run it writes (#120). Rounds
# 16 and 17 were generated one case per process at 5-way concurrency and the
# shard files were merged, so the merged snapshot describes a regime no single
# process could produce - and nothing in it said so, leaving the fact to be
# reconstructed from timestamps years later. Two ids inside one arm and day is
# two processes, stated rather than inferred. Per-run rather than per-snapshot
# for the same reason claude_cli_version is (#80): a snapshot-level stamp is
# written once at creation and is then inherited by every later pass that
# appends to the file, including passes a different process made.
GENERATOR = "%s-%d" % (
    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), os.getpid())

WORD_COMPRESSION = (
    "Answer concisely. Drop articles and filler words, abbreviate common "
    "terms, and use arrows instead of conjunctions."
)

# Arms delivered by a native Claude Code output style rather than by an
# appended system prompt. A style replaces part of the default system prompt
# instead of adding to it, so --append-system-prompt cannot reproduce one and
# a hand-copied transcription of the style text would be a different
# treatment wearing the same label. These arms carry no system_prompt and are
# passed to the CLI through --settings, so the arm measures what Claude Code
# actually ships. "Concise" is the built-in style added in CLI 2.1.x, and it
# is the closest thing to a native competitor this plugin has.
ARM_OUTPUT_STYLES = {"concise-style": "Concise"}

# The laconic entry is a placeholder here and is replaced at runtime with the
# real hook output, so the benchmark cannot drift from what ships.
ARMS = {
    "baseline": None,
    "terse-control": "Answer concisely.",
    "word-compression": WORD_COMPRESSION,
    "concise-style": None,
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


def require_claude_bin(arg):
    """Resolve the CLI path or exit with the same message everywhere.

    run.py, judge.py, prefer.py and subagent.py each opened main() with a
    byte-identical resolve/test/exit block. One copy, so the message and the
    resolution rule cannot drift apart.
    """
    claude_bin = resolve_claude_bin(arg)
    if not claude_bin_usable(claude_bin):
        sys.exit("claude binary not found or not executable: %s "
                 "(set --claude-bin or fix PATH)" % arg)
    return claude_bin


def parse_cli_json(raw):
    blank = {"ok": False, "text": "", "output_tokens": 0, "input_tokens": 0,
             "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
             "total_cost_usd": 0.0, "duration_ms": 0, "num_turns": 0,
             "session_id": None}
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
        # Lifted for #166: a second turn resumes this session by id. Also
        # provenance - a record now says which CLI session produced it.
        "session_id": d.get("session_id"),
    }


# A case may ask more than one question in sequence. #136 and #60's drift half
# both describe a failure that only exists across turns - the model defending a
# claim it made itself - and a fixture read cold cannot construct that, because
# a document is evidence to cite rather than a position to defend. Round 32
# measured the single-turn approximation and it does not reproduce the shape.
#
# An HTML comment, so prompt.md still renders as prose on GitHub and the marker
# is invisible in the rendered case. cases_cksum already hashes prompt.md whole,
# so adding a delimiter to an existing case invalidates its resumes correctly
# with no extra work.
TURN_DELIMITER = re.compile(r"^[ \t]*<!--[ \t]*turn[ \t]*-->[ \t]*$", re.M)


def split_turns(prompt):
    """prompt.md as a list of turns. No delimiter is one turn, unchanged.

    Empty segments are dropped rather than sent, so a trailing delimiter or a
    doubled one is a formatting slip and not a wasted CLI call.
    """
    parts = [s.strip() for s in TURN_DELIMITER.split(prompt)]
    return [s for s in parts if s] or [""]


def merge_turns(records):
    """One run record from a turn sequence.

    Top-level fields describe the **graded** turn, which is the last one, so
    judge.py, report.py and metrics.py all read the final answer without
    knowing this function exists. `total_cost_usd` and `duration_ms` sum
    instead, because those are resource accounting and undercounting them
    would misreport what a round spent; the summed duration is also the right
    window for concurrency.py, whose turns run back to back.

    A one-turn sequence returns the record untouched - no `turns`, no
    `turn_count` - so single-turn rounds stay byte-identical to every round
    generated before #166 and no stored comparison shifts. Absence of the
    field means one turn.
    """
    if not records or not all(r.get("ok") for r in records):
        return {"ok": False}
    merged = dict(records[-1])
    if len(records) == 1:
        return merged
    merged["total_cost_usd"] = sum(r.get("total_cost_usd") or 0.0 for r in records)
    merged["duration_ms"] = sum(r.get("duration_ms") or 0 for r in records)
    merged["turn_count"] = len(records)
    merged["turns"] = records
    return merged


def parse_cli_stream(raw):
    """Parse --output-format stream-json: the flat record, plus tool names.

    num_turns counts agentic loop iterations, so a file read and a file edit
    are the same integer (#49). The stream emits every assistant message as
    its own event with its tool_use blocks intact, and that is the only place
    the CLI says which tools a response actually invoked.

    The stream closes with the same object --output-format json returns
    whole, so the record shape stays defined in one place - parse_cli_json -
    and what is added here is the single field the flat format cannot carry.

    Two properties of the real stream this depends on. The result event is
    not necessarily the last line, because Claude Code emits a task_summary
    after it, so decoding the last line would record every run in a round as
    failed. And a line that is not a JSON object is not a reason to throw the
    run away; a stream with no result event at all is, because that is a run
    killed mid-transcript and it parses as the same failure a malformed flat
    payload does.

    Tools are reported even for a failed run. usable() filters those out of
    every statistic so this cannot reach a score, and it is what separates a
    cell that died after four tool calls from one that never started.
    """
    tools, result = [], ""
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        if d.get("type") == "result":
            result = line
        elif d.get("type") == "assistant":
            msg = d.get("message")
            blocks = msg.get("content") if isinstance(msg, dict) else None
            for b in blocks if isinstance(blocks, list) else []:
                if (isinstance(b, dict) and b.get("type") == "tool_use"
                        and isinstance(b.get("name"), str)):
                    tools.append(b["name"])
    return dict(parse_cli_json(result), tools=tools)


# What the shipped plugin actually sends on a later turn. hooks/hooks.json wires
# SessionStart to `laconic.sh start`, which emits the full slice once, and
# UserPromptSubmit to `laconic.sh remind`, which emits this one line before every
# prompt. Kept in step with the string in hooks/laconic.sh.
REMINDER = ("LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal "
            "grammar. Cut content, not words.")


def call_turns(claude_bin, model, turns, system_prompt, cwd, output_style=None,
               delivery="repeat", level=None):
    """Run a turn sequence in one CLI session and return one merged record.

    Turn 1 opens the session; each later turn resumes it by the id the previous
    turn reported. A turn that fails, or that comes back without a session id
    while turns remain, abandons the sequence - a half-finished conversation is
    not a shorter conversation, and the caller's retry starts a fresh one.

    `delivery` decides what a later turn carries, and the two modes are not the
    same treatment:

    - `repeat`, the default and what rounds 33 to 38 used, re-appends the whole
      rule slice as a system prompt on every turn.
    - `plugin` reproduces what a real session gets: the slice once on turn 1,
      then only the one-line reminder, prepended to the prompt the way
      UserPromptSubmit's additionalContext reaches the model.

    The default is `repeat` so no stored snapshot shifts, but it is the less
    faithful of the two. The plugin sends the full text once; the harness has
    been sending it five times. That matters for any multi-turn finding about
    persistence: rounds 33, 35 and 36 measured accumulated own output inflating
    an answer by about 35% *despite* the rules being re-asserted every turn, so
    that figure bounds the effect from below rather than estimating it. And a
    persistence clause of the kind [#60] asks for cannot be tested under
    `repeat` at all, because `repeat` already over-delivers persistence.

    [#60]: https://github.com/JordanMPDS/laconic/issues/60
    """
    records = []
    session = None
    for i, text in enumerate(turns):
        if i and not session:
            return {"ok": False}
        if delivery == "plugin" and i:
            sp = None
            if system_prompt and level:
                text = (REMINDER % level) + "\n\n" + text
        else:
            sp = system_prompt
        res = call(claude_bin, model, text, sp, cwd, output_style,
                   resume=session)
        records.append(res)
        if not res.get("ok"):
            return {"ok": False}
        session = res.get("session_id")
    merged = merge_turns(records)
    if merged.get("ok") and len(records) > 1:
        merged["turn_delivery"] = delivery
    return merged


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

    An arm the source does not have is copied as nothing, which is silent: the
    round then reports on the arms it happens to hold rather than the arms the
    benchmark defines, and the reader has no way to tell an arm that was left
    out from an arm that was never generated. concise-style is the first arm
    newer than the snapshots it would be carried from, and it will not be the
    last, so missing_arms records the gap and main() prints it.
    """
    carried = [dict(r) for r in usable(source.get("runs", []))
               if r["arm"] not in keep_arms]
    snap["runs"].extend(carried)
    carried_arms = sorted(set(r["arm"] for r in carried))
    snap["metadata"]["carried_arms_from"] = {
        "path": source.get("__path", ""),
        "rules_cksum": source.get("metadata", {}).get("rules_cksum"),
        "arms": carried_arms,
        "missing_arms": sorted(set(ARMS) - set(keep_arms) - set(carried_arms)),
    }
    return snap


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_snapshot(reps, models, level, rules_cksum, arms, claude_bin="claude",
                 cases_ck=None, cases_dir=None, concurrency_declared=1):
    arms_dict = {}
    for k, v in arms.items():
        entry = {"system_prompt": v}
        if k == "laconic":
            entry["source"] = "hooks/laconic.sh start @ %s" % level
        if k in ARM_OUTPUT_STYLES:
            entry["output_style"] = ARM_OUTPUT_STYLES[k]
        arms_dict[k] = entry
    return {
        "metadata": {
            "generated_at": _now(),
            "claude_cli_version": _cli_version(claude_bin),
            "git_commit": _git_commit(),
            "git_dirty": _git_dirty(),
            "cases_cksum": cases_ck,
            "cases_dir": cases_dir,
            "concurrency_declared": concurrency_declared,
            "laconic_level": level,
            "max_runs_in_flight": 0,
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


def match_case(name, patterns):
    """True when `name` matches any of a comma-separated list of globs.

    A single glob covers a scope like `design-*`, and every round up to 28 had
    one. A scope that is not a prefix family does not: round 29 targets
    `walkthrough` and the three `verdict-*` cases, which no one glob selects and
    which cannot be split across two invocations either - cases_cksum covers the
    cases the invocation names, so a second invocation into the same snapshot is
    refused by the #69 guard. Comma is the separator --target-cases already
    uses, so the two flags read alike.
    """
    return any(fnmatch.fnmatch(name, p.strip()) for p in patterns.split(","))


def cases_cksum(cases_dir, names):
    """A checksum over the case material a round was actually produced from.

    Every harness reads the working tree while it runs - prompt.md and the
    fixture in run.py, prompt.md and expect.json in judge.py, prompt.md in
    prefer.py - and a round takes hours. Editing a case, or switching branches,
    mid-pass silently produces one round graded against two different sets of
    criteria, with nothing in the snapshot recording that it happened. The
    rules text has been guarded by rules_cksum since the beginning; the cases
    were not guarded at all (#69).

    Hashes prompt.md, expect.json and every file under fixture/, for the cases
    in this round only, so an unrelated case being added or edited does not
    invalidate a resume. Directory names are included, so deleting a fixture
    file is caught as well as editing one.
    """
    out = {}
    for name in sorted(names):
        d = Path(cases_dir) / name
        entry = {}
        for rel in ("prompt.md", "expect.json"):
            f = d / rel
            if f.is_file():
                entry[rel] = zlib.crc32(f.read_bytes())
        fixture = d / "fixture"
        if fixture.is_dir():
            entry["fixture"] = {
                str(f.relative_to(fixture)): zlib.crc32(f.read_bytes())
                for f in sorted(fixture.rglob("*")) if f.is_file()}
        out[name] = entry
    return str(zlib.crc32(json.dumps(out, sort_keys=True).encode()))


def _git_dirty():
    """Whether the tree had uncommitted changes when the pass started.

    Recorded rather than refused: the loop's own workflow edits rules/laconic.md
    and runs before committing in some orders, and a hard refusal would block
    legitimate work. What it buys is that a snapshot produced from an
    uncommitted tree says so, instead of carrying a git_commit that does not
    describe what ran.
    """
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                             capture_output=True, text=True)
    except OSError:
        return None
    return bool(out.stdout.strip()) if out.returncode == 0 else None


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


def call(claude_bin, model, prompt, system_prompt, cwd, output_style=None,
         resume=None):
    # stream-json rather than json because only the stream carries the
    # tool_use blocks (#142); --verbose is not optional, the CLI refuses the
    # combination under --print without it. The terminal result event is the
    # json payload verbatim, so nothing about the stored record changes
    # except the tool list that is added beside it.
    cmd = [claude_bin, "-p", "--model", model,
           "--output-format", "stream-json", "--verbose"]
    # #166: a later turn continues the session the previous one opened, which
    # is what puts the model's own prior answer in its context rather than a
    # transcript of it. Resume by id rather than --continue, so the turn is
    # bound to the session it names and not to whatever ran last in this cwd.
    if resume:
        cmd += ["--resume", resume]
    if system_prompt:
        cmd += ["--append-system-prompt", system_prompt]
    if output_style:
        cmd += ["--settings", json.dumps({"outputStyle": output_style})]
    env = dict(os.environ, CLAUDE_CODE_SAFE_MODE="1")
    env.pop("LACONIC_DEFAULT", None)
    try:
        out = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                             cwd=cwd, env=env, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return {"ok": False}
    if out.returncode != 0:
        return {"ok": False}
    return parse_cli_stream(out.stdout)


STYLE_PROBE = (
    'Reply with ONLY the exact line from your system prompt that ends with '
    'the words "Style Active", or the word NONE if no such line exists.'
)


def output_style_reaches_model(claude_bin, model, style):
    """Whether --settings actually delivers `style` to the model.

    An unrecognised style name is not an error: the CLI drops it and answers
    from the default system prompt, verified against 2.1.238. Safe mode also
    disables custom output styles, and the built-ins surviving
    CLAUDE_CODE_SAFE_MODE=1 is an observed behavior rather than a documented
    guarantee. Either way the arm would become a second copy of baseline
    wearing a treatment label, and the round would publish "the native style
    changes nothing" as its finding. One probe call before a multi-hour pass
    is the cheapest way to not spend the pass measuring baseline twice.

    Every built-in style opens its block with "# <Name> Style Active", so the
    probe asks for that line back and checks the name it got.
    """
    scratch = tempfile.mkdtemp()
    try:
        res = call(claude_bin, model, STYLE_PROBE, None, scratch,
                   output_style=style)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return bool(res.get("ok")) and ("# %s Style Active" % style) in res["text"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="full")
    ap.add_argument("--turn-delivery", choices=("repeat", "plugin"),
                    default="repeat",
                    help="what a later turn of a multi-turn case carries. "
                         "'repeat' (default) re-appends the whole rule slice "
                         "every turn, which is what rounds 33 to 38 used and "
                         "is what every stored snapshot holds. 'plugin' "
                         "reproduces the shipped hook wiring instead: the slice "
                         "once on turn 1, then only the one-line reminder, "
                         "which is what a real session gets. 'repeat' is the "
                         "default so no stored comparison shifts, not because "
                         "it is the faithful one")
    ap.add_argument("--models", default="haiku,sonnet")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--cases", default="*")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--cases-dir", default=str(CASES),
                    help="case directory to glob; evals/holdout for the reserved set")
    ap.add_argument("--allow-case-change", action="store_true",
                    help="resume a snapshot whose case material has changed since "
                         "it was started. Records the override in the metadata; "
                         "see #69 before using it")
    ap.add_argument("--carry-arms-from",
                    help="snapshot to copy the arms this run is not regenerating from")
    ap.add_argument("--concurrency", type=int, default=1,
                    help="how many run.py processes are being launched over this "
                         "round, including this one. Purely a declaration - one "
                         "invocation is sequential either way - and it is recorded "
                         "as metadata.concurrency_declared so a snapshot says how "
                         "it was produced instead of leaving it to be "
                         "reconstructed from timestamps (#120). Concurrency is "
                         "allowed: it is roughly 4x faster and each process owns "
                         "its own shard file, so nothing races on a write. What is "
                         "not allowed is an undeclared one, because a concurrent "
                         "snapshot and a sequential one then get compared with "
                         "nothing recording the difference")
    ap.add_argument("--max-consecutive-failures", type=int, default=8,
                    help="stop the pass after this many failed cells in a row; "
                         "0 disables it. A usage limit or an outage fails every "
                         "remaining key, and each one costs two calls because "
                         "call() retries: round 25 ground through 152 keys twice "
                         "for no data. A failed key is not recorded as done, so "
                         "re-running the same command regenerates exactly the "
                         "keys this stop left behind")
    args = ap.parse_args()

    if args.concurrency < 1:
        sys.exit("--concurrency must be at least 1")

    claude_bin = require_claude_bin(args.claude_bin)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    arm_names = [a.strip() for a in args.arms.split(",") if a.strip()]
    bad_arms = [a for a in arm_names if a not in ARMS]
    if bad_arms:
        sys.exit("unknown arm(s): %s (valid: %s)" % (", ".join(bad_arms), ", ".join(ARMS)))
    cases_dir = Path(args.cases_dir)
    if not cases_dir.is_dir():
        sys.exit("no such case directory: %s" % args.cases_dir)
    cases = sorted(d for d in cases_dir.iterdir()
                   if (d / "prompt.md").exists()
                   and match_case(d.name, args.cases))
    if not cases:
        sys.exit("no cases matched: %s" % args.cases)

    # Resolved once, then stamped onto every run below. The snapshot-level
    # stamp is written when the file is created and never again, so a round
    # assembled into a pre-seeded file inherits that file's provenance:
    # round-12.json carries round-01-n10-v2.json's CLI and date for runs made
    # three days later on a different CLI (#80). A per-run stamp cannot be
    # inherited, and it can represent a round that legitimately spans hours.
    cli_version = _cli_version(claude_bin)
    case_ck = cases_cksum(cases_dir, [d.name for d in cases])

    arms = dict(ARMS)
    arms["laconic"] = laconic_rules(ROOT, args.level)
    if not arms["laconic"].strip():
        sys.exit("hook produced no rules for level %s" % args.level)
    cksum = str(zlib.crc32(arms["laconic"].encode()))

    snap = load_snapshot(args.snapshot)
    if snap is None:
        snap = new_snapshot(args.reps, models, args.level, cksum, arms, claude_bin,
                            cases_ck=case_ck, cases_dir=str(cases_dir),
                            concurrency_declared=args.concurrency)
        if args.carry_arms_from:
            source = load_snapshot(args.carry_arms_from)
            if source is None:
                sys.exit("no snapshot to carry arms from: %s" % args.carry_arms_from)
            source["__path"] = args.carry_arms_from
            carry_arms(snap, source, arm_names)
            absent = snap["metadata"]["carried_arms_from"]["missing_arms"]
            if absent:
                print("warning: %s has no runs to carry for %s. This is not an "
                      "error - the round reports on the arms it has - but it is "
                      "otherwise silent, so generate the arm into the source "
                      "snapshot first if this round should compare against it."
                      % (args.carry_arms_from, ", ".join(absent)))
    elif snap["metadata"].get("rules_cksum") != cksum:
        sys.exit("snapshot was generated from different rules (cksum %s vs %s); "
                 "move it aside before regenerating"
                 % (snap["metadata"].get("rules_cksum"), cksum))
    else:
        # The same guard the rules have had since the beginning, for the case
        # material (#69). A snapshot written before this field existed carries
        # None and is resumed with a note rather than refused - refusing would
        # make every committed snapshot unresumable to no purpose.
        stored = snap["metadata"].get("cases_cksum")
        if stored is None:
            print("note: this snapshot predates the case-set checksum (#69), so "
                  "a mid-round case change cannot be detected in it")
        elif stored != case_ck and not args.allow_case_change:
            sys.exit("the case material changed since this snapshot was started "
                     "(cases_cksum %s vs %s). Resuming would produce one round "
                     "generated from two different case sets. Restore the cases, "
                     "or pass --allow-case-change if the change genuinely cannot "
                     "affect the runs" % (stored, case_ck))
        elif stored != case_ck:
            print("warning: case material changed since this snapshot was started "
                  "(%s vs %s), continuing because --allow-case-change was given"
                  % (stored, case_ck))
            snap["metadata"]["cases_cksum_overridden"] = [stored, case_ck]
    # A declaration describes the file, not the invocation, so a resume records
    # the widest regime any pass over this snapshot ran under. Resuming a 5-way
    # round with the default would otherwise relabel it sequential.
    meta = snap["metadata"]
    meta["concurrency_declared"] = max(meta.get("concurrency_declared") or 1,
                                       args.concurrency)
    # Resolved once: carry_arms has already run by here, so the carried set
    # cannot change during the pass, and reading the carry source on each of
    # 440 writes would re-parse a multi-megabyte snapshot every time.
    carried = concurrency.carried_runs(snap)

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
    # A multi-turn case (#166) is one cell and several CLI calls, so the two
    # numbers come apart and the call count is the one a subscription limit is
    # denominated in. Priced per case rather than per cell.
    turns_per_case = {d.name: len(split_turns((d / "prompt.md").read_text()))
                      for d in cases}
    left_cells = [(d.name, a, m, rep) for rep in range(args.reps) for d in cases
                  for m in models for a in arm_names
                  if run_key(d.name, a, m, rep) not in done]
    left = len(left_cells)
    left_calls = sum(turns_per_case[c] for c, _, _, _ in left_cells)
    probes = sum(1 for a in arm_names if a in ARM_OUTPUT_STYLES)
    # Printed before the first call, because the number nobody had was the plan.
    # A round is priced afterwards, in report.py, off what it spent; what a
    # maintainer needs before committing hours of quota is what it is about to
    # spend. Every call is one CLI session, which is the unit a subscription
    # limit is denominated in.
    multi = sorted(c for c, n in turns_per_case.items() if n > 1)
    print("budget: %d call(s) to make, of %d cell(s) in this pass (%d already "
          "in the snapshot)%s. A failed call is retried once, so the ceiling "
          "is %d.%s" % (left_calls, total, total - left,
                        ", plus %d output-style probe(s)" % probes if probes else "",
                        2 * left_calls + probes,
                        (" Multi-turn: %s - one cell each, %s call(s) each."
                         % (", ".join(multi),
                            ", ".join(str(turns_per_case[c]) for c in multi)))
                        if multi else ""))

    # Checked after the cheap argument validation and after the snapshot
    # guards, so a typo in --cases or a checksum mismatch fails without
    # spending an API call, and before any generation, so a style that is not
    # landing stops the round instead of silently duplicating baseline.
    for arm in arm_names:
        style = ARM_OUTPUT_STYLES.get(arm)
        if style and not output_style_reaches_model(claude_bin, models[0], style):
            sys.exit("the %s output style is not reaching the model through "
                     "--settings on this CLI (%s), so arm %s would be a second "
                     "copy of baseline. Check that the style exists in this "
                     "version before running the round."
                     % (style, _cli_version(claude_bin), arm))

    n = 0
    streak = 0
    for rep in range(args.reps):
        for case_dir in cases:
            case = case_dir.name
            turns = split_turns((case_dir / "prompt.md").read_text())
            for model in models:
                for arm in arm_names:  # innermost: arms sampled at adjacent moments
                    n += 1
                    if run_key(case, arm, model, rep) in done:
                        continue
                    scratch = tempfile.mkdtemp()
                    fixture = case_dir / "fixture"
                    if fixture.is_dir():
                        shutil.copytree(fixture, scratch, dirs_exist_ok=True)
                    res = call_turns(claude_bin, model, turns, arms[arm],
                                     scratch, ARM_OUTPUT_STYLES.get(arm),
                                     delivery=args.turn_delivery,
                                     level=args.level)
                    shutil.rmtree(scratch, ignore_errors=True)
                    if not res.get("ok"):  # one retry before recording a failure
                        scratch = tempfile.mkdtemp()
                        if fixture.is_dir():
                            shutil.copytree(fixture, scratch, dirs_exist_ok=True)
                        res = call_turns(claude_bin, model, turns, arms[arm],
                                         scratch, ARM_OUTPUT_STYLES.get(arm),
                                         delivery=args.turn_delivery,
                                         level=args.level)
                        shutil.rmtree(scratch, ignore_errors=True)
                    res.update({"case": case, "arm": arm, "model": model, "rep": rep,
                                "generated_at": _now(),
                                "claude_cli_version": cli_version,
                                "generator": GENERATOR})
                    # Replace the failed record for this cell rather than
                    # appending beside it (#61): a resume is a second attempt
                    # at one cell, not a second cell.
                    key = run_key(case, arm, model, rep)
                    if key in at:
                        snap["runs"][at[key]] = res
                    else:
                        at[key] = len(snap["runs"])
                        snap["runs"].append(res)
                    # Recomputed rather than counted, so the number survives a
                    # merge of shard files this process never saw. Cheap: one
                    # sort of a few hundred intervals per write.
                    meta["max_runs_in_flight"] = (
                        concurrency.snapshot_max_in_flight(snap["runs"], carried))
                    save_snapshot(args.snapshot, snap)
                    print("[%d/%d] %-14s %-16s %-7s rep%d %s"
                          % (n, total, case, arm, model, rep,
                             "ok" if res.get("ok") else "FAILED"))
                    streak = 0 if res.get("ok") else streak + 1
                    if (args.max_consecutive_failures
                            and streak >= args.max_consecutive_failures):
                        sys.exit(
                            "\nstopped after %d consecutive failed cell(s), at "
                            "%s/%s/%s rep%d. That is what a usage limit or an "
                            "outage looks like from inside a pass, and every "
                            "remaining key would cost two calls to record "
                            "another failure. The snapshot is saved and no "
                            "failed key counts as done, so re-running this same "
                            "command regenerates exactly what is missing. Pass "
                            "--max-consecutive-failures 0 to grind through it "
                            "anyway." % (streak, case, arm, model, rep))

    # A resume that finds every cell done never enters the loop's save, and the
    # declaration it was given would be lost with it. Recomputing here also
    # gives a snapshot written before #120 the stamp the first time it is
    # touched, instead of leaving the key absent.
    meta["max_runs_in_flight"] = concurrency.snapshot_max_in_flight(
        snap["runs"], carried)
    save_snapshot(args.snapshot, snap)

    bad = len([r for r in snap["runs"] if not r.get("ok")])
    print("\nwrote %s (%d runs, %d failed)" % (args.snapshot, len(snap["runs"]), bad))

    # Said here rather than left for evals/bench/concurrency.py to find months
    # later. The reconstruction is a floor - a retried cell records only the
    # second attempt's duration - so an excess is real even when it is small.
    flight = meta["max_runs_in_flight"]
    if flight > meta["concurrency_declared"]:
        print("warning: this snapshot's timestamps reconstruct to %d CLI "
              "invocation(s) in flight at once, against a declared %d. If the "
              "round was generated in parallel shards, pass --concurrency %d so "
              "the file records it (#120)."
              % (flight, meta["concurrency_declared"], flight))


if __name__ == "__main__":
    main()
