#!/usr/bin/env python3
"""Score round 47: does a persistence clause make the licensed-long register expire?

The #136 register pilot established that a laconic session whose four prior
answers were written at a length the rules licensed answers the identical
closed question with 1.68x the words. This scores an edit against that effect,
on the same pair, with the group label being the rules revision rather than the
arm — so both sides are the laconic arm and the two snapshots come from two
trees generated simultaneously.

    python3 evals/pilot/score_persistence.py <control.json> <edit.json> [seed]

`score_register.py` does the same arithmetic with the label being the arm; the
tests, the word measure and the never-cut check are imported from it rather
than restated, so the two scorers cannot drift on what a word is.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_register import STEMS, fmt, permutation, turn_words  # noqa: E402

SEED = 60
SIDES = ("control", "edit")
CELLS = tuple((side, fam) for side in SIDES for fam in ("register", "deep"))


def collect(path):
    """Per-run word counts out of one snapshot, keyed by family and stem."""
    snap = json.loads(Path(path).read_text())
    graded, middle, cell, kept = {}, {}, defaultdict(list), defaultdict(list)
    graded = defaultdict(list)
    middle = defaultdict(list)
    n = 0
    for r in bench_run.usable(snap["runs"]):
        family, stem = r["case"].split("-", 1)
        if family not in ("deep", "register") or stem not in STEMS:
            continue
        if r["arm"] != "laconic":
            continue
        five = turn_words(r, 4)
        mid = [turn_words(r, i) for i in (1, 2, 3)]
        if five is None or any(m is None for m in mid):
            continue
        n += 1
        graded[family].append(five)
        middle[family].append(sum(mid))
        cell[(family, stem)].append(five)
        expect = json.loads(
            (Path(__file__).resolve().parent / r["case"] / "expect.json").read_text())
        kw = expect.get("never_cut") or []
        if kw:
            kept[(family, stem)].append(
                not metrics.never_cut_missing(r.get("text", ""), kw))
    return dict(n=n, meta=snap["metadata"], graded=graded, middle=middle,
                cell=cell, kept=kept)


def difference_of_differences(g):
    """How much further the register family falls than the deep family.

    Both sides are the laconic arm on the same fixture, so unlike the pilot's
    arm contrast the two groups are on comparable scales and the raw-words
    version of this test is not the broken one round 42 recorded. The log
    version is still the registered arbiter, because the finding this scores is
    stated as a ratio.
    """
    def mean(key):
        return sum(g[key]) / len(g[key])
    return ((mean(("edit", "register")) - mean(("control", "register")))
            - (mean(("edit", "deep")) - mean(("control", "deep"))))


def interaction(groups, seed, resamples=200000):
    """Permute the side label within each family, preserving family sizes."""
    import random
    if any(not groups[k] for k in CELLS):
        return None
    obs = abs(difference_of_differences(groups))
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        shuffled = {}
        for fam in ("register", "deep"):
            pool = list(groups[("control", fam)]) + list(groups[("edit", fam)])
            k = len(groups[("control", fam)])
            rng.shuffle(pool)
            shuffled[("control", fam)] = pool[:k]
            shuffled[("edit", fam)] = pool[k:]
        if abs(difference_of_differences(shuffled)) >= obs - 1e-9:
            hits += 1
    return (hits + 1) / (resamples + 1)


def main():
    control, edit = collect(sys.argv[1]), collect(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else SEED
    sides = {"control": control, "edit": edit}

    for name, s in sides.items():
        print("%-8s runs %3d   turn_delivery: %s   rules_cksum: %s"
              % (name, s["n"], s["meta"].get("turn_delivery"),
                 s["meta"].get("rules_cksum")))
    if control["meta"].get("rules_cksum") == edit["meta"].get("rules_cksum"):
        print("\n!! both snapshots carry the same rules_cksum - this is not a contrast")

    print("\n## Primary: prose words on the graded turn (turn 5), laconic arm")
    print("%-10s %5s %9s %8s %8s %8s"
          % ("family", "n", "control", "edit", "ratio", "p"))
    for fam in ("register", "deep"):
        c, e = control["graded"][fam], edit["graded"][fam]
        mc, me = metrics.median(c), metrics.median(e)
        print("%-10s %5d %9.1f %8.1f %8.3f %8s"
              % (fam, len(c), mc, me, (me / mc) if mc else float("nan"),
                 fmt(permutation(c, e, seed))))

    groups = {(side, fam): sides[side]["graded"][fam] for side, fam in CELLS}
    print("\n   interaction (register fall minus deep fall), p = %s"
          % fmt(interaction(groups, seed)))
    if all(v > 0 for k in CELLS for v in groups[k]):
        logged = {k: [math.log(v) for v in groups[k]] for k in CELLS}
        print("   same on log words, a ratio of ratios of %.3f, p = %s"
              % (math.exp(difference_of_differences(logged)),
                 fmt(interaction(logged, seed))))
    else:
        print("   same on log words: - (a run scored zero words)")

    print("\n## The scale-free statement: register median / deep median, turn 5")
    for name, s in sides.items():
        d = metrics.median(s["graded"]["deep"])
        print("   %-8s %.3f" % (name, metrics.median(s["graded"]["register"]) / d
                                if d else float("nan")))

    print("\n## Harm check (fatal): words over turns 2-4, the requested full form")
    print("%-10s %9s %8s %8s" % ("family", "control", "edit", "p"))
    for fam in ("register", "deep"):
        c, e = control["middle"][fam], edit["middle"][fam]
        print("%-10s %9.1f %8.1f %8s"
              % (fam, metrics.median(c), metrics.median(e),
                 fmt(permutation(c, e, seed))))

    print("\n## By stem, median words on the graded turn")
    print("%-10s %-9s %9s %8s %8s" % ("family", "stem", "control", "edit", "p"))
    for fam in ("register", "deep"):
        for stem in STEMS:
            c, e = control["cell"][(fam, stem)], edit["cell"][(fam, stem)]
            print("%-10s %-9s %9.1f %8.1f %8s"
                  % (fam, stem, metrics.median(c), metrics.median(e),
                     fmt(permutation(c, e, seed))))

    print("\n## Harm check: never-cut keyword present on the graded turn")
    for name, s in sides.items():
        for (fam, stem), vals in sorted(s["kept"].items()):
            print("   %-8s %-10s %-9s %d/%d"
                  % (name, fam, stem, sum(vals), len(vals)))


if __name__ == "__main__":
    main()
