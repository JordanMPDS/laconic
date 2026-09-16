#!/usr/bin/env python3
"""Round 69's reporting figures, which decide nothing.

The round's verdict is `score_register.py`'s registered permutation, and
nothing here recomputes it. This file computes what the registration said it
would publish beside that test - the geometric-mean ratio with a bootstrap
interval, the raw whitespace count beside the prose one, the graded turn's tool
calls - plus one instrument figure the round had to add after seeing the two
disagree: the width of the registered interaction's own null against the
sampling distribution of the same statistic.

    python3 evals/pilot/round69_supplement.py evals/snapshots/loop/round-69.json

Graded-turn and middle-turn extraction is imported from `score_register` rather
than repeated, because a copy is a second place for either to drift. The
families are named here rather than parameterised: this is round 69's report,
not a scorer, and a later round that wants these figures should import them
from a scorer instead of generalising this.
"""
import json
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import score_register as sr  # noqa: E402

REFERENCE = "reexplain"
TREATMENTS = ("deepexplain", "fullexplain")
STEMS = sr.STEMS
ARMS = ("baseline", "laconic")
SEED = 69
DRAWS = 10000


def family(run):
    return run["case"].rsplit("-", 1)[0]


def stem(run):
    return run["case"].rsplit("-", 1)[1]


def load(path):
    """{(arm, family, stem): [runs]} over the usable runs of one snapshot.

    Each run's graded word count is scored once and cached on the record: the
    bootstrap draws ten thousand replicates and re-running `metrics.score` on
    every one of them turns a second of work into several minutes.
    """
    snap = json.loads(Path(path).read_text())
    cells = {}
    for r in snap["runs"]:
        if r.get("ok"):
            r["_graded"] = sr.graded_words(r)
            cells.setdefault((r["arm"], family(r), stem(r)), []).append(r)
    return snap, cells


def words(cells, arm, fam):
    return [r["_graded"] for s in STEMS for r in cells[(arm, fam, s)]]


def gmean(vals):
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def _resample(cells, arm, fam, rng):
    """One bootstrap replicate, drawn within stem so the stem mix is fixed."""
    out = []
    for s in STEMS:
        pool = [r["_graded"] for r in cells[(arm, fam, s)]]
        out += [rng.choice(pool) for _ in pool]
    return out


def ratio_interval(cells, arm, fam, seed=SEED, draws=DRAWS):
    rng = random.Random(seed)
    point = gmean(words(cells, arm, fam)) / gmean(words(cells, arm, REFERENCE))
    draw = sorted(gmean(_resample(cells, arm, fam, rng))
                  / gmean(_resample(cells, arm, REFERENCE, rng))
                  for _ in range(draws))
    return point, draw[int(0.025 * draws)], draw[int(0.975 * draws)]


def rr(get):
    """Ratio of ratios: how much more the laconic arm rises than baseline."""
    return ((get("laconic", "treatment") / get("laconic", REFERENCE))
            / (get("baseline", "treatment") / get("baseline", REFERENCE)))


def rr_interval(cells, fam, seed=SEED, draws=DRAWS):
    rng = random.Random(seed)

    def point(arm, which):
        return gmean(words(cells, arm, fam if which == "treatment" else which))

    drawn = []
    for _ in range(draws):
        rep = {(a, f): gmean(_resample(cells, a, f, rng))
               for a in ARMS for f in (fam, REFERENCE)}
        drawn.append(rr(lambda a, w: rep[(a, fam if w == "treatment" else w)]))
    drawn.sort()
    return (rr(point), drawn[int(0.025 * draws)], drawn[int(0.975 * draws)])


def resolution(cells, fam, seed=SEED, draws=20000):
    """The registered interaction's null width against the statistic's own.

    The registered test shuffles the arm label inside each family. When the
    arms are far apart every shuffled group is a mixture of two separated
    modes, so the null is wide for a reason that is not the interaction. Round
    42 recorded this for raw words; the number below says whether the log scale
    the registration moved to actually escapes it.
    """
    logs = {(a, f): [math.log(v) for v in words(cells, a, f)]
            for a in ARMS for f in (fam, REFERENCE)}

    def dod(g):
        def m(a, f):
            return sum(g[(a, f)]) / len(g[(a, f)])
        return (m("laconic", fam) - m("laconic", REFERENCE)) \
            - (m("baseline", fam) - m("baseline", REFERENCE))

    obs = dod(logs)
    rng = random.Random(seed)
    null = []
    for _ in range(draws):
        sh = {}
        for f in (fam, REFERENCE):
            pool = list(logs[("laconic", f)]) + list(logs[("baseline", f)])
            n = len(logs[("laconic", f)])
            rng.shuffle(pool)
            sh[("laconic", f)] = pool[:n]
            sh[("baseline", f)] = pool[n:]
        null.append(dod(sh))
    boot = []
    for _ in range(draws):
        boot.append(dod({k: [rng.choice(v) for _ in v] for k, v in logs.items()}))
    gap = (sum(logs[("baseline", REFERENCE)]) / len(logs[("baseline", REFERENCE)])
           - sum(logs[("laconic", REFERENCE)]) / len(logs[("laconic", REFERENCE)]))
    return obs, statistics.pstdev(null), statistics.pstdev(boot), math.exp(gap)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "evals/snapshots/loop/round-69.json"
    snap, cells = load(path)
    runs = [r for r in snap["runs"] if r.get("ok")]
    print("runs scored: %d   seed: %d   draws: %d   rules_cksum: %s"
          % (len(runs), SEED, DRAWS, snap["metadata"]["rules_cksum"]))

    print("\n## Geometric-mean ratio on the graded turn, 95% bootstrap interval")
    print("arm       family        ratio        95% interval")
    for fam in TREATMENTS:
        for arm in ARMS:
            pt, lo, hi = ratio_interval(cells, arm, fam)
            print("%-9s %-12s  %6.3f       %.3f to %.3f" % (arm, fam, pt, lo, hi))

    print("\n## Ratio of ratios: the laconic rise over the baseline one")
    for fam in TREATMENTS:
        pt, lo, hi = rr_interval(cells, fam)
        print("%-12s  %6.3f       %.3f to %.3f" % (fam, pt, lo, hi))

    print("\n## What the registered interaction test can resolve")
    print("family        log dod   perm null sd   bootstrap sd   ratio   arms apart")
    for fam in TREATMENTS:
        obs, ns, bs, gap = resolution(cells, fam)
        print("%-12s  %+7.3f   %12.3f   %12.3f   %5.1fx   %8.2fx"
              % (fam, obs, ns, bs, ns / bs, gap))

    print("\n## Raw whitespace tokens on the graded turn, median")
    print("arm       " + "".join("%-13s" % f for f in (REFERENCE,) + TREATMENTS))
    for arm in ARMS:
        row = []
        for fam in (REFERENCE,) + TREATMENTS:
            raw = [len((r["turns"][-1].get("text") or "").split())
                   for s in STEMS for r in cells[(arm, fam, s)]]
            row.append("%-13.1f" % metrics.median(raw))
        print("%-9s " % arm + "".join(row))

    print("\n## Prose words on the graded turn: min, median, max")
    for arm in ARMS:
        for fam in (REFERENCE,) + TREATMENTS:
            v = sorted(words(cells, arm, fam))
            print("%-9s %-12s min %3d   median %6.1f   max %3d"
                  % (arm, fam, v[0], metrics.median(v), v[-1]))

    print("\n## Tool calls on the graded turn, which carries \"Don't edit anything.\"")
    for arm in ARMS:
        for fam in (REFERENCE,) + TREATMENTS:
            rs = [r for s in STEMS for r in cells[(arm, fam, s)]]
            names = [t for r in rs for t in (r["turns"][-1].get("tools") or [])]
            quiet = sum(1 for r in rs if not (r["turns"][-1].get("tools") or []))
            print("%-9s %-12s no tool call in %2d/%2d%s"
                  % (arm, fam, quiet, len(rs),
                     "" if not names else "   calls: " + ",".join(sorted(set(names)))))

    print("\n## Cost")
    print("total $%.2f over %d runs" % (
        sum(r.get("total_cost_usd") or 0 for r in runs), len(runs)))
    for arm in ARMS:
        for fam in (REFERENCE,) + TREATMENTS:
            rs = [r for s in STEMS for r in cells[(arm, fam, s)]]
            print("  %-9s %-12s $%5.2f" % (
                arm, fam, sum(r.get("total_cost_usd") or 0 for r in rs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
