#!/usr/bin/env python3
"""Emit one re-ordered copy of a blind file per labelling pass.

    python3 evals/results/loop/restatement/consensus/shuffle.py --out /tmp/restates-consensus

Six passes read the same 60 responses, and a labeller that reads them in the
same order every time can agree with itself for a reason that is not the
criterion: anchoring on the first few items, and drift down a long file. Both
consult targets raised re-ordering as the one decorrelation that costs nothing
and confounds nothing - a different model would measure a committee rather than
the labeller whose drift `labeller_drift.py` reports.

The response text is copied byte for byte and only the order moves, so a pass
is comparable to the committed labels, which were written in id order.
"""
import argparse
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BLIND = HERE.parent.parent / "restatement-b2" / "blind.md"
SEP = re.compile(r"^=====\s+(\S+)\s+\|", re.M)


def responses(text):
    """[(id, block)] in file order, block including its own header line."""
    starts = [m.start() for m in SEP.finditer(text)]
    ids = [m.group(1) for m in SEP.finditer(text)]
    if not starts:
        raise SystemExit("no response separators found")
    bounds = starts + [len(text)]
    return [(ids[i], text[bounds[i]:bounds[i + 1]]) for i in range(len(starts))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", default=str(DEFAULT_BLIND))
    ap.add_argument("--out", required=True)
    ap.add_argument("--passes", type=int, default=6)
    a = ap.parse_args()

    blocks = responses(Path(a.blind).read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in range(1, a.passes + 1):
        order = list(blocks)
        # Pass 1 keeps file order, so one pass is directly comparable to the
        # committed labels; passes 2..N are shuffled on their own pass number.
        if p > 1:
            random.Random(1550 + p).shuffle(order)
        path = out / ("blind-pass-%d.md" % p)
        path.write_text("".join(b for _, b in order))
        print("%s  %d responses  first=%s" % (path, len(order), order[0][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
