#!/usr/bin/env python3
"""Validates harness logic against stubs - no live model calls."""
import json
import os
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

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
