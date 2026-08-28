#!/usr/bin/env python3
"""The judged `deletable` detector ([#155] direction B, piloted for [#150]).

Scored against the 120 `restates` hand labels, which were written under a
different question. That is a yardstick and not a ground truth, and README.md
registers what it can and cannot show before any verdict was read.

Everything except the prompt and the reply shape is reused from
`../restatement/detector_v1.py` - the retry, the scratch directory that keeps
the call from reading this repository, the failure bookkeeping, and the lookup
from a key row to the stored response text. Reimplementing those is how the
first detector run wasted 176 calls on a usage limit.

The verdict is written under the key `restates` as well as `deletable`, so
`score_detector.py` reads it unchanged. `kind` is what separates the two
constructs and is scored on its own.

usage: python3 detector.py --key <key.json> --out <verdicts-deletable.json>
"""
import argparse
import json
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "restatement"))
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import detector_v1 as d1  # noqa: E402
import run as bench_run  # noqa: E402

TEMPLATE = """You are labelling one response against one specific criterion.

The criterion:
---
%s
---

The response to label:
---
%s
---

Reply with a single JSON object and nothing else:
{"deletable": true | false, "kind": "redundant" | "claimless" | "", "quote": "<short verbatim quote of the deletable passage, or empty>", "reason": "<one sentence>"}

Apply the criterion exactly as written, including its exclusions and its
borderline convention. A passage is one complete sentence or more: if the
passage would have to be rewritten rather than removed, the answer is false.
Set "kind" only when "deletable" is true.
"""


def criterion_text():
    return (HERE / "criterion.md").read_text()


def criterion_cksum():
    return str(zlib.crc32(criterion_text().encode()))


def build_prompt(response):
    return TEMPLATE % (criterion_text().strip(), response.strip())


def parse(text):
    """The verdict, or None when the reply is not a usable label.

    None is distinct from false, for the reason detector_v1.py gives: a model
    answering in prose has not said the response is clean, and counting it clean
    would inflate precision.
    """
    s = (text or "").strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s.split("\n", 1)[1] if "\n" in s else s
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j < i:
        return None
    try:
        d = json.loads(s[i:j + 1])
    except ValueError:
        return None
    if not isinstance(d, dict) or not isinstance(d.get("deletable"), bool):
        return None
    kind = d.get("kind") or ""
    if kind not in ("redundant", "claimless", ""):
        return None
    if d["deletable"] and not kind:
        return None
    return {"deletable": d["deletable"], "restates": d["deletable"],
            "kind": kind, "quote": d.get("quote") or "",
            "reason": d.get("reason") or ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="sonnet",
                    help="the model detector_v1 was measured on; changing it "
                         "makes the two constructs incomparable")
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--max-consecutive-failures", type=int, default=8)
    args = ap.parse_args()

    # The prompt and the reply shape are this module's; every mechanism around
    # them is detector_v1's.
    d1.TEMPLATE, d1.criterion_text, d1.parse = TEMPLATE, criterion_text, parse

    claude_bin = bench_run.require_claude_bin(args.claude_bin)
    key = json.loads(Path(args.key).read_text())
    out_path = Path(args.out)
    prev = (json.loads(out_path.read_text()) if out_path.exists()
            else {"metadata": {}, "verdicts": {}})
    done = prev.get("verdicts", {})

    todo = [k for k in key if k["id"] not in done]
    print("%d response(s) to label, %d already done" % (len(todo), len(done)))
    run_of_failures = 0
    stopped = None
    for n, k in enumerate(todo, 1):
        v, reason = d1.label_one(claude_bin, args.model, d1.response_text(k))
        if v is None:
            run_of_failures += 1
            print("  [%d/%d] %s FAILED (%s)" % (n, len(todo), k["id"], reason))
            if (args.max_consecutive_failures
                    and run_of_failures >= args.max_consecutive_failures):
                stopped = ("stopped after %d consecutive failure(s), last %s on %s"
                           % (run_of_failures, reason, k["id"]))
                print(stopped, file=sys.stderr)
                break
            continue
        run_of_failures = 0
        done[k["id"]] = v
        print("  [%d/%d] %s %s" % (n, len(todo), k["id"],
                                   ("deletable (%s)" % v["kind"]) if v["deletable"]
                                   else "clean"))
        out_path.write_text(json.dumps(
            {"metadata": {"detector": "deletable-v1", "model": args.model,
                          "criterion_cksum": criterion_cksum()},
             "verdicts": done}, indent=1) + "\n")
    cost = sum(v.get("usage", {}).get("total_cost_usd", 0) for v in done.values())
    print("wrote %s (%d of %d, $%.2f)" % (out_path, len(done), len(key), cost))
    if stopped:
        sys.exit(1)


if __name__ == "__main__":
    main()
