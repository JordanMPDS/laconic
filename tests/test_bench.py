#!/usr/bin/env python3
"""Validates harness logic against stubs - no live model calls."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import run as bench_run  # noqa: E402

fails = 0


def check(label, cond):
    global fails
    if cond:
        print("ok   %s" % label)
    else:
        print("FAIL %s" % label)
        fails += 1


GOOD_JSON = json.dumps({
    "is_error": False, "result": "the answer", "num_turns": 1,
    "total_cost_usd": 0.0096, "duration_ms": 2089,
    "usage": {"input_tokens": 10, "output_tokens": 33,
              "cache_creation_input_tokens": 3573,
              "cache_read_input_tokens": 17615},
})

parsed = bench_run.parse_cli_json(GOOD_JSON)
check("parses text", parsed["text"] == "the answer")
check("parses output tokens", parsed["output_tokens"] == 33)
check("parses cache fields", parsed["cache_read_input_tokens"] == 17615)
check("parses cost", parsed["total_cost_usd"] == 0.0096)
check("good json is ok", parsed["ok"] is True)

check("garbage is not ok", bench_run.parse_cli_json("not json")["ok"] is False)
check("empty is not ok", bench_run.parse_cli_json("")["ok"] is False)
check("is_error payload is not ok",
      bench_run.parse_cli_json(json.dumps({"is_error": True, "result": "x"}))["ok"] is False)

check("arms include all four",
      sorted(bench_run.ARMS) == ["baseline", "laconic", "terse-control", "word-compression"])
check("baseline has no system prompt", bench_run.ARMS["baseline"] is None)
check("terse control is exactly the control instruction",
      bench_run.ARMS["terse-control"] == "Answer concisely.")

rules = bench_run.laconic_rules(ROOT, "full")
check("laconic rules come from the hook and are non-empty", len(rules) > 200)
check("laconic rules carry the thesis sentinel", "fewer claims" in rules)

# Test resolve_claude_bin: bare names must not resolve to nonexistent <cwd>/claude
resolved_bare = bench_run.resolve_claude_bin("claude")
check("resolve bare claude doesn't return nonexistent repo/claude",
      resolved_bare != str(ROOT / "claude"))
# Either it found it in PATH, or it returned the bare name for PATH lookup by subprocess
check("resolve bare claude returns either a found path or the bare name",
      Path(resolved_bare).exists() or resolved_bare == "claude")

# Test resolve_claude_bin: relative paths become absolute
resolved_rel = bench_run.resolve_claude_bin("tests/stubs/claude-stub.sh")
check("resolve relative path returns absolute", Path(resolved_rel).is_absolute())
check("resolve relative path returns existing file", Path(resolved_rel).exists())

# Test call() with resolved stub path (absolute path that exists)
stub_result = bench_run.call(resolved_rel, "haiku", "test prompt", None, "/tmp")
check("call with resolved stub path returns ok", stub_result["ok"] is True)
check("call with resolved stub extracts text", stub_result["text"] == "stub answer")

# Test bare-name resolution and call: exercises shutil.which() path
with tempfile.TemporaryDirectory() as stub_dir:
    import shutil as shutil_module
    # Create a bare-name symlink to the stub
    stub_name = "claude-stub-test"
    stub_link = Path(stub_dir) / stub_name
    shutil_module.copy(resolved_rel, str(stub_link))
    stub_link.chmod(0o755)

    # Resolve with custom PATH
    old_path = os.environ.get("PATH", "")
    try:
        os.environ["PATH"] = str(stub_dir) + ":" + old_path
        resolved_bare_name = bench_run.resolve_claude_bin(stub_name)
        check("resolve bare name finds it in PATH", Path(resolved_bare_name).exists())

        # Call with the bare name resolved
        bare_result = bench_run.call(resolved_bare_name, "haiku", "test", None, "/tmp")
        check("call with bare-name resolution succeeds", bare_result["ok"] is True)
    finally:
        os.environ["PATH"] = old_path

# Test fail-fast check: unresolvable names must be rejected early
unresolvable = bench_run.resolve_claude_bin("nonexistent-command-xyz")
check("unresolvable name doesn't exist as path", not Path(unresolvable).exists())
# shutil.which returns None for unresolvable names, so resolve returns the arg unchanged
check("resolve returns bare name when not in PATH", unresolvable == "nonexistent-command-xyz")

# Test the guard's actual predicate (claude_bin_usable), not shutil.which
# directly - this is the function main() calls, so the test and the guard
# cannot diverge.
check("claude_bin_usable accepts a real executable",
      bench_run.claude_bin_usable(resolved_rel) is True)

with tempfile.TemporaryDirectory() as td_nonexec:
    nonexec_file = Path(td_nonexec) / "not-executable"
    nonexec_file.write_text("#!/bin/sh\necho hi")
    # File exists but is not executable
    check("claude_bin_usable rejects non-executable file",
          bench_run.claude_bin_usable(str(nonexec_file)) is False)

with tempfile.TemporaryDirectory() as td_dir:
    dir_path = Path(td_dir) / "is-a-directory"
    dir_path.mkdir()
    check("claude_bin_usable rejects directory",
          bench_run.claude_bin_usable(str(dir_path)) is False)

# End-to-end: invoke run.py as a real subprocess so the guard is exercised
# through main() itself, not just through the extracted predicate. This
# cannot be fooled by refactoring the predicate away from what main() calls.
with tempfile.TemporaryDirectory() as td_e2e:
    bad_bin = Path(td_e2e) / "not-executable"
    bad_bin.write_text("#!/bin/sh\necho hi")
    snap_path = Path(td_e2e) / "snap.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "run.py"),
         "--claude-bin", str(bad_bin), "--models", "haiku", "--reps", "1",
         "--cases", "floor", "--snapshot", str(snap_path)],
        capture_output=True, text=True,
    )
    check("subprocess: guard exits non-zero for non-executable claude-bin",
          proc.returncode != 0)
    check("subprocess: guard runs before any work, no snapshot written",
          not snap_path.exists())

with tempfile.TemporaryDirectory() as td:
    snap_path = Path(td) / "results.json"
    snap = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                  rules_cksum="123", arms=bench_run.ARMS)
    check("snapshot laconic arm has source field",
          "source" in snap["arms"]["laconic"])
    check("snapshot laconic source contains level",
          "full" in snap["arms"]["laconic"]["source"])
    snap["runs"].append({"case": "decision", "arm": "baseline",
                         "model": "haiku", "rep": 0, "ok": True, "text": "x"})
    bench_run.save_snapshot(snap_path, snap)
    reloaded = bench_run.load_snapshot(snap_path)
    check("snapshot round-trips", len(reloaded["runs"]) == 1)
    done = bench_run.completed_keys(reloaded)
    check("completed key recognized",
          bench_run.run_key("decision", "baseline", "haiku", 0) in done)
    check("other key not recognized",
          bench_run.run_key("decision", "laconic", "haiku", 0) not in done)

    failed = {"case": "c", "arm": "a", "model": "haiku", "rep": 0, "ok": False}
    check("failed runs are excluded from stats input",
          bench_run.usable([failed, {"case": "c", "arm": "a", "model": "haiku",
                                     "rep": 1, "ok": True, "text": "y"}]) ==
          [{"case": "c", "arm": "a", "model": "haiku", "rep": 1, "ok": True, "text": "y"}])

import judge as bench_judge  # noqa: E402

v = bench_judge.parse_verdict('{"verdict":"pass","quote":"q","reason":"r"}')
check("parses a clean verdict", v["verdict"] == "pass")
v = bench_judge.parse_verdict('here you go:\n{"verdict":"fail","quote":"q","reason":"r"}\nthanks')
check("parses a verdict wrapped in prose", v["verdict"] == "fail")
v = bench_judge.parse_verdict('{"verdict":"maybe","quote":"q","reason":"r"}')
check("rejects an out-of-range verdict", v["verdict"] == "not_exercised")
check("rejects garbage", bench_judge.parse_verdict("nope")["verdict"] == "not_exercised")
check("not_exercised is a supported verdict",
      bench_judge.parse_verdict('{"verdict":"not_exercised","quote":"","reason":"r"}')["verdict"]
      == "not_exercised")

p = bench_judge.build_judge_prompt("the question", "the trap",
                                   "a distinctive-response-marker")
check("judge prompt carries the trap", "the trap" in p)
# NOTE: deliberately not literally "the response" - that phrase already
# appears in the TEMPLATE's static instructional prose ("a short verbatim
# quote from the response...", "when the response does not engage..."), so
# checking for it would pass even if the actual response were dropped.
check("judge prompt carries the response", "a distinctive-response-marker" in p)
for arm in ["laconic", "baseline", "terse-control", "word-compression"]:
    check("judge prompt is blind to arm %s" % arm, arm not in p)

# judge.py's main() must resolve --claude-bin and fail fast, the same guard
# run.py has (see run.py's own subprocess e2e test) - otherwise a bad binary
# would silently record every case as a "judge call failed" not_exercised
# judgment instead of stopping before any work is done.
with tempfile.TemporaryDirectory() as td_judge_e2e:
    bad_bin = Path(td_judge_e2e) / "not-executable"
    bad_bin.write_text("#!/bin/sh\necho hi")
    # A real snapshot with a usable run, so a non-fail-fast implementation
    # would have something to (wrongly) grade.
    snap_path = Path(td_judge_e2e) / "results.json"
    snap = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                  rules_cksum="123", arms=bench_run.ARMS)
    snap["runs"].append({"case": "floor", "arm": "baseline", "model": "haiku",
                         "rep": 0, "ok": True, "text": "some answer"})
    bench_run.save_snapshot(snap_path, snap)
    out_path = Path(td_judge_e2e) / "judgments.json"

    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(bad_bin), "--results", str(snap_path),
         "--out", str(out_path)],
        capture_output=True, text=True,
    )
    check("judge: guard exits non-zero for non-executable claude-bin",
          proc.returncode != 0)
    check("judge: guard runs before any grading, no judgments file written",
          not out_path.exists())

import report as bench_report  # noqa: E402

synthetic = {
    "metadata": {"reps": 2, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"baseline": {"system_prompt": None}, "laconic": {"system_prompt": "r"}},
    "runs": [
        {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 0, "ok": True,
         "text": "The command removes the file from the staging area. It is safe.",
         "output_tokens": 100, "total_cost_usd": 0.01, "duration_ms": 1000},
        {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 1, "ok": True,
         "text": "The command removes the file from the staging area. It is safe.",
         "output_tokens": 120, "total_cost_usd": 0.01, "duration_ms": 1000},
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "It removes the file from the staging area and does not touch the disk.",
         "output_tokens": 40, "total_cost_usd": 0.005, "duration_ms": 500},
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 1, "ok": False},
    ],
}

agg = bench_report.aggregate(synthetic)
check("aggregates by case/arm/model", ("floor", "baseline", "haiku") in agg)
check("median output tokens", agg[("floor", "baseline", "haiku")]["output_tokens"] == 110)
check("failed runs excluded from n", agg[("floor", "laconic", "haiku")]["n"] == 1)
check("clean arms show no violations", agg[("floor", "laconic", "haiku")]["violations"] == 0)

check("clean run passes gates", bench_report.gate_failures(agg, 0.70) == [])

dirty = json.loads(json.dumps(synthetic))
dirty["runs"][2]["text"] = "removes file -> staging area. impl detail."
dirty["runs"][3] = dict(dirty["runs"][2], rep=1)
bad_agg = bench_report.aggregate(dirty)
fails_found = bench_report.gate_failures(bad_agg, 0.70)
check("degraded prose trips a gate", len(fails_found) > 0)
check("gate failure names the case", any("floor" in f for f in fails_found))

md = bench_report.render(synthetic, {"judgments": []}, 0.70)
check("report renders markdown", "| arm |" in md.lower() or "arm" in md)
check("report states the excluded count", "excluded" in md.lower())

# Cases with an empty never_cut list (decision, floor, ordered-steps in the
# real case set) must aggregate cleanly - an empty list has no missing
# keywords, so never_cut_missing() should return [] and never_cut_failures
# should be 0, not an exception and not a false failure.
check("empty never_cut list scores as zero failures, not a crash",
      agg[("floor", "laconic", "haiku")]["never_cut_failures"] == 0)

# judge.py records an infrastructure failure (subprocess/parse error) as
# verdict "not_exercised", reason "judge call failed" - distinct from a
# genuine "the trap never fired" not_exercised verdict. Folding the two
# together would make a run of judge outages look like a run of clean
# responses. The trap-verdicts table must keep them apart in a separate
# judge_failed column.
judg_mixed = {"judgments": [
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 0,
     "verdict": "not_exercised", "quote": "", "reason": "judge call failed"},
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 1,
     "verdict": "not_exercised", "quote": "", "reason": "asked for missing context"},
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 2,
     "verdict": "pass", "quote": "q", "reason": "fine"},
]}
md_mixed = bench_report.render(synthetic, judg_mixed, 0.70)
check("judge_failed column present in trap-verdicts table",
      "judge_failed" in md_mixed)
check("judge call failures counted separately from genuine not_exercised",
      "| floor | laconic | 1 | 0 | 1 | 1 |" in md_mixed)

# A total generation outage (every run recorded ok=False) must not be blessed
# as "gates pass" - aggregate() returns {} and gate_failures() vacuously
# returns [] for an empty agg, so report.py needs an explicit guard in main()
# that fires before rendering, regardless of --no-gate. Task 4 shipped this
# exact failure mode once (every call in a real run recorded as a failure);
# this is the second line of defense against a recurrence. Exercised as a
# real subprocess so the guard is proven through main() itself, the same way
# run.py's and judge.py's claude-bin guards are tested above.
with tempfile.TemporaryDirectory() as td_outage:
    outage_snap = Path(td_outage) / "results.json"
    snap_all_failed = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                             rules_cksum="1", arms=bench_run.ARMS)
    snap_all_failed["runs"].append({"case": "floor", "arm": "laconic", "model": "haiku",
                                    "rep": 0, "ok": False})
    bench_run.save_snapshot(outage_snap, snap_all_failed)

    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "report.py"),
         "--results", str(outage_snap), "--judgments", "/dev/null", "--no-gate"],
        capture_output=True, text=True,
    )
    check("total outage exits non-zero even with --no-gate", proc.returncode != 0)
    check("total outage message names the cause",
          "no usable runs" in (proc.stdout + proc.stderr))

# The gate's diagnostic message must not round a fractional median down to
# zero via %d - statistics.median([0, 0, 1, 1]) is 0.5, the gate correctly
# fires (0.5 > 0), but a developer reading "0 readability violation(s)" would
# be told the wrong thing while trying to diagnose exactly this failure.
frac_agg = {
    ("floor", "baseline", "haiku"): {"article_rate": 0.0, "aux_verb_rate": 0.0},
    ("floor", "laconic", "haiku"): {"violations": 0.5, "never_cut_failures": 0,
                                    "article_rate": 0.0, "aux_verb_rate": 0.0,
                                    "spans": []},
}
frac_fails = bench_report.gate_failures(frac_agg, 0.70)
check("fractional violation median doesn't round down to zero in the gate message",
      any("0.5 readability violation" in f for f in frac_fails))

# _load_judgments() exists only to treat an empty-but-existing file (/dev/null
# standing in for "no judgments yet") as absence. A genuinely corrupt
# non-empty judgments file is a real problem and must surface as an error,
# not be swallowed into a clean, silently judgment-free report.
check("empty judgments file still treated as no judgments",
      bench_report._load_judgments("/dev/null") == {"judgments": []})
with tempfile.TemporaryDirectory() as td_corrupt:
    corrupt_path = Path(td_corrupt) / "judgments.json"
    corrupt_path.write_text("{not valid json")
    try:
        bench_report._load_judgments(str(corrupt_path))
        check("corrupt non-empty judgments file is not silently swallowed", False)
    except ValueError:
        check("corrupt non-empty judgments file is not silently swallowed", True)

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
