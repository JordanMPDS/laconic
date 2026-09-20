#!/usr/bin/env python3
"""How much of a `restates` re-label is the criterion, and how much is the labeller?

    python3 evals/results/loop/restatement/labeller_drift.py

[#155]'s direction A is "sharpen the criterion, freeze it, re-label all 120,
freeze a v2 detector, draw a third batch, measure". The step that was never
costed is the re-label. A re-label measures the criterion only if the labeller
is stable across sessions, and nothing in this repository had measured that -
`unread_asks` ruled its labeller out at kappa 0.902 and `restates` never ran the
equivalent.

This script runs both halves of that question off files that cost no calls:

- **The control.** `restatement-b2/labels-v1-relabel.json` is batch 2 labelled
  again under criterion.md UNCHANGED, blind to labels.json, in a separate
  session. Any disagreement here is the labeller, because the rule is identical.
- **The signal.** `restatement/labels-v2.json` is batch 1 labelled under
  criterion-v2.md, whose only change is the whole-sentence rule. The difference
  from labels.json is the criterion plus whatever the labeller contributes.

The comparison of the two is the point. It is also why the oracle ceiling below
matters: a detector is scored against one label set, so a second label set drawn
the same way is the best any detector could possibly read.
"""
import json
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
B1, B2 = HERE, HERE.parent / "restatement-b2"


def labels(path):
    return json.loads(Path(path).read_text())["labels"]


def cases(path):
    return {k["id"]: k["case"] for k in json.loads(Path(path).read_text())}


def confusion(ids, a, b):
    """(both true, a-only, b-only, both false) - a is the reference set."""
    tt = sum(1 for i in ids if a[i] and b[i])
    af = sum(1 for i in ids if a[i] and not b[i])
    bf = sum(1 for i in ids if b[i] and not a[i])
    ff = sum(1 for i in ids if not a[i] and not b[i])
    return tt, af, bf, ff


def kappa(ids, a, b):
    n = len(ids)
    po = sum(1 for i in ids if a[i] == b[i]) / n
    pa, pb = sum(a[i] for i in ids) / n, sum(b[i] for i in ids) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def fisher_two_sided(a, b, c, d):
    n, r1, c1 = a + b + c + d, a + b, a + c
    if not r1 or not (c + d) or not c1 or not (b + d):
        return 1.0
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)

    def p(k):
        return comb(r1, k) * comb(n - r1, c1 - k) / comb(n, c1)
    obs = p(a) * (1 + 1e-9)
    return min(1.0, sum(p(k) for k in range(lo, hi + 1) if p(k) <= obs))


def pair(name, ids, a, b, a_name, b_name):
    tt, af, bf, ff = confusion(ids, a, b)
    po, k = kappa(ids, a, b)
    print("%s  n=%d" % (name, len(ids)))
    print("    %-22s true %2d (%.1f%%)" % (a_name, tt + af, 100.0 * (tt + af) / len(ids)))
    print("    %-22s true %2d (%.1f%%)" % (b_name, tt + bf, 100.0 * (tt + bf) / len(ids)))
    print("    agreement %d/%d = %.1f%%   Cohen kappa = %.3f"
          % (tt + ff, len(ids), 100.0 * po, k))
    print("    moved: %d true->false, %d false->true, %d total"
          % (af, bf, af + bf))
    # The ceiling a detector could read against `a`, if it were as good as `b`.
    prec = 100.0 * tt / (tt + bf) if tt + bf else float("nan")
    rec = 100.0 * tt / (tt + af) if tt + af else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
    print("    oracle ceiling against %s: precision %.1f%%  recall %.1f%%  F1 %.1f%%"
          % (a_name, prec, rec, f1))
    return af + bf


def by_case(ids, a, b, cmap):
    groups = {}
    for i in ids:
        groups.setdefault(cmap[i], []).append(i)
    print("    by case:")
    rows = []
    for c in sorted(groups):
        g = groups[c]
        moved = sum(1 for i in g if a[i] != b[i])
        rows.append((c, moved, len(g)))
        print("      %-20s %2d of %2d moved  (%.1f%%)"
              % (c, moved, len(g), 100.0 * moved / len(g)))
    # Is the movement concentrated, or spread evenly over the four cases?
    worst = max(rows, key=lambda r: r[1] / r[2] if r[2] else 0)
    om, on = sum(r[1] for r in rows) - worst[1], sum(r[2] for r in rows) - worst[2]
    p = fisher_two_sided(worst[1], worst[2] - worst[1], om, on - om)
    print("      %s against the rest: %d/%d vs %d/%d, Fisher p = %.4f"
          % (worst[0], worst[1], worst[2], om, on, p))


def main():
    b2_committed = labels(B2 / "labels.json")
    b2_relabel = labels(B2 / "labels-v1-relabel.json")
    b1_v1 = labels(B1 / "labels.json")
    b1_v2 = labels(B1 / "labels-v2.json")

    print("=== CONTROL: batch 2, criterion v1 twice, two sessions ===")
    ids2 = sorted(set(b2_committed) & set(b2_relabel))
    drift = pair("same rule, different session", ids2, b2_committed, b2_relabel,
                 "committed labels", "re-label")
    by_case(ids2, b2_committed, b2_relabel, cases(B2 / "key.json"))

    print()
    print("=== SIGNAL: batch 1, criterion v1 against criterion v2 ===")
    ids1 = sorted(set(b1_v1) & set(b1_v2))
    signal = pair("v1 against v2", ids1, b1_v1, b1_v2,
                  "v1 labels", "v2 labels")
    by_case(ids1, b1_v1, b1_v2, cases(B1 / "key.json"))
    # v2 adds a restriction and changes nothing else, so every v2 true should be
    # a v1 true. A false-to-true move cannot come from the criterion.
    impossible = [i for i in ids1 if b1_v2[i] and not b1_v1[i]]
    print("    nesting: v2 is v1 plus one restriction, so v2-true should be a")
    print("    subset of v1-true. %d response(s) violate that: %s"
          % (len(impossible), ", ".join(impossible) or "none"))

    print()
    print("=== THE COMPARISON ===")
    print("  criterion moved %d of %d labels; the labeller alone moves %d of %d."
          % (signal, len(ids1), drift, len(ids2)))
    print("  A re-label separates the two only if the first number is large")
    print("  against the second. It is not.")


if __name__ == "__main__":
    sys.exit(main())
