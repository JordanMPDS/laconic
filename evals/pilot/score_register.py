#!/usr/bin/env python3
"""Score the #136 register pilot: does a licensed-long stretch carry forward?

`register-*` and `deep-*` are the same fixture, the same five turns and the
same trap. Turns 1 and 5 are byte-identical. Turns 2 to 4 ask deep's three
questions verbatim and add an explicit request for the full form, which
`rules/laconic.md` licenses at length. So the only thing that varies is the
register the model's own four prior answers were written in.

    python3 evals/pilot/score_register.py <snapshot> [seed]

Words are prose words by `metrics.score`, so fenced code and inline spans are
out of the count on both families. #136 is about prose.
"""
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402

STEMS = ("index", "metric", "rollback")
SEED = 136


def permutation(a, b, seed, resamples=200000):
    """Two-sided permutation of the group label over per-response counts.

    Returns None when either side is empty, which is what a partial snapshot
    looks like while a shard is still generating. A p-value invented from one
    group is worse than no p-value.
    """
    if not a or not b:
        return None
    obs = abs(sum(b) / len(b) - sum(a) / len(a))
    pool = list(a) + list(b)
    n = len(a)
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        rng.shuffle(pool)
        d = abs(sum(pool[n:]) / (len(pool) - n) - sum(pool[:n]) / n)
        if d >= obs - 1e-9:
            hits += 1
    return (hits + 1) / (resamples + 1)


CELLS = (("laconic", "register"), ("laconic", "deep"),
         ("baseline", "register"), ("baseline", "deep"))


def difference_of_differences(g):
    """How much more the laconic arm rises from deep to register than baseline.

    On raw words this is a difference of word counts. On logged words it is a
    log ratio of ratios, so exponentiating it gives the factor by which the
    laconic rise exceeds the baseline one.
    """
    def mean(key):
        return sum(g[key]) / len(g[key])
    return ((mean(("laconic", "register")) - mean(("laconic", "deep")))
            - (mean(("baseline", "register")) - mean(("baseline", "deep"))))


def interaction(groups, seed, resamples=200000):
    """Permute the arm label within each family, preserving family sizes.

    The statistic is the difference of differences. Runs are not paired across
    families - the two families are different cases - so the label that can be
    shuffled is the arm's, inside a family.

    On raw words this test is known to be broken rather than conservative: the
    arms are an order of magnitude apart, so shuffling the arm label builds
    each group as a mixture of two well-separated modes and the null
    distribution is dominated by which arm drew the long answers. Round 42
    recorded that defect. It is computed here because the #136 registration
    named it, and reported beside the log-scale version where the arms are on
    comparable scales.
    """
    stat = difference_of_differences
    if any(not groups[k] for k in CELLS):
        return None
    obs = abs(stat(groups))
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        shuffled = {}
        for fam in ("deep", "register"):
            pool = list(groups[("laconic", fam)]) + list(groups[("baseline", fam)])
            n = len(groups[("laconic", fam)])
            rng.shuffle(pool)
            shuffled[("laconic", fam)] = pool[:n]
            shuffled[("baseline", fam)] = pool[n:]
        if abs(stat(shuffled)) >= obs - 1e-9:
            hits += 1
    return (hits + 1) / (resamples + 1)


def log_words(groups):
    """The same cells on a log scale, or None if any run scored zero words.

    Returns None rather than dropping the run, because silently shrinking a
    group changes the test being reported without saying so.
    """
    if any(not groups[k] for k in CELLS):
        return None
    if any(v <= 0 for k in CELLS for v in groups[k]):
        return None
    return {k: [math.log(v) for v in groups[k]] for k in CELLS}


def fmt(p):
    return "-" if p is None else "%.4f" % p


def turn_words(run, idx):
    turns = run.get("turns") or []
    if idx >= len(turns):
        return None
    return metrics.score(turns[idx].get("text", ""))["words"]


def main():
    snap = json.loads(Path(sys.argv[1]).read_text())
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else SEED

    graded = defaultdict(list)   # (arm, family) -> words on turn 5
    middle = defaultdict(list)   # (arm, family) -> words over turns 2-4
    cell = defaultdict(list)     # (arm, family, stem) -> words on turn 5
    kept = defaultdict(list)     # (arm, family) -> never-cut keyword present
    n_runs = 0

    for r in bench_run.usable(snap["runs"]):
        family, stem = r["case"].split("-", 1)
        if family not in ("deep", "register") or stem not in STEMS:
            continue
        five = turn_words(r, 4)
        mid = [turn_words(r, i) for i in (1, 2, 3)]
        if five is None or any(m is None for m in mid):
            continue
        n_runs += 1
        graded[(r["arm"], family)].append(five)
        middle[(r["arm"], family)].append(sum(mid))
        cell[(r["arm"], family, stem)].append(five)
        expect = json.loads(
            (Path(__file__).resolve().parent / r["case"] / "expect.json").read_text())
        kw = expect.get("never_cut") or []
        if kw:
            kept[(r["arm"], family, stem)].append(
                not metrics.never_cut_missing(r.get("text", ""), kw))

    print("runs scored: %d   turn_delivery: %s   rules_cksum: %s"
          % (n_runs, snap["metadata"].get("turn_delivery"),
             snap["metadata"].get("rules_cksum")))

    print("\n## Manipulation check: words over turns 2-4 (per run)")
    print("%-9s %8s %8s %8s" % ("arm", "deep", "register", "p"))
    for arm in ("baseline", "laconic"):
        d, g = middle[(arm, "deep")], middle[(arm, "register")]
        print("%-9s %8.1f %8.1f %8s"
              % (arm, metrics.median(d), metrics.median(g),
                 fmt(permutation(d, g, seed))))

    print("\n## Primary: prose words on the graded turn (turn 5)")
    print("%-9s %5s %8s %8s %8s %8s"
          % ("arm", "n", "deep", "register", "ratio", "p"))
    for arm in ("baseline", "laconic"):
        d, g = graded[(arm, "deep")], graded[(arm, "register")]
        md, mg = metrics.median(d), metrics.median(g)
        print("%-9s %5d %8.1f %8.1f %8.3f %8s"
              % (arm, len(d), md, mg, (mg / md) if md else float("nan"),
                 fmt(permutation(d, g, seed))))

    print("\n   interaction (laconic rise minus baseline rise), p = %s"
          % fmt(interaction(graded, seed)))
    logged = log_words(graded)
    if logged is None:
        print("   same on log words: - (a run scored zero words)")
    else:
        print("   same on log words, a ratio of ratios of %.3f, p = %s"
              % (math.exp(difference_of_differences(logged)),
                 fmt(interaction(logged, seed))))

    print("\n## By stem, median words on the graded turn")
    print("%-9s %-9s %8s %8s %8s" % ("arm", "stem", "deep", "register", "p"))
    for arm in ("baseline", "laconic"):
        for stem in STEMS:
            d, g = cell[(arm, "deep", stem)], cell[(arm, "register", stem)]
            print("%-9s %-9s %8.1f %8.1f %8s"
                  % (arm, stem, metrics.median(d), metrics.median(g),
                     fmt(permutation(d, g, seed))))

    print("\n## Harm check: never-cut keyword present on the graded turn")
    for (arm, family, stem), vals in sorted(kept.items()):
        print("   %-9s %-9s %-9s %d/%d" % (arm, family, stem, sum(vals), len(vals)))


if __name__ == "__main__":
    main()
