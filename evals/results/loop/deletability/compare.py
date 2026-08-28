#!/usr/bin/env python3
"""Score the four predictions README.md registered, and show the disagreements.

Reads the `restates` hand labels, detector v1's verdicts, and the `deletable`
verdicts over the same 120 keys. Prediction 1 is scored against
`fp_shapes.json`, which assigns every one of v1's 26 false positives to a shape
and was written before this detector ran.

usage: python3 compare.py [--verdicts verdicts-deletable.json] [--quotes]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCHES = [("batch 1", HERE.parent / "restatement"),
           ("batch 2", HERE.parent / "restatement-b2")]


def load(d, name):
    key = {k["id"]: k for k in json.loads((d / "key.json").read_text())}
    lab = json.loads((d / "labels.json").read_text())["labels"]
    v1 = json.loads((d / "verdicts.json").read_text())["verdicts"]
    p = d / name
    b = json.loads(p.read_text())["verdicts"] if p.exists() else {}
    return key, lab, v1, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", default="verdicts-deletable.json")
    ap.add_argument("--quotes", action="store_true",
                    help="print the quote both detectors returned")
    args = ap.parse_args()

    shapes = json.loads((HERE / "fp_shapes.json").read_text())["shapes"]
    rows = []
    for name, d in BATCHES:
        key, lab, v1, b = load(d, args.verdicts)
        for i in sorted(key):
            if i not in b:
                continue
            rows.append({"batch": name, "id": i, "case": key[i]["case"],
                         "model": key[i]["model"], "label": lab[i],
                         "v1": v1.get(i, {}).get("restates"),
                         "v1_quote": v1.get(i, {}).get("quote", ""),
                         "b": b[i]["deletable"], "kind": b[i].get("kind", ""),
                         "b_quote": b[i].get("quote", "")})
    if not rows:
        sys.exit("no %s verdicts yet" % args.verdicts)

    print("=== prediction 1: at least 10 of the 14 mixed-closing false "
          "positives go clean")
    by_shape = {}
    for r in rows:
        s = shapes.get(r["id"])
        if s is None or r["v1"] is not True or r["label"] is not False:
            continue
        cleared = not r["b"]
        by_shape.setdefault(s, []).append((r["id"], cleared, r["kind"]))
    for s in sorted(by_shape):
        got = by_shape[s]
        n = sum(1 for _, c, _ in got if c)
        print("  %-26s %2d of %2d cleared   %s"
              % (s, n, len(got),
                 " ".join("%s%s" % (i, "" if c else "(%s)" % (k or "still true"))
                          for i, c, k in got)))
    mixed = by_shape.get("mixed_closing", [])
    n = sum(1 for _, c, _ in mixed if c)
    print("  VERDICT: %d of %d cleared - prediction 1 %s"
          % (n, len(mixed), "HOLDS" if n >= 10 else "FAILS"))

    print("\n=== prediction 3: claimless-only true on no more than 15% of "
          "responses")
    only_claimless = [r for r in rows if r["b"] and r["kind"] == "claimless"]
    pct = 100.0 * len(only_claimless) / len(rows)
    print("  %d of %d (%.1f%%) - prediction 3 %s"
          % (len(only_claimless), len(rows), pct,
             "HOLDS" if pct <= 15.0 else "FAILS"))
    if only_claimless:
        print("  hand label true on %d of them, so they are not all ceremony"
              % sum(1 for r in only_claimless if r["label"]))

    print("\n=== where the two detectors disagree with each other")
    dis = [r for r in rows if r["v1"] is not None and r["v1"] != r["b"]]
    print("  %d of %d responses" % (len(dis), len(rows)))
    agree_lab = sum(1 for r in dis if r["b"] == r["label"])
    print("  on those, `deletable` matches the hand label %d times, v1 %d times"
          % (agree_lab, len(dis) - agree_lab))

    print("\n=== every response, hand label / v1 / deletable")
    for r in rows:
        mark = "".join(("L" if r["label"] else ".",
                        "1" if r["v1"] else ".",
                        "B" if r["b"] else "."))
        print("  %s %-4s %-18s %-6s %s %-9s %s"
              % (r["batch"], r["id"], r["case"], r["model"], mark, r["kind"],
                 shapes.get(r["id"], "")))
        if args.quotes:
            for who, q in (("v1", r["v1_quote"]), ("B ", r["b_quote"])):
                if q:
                    print("        %s: %s" % (who, q.replace("\n", " ")[:160]))


if __name__ == "__main__":
    main()
