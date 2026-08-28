#!/usr/bin/env python3
"""Score detector v1 against the hand labels (#150).

Batch 2 is the out-of-sample measurement: the detector was frozen at 1e116ac
before that batch was drawn. Batch 1 is reported beside it, but it is NOT an
in-sample figure in the tuning sense - nothing was tuned on batch 1's errors -
so a gap between the two is sampling, not overfitting.

Duplicate texts are collapsed for the headline figures. The frame holds 1,780
rows over 1,430 distinct responses because the -v2/-v3/-v4 baselines are
supersets of round-01-n10.json, so the same run appears under several snapshot
names. Batch 2 drew two such pairs; counting both would treat one observation
as two.

`--verdicts` scores a different detector's file over the same keys and labels:
`--verdicts verdicts-deletable.json --kinds redundant` is how [#155]'s
direction B pilot is read. Passing `--kinds` counts a verdict as positive only
when its `kind` is one of the named ones, which is what scores a construct that
records why a passage costs nothing to delete.

usage: python3 score_detector.py [--verdicts NAME] [--kinds redundant,claimless]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
from report import _fisher_upper_tail  # noqa: E402

BATCHES = [("batch 1 (frozen after)", HERE),
           ("batch 2 (OUT OF SAMPLE)", HERE.parent / "restatement-b2")]


def load(d, name="verdicts.json"):
    key = {k["id"]: k for k in json.loads((d / "key.json").read_text())}
    lab = json.loads((d / "labels.json").read_text())["labels"]
    vpath = d / name
    doc = json.loads(vpath.read_text()) if vpath.exists() else {}
    return key, lab, doc.get("verdicts", {}), doc.get("metadata", {})


def texts(key):
    """id -> response text, for collapsing duplicates."""
    out = {}
    for i, k in key.items():
        for sub in ("evals/snapshots/loop", "evals/snapshots"):
            p = ROOT / sub / ("%s.json" % k["snap"])
            if p.exists():
                d = json.loads(p.read_text())
                hit = [r for r in d["runs"]
                       if r["case"] == k["case"] and r["rep"] == k["rep"]
                       and r["arm"] == "laconic" and r["model"] == k["model"]]
                if hit:
                    out[i] = hit[0]["text"].strip()
                    break
    return out


def confusion(ids, lab, ver, kinds=None):
    tp = fp = fn = tn = 0
    for i in ids:
        p = ver[i]["restates"]
        if kinds and ver[i].get("kind") not in kinds:
            p = False
        t = lab[i]
        tp += p and t
        fp += p and not t
        fn += (not p) and t
        tn += (not p) and (not t)
    return tp, fp, fn, tn


def report(name, tp, fp, fn, tn):
    n = tp + fp + fn + tn
    prec = 100.0 * tp / (tp + fp) if tp + fp else float("nan")
    rec = 100.0 * tp / (tp + fn) if tp + fn else float("nan")
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else float("nan")
    acc = 100.0 * (tp + tn) / n if n else float("nan")
    print("  %-26s n=%3d  TP %2d  FP %2d  FN %2d  TN %2d   "
          "precision %5.1f%%  recall %5.1f%%  F1 %5.1f%%  acc %5.1f%%"
          % (name, n, tp, fp, fn, tn, prec, rec, f1, acc))
    return prec, rec, f1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", default="verdicts.json",
                    help="verdicts file name inside each batch directory")
    ap.add_argument("--kinds", default="",
                    help="comma-separated `kind` values to count as positive; "
                         "empty counts every positive verdict")
    args = ap.parse_args()
    kinds = [k for k in args.kinds.split(",") if k]
    pooled = [0, 0, 0, 0]
    for name, d in BATCHES:
        key, lab, ver, meta = load(d, args.verdicts)
        scored = [i for i in key if i in ver]
        if not scored:
            print("%s: no verdicts yet" % name)
            continue
        seen, uniq = set(), []
        tx = texts(key)
        for i in sorted(scored):
            h = tx.get(i)
            if h in seen:
                continue
            seen.add(h)
            uniq.append(i)
        print("%s  (%d of %d labelled scored; %d after collapsing duplicates)"
              % (name, len(scored), len(key), len(uniq)))
        print("    detector %s, criterion %s%s"
              % (meta.get("detector", "?"), meta.get("criterion_cksum", "?"),
                 (", counting kind in %s" % ",".join(kinds)) if kinds else ""))
        c = confusion(uniq, lab, ver, kinds)
        report("deduplicated", *c)
        if len(uniq) != len(scored):
            report("all draws", *confusion(scored, lab, ver, kinds))
        base = sum(lab[i] for i in uniq)
        print("    hand-label base rate in the scored set: %d/%d (%.1f%%)"
              % (base, len(uniq), 100.0 * base / len(uniq)))
        # Does the detector beat "call everything restating"?
        print("    a detector that always said true would read precision %.1f%%, recall 100.0%%"
              % (100.0 * base / len(uniq)))
        if kinds or any("kind" in v for v in ver.values()):
            tally = {}
            for i in uniq:
                tally[ver[i].get("kind", "")] = tally.get(ver[i].get("kind", ""), 0) + 1
            print("    kinds: %s" % ", ".join(
                "%s %d" % (k or "clean", n) for k, n in sorted(tally.items())))
        pooled = [a + b for a, b in zip(pooled, c)]
        cost = sum(v.get("usage", {}).get("total_cost_usd", 0)
                   for k, v in ver.items() if k in scored)
        print("    cost: $%.2f over %d calls ($%.4f each)"
              % (cost, len(scored), cost / len(scored)))
        print()
    if all(x == 0 for x in pooled):
        return
    print("pooled across both batches:")
    report("deduplicated", *pooled)
    tp, fp, fn, tn = pooled
    print("  detector-positive vs detector-negative hand-label rate: "
          "%d/%d against %d/%d, one-sided Fisher p = %.2e"
          % (tp, tp + fp, fn, fn + tn,
             _fisher_upper_tail(tp, tp + fp, fn, fn + tn)))


if __name__ == "__main__":
    main()
