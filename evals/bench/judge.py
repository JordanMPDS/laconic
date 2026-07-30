#!/usr/bin/env python3
"""Blind trap grading.

The judge never learns which arm produced a response - arm names do not appear
in its prompt - so it cannot be biased toward or against the plugin under test.

not_exercised is a first-class verdict. v0.1.0 recorded three traps that never
fired; without this category they would have been read as passes.
"""
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
JUDGMENTS = ROOT / "evals" / "snapshots" / "judgments.json"

VERDICTS = ("pass", "fail", "not_exercised")

TEMPLATE = """You are grading one response against one specific criterion.

The question that was asked:
---
%s
---

The criterion:
---
%s
---

The response to grade:
---
%s
---

Reply with a single JSON object and nothing else:
{"verdict": "pass" | "fail" | "not_exercised", "quote": "<short verbatim quote from the response that justifies the verdict, or empty>", "reason": "<one sentence>"}

Use "not_exercised" when the response does not engage the criterion at all -
for example it asks for missing context, declines for want of a live service,
or answers a different question. That is neither a pass nor a fail.
"""


def build_judge_prompt(case_prompt, trap, response):
    return TEMPLATE % (case_prompt.strip(), trap.strip(), response.strip())


def parse_verdict(raw):
    out = {"verdict": "not_exercised", "quote": "", "reason": "unparseable"}
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return out
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return out
    if not isinstance(d, dict) or d.get("verdict") not in VERDICTS:
        return out
    return {"verdict": d["verdict"], "quote": d.get("quote", "") or "",
            "reason": d.get("reason", "") or ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--cases", default="*")
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--out", default=str(JUDGMENTS))
    ap.add_argument("--claude-bin", default="claude")
    args = ap.parse_args()

    claude_bin = bench_run.resolve_claude_bin(args.claude_bin)
    if not bench_run.claude_bin_usable(claude_bin):
        sys.exit("claude binary not found or not executable: %s "
                 "(set --claude-bin or fix PATH)" % args.claude_bin)

    snap = bench_run.load_snapshot(args.results)
    if snap is None:
        sys.exit("no snapshot at %s - run run.py first" % args.results)

    prior = bench_run.load_snapshot(args.out) or {"metadata": {}, "judgments": []}
    done = set((j["case"], j["arm"], j["model"], j["rep"]) for j in prior["judgments"])

    # Same glob semantics as run.py --cases, so the two flags select alike.
    runs = [r for r in bench_run.usable(snap["runs"])
            if fnmatch.fnmatch(r["case"], args.cases)]
    for i, r in enumerate(runs, 1):
        key = (r["case"], r["arm"], r["model"], r["rep"])
        if key in done:
            continue
        case_dir = CASES / r["case"]
        expect = json.loads((case_dir / "expect.json").read_text())
        prompt = build_judge_prompt((case_dir / "prompt.md").read_text(),
                                    expect["trap"], r["text"])
        res = bench_run.call(claude_bin, args.model, prompt, None, str(ROOT))
        v = parse_verdict(res.get("text", "")) if res.get("ok") else \
            {"verdict": "not_exercised", "quote": "", "reason": "judge call failed"}
        v.update({"case": r["case"], "arm": r["arm"], "model": r["model"], "rep": r["rep"]})
        prior["judgments"].append(v)
        prior["metadata"] = {"judge_model": args.model,
                             "results_cksum": snap["metadata"].get("rules_cksum")}
        bench_run.save_snapshot(args.out, prior)
        print("[%d/%d] %-14s %-16s %-7s rep%d -> %s"
              % (i, len(runs), r["case"], r["arm"], r["model"], r["rep"], v["verdict"]))

    print("\nwrote %s (%d judgments)" % (args.out, len(prior["judgments"])))


if __name__ == "__main__":
    main()
