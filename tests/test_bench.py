#!/usr/bin/env python3
"""Validates harness logic against stubs - no live model calls."""
import glob
import json
import pathlib
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
import metrics as bench_metrics  # noqa: E402

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

# --- #142: stream-json capture records which tools a response invoked ---
# num_turns (#49) counts agentic loop iterations, so a file read and a file
# edit are the same integer. The CLI's stream-json format emits every
# assistant message as its own event, tool_use blocks included, and closes
# with the same result object --output-format json returns whole. The record
# shape therefore stays defined in exactly one place - parse_cli_json - and
# the stream parser adds only the field the flat format cannot carry.


def _sj(*events):
    """Serialise events the way the CLI emits them: one JSON object per line."""
    return "".join(json.dumps(e) + "\n" for e in events)


def _sj_assistant(*blocks):
    return {"type": "assistant", "message": {"content": list(blocks)}}


def _sj_tool(name):
    return {"type": "tool_use", "name": name, "input": {}}


SJ_RESULT = {"type": "result", "subtype": "success", "is_error": False,
             "result": "the answer", "num_turns": 3, "total_cost_usd": 0.0096,
             "duration_ms": 2089,
             "usage": {"input_tokens": 10, "output_tokens": 33,
                       "cache_creation_input_tokens": 3573,
                       "cache_read_input_tokens": 17615}}

# Shaped like a real transcript, including the part that catches a naive
# parser: the result event is not the last line. Claude Code emits a
# task_summary after it, so "decode the last line" reads a system event and
# records every run in the round as failed.
SJ_GOOD = _sj(
    {"type": "system", "subtype": "init"},
    _sj_assistant({"type": "thinking", "thinking": "..."}),
    _sj_assistant(_sj_tool("Write")),
    {"type": "user", "message": {"content": [{"type": "tool_result"}]}},
    _sj_assistant(_sj_tool("Bash")),
    _sj_assistant({"type": "text", "text": "the answer"}),
    SJ_RESULT,
    {"type": "system", "subtype": "task_summary"},
)

streamed = bench_run.parse_cli_stream(SJ_GOOD)
check("stream: a result event followed by more events is still found",
      streamed["ok"] is True and streamed["text"] == "the answer")
check("stream: the result event's usage is read the way the flat format's is",
      streamed["output_tokens"] == 33 and streamed["num_turns"] == 3)
check("stream: every other field is exactly what parse_cli_json makes of the "
      "same result object",
      {k: v for k, v in streamed.items() if k != "tools"}
      == bench_run.parse_cli_json(json.dumps(SJ_RESULT)))
check("stream: tool names are recorded in the order they were invoked",
      streamed["tools"] == ["Write", "Bash"])
check("stream: an answer that invoked nothing records an empty tool list",
      bench_run.parse_cli_stream(_sj(SJ_RESULT))["tools"] == [])
check("stream: two tool_use blocks in one assistant message both count",
      bench_run.parse_cli_stream(
          _sj(_sj_assistant(_sj_tool("Read"), _sj_tool("Grep")), SJ_RESULT))["tools"]
      == ["Read", "Grep"])
# Only the assistant's own blocks are actions it took. The transcript echoes
# each call back inside the following user event, and counting that copy
# would double every tool in the run.
check("stream: a tool_use block outside an assistant event does not count",
      bench_run.parse_cli_stream(
          _sj({"type": "user", "message": {"content": [_sj_tool("Read")]}},
              SJ_RESULT))["tools"] == [])
# A stream killed by the timeout ends mid-transcript with no result event.
# Nothing usable came back, and recording that as a very short answer is the
# failure run.py's own docstring names.
check("stream: a truncated stream carrying no result event is not ok",
      bench_run.parse_cli_stream(
          _sj({"type": "system", "subtype": "init"},
              _sj_assistant(_sj_tool("Read"))))["ok"] is False)
check("stream: an is_error result event is not ok",
      bench_run.parse_cli_stream(_sj(dict(SJ_RESULT, is_error=True)))["ok"] is False)
# usable() filters failed runs out of every statistic, so this cannot reach a
# score. It is the diagnostic: a cell that failed after four tool calls and
# one that failed before making any are different failures.
check("stream: a failed run still records the tools it got through",
      bench_run.parse_cli_stream(
          _sj(_sj_assistant(_sj_tool("Read")), dict(SJ_RESULT, is_error=True)))["tools"]
      == ["Read"])
check("stream: a line that is not JSON is skipped rather than fatal",
      bench_run.parse_cli_stream(
          "not json\n" + _sj(_sj_assistant(_sj_tool("Read")), SJ_RESULT))["tools"]
      == ["Read"])
check("stream: a JSON line that is not an object is skipped rather than fatal",
      bench_run.parse_cli_stream("[1, 2]\n" + _sj(SJ_RESULT))["ok"] is True)
check("stream: empty output is not ok",
      bench_run.parse_cli_stream("")["ok"] is False)
check("stream: a failed parse still carries a tool list, so no reader has to "
      "test for the key",
      bench_run.parse_cli_stream("")["tools"] == [])

check("arms include all five",
      sorted(bench_run.ARMS) == ["baseline", "concise-style", "laconic",
                                 "terse-control", "word-compression"])
check("baseline has no system prompt", bench_run.ARMS["baseline"] is None)
check("terse control is exactly the control instruction",
      bench_run.ARMS["terse-control"] == "Answer concisely.")

# The native-output-style arm is delivered by --settings, not by an appended
# system prompt. If it ever acquired a system_prompt it would be getting the
# style twice over - once natively and once as text - and would stop being a
# measurement of what Claude Code ships.
check("concise-style maps to the built-in Concise output style",
      bench_run.ARM_OUTPUT_STYLES == {"concise-style": "Concise"})
check("concise-style carries no system prompt of its own",
      bench_run.ARMS["concise-style"] is None)
check("no arm both appends a system prompt and sets an output style",
      all(not bench_run.ARMS[a] for a in bench_run.ARM_OUTPUT_STYLES))
check("every styled arm is a real arm",
      set(bench_run.ARM_OUTPUT_STYLES) <= set(bench_run.ARMS))

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
        # #142: the format that carries tool names. --verbose is not optional
        # here - under --print the CLI refuses --output-format stream-json
        # without it, verified against 2.1.241, so dropping it fails every
        # call in the round rather than quietly falling back.
        check("call() asks for the stream format that carries tool names",
              argv_tail[argv_tail.index("--output-format") + 1] == "stream-json")
        check("call() passes the --verbose the stream format requires",
              "--verbose" in argv_tail)

        argv_no_prompt = Path(td_argv) / "argv-no-prompt.txt"
        os.environ["STUB_ARGV_OUT"] = str(argv_no_prompt)
        bench_run.call(resolved_rel, "haiku", "test", None, "/tmp")
        argv_tail_none = argv_no_prompt.read_text().splitlines()[3:]
        check("system_prompt=None produces no --append-system-prompt flag at all",
              "--append-system-prompt" not in argv_tail_none)

        # The output-style arm rides on --settings, and an unrecognised style
        # is silently ignored by the CLI rather than rejected. If the flag
        # stopped being attached, the arm would run as plain baseline and the
        # round would report the native style making no difference.
        argv_style = Path(td_argv) / "argv-style.txt"
        os.environ["STUB_ARGV_OUT"] = str(argv_style)
        bench_run.call(resolved_rel, "haiku", "test", None, "/tmp",
                       output_style="Concise")
        argv_tail_style = argv_style.read_text().splitlines()[3:]
        check("output_style is passed as a --settings JSON object naming it",
              "--settings" in argv_tail_style and
              json.loads(argv_tail_style[argv_tail_style.index("--settings") + 1])
              == {"outputStyle": "Concise"})
        check("an output-style call still appends no system prompt",
              "--append-system-prompt" not in argv_tail_style)

        argv_nostyle = Path(td_argv) / "argv-nostyle.txt"
        os.environ["STUB_ARGV_OUT"] = str(argv_nostyle)
        bench_run.call(resolved_rel, "haiku", "test", None, "/tmp")
        check("output_style=None produces no --settings flag at all",
              "--settings" not in argv_nostyle.read_text().splitlines()[3:])
finally:
    if old_stub_argv_out is None:
        os.environ.pop("STUB_ARGV_OUT", None)
    else:
        os.environ["STUB_ARGV_OUT"] = old_stub_argv_out
    if old_laconic_default is None:
        os.environ.pop("LACONIC_DEFAULT", None)
    else:
        os.environ["LACONIC_DEFAULT"] = old_laconic_default

# The preflight probe that stops a round from spending hours measuring
# baseline twice. A style name the CLI does not recognise is dropped without
# an error, so "the call succeeded" proves nothing on its own - only the
# style's own banner coming back does.
old_stub_text = os.environ.get("STUB_TEXT")
old_stub_fail = os.environ.get("STUB_FAIL")
try:
    os.environ["STUB_TEXT"] = "# Concise Style Active"
    check("probe accepts the style when its banner comes back",
          bench_run.output_style_reaches_model(resolved_rel, "haiku", "Concise")
          is True)
    check("probe rejects a style whose banner names a different style",
          bench_run.output_style_reaches_model(resolved_rel, "haiku",
                                               "Explanatory") is False)

    os.environ["STUB_TEXT"] = "NONE"
    check("probe rejects the style when the model reports no style banner",
          bench_run.output_style_reaches_model(resolved_rel, "haiku", "Concise")
          is False)

    os.environ["STUB_FAIL"] = "1"
    check("probe rejects the style when the probe call itself fails",
          bench_run.output_style_reaches_model(resolved_rel, "haiku", "Concise")
          is False)
finally:
    for _k, _v in (("STUB_TEXT", old_stub_text), ("STUB_FAIL", old_stub_fail)):
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v

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
# require_claude_bin is the one guard all four entry points now share, so its
# two behaviours are tested here rather than four times over.
check("require_claude_bin returns the resolved path for a usable binary",
      bench_run.require_claude_bin("tests/stubs/claude-stub.sh") == resolved_rel)
try:
    bench_run.require_claude_bin("nonexistent-command-xyz")
    check("require_claude_bin exits on an unusable binary", False)
except SystemExit as _e:
    check("require_claude_bin exits on an unusable binary",
          "claude binary not found or not executable" in str(_e))
    check("and its message names the argument the user passed, not the resolved path",
          "nonexistent-command-xyz" in str(_e) and "--claude-bin" in str(_e))

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
    # Provenance: a snapshot has to say how the styled arm was delivered, or a
    # reader cannot tell it apart from an arm that simply got no rules.
    check("snapshot records the output style the concise-style arm ran under",
          snap["arms"]["concise-style"]["output_style"] == "Concise")
    check("snapshot records no output style for the prompt-delivered arms",
          not any("output_style" in snap["arms"][a]
                  for a in ("baseline", "terse-control", "word-compression",
                            "laconic")))
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

# #61: a resume is a second attempt at one cell, not a second cell. Before the
# fix the retry was appended beside the failure, so round-08.json carries 740
# records for 700 cells - every duplicate a (failed, succeeded) pair.
retry = {"case": "c", "arm": "a", "model": "haiku", "rep": 0, "ok": True, "text": "y"}
check("a retried cell collapses to its successful run",
      bench_run.dedupe([failed, retry]) == [retry])
check("dedupe prefers the success whichever order it appears in",
      bench_run.dedupe([retry, failed]) == [retry])
check("dedupe leaves distinct cells alone",
      len(bench_run.dedupe([failed, dict(failed, rep=1), dict(failed, arm="b")])) == 3)
# The pair differs only by arm, so a dedupe keying on (case, model, rep) alone
# would collapse two real cells into one and silently halve a round.
check("dedupe keys on arm too",
      len(bench_run.dedupe([retry, dict(retry, arm="laconic")])) == 2)

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

# #67: a failed judge call is stored as not_exercised so the file stays
# one-record-per-response, and must not then count as finished work. Round 12's
# judging pass returned 850 judgments of which 666 were "judge call failed",
# and re-running repaired none of them.
_failed = {"case": "c", "arm": "laconic", "model": "haiku", "rep": 0,
           "verdict": "not_exercised", "quote": "",
           "reason": bench_judge.REASON_JUDGE_CALL_FAILED}
_unparseable = dict(_failed, reason=bench_judge.REASON_UNPARSEABLE)
_genuine = dict(_failed, reason="the response asked for context without engaging")
check("a failed judge call is not finished work",
      bench_judge._is_infra_failure(_failed))
check("an unparseable judge reply is not finished work either",
      bench_judge._is_infra_failure(_unparseable))
check("a genuine not_exercised verdict IS finished work",
      not bench_judge._is_infra_failure(_genuine))
check("a pass is finished work",
      not bench_judge._is_infra_failure(dict(_failed, verdict="pass", reason="r")))

_key = ("c", "laconic", "haiku", 0)
_at, _done = bench_judge.resume_index([_failed])
check("a resume retries a failed judge call", _key not in _done)
check("the retry knows where to overwrite it", _at[_key] == 0)

_at, _done = bench_judge.resume_index([dict(_failed, verdict="fail", reason="r")])
check("a resume skips a decided judgment", _key in _done)

# The repair writes over the failure rather than beside it, so the file keeps
# one record per response however many attempts it took.
_js = [_failed, dict(_failed, rep=1, verdict="pass", reason="r")]
_at, _done = bench_judge.resume_index(_js)
_js[_at[_key]] = dict(_failed, verdict="pass", reason="r")
check("repairing in place does not grow a duplicate",
      len(_js) == 2 and _js[0]["verdict"] == "pass")
for arm in ["laconic", "baseline", "terse-control", "word-compression",
            "concise-style"]:
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

# An arm missing from ARM_ORDER is generated, judged, paid for, and then
# silently dropped from every table report.py prints.
check("report orders every arm run.py can generate",
      set(bench_report.ARM_ORDER) == set(bench_run.ARMS))
check("report keeps laconic last so it reads against the controls",
      bench_report.ARM_ORDER[-1] == "laconic")

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
        '{"type":"result","is_error":false,"result":"stub answer","num_turns":1,'
        '"total_cost_usd":0.001,"duration_ms":1,'
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

    # --judge-all because floor is a rule-adherence case, which the default
    # coverage skips. This test is about the retry, not about what gets graded.
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(flaky), "--results", str(snap_path),
         "--out", str(out_path), "--judge-all"],
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
        '{"type":"result","is_error":false,"result":"stub answer","num_turns":1,'
        '"total_cost_usd":0.001,"duration_ms":1,'
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
         "--claude-bin", str(cwd_stub), "--results", str(snap_path),
         "--out", str(out_path), "--judge-all"],  # floor is rule-adherence
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
# Read back through the parser run.py itself uses, so one check covers both
# the escaping and the stub still emitting the stream shape call() asks for.
# A stub that drifts from the real format turns every harness test into a
# test of the stub.
# The percent sign is deliberate: the stub interpolates STUB_TEXT into a
# printf argument, and a bare format string would eat it.
stub_env = dict(os.environ, STUB_TEXT='He said "stop", 100% of the time.',
                STUB_TOOLS="Read")
stub_out = subprocess.run(["bash", str(ROOT / "tests" / "stubs" / "claude-stub.sh")],
                          input="prompt", capture_output=True, text=True, env=stub_env)
stub_parsed = bench_run.parse_cli_stream(stub_out.stdout)
check("claude-stub.sh escapes a quote in STUB_TEXT so its JSON stays valid",
      stub_parsed["ok"] is True
      and stub_parsed["text"] == 'He said "stop", 100% of the time.')
check("claude-stub.sh emits the stream shape call() parses, tool events included",
      stub_parsed["tools"] == ["Read"])

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
      bench_prefer.flip_rate(recs) == (1, 2, 0))

# #55: a failed judge call carries winner_arm None, and None != "baseline" is
# true, so counting it as a flip manufactures position bias out of an API
# error. Round 09 lost its whole reversed-order pass and scored 95% from zero
# decided pairs.
undec = [{"case": "a", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"},
         {"case": "a", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": None},
         {"case": "b", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "tie"},
         {"case": "b", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": "tie"}]
check("an undecided side leaves the flip rate instead of counting as a flip",
      bench_prefer.flip_rate(undec) == (0, 1, 1))
check("a wholly undecided reversed pass measures no pairs at all",
      bench_prefer.flip_rate(undec[:2]) == (0, 0, 1))

# #55: a resume is a second attempt at one comparison, not a second comparison.
dup = [{"case": "a", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": None},
       {"case": "a", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": "laconic"}]
check("a repaired duplicate collapses to the decided record",
      bench_prefer._dedupe(dup) == [dup[1]])
check("dedupe keeps a decided record over a later failure",
      bench_prefer._dedupe(dup[::-1]) == [dup[1]])
check("dedupe leaves distinct comparisons alone",
      len(bench_prefer._dedupe(recs)) == len(recs))

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
# An arm the source never had is copied as nothing and nothing says so. The
# source above holds baseline, laconic and terse-control, and laconic is being
# regenerated, so the two arms it has never heard of are the gap to disclose.
check("carrying names the arms it could not carry",
      carried["metadata"]["carried_arms_from"]["missing_arms"]
      == ["concise-style", "word-compression"])
check("an arm being regenerated is not reported as missing",
      "laconic" not in carried["metadata"]["carried_arms_from"]["missing_arms"])
src_full = {"metadata": {"rules_cksum": "111"},
            "runs": [{"case": "a", "arm": a, "model": "sonnet", "rep": 0,
                      "ok": True, "text": "x"} for a in bench_run.ARMS]}
check("a source holding every arm reports no gap",
      bench_run.carry_arms({"metadata": {}, "runs": []}, src_full,
                           ["laconic"])["metadata"]["carried_arms_from"]
      ["missing_arms"] == [])
# Failed runs are excluded from every statistic; carrying them in would
# reintroduce them under a fresh snapshot's provenance.
src_bad = {"metadata": {"rules_cksum": "111"},
           "runs": [{"case": "a", "arm": "baseline", "model": "sonnet", "rep": 0, "ok": False}]}
check("carrying skips failed runs",
      bench_run.carry_arms({"metadata": {}, "runs": []}, src_bad, ["laconic"])["runs"] == [])

# End-to-end, because the disclosure is only worth having if a human sees it:
# the metadata field can be correct while the print that surfaces it is
# refactored away, and a warning nobody prints is the silence it was added to
# fix. Driven through main() as a subprocess against the stub.
with tempfile.TemporaryDirectory() as td_gap:
    gap_src = Path(td_gap) / "prev.json"
    gap_src.write_text(json.dumps({
        "metadata": {"rules_cksum": "1"},
        "arms": {"baseline": {"system_prompt": None}},
        "runs": [{"case": "floor", "arm": "baseline", "model": "haiku", "rep": 0,
                  "ok": True, "text": "x"}]}))
    gap_out = Path(td_gap) / "round.json"
    proc_gap = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "run.py"),
         "--claude-bin", str(ROOT / "tests" / "stubs" / "claude-stub.sh"),
         "--arms", "laconic", "--models", "haiku", "--reps", "1",
         "--cases", "floor", "--carry-arms-from", str(gap_src),
         "--snapshot", str(gap_out)],
        capture_output=True, text=True)
    check("subprocess: the carrying pass still succeeds with a gap",
          proc_gap.returncode == 0)
    check("subprocess: main() warns that arms could not be carried",
          "no runs to carry" in proc_gap.stdout)
    check("subprocess: the warning names every arm the source lacked",
          all(a in proc_gap.stdout
              for a in ("concise-style", "terse-control", "word-compression")))
    _gap_line = next(l for l in proc_gap.stdout.splitlines()
                     if "no runs to carry" in l)
    check("subprocess: the warning does not name the regenerated arm",
          "laconic" not in _gap_line)
    check("subprocess: the gap is recorded in the snapshot, not only printed",
          json.loads(gap_out.read_text())["metadata"]["carried_arms_from"]
          ["missing_arms"] == ["concise-style", "terse-control",
                               "word-compression"])

# --- #142: the tool list has to reach the snapshot, not just the parser ---
# The parser checks above run on a fixture string. This one drives main()
# against a stub that emits a real stream, because a field call() returns and
# run.py drops is a field no round ever carries.
with tempfile.TemporaryDirectory() as td_tools:
    tools_out = Path(td_tools) / "round.json"
    proc_tools = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "run.py"),
         "--claude-bin", str(ROOT / "tests" / "stubs" / "claude-stub.sh"),
         "--arms", "baseline", "--models", "haiku", "--reps", "1",
         "--cases", "floor", "--snapshot", str(tools_out)],
        capture_output=True, text=True,
        env=dict(os.environ, STUB_TOOLS="Read Bash"))
    check("subprocess: a pass against a tool-invoking stub succeeds",
          proc_tools.returncode == 0)
    _tool_runs = json.loads(tools_out.read_text())["runs"] if tools_out.exists() else []
    check("subprocess: the tool names reach the stored run record",
          [r.get("tools") for r in _tool_runs] == [["Read", "Bash"]])

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


def _summary(nc=0, qf=0, sf=0, viol=0, tokens=None, flip=0.2, n_runs=110,
             one_turn=0, one_turn_n_runs=None, unread_asks=0):
    return {"never_cut_failures": nc, "quality_fails": qf, "safety_fails": sf,
            "violations_total": viol,
            "tokens": TEN_CELLS(100) if tokens is None else tokens, "flip_rate": flip,
            "n_runs": n_runs, "one_turn": one_turn, "unread_asks": unread_asks,
            "one_turn_n_runs": n_runs if one_turn_n_runs is None else one_turn_n_runs}


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

# --- #96 follow-on: a scoped count target can name one model ---
# The composition table made the need obvious and there was no way to act on it.
# Round 16's six-cell scope was 82% haiku by expected failures, so a real sonnet
# effect could not reach a threshold the pooled scope set. A hypothesis that
# expects one stratum to move has to be able to say so before the round.
_MRUNS = [{"case": "design-cache", "arm": "laconic", "model": m, "rep": 0,
           "ok": True, "text": "x", "output_tokens": 100}
          for m in ("haiku", "sonnet")]
_MJUDG = [{"case": "design-cache", "arm": "laconic", "model": "haiku", "rep": 0,
           "verdict": "fail"},
          {"case": "design-cache", "arm": "laconic", "model": "sonnet", "rep": 0,
           "verdict": "pass"}]
both = bench_report.round_summary({"runs": _MRUNS}, _MJUDG,
                                  target_cases=["design-cache"])
son = bench_report.round_summary({"runs": _MRUNS}, _MJUDG,
                                 target_cases=["design-cache"],
                                 target_models=["sonnet"])
check("an unscoped-by-model target counts both models",
      both["scoped"]["quality_fails"] == 1 and both["scoped"]["n_runs"] == 2)
check("naming a model narrows the scoped count to that stratum",
      son["scoped"]["quality_fails"] == 0 and son["scoped"]["n_runs"] == 1)
check("the model scope is recorded in the summary so it cannot be added later",
      son["scoped"]["models"] == ["sonnet"] and both["scoped"]["models"] is None)

# The round-wide counters are what the fatal conditions read, and narrowing the
# target must not narrow them - an edit that helps sonnet and breaks haiku still
# has to reject.
check("naming a model leaves the round-wide counters over both",
      son["quality_fails"] == both["quality_fails"] == 1)

# Omitting it is the old behaviour exactly, which is what keeps stored rounds
# where they are: no round before 17 passed target_models at all.
check("omitting the model scope reproduces the previous scoped count",
      bench_report.round_summary({"runs": _MRUNS}, _MJUDG,
                                 target_cases=["design-cache"])["scoped"]
      == both["scoped"])

# --- #69: the case material a round was generated from is pinned ---
# Every harness reads the working tree while it runs, and a round takes hours.
# rules_cksum has guarded the rules text since the beginning; the cases were not
# guarded at all, so editing a case or switching branches mid-pass produced one
# round graded against two different criteria with nothing recording it. This
# nearly cost round 17 when a rebase mid-round briefly reverted the tree.
import tempfile as _tf

_cd = pathlib.Path(_tf.mkdtemp()) / "cases"
(_cd / "c1").mkdir(parents=True)
(_cd / "c1" / "prompt.md").write_text("q?\n")
(_cd / "c1" / "expect.json").write_text(json.dumps({"trap": "t"}))
_base = bench_run.cases_cksum(_cd, ["c1"])

(_cd / "c1" / "prompt.md").write_text("a different question?\n")
check("editing a prompt changes the case checksum",
      bench_run.cases_cksum(_cd, ["c1"]) != _base)
(_cd / "c1" / "prompt.md").write_text("q?\n")
check("restoring the prompt restores it",
      bench_run.cases_cksum(_cd, ["c1"]) == _base)

# The trap is what the judge grades against, and correcting one has moved
# verdicts twice in this project's history.
(_cd / "c1" / "expect.json").write_text(json.dumps({"trap": "different"}))
check("editing a trap changes the case checksum",
      bench_run.cases_cksum(_cd, ["c1"]) != _base)
(_cd / "c1" / "expect.json").write_text(json.dumps({"trap": "t"}))

# The fixture is what a design case's answer is derived from, so a fixture edit
# invalidates generation even though it never reaches the judge's prompt.
(_cd / "c1" / "fixture").mkdir()
(_cd / "c1" / "fixture" / "app.js").write_text("x")
_with_fixture = bench_run.cases_cksum(_cd, ["c1"])
check("adding a fixture file changes the case checksum", _with_fixture != _base)
(_cd / "c1" / "fixture" / "app.js").write_text("y")
check("editing a fixture file changes it again",
      bench_run.cases_cksum(_cd, ["c1"]) != _with_fixture)
(_cd / "c1" / "fixture" / "app.js").unlink()
(_cd / "c1" / "fixture").rmdir()
check("deleting the fixture restores the original checksum",
      bench_run.cases_cksum(_cd, ["c1"]) == _base)

# Scoped to the round's own cases: adding a case must not invalidate a resume
# of a round that never touched it.
(_cd / "c2").mkdir()
(_cd / "c2" / "prompt.md").write_text("other\n")
check("an unrelated case does not affect a scoped checksum",
      bench_run.cases_cksum(_cd, ["c1"]) == _base)
check("naming the new case does affect it",
      bench_run.cases_cksum(_cd, ["c1", "c2"]) != _base)

# The dirty-tree record is informational, never a refusal: the loop's own
# workflow edits rules/laconic.md and runs before committing in some orders.
check("the dirty-tree probe returns a bool or None",
      bench_run._git_dirty() in (True, False, None))

# --- #96: a count target is scored against the measured rates, not one draw ---
# report.py fed cell_rates to the fatal screen and not to the target, so a count
# target still compared against a single n=10 baseline draw - the defect #66 was
# filed about, fixed on half the gate. Round 16 read its sonnet cells 5 -> 2
# against the draw, which looks like a win, and 2 of 30 against the measured
# 22 of 120 is p = 0.165.
RATES_2 = {("a", "haiku"): {"failures": 20, "runs": 40},
           ("a", "sonnet"): {"failures": 2, "runs": 40}}
CELLS_2 = [("a", "haiku"), ("a", "sonnet")]

check("a fully measured scope is scored against the pooled rate",
      abs(bench_report._rate_count_p(RATES_2, CELLS_2, 4, 20) -
          bench_report._binom_cdf(4, 26, 20 / 100)) < 1e-12)

# The guard is what keeps every stored round where it was. Three of the four
# stored count-target rounds target violations_total, which has no measured
# rates at all, and the fourth is round 16.
check("a scope missing one rate falls back rather than scoring on a subset",
      bench_report._rate_count_p(RATES_2, CELLS_2 + [("b", "haiku")], 4, 20) is None)
check("no rates at all falls back",
      bench_report._rate_count_p({}, CELLS_2, 4, 20) is None)
check("a scope with no cells falls back",
      bench_report._rate_count_p(RATES_2, [], 4, 20) is None)
# A measured rate of 0 across the whole scope leaves nothing to test against,
# the same way _count_p refuses a target already at 0.
check("an all-zero measured scope falls back instead of dividing by nothing",
      bench_report._rate_count_p({("a", "haiku"): {"failures": 0, "runs": 40}},
                                 [("a", "haiku")], 0, 20) is None)

# The composition table is the part that would have changed round 16 before it
# ran: six cells that behaved like three.
comp = bench_report._scope_composition(RATES_2, CELLS_2,
                                       {("a", "haiku"): 10, ("a", "sonnet"): 10})
check("scope composition ranks cells by measured rate",
      [c for c, _, _ in comp] == [("a", "haiku"), ("a", "sonnet")])
check("scope composition reports each cell's expected share",
      abs(comp[0][2] - 5.0) < 1e-9 and abs(comp[1][2] - 0.5) < 1e-9)
check("scope composition is empty when a cell has no rate",
      bench_report._scope_composition(RATES_2, CELLS_2 + [("b", "haiku")],
                                      {}) == [])

# --- #88 part B: quality_fails split on whether the answer hands a decision back ---
# Round 15's round-wide quality count was flat while both of its halves moved in
# opposite directions, and the gate read the flat number. The split is
# disclosure only - it may never reject - but it has to be computed and printed,
# or the same cancellation is invisible again.
def _strata_round(rows):
    """rows: (rep, text, verdict) on a quality-graded case, laconic arm."""
    runs = [{"case": "design-cache", "arm": "laconic", "model": "sonnet",
             "rep": r, "ok": True, "text": t, "output_tokens": 100}
            for r, t, _ in rows]
    judg = [{"case": "design-cache", "arm": "laconic", "model": "sonnet",
             "rep": r, "verdict": v} for r, _, v in rows]
    return bench_report.round_summary({"runs": runs}, judg)


ASKED = "Use the CDN. Which stack are you running?"
RESOLVED = "Scope the no-store header to /account; the CDN already fronts this."
st = _strata_round([(0, ASKED, "fail"), (1, ASKED, "pass"),
                    (2, RESOLVED, "fail"), (3, RESOLVED, "pass")])["quality_strata"]
check("the strata split a round's quality verdicts on the covariate",
      st == {"asks": {"fails": 1, "n": 2}, "resolves": {"fails": 1, "n": 2}})

# A rule-adherence or safety case may not enter the split, for the same reason
# it may not enter quality_fails.
mixed = bench_report.round_summary(
    {"runs": [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
               "ok": True, "text": ASKED, "output_tokens": 10}]},
    [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
      "verdict": "fail"}])
check("a rule-adherence case stays out of the quality strata",
      mixed["quality_strata"] == {"asks": {"fails": 0, "n": 0},
                                  "resolves": {"fails": 0, "n": 0}})

# A judge outage is not a verdict, and counting it as one would move a stratum
# on infrastructure rather than on an answer.
infra = bench_report.round_summary(
    {"runs": [{"case": "design-cache", "arm": "laconic", "model": "sonnet",
               "rep": 0, "ok": True, "text": ASKED, "output_tokens": 10}]},
    [{"case": "design-cache", "arm": "laconic", "model": "sonnet", "rep": 0,
      "verdict": "not_exercised",
      "reason": bench_judge.REASON_JUDGE_CALL_FAILED}])
check("an infrastructure failure does not enter a stratum",
      infra["quality_strata"]["asks"]["n"] == 0)

# The cancelling pair: the round-wide count is identical and each half moved.
before = _strata_round([(0, ASKED, "pass"), (1, ASKED, "pass"),
                        (2, RESOLVED, "fail"), (3, RESOLVED, "fail")])
after = _strata_round([(0, ASKED, "fail"), (1, ASKED, "fail"),
                       (2, RESOLVED, "pass"), (3, RESOLVED, "pass")])
check("the cancelling pair leaves the round-wide count identical",
      before["quality_fails"] == after["quality_fails"] == 2)
line = bench_report._strata_line(before, after)
check("the cancellation is disclosed", line is not None and "OPPOSITE" in line)
check("the disclosure says it is not a gate", "not a gate" in line)
check("the disclosure names which stratum got worse", "hands-back" in line)

# It rides on the verdict whatever the verdict was, and never changes it.
prev = dict(_summary(tokens=TEN_CELLS(500)), quality_strata=before["quality_strata"])
cur = dict(_summary(tokens=TEN_CELLS(100)), quality_strata=after["quality_strata"])
v, why = bench_report.accept_verdict(prev, cur, "output_tokens")
check("the strata disclosure does not reject an otherwise-passing edit",
      v == "accept")
check("the strata disclosure is printed with the reasons",
      any("quality strata" in r for r in why))

# Two strata moving the same way is not a cancellation and must not be labelled
# one, or the word stops meaning anything.
same = _strata_round([(0, ASKED, "fail"), (1, ASKED, "fail"),
                      (2, RESOLVED, "fail"), (3, RESOLVED, "fail")])
line_same = bench_report._strata_line(before, same)
check("strata moving the same way are reported without the cancellation note",
      line_same is not None and "OPPOSITE" not in line_same)

# A round with an empty stratum cannot be compared on it, and says nothing
# rather than dividing by zero.
empty = _strata_round([(0, RESOLVED, "pass")])
check("an empty stratum produces no disclosure line",
      bench_report._strata_line(before, empty) is None)

check("round_summary reads the treatment tokens", rs["tokens"] == {("floor", "sonnet"): 10})
check("round_summary computes the flip rate", rs["flip_rate"] == 1.0)
check("a fully decided round reports no undecided pairs", rs["flip_undecided"] == 0)

# #55: round 09's first preference pass lost every reversed-order comparison to
# API failures, and round_summary read the resulting Nones as position flips.
RUN1 = {"runs": [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
                  "ok": True, "text": "Fine.", "output_tokens": 10}]}
rs_undec = bench_report.round_summary(
    RUN1, [],
    [{"case": "floor", "model": "sonnet", "rep": 0, "order": 0, "winner_arm": "laconic"},
     {"case": "floor", "model": "sonnet", "rep": 0, "order": 1, "winner_arm": None}])
check("an undecided side is not counted as a position flip",
      rs_undec["flip_rate"] == 0.0 and rs_undec["flip_pairs"] == 0)
check("the undecided pair is disclosed rather than dropped silently",
      rs_undec["flip_undecided"] == 1)

# Excluding them creates the opposite hazard: 0 decided pairs divides into a
# 0% flip rate, which reads as the most citable round possible. Unmeasured has
# to be named before the ceiling is.
und = _summary(tokens=TEN_CELLS(100), flip=0.0)
und["flip_pairs"], und["flip_undecided"] = 0, 20
v, why = bench_report.accept_verdict(worse, und, "output_tokens")
check("a round with no decided pair is not citable on a 0% flip rate",
      v == "accept" and any("unmeasured" in r for r in why))

# A measured round that still lost some pairs says so beside its rate.
part = _summary(tokens=TEN_CELLS(100), flip=0.1)
part["flip_pairs"], part["flip_undecided"] = 18, 2
v, why = bench_report.accept_verdict(worse, part, "output_tokens")
check("undecided pairs are disclosed beside a citable flip rate",
      any("2 both-order pair(s) undecided" in r for r in why))
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
# Exercised on sonnet, which is also what the case counts on both models since
# #94 retired destructive/haiku's saturation in favour of a measured rate.
NAMED_THEN_DISMISSED = ("The `invoices` foreign key blocks the drop. "
                        "The `sessions` table is safe (it has `ON DELETE CASCADE`).")
rs_safety = bench_report.round_summary(
    {"runs": [{"case": "destructive", "arm": "laconic", "model": "sonnet", "rep": 0,
               "ok": True, "text": NAMED_THEN_DISMISSED, "output_tokens": 10}]},
    [{"case": "destructive", "arm": "laconic", "model": "sonnet", "rep": 0,
      "verdict": "fail"}])
check("a response that names its never-cut keywords passes the substring check",
      rs_safety["never_cut_failures"] == 0)
check("the same response's lost safety verdict is counted",
      rs_safety["safety_fails"] == 1)
check("a safety-graded failure is not double-counted as a quality one",
      rs_safety["quality_fails"] == 0)

# --- saturated cells leave the counters but not the table ---
# The mechanism is exercised on ordered-steps/haiku, which is the cell it is
# actually for. #94 retired destructive/haiku's marking: saturation was
# conflating two problems, and only one of them needs it.
#
#   ordered-steps/haiku is a VARIANCE problem - 48.3% is where a binomial's
#   variance is largest, its baseline draw of 2 of 10 sits below a mean of 4.8,
#   so it enters every round about +3 high and pushes the round-wide total up.
#   That total gates whether the fatal check runs at all, before any per-cell
#   screen, so the measured-rate screen cannot reach it. Exclusion is the only
#   tool.
#
#   destructive/haiku was a LEVEL problem - 53 of 55 under master rules, with a
#   baseline draw of 10 of 10. The fatal counters reject only on a rise, and a
#   cell already at the ceiling in the baseline cannot produce one, so the
#   exclusion bought nothing and hid a fall. A measured rate covers it instead.
check("ordered-steps marks haiku saturated",
      "haiku" in bench_report.case_saturated_models("ordered-steps"))
check("destructive no longer marks haiku saturated (#94)",
      bench_report.case_saturated_models("destructive") == {})
check("a case without the field has no saturated models",
      bench_report.case_saturated_models("floor") == {})
DROPPED_STEP = "Rotate the key and remove the old one."
rs_saturated = bench_report.round_summary(
    {"runs": [{"case": "ordered-steps", "arm": "laconic", "model": "haiku", "rep": 0,
               "ok": True, "text": DROPPED_STEP, "output_tokens": 10}]},
    [{"case": "ordered-steps", "arm": "laconic", "model": "haiku", "rep": 0,
      "verdict": "fail"}])
check("a saturated cell's lost safety verdict is not counted",
      rs_saturated["safety_fails"] == 0)
# The un-saturated cell is counted again, which is the whole point of #94: a
# fall on it can now register.
rs_unsat = bench_report.round_summary(
    {"runs": [{"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 0,
               "ok": True, "text": NAMED_THEN_DISMISSED, "output_tokens": 10}]},
    [{"case": "destructive", "arm": "laconic", "model": "haiku", "rep": 0,
      "verdict": "fail"}])
check("the un-saturated cell's safety verdict is counted again",
      rs_unsat["safety_fails"] == 1)
check("the un-saturated cell's deterministic never-cut check still applies",
      rs_unsat["never_cut_failures"] == 0)
sat_synth = {
    "metadata": {"generated_at": "t", "reps": 1, "laconic_level": "full",
                 "rules_cksum": "1", "git_commit": "c", "claude_cli_version": "z"},
    "arms": {"laconic": {"system_prompt": "r"}},
    "runs": [{"case": "ordered-steps", "arm": "laconic", "model": "haiku", "rep": 0,
              "ok": True, "text": DROPPED_STEP, "output_tokens": 10,
              "total_cost_usd": 0.001, "duration_ms": 500}],
}
sat_md = bench_report.render(sat_synth, {"judgments": [
    {"case": "ordered-steps", "arm": "laconic", "model": "haiku", "rep": 0,
     "verdict": "fail", "quote": "", "reason": "dropped a step"}]}, 0.70)
check("the trap-verdicts table still shows the saturated cell's verdicts",
      "| ordered-steps | safety | laconic | 0 | 1 | 0 | 0 |" in sat_md)
check("the report discloses the exclusion beside the table",
      "marked saturated" in sat_md and "ordered-steps" in sat_md)

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
# The floor is the median stdev over ALL scoped cells since #51 - haiku cells
# included, matching the shift median they participate in. Here that is
# median(60, 75.8, 101.5, 138.5, 250, 1519.1) = 120.0.
STDEV3 = {("badnews", "haiku"): 60.0, ("badnews", "sonnet"): 75.8,
          ("ordered-steps", "haiku"): 101.5, ("ordered-steps", "sonnet"): 138.5,
          ("walkthrough", "haiku"): 250.0, ("walkthrough", "sonnet"): 1519.1}


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


# Round 01's real scoped cells: median 856, all-cells floor 120.0.
base6 = _scoped_tok(_tok6(442, 439, 653, 1059, 1163, 3666), stdev=STDEV3)

v, why = bench_report.accept_verdict(
    base6, _scoped_tok(_tok6(380, 400, 500, 700, 900, 1700)),
    "output_tokens", target_cases=SCOPE3)
check("a 6-cell sweep past the scoped floor is accepted", v == "accept")
check("the scoped token line names its floor",
      any("scoped floor 120.0" in r for r in why))
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
check("a scoped cell without a baseline stdev leaves the floor unbuildable",
      v == "reject" and any("no baseline stdev" in r for r in why))

# Since #51 a haiku-only scope carries its own floor - its cells' own
# dispersion - instead of being refused for lacking a sonnet cell.
v, why = bench_report.accept_verdict(
    _scoped_tok(dict(haiku6), stdev={k: 20.0 for k in haiku6},
                cases=list("abcdef")),
    _scoped_tok({k: 10 for k in haiku6}, cases=list("abcdef")),
    "output_tokens", target_cases=list("abcdef"))
check("a haiku-only scope with baseline stdevs is gated on its own floor",
      v == "accept")

# The #51 regression itself: round-08's shape. Big sonnet effects, small
# haiku effects, all six cells down. The old sonnet-only floor was
# median(575, 954, 322) = 575 and the mixed shift median of 503 sat inside
# it; the all-cells floor is median(80, 100, 150, 322, 575, 954) = 236 and
# the same shift clears it.
r8_cases = ["da", "db", "dc"]
r8_base = {("da", "haiku"): 978, ("da", "sonnet"): 4651,
           ("db", "haiku"): 1486, ("db", "sonnet"): 6544,
           ("dc", "haiku"): 587, ("dc", "sonnet"): 2264}
r8_stdev = {("da", "haiku"): 100.0, ("da", "sonnet"): 575.0,
            ("db", "haiku"): 150.0, ("db", "sonnet"): 954.0,
            ("dc", "haiku"): 80.0, ("dc", "sonnet"): 322.0}
r8_cur = {("da", "haiku"): 899, ("da", "sonnet"): 3413,
          ("db", "haiku"): 741, ("db", "sonnet"): 4410,
          ("dc", "haiku"): 535, ("dc", "sonnet"): 1844}
v, why = bench_report.accept_verdict(
    _scoped_tok(r8_base, stdev=r8_stdev, cases=r8_cases),
    _scoped_tok(r8_cur, cases=r8_cases),
    "output_tokens", target_cases=r8_cases)
check("a sonnet-large haiku-small sweep clears the all-cells floor (#51)",
      v == "accept")

# --- #131: the token target is scored inside one reading stratum ---
# An unread answer is several times shorter than a grounded one, so a marginal
# median falls when an edit suppresses reading and the old target could not
# tell that from compression.


def _strata(cells, **kw):
    """A summary whose cells carry a (grounded, unread) token split."""
    tokens = {c: bench_report._median(list(g) + list(u))
              for c, (g, u) in cells.items()}
    return dict(_summary(tokens=tokens, **kw),
                strata_tokens={c: {"grounded": list(g), "unread": list(u)}
                               for c, (g, u) in cells.items()})


# Round 20's shape: every grounded answer is exactly as long as it was, and the
# whole marginal move is answers leaving the grounded stratum.
mix_prev = _strata({c: ([1000] * 6, [200] * 4) for c in TEN_CELLS(0)})
mix_cur = _strata({c: ([1000] * 2, [200] * 8) for c in TEN_CELLS(0)})
v, why = bench_report.accept_verdict(mix_prev, mix_cur, "output_tokens")
check("a token win that is only mix-shift is rejected (#131)", v == "reject")
check("the mix-shift rejection reports no cell improving",
      any("0 of 10 cells improved" in r for r in why))
check("the marginal shift the old target read is still disclosed",
      any("the marginal shift is 800 tokens" in r for r in why))
check("the counterfactual holds each cell at the baseline's reading rate",
      any("and 0 with each cell's reading rate held at the baseline's" in r
          for r in why))

# The target is scored inside the grounded stratum, so an edit that shortens
# only the answers that never opened a file has to be visible somewhere or the
# verdict would report nothing at all about it.
v, why = bench_report.accept_verdict(
    _strata({c: ([1000] * 6, [800] * 4) for c in TEN_CELLS(0)}),
    _strata({c: ([1000] * 6, [300] * 4) for c in TEN_CELLS(0)}),
    "output_tokens")
check("compressing only unread answers does not pass the target", v == "reject")
check("the unread stratum is reported beside the grounded one",
      any("the unread stratum reads 800 -> 300 over 10 of 10 cells" in r
          for r in why))

# A round whose cells all sit in one stratum still reports that stratum's
# level, even though no counterfactual can be built for it.
v, why = bench_report.accept_verdict(
    _strata({c: ([], [1000] * 10) for c in TEN_CELLS(0)}),
    _strata({c: ([], [400] * 10) for c in TEN_CELLS(0)}),
    "output_tokens")
check("a single-stratum round still reports the unread median",
      any("the unread stratum reads 1000 -> 400" in r for r in why)
      and not any("both strata" in r for r in why))

# The same mix, with real compression under it, still passes.
comp_cur = _strata({c: ([400] * 2, [200] * 8) for c in TEN_CELLS(0)})
v, why = bench_report.accept_verdict(mix_prev, comp_cur, "output_tokens")
check("compression inside the grounded stratum is still accepted", v == "accept")
check("the accepted shift is the grounded one, not the marginal one",
      any("median shift 600 tokens" in r for r in why))

# A cell whose reading rate crossed the floor has no stratum to be compared
# inside. It does not vote, and the verdict names it rather than dropping it
# silently.
crossed = dict({c: ([1000] * 6, [200] * 4) for c in TEN_CELLS(0)})
crossed[("a", "sonnet")] = ([], [200] * 10)
v, why = bench_report.accept_verdict(
    mix_prev, _strata({c: ([400] * 6, [200] * 4) if c != ("a", "sonnet")
                       else ([], [200] * 10) for c in TEN_CELLS(0)}),
    "output_tokens")
check("a cell whose reading rate crossed the floor does not vote",
      any("9 of 9 cells improved" in r for r in why))
check("the verdict names the cell it refused and its reading rates",
      any("a/sonnet 6 of 10 -> 0 of 10" in r for r in why))

# A case with no fixture has nothing to open, so every answer is unread by
# construction. There is no mix to shift and the cell is compared as it always
# was, inside the unread stratum.
v, why = bench_report.accept_verdict(
    _strata({c: ([], [1000] * 10) for c in TEN_CELLS(0)}),
    _strata({c: ([], [400] * 10) for c in TEN_CELLS(0)}),
    "output_tokens")
check("a cell that never reads is compared inside the unread stratum",
      v == "accept" and any("10 unread" in r for r in why))

# GROUNDED_MIN_RUNS is a floor on whether a stratum exists at all: two runs on
# both sides is a grounded comparison, one against three is a crossing.
v, why = bench_report.accept_verdict(
    _strata({c: ([1000] * 2, [200] * 8) for c in TEN_CELLS(0)}),
    _strata({c: ([400] * 2, [200] * 8) for c in TEN_CELLS(0)}),
    "output_tokens")
check("two grounded runs a side is enough to compare grounded medians",
      v == "accept" and any("10 grounded" in r for r in why))
v, why = bench_report.accept_verdict(
    _strata({c: ([1000], [200] * 9) for c in TEN_CELLS(0)}),
    _strata({c: ([400] * 3, [200] * 7) for c in TEN_CELLS(0)}),
    "output_tokens")
check("one grounded run against three is refused, not compared",
      v == "reject" and any("not voting" in r for r in why))

# A summary built before #131 carries no strata block. It is scored on the
# marginal median, which is what every stored round was scored by, and says so
# by printing no stratum line at all.
v, why = bench_report.accept_verdict(_summary(tokens=TEN_CELLS(500)),
                                     _summary(tokens=TEN_CELLS(100)),
                                     "output_tokens")
check("a summary with no strata block is still scored on its marginal median",
      v == "accept" and not any("#131" in r for r in why))

# The scoped branch reads the same stratified medians, and builds its floor
# from the stratum the cells voted in.
scoped_prev = dict(_strata({(c, "sonnet"): ([1000] * 6, [200] * 4)
                            for c in "abcdef"}),
                   scoped=_scoped(cases=list("abcdef"))["scoped"])
scoped_cur = dict(_strata({(c, "sonnet"): ([1000] * 2, [200] * 8)
                           for c in "abcdef"}),
                  scoped=_scoped(cases=list("abcdef"))["scoped"])
v, why = bench_report.accept_verdict(scoped_prev, scoped_cur, "output_tokens",
                                     target_cases=list("abcdef"))
check("a scoped token target is stratified too (#131)",
      v == "reject" and any("0 of 6 cells improved" in r for r in why))

# aggregate and round_summary build the split from num_turns, which is the
# same proxy the one_turn counter uses.
rs_strata = bench_report.round_summary({"runs": [
    {"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0, "ok": True,
     "text": "Fine.", "output_tokens": 900, "num_turns": 3},
    {"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 1, "ok": True,
     "text": "Fine.", "output_tokens": 100, "num_turns": 1}]})
check("round_summary splits a cell's tokens on whether the answer read (#131)",
      rs_strata["strata_tokens"][("floor", "sonnet")]
      == {"grounded": [900], "unread": [100]})
check("round_summary keeps the marginal median beside the split",
      rs_strata["tokens"][("floor", "sonnet")] == 500)

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

# --- #49: action scope is measured as grounded turns, and a rise is fatal ---
# Laconic bounds prose, so an edit can cut words and relocate the excess into
# tool calls. num_turns is the action proxy every stored round carries: the CLI
# reports how many agentic turns a response took and nothing about which tools
# ran. The tool list #142 added is not read here and gates nothing.
#
# Scored inside the grounded stratum only. In the unread stratum num_turns is
# 0 or 1 by construction, so an unconditioned turn median falls whenever an
# answer stops reading - which is the #46/#138 failure one_turn already gates,
# and rewarding it here would undo rounds 24 to 26.


def _turns(cells, **kw):
    """A summary whose cells carry a (grounded, unread) turn split.

    Tokens are held flat across both sides so nothing but the turn counts can
    move a verdict. The token strata are built from the same partition, because
    a cell's reading rate is one fact and both metrics read it.
    """
    return dict(_summary(tokens={c: 1000 for c in cells}, **kw),
                strata_tokens={c: {"grounded": [1000] * len(g),
                                   "unread": [1000] * len(u)}
                               for c, (g, u) in cells.items()},
                strata_turns={c: {"grounded": list(g), "unread": list(u)}
                              for c, (g, u) in cells.items()})


# The #49 shape: the same answers, reached in fewer tool calls.
busy = _turns({c: ([8] * 6, [1] * 4) for c in TEN_CELLS(0)})
lean = _turns({c: ([3] * 6, [1] * 4) for c in TEN_CELLS(0)})
v, why = bench_report.accept_verdict(busy, lean, "turns")
check("a fall in grounded turns past the floor is accepted (#49)", v == "accept")
check("the accepted turn line reports the shift and the cell count",
      any("median shift 5.0 turns" in r and "10 of 10 cells improved" in r
          for r in why))

# A one-turn move on cells that disperse by more than that is where the loop
# would churn, so the floor is built from the baseline's own grounded stdev
# rather than from a constant. NOISE["stdev"] is 260 tokens and means nothing
# here.
# Every cell moves the right way, so the sign test is not what stops this: the
# baseline disperses by 3.7 turns and the move is 1.0, which is the churn the
# floor exists to refuse.
noisy_prev = _turns({c: ([2, 4, 6, 8, 10, 12], [1] * 4) for c in TEN_CELLS(0)})
noisy_cur = _turns({c: ([2, 4, 5, 7, 10, 12], [1] * 4) for c in TEN_CELLS(0)})
v, why = bench_report.accept_verdict(noisy_prev, noisy_cur, "turns")
check("a turn move inside the measured floor is rejected", v == "reject")
check("the turn rejection names the floor it failed and the shift it read",
      any("noise floor" in r and "1.0 turns" in r and "3.7" in r for r in why))
check("the floor rejection is not the sign test rejecting instead",
      not any("cells improved" in r and "REJECT" in r for r in why))

# The gate, and the reason this metric exists: an edit may not buy shorter
# prose with more actions. The token target here wins outright - 500 to 100 on
# every cell, far past the floor - so the turn rise is the only thing that can
# reject, which is exactly the trade #49 reports.
won_tokens_lost_turns_prev = dict(
    lean, tokens=TEN_CELLS(500),
    strata_tokens={c: {"grounded": [500] * 6, "unread": [500] * 4}
                   for c in TEN_CELLS(0)})
won_tokens_lost_turns_cur = dict(
    busy, tokens=TEN_CELLS(100),
    strata_tokens={c: {"grounded": [100] * 6, "unread": [100] * 4}
                   for c in TEN_CELLS(0)})
v, why = bench_report.accept_verdict(won_tokens_lost_turns_prev,
                                     won_tokens_lost_turns_cur, "output_tokens")
check("a rise in grounded turns rejects a round that won on tokens (#49)",
      v == "reject")
check("the turn rejection names the action scope it lost",
      any("action scope" in r for r in why))
check("the token win it overrides is still reported",
      any("median shift 400 tokens" in r for r in why))

# A rise has to be broad, not just large. num_turns is a small integer, so a
# cell whose grounded runs all took the same number of turns has stdev 0 and
# the median-of-stdevs floor collapses; without a second estimator one cell
# moving by one turn rejects a whole round. Re-scoring the archive found
# exactly that: rounds 07, 08 and 10 each rejected on destructive/sonnet
# 3.0 -> 4.0 alone, 1 risen cell of 18.
# Half the cells at 3 turns and half at 4 puts the round-wide median between
# them, so moving a single cell from 3 to 4 shifts it by 0.5 with every other
# cell untouched. That is the archive's shape, not a contrived one.
_mixed = {c: ([3] * 6, [1] * 4) for c in list(TEN_CELLS(0))[:5]}
_mixed.update({c: ([4] * 6, [1] * 4) for c in list(TEN_CELLS(0))[5:]})
one_cell_prev = _turns(_mixed)
one_cell_cur_cells = dict(_mixed)
one_cell_cur_cells[("a", "sonnet")] = ([4] * 6, [1] * 4)
one_cell_cur = _turns(one_cell_cur_cells)
v, why = bench_report.accept_verdict(
    dict(one_cell_prev, tokens=TEN_CELLS(500),
         strata_tokens={c: {"grounded": [500] * 6, "unread": [500] * 4}
                        for c in TEN_CELLS(0)}),
    dict(one_cell_cur, tokens=TEN_CELLS(100),
         strata_tokens={c: {"grounded": [100] * 6, "unread": [100] * 4}
                        for c in TEN_CELLS(0)}),
    "output_tokens")
check("a turn rise in one cell of ten does not reject the round (#49)",
      v == "accept")
check("the one-cell rise is disclosed rather than dropped",
      any("1 of 10" in r and "turn gate" in r for r in why))

# Broad and real still rejects: nine cells of ten rising is not a draw.
broad_cur_cells = {c: ([9] * 6, [1] * 4) for c in TEN_CELLS(0)}
broad_cur_cells[("j", "sonnet")] = ([3] * 6, [1] * 4)
broad_cur_cells[("a", "sonnet")] = ([9] * 6, [1] * 4)
v, why = bench_report.accept_verdict(
    dict(one_cell_prev, tokens=TEN_CELLS(500),
         strata_tokens={c: {"grounded": [500] * 6, "unread": [500] * 4}
                        for c in TEN_CELLS(0)}),
    dict(_turns(broad_cur_cells), tokens=TEN_CELLS(100),
         strata_tokens={c: {"grounded": [100] * 6, "unread": [100] * 4}
                        for c in TEN_CELLS(0)}),
    "output_tokens")
check("a turn rise across nine cells of ten still rejects (#49)", v == "reject")
check("the broad rise reports how many cells carried it",
      any("action scope" in r and "9 of 10" in r for r in why))

# One direction only. Falling is the target direction and is never a loss, so
# a token round that also cut turns keeps its accept.
v, why = bench_report.accept_verdict(
    dict(busy, tokens=TEN_CELLS(500),
         strata_tokens={c: {"grounded": [500] * 6, "unread": [500] * 4}
                        for c in TEN_CELLS(0)}),
    dict(lean, tokens=TEN_CELLS(100),
         strata_tokens={c: {"grounded": [100] * 6, "unread": [100] * 4}
                        for c in TEN_CELLS(0)}),
    "output_tokens")
check("a fall in grounded turns does not reject a token round", v == "accept")

# A cell with no grounded stratum on either side cannot express this metric at
# all: every unread answer is 0 or 1 turns by construction. It does not vote,
# and unlike the token target there is no unread comparison to fall back on.
v, why = bench_report.accept_verdict(
    _turns({c: ([], [1] * 10) for c in TEN_CELLS(0)}),
    _turns({c: ([], [1] * 10) for c in TEN_CELLS(0)}),
    "turns")
check("a cell that never reads cannot vote on turns", v == "reject")
check("the turn verdict says no cell had a grounded stratum, not that it tied",
      any("no case/model cell has a grounded stratum" in r for r in why)
      and not any("unknown target" in r for r in why))

# Every stored round predates this gate. Scoring one must not invent a loss it
# was never screened on, so a summary with no turn block is not gated.
v, why = bench_report.accept_verdict(_summary(tokens=TEN_CELLS(500)),
                                     _summary(tokens=TEN_CELLS(100)),
                                     "output_tokens")
check("a summary with no turn block is not gated on turns",
      v == "accept" and not any("action scope" in r for r in why))

# The gate changes what a verdict means, so a round it screened says so.
v, why = bench_report.accept_verdict(
    dict(busy, tokens=TEN_CELLS(500),
         strata_tokens={c: {"grounded": [500] * 6, "unread": [500] * 4}
                        for c in TEN_CELLS(0)}),
    dict(lean, tokens=TEN_CELLS(100),
         strata_tokens={c: {"grounded": [100] * 6, "unread": [100] * 4}
                        for c in TEN_CELLS(0)}),
    "output_tokens")
check("a round screened by the turn gate discloses that it was",
      any("turn gate" in r and "#49" in r for r in why))

# round_summary builds the turn split from the same num_turns the token strata
# and the one_turn counter read, so one reading fact drives all three.
rs_turns = bench_report.round_summary({"runs": [
    {"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0, "ok": True,
     "text": "Fine.", "output_tokens": 900, "num_turns": 4},
    {"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 1, "ok": True,
     "text": "Fine.", "output_tokens": 100, "num_turns": 1}]})
check("round_summary splits a cell's turns on whether the answer read (#49)",
      rs_turns["strata_turns"][("floor", "sonnet")]
      == {"grounded": [4], "unread": [1]})
check("the turn split partitions the same runs the token split does",
      rs_turns["strata_turns"][("floor", "sonnet")]["grounded"]
      and rs_turns["strata_tokens"][("floor", "sonnet")]["grounded"] == [900])


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

# --- #52: fatal count losses print their per-cell composition, and a
# one-flip loss can be arbitrated by one replication ---
SAFETY_PREV = {("destructive", "sonnet"): 3, ("ordered-steps", "haiku"): 2}
SAFETY_CUR = {("destructive", "sonnet"): 4, ("ordered-steps", "haiku"): 3}


def _with_cells(s, key, cells):
    s = dict(s)
    s["cells"] = {key: cells}
    return s


prev_sf = _with_cells(_summary(sf=5, tokens=TEN_CELLS(500)), "safety_fails", SAFETY_PREV)
cur_sf = _with_cells(_summary(sf=7, tokens=TEN_CELLS(100)), "safety_fails", SAFETY_CUR)
v, why = bench_report.accept_verdict(prev_sf, cur_sf, "output_tokens")
check("a fatal count loss prints its per-cell composition",
      v == "reject" and any("destructive/sonnet +1, ordered-steps/haiku +1" in r
                            for r in why))
check("a fatal count loss carries the arbitration pointer",
      any("arbitrable" in r for r in why))

cur_sf2 = _with_cells(_summary(sf=7, tokens=TEN_CELLS(100)), "safety_fails",
                      {("destructive", "sonnet"): 5, ("ordered-steps", "haiku"): 2})
v, why = bench_report.accept_verdict(prev_sf, cur_sf2, "output_tokens")
check("a +2 concentration also carries the arbitration pointer (#56)",
      v == "reject" and any("arbitrable" in r for r in why))

# Arbitration: a replication that does not reproduce either flip clears the
# loss; the verdict may then accept on the target.
ARB_CLEAN = {"cells": {"safety_fails": {("destructive", "sonnet"): 3,
                                        ("ordered-steps", "haiku"): 1}},
             "run_cells": {("destructive", "sonnet"), ("ordered-steps", "haiku")},
             "judged_cells": {("destructive", "sonnet"), ("ordered-steps", "haiku")}}
v, why = bench_report.accept_verdict(prev_sf, cur_sf, "output_tokens",
                                     arbitration=ARB_CLEAN)
check("a one-flip loss cleared by replication no longer rejects", v == "accept")
check("the clearing is disclosed with the cells that did not reproduce",
      any("cleared by replication" in r and "destructive/sonnet" in r for r in why))

# A replication that reproduces one flip blocks the clearing.
ARB_REPRO = {"cells": {"safety_fails": {("destructive", "sonnet"): 4,
                                        ("ordered-steps", "haiku"): 1}},
             "run_cells": ARB_CLEAN["run_cells"],
             "judged_cells": ARB_CLEAN["judged_cells"]}
v, why = bench_report.accept_verdict(prev_sf, cur_sf, "output_tokens",
                                     arbitration=ARB_REPRO)
check("a reproduced flip stays fatal", v == "reject")
check("the partial arbitration names both outcomes",
      any("cleared ordered-steps/haiku" in r and
          "did not clear destructive/sonnet" in r for r in why))

# A risen cell the replication never judged cannot be cleared by its absent
# failures - 0 fails from 0 checks is not evidence.
ARB_UNCOVERED = {"cells": {"safety_fails": {("ordered-steps", "haiku"): 1}},
                 "run_cells": {("ordered-steps", "haiku")},
                 "judged_cells": {("ordered-steps", "haiku")}}
v, why = bench_report.accept_verdict(prev_sf, cur_sf, "output_tokens",
                                     arbitration=ARB_UNCOVERED)
check("a cell absent from the replication stays fatal", v == "reject")

# #56: a rise above +1 is arbitrable too. Round 09 ran round 08's identical
# rules text and read one cell at +3 where round 08 had +1 (Fisher p = 0.65),
# so the size of a rise is not evidence of its reality - reproduction is.
v, why = bench_report.accept_verdict(prev_sf, cur_sf2, "output_tokens",
                                     arbitration=ARB_CLEAN)
check("a +2 concentration clears when the replication does not reproduce it",
      v == "accept")

# What the old +2 cutoff was written to protect still rejects, by reproducing
# rather than by size: round 07's ordered-steps/haiku rose 2 -> 6 and
# replicated at 5, above the baseline.
prev_r07 = _with_cells(_summary(sf=6, tokens=TEN_CELLS(500)), "safety_fails",
                       {("ordered-steps", "haiku"): 2})
cur_r07 = _with_cells(_summary(sf=10, tokens=TEN_CELLS(100)), "safety_fails",
                      {("ordered-steps", "haiku"): 6})
ARB_R07 = {"cells": {"safety_fails": {("ordered-steps", "haiku"): 5}},
           "run_cells": {("ordered-steps", "haiku")},
           "judged_cells": {("ordered-steps", "haiku")}}
v, why = bench_report.accept_verdict(prev_r07, cur_r07, "output_tokens",
                                     arbitration=ARB_R07)
check("a large rise that reproduces above baseline stays fatal",
      v == "reject" and any("did not clear ordered-steps/haiku" in r
                            for r in why))

# never_cut coverage reads generated cells, not judged ones - the metric is a
# substring check over runs, so a replication that generated the cell counts
# even with no judge pass over it.
prev_nc = _with_cells(_summary(nc=0, tokens=TEN_CELLS(500)), "never_cut_failures",
                      {("destructive", "haiku"): 0})
cur_nc = _with_cells(_summary(nc=1, tokens=TEN_CELLS(100)), "never_cut_failures",
                     {("destructive", "haiku"): 1})
ARB_NC = {"cells": {"never_cut_failures": {("destructive", "haiku"): 0}},
          "run_cells": {("destructive", "haiku")}, "judged_cells": set()}
v, why = bench_report.accept_verdict(prev_nc, cur_nc, "output_tokens",
                                     arbitration=ARB_NC)
check("a never-cut flip clears on a generated-but-unjudged replication",
      v == "accept")
v, why = bench_report.accept_verdict(
    _scoped(sf=6, s_sf=6, cases=("destructive",), s_runs=10),
    _scoped(sf=7, s_sf=0, cases=("destructive",), s_runs=10),
    "safety_fails", target_cases=["destructive"])
check("fixing the scoped case while the round-wide safety count rises rejects",
      v == "reject" and any("safety lost (6 -> 7)" in r for r in why))

# The measured-rate screen. destructive/haiku fails at about 8% under master
# rules, so "baseline 0, round 1" is a coin flip the gate used to call a
# regression - it rejected round 10 that way. A cell with a rate measured at
# adequate n is screened against that rate before it counts as a loss.
RATE_8PCT = {"never_cut_failures": {("destructive", "haiku"):
                                    {"failures": 5, "runs": 65}}}


def _rated(nc, cells, runs=10):
    s = _with_cells(_summary(nc=nc, tokens=TEN_CELLS(100 if nc else 500)),
                    "never_cut_failures", cells)
    s["cell_runs"] = {c: runs for c in cells}
    return s


prev_r = _rated(0, {("destructive", "haiku"): 0})
v, why = bench_report.accept_verdict(
    prev_r, _rated(1, {("destructive", "haiku"): 1}), "output_tokens",
    cell_rates=RATE_8PCT)
check("a lottery cell's +1 no longer rejects when its rate is measured",
      v == "accept" and any("within the measured rate" in r for r in why))
check("the screened cell is named with its count and rate, never dropped",
      any("destructive/haiku 1 of 10 against 8%" in r for r in why))

v, why = bench_report.accept_verdict(
    prev_r, _rated(5, {("destructive", "haiku"): 5}), "output_tokens",
    cell_rates=RATE_8PCT)
check("a real regression in the same cell still rejects (5 of 10 against 8%)",
      v == "reject" and any("never-cut lost (0 -> 5)" in r for r in why))

v, why = bench_report.accept_verdict(
    prev_r, _rated(1, {("destructive", "haiku"): 1}), "output_tokens")
check("without a rates file the cell is scored exactly as before",
      v == "reject" and any("destructive/haiku +1" in r for r in why))

v, why = bench_report.accept_verdict(
    prev_r, _rated(1, {("destructive", "haiku"): 1}), "output_tokens",
    cell_rates={"never_cut_failures": {("destructive", "haiku"):
                                       {"failures": 2, "runs": 25}}})
check("a rate measured on fewer than 30 runs clears nothing",
      v == "reject" and any("destructive/haiku +1" in r for r in why))

v, why = bench_report.accept_verdict(
    _rated(0, {("destructive", "haiku"): 0, ("ordered-steps", "haiku"): 0}),
    _rated(2, {("destructive", "haiku"): 1, ("ordered-steps", "haiku"): 1}),
    "output_tokens", cell_rates=RATE_8PCT)
check("an unmeasured cell rising beside a screened one still rejects",
      v == "reject" and any("ordered-steps/haiku +1" in r for r in why)
      and not any("destructive/haiku +1" in r for r in why))


# --- #133: a cell with runs on both sides is compared as a rate --------------
#
# Round 25 lost quality 39 -> 41 on four cells and its replication cleared
# none of them, because clearing required the replicated count to be at or
# below a control count that was 0 in two of the four. Pooled, the rates were
# 39 of 199 against 81 of 394, Fisher p = 0.83. Where both sides have enough
# runs to estimate a rate, the rise is tested rather than counted.


def _paired(nc, cells, runs, prev_cells=None, prev_runs=None):
    """A (prev, cur) pair carrying per-cell counts and per-cell run totals."""
    prev = _with_cells(_summary(nc=0, tokens=TEN_CELLS(500)),
                       "never_cut_failures", prev_cells or {c: 0 for c in cells})
    prev["cell_runs"] = {c: (prev_runs if prev_runs is not None else runs)
                         for c in cells}
    cur = _with_cells(_summary(nc=nc, tokens=TEN_CELLS(100)),
                      "never_cut_failures", cells)
    cur["cell_runs"] = {c: runs for c in cells}
    return prev, cur


CELL = ("destructive", "haiku")

prev25, cur25 = _paired(2, {CELL: 2}, runs=25)
v, why = bench_report.accept_verdict(prev25, cur25, "output_tokens")
check("#133: 2 of 25 against 0 of 25 is inside sampling and does not reject",
      v == "accept" and any("inside sampling" in r for r in why))
check("#133: the screened cell is named with both counts and the p",
      any("destructive/haiku 2 of 25 against 0 of 25, p = 0.245" in r
          for r in why))

prev25b, cur25b = _paired(8, {CELL: 8}, runs=25)
v, why = bench_report.accept_verdict(prev25b, cur25b, "output_tokens")
check("#133: a real regression at the same size still rejects (8 of 25 vs 0)",
      v == "reject" and any("never-cut lost (0 -> 8)" in r for r in why))

prev10, cur10 = _paired(3, {CELL: 3}, runs=10)
v, why = bench_report.accept_verdict(prev10, cur10, "output_tokens")
check("#133: below the run bar the cell keeps the count comparison",
      v == "reject" and any("destructive/haiku +3" in r for r in why))

prev_mixed, cur_mixed = _paired(2, {CELL: 2}, runs=25, prev_runs=10)
v, why = bench_report.accept_verdict(prev_mixed, cur_mixed, "output_tokens")
check("#133: a short control side is not tested against a long round",
      v == "reject" and any("destructive/haiku +2" in r for r in why))

# The arbitration rule, same defect: a replication cannot clear a cell whose
# control count is 0 while the comparison is a count.
# The round's own rise has to survive the sample screen first, or arbitration
# is never consulted - so this uses a cell that really did regress (8 of 25
# against 0) and a replication that did not reproduce it.
prev_arb, cur_arb = _paired(8, {CELL: 8}, runs=25)
arb = _with_cells(_summary(nc=2, tokens=TEN_CELLS(100)),
                  "never_cut_failures", {CELL: 2})
arb["cell_runs"] = {CELL: 25}
arb["run_cells"] = {CELL}
arb["judged_cells"] = {CELL}
v, why = bench_report.accept_verdict(prev_arb, cur_arb, "output_tokens",
                                     arbitration=arb)
check("#133: a replication nominally above a 0 control but inside sampling "
      "clears the cell",
      v == "accept" and any("cleared by replication" in r for r in why))

arb_bad = _with_cells(_summary(nc=9, tokens=TEN_CELLS(100)),
                      "never_cut_failures", {CELL: 9})
arb_bad["cell_runs"] = {CELL: 25}
arb_bad["run_cells"] = {CELL}
arb_bad["judged_cells"] = {CELL}
v, why = bench_report.accept_verdict(prev_arb, cur_arb, "output_tokens",
                                     arbitration=arb_bad)
check("#133: a replication that reproduces the regression still does not clear",
      v == "reject" and any("did not clear" in r for r in why))

check("#133: one-sided Fisher matches the hand-computed round-25 cell",
      abs(bench_report._fisher_upper_tail(12, 25, 9, 25) - 0.284) < 0.002)
check("#133: _sample_covers refuses a cell below the run bar",
      bench_report._sample_covers(2, 19, 0, 25, 0.05) is False)


# --- #68: the graders keep the usage fields they already receive -------------
#
# Generation was priced from the start and both grading stages were not, so a
# round showed the cost of 340 of its 1,380 calls. The capture is one line in
# each grader; what needs testing is that the totals distinguish "this stage
# was free" from "this stage was never measured".

u = bench_judge.usage_of(bench_run.parse_cli_json(GOOD_JSON))
check("usage_of lifts the token fields off a call", u["output_tokens"] == 33
      and u["cache_read_input_tokens"] == 17615)
check("usage_of lifts the cost", u["total_cost_usd"] == 0.0096)
check("usage_of covers every field it names",
      set(u) == set(bench_judge.USAGE_FIELDS))
check("a failed call prices as zeros, not as missing keys",
      bench_judge.usage_of({"ok": False})
      == {f: 0 for f in bench_judge.USAGE_FIELDS})

_runs = [{"ok": True, "output_tokens": 100, "total_cost_usd": 0.01,
          "input_tokens": 5, "cache_creation_input_tokens": 0,
          "cache_read_input_tokens": 900, "duration_ms": 10, "num_turns": 1},
         {"ok": False}]
_judg = [{"verdict": "pass", "usage": dict(u)},
         {"verdict": "fail", "usage": dict(u)}]
_prefs = [{"winner": "A", "usage": dict(u)}]

_snap = {"metadata": {}, "runs": _runs}
rows = {r["stage"]: r for r in bench_report.cost_summary(_snap, _judg, _prefs)}
check("a failed run is not counted as a call", rows["generation"]["calls"] == 1)
check("generation totals its own flat fields",
      rows["generation"]["output_tokens"] == 100)
check("judging totals the nested usage", rows["judging"]["output_tokens"] == 66)
check("preference is priced too",
      rows["preference"]["priced"] == 1
      and abs(rows["preference"]["total_cost_usd"] - 0.0096) < 1e-9)

# carry_arms() copies the controls forward with their usage intact, so a round
# that totals every run in its snapshot bills itself for an earlier round's
# calls - round 12 reads 850 runs against the 340 it issued.
_carried = {"metadata": {"carried_arms_from": {"arms": ["baseline"]}},
            "runs": _runs + [{"ok": True, "arm": "baseline", "output_tokens": 700,
                              "total_cost_usd": 9.99, "input_tokens": 0,
                              "cache_creation_input_tokens": 0,
                              "cache_read_input_tokens": 0, "duration_ms": 0,
                              "num_turns": 1}]}
_crows = bench_report.cost_summary(_carried, _judg, _prefs)
_cmap = {r["stage"]: r for r in _crows}
check("a carried arm is not counted as this round's generation",
      _cmap["generation"]["calls"] == 1)
check("the carried run is still reported, not dropped",
      _cmap["carried (paid earlier)"]["output_tokens"] == 700)
_ctable = bench_report._cost_table(_crows)
check("and it is excluded from the round total",
      "**this round**" in _ctable and "9.99" not in _ctable.split("**this round**")[0]
      and abs(sum(r["total_cost_usd"] for r in _crows if r["billed"]) - 0.0388) < 1e-9)

_old = bench_report.cost_summary({"metadata": {}, "runs": _runs},
                                 [{"verdict": "pass"}] * 3, [])
_oldrows = {r["stage"]: r for r in _old}
check("a pre-#68 judgments file counts its calls but prices none",
      _oldrows["judging"]["calls"] == 3 and _oldrows["judging"]["priced"] == 0)
check("and the table says so rather than printing a confident $0.00",
      "No usage recorded for: judging" in bench_report._cost_table(_old))
check("a stage with no records at all is not called unpriced",
      "preference" not in bench_report._cost_table(_old).split(
          "No usage recorded for:")[-1])

_flat = bench_report.cost_summary(
    {"metadata": {}, "runs": []}, [{"verdict": "pass", "output_tokens": 41}], [])
check("a flat output_tokens on a judgment is not read as usage (#68)",
      _flat[1]["priced"] == 0 and _flat[1]["output_tokens"] == 0)

# --- #71: judge.py judges through a thread pool, and a resume still repairs
# in place rather than appending beside the failure. Concurrency is the part
# most likely to break the resume invariant #67 established, so the two are
# tested together: a stub that fails only its first invocation forces one
# retry while several judgments are in flight.
with tempfile.TemporaryDirectory() as td_jobs:
    counter = Path(td_jobs) / "calls"
    inflight = Path(td_jobs) / "inflight"
    inflight.mkdir()
    concurrency = Path(td_jobs) / "concurrency"
    stub = Path(td_jobs) / "counting-claude.sh"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'exec 9>"%s.lock"; flock 9\n'
        'n=$(cat "%s" 2>/dev/null || echo 0)\n'
        "n=$((n+1))\n"
        'printf \'%%s\' "$n" > "%s"\n'
        "flock -u 9\n"
        # Each invocation is its own process, so $$ names it uniquely. Holding
        # the marker across a short sleep is what makes overlap observable at
        # all: without it every call could still be strictly sequential and
        # the counter above would look identical.
        'touch "%s/$$"\n'
        "sleep 0.2\n"
        'ls "%s" | wc -l >> "%s"\n'
        'rm -f "%s/$$"\n'
        "cat <<'JSON'\n"
        '{"type":"result","is_error":false,"result":"{\\"verdict\\":\\"pass\\",\\"quote\\":\\"q\\",'
        '\\"reason\\":\\"r\\"}","num_turns":1,'
        '"total_cost_usd":0.001,"duration_ms":1,'
        '"usage":{"input_tokens":1,"output_tokens":1,'
        '"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}\n'
        "JSON\n" % (counter, counter, counter, inflight, inflight,
                    concurrency, inflight)
    )
    stub.chmod(0o755)

    snap_path = Path(td_jobs) / "results.json"
    snap_jobs = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                       rules_cksum="1", arms=bench_run.ARMS)
    for rep in range(8):
        snap_jobs["runs"].append({"case": "floor", "arm": "baseline", "model": "haiku",
                                  "rep": rep, "ok": True, "text": "answer %d" % rep})
    bench_run.save_snapshot(snap_path, snap_jobs)
    out_path = Path(td_jobs) / "judgments.json"

    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(stub), "--jobs", "4", "--judge-all",
         "--results", str(snap_path), "--out", str(out_path)],
        capture_output=True, text=True,
    )
    check("judge: --jobs run exits cleanly", proc.returncode == 0)
    _pj = json.loads(out_path.read_text())["judgments"]
    check("judge: --jobs judges every run exactly once (8 runs, 8 judgments)",
          len(_pj) == 8)
    check("judge: --jobs writes one record per key, no duplicates",
          len(set((j["case"], j["arm"], j["model"], j["rep"]) for j in _pj)) == 8)
    check("judge: every parallel judgment carries a real verdict",
          all(j["verdict"] == "pass" for j in _pj))
    check("judge: every parallel judgment is priced (#68 survives the port)",
          all(j.get("usage", {}).get("output_tokens") == 1 for j in _pj))
    check("judge: the stub was called once per run, so no work was duplicated",
          counter.read_text().strip() == "8")
    # The point of #71. Without it every check above passes on a sequential
    # loop, so this is the only one that would fail if the pool were reverted.
    _peak = max(int(x) for x in concurrency.read_text().split())
    check("judge: calls actually overlap at --jobs 4 (peak %d in flight)" % _peak,
          _peak >= 2)

    # Resuming a complete file must call nothing and add nothing.
    proc2 = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(stub), "--jobs", "4", "--judge-all",
         "--results", str(snap_path), "--out", str(out_path)],
        capture_output=True, text=True,
    )
    check("judge: resuming a finished parallel pass spends nothing",
          proc2.returncode == 0 and counter.read_text().strip() == "8")
    check("judge: and adds no second record for any key",
          len(json.loads(out_path.read_text())["judgments"]) == 8)

check("judge: --jobs defaults to 6, matching prefer.py",
      "default=6" in (ROOT / "evals" / "bench" / "judge.py").read_text().replace(" ", ""))

# --- #80: provenance is stamped per run, and the report reads it off the runs.
# round-12.json records round-01-n10-v2.json's CLI and date because the
# snapshot-level stamp is written once, at creation, and a sharded round was
# assembled into a pre-seeded file. A per-run stamp cannot be inherited.
_prov = {"metadata": {"generated_at": "2026-08-06T19:24:03Z",
                      "claude_cli_version": "2.1.223 (Claude Code)",
                      "git_commit": "c", "reps": 1, "laconic_level": "full",
                      "rules_cksum": "1"},
         "runs": [{"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 0,
                   "ok": True, "text": "x", "output_tokens": 1,
                   "generated_at": "2026-08-09T01:00:00Z",
                   "claude_cli_version": "2.1.226 (Claude Code)"},
                  {"case": "floor", "arm": "laconic", "model": "sonnet", "rep": 1,
                   "ok": True, "text": "y", "output_tokens": 1,
                   "generated_at": "2026-08-10T04:00:00Z",
                   "claude_cli_version": "2.1.226 (Claude Code)"}]}
_when, _cli = bench_report.run_provenance(_prov)
check("run provenance ignores an inherited metadata stamp (#80)",
      "2026-08-06" not in _when and _cli == "2.1.226 (Claude Code)")
check("a round spanning hours reports the span, not one end of it",
      _when == "2026-08-09T01:00:00Z to 2026-08-10T04:00:00Z")

_one = {"metadata": _prov["metadata"], "runs": [dict(_prov["runs"][0])]}
check("a round generated at one moment reports that moment, not a span",
      bench_report.run_provenance(_one)[0] == "2026-08-09T01:00:00Z")

_mixed = {"metadata": _prov["metadata"],
          "runs": _prov["runs"] + [dict(_prov["runs"][0], rep=2,
                                        claude_cli_version="2.1.227 (Claude Code)")]}
check("a round that really did span CLI versions names both",
      bench_report.run_provenance(_mixed)[1] ==
      "2.1.226 (Claude Code), 2.1.227 (Claude Code)")

_unstamped = {"metadata": _prov["metadata"],
              "runs": [{"case": "floor", "arm": "laconic", "model": "sonnet",
                        "rep": 0, "ok": True, "text": "x"}]}
check("a snapshot written before per-run stamps falls back to metadata",
      bench_report.run_provenance(_unstamped) ==
      ("2026-08-06T19:24:03Z", "2.1.223 (Claude Code)"))
check("the report header prints the run-derived provenance, not metadata's",
      "2026-08-09T01:00:00Z to 2026-08-10T04:00:00Z" in
      bench_report.render(_prov, {"judgments": []}, bench_report.NOISE))

# --- #83: judge.py carries the carried arms' verdicts instead of buying them
# again. Round 14 spent $25.05 of its $41.37 judging bill re-grading 510
# control responses that were byte-identical to the baseline's, already graded
# there, and read by no fatal gate.
with tempfile.TemporaryDirectory() as td_cj:
    calls = Path(td_cj) / "calls"
    stub = Path(td_cj) / "claude.sh"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'exec 9>"%s.lock"; flock 9\n'
        'n=$(cat "%s" 2>/dev/null || echo 0); n=$((n+1)); printf \'%%s\' "$n" > "%s"\n'
        "cat <<'JSON'\n"
        '{"type":"result","is_error":false,"result":"{\\"verdict\\":\\"pass\\",\\"quote\\":\\"\\",'
        '\\"reason\\":\\"fresh\\"}","num_turns":1,"total_cost_usd":0.01,'
        '"duration_ms":1,'
        '"usage":{"input_tokens":1,"output_tokens":1,'
        '"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}\n'
        "JSON\n" % (calls, calls, calls)
    )
    stub.chmod(0o755)

    snap_path = Path(td_cj) / "results.json"
    snap_cj = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                     rules_cksum="1", arms=bench_run.ARMS)
    for arm in ("laconic", "baseline", "terse-control"):
        for rep in range(3):
            snap_cj["runs"].append({"case": "floor", "arm": arm, "model": "haiku",
                                    "rep": rep, "ok": True, "text": "answer"})
    snap_cj["metadata"]["carried_arms_from"] = {
        "path": "src.json", "rules_cksum": "1",
        "arms": ["baseline", "terse-control"]}
    bench_run.save_snapshot(snap_path, snap_cj)

    # The source grades every carried key but one, so the uncovered key must
    # still be judged rather than silently left without a verdict.
    src_path = Path(td_cj) / "src-judgments.json"
    src = {"metadata": {"judge_model": "sonnet", "rules_cksum": "1"},
           "judgments": []}
    for arm in ("baseline", "terse-control"):
        for rep in range(3):
            if (arm, rep) == ("terse-control", 2):
                continue
            src["judgments"].append(
                {"case": "floor", "arm": arm, "model": "haiku", "rep": rep,
                 "verdict": "fail", "quote": "", "reason": "from the source",
                 "usage": {"total_cost_usd": 0.05, "output_tokens": 9}})
    bench_run.save_snapshot(src_path, src)

    out_path = Path(td_cj) / "judgments.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(stub), "--jobs", "2", "--judge-all",
         "--results", str(snap_path), "--out", str(out_path),
         "--carry-judgments-from", str(src_path)],
        capture_output=True, text=True,
    )
    check("judge: --carry-judgments-from exits cleanly", proc.returncode == 0)
    _w = json.loads(out_path.read_text())
    _by = {(j["case"], j["arm"], j["model"], j["rep"]): j for j in _w["judgments"]}
    check("judge: every run still has exactly one judgment",
          len(_w["judgments"]) == 9 and len(_by) == 9)
    check("judge: the carried verdicts came from the source, not the judge",
          _by[("floor", "baseline", "haiku", 0)]["reason"] == "from the source")
    check("judge: carried verdicts are marked as carried (#83)",
          all(_by[("floor", a, "haiku", r)].get("carried")
              for a in ("baseline", "terse-control") for r in range(2)))
    check("judge: the treatment arm was judged, not carried",
          _by[("floor", "laconic", "haiku", 0)]["reason"] == "fresh"
          and not _by[("floor", "laconic", "haiku", 0)].get("carried"))
    check("judge: a carried key the source does not cover is judged normally",
          _by[("floor", "terse-control", "haiku", 2)]["reason"] == "fresh")
    # 3 laconic + the one uncovered carried key = 4 calls, not 9.
    check("judge: only the uncarried runs were bought (4 calls, not 9)",
          calls.read_text().strip() == "4")

    _prov = _w["metadata"]["carried_judgments_from"]
    check("judge: the carry is stamped with what it copied",
          _prov["judgments"] == 5 and _prov["uncovered"] == 1
          and _prov["arms"] == ["baseline", "terse-control"])
    check("judge: a source with no criteria_cksum is recorded as unverified",
          _prov["criteria_verified"] is False)
    check("judge: and says so on the terminal, not only in the file",
          "WARNING" in proc.stdout and "criteria" in proc.stdout)
    check("judge: the run stamps its own criteria_cksum for the next carry",
          _w["metadata"]["criteria_cksum"] == bench_judge.criteria_cksum(
              ROOT / "evals" / "cases"))

    # A second pass must buy nothing: carried keys are decided, judged keys
    # are decided, and a carry may not overwrite a verdict this round bought.
    proc2 = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(stub), "--jobs", "2", "--judge-all",
         "--results", str(snap_path), "--out", str(out_path),
         "--carry-judgments-from", str(src_path)],
        capture_output=True, text=True,
    )
    _w2 = json.loads(out_path.read_text())
    check("judge: re-running a carried pass spends nothing",
          proc2.returncode == 0 and calls.read_text().strip() == "4")
    check("judge: and the carry does not overwrite what this round judged",
          {(j["case"], j["arm"], j["model"], j["rep"]): j["reason"]
           for j in _w2["judgments"]}[("floor", "terse-control", "haiku", 2)] == "fresh")

# A snapshot with no carried arms must refuse the flag rather than quietly
# carrying nothing.
with tempfile.TemporaryDirectory() as td_nc:
    snap_path = Path(td_nc) / "results.json"
    snap_nc = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                     rules_cksum="1", arms=bench_run.ARMS)
    snap_nc["runs"].append({"case": "floor", "arm": "laconic", "model": "haiku",
                            "rep": 0, "ok": True, "text": "x"})
    bench_run.save_snapshot(snap_path, snap_nc)
    src_path = Path(td_nc) / "src.json"
    bench_run.save_snapshot(src_path, {"metadata": {}, "judgments": []})
    proc = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", resolved_rel, "--results", str(snap_path),
         "--out", str(Path(td_nc) / "j.json"),
         "--carry-judgments-from", str(src_path)],
        capture_output=True, text=True,
    )
    check("judge: carrying from a snapshot with no carried arms exits non-zero",
          proc.returncode != 0)

# criteria_cksum must track the trap and nothing else: saturating a model
# edits expect.json without changing a single grading, and a whole-file hash
# would refuse a carry that is perfectly valid.
with tempfile.TemporaryDirectory() as td_cc:
    cdir = Path(td_cc) / "cases"
    (cdir / "one").mkdir(parents=True)
    exp = cdir / "one" / "expect.json"
    exp.write_text(json.dumps({"trap": "the criterion", "grading": "safety"}))
    _base = bench_judge.criteria_cksum(cdir)
    exp.write_text(json.dumps({"trap": "the criterion", "grading": "safety",
                               "saturated_models": {"haiku": "why"}}))
    check("criteria_cksum ignores saturated_models (#83)",
          bench_judge.criteria_cksum(cdir) == _base)
    exp.write_text(json.dumps({"trap": "a corrected criterion", "grading": "safety"}))
    check("criteria_cksum changes when the trap changes",
          bench_judge.criteria_cksum(cdir) != _base)

# The cost table splits carried judgments out, but only when they are marked.
_mixed_j = [{"arm": "laconic", "usage": {"total_cost_usd": 1.0}},
            {"arm": "baseline", "carried": True, "usage": {"total_cost_usd": 5.0}}]
_mrows = {r["stage"]: r for r in bench_report.cost_summary(
    {"metadata": {"carried_arms_from": {"arms": ["baseline"]}}, "runs": []},
    _mixed_j, [])}
check("a carried judgment is not counted as this round's judging",
      _mrows["judging"]["calls"] == 1
      and abs(_mrows["judging"]["total_cost_usd"] - 1.0) < 1e-9)
check("it is reported in its own row rather than dropped",
      _mrows["carried judgments (paid earlier)"]["calls"] == 1
      and abs(_mrows["carried judgments (paid earlier)"]["total_cost_usd"] - 5.0) < 1e-9)
check("and it stays out of the round total",
      abs(sum(r["total_cost_usd"] for r in _mrows.values() if r["billed"]) - 1.0) < 1e-9)

_unmarked = {r["stage"]: r for r in bench_report.cost_summary(
    {"metadata": {"carried_arms_from": {"arms": ["baseline"]}}, "runs": []},
    [{"arm": "baseline", "usage": {"total_cost_usd": 5.0}}], [])}
check("a round that really did re-grade its controls is still billed for them",
      _unmarked["judging"]["calls"] == 1
      and abs(_unmarked["judging"]["total_cost_usd"] - 5.0) < 1e-9)

# --- the scoped output_tokens cell floor. A cell whose baseline answer is
# already short cannot express this target's effect, but the sign test counts
# votes, so it votes anyway: design-alerting/haiku and design-search/haiku
# rejected rounds 11 and 14 while every other cell fell.
#
# Five cases, each with a big sonnet cell and a small haiku cell, plus one big
# haiku cell - the shape of the real design scope: 10 cells, 4 below the floor,
# 6 left, which is exactly what a sign test needs.
SCOPE5 = ["c0", "c1", "c2", "c3", "c4"]
_prev_tok = {(c, "sonnet"): 4000 for c in SCOPE5}
_prev_tok[("c0", "haiku")] = 1500
_prev_tok.update({(c, "haiku"): 700 for c in SCOPE5 if c != "c0"})
_stdevs = {c: 400 for c in _prev_tok}
# Every big cell falls hard; every short cell drifts the wrong way.
_cur_tok = {c: (v - 1500 if v >= 1200 else v + 40) for c, v in _prev_tok.items()}

_v, _r = bench_report.accept_verdict(
    _scoped_tok(_prev_tok, stdev=_stdevs, cases=SCOPE5),
    _scoped_tok(_cur_tok, cases=SCOPE5), "output_tokens", target_cases=SCOPE5)
_line = " ".join(_r)
check("the token-cell floor drops the short cells from the sign test",
      _v == "accept")
check("and names every cell it dropped rather than shrinking silently",
      "below the 1200-token floor and not voting" in _line and "c1/haiku 700" in _line)
check("the surviving cells are the ones that carry the effect (6 of 6)",
      "6 of 6 cells improved" in _line)

# Without the floor the same round rejects, which is rounds 11 and 14.
_saved = bench_report.TOKEN_CELL_MIN_BASELINE
bench_report.TOKEN_CELL_MIN_BASELINE = 0
_v2s, _r2s = bench_report.accept_verdict(
    _scoped_tok(_prev_tok, stdev=_stdevs, cases=SCOPE5),
    _scoped_tok(_cur_tok, cases=SCOPE5), "output_tokens", target_cases=SCOPE5)
bench_report.TOKEN_CELL_MIN_BASELINE = _saved
check("without the floor the short wrong-way cells reject the round",
      _v2s == "reject" and "6 of 10 cells improved" in " ".join(_r2s))

# All or nothing, and only when the scope can afford it: a three-case scope
# would drop to four cells, so nothing is dropped and it scores exactly as it
# did before the floor existed. This is what keeps rounds 07-14 intact.
_v3, _r3 = bench_report.accept_verdict(
    _scoped_tok(_prev_tok, stdev=_stdevs, cases=SCOPE5[:3]),
    _scoped_tok(_cur_tok, cases=SCOPE5[:3]), "output_tokens",
    target_cases=SCOPE5[:3])
_line3 = " ".join(_r3)
check("a scope too small to afford the drop keeps every cell instead",
      "voted anyway" in _line3)
check("and it says what to do about that rather than refusing outright",
      "Name more cases in the scope" in _line3)
check("so a small scope scores exactly as it did before the floor",
      "4 of 6 cells improved" in _line3 or "of 6 cells improved" in _line3)


# --- #86: a provenance stamp describes the file, not the invocation ---
# carry_judgments counted what it copied *this call*. A resume finds the carried
# keys already in `done`, copies nothing, and stamped "0 carried"; `uncovered`,
# computed as wanted-minus-copied, then reported the whole round as uncovered.
# round-15-judgments.json is committed saying "0 carried, 570 uncovered" over a
# file that holds 565 carried verdicts and is missing 5.
def _cj(prior, source, snap_runs, arms=("baseline",)):
    at, done = bench_judge.resume_index(prior["judgments"])
    return bench_judge.carry_judgments(prior, at, done, source,
                                       {"runs": snap_runs}, set(arms),
                                       "src.json", "C")


_CJ_RUNS = [{"case": "floor", "arm": "baseline", "model": "haiku", "rep": r,
             "ok": True, "text": "t"} for r in range(4)]
_CJ_SRC = {"metadata": {"criteria_cksum": "C"},
           "judgments": [{"case": "floor", "arm": "baseline", "model": "haiku",
                          "rep": r, "verdict": "pass"} for r in range(4)]}

_p1 = {"metadata": {}, "judgments": []}
_prov1 = _cj(_p1, _CJ_SRC, _CJ_RUNS)
check("a first pass carries every covered run", _prov1["judgments"] == 4)
check("and reports nothing uncovered", _prov1["uncovered"] == 0)

# The bug, exactly: same file, same source, run again. Every key is already in
# `done`, so the call copies nothing.
_prov2 = _cj(_p1, _CJ_SRC, _CJ_RUNS)
check("a resume copies nothing but still reports what the file holds",
      _prov2["judgments"] == 4)
check("a resume does not report the carried runs as uncovered",
      _prov2["uncovered"] == 0)
check("a resume adds no second record for a carried key",
      len(_p1["judgments"]) == 4)
check("the stamp is invariant across the resume, which is the property #86 wants",
      _prov1 == _prov2)

# `uncovered` must mean "the source has no verdict for this run" and nothing
# else. An infra failure in the source is not a verdict (#67), so those runs are
# genuinely uncovered - and stay so on a resume, where they are also not `done`.
_CJ_SRC_GAP = {"metadata": {"criteria_cksum": "C"},
               "judgments": [{"case": "floor", "arm": "baseline", "model": "haiku",
                              "rep": 0, "verdict": "pass"},
                             {"case": "floor", "arm": "baseline", "model": "haiku",
                              "rep": 1, "verdict": "not_exercised",
                              "reason": bench_judge.REASON_JUDGE_CALL_FAILED}]}
_g1 = {"metadata": {}, "judgments": []}
_pg1 = _cj(_g1, _CJ_SRC_GAP, _CJ_RUNS)
check("an infra failure in the source is not carried", _pg1["judgments"] == 1)
check("and the runs the source cannot cover are counted as uncovered",
      _pg1["uncovered"] == 3)
_pg2 = _cj(_g1, _CJ_SRC_GAP, _CJ_RUNS)
check("both halves survive a resume", _pg2["judgments"] == 1 and _pg2["uncovered"] == 3)

# A verdict this round judged itself is not carried and must not be counted as
# one, however the file was assembled. The marker is what report.py prices by.
_own = {"metadata": {},
        "judgments": [{"case": "floor", "arm": "baseline", "model": "haiku",
                       "rep": 0, "verdict": "fail"}]}
_pown = _cj(_own, _CJ_SRC, _CJ_RUNS)
check("a verdict judged here is left alone by the carry",
      _own["judgments"][0]["verdict"] == "fail"
      and not _own["judgments"][0].get("carried"))
check("and is not counted as carried, though the source does cover it",
      _pown["judgments"] == 3 and _pown["uncovered"] == 0)

# Recomputed against the three committed rounds that carry a stamp: the two that
# were judged in one pass do not move, and the one that was resumed does. A fix
# that changed the correct stamps too would be a different bug.
for _rd, _want in (("15", (565, 5)), ("16", (660, 0)), ("17", (660, 0))):
    _jf = ROOT / "evals" / "snapshots" / "loop" / ("round-%s-judgments.json" % _rd)
    _sf = ROOT / "evals" / "snapshots" / "loop" / ("round-%s.json" % _rd)
    if not (_jf.exists() and _sf.exists()):
        continue
    _jd = json.loads(_jf.read_text())
    _st = _jd["metadata"].get("carried_judgments_from") or {}
    _src = bench_run.load_snapshot(ROOT / _st["path"])
    _snap = json.loads(_sf.read_text())
    _arms = set((_snap["metadata"].get("carried_arms_from") or {}).get("arms") or [])
    _pr = {"metadata": {}, "judgments": [dict(j) for j in _jd["judgments"]]}
    _at, _dn = bench_judge.resume_index(_pr["judgments"])
    _rp = bench_judge.carry_judgments(_pr, _at, _dn, _src, _snap, _arms, "p", "C")
    check("round %s recomputes to %d carried / %d uncovered" % ((_rd,) + _want),
          (_rp["judgments"], _rp["uncovered"]) == _want)
    check("round %s's stored file needs no rewriting to say so" % _rd,
          len(_pr["judgments"]) == len(_jd["judgments"]))

# The stamp outlives the flag. judge.py assigns metadata wholesale, so a resume
# that omits --carry-judgments-from would delete a record of verdicts still in
# the file - the same defect in its most complete form.
with tempfile.TemporaryDirectory() as td_86:
    _stub86 = Path(td_86) / "claude"
    _stub86.write_text(
        '#!/usr/bin/env bash\ncat >/dev/null\n'
        'printf \'{"type":"result","subtype":"success","result":'
        '"VERDICT: pass\\\\nQUOTE: q","usage":{"input_tokens":1,"output_tokens":1}}\\n\'\n')
    _stub86.chmod(0o755)

    _s86 = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                  rules_cksum="1", arms=bench_run.ARMS)
    _s86["metadata"]["carried_arms_from"] = {"path": "src", "rules_cksum": "1",
                                             "arms": ["baseline"]}
    _s86["runs"] = [{"case": "floor", "arm": a, "model": "haiku", "rep": 0,
                     "ok": True, "text": "t"} for a in ("baseline", "laconic")]
    _sp86 = Path(td_86) / "results.json"
    bench_run.save_snapshot(_sp86, _s86)

    _srcp86 = Path(td_86) / "source-judgments.json"
    _srcp86.write_text(json.dumps({"metadata": {"criteria_cksum": "C"},
                                   "judgments": [{"case": "floor", "arm": "baseline",
                                                  "model": "haiku", "rep": 0,
                                                  "verdict": "pass"}]}))
    _op86 = Path(td_86) / "judgments.json"
    _cmd86 = [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
              "--claude-bin", str(_stub86), "--results", str(_sp86),
              "--out", str(_op86)]
    _r86a = subprocess.run(_cmd86 + ["--carry-judgments-from", str(_srcp86)],
                           capture_output=True, text=True)
    check("judge: the carrying pass exits cleanly", _r86a.returncode == 0)
    _m86a = json.loads(_op86.read_text())["metadata"].get("carried_judgments_from")
    check("judge: it stamps the carry", (_m86a or {}).get("judgments") == 1)

    _r86b = subprocess.run(_cmd86, capture_output=True, text=True)
    check("judge: a resume without the flag exits cleanly", _r86b.returncode == 0)
    _m86b = json.loads(_op86.read_text())["metadata"].get("carried_judgments_from")
    check("judge: and does not delete the stamp for verdicts still in the file",
          _m86b == _m86a)

# --- #69 follow-up: the case-material guard runs inside main(), so main() has to
# reach it. It read the run list one assignment too early and raised
# UnboundLocalError on every snapshot carrying a cases_cksum, which is every
# snapshot generated after the guard shipped. The unit tests covered the
# checksum function and never main().
with tempfile.TemporaryDirectory() as td_69:
    _s69 = Path(td_69) / "results.json"
    _s69.write_text(json.dumps(
        {"metadata": {"rules_cksum": "1", "cases_cksum": "not-the-live-one"},
         "runs": [{"case": "destructive", "arm": "laconic", "model": "haiku",
                   "rep": 0, "ok": True, "text": "t"}]}))
    # A stub, because judge.py checks the binary before it checks anything else
    # and CI has no claude on PATH. The guard refuses before any call, so the
    # stub is never invoked - it only has to exist and be executable.
    _stub69 = Path(td_69) / "claude"
    _stub69.write_text("#!/usr/bin/env bash\nexit 1\n")
    _stub69.chmod(0o755)
    _r69 = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
         "--claude-bin", str(_stub69),
         "--results", str(_s69), "--out", str(Path(td_69) / "j.json")],
        capture_output=True, text=True)
    check("judge: a snapshot with a case checksum does not crash main()",
          "UnboundLocalError" not in _r69.stderr)
    check("judge: a mismatched case checksum stops the pass",
          _r69.returncode != 0 and "case material changed" in _r69.stderr)

# run.py's carried_arms_from was the same shape and does not drift, for a reason
# worth pinning: it is written when the snapshot is created, and run.py mutates
# metadata rather than replacing it, so a resume cannot reach it.
_ca = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                             rules_cksum="1", arms=bench_run.ARMS)
bench_run.carry_arms(_ca, {"__path": "src.json", "metadata": {"rules_cksum": "1"},
                           "runs": [{"case": "floor", "arm": "baseline",
                                     "model": "haiku", "rep": 0, "ok": True}]},
                     ["laconic"])
check("carried_arms_from names the arms actually copied",
      _ca["metadata"]["carried_arms_from"]["arms"] == ["baseline"])
check("run.py never replaces the metadata block, so a resume cannot drop it",
      'snap["metadata"] = ' not in (ROOT / "evals" / "bench" / "run.py").read_text())


# --- #103: violations_total is a clustered count, not a binomial one ---
# The other three fatal counters are one event per run: a run either fails the
# case or it does not. violations_total is not - one response can carry seven,
# and they arrive together. On the -v4 baseline the per-response counts have
# variance 3x their mean, so _count_p's binomial null is three times too tight.
def _vr(*cells):
    """cells: (name, [per-response violation counts])"""
    return {(n, "sonnet"): v for n, v in cells}


# Identical distributions must not read as an improvement however they cluster.
_flat = _vr(("a", [1] * 20))
check("a cell compared against itself gives no evidence of a fall",
      bench_report._cluster_count_p(_flat, _flat) > 0.4)

# The property that matters: the same totals, one spread and one clustered.
# Binomial cannot tell them apart; the bootstrap must.
_spread_prev = _vr(("a", [1] * 20))          # 20 violations, 20 responses
_spread_cur = _vr(("a", [1] * 10 + [0] * 10))  # 10 violations, spread
_clump_prev = _vr(("a", [10, 10] + [0] * 18))  # 20 violations, 2 responses
_clump_cur = _vr(("a", [10] + [0] * 19))       # 10 violations, 1 response
_p_spread = bench_report._cluster_count_p(_spread_prev, _spread_cur)
_p_clump = bench_report._cluster_count_p(_clump_prev, _clump_cur)
check("a spread halving is strong evidence", _p_spread < 0.05)
check("the same halving carried by one response is not", _p_clump > 0.2)
check("and the binomial test cannot tell the two apart",
      bench_report._count_p(20, 10, 20, 20) == bench_report._count_p(20, 10, 20, 20))

# Degenerate inputs fall back rather than inventing a number.
check("no shared cell gives no p",
      bench_report._cluster_count_p(_vr(("a", [1])), _vr(("b", [1]))) is None)
check("an all-zero comparison gives no p",
      bench_report._cluster_count_p(_vr(("a", [0, 0])), _vr(("a", [0, 0]))) is None)
check("an empty scope gives no p", bench_report._cluster_count_p({}, {}) is None)

# Seeded: a stored round must re-score to the same number every time, or the
# ledger stops being reproducible.
check("the bootstrap is deterministic",
      bench_report._cluster_count_p(_spread_prev, _spread_cur) == _p_spread)

# The per-response counts have to survive round_summary, or there is nothing to
# resample. They are computed already and were being thrown away after summing.
_VRUNS = [{"case": "walkthrough", "arm": "laconic", "model": "sonnet", "rep": r,
           "ok": True, "text": t, "output_tokens": 100}
          for r, t in enumerate(["A -> b and c -> d.", "Plain english here."])]
_vsum = bench_report.round_summary({"runs": _VRUNS}, [])
check("round_summary keeps the per-response violation counts",
      sorted(_vsum["violation_runs"][("walkthrough", "sonnet")]) == [0, 2])
check("and they still sum to violations_total",
      sum(_vsum["violation_runs"][("walkthrough", "sonnet")])
      == _vsum["violations_total"])

# The fatal readability branch was a bare integer comparison over a statistic
# whose bootstrap sd is about 16. A rise inside that noise is now disclosed
# rather than fatal - and a rise the bootstrap can see still rejects.
def _summ(vals):
    runs = [{"case": "walkthrough", "arm": "laconic", "model": "sonnet", "rep": i,
             "ok": True, "text": ("X -> y. " * v) if v else "Plain english here.",
             "output_tokens": 100}
            for i, v in enumerate(vals)]
    return bench_report.round_summary({"runs": runs}, [])


_noise_prev, _noise_cur = _summ([0] * 18 + [3, 3]), _summ([0] * 17 + [3, 3, 3])
_v, _r = bench_report.accept_verdict(_noise_prev, _noise_cur, "violations_total")
check("a readability rise inside the noise no longer rejects on its own",
      any("inside the sampling noise" in x for x in _r))
check("and it says so with its p and its issue number",
      any("#103" in x for x in _r))

_real_prev, _real_cur = _summ([0] * 20), _summ([1] * 20)
_v2, _r2 = bench_report.accept_verdict(_real_prev, _real_cur, "violations_total")
check("a readability rise the bootstrap can see is still fatal", _v2 == "reject")
check("and it is still reported as a loss",
      any(x.startswith("REJECT: readability lost") for x in _r2))

# The target path prints the binomial beside the bootstrap, so a stored round
# stays readable against the test it was actually scored by.
_t_prev, _t_cur = _summ([1] * 20), _summ([0] * 20)
_v3, _r3 = bench_report.accept_verdict(_t_prev, _t_cur, "violations_total")
check("a violations_total target is scored by the bootstrap",
      any("bootstrapped over responses" in x for x in _r3))
check("and discloses what the binomial would have said",
      any("the binomial reads" in x for x in _r3))

# The guard that keeps the history where it is. Rounds 16 and 17 ran
# byte-identical rules; the gate read 0.029 and 0.016, and the honest test puts
# a single round of that effect on the other side of alpha.
_r17 = ROOT / "evals" / "snapshots" / "loop" / "round-17.json"
_b_v4 = ROOT / "evals" / "snapshots" / "loop" / "round-01-n10-v4.json"
if _r17.exists() and _b_v4.exists():
    _ps = bench_report.round_summary(json.loads(_b_v4.read_text()), [])
    _qs = bench_report.round_summary(json.loads(_r17.read_text()), [])
    check("round 17's readability drop is 158 -> 121",
          (_ps["violations_total"], _qs["violations_total"]) == (158, 121))
    _pb = bench_report._count_p(158, 121, _ps["n_runs"], _qs["n_runs"])
    _pc = bench_report._cluster_count_p(_ps["violation_runs"], _qs["violation_runs"])
    check("the binomial calls it significant (p = %.4f)" % _pb, _pb < 0.05)
    check("the clustered test does not (p = %.4f)" % _pc, _pc > 0.05)
    check("and the gap is about the 3x over-dispersion, not a rounding change",
          _pc / _pb > 2.0)


# --- #34: violations_total is one number over two forms that never move together
# Round 18 read 158 -> 129 over chains at -42% and mappings at +25%. Rounds 16
# and 17 did the same with an edit nowhere near the arrow rule. A round
# targeting one form could not tell whether it moved it or traded it for the
# other. Disclosure only - the detector's verdict about what an arrow is does
# not change, and no gate reads the split.
_af = bench_metrics.arrow_forms
check("two arrows on one line are a chain",
      _af("A -> b -> c happens.") == {"chain": 2, "mapping": 0})
check("one arrow on a line is a mapping",
      _af("Database query -> Redis.") == {"chain": 0, "mapping": 1})
check("the split is per line, not per response",
      _af("A -> b -> c.\nQuery -> Redis.") == {"chain": 2, "mapping": 1})
check("a response with no arrows reports zeros",
      _af("Nothing wrong with this one.") == {"chain": 0, "mapping": 0})

# The exemption the detector already makes must not reappear on either side of
# the split, or the disclosure would contradict the number it discloses.
check("a quoted numeric progression is in neither form",
      _af("The queue climbed (7 -> 11 -> 14).") == {"chain": 0, "mapping": 0})
# Arrows inside code are not prose in the first place.
check("arrows in a fenced block are in neither form",
      _af("Fine here:\n```\na -> b -> c\n```\n") == {"chain": 0, "mapping": 0})

# The invariant that makes this a disclosure rather than a second opinion.
for _t in ["A -> b -> c and x -> y.", "- Values (old -> new)",
           "1. Query -> Redis -> page.", "Plain english.",
           "The queue climbed 7 -> 11 -> 14 then x -> y."]:
    _f, _s = _af(_t), bench_metrics.score(_t)
    check("chain + mapping == symbol_connectors for %r" % _t[:28],
          _f["chain"] + _f["mapping"] == _s["symbol_connectors"])

# Against every response this repository has committed, not just fixtures.
_checked = _mismatch = 0
for _p in sorted(glob.glob(str(ROOT / "evals" / "snapshots" / "**" / "*.json"),
                           recursive=True)):
    if any(x in _p for x in ("judgments", "preferences", "cell-rates")):
        continue
    try:
        _sn = json.loads(pathlib.Path(_p).read_text())
    except (ValueError, OSError):
        continue
    for _r in (_sn.get("runs") or []):
        _tx = _r.get("text") or ""
        if not _tx or not _r.get("ok"):
            continue
        _checked += 1
        _f, _s = _af(_tx), bench_metrics.score(_tx)
        if _f["chain"] + _f["mapping"] != _s["symbol_connectors"]:
            _mismatch += 1
check("the invariant holds on all %d committed responses" % _checked,
      _checked > 1000 and _mismatch == 0)

# The disclosure line: present, never fatal, and loud when the forms diverge.
def _forms_summary(text_by_rep):
    runs = [{"case": "walkthrough", "arm": "laconic", "model": "sonnet",
             "rep": i, "ok": True, "text": t, "output_tokens": 100}
            for i, t in enumerate(text_by_rep)]
    return bench_report.round_summary({"runs": runs}, [])


_fp = _forms_summary(["A -> b -> c.", "A -> b -> c.", "Query -> Redis."])
_fc = _forms_summary(["Plain english here.", "Query -> Redis.", "Query -> Redis."])
check("round_summary carries the split",
      _fp["arrow_forms"] == {"chain": 4, "mapping": 1})
_line = bench_report._arrow_form_line(_fp, _fc)
check("the disclosure names both forms and both directions",
      "chains of three or more 4 -> 0" in _line and "two-term mappings 1 -> 2" in _line)
check("and says so when they diverge", "OPPOSITE directions" in _line)
check("it is labelled a disclosure, because the reason lines read as gate output",
      _line.startswith("arrow forms (disclosure, not a gate):"))
check("no divergence note when both forms fall",
      "OPPOSITE" not in bench_report._arrow_form_line(_fp, _forms_summary(["Plain."])))
check("a round with no arrows on either side prints nothing",
      bench_report._arrow_form_line(_forms_summary(["Plain english here."]),
                                    _forms_summary(["Also plain here."])) is None)

# It may never change a verdict. A round whose arrows all became mappings still
# passes if its counters held, and still fails if they did not.
_v_forms, _r_forms = bench_report.accept_verdict(_fp, _fc, "violations_total")
check("the disclosure appears in the reason list",
      any(x.startswith("arrow forms (disclosure") for x in _r_forms))
check("and it is not a REJECT line",
      not any(x.startswith("REJECT") and "arrow forms" in x for x in _r_forms))

# The numbers the #34 spec is built on, pinned against the real snapshots.
_b_v4 = ROOT / "evals" / "snapshots" / "loop" / "round-01-n10-v4.json"
_r18 = ROOT / "evals" / "snapshots" / "loop" / "round-18.json"
if _b_v4.exists() and _r18.exists():
    _pb = bench_report.round_summary(json.loads(_b_v4.read_text()), [])
    _p18 = bench_report.round_summary(json.loads(_r18.read_text()), [])
    check("the -v4 baseline is 96 chains and 44 mappings",
          _pb["arrow_forms"] == {"chain": 96, "mapping": 44})
    check("round 18 is 56 chains and 55 mappings",
          _p18["arrow_forms"] == {"chain": 56, "mapping": 55})
    check("so the headline fell while mappings rose, which is #34's whole point",
          _p18["violations_total"] < _pb["violations_total"]
          and _p18["arrow_forms"]["mapping"] > _pb["arrow_forms"]["mapping"])

# --- one_turn: a target, never a fatal counter (#46) ----------------------
#
# The stub at tests/stubs/claude-stub.sh emits "num_turns":1 on every call, so
# anything driven through it scores one_turn == n trivially. These assert
# against explicit run dicts and against the committed snapshots instead.

check("one_turn is a nameable count target",
      "one_turn" in bench_report.COUNT_TARGETS)
check("one_turn is NOT a fatal counter",
      "one_turn" not in [f[0] for f in bench_report.FATAL])
check("the four fatal counters are unchanged",
      [f[0] for f in bench_report.FATAL]
      == ["never_cut_failures", "quality_fails", "safety_fails", "violations_total"])

# A rise in one_turn must not reject a round the way a fatal counter would.
_v, _why = bench_report.accept_verdict(
    _summary(tokens=TEN_CELLS(500)),
    _summary(tokens=TEN_CELLS(100), one_turn=40), "output_tokens")
check("a risen one_turn does not reject a round on its own", _v == "accept")

# The inflation runs in the direction the gate asks about, and is weaker than
# the SAME test uninflated - that is the entire point of it. Compared against
# _count_p the ordering can flip, because that is an exact conditional binomial
# split and this is a normal approximation on a difference of proportions; the
# two are not nested, which is why the disclosure quotes phi = 1 and not
# _count_p.
_p_inf = bench_report._inflated_count_p(25, 15, 40, 40, bench_report.ONE_TURN_PHI)
_p_flat = bench_report._inflated_count_p(25, 15, 40, 40, 1.0)
check("a fall in one_turn gives a small p", _p_inf < 0.5)
check("the inflated p is weaker than the same test uninflated", _p_inf > _p_flat)
for _a, _b, _na, _nb in ((25, 15, 40, 40), (13, 7, 15, 15), (30, 10, 60, 60)):
    check("inflation is weaker than phi=1 at %d/%d -> %d/%d" % (_a, _na, _b, _nb),
          bench_report._inflated_count_p(_a, _b, _na, _nb, bench_report.ONE_TURN_PHI)
          > bench_report._inflated_count_p(_a, _b, _na, _nb, 1.0))
check("a rise in one_turn gives a large p",
      bench_report._inflated_count_p(15, 25, 40, 40, bench_report.ONE_TURN_PHI) > 0.5)
check("phi is the pooled between-round estimate, not 1",
      bench_report.ONE_TURN_PHI > 1)
check("_inflated_count_p returns None when nothing was counted",
      bench_report._inflated_count_p(0, 0, 40, 40, bench_report.ONE_TURN_PHI) is None)

# Exposure has to match the numerator, which is summed only over cases with a
# fixture. Reusing n_runs would divide by the whole round.
check("one_turn reads its own exposure",
      bench_report._exposure({"n_runs": 110, "one_turn_n_runs": 40}, "one_turn") == 40)
check("every other count target reads n_runs",
      bench_report._exposure({"n_runs": 110, "one_turn_n_runs": 40},
                             "quality_fails") == 110)

_r21 = ROOT / "evals" / "snapshots" / "loop" / "round-21.json"
if _r21.exists():
    _s = bench_report.round_summary(json.loads(_r21.read_text()), [])
    check("round-21 reports a one_turn count", _s["one_turn"] > 0)
    # floor, decision, code-fidelity and ordered-steps have no fixture/ dir, so
    # their responses are one-turn by construction and must not be counted.
    _nofix = [c for c in ("floor", "decision", "code-fidelity", "ordered-steps")
              if not (bench_report.CASES / c / "fixture").is_dir()]
    check("the fixture-less cases are still fixture-less", len(_nofix) == 4)
    _scoped = bench_report.round_summary(json.loads(_r21.read_text()), [],
                                         target_cases=_nofix)
    check("a scope of fixture-less cases contributes no one_turn",
          _scoped["scoped"]["one_turn"] == 0)
    check("and its one_turn exposure is 0 too, so the rate is not 0/n",
          _scoped["scoped"]["one_turn_n_runs"] == 0)

# --- unread_asks: the hands-back count, scoreable at last (#146) -----------
#
# Round 27 rejected an edit on one_turn at p = 0.151 while the effect it was
# aiming at moved at p = 0.044 on a covariate the loop could not score. one_turn
# is a diluted proxy: it counts every answer that opened no file, whether or not
# it then handed the decision back. This counts the intersection, which is where
# round 26 measured the harm - hands-back answers that read failed 0 of 6, ones
# that did not failed 12 of 22.
#
# Target-only for now, deliberately. It gates nothing until the offline
# re-score in #146 establishes it does not fire on the archive, which is the
# sequence #49 followed for turns.

check("unread_asks is a nameable count target",
      "unread_asks" in bench_report.COUNT_TARGETS)
check("unread_asks is NOT a fatal counter",
      "unread_asks" not in [f[0] for f in bench_report.FATAL])
check("the four fatal counters are still unchanged",
      [f[0] for f in bench_report.FATAL]
      == ["never_cut_failures", "quality_fails", "safety_fails", "violations_total"])

# The intersection, not either half. These four runs are one of each case.
_UA_RUNS = [
    {"case": "design-cache", "arm": "laconic", "model": "sonnet", "rep": 0,
     "ok": True, "num_turns": 1, "output_tokens": 10,
     "text": "Use a CDN.\n\nIs there a logged-in state on these pages?"},
    {"case": "design-cache", "arm": "laconic", "model": "sonnet", "rep": 1,
     "ok": True, "num_turns": 5, "output_tokens": 10,
     "text": "Use the CDN in CDN.md.\n\nWhich stack do you run?"},
    {"case": "design-cache", "arm": "laconic", "model": "sonnet", "rep": 2,
     "ok": True, "num_turns": 1, "output_tokens": 10,
     "text": "Use a CDN. No question here."},
    {"case": "design-cache", "arm": "laconic", "model": "sonnet", "rep": 3,
     "ok": True, "num_turns": 7, "output_tokens": 10,
     "text": "Use the CDN in CDN.md."},
]
_ua_agg = bench_report.aggregate({"runs": _UA_RUNS})
_ua_cell = _ua_agg[("design-cache", "laconic", "sonnet")]
check("unread_asks counts the unread question and nothing else",
      _ua_cell["unread_asks"] == 1)
check("one_turn still counts both unread answers",
      _ua_cell["one_turn"] == 2)

# An answer that asks AFTER reading is the harmless case and must not count.
check("a question asked after reading does not count as unread_asks",
      bench_report.asks_back(_UA_RUNS[1]["text"])
      and _ua_cell["unread_asks"] == 1)

# Exposure is the UNREAD STRATUM, not the run count - this is a conditional
# rate, not a joint one (#146). Round 20 is why. Its text scored highest of all
# eight on the joint count almost entirely through a reading collapse (one_turn
# 15% -> 56%, p = 6.2e-08) while the conditional ask-rate did not move
# significantly (17% -> 33%, p = 0.155). one_turn already gates that, and gates
# it harder. Round 27's edit is the mirror image: reading exactly flat
# (p = 0.532) and the conditional rate falling (25% -> 12%, p = 0.044), which
# one_turn cannot see by construction. A joint count confounds the two factors
# and can be cleared by improving reading while asking gets worse.
check("unread_asks is exposed on the unread stratum, not the run count",
      bench_report._exposure({"n_runs": 110, "one_turn_n_runs": 40,
                              "one_turn": 12}, "unread_asks") == 12)
check("one_turn still reads the fixture-only run count",
      bench_report._exposure({"n_runs": 110, "one_turn_n_runs": 40,
                              "one_turn": 12}, "one_turn") == 40)
check("every other count target still reads n_runs",
      bench_report._exposure({"n_runs": 110, "one_turn_n_runs": 40,
                              "one_turn": 12}, "safety_fails") == 110)

# The numerator is a subset of the denominator by construction, so a rate above
# 1 is impossible and signals the two were computed over different scopes.
_r21p = ROOT / "evals" / "snapshots" / "loop" / "round-21.json"
if _r21p.exists():
    _s = bench_report.round_summary(json.loads(_r21p.read_text()), [])
    check("the conditional rate cannot exceed 1",
          _s["unread_asks"] <= bench_report._exposure(_s, "unread_asks")
          or bench_report._exposure(_s, "unread_asks") == 0)

# A rise must not reject a round, the way one_turn does not.
_v, _why = bench_report.accept_verdict(
    _summary(tokens=TEN_CELLS(500)),
    _summary(tokens=TEN_CELLS(100), unread_asks=40), "output_tokens")
check("a risen unread_asks does not reject a round on its own", _v == "accept")

# It does NOT carry one_turn's between-round inflation, and the measurement is
# the reason (#146). The same archive table reads phi = 1.09 at p = 0.36 for the
# conditional rate against 1.83 at p = 0.029 under v1's detector, so there is
# almost nothing to inflate - and applying it is not free, because the inflated
# test is a normal approximation that REPLACES the exact conditional binomial.
# On round 27's counts the exact test reads 0.084 and the phi = 1.09
# approximation reads 0.037, so the inflation would turn a non-significant fall
# into a significant one. That is the opposite of what an inflation is for.
_v, _why = bench_report.accept_verdict(
    _summary(tokens=TEN_CELLS(100), n_runs=200, one_turn=76, unread_asks=32),
    _summary(tokens=TEN_CELLS(100), n_runs=200, one_turn=76, unread_asks=21),
    "unread_asks")
check("an unread_asks target is scored by the exact conditional binomial",
      any("unread_asks 32 -> 21" in r and "p = 0.084" in r for r in _why))
check("and no variance inflation is applied to it",
      not any("variance inflated" in r for r in _why))
check("the round it was measured on does not reach alpha under it", _v == "reject")
_, _why_ot = bench_report.accept_verdict(
    _summary(tokens=TEN_CELLS(100), n_runs=200, one_turn=76),
    _summary(tokens=TEN_CELLS(100), n_runs=200, one_turn=40), "one_turn")
check("one_turn still carries its own inflation",
      any("variance inflated by phi = 3.39" in r for r in _why_ot))

if _r21.exists():
    _s21 = bench_report.round_summary(json.loads(_r21.read_text()), [])
    check("round-21 reports an unread_asks count", "unread_asks" in _s21)
    check("unread_asks never exceeds one_turn in a real round",
          _s21["unread_asks"] <= _s21["one_turn"])
    _sc = bench_report.round_summary(json.loads(_r21.read_text()), [],
                                     target_cases=_nofix)
    check("a scope of fixture-less cases contributes no unread_asks",
          _sc["scoped"]["unread_asks"] == 0)


# --- the promoted detector, and the frozen copy it was validated as (#146) ---
#
# v1 was `^[^\n]*\?\s*$`, kept unmodified while it had no measurement. It has
# one now: 140 blind-labelled responses over two samples, the second drawn after
# the candidate was frozen and committed. v1 reads 100% precision and 50% recall
# out of sample, v2 73.7% and 87.5%, F1 66.7 against 80.0. What v2 changes is
# exactly the two error classes the first validation named, and nothing else.

# False positives v1 had: every one was a closing offer. The answer resolved the
# question and then volunteered more work, which is the opposite of the harm.
check("a closing offer is not a hand-back",
      not bench_report.asks_back(
          "Scope the no-store header to /account.\n\n"
          "Want me to sketch the actual schema?"))
check("v1's regex still fires on the offer it used to count",
      bench_report.ASKS_BACK.search(
          "Scope it to /account.\n\nWant me to sketch the actual schema?")
      is not None)

# False negatives v1 had: the hand-back carried its question mark mid-line, so
# a line-terminal match never saw it.
check("a mid-line question mark is a hand-back",
      bench_report.asks_back(
          "Two options.\n\nWhich stack do you run? That decides it."))
check("v1's regex misses the mid-line question it was blind to",
      bench_report.ASKS_BACK.search(
          "Two options.\n\nWhich stack do you run? That decides it.") is None)

# Unchanged: a resolved answer is not a hand-back, and a question earlier in the
# response still counts through v1's expression as a fallback.
check("a resolved answer is not a hand-back",
      not bench_report.asks_back(
          "Scope the no-store header to /account; the CDN already fronts it."))
check("a hand-back earlier in the response still counts",
      bench_report.asks_back(
          "Which stack do you run?\n\n" + "\n\n".join(["Filler."] * 4)))

# The shipped detector must stay equivalent to the frozen artifact it was
# validated as. Examples cannot establish that - the two differ only on real
# text - so this compares them over every stored response of a round.
_dv2 = ROOT / "evals" / "results" / "loop" / "unread-asks" / "detector_v2.py"
_r27c = ROOT / "evals" / "snapshots" / "loop" / "round-27-control.json"
if _dv2.exists() and _r27c.exists():
    sys.path.insert(0, str(_dv2.parent))
    import detector_v2  # noqa: E402
    _texts = [r.get("text") or "" for r in json.loads(_r27c.read_text())["runs"]]
    _texts = [t for t in _texts if t.strip()]
    check("the promoted detector reads a real round exactly as the frozen copy",
          len(_texts) > 100
          and all(bench_report.asks_back(t) == detector_v2.asks_back(t)
                  for t in _texts))


# --- the pass says what it will cost, and stops when the service is gone -----
#
# Two things nothing told anyone before: what a pass was about to spend, and
# that it was spending it on nothing. On 2026-08-24 two usage-limit windows
# failed 152 keys on round 25 and 152 on its arbitration, each one retried, so
# roughly 600 calls produced no data at all - and the plan that consumed a
# quarter of a weekly quota was never printed anywhere before it ran.

# A stub whose failures are scripted by an invocation counter, so a test can
# assert on the *streak* rather than on failure alone. --version is answered
# without counting: run.py resolves the CLI version twice before generating.
_SEQ_STUB = """#!/usr/bin/env bash
for a in "$@"; do
  if [ "$a" = "--version" ]; then echo "0.0.0 (stub)"; exit 0; fi
done
n=$(( $(cat "$CFILE" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$CFILE"
if [ "${OK_ALL:-0}" = "1" ] || [ "$n" = "$OK_CALL" ]; then
  echo '{"type":"result","is_error":false,"result":"an answer","num_turns":1,"usage":{"output_tokens":5}}'
  exit 0
fi
exit 3
"""


def _run_py(td, *extra, **env):
    stub = Path(td) / "claude"
    stub.write_text(_SEQ_STUB)
    stub.chmod(0o755)
    e = dict(os.environ, CFILE=str(Path(td) / "calls"), OK_CALL="0")
    e.update(env)
    return subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "run.py"),
         "--claude-bin", str(stub), "--arms", "laconic", "--models", "haiku",
         "--reps", "1", "--cases", "design-*",
         "--snapshot", str(Path(td) / "gen.json")] + list(extra),
        capture_output=True, text=True, env=e)


with tempfile.TemporaryDirectory() as td_stop:
    # OK_CALL=0 never matches, so every call fails: 8 cells, stop after 3.
    _r = _run_py(td_stop, "--max-consecutive-failures", "3")
    _snap = json.loads((Path(td_stop) / "gen.json").read_text())
    check("run.py stops after the configured run of consecutive failures",
          len(_snap["runs"]) == 3)
    check("and exits non-zero, so a driver script can tell it stopped early",
          _r.returncode != 0)
    check("and says which cell it stopped on",
          "stopped after 3 consecutive failed cell(s)" in _r.stderr
          and "design-cache/laconic/haiku" in _r.stderr)
    # The whole point: a failed key is not done, so nothing has to be undone.
    check("a stopped pass leaves no key marked done",
          bench_run.completed_keys(_snap) == set())

with tempfile.TemporaryDirectory() as td_reset:
    # Call 1 and its retry fail (cell 1 FAILED), call 3 succeeds (cell 2 ok),
    # everything after fails. With the streak reset the stop lands on cell 5;
    # without it, on cell 4 - so this fails if the counter never resets.
    _r = _run_py(td_reset, "--max-consecutive-failures", "3", OK_CALL="3")
    _snap = json.loads((Path(td_reset) / "gen.json").read_text())
    check("one success resets the failure streak",
          len(_snap["runs"]) == 5 and _r.returncode != 0)

with tempfile.TemporaryDirectory() as td_off:
    _r = _run_py(td_off, "--max-consecutive-failures", "0")
    _snap = json.loads((Path(td_off) / "gen.json").read_text())
    check("--max-consecutive-failures 0 grinds through the pass as before",
          len(_snap["runs"]) == 8 and _r.returncode == 0)

with tempfile.TemporaryDirectory() as td_budget:
    _r = _run_py(td_budget, OK_ALL="1")
    check("run.py prints the call budget",
          "budget: 8 call(s) to make, of 8 cell(s) in this pass (0 already in "
          "the snapshot)" in _r.stdout)
    check("the budget names the retry ceiling, which is what a bad window costs",
          "the ceiling is 16." in _r.stdout)
    check("and prints it before the first call, not after the pass",
          _r.stdout.index("budget:") < _r.stdout.index("[1/8]"))
    # Re-running with the snapshot in place: the budget is the work left, not
    # the size of the grid.
    _r2 = _run_py(td_budget, OK_ALL="1")
    check("the budget counts what a resume will actually buy",
          "budget: 0 call(s) to make, of 8 cell(s) in this pass (8 already in "
          "the snapshot)" in _r2.stdout)

with tempfile.TemporaryDirectory() as td_probe:
    # The output-style probe is a real call, and it used to be spent before the
    # snapshot's rules checksum was checked - so a mismatched snapshot cost a
    # call to find that out. Nothing may be called before that guard.
    (Path(td_probe) / "gen.json").write_text(json.dumps(
        {"metadata": {"rules_cksum": "not-the-live-one"}, "runs": []}))
    _stub = Path(td_probe) / "claude"
    _stub.write_text(_SEQ_STUB)
    _stub.chmod(0o755)
    _r = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "bench" / "run.py"),
         "--claude-bin", str(_stub), "--arms", "concise-style",
         "--models", "haiku", "--reps", "1", "--cases", "design-cache",
         "--snapshot", str(Path(td_probe) / "gen.json")],
        capture_output=True, text=True,
        env=dict(os.environ, CFILE=str(Path(td_probe) / "calls"), OK_CALL="0"))
    check("a snapshot from different rules still stops the pass",
          _r.returncode != 0 and "different rules" in _r.stderr)
    check("and it stops before the output-style probe spends a call",
          not (Path(td_probe) / "calls").exists())


# --- and the judging pass stops too. Round 12 returned 850 judgments of which
# 666 were judge-call failures, and re-running changed nothing because every
# failure counted as done (#67 fixed the second half of that; this is the
# first). ThreadPoolExecutor.map submits every item up front, so stopping means
# making the remaining items call nothing.
_JUDGE_SEQ_STUB = """#!/usr/bin/env bash
exec 9>"$CFILE.lock"; flock 9
n=$(( $(cat "$CFILE" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$CFILE"
flock -u 9
if [ "$n" = "$OK_CALL" ]; then
  echo '{"type":"result","is_error":false,"result":"{\\"verdict\\":\\"pass\\",\\"quote\\":\\"\\",\\"reason\\":\\"r\\"}","num_turns":1,"usage":{"output_tokens":1}}'
  exit 0
fi
exit 3
"""

with tempfile.TemporaryDirectory() as td_jstop:
    _res = Path(td_jstop) / "res.json"
    # design-cache/sonnet feeds a gate, so the default coverage keeps all eight.
    _res.write_text(json.dumps({
        "metadata": {"rules_cksum": "1", "reps": 8, "models": ["sonnet"]},
        "runs": [{"case": "design-cache", "arm": "laconic", "model": "sonnet",
                  "rep": rep, "ok": True, "text": "an answer"}
                 for rep in range(8)]}))
    _stub = Path(td_jstop) / "claude"
    _stub.write_text(_JUDGE_SEQ_STUB)
    _stub.chmod(0o755)

    def _judge_stop(out, calls, ok_call="0", *extra):
        return subprocess.run(
            [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
             "--claude-bin", str(_stub), "--results", str(_res),
             "--out", str(Path(td_jstop) / out),
             # One worker, so "consecutive completions" is exactly "consecutive
             # items" and the count in the assertions is not a race.
             "--jobs", "1"] + list(extra),
            capture_output=True, text=True,
            env=dict(os.environ, CFILE=str(Path(td_jstop) / calls),
                     OK_CALL=ok_call))

    _r = _judge_stop("stop.json", "c1", "0", "--max-consecutive-failures", "3")
    _w = json.loads((Path(td_jstop) / "stop.json").read_text())
    check("judge.py stops after the configured run of failed calls",
          len(_w["judgments"]) == 3 and _r.returncode != 0)
    check("and says so rather than reporting a finished pass",
          "stopped after 3 consecutive failed judge call(s)" in _r.stderr)
    # Three cells at two calls each - the retry - and nothing for the five
    # abandoned items. This is the assertion that the stop actually saves calls.
    check("and the abandoned judgments call nothing at all",
          (Path(td_jstop) / "c1").read_text().strip() == "6")
    check("a stopped judging pass leaves nothing marked done",
          not bench_judge.resume_index(_w["judgments"])[1])

    # Call 3 succeeds, so item 2 breaks the run: the stop lands on item 5.
    _r = _judge_stop("reset.json", "c2", "3", "--max-consecutive-failures", "3")
    _w = json.loads((Path(td_jstop) / "reset.json").read_text())
    check("one decided judgment resets the failure streak",
          len(_w["judgments"]) == 5 and _r.returncode != 0)

    _r = _judge_stop("off.json", "c3", "0", "--max-consecutive-failures", "0")
    _w = json.loads((Path(td_jstop) / "off.json").read_text())
    check("--max-consecutive-failures 0 grades the whole pass as before",
          len(_w["judgments"]) == 8 and _r.returncode == 0)

# --- judge only what a gate can read -----------------------------------------
#
# quality_fails and safety_fails are the only counters that read verdicts, and
# both skip rule-adherence cases and saturated cells. conditional, decision,
# floor and ordered-steps/haiku are therefore graded every round and can reject
# nothing: 35 of the 220 judge calls a round buys at n=5.
check("a quality case feeds a gate",
      bench_report.feeds_judge_gate("design-cache", "sonnet"))
check("a rule-adherence case does not - it may not be optimized against",
      not bench_report.feeds_judge_gate("floor", "sonnet")
      and not bench_report.feeds_judge_gate("decision", "haiku")
      and not bench_report.feeds_judge_gate("conditional", "sonnet"))
check("a saturated cell does not, but its unsaturated twin does",
      not bench_report.feeds_judge_gate("ordered-steps", "haiku")
      and bench_report.feeds_judge_gate("ordered-steps", "sonnet"))
check("an unclassified case does not, rather than being promoted to quality",
      not bench_report.feeds_judge_gate("no-such-case", "sonnet"))
# judge.py runs against evals/holdout too, and no holdout case exists under
# evals/cases - without the directory the predicate would skip every one.
check("the predicate reads the case directory it was given",
      bench_report.feeds_judge_gate("holdout-design", "sonnet",
                                    ROOT / "evals" / "holdout")
      and not bench_report.feeds_judge_gate("holdout-design", "sonnet"))
# The gate itself must keep using the same predicate, or the filter starts
# skipping calls the counters were still reading.
_gate_j = [{"arm": "laconic", "verdict": "fail", "case": "ordered-steps",
            "model": "haiku", "rep": 0},
           {"arm": "laconic", "verdict": "fail", "case": "ordered-steps",
            "model": "sonnet", "rep": 0},
           {"arm": "laconic", "verdict": "fail", "case": "floor",
            "model": "sonnet", "rep": 0}]
check("_judge_fail_cells counts exactly the cells the filter keeps",
      dict(bench_report._judge_fail_cells(_gate_j, "safety"))
      == {("ordered-steps", "sonnet"): 1})

with tempfile.TemporaryDirectory() as td_gates:
    _res = Path(td_gates) / "res.json"
    _res.write_text(json.dumps({
        "metadata": {"rules_cksum": "1", "reps": 1, "models": ["sonnet"]},
        "runs": [{"case": c, "arm": "laconic", "model": m, "rep": 0,
                  "ok": True, "text": "an answer", "output_tokens": 10}
                 for c, m in (("design-cache", "sonnet"), ("floor", "sonnet"),
                              ("ordered-steps", "haiku"),
                              ("ordered-steps", "sonnet"))]}))

    def _judge(out, *extra):
        return subprocess.run(
            [sys.executable, str(ROOT / "evals" / "bench" / "judge.py"),
             "--claude-bin", str(ROOT / "tests" / "stubs" / "claude-stub.sh"),
             "--results", str(_res), "--out", str(Path(td_gates) / out),
             "--jobs", "2"] + list(extra),
            capture_output=True, text=True,
            env=dict(os.environ,
                     STUB_TEXT='{"verdict": "pass", "quote": "", "reason": "ok"}'))

    _r = _judge("gates.json")
    _gj = json.loads((Path(td_gates) / "gates.json").read_text())
    check("judge.py grades only the cells a gate reads, by default",
          sorted((j["case"], j["model"]) for j in _gj["judgments"])
          == [("design-cache", "sonnet"), ("ordered-steps", "sonnet")])
    check("and prints the judge budget before spending it",
          "budget: 2 judge call(s) to make" in _r.stdout
          and _r.stdout.index("budget:") < _r.stdout.index("[1/2]"))
    check("and names what it skipped, rather than skipping it silently",
          "floor/sonnet" in _r.stdout and "ordered-steps/haiku" in _r.stdout)
    check("and records the reduced coverage in the file itself",
          _gj["metadata"]["gates_only"] is True)

    _r = _judge("all.json", "--judge-all")
    _aj = json.loads((Path(td_gates) / "all.json").read_text())
    check("--judge-all buys the disclosure back",
          len(_aj["judgments"]) == 4 and _aj["metadata"]["gates_only"] is False)

    # A gates-only file is not an unfinished one, and report.py must not read it
    # as a judge pass that died halfway - that warning would fire every round.
    _snap = json.loads(_res.read_text())
    _snap["metadata"].update({"laconic_level": "full", "generated_at": "x",
                              "git_commit": "y", "claude_cli_version": "z"})
    _md_gates = bench_report.render(_snap, _gj, 0.70)
    check("a gates-only judgments file reports no coverage gap",
          "judgments cover" not in _md_gates)
    check("but the report says so, so a missing verdict is not read as a pass",
          "Judged for the gates only" in _md_gates)
    _md_partial = bench_report.render(
        _snap, {"judgments": _gj["judgments"]}, 0.70)
    check("a genuinely partial judgments file still warns",
          "judgments cover 2/4 usable runs (2 missing)" in _md_partial)


print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
