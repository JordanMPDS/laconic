#!/usr/bin/env python3
"""How the judge panel agreed with itself, and with a single judge's file.

    python3 evals/bench/panel_agreement.py <panel-judgments.json> [<single-judgments.json>]

Reads the per-member votes judge.py keeps on every panel record. Prints each
member's agreement with the majority, every pairwise agreement with Cohen's
kappa, the split and undecided rates, and each member's parse failures. Given a
single-judge file over the same runs, it also prints how often the panel's
majority differs from that judge's verdict, split by direction, which is what
changing the judge does to a counter.
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402


def key(j):
    return (j["case"], j["arm"], j["model"], j["rep"])


def kappa(pairs):
    """Cohen's kappa over (a, b) label pairs; None when chance agreement is 1."""
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[x] * cb[x] for x in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def fmt(k):
    return "  n/a" if k is None else "%.3f" % k


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    panel = json.loads(Path(sys.argv[1]).read_text())
    recs = [j for j in panel["judgments"] if j.get("panel")]
    print("setup: %s   records with panel votes: %d"
          % ((panel.get("metadata") or {}).get("judge_model"), len(recs)))
    decided = [j for j in recs if not judge._is_infra_failure(j)]
    split = sum(j["reason"] == judge.REASON_PANEL_SPLIT for j in decided)
    print("decided %d, undecided (retry on resume) %d, three-way splits %d"
          % (len(decided), len(recs) - len(decided), split))

    members = judge.PANEL
    print("\n## Each member against the majority, and its failed or unparsed votes")
    for m in members:
        pairs = [(j["panel"][m]["verdict"], j["verdict"]) for j in decided
                 if j["panel"][m]["verdict"] is not None]
        lost = sum(j["panel"][m]["verdict"] is None for j in recs)
        agree = sum(a == b for a, b in pairs)
        print("   %-7s %3d/%-3d agree  kappa %s   no vote %d"
              % (m, agree, len(pairs), fmt(kappa(pairs)), lost))

    print("\n## Pairwise")
    for a, b in itertools.combinations(members, 2):
        pairs = [(j["panel"][a]["verdict"], j["panel"][b]["verdict"]) for j in recs
                 if j["panel"][a]["verdict"] and j["panel"][b]["verdict"]]
        print("   %-7s %-7s %3d/%-3d agree  kappa %s"
              % (a, b, sum(x == y for x, y in pairs), len(pairs), fmt(kappa(pairs))))

    if len(sys.argv) == 3:
        single = json.loads(Path(sys.argv[2]).read_text())
        name = (single.get("metadata") or {}).get("judge_model") or "single"
        before = {key(j): j["verdict"] for j in single["judgments"]
                  if not judge._is_infra_failure(j)}
        both = [(before[key(j)], j["verdict"]) for j in decided if key(j) in before]
        moved = Counter((a, b) for a, b in both if a != b)
        print("\n## The panel's majority against %s's file, %d runs in both"
              % (name, len(both)))
        print("   same verdict %d, kappa %s"
              % (sum(a == b for a, b in both), fmt(kappa(both))))
        for (a, b), n in sorted(moved.items()):
            print("   %s -> %s: %d" % (a, b, n))


if __name__ == "__main__":
    main()
