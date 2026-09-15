#!/usr/bin/env python3
"""Score the #298 re-explanation pilot: does the scoped carve-out cut restatement?

[#298] reports a seven-word definition request answered in 342 prose words, of
which 239 restated claims the session had already delivered. The reporter's
diagnosis is that nothing in `rules/laconic.md` forbids it: the never-cut bullet
protecting "anything the user asked to have explained" fires on "what is X?" and
is silent on whether X was explained two turns ago.

`explain-*` and `reexplain-*` are the same fixture and the same graded question.
`explain-*` asks it cold in one turn; `reexplain-*` asks `deep-*`'s open
diagnosis question first, so the model's own answer has already delivered the
rationale before the definition request arrives. The manipulation is whether the
content is already in the transcript, and nothing else.

    python3 evals/pilot/score_reexplain.py <control.json> <edit.json> [seed]

The two snapshots are the two rules revisions, generated simultaneously from two
worktrees per [round 38](../results/loop/round-38.md), because this project has
measured style moving 4x across days at byte-identical rules and a sequential
pair cannot be read.

The primary is the difference of differences: how much more the edit shortens
`reexplain` than it shortens `explain`. `explain` is the placebo - a cold
question has nothing already given for the new clause to remove, so an edit that
shortens both equally is a general brevity effect rather than the scoped one
[#298] asks for, and the interaction is what separates them.

Words are prose words by `metrics.score`, so fenced code and inline spans are
out of the count on both families. [#298] is about prose.
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
FAMILIES = ("explain", "reexplain")
SEED = 68

#: Two-sided permutation on two independent samples. Shared with the other
#: pilots rather than copied, so the test cannot drift between them.
permutation = metrics.permutation


def cells():
    return tuple((side, fam) for side in ("control", "edit") for fam in FAMILIES)


def difference_of_differences(g):
    """How much more the edit moves `reexplain` than it moves `explain`.

    On logged words this is a log ratio of ratios, so exponentiating it gives
    the factor by which the edit's effect on the already-told question exceeds
    its effect on the cold one. Below 1 is the registered direction.
    """
    def mean(key):
        return sum(g[key]) / len(g[key])
    return ((mean(("edit", "reexplain")) - mean(("control", "reexplain")))
            - (mean(("edit", "explain")) - mean(("control", "explain"))))


def interaction(groups, seed, resamples=200000):
    """Permute the rules-revision label within each family, preserving sizes.

    The statistic is the difference of differences. Runs are not paired across
    families - the two families are different cases - so the label that can be
    shuffled is the side's, inside a family. This is `score_register.py`'s test
    with the rules revision in place of the arm; the shape is identical and so
    is the caveat, which is that on raw words two well-separated modes make the
    null distribution reflect which side drew the long answers. The log-scale
    version is the one to read.
    """
    if any(not groups[k] for k in cells()):
        return None
    obs = abs(difference_of_differences(groups))
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        shuffled = {}
        for fam in FAMILIES:
            pool = list(groups[("control", fam)]) + list(groups[("edit", fam)])
            n = len(groups[("control", fam)])
            rng.shuffle(pool)
            shuffled[("control", fam)] = pool[:n]
            shuffled[("edit", fam)] = pool[n:]
        if abs(difference_of_differences(shuffled)) >= obs - 1e-9:
            hits += 1
    return (hits + 1) / (resamples + 1)


def log_words(groups):
    """The same cells on a log scale, or None if any run scored zero words."""
    keys = cells()
    if any(not groups[k] for k in keys):
        return None
    if any(v <= 0 for k in keys for v in groups[k]):
        return None
    return {k: [math.log(v) for v in groups[k]] for k in keys}


def sign_test(diffs):
    """Two-sided exact sign test over per-cell differences. Ties dropped.

    Six cells is the registered scope and 6 of 6 reads p = 0.031, which is the
    only outcome that reaches alpha; 5 of 6 is p = 0.219. That ceiling is
    stated in the round document rather than discovered here - `kimi`, via
    `tools/consult.sh`, is why the scope is six cells rather than three.
    """
    vals = [d for d in diffs if abs(d) > 1e-12]
    n = len(vals)
    if n == 0:
        return None, 0, 0
    neg = sum(1 for d in vals if d < 0)
    k = min(neg, n - neg)
    tail = sum(math.comb(n, i) for i in range(k + 1))
    return min(1.0, 2 * tail / 2 ** n), neg, n


def fmt(p):
    return "-" if p is None else "%.4f" % p


def load(path, side, graded, cell, kept, counts):
    snap = json.loads(Path(path).read_text())
    for r in bench_run.usable(snap["runs"]):
        family, stem = r["case"].split("-", 1)
        if family not in FAMILIES or stem not in STEMS:
            continue
        words = metrics.score(r.get("text", ""))["words"]
        counts[side] += 1
        graded[(side, family)].append(words)
        cell[(side, family, stem, r["model"])].append(words)
        expect = json.loads(
            (Path(__file__).resolve().parent / r["case"] / "expect.json").read_text())
        kw = expect.get("never_cut") or []
        if kw:
            kept[(side, family)].append(
                not metrics.never_cut_missing(r.get("text", ""), kw))
    return snap


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else SEED

    graded = defaultdict(list)
    cell = defaultdict(list)
    kept = defaultdict(list)
    counts = defaultdict(int)
    snaps = {}
    for side, path in (("control", sys.argv[1]), ("edit", sys.argv[2])):
        snaps[side] = load(path, side, graded, cell, kept, counts)

    for side in ("control", "edit"):
        m = snaps[side]["metadata"]
        print("%-8s runs %3d   rules_cksum %-12s turn_delivery %s"
              % (side, counts[side], m.get("rules_cksum"), m.get("turn_delivery")))
    if snaps["control"]["metadata"].get("rules_cksum") == \
            snaps["edit"]["metadata"].get("rules_cksum"):
        print("\n!! both snapshots carry the same rules_cksum: there is no edit here")

    print("\n## The harm, on the control side: does already-told inflate the answer?")
    c_ex = graded[("control", "explain")]
    c_re = graded[("control", "reexplain")]
    print("   explain (cold)     n=%3d  median %6.1f words"
          % (len(c_ex), metrics.median(c_ex)))
    print("   reexplain (told)   n=%3d  median %6.1f words"
          % (len(c_re), metrics.median(c_re)))
    print("   ratio %.3f, p = %s"
          % ((metrics.median(c_re) / metrics.median(c_ex)) if c_ex and metrics.median(c_ex) else float("nan"),
             fmt(permutation(c_ex, c_re, seed))))

    print("\n## Primary: prose words on the graded turn, by side and family")
    print("%-11s %5s %9s %9s %8s %9s" % ("family", "n", "control", "edit", "ratio", "p"))
    for fam in FAMILIES:
        a, b = graded[("control", fam)], graded[("edit", fam)]
        ma, mb = metrics.median(a), metrics.median(b)
        print("%-11s %5d %9.1f %9.1f %8.3f %9s"
              % (fam, len(a), ma, mb, (mb / ma) if ma else float("nan"),
                 fmt(permutation(a, b, seed))))

    print("\n   interaction (edit's effect on reexplain minus its effect on explain)")
    print("   raw words, p = %s" % fmt(interaction(graded, seed)))
    logged = log_words(graded)
    if logged is None:
        print("   log words: - (a run scored zero words)")
    else:
        print("   log words, a ratio of ratios of %.3f, p = %s"
              % (math.exp(difference_of_differences(logged)),
                 fmt(interaction(logged, seed))))

    print("\n## Secondary: the same interaction per cell, six cells")
    print("%-9s %-7s %19s %19s %9s"
          % ("stem", "model", "explain c/e", "reexplain c/e", "log DiD"))
    diffs = []
    for stem in STEMS:
        for model in sorted({k[3] for k in cell}):
            got = {}
            for side in ("control", "edit"):
                for fam in FAMILIES:
                    got[(side, fam)] = cell[(side, fam, stem, model)]
            if any(not v for v in got.values()):
                print("%-9s %-7s %19s %19s %9s"
                      % (stem, model, "-", "-", "(a group is empty)"))
                continue
            med = {k: metrics.median(v) for k, v in got.items()}
            if any(v <= 0 for v in med.values()):
                print("%-9s %-7s %19s %19s %9s"
                      % (stem, model, "-", "-", "(a median is zero)"))
                continue
            did = ((math.log(med[("edit", "reexplain")]) - math.log(med[("control", "reexplain")]))
                   - (math.log(med[("edit", "explain")]) - math.log(med[("control", "explain")])))
            diffs.append(did)
            print("%-9s %-7s %19s %19s %9.3f"
                  % (stem, model,
                     "%.1f / %.1f" % (med[("control", "explain")], med[("edit", "explain")]),
                     "%.1f / %.1f" % (med[("control", "reexplain")], med[("edit", "reexplain")]),
                     did))
    p, neg, n = sign_test(diffs)
    print("\n   %d of %d cells negative, two-sided exact sign test p = %s"
          % (neg, n, fmt(p)))

    print("\n## Harm check: the index stem's never-cut keyword on the graded turn")
    for fam in FAMILIES:
        for side in ("control", "edit"):
            v = kept[(side, fam)]
            print("   %-10s %-8s %d/%d kept" % (fam, side, sum(v), len(v)))


if __name__ == "__main__":
    main()
