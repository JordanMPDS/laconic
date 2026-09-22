#!/usr/bin/env python3
"""Score the #136 register pilot: does a licensed-long stretch carry forward?

`register-*` and `deep-*` are the same fixture, the same five turns and the
same trap. Turns 1 and 5 are byte-identical. Turns 2 to 4 ask deep's three
questions verbatim and add an explicit request for the full form, which
`rules/laconic.md` licenses at length. So the only thing that varies is the
register the model's own four prior answers were written in.

    python3 evals/pilot/score_register.py <snapshot> [seed] [treatment] [reference]

Words are prose words by `metrics.score`, so fenced code and inline spans are
out of the count on both families. #136 is about prose.

`treatment` names the family on the right-hand side of every table and
`reference` the family on the left. They default to `register` and `deep`, so
every figure published in `register-inheritance-136.md` reproduces from the
stored snapshot with the command that produced it. Round 67 passes `work`: the
same pair shape, with turns 2 to 4 moving their deliverable into the fixture
file instead of lengthening the reply. Round 69 passes both halves -
`fullexplain reexplain` and `deepexplain reexplain` - which is a pair whose two
families have *different turn counts*, and is why the graded turn is the last
turn of the run rather than turn 5 (see `graded_words`). One scorer rather than
a copy, because the pilots differ only in which families sit on the two sides of
every table - and a copy is a second place for the permutation, the
stratification and the broken-interaction note to drift.
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


#: Two-sided permutation of the group label over per-response counts, on
#: means. Lived here until round 51 needed the same test on medians; one
#: implementation in metrics keeps the two scorers from drifting apart.
permutation = metrics.permutation


#: Set by main() from argv, so a pilot that is not #136's reads the same code.
TREATMENT = "register"
#: The family on the left of every table, and the one the treatment is measured
#: against. Round 69's is `reexplain`, which has two turns where the treatment
#: has five.
REFERENCE = "deep"
#: Tool names that mean the response changed something in the workspace. Read
#: off the per-turn tool list, which run.py records for every turn.
WORK_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


def cells():
    return (("laconic", TREATMENT), ("laconic", REFERENCE),
            ("baseline", TREATMENT), ("baseline", REFERENCE))


def difference_of_differences(g):
    """How much more the laconic arm rises from deep to register than baseline.

    On raw words this is a difference of word counts. On logged words it is a
    log ratio of ratios, so exponentiating it gives the factor by which the
    laconic rise exceeds the baseline one.
    """
    def mean(key):
        return sum(g[key]) / len(g[key])
    return ((mean(("laconic", TREATMENT)) - mean(("laconic", REFERENCE)))
            - (mean(("baseline", TREATMENT)) - mean(("baseline", REFERENCE))))


def interaction_corrected(groups, seed, resamples=200000):
    """[#298]'s corrected null: additive-fit residuals shuffled across cells.

    The statistic is unchanged and so is the bootstrap interval printed beside
    it; only the way the null is built moves. See
    `metrics.interaction_permutation` for why shuffling the arm label is 1.9x
    too wide on this instrument and why shuffling the family label instead is
    the same defect mirrored, and
    `evals/results/loop/interaction-null-298.md` for the calibration and the
    archive re-analysis.

    [#298]: https://github.com/JordanMPDS/laconic/issues/298
    """
    return metrics.interaction_permutation(
        groups, ("baseline", "laconic"), (REFERENCE, TREATMENT), seed,
        resamples=resamples)


def interaction(groups, seed, resamples=200000):
    """Permute the arm label within each family, preserving family sizes.

    **Superseded by `interaction_corrected` and kept only to reproduce the
    rounds that registered it** — rounds 47, 49, 67 and 69 and
    `register-inheritance-136.md` all read their interaction off this test, and
    a stored verdict has to stay recomputable from the code that produced it.
    Do not register a new round against it.

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
    if any(not groups[k] for k in cells()):
        return None
    obs = abs(stat(groups))
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        shuffled = {}
        for fam in (REFERENCE, TREATMENT):
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
    keys = cells()
    if any(not groups[k] for k in keys):
        return None
    if any(v <= 0 for k in keys for v in groups[k]):
        return None
    return {k: [math.log(v) for v in groups[k]] for k in keys}


def fmt(p):
    return "-" if p is None else "%.4f" % p


def turn_words(run, idx):
    turns = run.get("turns") or []
    if idx >= len(turns):
        return None
    return metrics.score(turns[idx].get("text", ""))["words"]


def graded_words(run):
    """Prose words on the run's **last** turn, which is the graded one.

    Every pair this scorer serves holds turn 1 and the final turn byte-identical
    and manipulates what lies between, so the graded turn is the last one by
    construction. Indexing from the end rather than at turn 5 is what lets a
    pair compare families of different lengths: round 69 measures a five-turn
    family against `reexplain-*`, which has two turns. On the five-turn pairs
    this is turn 5, so #136's and round 67's published figures are unchanged.
    """
    turns = run.get("turns") or []
    if not turns:
        return None
    return turn_words(run, len(turns) - 1)


def middle_words(run):
    """Prose words summed over the turns between the first and the graded one.

    Empty for a two-turn family, which has no middle, and `None` if any turn
    that should be there is missing - a partial run has to be dropped rather
    than scored as a short one.
    """
    turns = run.get("turns") or []
    vals = [turn_words(run, i) for i in range(1, max(len(turns) - 1, 1))]
    if any(v is None for v in vals):
        return None
    return sum(vals)


def did_work(run):
    """True when a turn between the first and the graded one called a tool that
    changes the workspace.

    The graded turn is excluded deliberately: it carries "Don't edit anything."
    in both families, so a tool call there would be a rule violation rather
    than the manipulation, and counting it would let a violation clear the
    check.
    """
    turns = run.get("turns") or []
    return any(t in WORK_TOOLS
               for turn in turns[1:len(turns) - 1]
               for t in (turn.get("tools") or []))


def main():
    snap = json.loads(Path(sys.argv[1]).read_text())
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else SEED
    global TREATMENT, REFERENCE
    if len(sys.argv) > 3:
        TREATMENT = sys.argv[3]
    if len(sys.argv) > 4:
        REFERENCE = sys.argv[4]

    graded = defaultdict(list)   # (arm, family) -> words on the graded turn
    middle = defaultdict(list)   # (arm, family) -> words over the middle turns
    cell = defaultdict(list)     # (arm, family, stem) -> words on the graded turn
    kept = defaultdict(list)     # (arm, family) -> never-cut keyword present
    worked = defaultdict(list)   # (arm, family) -> turns 2-4 changed the tree
    wrote = defaultdict(list)    # (arm, family) -> the run left an artifact
    n_runs = 0

    for r in bench_run.usable(snap["runs"]):
        family, stem = r["case"].split("-", 1)
        if family not in (REFERENCE, TREATMENT) or stem not in STEMS:
            continue
        last = graded_words(r)
        mid = middle_words(r)
        if last is None or mid is None:
            continue
        n_runs += 1
        graded[(r["arm"], family)].append(last)
        middle[(r["arm"], family)].append(mid)
        worked[(r["arm"], family)].append(did_work(r))
        wrote[(r["arm"], family)].append(bool(r.get("artifacts")))
        cell[(r["arm"], family, stem)].append(last)
        expect = json.loads(
            (Path(__file__).resolve().parent / r["case"] / "expect.json").read_text())
        kw = expect.get("never_cut") or []
        if kw:
            kept[(r["arm"], family, stem)].append(
                not metrics.never_cut_missing(r.get("text", ""), kw))

    print("runs scored: %d   turn_delivery: %s   rules_cksum: %s"
          % (n_runs, snap["metadata"].get("turn_delivery"),
             snap["metadata"].get("rules_cksum")))

    print("\n## Manipulation check: the middle turns changed the workspace")
    print("%-9s %12s %12s   %s" % ("arm", REFERENCE, TREATMENT, "(artifacts left)"))
    for arm in ("baseline", "laconic"):
        for key, label in ((worked, "tool"), (wrote, "artifact")):
            d, g = key[(arm, REFERENCE)], key[(arm, TREATMENT)]
            print("%-9s %12s %12s   %s"
                  % (arm if label == "tool" else "",
                     "%d/%d" % (sum(d), len(d)), "%d/%d" % (sum(g), len(g)),
                     label))

    print("\n## Manipulation check: words over the middle turns (per run)")
    print("   a two-turn family has no middle turns and reads 0.0 by construction")
    print("%-9s %8s %8s %8s" % ("arm", REFERENCE, TREATMENT, "p"))
    for arm in ("baseline", "laconic"):
        d, g = middle[(arm, REFERENCE)], middle[(arm, TREATMENT)]
        print("%-9s %8.1f %8.1f %8s"
              % (arm, metrics.median(d or [0]), metrics.median(g or [0]),
                 fmt(permutation(d, g, seed))))

    print("\n## Primary: prose words on the graded turn (the last turn)")
    print("%-9s %5s %8s %8s %8s %8s"
          % ("arm", "n", REFERENCE, TREATMENT, "ratio", "p"))
    for arm in ("baseline", "laconic"):
        d, g = graded[(arm, REFERENCE)], graded[(arm, TREATMENT)]
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
        print("   same, [#298]'s corrected null (aligned residuals), p = %s"
              % fmt(interaction_corrected(logged, seed)))

    print("\n## By stem, median words on the graded turn")
    print("%-9s %-9s %8s %8s %8s" % ("arm", "stem", REFERENCE, TREATMENT, "p"))
    for arm in ("baseline", "laconic"):
        for stem in STEMS:
            d, g = cell[(arm, REFERENCE, stem)], cell[(arm, TREATMENT, stem)]
            print("%-9s %-9s %8.1f %8.1f %8s"
                  % (arm, stem, metrics.median(d), metrics.median(g),
                     fmt(permutation(d, g, seed))))

    print("\n## Harm check: never-cut keyword present on the graded turn")
    for (arm, family, stem), vals in sorted(kept.items()):
        print("   %-9s %-9s %-9s %d/%d" % (arm, family, stem, sum(vals), len(vals)))


if __name__ == "__main__":
    main()
