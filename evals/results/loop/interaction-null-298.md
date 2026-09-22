# The interaction null, corrected (#298)

**This is an instrument correction, not a round.** It proposes no rule edit,
buys no generation and moves no ledger row. `rules/laconic.md` is untouched and
`bash tools/candidate-due.sh` is unaffected, because no round document is added.

[Round 69](round-69.md) named it and said where it belongs:

> A paired or stratified interaction statistic — the bootstrap used here, or a
> within-stem pairing — is a harness change of maybe fifty lines and it would
> re-decide, cheaply, several rounds' worth of stored interaction nulls. **That
> is a backlog issue, not a round.**

[`over-length-cluster.md`](over-length-cluster.md) carries the same sentence in
its own words: *"Several stored interaction nulls bound less than they appear
to, and re-deciding them is a harness change rather than a round."*

Reproduce every number below with:

```sh
python3 evals/pilot/interaction_calibration.py
```

## The defect

Three pilot scorers test a 2x2 interaction on log prose words — a difference of
differences over the four cell means:

    DoD = (mean[L,B] - mean[L,A]) - (mean[C,B] - mean[C,A])

`A` and `B` are two case families; `L` and `C` are the two sides, which on
`score_register.py` are the two **arms** and on `score_persistence.py` and
`score_reexplain.py` are two **rules revisions**. All three built the null by
shuffling the **side** label inside each family.

That is wrong whenever the side carries a main effect. On the arm scorers the
arms sit about **8x apart** in words, so every shuffled group is a 50/50
mixture of two well-separated modes and the null inherits a spread the
statistic itself does not have. Round 69 measured it at **1.9x the sampling
distribution of the statistic under test**, on both of its families. Round 42
had already recorded the raw-word version of the same defect; what round 69
added is that moving to a log scale does not escape it.

## The correction, and the repair that is not one

**The obvious repair fails, and it fails symmetrically.** Shuffling the family
label instead of the side label does not remove the inflation; it moves it onto
the family's main effect. Section 1 below measures that on synthetic cells
where the answer is known in advance, and section 2 confirms it on the real
ones. Both labels carry main effects on every pilot here, so neither shuffle is
safe.

`metrics.interaction_permutation` therefore builds the null from residuals that
carry neither. It fits the additive model — grand mean plus a side effect plus
a family effect, which is the four cell means with the interaction removed —
and shuffles those residuals across all four cells. Under the null of no
interaction the additive model is correct, so its residuals are exchangeable
across every cell, and the fitted part contributes exactly zero to a difference
of differences. **The statistic is unchanged and so is the bootstrap interval
printed beside it.** Only the way the null is built moves.

**It holds on a log scale and not on raw counts**, because pooling residuals
assumes comparable within-cell spread, which logged words give and word counts
do not. The raw-word line stays in the scorers' output because the rounds that
registered it printed it, and it is still the broken one round 42 described.

## What `tools/consult.sh` said, and the one place the measurement overruled it

Asked with the defect, the design I was leaning towards, and the four things I
was least sure of. **`codex` did not answer** — it timed out at 240s.
`deepseek` read the two scorers; `kimi` answered from the description, its
workspace being empty.

**Overruled by measurement: both targets endorsed the family shuffle, and it is
wrong.** `deepseek`'s argument was that the nuisance is already differenced
out —

> The family main effect that the within-arm shuffle destroys cancels in the
> DoD by construction […] the shuffle regenerates gaps centered at 0 with the
> same within-arm variance, and variance is location-invariant, so the null DoD
> distribution matches the sampling distribution.

— and `kimi` reached the same conclusion independently, calling the family
shuffle "the correct restricted permutation for an interaction in a 2×2
layout". The first half is right: the statistic does difference out both main
effects. The second half does not follow, and section 1 is the counterexample.
Pooling two groups that a gap `g` separates and splitting them at random
produces a gap whose variance carries a term in `g`, so the shuffle *recreates*
the destroyed main effect as noise. It is the same mechanism as the defect,
pointed at the other label.

Both targets also told me to drop the align-and-permute scheme my draft
carried — `deepseek`: *"Align-and-permute and the studentized bootstrap exist
for statistics that don't already difference out the nuisance"* — and that is
the scheme this unit shipped. The advice was consistent and it was checkable,
so it was checked.

**Adopted, from both: do not block on stem.** Three fixture stems are crossed
identically into both families and both arms, so the stem effect already
cancels inside the DoD. The three-stem paired test is dead on arrival for the
reason `score_reexplain.py` already records — the minimum two-sided sign-test
p over three cells is 0.25.

**Adopted, from `deepseek`: name the relabel `unresolved`, not `undecided`.**

> Do not reuse "undecided": that already means "buy a second grading pass" in
> the judge-noise gate.

Correct, and it is the kind of collision that is invisible until someone reads
two documents together. `report.py --judge-noise-gate` exits 2 with `undecided`
and that vocabulary is spoken for.

**Adopted, from `kimi`: publish the archive as a table that never overwrites
the registered verdict column.** The table in section 4 has that shape.

**Adopted, from `deepseek`: run the calibration on both tests, not just the new
one.** *"old FPR ≈ 0 (it under-rejects), new ≈ alpha"* was a prediction, and
section 3 is it tested. It is worth having because "conservative" is the
charitable reading of a wide null, and a measured false-positive rate is what
separates a conservative test from one that cannot reject at all.

## The specification

Fixed before the calibration ran, and all of it is in
`evals/pilot/interaction_calibration.py`:

- **The test.** Fit the additive model on logged prose words, shuffle its
  residuals across all four cells preserving cell sizes, recompute the
  difference of differences. 200,000 resamples, two-sided, at the seed the
  round being recomputed passed.
- **The calibration bar.** The false-positive rate under a constructed true
  null must lie in `FPR_BAND` = [0.035, 0.065] at alpha 0.05, about two
  standard errors either side at 1000 draws.
- **The power points.** 1.00x (the null), 1.25x, 1.50x, 1.75x, 2.00x.
- **The null construction.** The four observed cell means are replaced by their
  additive fit, so the true interaction is exactly zero while the side gap, the
  family gap and every cell's spread stay the ones the instrument produced.
  Residuals are resampled within their own cell, so a noisier cell stays
  noisier.

## The disclosure rule

**A recomputed p may relabel a stored null `unresolved`. It may not restate a
round's verdict, and no ledger row moves.**

`unresolved` means *the registered test could not have decided this, so that
round did not measure its interaction*. It is an invitation to buy a fresh
pre-registered round, not a result. The round's own verdict column stands as
registered.

---

# Results

## 1. The defect is symmetric

*Synthetic cells, 30 a cell, no interaction, gaps known in advance. Each null's
standard deviation as a multiple of the sampling standard deviation of the same
statistic, which is what the data actually carry.*

| synthetic cells, 30 a cell | sampling sd | legacy (side) | family | residual |
|---|--:|--:|--:|--:|
| side gap 2.0, family gap 0 | 0.177 | **2.2x** | 1.0x | 1.0x |
| side gap 0, family gap 2.0 | 0.174 | 1.0x | **2.3x** | 1.0x |
| neither gap | 0.165 | 1.0x | 1.0x | 1.0x |

**Whichever label is shuffled, that label's main effect inflates the null.**
The two rows are mirror images, and only the aligned residuals are the right
width in both. This is the finding that decided the implementation, and it is
the one the two consulted targets got wrong.

## 2. The same three on the stored interactions

| interaction | sampling sd | legacy (side) | family | residual |
|---|--:|--:|--:|--:|
| `register-inheritance-136` | 0.122 | **2.8x** | 1.2x | 1.1x |
| `round-67` | 0.101 | **2.7x** | 1.1x | 1.0x |
| `round-69 deepexplain` | 0.243 | **1.9x** | 1.0x | 1.0x |
| `round-69 fullexplain` | 0.220 | **1.9x** | 1.1x | 1.0x |

Round 69's 1.9x reproduces exactly, and the two `deep`-family pairs are worse
at 2.7x and 2.8x — their arms are further apart. The family shuffle is close to
right *here* only because these instruments pair families whose own gap is
small; section 1 is what says not to rely on that.

## 3. Calibration and power

*Constructed true null on `register-inheritance-136`'s own cells, 1000 draws
of 1000 resamples. The `factor` column is the interaction injected into the
treated cell, so 1.00 is the false-positive rate.*

| factor | legacy (side) | family | residual |
|---|--:|--:|--:|
| **1.00 — the null** | **0.000** | 0.039 | **0.059** |
| 1.25 | 0.003 | 0.320 | 0.445 |
| 1.50 | 0.066 | 0.845 | 0.916 |
| 1.75 | 0.502 | 0.992 | 0.996 |
| 2.00 | 0.895 | 0.999 | 1.000 |

**The legacy test's false-positive rate is 0.000 in a thousand draws.** That is
not a conservative test, it is a test that cannot reject: at alpha 0.05 it fires
on nothing, and it needs an interaction near **1.75x** before it detects one
half the time. The corrected test sits at 0.059, inside the registered
[0.035, 0.065] band, and detects 1.50x at 0.916 where the legacy test detects it
at 0.066.

So the reading a stored arm-label null supports is much weaker than it looks. A
null from that test rules out roughly nothing below 1.75x.

## 4. The archive

*Every stored interaction, 200,000 resamples, each row at the seed its round
passed — so the legacy column reproduces what that round printed. The registered
verdict column is the round's own and is not restated.*

| interaction | ratio of ratios | registered reading | legacy p | corrected p | relabel |
|---|--:|---|--:|--:|---|
| `register-inheritance-136` | 1.782x | post-hoc, "closer, still not clearing" | 0.0844 | **0.0000** | **unresolved** |
| `round-69 fullexplain` | 1.484x | null; movement read as the case, not the rules | 0.3375 | 0.0737 | unchanged |
| `round-69 deepexplain` | 0.929x | null | 0.8725 | 0.7638 | unchanged |
| `round-67` | 1.015x | null | 0.9559 | 0.8840 | unchanged |
| `round-47` | 0.904x | null | 0.5402 | 0.5369 | unchanged |
| `round-49` | 1.109x | null | 0.5203 | 0.5184 | unchanged |
| `round-68` | 0.988x | null | 0.9430 | 0.9423 | unchanged |

The last three rows are the rules-revision pilots, recomputed by running
`score_persistence.py` and `score_reexplain.py`, which now print the corrected
line themselves. **They move by less than 0.004.** Their two sides are two rules
revisions rather than two arms, so the label being shuffled carries almost no
main effect and the legacy null was the right width by accident. Rounds 47, 49
and 68 are unaffected, and that is worth stating as plainly as the row that
moves: the defect is a property of the arm instrument, not of every interaction
this loop has run.

## What this changes

**One stored interaction is relabelled, and it is the one whose own document
already said the test was broken.** `register-inheritance-136` registered its
interaction on raw words, disclosed that as its own design error — *"the
registration should have specified the interaction on the log scale"* — and
reported the log-scale figure as post-hoc at p = 0.0844, *"closer, still not
clearing"*, explicitly not leaned on. Under a correctly sized null the same
figure reads **p < 0.00001 at 1.782x**. It remains post-hoc, so it becomes no
one's registered finding; what changes is that the pilot's registered arbiter is
now known to have been incapable of clearing anything, which is a stronger
statement than "it failed". The conclusion that pilot reached rests on its
control's own null — the baseline arm does not rise, p = 0.9135 — and the
corrected interaction agrees with it rather than replacing it.

**Round 69's interaction is not rescued.** 0.3375 to 0.0737 is a large move and
it does not cross alpha. Round 69's branch-2 reading stands unchanged: the
register effect moves the baseline arm too, so the movement is the case rather
than the rules. The round's disclosure that its registered control "was too
blunt to say more" is now quantified — blunt enough to have a false-positive
rate of zero — and the reading it licensed is the same one.

**What the cluster's stored nulls bound, restated.** Round 69 wrote that
"several stored interaction nulls bound less than they appear to". With the
detection curve measured, the figure is: an arm-label null bounds the
interaction below about **1.75x**, not below the 1.2x a reader would assume
from a p near 1. Three of the four arm-label rows sit at ratios of 0.93x to
1.02x, so nothing about them changes; the one at 1.48x is the one that was
being bounded on a promise the test could not keep.

**Going forward, `metrics.interaction_permutation` is the instrument.** The
three scorers print it beside the test their rounds registered, and the legacy
function stays only so a stored verdict remains recomputable from the code that
produced it. A new round registers against the corrected one.

## Disclosures

- **The ordering is honest but not ideal, and here is exactly what it was.**
  The specification and the calibration bars were fixed in
  `interaction_calibration.py` before any calibration ran, and git dates the
  commit. **Section 4's archive table was computed during development, before
  this document existed.** What keeps that from being a forking path is that
  the choice of implementation was decided by section 1, on synthetic cells
  whose answer is known in advance and which contain no archive data at all —
  and that the direction of the correction was settled by round 42 and round 69
  before this unit started. The disclosure rule was written down before the
  relabel was applied; it was not written before the numbers were seen.
- **The residual permutation pools residuals across cells**, so it assumes
  comparable within-cell spread. That is why callers pass logged words, and at
  equal n — 30 a cell throughout — a permutation test is level-robust to the
  spread that remains. On raw counts the assumption fails and the test is not
  offered there.
- **The corrected false-positive rate is 0.059, at the upper half of the
  band.** 1000 draws resolve a rate to about ±0.007, so it sits roughly 1.3
  standard errors above 0.05. Inside the bar, and not centred on it.
- **The calibration is on one instrument's cells.** `register-inheritance-136`
  has the widest legacy null of the four, which makes it the hardest case for
  the legacy test and the easiest place to see the difference. A cell geometry
  with a much smaller side gap would show a smaller gap between the two tests,
  which is what rounds 47, 49 and 68 demonstrate in section 4.
- **No verdict moves and no ledger row moves.** `LEDGER.md` gains a prose note
  after the table, in the place its other instrument corrections live.
- **Nothing regenerates.** No snapshot is rewritten and no case is touched, so
  `cases_cksum` and `rules_cksum` are untouched everywhere.

[#42]: https://github.com/JordanMPDS/laconic/issues/42
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#298]: https://github.com/JordanMPDS/laconic/issues/298
