#!/usr/bin/env python3
"""Validates harness logic against stubs - no live model calls."""
import json
import os
import re
import shutil
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

# The two checks above pass just as well against a hardcoded copy of today's
# hook output - they don't prove laconic_rules() actually calls the hook.
# Invoke hooks/laconic.sh directly (independently of laconic_rules()'s own
# implementation) with the same level and compare byte-for-byte; then prove
# the function isn't just a fixed string at all by checking two different
# levels produce different output.
with tempfile.TemporaryDirectory() as hook_direct_dir:
    (Path(hook_direct_dir) / ".laconic-level").write_text("full")
    hook_direct_env = dict(os.environ, CLAUDE_CONFIG_DIR=hook_direct_dir)
    hook_direct_env.pop("LACONIC_DEFAULT", None)
    hook_direct_out = subprocess.run(
        ["bash", str(ROOT / "hooks" / "laconic.sh"), "start"],
        capture_output=True, text=True, env=hook_direct_env, stdin=subprocess.DEVNULL,
    )
check("laconic_rules output matches invoking the hook directly for the same level",
      rules == hook_direct_out.stdout)

rules_lite = bench_run.laconic_rules(ROOT, "lite")
rules_ultra = bench_run.laconic_rules(ROOT, "ultra")
check("laconic rules differ between lite and ultra levels "
      "(a hardcoded constant could not do this)",
      rules_lite != rules_ultra)

# Test resolve_claude_bin: bare names must not resolve to nonexistent <cwd>/claude
resolved_bare = bench_run.resolve_claude_bin("claude")
check("resolve bare claude doesn't return nonexistent repo/claude",
      resolved_bare != str(ROOT / "claude"))
# NOTE: "Path(resolved_bare).exists() or resolved_bare == 'claude'" is true by
# construction (resolve_claude_bin is literally `shutil.which(arg) or arg`),
# so it would pass even if PATH lookup were removed entirely. Prove PATH
# resolution actually happens: put a stub literally named "claude" on a
# controlled PATH and require resolve_claude_bin("claude") to return its
# real absolute location, not the bare string.
with tempfile.TemporaryDirectory() as claude_named_dir:
    claude_named_bin = Path(claude_named_dir) / "claude"
    shutil.copy(str(ROOT / "tests" / "stubs" / "claude-stub.sh"), str(claude_named_bin))
    claude_named_bin.chmod(0o755)
    old_path_named = os.environ.get("PATH", "")
    try:
        os.environ["PATH"] = str(claude_named_dir) + ":" + old_path_named
        resolved_named_claude = bench_run.resolve_claude_bin("claude")
    finally:
        os.environ["PATH"] = old_path_named
check("resolve_claude_bin('claude') resolves through PATH to the stub's real "
      "absolute location, not the bare string",
      resolved_named_claude == str(claude_named_bin.resolve()))

# Test resolve_claude_bin: relative paths become absolute
resolved_rel = bench_run.resolve_claude_bin("tests/stubs/claude-stub.sh")
check("resolve relative path returns absolute", Path(resolved_rel).is_absolute())
check("resolve relative path returns existing file", Path(resolved_rel).exists())

# Test call() with resolved stub path (absolute path that exists)
stub_result = bench_run.call(resolved_rel, "haiku", "test prompt", None, "/tmp")
check("call with resolved stub path returns ok", stub_result["ok"] is True)
check("call with resolved stub extracts text", stub_result["text"] == "stub answer")

# call() is only ever exercised above with system_prompt=None. Nothing proves
# --append-system-prompt actually gets attached, and nothing proves the
# isolation env vars (CLAUDE_CODE_SAFE_MODE=1, LACONIC_DEFAULT stripped) are
# set - if either silently vanished from call(), every arm would collapse to
# the same behavior and the benchmark would report ~0% difference while
# staying green. The stub records its own argv and the relevant environment
# to STUB_ARGV_OUT when set, so assert on the invocation itself.
old_stub_argv_out = os.environ.get("STUB_ARGV_OUT")
old_laconic_default = os.environ.get("LACONIC_DEFAULT")
try:
    os.environ["LACONIC_DEFAULT"] = "ultra"  # must not reach the stub

    with tempfile.TemporaryDirectory() as td_argv:
        argv_with_prompt = Path(td_argv) / "argv-with-prompt.txt"
        os.environ["STUB_ARGV_OUT"] = str(argv_with_prompt)
        bench_run.call(resolved_rel, "haiku", "test", "SENTINEL_RULES", "/tmp")
        argv_lines = argv_with_prompt.read_text().splitlines()
        check("call() sets CLAUDE_CODE_SAFE_MODE=1 for the subprocess",
              argv_lines[0] == "SAFE_MODE=1")
        check("call() strips LACONIC_DEFAULT from the subprocess env",
              argv_lines[1] == "LACONIC_DEFAULT=<unset>")
        argv_tail = argv_lines[3:]  # after "SAFE_MODE=...", "LACONIC_DEFAULT=...", "ARGV:"
        check("system_prompt is passed via --append-system-prompt immediately "
              "followed by the prompt text",
              "--append-system-prompt" in argv_tail and
              argv_tail[argv_tail.index("--append-system-prompt") + 1] == "SENTINEL_RULES")

        argv_no_prompt = Path(td_argv) / "argv-no-prompt.txt"
        os.environ["STUB_ARGV_OUT"] = str(argv_no_prompt)
        bench_run.call(resolved_rel, "haiku", "test", None, "/tmp")
        argv_tail_none = argv_no_prompt.read_text().splitlines()[3:]
        check("system_prompt=None produces no --append-system-prompt flag at all",
              "--append-system-prompt" not in argv_tail_none)
finally:
    if old_stub_argv_out is None:
        os.environ.pop("STUB_ARGV_OUT", None)
    else:
        os.environ["STUB_ARGV_OUT"] = old_stub_argv_out
    if old_laconic_default is None:
        os.environ.pop("LACONIC_DEFAULT", None)
    else:
        os.environ["LACONIC_DEFAULT"] = old_laconic_default

# claude-stub.sh's own STUB_FAIL branch is untested - if it were removed, a
# real generation outage would go undetected offline (the stub would just
# keep "succeeding").
stub_fail_out = subprocess.run(
    ["bash", str(ROOT / "tests" / "stubs" / "claude-stub.sh")],
    input="prompt", capture_output=True, text=True,
    env=dict(os.environ, STUB_FAIL="1"),
)
check("STUB_FAIL=1 makes the stub exit non-zero", stub_fail_out.returncode != 0)

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
    # The two checks above only ever vary arm - a run_key() that silently
    # dropped rep from the tuple would still pass both. A --reps 5 resume
    # would then treat rep 0's key as already covering reps 1-4 and collect
    # only one sample instead of five. Vary rep and nothing else.
    check("run_key varying only rep produces distinct keys",
          bench_run.run_key("decision", "baseline", "haiku", 0) !=
          bench_run.run_key("decision", "baseline", "haiku", 1))

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
# NOTE: the check above cannot tell median from mean - [100, 120] has
# mean == median == 110, so swapping statistics.median for statistics.mean in
# aggregate() would pass silently. [10, 20, 90] separates them: median 20,
# mean 40.
median_vs_mean_synthetic = {
    "metadata": {"reps": 3, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"baseline": {"system_prompt": None}},
    "runs": [
        {"case": "floor", "arm": "baseline", "model": "haiku", "rep": i, "ok": True,
         "text": "ok", "output_tokens": t, "total_cost_usd": 0.01, "duration_ms": 1000}
        for i, t in enumerate([10, 20, 90])
    ],
}
median_vs_mean_agg = bench_report.aggregate(median_vs_mean_synthetic)
check("output_tokens is the true median (20), not the mean (40), of [10, 20, 90]",
      median_vs_mean_agg[("floor", "baseline", "haiku")]["output_tokens"] == 20)
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
# NOTE: "arm" in md is tautological - it also matches the literal string
# "warm" (e.g. in a word like "warmup"), so it passes whether or not a table
# actually rendered. Check the real table header instead, built from the
# synthetic fixture's own models list.
check("report renders a markdown table with the arm/model header",
      "| arm | haiku |" in md)
# synthetic has exactly one ok=False run (floor/laconic/haiku/rep1) out of 4.
check("report states the exact excluded count",
      "Excluded runs (call failed, never scored): 1" in md)

# Cases with an empty never_cut list (decision, floor, ordered-steps in the
# real case set) must aggregate cleanly - an empty list has no missing
# keywords, so never_cut_missing() should return [] and never_cut_failures
# should be 0, not an exception and not a false failure.
check("empty never_cut list scores as zero failures, not a crash",
      agg[("floor", "laconic", "haiku")]["never_cut_failures"] == 0)

# The check above only ever exercises an EMPTY never_cut list (floor's is
# []), so never_cut_missing() is never called with real keywords and the
# never-cut gate itself has zero end-to-end coverage - a hardcoded
# never_cut_failures = 0, or the gate block being deleted from
# gate_failures() entirely, would both pass every check above. Use
# "destructive" (never_cut: ["cascade", "invoices"]) with one response that
# names both and one that omits them.
never_cut_gate_synthetic = {
    "metadata": {"reps": 2, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"laconic": {"system_prompt": "r"}},
    "runs": [
        {"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "Sessions cascade-delete and invoices reference users.",
         "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
        {"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 1, "ok": True,
         "text": "The rows are removed from the table.",
         "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
    ],
}
never_cut_gate_agg = bench_report.aggregate(never_cut_gate_synthetic)
check("never_cut_failures counts the response missing a required keyword",
      never_cut_gate_agg[("destructive", "laconic", "haiku")]["never_cut_failures"] == 1)
never_cut_gate_fails = bench_report.gate_failures(never_cut_gate_agg, 0.70)
check("the never-cut gate fires when a required keyword is missing",
      any("never-cut failure" in f for f in never_cut_gate_fails))

# judge.py records two kinds of infrastructure failure - the call itself
# failed ("judge call failed"), or it succeeded but the reply couldn't be
# parsed as a verdict ("unparseable") - both distinct from a genuine "the
# trap never fired" not_exercised verdict. Folding either into not_exercised
# would make a run of judge outages or parse failures look like a run of
# clean responses. The trap-verdicts table must keep them apart in a
# separate judge_failed column, routed through the shared constants in
# judge.py (not a magic string re-typed here and in report.py).
judg_mixed = {"judgments": [
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 0,
     "verdict": "not_exercised", "quote": "", "reason": bench_judge.REASON_JUDGE_CALL_FAILED},
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 1,
     "verdict": "not_exercised", "quote": "", "reason": "asked for missing context"},
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 2,
     "verdict": "pass", "quote": "q", "reason": "fine"},
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 3,
     "verdict": "not_exercised", "quote": "", "reason": bench_judge.REASON_UNPARSEABLE},
]}
md_mixed = bench_report.render(synthetic, judg_mixed, 0.70)
check("judge_failed column present in trap-verdicts table",
      "judge_failed" in md_mixed)
check("judge call failures and unparseable replies both counted separately "
      "from genuine not_exercised",
      "| floor | rule-adherence | laconic | 1 | 0 | 1 | 2 |" in md_mixed)

# The grading column is what stops a rule-adherence row being read as evidence
# about answer quality, so it has to carry the case's real classification, not
# a default. floor is the case whose pass count was read that way once.
check("the trap-verdicts table labels each case with where its criteria came from",
      "| case | grading | arm |" in md_mixed and "rule-adherence" in md_mixed)
check("a case with no expect.json is reported unclassified, never as quality",
      bench_report.case_grading("no-such-case") == "unclassified")
check("the quality cases are labelled quality",
      all(bench_report.case_grading(c) == "quality"
          for c in ("fail-open", "silent-success", "stale-cache")))

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

# The outage guard above is subprocess-tested, but an ordinary gate failure
# (not a total outage - some runs are usable, but a laconic arm regressed) is
# only ever checked by calling gate_failures() directly in-process. main()
# could drop its `sys.exit(1)` on gate failure entirely and every other check
# in this file would stay green. Exercise it through the real CLI: a
# degraded-prose snapshot must exit non-zero by default, and exit zero for
# the identical snapshot when --no-gate is passed.
with tempfile.TemporaryDirectory() as td_gate_exit:
    gate_exit_snap = Path(td_gate_exit) / "results.json"
    bench_run.save_snapshot(gate_exit_snap, dirty)

    proc_gated = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "report.py"),
         "--results", str(gate_exit_snap), "--judgments", "/dev/null"],
        capture_output=True, text=True,
    )
    check("a degraded laconic arm exits non-zero through main() by default",
          proc_gated.returncode != 0)

    proc_nogate = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "report.py"),
         "--results", str(gate_exit_snap), "--judgments", "/dev/null", "--no-gate"],
        capture_output=True, text=True,
    )
    check("the identical degraded snapshot exits zero with --no-gate",
          proc_nogate.returncode == 0)

# The gate's diagnostic message must lead with the number it actually gated
# on (the total) and must not silently round a fractional median down to
# zero either - statistics.median([0, 0, 1, 1]) is 0.5, the total across the
# same 4 responses is 2, and the gate correctly fires on the total. A message
# that only said "0.0 readability violation(s)" would read as self-
# contradictory (a failure reporting zero); the median must still be visible
# so a developer isn't told a rounded-to-zero number while diagnosing this
# exact failure mode.
frac_agg = {
    ("floor", "baseline", "haiku"): {"article_rate": 0.0, "aux_verb_rate": 0.0,
                                     "article_count": 0.0, "aux_count": 0.0},
    ("floor", "laconic", "haiku"): {"violations": 0.5, "violations_total": 2, "n": 4,
                                    "never_cut_failures": 0,
                                    "article_rate": 0.0, "aux_verb_rate": 0.0,
                                    "spans": []},
}
frac_fails = bench_report.gate_failures(frac_agg, 0.70)
check("gate message leads with the total the gate used, not the median",
      any("2 readability violation(s) across 4 response(s)" in f for f in frac_fails))
check("gate message still shows the fractional median, not rounded to zero",
      any("median 0.5" in f for f in frac_fails))

# A ratio of small integers is not evidence: a baseline that only had ~1
# auxiliary word to begin with (code-fidelity/haiku's real baseline: 49
# words, aux_rate 0.021) clears RATE_FLOOR trivially even though there is no
# meaningful count behind it. The absolute-count floor must suppress this;
# a baseline with a healthy count must still gate on the same rate drop.
# Both fixtures carry BOTH models: the rate gates need corroboration, so a
# single-model fixture can only ever produce a "not gated" note and would
# prove nothing about whether the gate fires.
def rate_agg(base_aux_rate, base_aux_count, laconic_aux_rate, models=("haiku", "sonnet")):
    out = {}
    for m in models:
        out[("c", "baseline", m)] = {"article_rate": 0.0, "article_count": 0.0,
                                     "aux_verb_rate": base_aux_rate,
                                     "aux_count": base_aux_count}
        out[("c", "laconic", m)] = {"violations_total": 0, "n": 1, "violations": 0.0,
                                    "never_cut_failures": 0, "article_rate": 0.0,
                                    "aux_verb_rate": laconic_aux_rate, "spans": []}
    return out


low_count_fails = bench_report.gate_failures(rate_agg(0.021, 1.0, 0.0), 0.70)
check("a baseline with ~1 auxiliary word does not trip the aux-rate gate",
      not any("aux verb rate" in f for f in low_count_fails))

healthy_count_agg = rate_agg(0.05, 6.0, 0.01)
healthy_count_fails = bench_report.gate_failures(healthy_count_agg, 0.70)
check("a baseline with a healthy auxiliary-word count still trips the aux-rate gate",
      any("aux verb rate" in f for f in healthy_count_fails))

# One model showing the drop is the documented noise pattern and must not
# fail the run; it must not vanish silently either.
half_agg = rate_agg(0.05, 6.0, 0.01)
half_agg[("c", "laconic", "sonnet")]["aux_verb_rate"] = 0.05
check("a drop on one model only does not fail the aux-rate gate",
      not any("aux verb rate" in f
              for f in bench_report.gate_failures(half_agg, 0.70)))
check("a single-model case is surfaced as a note rather than dropped",
      any("not gated" in n
          for n in bench_report.gate_notes(rate_agg(0.05, 6.0, 0.01, ("haiku",)), 0.70)))

# gate_failures() taking `threshold` as an argument is never actually proven
# to matter - every call above always used 0.70. If the function ignored the
# argument and hardcoded 0.70 internally, every check so far would still
# pass. A lax threshold (0.01) on the same healthy_count_agg data must clear
# the gate that 0.70 trips: 0.01 < 0.01*0.05 is False, so nothing fires.
lax_threshold_fails = bench_report.gate_failures(healthy_count_agg, 0.01)
check("two different thresholds produce different gate outcomes on the same "
      "data (threshold is not ignored)",
      lax_threshold_fails != healthy_count_fails)

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

import statistics as _statistics  # noqa: E402

# --- B: the readability gate must see every violation, not the median ---
# Two of five laconic responses carry 2 running-prose-arrow violations each,
# three are clean. statistics.median([0,0,0,2,2]) == 0, so a median-based
# gate reads this as "clean". The total (4) and the flagged-response count
# (2) both correctly show a regression, and the gate must use one of those.
BAD_ARROW_TEXT = "It skips -> avoids the extra check. It removes -> deletes the file."
minority_synthetic = {
    "metadata": {"reps": 5, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"laconic": {"system_prompt": "r"}},
    "runs": [
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": i, "ok": True,
         "text": "It removes the file from the staging area.",
         "output_tokens": 20, "total_cost_usd": 0.001, "duration_ms": 500}
        for i in range(3)
    ] + [
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": i, "ok": True,
         "text": BAD_ARROW_TEXT,
         "output_tokens": 20, "total_cost_usd": 0.001, "duration_ms": 500}
        for i in range(3, 5)
    ],
}
minority_agg = bench_report.aggregate(minority_synthetic)
minority_key = ("floor", "laconic", "haiku")
check("minority regression: median reads as clean",
      minority_agg[minority_key]["violations"] == 0)
check("minority regression: total correctly shows it",
      minority_agg[minority_key]["violations_total"] == 4)
check("minority regression: flagged-response count correctly shows it",
      minority_agg[minority_key]["violations_flagged_responses"] == 2)
minority_gate_fails = bench_report.gate_failures(minority_agg, 0.70)
check("a minority-of-responses regression trips the readability gate",
      any("floor" in f for f in minority_gate_fails))

# --- C: output-token dispersion (min/max/stdev) must actually be computed ---
# synthetic's floor/baseline/haiku bucket has output_tokens [100, 120].
check("output token dispersion: min is computed",
      agg[("floor", "baseline", "haiku")]["output_tokens_min"] == 100)
check("output token dispersion: max is computed",
      agg[("floor", "baseline", "haiku")]["output_tokens_max"] == 120)
check("output token dispersion: stdev is computed with statistics.stdev",
      abs(agg[("floor", "baseline", "haiku")]["output_tokens_stdev"]
          - _statistics.stdev([100, 120])) < 1e-9)
check("output token dispersion: stdev guarded for n<2 (no crash, reads 0.0)",
      agg[("floor", "laconic", "haiku")]["output_tokens_stdev"] == 0.0)
check("output token dispersion is published in the rendered markdown",
      "min:" in md and "max:" in md and "stdev:" in md)

# --- The "totals" table must render a sum, not a median across cases ---
# _by_arm_model takes a median across cases by default. A table headed
# "total across responses" that uses the default renders a median-of-
# per-case-totals under a "total" label - self-contradicting the gate
# immediately below it, which fires on the real sum. Three cases with
# per-case violations_total [5, 0, 0]: sum is 5, median is 0.
FIVE_ARROW_TEXT = ("A fails -> B happens. C fails -> D happens. "
                   "E fails -> F happens. G fails -> H happens. I fails -> J happens.")
totals_synthetic = {
    "metadata": {"reps": 1, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"laconic": {"system_prompt": "r"}},
    "runs": [
        {"case": "c1", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": FIVE_ARROW_TEXT, "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
        {"case": "c2", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "It removes the file.", "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
        {"case": "c3", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "It removes the file.", "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
    ],
}
totals_agg = bench_report.aggregate(totals_synthetic)
per_case_totals = [totals_agg[("c1", "laconic", "haiku")]["violations_total"],
                   totals_agg[("c2", "laconic", "haiku")]["violations_total"],
                   totals_agg[("c3", "laconic", "haiku")]["violations_total"]]
check("fixture actually has sum != median (sanity check on the fixture itself)",
      sum(per_case_totals) == 5 and _statistics.median(per_case_totals) == 0)
md_totals = bench_report.render(totals_synthetic, {"judgments": []}, 0.70)
check("the 'total across responses' table renders the sum (5), not the median (0)",
      "| laconic | 5 |" in md_totals)
check("the 'responses with >=1 violation' table also renders a sum, not a median",
      "| laconic | 1 |" in md_totals)

# --- D: never-cut must show checked vs unchecked, not a bare failure count ---
# floor's never_cut is [] (nothing to check); destructive's is non-empty.
# "0 failures" must not be readable as "everything was verified".
never_cut_synthetic = {
    "metadata": {"reps": 1, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"laconic": {"system_prompt": "r"}},
    "runs": [
        {"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "Sessions cascade-delete and invoices reference users.",
         "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "It removes the file.",
         "output_tokens": 10, "total_cost_usd": 0.001, "duration_ms": 500},
    ],
}
nc_agg = bench_report.aggregate(never_cut_synthetic)
check("never_cut_checked is True for a case with keywords to verify",
      nc_agg[("destructive", "laconic", "haiku")]["never_cut_checked"] is True)
check("never_cut_checked is False for a case with an empty never_cut list",
      nc_agg[("floor", "laconic", "haiku")]["never_cut_checked"] is False)
md_nc = bench_report.render(never_cut_synthetic, {"judgments": []}, 0.70)
check("never-cut table reports checked and unchecked counts, not just failures",
      "| laconic | 1 | 1 | 0 |" in md_nc)

# --- F.4: report.py must warn loudly when judgments don't cover all usable runs ---
# synthetic has 3 usable runs (2 baseline + 1 laconic); give it only 1 judgment.
partial_judg = {"judgments": [
    {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 0,
     "verdict": "pass", "quote": "", "reason": "fine"},
]}
md_partial = bench_report.render(synthetic, partial_judg, 0.70)
check("partial judge coverage is named in the report (1/3, 2 missing)",
      "judgments cover 1/3 usable runs (2 missing)" in md_partial)
full_judg = {"judgments": [
    {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 0,
     "verdict": "pass", "quote": "", "reason": "fine"},
    {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 1,
     "verdict": "pass", "quote": "", "reason": "fine"},
    {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 0,
     "verdict": "pass", "quote": "", "reason": "fine"},
]}
md_full_cov = bench_report.render(synthetic, full_judg, 0.70)
check("full judge coverage shows no completeness warning",
      "judgments cover" not in md_full_cov)
check("no judgments at all (nobody ran judge.py yet) shows no false-positive warning",
      "judgments cover" not in md)

# --- F.1: judge.py must retry a failed call once before recording it ---
# A stub that fails on its first invocation and succeeds on its second proves
# the retry: without it, judge.py would record "judge call failed" after a
# single attempt and the counter file would read "1", not "2".
with tempfile.TemporaryDirectory() as td_retry:
    counter = Path(td_retry) / "calls"
    flaky = Path(td_retry) / "flaky-claude.sh"
    flaky.write_text(
        "#!/usr/bin/env bash\n"
        'n=$(cat "%s" 2>/dev/null || echo 0)\n'
        "n=$((n+1))\n"
        'printf \'%%s\' "$n" > "%s"\n'
        '[ "$n" -eq 1 ] && exit 3\n'
        "cat <<'JSON'\n"
        '{"is_error":false,"result":"stub answer","num_turns":1,'
        '"total_cost_usd":0.001,"duration_ms":1,\n'
        '"usage":{"input_tokens":1,"output_tokens":1,'
        '"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}\n'
        "JSON\n" % (counter, counter)
    )
    flaky.chmod(0o755)

    snap_path = Path(td_retry) / "results.json"
    snap_retry = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                        rules_cksum="1", arms=bench_run.ARMS)
    snap_retry["runs"].append({"case": "floor", "arm": "baseline", "model": "haiku",
                               "rep": 0, "ok": True, "text": "some answer"})
    bench_run.save_snapshot(snap_path, snap_retry)
    out_path = Path(td_retry) / "judgments.json"

    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(flaky), "--results", str(snap_path), "--out", str(out_path)],
        capture_output=True, text=True,
    )
    check("judge subprocess ran cleanly against the flaky stub", proc.returncode == 0)
    check("judge retries once on a failed call (stub invoked exactly twice)",
          counter.exists() and counter.read_text().strip() == "2")
    written = json.loads(out_path.read_text())
    check("judge records a real result after the retry succeeds, not 'judge call failed'",
          written["judgments"][0]["reason"] != bench_judge.REASON_JUDGE_CALL_FAILED)
    # The guard key is named for what it actually holds (the rules checksum
    # out of results.json's metadata), not "results_cksum" - a name that
    # would wrongly imply two runs with different responses but unchanged
    # rules are detected as stale.
    check("judge writes the checksum guard under 'rules_cksum', matching "
          "what the value actually is",
          written["metadata"].get("rules_cksum") == "1" and
          "results_cksum" not in written["metadata"])

# --- F.2: judge.py must hard-exit on a results/judgments checksum mismatch ---
with tempfile.TemporaryDirectory() as td_cksum:
    snap_path = Path(td_cksum) / "results.json"
    snap_new = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                      rules_cksum="NEWCKSUM", arms=bench_run.ARMS)
    snap_new["runs"].append({"case": "floor", "arm": "baseline", "model": "haiku",
                             "rep": 0, "ok": True, "text": "x"})
    bench_run.save_snapshot(snap_path, snap_new)

    judg_path = Path(td_cksum) / "judgments.json"
    stale = {"metadata": {"judge_model": "sonnet", "results_cksum": "OLDCKSUM"},
             "judgments": [{"case": "floor", "arm": "baseline", "model": "haiku",
                            "rep": 0, "verdict": "pass", "quote": "", "reason": "r"}]}
    judg_path.write_text(json.dumps(stale))

    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", resolved_rel, "--results", str(snap_path), "--out", str(judg_path)],
        capture_output=True, text=True,
    )
    check("judge: results/judgments cksum mismatch exits non-zero", proc.returncode != 0)
    check("judge: cksum mismatch message names both checksums",
          "OLDCKSUM" in (proc.stdout + proc.stderr) and "NEWCKSUM" in (proc.stdout + proc.stderr))
    check("judge: cksum mismatch leaves the existing judgments file untouched",
          json.loads(judg_path.read_text())["judgments"][0]["reason"] == "r")

# --- F.3: judge.py must call blind, from a fresh temp dir, never the repo root ---
# evals/snapshots/results.json (arm labels) and rules/laconic.md (the
# treatment's own system prompt) both live under ROOT; a judge call made
# with cwd=ROOT could see either. The stub logs $PWD independently of stdout
# so the check doesn't depend on parsing a verdict out of it.
with tempfile.TemporaryDirectory() as td_blind:
    cwd_log = Path(td_blind) / "cwd.log"
    cwd_stub = Path(td_blind) / "cwd-stub.sh"
    cwd_stub.write_text(
        "#!/usr/bin/env bash\n"
        'printf \'%s\\n\' "$PWD" >> "$JUDGE_CWD_LOG"\n'
        "cat <<'JSON'\n"
        '{"is_error":false,"result":"stub answer","num_turns":1,'
        '"total_cost_usd":0.001,"duration_ms":1,\n'
        '"usage":{"input_tokens":1,"output_tokens":1,'
        '"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}\n'
        "JSON\n"
    )
    cwd_stub.chmod(0o755)

    snap_path = Path(td_blind) / "results.json"
    snap_blind = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                        rules_cksum="1", arms=bench_run.ARMS)
    snap_blind["runs"].append({"case": "floor", "arm": "baseline", "model": "haiku",
                               "rep": 0, "ok": True, "text": "some answer"})
    bench_run.save_snapshot(snap_path, snap_blind)
    out_path = Path(td_blind) / "judgments.json"

    env = dict(os.environ, JUDGE_CWD_LOG=str(cwd_log))
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(cwd_stub), "--results", str(snap_path), "--out", str(out_path)],
        capture_output=True, text=True, env=env,
    )
    check("judge subprocess ran cleanly for the blindness test", proc.returncode == 0)
    logged_cwds = cwd_log.read_text().splitlines() if cwd_log.exists() else []
    check("judge call's cwd was logged", len(logged_cwds) == 1)
    check("judge call did not run with cwd at the repo root "
          "(blind to results.json's arm labels and rules/laconic.md)",
          logged_cwds and logged_cwds[0] != str(ROOT))

# --- G: run.py._cli_version must use the resolved --claude-bin, with a timeout ---
with tempfile.TemporaryDirectory() as td_ver:
    ver_stub = Path(td_ver) / "fake-claude-version.sh"
    ver_stub.write_text("#!/usr/bin/env bash\nprintf 'FAKE-VERSION-MARKER-42'\n")
    ver_stub.chmod(0o755)
    check("_cli_version uses the given claude_bin, not a hardcoded 'claude'",
          bench_run._cli_version(str(ver_stub)) == "FAKE-VERSION-MARKER-42")

    bad_ver_stub = Path(td_ver) / "bad-version.sh"
    bad_ver_stub.write_text("#!/usr/bin/env bash\nexit 1\n")
    bad_ver_stub.chmod(0o755)
    check("_cli_version reads 'unknown' when the binary's return code is non-zero",
          bench_run._cli_version(str(bad_ver_stub)) == "unknown")

# --- G: an invalid --arms value must not crash with a bare KeyError ---
with tempfile.TemporaryDirectory() as td_arms:
    snap_path = Path(td_arms) / "snap.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "run.py"),
         "--claude-bin", resolved_rel, "--models", "haiku", "--reps", "1",
         "--cases", "floor", "--arms", "bogus-arm", "--snapshot", str(snap_path)],
        capture_output=True, text=True,
    )
    check("invalid --arms value exits non-zero", proc.returncode != 0)
    check("invalid --arms value gives a clear message naming it, not a raw KeyError traceback",
          "Traceback" not in proc.stderr and "bogus-arm" in (proc.stdout + proc.stderr))

# --- G: parse_cli_json must treat a missing/non-string result as ok:false ---
# is_error:false with a null or absent "result" must not read as a
# successful empty-string answer - metrics.score(None) crashes downstream.
check("is_error:false with a null result is not ok",
      bench_run.parse_cli_json(json.dumps({"is_error": False, "result": None}))["ok"] is False)
check("is_error:false with a missing result is not ok",
      bench_run.parse_cli_json(json.dumps({"is_error": False}))["ok"] is False)

# --- G: report.py must exit cleanly (not a raw traceback) on a corrupt judgments file ---
with tempfile.TemporaryDirectory() as td_corrupt_cli:
    corrupt_cli = Path(td_corrupt_cli) / "judgments.json"
    corrupt_cli.write_text("{not valid json")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "report.py"),
         "--results", str(ROOT / "evals" / "snapshots" / "results.json"),
         "--judgments", str(corrupt_cli), "--no-gate"],
        capture_output=True, text=True,
    )
    check("corrupt judgments file exits non-zero", proc.returncode != 0)
    check("corrupt judgments file message names the file, not a raw traceback",
          "Traceback" not in proc.stderr and str(corrupt_cli) in (proc.stdout + proc.stderr))

# --- G: report.py must exit cleanly (not a raw traceback) on a corrupt results file ---
# bench_run.load_snapshot() has the identical unguarded json.loads() as
# _load_judgments() had before its own fix - main() called it four lines
# earlier with no try/except at all.
with tempfile.TemporaryDirectory() as td_corrupt_results:
    corrupt_results = Path(td_corrupt_results) / "results.json"
    corrupt_results.write_text("{not valid json")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "report.py"),
         "--results", str(corrupt_results), "--no-gate"],
        capture_output=True, text=True,
    )
    check("corrupt results file exits non-zero", proc.returncode != 0)
    check("corrupt results file message names the file, not a raw traceback",
          "Traceback" not in proc.stderr and str(corrupt_results) in (proc.stdout + proc.stderr))

# --- G: tests/stubs/claude-stub.sh must escape STUB_TEXT for the JSON it sits in ---
stub_env = dict(os.environ, STUB_TEXT='He said "stop".')
stub_out = subprocess.run(["bash", str(ROOT / "tests" / "stubs" / "claude-stub.sh")],
                          input="prompt", capture_output=True, text=True, env=stub_env)
try:
    stub_parsed = json.loads(stub_out.stdout)
    stub_ok = stub_parsed.get("result") == 'He said "stop".'
except ValueError:
    stub_ok = False
check("claude-stub.sh escapes a quote in STUB_TEXT so its JSON stays valid", stub_ok)

RESULTS = ROOT / "evals" / "snapshots" / "results.json"

# --- H: the article/aux rate gates require cross-model corroboration ---
# These two are density proxies, not observed defects: on the committed
# snapshot one half of baseline's reps fires the uncorroborated gate against
# baseline's own other half ~7% of the time, which at 16 buckets means a
# perfectly clean arm is expected to "fail". Requiring every model tested to
# show the drop removes that noise. The cost of the change must be zero
# sensitivity, so the drop-on-both case below has to keep firing.
ARTICLE_RICH = ("The service reads the file and the parser writes the record "
                "to the table for the user of the system.")   # 7 articles / 21 words
ARTICLE_STRIPPED = ("Service reads file and parser writes record to table for "
                    "user of system.")                        # 0 articles


def rate_snapshot(laconic_text_by_model):
    """One case, two models, baseline vs laconic. No auxiliary verbs in either
    text, so the aux gate finds no comparable baseline and stays silent."""
    runs = []
    for model in ("haiku", "sonnet"):
        runs.append({"case": "floor", "arm": "baseline", "model": model, "rep": 0,
                     "ok": True, "text": ARTICLE_RICH, "output_tokens": 10,
                     "total_cost_usd": 0.001, "duration_ms": 500})
        if model in laconic_text_by_model:
            runs.append({"case": "floor", "arm": "laconic", "model": model, "rep": 0,
                         "ok": True, "text": laconic_text_by_model[model],
                         "output_tokens": 10, "total_cost_usd": 0.001,
                         "duration_ms": 500})
    return {"metadata": {"reps": 1, "models": ["haiku", "sonnet"],
                         "laconic_level": "full", "rules_cksum": "1",
                         "generated_at": "x", "git_commit": "y",
                         "claude_cli_version": "z"},
            "arms": {"laconic": {"system_prompt": "r"}}, "runs": runs}


def article_gate_fails(laconic_text_by_model):
    agg_r = bench_report.aggregate(rate_snapshot(laconic_text_by_model))
    return [f for f in bench_report.gate_failures(agg_r, 0.70) if "article" in f]


# Sensitivity: the gate must still catch a genuine regression.
both_dropped = article_gate_fails({"haiku": ARTICLE_STRIPPED,
                                   "sonnet": ARTICLE_STRIPPED})
check("article gate fires when every model shows the drop",
      len(both_dropped) == 1)
check("the corroborated failure names the case and how many models agreed",
      both_dropped and "floor" in both_dropped[0] and "all 2 models" in both_dropped[0])

# Specificity: one model dropping is the noise pattern, not a regression.
check("article gate stays silent when only one model shows the drop",
      article_gate_fails({"haiku": ARTICLE_STRIPPED, "sonnet": ARTICLE_RICH}) == [])
check("article gate stays silent when no model shows the drop",
      article_gate_fails({"haiku": ARTICLE_RICH, "sonnet": ARTICLE_RICH}) == [])

# A single comparable model cannot corroborate itself. It must not fail the
# run, and it must not disappear either - reporting nothing would be a gate
# that silently checked nothing.
single_agg = bench_report.aggregate(rate_snapshot({"haiku": ARTICLE_STRIPPED}))
check("a case with only one comparable model does not fail the run",
      article_gate_fails({"haiku": ARTICLE_STRIPPED}) == [])
single_notes = [n for n in bench_report.gate_notes(single_agg, 0.70) if "article" in n]
check("a case with only one comparable model is reported as a note",
      len(single_notes) == 1 and "not gated" in single_notes[0])

# The whole point of the corroboration rule is that it costs no sensitivity
# on the real corpus: strip the articles out of every committed laconic
# response and the gate must still fire.
if RESULTS.exists():
    real_snap = json.loads(RESULTS.read_text())
    stripped_runs = []
    for r in real_snap["runs"]:
        r = dict(r)
        if r.get("arm") == "laconic" and r.get("ok"):
            r["text"] = re.sub(r"\b(the|a|an)\s+", "", r.get("text", ""), flags=re.I)
        stripped_runs.append(r)
    stripped_agg = bench_report.aggregate(dict(real_snap, runs=stripped_runs))
    stripped_fails = [f for f in bench_report.gate_failures(stripped_agg, 0.70)
                      if "article rate below" in f]
    real_agg = bench_report.aggregate(real_snap)
    real_article_fails = [f for f in bench_report.gate_failures(real_agg, 0.70)
                          if "article rate below" in f]
    # Most cases fire. The exceptions are not silent ones: a case whose haiku
    # baseline writes too few article words to clear ABS_COUNT_FLOOR is left
    # with one comparable model, and the gate reports that as not gated rather
    # than passing it. The invariant is that every case lands in exactly one of
    # the two buckets - caught, or named as uncheckable - which is what makes
    # "no article failure on the real snapshot" mean something. Asserted as a
    # partition rather than as a count, so adding a case cannot quietly turn a
    # newly-uncheckable case into a passing one.
    stripped_notes = [n for n in bench_report.gate_notes(stripped_agg, 0.70)
                      if "article rate not gated" in n]
    n_cases = len(set(r["case"] for r in bench_run.usable(real_snap["runs"])))
    check("stripping articles accounts for every case - caught (%d) or "
          "uncheckable (%d), across %d" % (len(stripped_fails),
                                           len(stripped_notes), n_cases),
          len(stripped_fails) + len(stripped_notes) == n_cases)
    check("the gate catches the clear majority once articles are stripped",
          len(stripped_fails) >= n_cases - 2)
    check("code-fidelity is named uncheckable, never silently passed",
          any("code-fidelity" in n for n in stripped_notes))
    check("corroborated gate reports no article failure on the committed snapshot",
          real_article_fails == [])

import levels as bench_levels  # noqa: E402

# The ladder verdict is the whole point of the cross-level run, so a tie must
# not read as a pass: two levels producing the same length is the "cumulative
# and distinct" claim failing quietly, which is a different finding from a
# reversal and must not be reported as one.
check("ladder: falling lengths are monotonic",
      bench_levels.ladder([900, 700, 400]) == "monotonic")
check("ladder: a reversal is broken",
      bench_levels.ladder([900, 400, 700]) == "broken")
check("ladder: a tie is called flat, never monotonic",
      bench_levels.ladder([900, 900, 400]) == "flat")
check("ladder: a missing level is incomplete, not a pass",
      bench_levels.ladder([900, None, 400]) == "incomplete")

# 11 of 22 is the actual result at the lite/full boundary, and it has to come
# back as a coin flip rather than as a direction.
check("sign test: an even split is p = 1", bench_levels.sign_test(11, 22) == 1.0)
check("sign test: a clean sweep is significant", bench_levels.sign_test(22, 22) < 0.001)
check("sign test: symmetric in k", bench_levels.sign_test(4, 22) == bench_levels.sign_test(18, 22))

# The structure/arrow correlation is a published figure, so the estimator
# behind it gets checked rather than trusted.
check("pearson: a perfect line is 1", abs(bench_levels.pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-9)
check("pearson: a perfect inverse is -1",
      abs(bench_levels.pearson([1, 2, 3], [6, 4, 2]) + 1.0) < 1e-9)
check("pearson: a constant series is 0, not a division error",
      bench_levels.pearson([1, 1, 1], [3, 5, 9]) == 0.0)

# arrow_rows is per response and laconic-only: pooling the control arms into it
# would report the foil's arrows as laconic's.
_arrow_views = {"lite": (None, [
    {"arm": "laconic", "case": "walkthrough", "model": "haiku",
     "text": "1. **A** calls x -> needs y\n2. then z\n"},
    {"arm": "word-compression", "case": "walkthrough", "model": "haiku",
     "text": "req -> resp -> done\n"},
], None)}
_rows = bench_levels.arrow_rows(_arrow_views, ["lite"])
check("arrow_rows keeps the laconic arm only", len(_rows) == 1)
check("arrow_rows counts the arrow in a numbered step", _rows[0]["arrows"] == 1)
check("arrow_rows counts that response's structure", _rows[0]["structure"] == 3)

import subagent as bench_subagent  # noqa: E402

# Fisher is what decides whether an arm difference in the relay run is real,
# so it is checked against tables enumerated by hand rather than assumed.
# [[1,9],[11,3]]: n=24, C(24,12)=2704156, and the tables at least as extreme
# as the observed one are x in {0,1,9,10}, summing to 7462.
check("fisher: symmetric 3/1 table", round(bench_subagent.fisher_exact(3, 1, 1, 3), 4) == 0.4857)
check("fisher: 1,9,11,3 matches the hand enumeration",
      round(bench_subagent.fisher_exact(1, 9, 11, 3), 6) == round(7462 / 2704156, 6))
check("fisher: no difference is p = 1", bench_subagent.fisher_exact(5, 5, 5, 5) == 1.0)
check("fisher: a clean separation is significant",
      bench_subagent.fisher_exact(10, 0, 0, 10) < 0.001)
# An empty margin has no alternative table to compare against. Returning
# something below 1 there would manufacture significance out of a missing arm.
check("fisher: an empty margin is p = 1, never significant",
      bench_subagent.fisher_exact(0, 0, 3, 3) == 1.0)

# The relay prompt must not name the arm, the level, or the plugin: the whole
# comparison rests on the parent being unable to tell which arm wrote the
# report it was handed.
low = bench_subagent.RELAY.lower()
check("relay prompt is blind to the arm",
      not any(w in low for w in ("laconic", "lite", "ultra", "baseline", "terse", "concise")))
check("relay prompt has exactly two substitution slots",
      bench_subagent.RELAY.count("%s") == 2)
# Without this the parent hunts for files in an empty scratch dir and answers
# "I need the repository" in every arm alike, measuring the harness instead of
# the handoff.
check("relay prompt tells the parent it cannot see the files",
      "cannot see the codebase" in low)

# never_cut accounting must exclude cases carrying no tokens from both the
# numerator and the denominator, or "0 failures" reads as "every response
# verified" when most cases verify nothing.
# The first text must carry every keyword destructive's expect.json lists -
# cascade, invoices and sessions - or this checks the wrong thing: it is here to
# show that fail-open leaves the denominator alone, not to count a miss.
nc_runs = [{"case": "destructive",
            "text": "the cascade reaches invoices and sessions"},
           {"case": "destructive", "text": "it deletes some rows"},
           {"case": "fail-open", "text": "anything at all"}]
check("never-cut counts only cases with tokens",
      bench_subagent._never_cut(nc_runs) == (2, 1))
check("never-cut on no eligible case reports nothing checked",
      bench_subagent._never_cut([{"case": "fail-open", "text": "x"}]) == (0, 0))

# --- prefer.py: blind pairwise preference ---
# The comparison rests on the judge being unable to tell which side is the
# plugin, and on the A/B layout being decided by the comparison rather than by
# the arm. Both are checked here rather than in review, because either failure
# still produces a full snapshot of plausible-looking verdicts.
import prefer as bench_prefer  # noqa: E402

check("preference prompt is blind to the arm",
      not any(w in bench_prefer.TEMPLATE.lower()
              for w in ("laconic", "baseline", "terse", "concise", "plugin")))
check("preference prompt has exactly three substitution slots",
      bench_prefer.TEMPLATE.count("%s") == 3)
# Length is the thing under test. A judge told that shorter is better would
# return laconic's own thesis rather than a reader's preference.
check("preference prompt does not tell the judge which length to prefer",
      "virtue or a fault" in bench_prefer.TEMPLATE)

keys = [("case%d" % i, "sonnet", i % 5) for i in range(110)]
a_side = [bench_prefer.treatment_is_a(c, m, r, 0) for c, m, r in keys]
check("A/B assignment is deterministic",
      a_side == [bench_prefer.treatment_is_a(c, m, r, 0) for c, m, r in keys])
check("A/B assignment is not one-sided", 20 < sum(a_side) < 90)
# order=1 has to be the exact inverse, not a second hash: a flipped pass that
# repeats the original position for half the subset dilutes the flip rate with
# comparisons that never flipped.
check("the flipped order inverts every comparison",
      all(bench_prefer.treatment_is_a(c, m, r, 1) is not
          bench_prefer.treatment_is_a(c, m, r, 0) for c, m, r in keys))

check("parses a winner", bench_prefer.parse_winner('{"winner":"A","reason":"x"}')["winner"] == "A")
check("tie is a first-class verdict",
      bench_prefer.parse_winner('{"winner":"tie","reason":"x"}')["winner"] == "tie")
check("garbage has no winner", bench_prefer.parse_winner("not json")["winner"] is None)
check("an unknown verdict has no winner",
      bench_prefer.parse_winner('{"winner":"C"}')["winner"] is None)

check("position A maps to the treatment when the treatment is A",
      bench_prefer.winning_arm("A", "laconic", "baseline", True) == "laconic")
check("position A maps to the control when the treatment is B",
      bench_prefer.winning_arm("A", "laconic", "baseline", False) == "baseline")
check("position B maps to the treatment when the treatment is B",
      bench_prefer.winning_arm("B", "laconic", "baseline", False) == "laconic")
check("a tie stays a tie in either layout",
      bench_prefer.winning_arm("tie", "laconic", "baseline", True) == "tie")
check("an unparseable verdict names no winner",
      bench_prefer.winning_arm(None, "laconic", "baseline", True) is None)

sub = bench_prefer.both_orders_subset(list(range(100)), 10)
check("both-orders subset is the size asked for", len(sub) == 10)
check("both-orders subset spans the range, not a prefix", max(sub) > 50)
check("both-orders subset caps at what exists",
      bench_prefer.both_orders_subset([1, 2], 10) == [1, 2])
check("both-orders 0 asks for nothing", bench_prefer.both_orders_subset([1, 2], 0) == [])

recs = [{"case": "a", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"},
        {"case": "a", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": "baseline"},
        {"case": "b", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "tie"},
        {"case": "b", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": "tie"},
        {"case": "c", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"}]
check("the flip rate counts only comparisons run in both orders",
      bench_prefer.flip_rate(recs) == (1, 2))

# The headline tally is only readable if the treatment won at similar rates from
# both sides, so the split has to be reported, not inferred.
pos_recs = [{"order": 0, "treatment_position": "A", "winner_arm": "laconic"},
            {"order": 0, "treatment_position": "A", "winner_arm": "baseline"},
            {"order": 0, "treatment_position": "B", "winner_arm": "laconic"},
            {"order": 0, "treatment_position": "B", "winner_arm": "tie"},
            {"order": 1, "treatment_position": "A", "winner_arm": "laconic"}]
check("wins split by position, flipped pass excluded",
      bench_prefer.by_position(pos_recs, "laconic", "baseline")
      == {"A": (1, 1, 0), "B": (1, 0, 1)})

# The length bias is what decides whether a treatment loss may be read as a
# preference at all, so it is measured per run. A tie has no winner to compare
# and an equal-length pair has no longer answer: counting either would move the
# rate toward 50% and hide the bias it exists to expose.
len_recs = [{"case": "a", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "baseline"},
            {"case": "b", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"},
            {"case": "c", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "tie"},
            {"case": "d", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"},
            {"case": "a", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": "laconic"}]
lengths = {(("a", "sonnet", 0), "laconic"): 10, (("a", "sonnet", 0), "baseline"): 99,
           (("b", "sonnet", 0), "laconic"): 99, (("b", "sonnet", 0), "baseline"): 10,
           (("c", "sonnet", 0), "laconic"): 10, (("c", "sonnet", 0), "baseline"): 99,
           (("d", "sonnet", 0), "laconic"): 42, (("d", "sonnet", 0), "baseline"): 42}
check("the length bias counts decided, unequal-length comparisons only",
      bench_prefer.longer_won(len_recs, lengths, "laconic", "baseline") == (2, 2))
check("response lengths key on (case, model, rep) and arm",
      bench_prefer.response_lengths(
          {"runs": [{"case": "a", "model": "sonnet", "rep": 0, "arm": "laconic",
                     "text": "abc", "ok": True}]}) == {(("a", "sonnet", 0), "laconic"): 3})
# Counting the flipped pass again would double-count the same pair of responses
# and inflate whichever side the judge favours in position A.
check("the tally counts each comparison once, not once per order",
      bench_prefer.tally(recs, "laconic", "baseline")
      == {"laconic": 2, "baseline": 0, "tie": 1, "unparseable": 0})

# --- run.py: carrying control arms between rounds ---
# A rule edit changes the laconic arm and nothing else, so regenerating the
# controls each round would pay three times over for runs that cannot have
# moved. The provenance stamp is the point: the mixed-snapshot caveat the
# benchmark discloses by hand travels with the data instead.
src = {"metadata": {"rules_cksum": "111"},
       "runs": [{"case": "a", "arm": "baseline", "model": "sonnet", "rep": 0, "ok": True, "text": "b"},
                {"case": "a", "arm": "laconic", "model": "sonnet", "rep": 0, "ok": True, "text": "l"},
                {"case": "a", "arm": "terse-control", "model": "sonnet", "rep": 0, "ok": True, "text": "t"}]}
carried = bench_run.carry_arms({"metadata": {"rules_cksum": "222"}, "runs": []}, src, ["laconic"])
check("carried snapshot takes the control arms",
      sorted(r["arm"] for r in carried["runs"]) == ["baseline", "terse-control"])
check("carried snapshot does not take the treatment arm",
      all(r["arm"] != "laconic" for r in carried["runs"]))
check("carrying stamps the source and its cksum",
      carried["metadata"]["carried_arms_from"]["rules_cksum"] == "111"
      and carried["metadata"]["carried_arms_from"]["arms"] == ["baseline", "terse-control"])
# Failed runs are excluded from every statistic; carrying them in would
# reintroduce them under a fresh snapshot's provenance.
src_bad = {"metadata": {"rules_cksum": "111"},
           "runs": [{"case": "a", "arm": "baseline", "model": "sonnet", "rep": 0, "ok": False}]}
check("carrying skips failed runs",
      bench_run.carry_arms({"metadata": {}, "runs": []}, src_bad, ["laconic"])["runs"] == [])

# --- review.py: the failure inventory ---
import review as bench_review  # noqa: E402

RULES_STUB = """## Never cut

- Code, config, commands, and error strings - verbatim and complete.

## Never do this

No dropped articles. No arrows standing in for conjunctions in running prose.
"""
check("a readability failure resolves to the rule that bans it",
      "arrows" in bench_review.governing_rule(RULES_STUB, "symbol_connectors")[1])
check("a never-cut failure resolves to the never-cut bullet",
      "verbatim" in bench_review.governing_rule(RULES_STUB, "never_cut")[1])
# A benchmark expecting behaviour the rule set never mentions is a more useful
# finding than another instance of a rule being disobeyed, so it does not just
# get reported - it ranks first.
check("a failure the rules never mention has no governing rule",
      bench_review.governing_rule(RULES_STUB, "quality") is None)
check("unruled outranks every other class", bench_review.CLASS_ORDER[0] == "unruled")
check("never-cut outranks quality, readability and preference",
      bench_review.CLASS_ORDER.index("never-cut")
      < min(bench_review.CLASS_ORDER.index(c)
            for c in ("quality", "readability", "preference")))

snap_stub = {"runs": [
    {"case": "badnews", "arm": "laconic", "model": "sonnet", "rep": 0, "ok": True,
     "text": "Three tests fail -> see the log."},
    {"case": "badnews", "arm": "baseline", "model": "sonnet", "rep": 0, "ok": True,
     "text": "Control arms carry no rules, so a control failure is not actionable -> never reviewed."}]}
rev = bench_review.findings(snap_stub, [], [], RULES_STUB)
check("only the treatment arm is reviewed", rev and all(x["case"] == "badnews" for x in rev))
check("the finding quotes the offending span", any("->" in x["excerpt"] for x in rev))
check("a never-cut miss is found and ranked above readability",
      [x["class"] for x in rev][0] == "never-cut")
# decision is graded rule-adherence: optimizing rules against a case that
# grades adherence to those rules is circular, so it is flagged, not ranked.
check("a rule-adherence case is marked unoptimizable",
      bench_review.findings(
          {"runs": [{"case": "decision", "arm": "laconic", "model": "sonnet", "rep": 0,
                     "ok": True, "text": "Do X -> then Y."}]}, [], [], RULES_STUB
      )[0]["optimizable"] is False)
check("an empty round renders as nothing to propose from",
      "Nothing to propose" in bench_review.render([]))
# unruled means the rule set is silent where the benchmark checks. A wrong
# answer is not that, and classing every quality failure as unruled would bury
# the signal under the largest category in the run.
judg_stub = [{"case": "fail-open", "arm": "laconic", "model": "sonnet", "rep": 0,
              "verdict": "fail", "quote": "blamed the window arithmetic", "reason": ""}]
qf = bench_review.findings({"runs": []}, judg_stub, [], RULES_STUB)
check("a quality failure is classed quality, not unruled",
      [f["class"] for f in qf] == ["quality"])
check("a quality failure carries no governing rule", qf[0]["rule"] is None)
# Only a rule-class failure can be unruled, and only when its rule is absent.
check("a readability failure with no matching rule is unruled",
      bench_review.findings(
          {"runs": [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
                     "ok": True, "text": "Do X -> then Y."}]},
          [], [], "## Never cut\n\n- Nothing about symbols here.\n")[0]["class"]
      == "unruled")

# --- report.py --against: the accept rule ---
import report as bench_report  # noqa: E402

TEN_CELLS = lambda v: {(c, "sonnet"): v for c in "abcdefghij"}  # noqa: E731


def _summary(nc=0, qf=0, sf=0, viol=0, tokens=None, flip=0.2, n_runs=110):
    return {"never_cut_failures": nc, "quality_fails": qf, "safety_fails": sf,
            "violations_total": viol,
            "tokens": TEN_CELLS(100) if tokens is None else tokens, "flip_rate": flip,
            "n_runs": n_runs}


worse = _summary(tokens=TEN_CELLS(500))
v, why = bench_report.accept_verdict(worse, _summary(tokens=TEN_CELLS(100)), "output_tokens")
check("a clean improvement past the noise floor is accepted", v == "accept")

for kw, label in (("nc", "never-cut"), ("qf", "quality"), ("sf", "safety"),
                  ("viol", "readability")):
    v, why = bench_report.accept_verdict(
        worse, _summary(tokens=TEN_CELLS(100), **{kw: 1}), "output_tokens")
    check("a lost %s verdict rejects on its own" % label, v == "reject")
    check("the rejection names the %s failure" % label,
          any(label in r for r in why))

# 10 tokens off a 100-token median is well inside the published 175-token
# stdev. A loop that accepts a move this size churns forever on noise.
v, why = bench_report.accept_verdict(_summary(tokens=TEN_CELLS(100)),
                                     _summary(tokens=TEN_CELLS(90)), "output_tokens")
check("a move inside the noise floor is rejected", v == "reject")
check("the rejection names the noise floor", any("noise floor" in r for r in why))

# Every cell moving the wrong way must reject even when the median improves,
# which cannot happen here - but a split decision can.
split = dict(TEN_CELLS(100))
for c in "abcde":
    split[(c, "sonnet")] = 900
v, why = bench_report.accept_verdict(_summary(tokens=TEN_CELLS(500)),
                                     _summary(tokens=split), "output_tokens")
check("a split result fails the sign test", v == "reject")

# Preference is admissible but never decisive: it cannot reject an edit that
# passed every deterministic gate, and a noisy round cannot cite it either way.
v, why = bench_report.accept_verdict(worse, _summary(tokens=TEN_CELLS(100), flip=0.6),
                                     "output_tokens")
check("a high flip rate does not reject an otherwise-passing edit", v == "accept")
check("a high flip rate is disclosed in the reasons", any("flip rate" in r for r in why))

# round_summary reads one round's artefacts into the four numbers the decision
# needs. The flip rate counts only comparisons present in both orders.
rs = bench_report.round_summary(
    {"runs": [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
               "ok": True, "text": "Fine.", "output_tokens": 10}]},
    [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0, "verdict": "fail"}],
    [{"case": "floor", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"},
     {"case": "floor", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": "baseline"}])
# --- a count target gets a real test, not a silent pass ---
# 7 -> 0 over equal exposure is p = 0.5^7; 7 -> 3 is p = 0.17 and must reject,
# or the loop banks a move it cannot distinguish from where the arrows landed.
v, why = bench_report.accept_verdict(_summary(viol=7), _summary(viol=0), "violations_total")
check("a count target clearing the binomial test is accepted", v == "accept")
check("the acceptance reports the count and its p", any("7 -> 0" in r for r in why))

v, why = bench_report.accept_verdict(_summary(viol=7), _summary(viol=3), "violations_total")
check("a count move inside sampling noise is rejected", v == "reject")

# Exposure is not assumed equal: the same 7 -> 1 is only evidence if the second
# round actually ran comparable numbers of responses.
v, _ = bench_report.accept_verdict(_summary(viol=7), _summary(viol=1, n_runs=110),
                                   "violations_total")
check("7 -> 1 at equal exposure is accepted", v == "accept")
v, why = bench_report.accept_verdict(_summary(viol=7), _summary(viol=1, n_runs=12),
                                     "violations_total")
check("the same drop on a tenth of the runs is rejected", v == "reject")

# A metric already at 0 cannot be shown to fall, and must not read as confirmed.
v, why = bench_report.accept_verdict(_summary(nc=0), _summary(nc=0), "never_cut_failures")
check("a target already at 0 is rejected", v == "reject")
check("the rejection says there was nothing to improve",
      any("already 0" in r for r in why))

# The bug this replaced: an unrecognized target skipped every statistical gate
# and returned accept for any round that merely failed to regress.
v, why = bench_report.accept_verdict(_summary(viol=7), _summary(viol=7), "readability")
check("an unknown target rejects instead of silently passing", v == "reject")
check("the rejection names the unknown target", any("unknown target" in r for r in why))

check("round_summary reads the treatment tokens", rs["tokens"] == {("floor", "sonnet"): 10})
check("round_summary computes the flip rate", rs["flip_rate"] == 1.0)
# floor is graded rule-adherence, so its judge failure is not a quality loss.
check("round_summary counts only quality-graded judge failures", rs["quality_fails"] == 0)
# ...and it is not a safety loss either. rule-adherence counts nowhere: its
# criteria are laconic's own prohibitions restated, so an edit tuned against
# them is tuned against the text it was handed.
check("a rule-adherence judge failure is not counted as a safety loss",
      rs["safety_fails"] == 0)

# --- safety_fails: the gate destructive/haiku spent three rounds behind ---
# The failure this counter exists for names its never-cut keywords and then
# calls the cascade harmless. never_cut_failures is a substring check, so it
# sees both words and passes; quality_fails skips the case because destructive
# is graded safety. Before this counter, nothing in the round rejected on it.
NAMED_THEN_DISMISSED = ("The `invoices` foreign key blocks the drop. "
                        "The `sessions` table is safe (it has `ON DELETE CASCADE`).")
rs_safety = bench_report.round_summary(
    {"runs": [{"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 0,
               "ok": True, "text": NAMED_THEN_DISMISSED, "output_tokens": 10}]},
    [{"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 0,
      "verdict": "fail"}])
check("a response that names its never-cut keywords passes the substring check",
      rs_safety["never_cut_failures"] == 0)
check("the same response's lost safety verdict is counted",
      rs_safety["safety_fails"] == 1)
check("a safety-graded failure is not double-counted as a quality one",
      rs_safety["quality_fails"] == 0)

# A hypothesis may name it, the same as the other three counters.
check("safety_fails is an admissible target", "safety_fails" in bench_report.COUNT_TARGETS)
v, why = bench_report.accept_verdict(_summary(sf=6), _summary(sf=0), "safety_fails")
check("a safety_fails target clearing the binomial test is accepted", v == "accept")
check("the acceptance reports the safety count", any("safety_fails 6 -> 0" in r for r in why))
v, why = bench_report.accept_verdict(_summary(sf=6), _summary(sf=4), "safety_fails")
check("a safety_fails move inside sampling noise is rejected", v == "reject")

# Only the treatment arm. A control's safety failure is not the rules' doing,
# and counting it would let a noisy baseline reject an edit.
rs_control = bench_report.round_summary(
    {"runs": [{"case": "destructive", "arm": "baseline", "model": "haiku", "rep": 0,
               "ok": True, "text": NAMED_THEN_DISMISSED, "output_tokens": 10}]},
    [{"case": "destructive", "arm": "baseline", "model": "haiku", "rep": 0,
      "verdict": "fail"}])
check("a control arm's safety failure is not counted", rs_control["safety_fails"] == 0)

# --- --target-cases: scoring the target on the cases a hypothesis named ---
# Round 03 is the reason this exists. It moved walkthrough and ordered-steps 21
# arrows to 5 and the whole-round sum could only report 26 to 20 at p = 0.231,
# so the loop had no way to score the hypothesis it actually wrote.


def _scoped(nc=0, qf=0, sf=0, viol=0, cases=("walkthrough", "ordered-steps"),
            s_nc=0, s_qf=0, s_sf=0, s_viol=0, n_runs=110, s_runs=20, flip=0.2):
    s = _summary(nc=nc, qf=qf, sf=sf, viol=viol, n_runs=n_runs, flip=flip)
    s["scoped"] = {"never_cut_failures": s_nc, "quality_fails": s_qf,
                   "safety_fails": s_sf, "violations_total": s_viol,
                   "n_runs": s_runs, "cases": sorted(cases)}
    return s


CASES2 = ["ordered-steps", "walkthrough"]
v, why = bench_report.accept_verdict(
    _scoped(viol=26, s_viol=21), _scoped(viol=20, s_viol=5),
    "violations_total", target_cases=CASES2)
check("a scoped count target scores the named cases, not the round", v == "accept")
check("the scoped line names the cases", any("on ordered-steps, walkthrough" in r for r in why))
check("the scoped line still discloses the round-wide count",
      any("round-wide 26 -> 20" in r for r in why))

# The fatal conditions stay round-wide: fixing two cases while breaking a third
# is still a rejection, and the scoped target must not rescue it.
v, why = bench_report.accept_verdict(
    _scoped(viol=26, s_viol=21), _scoped(viol=30, s_viol=5, nc=1),
    "violations_total", target_cases=CASES2)
check("a round-wide never-cut loss rejects a passing scoped target", v == "reject")
check("a round-wide readability rise rejects a passing scoped target",
      any("readability lost" in r for r in why))

# Scoped exposure is the scoped exposure. Reading n_runs from the whole round
# would treat 20 responses as 110 chances to fail and inflate every p.
v, why = bench_report.accept_verdict(
    _scoped(viol=26, s_viol=6, s_runs=20), _scoped(viol=20, s_viol=1, s_runs=4),
    "violations_total", target_cases=CASES2)
check("a scoped drop on a fifth of the scoped runs is rejected", v == "reject")

# A summary built without the scope cannot be scored against one that has it.
v, why = bench_report.accept_verdict(
    _summary(viol=26), _scoped(viol=20, s_viol=5), "violations_total",
    target_cases=CASES2)
check("an unscoped summary rejects rather than falling back to the round",
      v == "reject" and any("same scope" in r for r in why))

# Scoped output_tokens is offered from 6 cells up: sign_test(4, 4) = 0.125 and
# sign_test(5, 5) = 0.0625 can never reach alpha, so smaller scopes are still
# refused - with the arithmetic printed rather than a blanket no.
SCOPE3 = ["badnews", "ordered-steps", "walkthrough"]
STDEV3 = {("badnews", "sonnet"): 75.8, ("ordered-steps", "sonnet"): 138.5,
          ("walkthrough", "sonnet"): 1519.1}


def _tok6(bn_h, bn_s, os_h, os_s, wt_h, wt_s):
    t = TEN_CELLS(500)
    t.update({("badnews", "haiku"): bn_h, ("badnews", "sonnet"): bn_s,
              ("ordered-steps", "haiku"): os_h, ("ordered-steps", "sonnet"): os_s,
              ("walkthrough", "haiku"): wt_h, ("walkthrough", "sonnet"): wt_s})
    return t


def _scoped_tok(tokens, stdev=None, cases=SCOPE3, **kw):
    s = _scoped(cases=cases, **kw)
    s["tokens"] = tokens
    if stdev is not None:
        s["tokens_stdev"] = stdev
    return s


# Round 01's real scoped cells: median 856, sonnet-cell floor 138.5.
base6 = _scoped_tok(_tok6(442, 439, 653, 1059, 1163, 3666), stdev=STDEV3)

v, why = bench_report.accept_verdict(
    base6, _scoped_tok(_tok6(380, 400, 500, 700, 900, 1700)),
    "output_tokens", target_cases=SCOPE3)
check("a 6-cell sweep past the scoped floor is accepted", v == "accept")
check("the scoped token line names its floor",
      any("scoped floor 138.5" in r for r in why))
check("the scoped token line discloses the round-wide cells",
      any("round-wide" in r for r in why))

v, why = bench_report.accept_verdict(
    base6, _scoped_tok(_tok6(380, 450, 500, 700, 900, 1700)),
    "output_tokens", target_cases=SCOPE3)
check("5 of 6 scoped cells fails the sign test at p = 0.219",
      v == "reject" and any("p = 0.219" in r for r in why))

v, why = bench_report.accept_verdict(
    base6, _scoped_tok(_tok6(441, 438, 652, 1058, 1162, 3660)),
    "output_tokens", target_cases=SCOPE3)
check("a 6-cell sweep inside the scoped floor is rejected on magnitude",
      v == "reject" and any("scoped noise floor" in r for r in why))

v, why = bench_report.accept_verdict(
    base6, _scoped_tok(_tok6(380, 400, 500, 700, 900, 1700), nc=1),
    "output_tokens", target_cases=SCOPE3)
check("a round-wide never-cut loss rejects a passing scoped token target",
      v == "reject" and any("never-cut" in r for r in why))

four = {("ordered-steps", m): 100 for m in ("haiku", "sonnet")}
four.update({("walkthrough", m): 100 for m in ("haiku", "sonnet")})
v, why = bench_report.accept_verdict(
    _scoped_tok(dict(four), stdev={("walkthrough", "sonnet"): 100.0},
                cases=CASES2),
    _scoped_tok({k: v_ - 90 for k, v_ in four.items()}, cases=CASES2),
    "output_tokens", target_cases=CASES2)
check("a 4-cell scope is still refused, with the arithmetic",
      v == "reject" and any("at least 6" in r and "p = 0.125" in r for r in why))

haiku6 = {(c, "haiku"): 100 for c in "abcdef"}
v, why = bench_report.accept_verdict(
    _scoped_tok(dict(haiku6), stdev={}, cases=list("abcdef")),
    _scoped_tok({k: 10 for k in haiku6}, cases=list("abcdef")),
    "output_tokens", target_cases=list("abcdef"))
check("a scope with no sonnet cell in the baseline has no floor and refuses",
      v == "reject" and any("no sonnet cell" in r for r in why))

# round_summary's scope is an addition, never a replacement.
rs_scoped = bench_report.round_summary(
    {"runs": [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
               "ok": True, "text": "Do X -> then Y.", "output_tokens": 10},
              {"case": "walkthrough", "arm": "laconic", "model": "sonnet", "rep": 0,
               "ok": True, "text": "First A -> then B -> then C.", "output_tokens": 10}]},
    [], None, target_cases=["walkthrough"])
check("round_summary keeps the round-wide count beside the scoped one",
      rs_scoped["violations_total"] == 3)
check("round_summary scopes the count to the named case",
      rs_scoped["scoped"]["violations_total"] == 2)
check("round_summary scopes the exposure too", rs_scoped["scoped"]["n_runs"] == 1)

# safety_fails scopes like the other counters, which is what a hypothesis about
# destructive alone needs. The round-wide count still rejects on its own: an
# edit that fixes destructive while breaking ordered-steps is not an
# improvement to the never-cut contract, it is a trade.
v, why = bench_report.accept_verdict(
    _scoped(sf=6, s_sf=6, cases=("destructive",), s_runs=10),
    _scoped(sf=0, s_sf=0, cases=("destructive",), s_runs=10),
    "safety_fails", target_cases=["destructive"])
check("a scoped safety_fails target scores the named case", v == "accept")
check("the scoped safety line names the case", any("on destructive" in r for r in why))
v, why = bench_report.accept_verdict(
    _scoped(sf=6, s_sf=6, cases=("destructive",), s_runs=10),
    _scoped(sf=7, s_sf=0, cases=("destructive",), s_runs=10),
    "safety_fails", target_cases=["destructive"])
check("fixing the scoped case while the round-wide safety count rises rejects",
      v == "reject" and any("safety lost (6 -> 7)" in r for r in why))

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
