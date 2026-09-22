#!/usr/bin/env python3
"""[#298]: what the interaction null costs, and which repair actually sizes it.

    python3 evals/pilot/interaction_calibration.py            # everything
    python3 evals/pilot/interaction_calibration.py --archive  # the stored rounds

Three pilot scorers test a 2x2 interaction on log prose words by permuting the
**side** label inside each family, where the side is an arm (`baseline` against
`laconic`) or a rules revision. Round 69 measured the consequence on the arm
version: a null **1.9x wider** than the sampling distribution of the statistic
it tests, because the arms sit about 8x apart and every shuffled group is a
mixture of two separated modes.

**The obvious repair is not the repair, and section 1 is why.** Shuffling the
family label instead moves the same inflation onto the family's main effect.
Both labels carry main effects on the real pilots, so the null has to be built
from residuals that carry neither: `metrics.interaction_permutation` aligns on
the additive fit and shuffles those residuals across all four cells. The
statistic never changes - the additive part contributes exactly zero to a
difference of differences - and neither does the bootstrap interval reported
beside it.

Four sections, in the order `evals/results/loop/interaction-null-298.md`
reports them:

1. **Symmetry.** Three nulls against the sampling standard deviation on
   synthetic cells with a side gap only, a family gap only, and neither.
2. **Widths.** The same three on every stored interaction.
3. **Calibration and power.** False-positive rate under a constructed true
   null, and detection at injected effects.
4. **Archive.** Every stored interaction recomputed.

The true null is constructed rather than assumed: the four observed cell means
are replaced by their additive fit, so the interaction is exactly zero while the
side gap, the family gap and every cell's spread stay the ones the instrument
really produced. Residuals are resampled within their own cell, so a cell that
is noisier than its neighbours stays noisier.
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

SEED = 298
ALPHA = 0.05
#: Calibration is 1000 draws of 1000 resamples, which resolves a rate of 0.05
#: to about +/- 0.007. The archive re-score below uses the scorers' own 200000,
#: because a published p is read to four places and a calibration rate is not.
DRAWS = 1000
RESAMPLES = 1000
#: Fixed before any figure was computed: a test is calibrated when its
#: false-positive rate at alpha 0.05 lies in [0.035, 0.065], about two standard
#: errors either side at 1000 draws.
FPR_BAND = (0.035, 0.065)
POWER_FACTORS = (1.00, 1.25, 1.50, 1.75, 2.00)
SD_DRAWS = 4000

#: Every stored interaction read off an **arm**-label permutation, with the
#: seed and the families the round that published it passed, so the legacy
#: column reproduces what that round printed. These are the four round 69
#: names: the arms are about 8x apart here, which is what makes the legacy null
#: wide. The rules-revision pilots - rounds 47 and 49 through
#: `score_persistence.py`, round 68 through `score_reexplain.py` - shuffle a
#: label whose two sides are close together, and are recomputed by running
#: those scorers, which now print the corrected line themselves.
ARCHIVE = (
    ("register-inheritance-136", "register-136.json", "register", "deep", 136),
    ("round-67", "round-67.json", "work", "deep", 67),
    ("round-69 deepexplain", "round-69.json", "deepexplain", "reexplain", 69),
    ("round-69 fullexplain", "round-69.json", "fullexplain", "reexplain", 69),
)
SNAPS = Path("evals/snapshots/loop")
SIDES = ("baseline", "laconic")


def cells_of(sides, families):
    return [(s, f) for s in sides for f in families]


def dod(groups, sides, families):
    return metrics.difference_of_differences(groups, sides, families)


def log_cells(path, treatment, reference):
    """{(arm, family): [log prose words]} on the graded turn of one snapshot.

    Returns None when a cell is empty or a run scored zero words, which is what
    `log_words` in the scorers does and for the same reason: a log of zero is
    not a shorter answer, it is a run with no prose in it.
    """
    sr.TREATMENT, sr.REFERENCE = treatment, reference
    snap = json.loads(Path(path).read_text())
    groups = {}
    for r in snap["runs"]:
        if not r.get("ok"):
            continue
        fam = r["case"].rsplit("-", 1)[0]
        if fam not in (treatment, reference):
            continue
        groups.setdefault((r["arm"], fam), []).append(sr.graded_words(r))
    keys = cells_of(SIDES, (reference, treatment))
    if any(not groups.get(k) for k in keys):
        return None
    if any(v <= 0 for k in keys for v in groups[k]):
        return None
    return {k: [math.log(v) for v in groups[k]] for k in keys}


def shuffle_side(groups, sides, families, rng):
    """The superseded null: the side label shuffled inside each family.

    **The pool is built treated-side-first and split at its length**, which is
    the order `score_register.py` uses. A permutation p depends on the order the
    random stream is consumed, so reversing it would move the legacy column in
    the fourth decimal and stop it reproducing what the rounds published.
    """
    out = {}
    for fam in families:
        pool = list(groups[(sides[1], fam)]) + list(groups[(sides[0], fam)])
        n = len(groups[(sides[1], fam)])
        rng.shuffle(pool)
        out[(sides[1], fam)] = pool[:n]
        out[(sides[0], fam)] = pool[n:]
    return out


def shuffle_family(groups, sides, families, rng):
    """The mirror-image null, computed only to show it is the mirror image."""
    out = {}
    for side in sides:
        pool = list(groups[(side, families[0])]) + list(groups[(side, families[1])])
        n = len(groups[(side, families[0])])
        rng.shuffle(pool)
        out[(side, families[0])] = pool[:n]
        out[(side, families[1])] = pool[n:]
    return out


def shuffle_residual(groups, sides, families, rng):
    """The corrected null: additive-fit residuals shuffled across all cells."""
    cells = cells_of(sides, families)
    fit = metrics.additive_fit(groups, sides, families)
    resid = [v - fit[c] for c in cells for v in groups[c]]
    rng.shuffle(resid)
    out, i = {}, 0
    for c in cells:
        n = len(groups[c])
        out[c] = resid[i:i + n]
        i += n
    return out


SHUFFLES = (("legacy", shuffle_side), ("family", shuffle_family),
            ("residual", shuffle_residual))


def permutation_p(groups, sides, families, seed, shuffle, resamples):
    obs = abs(dod(groups, sides, families))
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        if abs(dod(shuffle(groups, sides, families, rng),
                   sides, families)) >= obs - 1e-9:
            hits += 1
    return (hits + 1) / (resamples + 1)


def null_sd(groups, sides, families, seed, shuffle, draws=SD_DRAWS):
    rng = random.Random(seed)
    return statistics.stdev(
        dod(shuffle(groups, sides, families, rng), sides, families)
        for _ in range(draws))


def sampling_sd(groups, sides, families, seed, draws=SD_DRAWS):
    """Bootstrap standard deviation of the statistic, resampling within cell.

    This is the spread the data actually carry: each cell is resampled from
    itself, so no main effect is disturbed and neither separation enters. A
    null wider than this is a null testing something the statistic does not
    vary over.
    """
    rng = random.Random(seed)
    cells = cells_of(sides, families)
    return statistics.stdev(
        dod({c: [rng.choice(groups[c]) for _ in groups[c]] for c in cells},
            sides, families)
        for _ in range(draws))


def widths(groups, sides, families, seed):
    samp = sampling_sd(groups, sides, families, seed)
    return samp, [null_sd(groups, sides, families, seed, sh) / samp
                  for _, sh in SHUFFLES]


def draw(groups, sides, families, means, rng, factor):
    """One dataset at the given cell means, with `factor` injected.

    Residuals are resampled within their own cell with replacement, so the
    per-cell spread is the observed one. `factor` multiplies the treated cell -
    the second side crossed with the second family - which on a log scale is an
    added `log(factor)` and is the interaction the test has to find.
    """
    treated = (sides[1], families[1])
    out = {}
    for c in cells_of(sides, families):
        base = sum(groups[c]) / len(groups[c])
        resid = [v - base for v in groups[c]]
        shift = means[c] + (math.log(factor) if c == treated else 0.0)
        out[c] = [shift + rng.choice(resid) for _ in groups[c]]
    return out


def rates(groups, sides, families, factor, seed, draws=DRAWS, resamples=RESAMPLES):
    """Rejection rate of each of the three tests at `factor`."""
    rng = random.Random(seed)
    means = metrics.additive_fit(groups, sides, families)
    hits = {name: 0 for name, _ in SHUFFLES}
    for i in range(draws):
        d = draw(groups, sides, families, means, rng, factor)
        for name, sh in SHUFFLES:
            if permutation_p(d, sides, families, seed + i, sh, resamples) < ALPHA:
                hits[name] += 1
    return [hits[name] / draws for name, _ in SHUFFLES]


def synthetic(side_gap, family_gap, rng, n=30, sd=0.5):
    """Four cells with known gaps and no interaction at all."""
    sides, fams = ("c", "e"), ("A", "B")
    return sides, fams, {
        (s, f): [(side_gap if s == "e" else 0.0)
                 + (family_gap if f == "B" else 0.0) + rng.gauss(0, sd)
                 for _ in range(n)]
        for s in sides for f in fams}


def load(name, snap, treatment, reference):
    groups = log_cells(SNAPS / snap, treatment, reference)
    if groups is None:
        print("%-30s  unreadable: a cell is empty or a run scored zero words" % name)
    return groups


def row(label, samp, ratios):
    print("%-30s %9.3f %9.1fx %9.1fx %9.1fx"
          % (label, samp, ratios[0], ratios[1], ratios[2]))


def main():
    archive_only = "--archive" in sys.argv

    if not archive_only:
        print("## 1. The defect is symmetric: three nulls over the sampling spread")
        print("%-30s %9s %10s %10s %10s"
              % ("synthetic cells", "sampling", "legacy", "family", "residual"))
        rng = random.Random(SEED)
        for label, sg, fg in (("side gap 2.0, family gap 0", 2.0, 0.0),
                              ("side gap 0, family gap 2.0", 0.0, 2.0),
                              ("neither gap", 0.0, 0.0)):
            sides, fams, g = synthetic(sg, fg, rng)
            row(label, *widths(g, sides, fams, SEED))

        print("\n## 2. The same three on every stored arm-label interaction")
        print("%-30s %9s %10s %10s %10s"
              % ("interaction", "sampling", "legacy", "family", "residual"))
        for name, snap, treatment, reference, _ in ARCHIVE:
            groups = load(name, snap, treatment, reference)
            if groups is None:
                continue
            row(name, *widths(groups, SIDES, (reference, treatment), SEED))

        name, snap, treatment, reference, _ = ARCHIVE[0]
        groups = load(name, snap, treatment, reference)
        fams = (reference, treatment)
        print("\n## 3. Calibration and power on %s, %d draws of %d resamples"
              % (name, DRAWS, RESAMPLES))
        print("   band fixed for the false-positive rate: [%.3f, %.3f]" % FPR_BAND)
        print("%9s %11s %11s %11s" % ("factor", "legacy", "family", "residual"))
        for factor in POWER_FACTORS:
            leg, fam, res = rates(groups, SIDES, fams, factor, SEED)
            tag = "  <- the null" if factor == 1.0 else ""
            print("%9.2f %11.3f %11.3f %11.3f%s" % (factor, leg, fam, res, tag))

    print("\n## 4. The archive, 200000 resamples, each row at its round's seed")
    print("%-26s %9s %11s %11s"
          % ("interaction", "ratio", "legacy p", "corrected p"))
    for name, snap, treatment, reference, seed in ARCHIVE:
        groups = load(name, snap, treatment, reference)
        if groups is None:
            continue
        fams = (reference, treatment)
        leg = permutation_p(groups, SIDES, fams, seed, shuffle_side, 200000)
        cor = metrics.interaction_permutation(groups, SIDES, fams, seed)
        print("%-26s %8.3fx %11.4f %11.4f"
              % (name, math.exp(dod(groups, SIDES, fams)), leg, cor))


if __name__ == "__main__":
    main()
