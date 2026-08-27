#!/usr/bin/env python3
"""The judged `restates` detector, v1 (#150).

COMMITTED BEFORE BATCH 2 WAS DRAWN. That order is the whole reason the
out-of-sample figures mean anything: unread_asks v2 read 93.1% precision on the
batch it was designed against and 73.7% on a fresh one, and the only reason
anyone knows that is that the freeze happened first.

Why judged rather than computed. asks_back is a regex, which made unread_asks
free to re-score across every stored run. Restatement has no such surface form,
and both cheap alternatives were measured rather than assumed:

- Lexical containment (lexical_probe.py) fails in the WRONG DIRECTION. On the
  known-redundant response the closing recap scores 0.21; on the known-dense
  response the top score is 0.40, on a passage that contrasts two kinds of 401
  rather than repeating either.
- A closing-flourish regex reads 87.5% precision and 26.9% recall against
  batch 1. Formulaic closers are nearly always real restatements and account
  for about a quarter of them; the rest are recap lists that re-ask questions
  already posed and sections that re-argue a mechanism already stated in full.

The criterion is READ FROM criterion.md rather than restated here, so the rule
the labeller applied and the rule the detector is given cannot drift. Its
checksum is returned with every verdict, the way judge.py carries
criteria_cksum: a criterion that changes invalidates the comparison, and that
has to be visible rather than inferred.

usage: python3 detector_v1.py --key key.json [--out verdicts.json] [--model sonnet]
"""
import argparse
import json
import shutil
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
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
{"restates": true | false, "quote": "<short verbatim quote of the restating passage, or empty>", "reason": "<one sentence>"}

Apply the criterion exactly as written, including its exclusions and its
borderline convention. Length is not the criterion: a long response that says
each thing once is false, and a short response whose last sentence repeats its
first is true.
"""


def criterion_text():
    return (HERE / "criterion.md").read_text()


def criterion_cksum():
    return str(zlib.crc32(criterion_text().encode()))


def build_prompt(response):
    return TEMPLATE % (criterion_text().strip(), response.strip())


def parse(text):
    """The verdict, or None when the reply is not a usable label.

    None is distinct from false. A model that returns prose instead of JSON has
    not said the response is clean, and counting it as clean would silently
    inflate the detector's apparent precision.
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
    if not isinstance(d, dict) or not isinstance(d.get("restates"), bool):
        return None
    return {"restates": d["restates"], "quote": d.get("quote") or "",
            "reason": d.get("reason") or ""}


def label_one(claude_bin, model, response):
    """One detector call, retried once, in a fresh temp dir.

    The temp dir is not decoration. This repository contains rules/laconic.md,
    the snapshots labelled by arm, and criterion.md's own worked examples; a
    call made from ROOT could read any of them. judge.py takes the same
    precaution for the same reason.
    """
    prompt = build_prompt(response)
    for _ in range(2):
        scratch = tempfile.mkdtemp()
        try:
            res = bench_run.call(claude_bin, model, prompt, None, scratch)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        if res.get("ok"):
            v = parse(res.get("text"))
            if v is not None:
                v["usage"] = {k: res.get(k, 0) for k in
                              ("input_tokens", "output_tokens",
                               "cache_creation_input_tokens",
                               "cache_read_input_tokens", "total_cost_usd",
                               "duration_ms")}
                return v
    return None


def response_text(k):
    for sub in ("evals/snapshots/loop", "evals/snapshots"):
        p = ROOT / sub / ("%s.json" % k["snap"])
        if p.exists():
            d = json.loads(p.read_text())
            hit = [r for r in d["runs"]
                   if r["case"] == k["case"] and r["rep"] == k["rep"]
                   and r["arm"] == "laconic" and r["model"] == k["model"]]
            if hit:
                return hit[0]["text"]
    sys.exit("no response for %s" % k["id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=str(HERE / "key.json"))
    ap.add_argument("--out", default=str(HERE / "verdicts.json"))
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--claude-bin", default="claude")
    args = ap.parse_args()

    claude_bin = bench_run.require_claude_bin(args.claude_bin)
    key = json.loads(Path(args.key).read_text())
    out_path = Path(args.out)
    prev = (json.loads(out_path.read_text()) if out_path.exists()
            else {"metadata": {}, "verdicts": {}})
    done = prev.get("verdicts", {})

    todo = [k for k in key if k["id"] not in done]
    print("%d response(s) to label, %d already done" % (len(todo), len(done)))
    for n, k in enumerate(todo, 1):
        v = label_one(claude_bin, args.model, response_text(k))
        if v is None:
            print("  [%d/%d] %s UNPARSEABLE" % (n, len(todo), k["id"]))
            continue
        done[k["id"]] = v
        print("  [%d/%d] %s %s" % (n, len(todo), k["id"],
                                   "restates" if v["restates"] else "clean"))
        out_path.write_text(json.dumps(
            {"metadata": {"detector": "v1", "model": args.model,
                          "criterion_cksum": criterion_cksum()},
             "verdicts": done}, indent=1) + "\n")
    cost = sum(v.get("usage", {}).get("total_cost_usd", 0) for v in done.values())
    print("wrote %s (%d verdicts, $%.2f)" % (out_path, len(done), cost))


if __name__ == "__main__":
    main()
