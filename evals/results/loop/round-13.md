# Round 13 — the judge is steadier than predicted, and the noise is upstream of it

**Date:** 2026-08-10
**Rules under test:** none. `rules_cksum` 1830906901, unchanged from master.
**Subject:** `evals/snapshots/loop/round-12.json`, laconic arm, 340 responses
**Round artefacts:** `evals/snapshots/loop/round-12-judgments-b.json`
**Result:** the pre-registered hypothesis is **refuted**, and the reason is
worth more than the hypothesis was

This is an instrument round. It changes no rule, targets no case, and can
neither accept nor reject an edit. It takes no ledger row of the usual kind.

## Hypothesis (registered in `4129515`, before the round ran)

> Re-judging round 12's 340 laconic responses a second time, under identical
> case criteria and the same judge model, yields a verdict-agreement rate below
> 100%. The resulting per-counter noise floors for `quality_fails` and
> `safety_fails` are large enough that round 12's observed safety rise of 6 to
> 15 lies inside the floor for `safety_fails`.

The decision rule, fixed in the same commit: if the floor covers +9,
`safety_fails` cannot distinguish an edit effect from judge variance and needs a
noise gate. If it does not, round 12's rejection stands on its own terms.

**The floor does not cover it.** The first clause holds and the second fails.

## What the second grading found

340 responses, byte-identical, same criteria, same judge model, 0 infra
failures on either side.

| | |
| --- | --: |
| verdict agreement | 322 of 340 (**94.7%**) |
| `pass` → `fail` | 8 of 254 (3.1%) |
| `fail` → `pass` | 7 of 81 (8.6%) |
| `fail` → `not_exercised` | 2 |
| `not_exercised` → `fail` | 1 |

Self-disagreement is **5.3%**, 95% CI [3.4%, 8.2%].

## [#70]'s extrapolation was wrong by about four times

[#70] estimated this from the carried control arm, where 415 byte-identical
responses graded twice disagreed 9.6% of the time. Applied to a 6-in-100 safety
baseline, that predicted a re-grade would read about 14 with sd 2.9.

The laconic arm is measurably steadier than the control arm: 18 of 340 against
40 of 415, **Fisher p = 0.028**. The caveat filed with [#70] — that the flip
rates came from control responses and a very different pass/fail mix — was the
right caveat, and it mattered more than the direction did.

| | predicted from controls | measured on laconic |
| --- | --: | --: |
| `pass` → `fail` | 8.8% | **3.1%** |
| `fail` → `pass` | 12.0% | **8.6%** |
| expected `safety_fails` drift | +7.5 | **+1.4** |
| sd | 2.9 | **1.9** |

## The counters under two gradings of the same responses

| counter | baseline | grading A | grading B | B − A |
| --- | --: | --: | --: | --: |
| `quality_fails` | 41 | 39 | 38 | −1 |
| `safety_fails` | 6 | 15 | 12 | **−3** |

| safety cell | baseline | A | B |
| --- | --: | --: | --: |
| `destructive`/sonnet | 3 | 7 | 6 |
| `ordered-steps`/haiku | 2 | 5 | 4 |
| `ordered-steps`/sonnet | 1 | 3 | 2 |

From the measured transition rates, a re-grade of a fixed set of responses moves
`safety_fails` by a net +1.4 with sd 1.9 — **a two-sigma band of about ±4** —
and `quality_fails` by +1.1 with sd 2.7, about ±5.

Round 12's rise was +9. It is outside the judge's band. The hypothesis is
refuted, and I am recording that plainly because it was registered before the
numbers existed and the loop is worth nothing if a refuted prediction gets
quietly reframed.

## But the gate is still not measuring the edit

The refutation narrows the problem rather than dissolving it. Two facts sit
beside each other:

- **Same rules, different generations:** round 10 read `safety_fails` 7 and
  round 12 read 15. That is +8, from byte-identical rule text.
- **Same responses, different gradings:** 15 and 12. That is −3, inside a ±4
  band.

So the judge accounts for roughly a third of the movement between two rounds of
identical rules, and **generation sampling accounts for the rest.** The noise is
mostly upstream of the judge, in which responses the model happened to produce.

That is a different fix from the one [#70] proposed. A floor built by re-judging
fixed responses would be too small — about ±4, where the observed
same-rules movement is 8. What the gate needs is a floor built from repeated
*generations* under fixed rules, which is exactly what [#66] already does for
`never_cut_failures`: measure a cell's failure rate under master rules at n = 40
and screen a risen cell against its own rate.

The three cells that rejected round 12 are the obvious candidates:

| cell | baseline | r10 | r11 | r12 | measured rate? |
| --- | --: | --: | --: | --: | --- |
| `destructive`/sonnet | 3 | 4 | 4 | 7 | no |
| `ordered-steps`/haiku | 2 | 2 | 5 | 5 | no |
| `ordered-steps`/sonnet | 1 | 1 | 5 | 3 | no |

`ordered-steps`/haiku alone has read 2, 6, 3, 5, 2, 5, 5 across the baseline and
six rounds, under three different rule texts. Measuring it at n = 40 under master
rules costs about 40 generation calls plus 40 judge calls, and would tell the
gate what that cell does when nothing is being tested.

## What this round settles

1. **The judge is reliable enough to keep.** 94.7% self-agreement on identical
   text, and the two counters move by ±4 and ±5 at two sigma under re-grading.
   That is a real limitation but it is not the one that has been rejecting
   rounds.
2. **[#70]'s headline is wrong and its method was right.** Extrapolating the
   control arm's flip rates onto the laconic arm overstated the effect four-fold.
   The issue's own caveat named the risk; the measurement it asked for is what
   corrected it.
3. **The next instrument step is per-cell generation rates for the safety
   cells**, not a judge-noise floor. [#66]'s machinery already exists and
   `cell-rates.json` already has a `never_cut_failures` section to sit beside.

## What it does not settle

The re-grade is one draw. 94.7% agreement has a 95% interval of [3.4%, 8.2%] on
the disagreement rate, so the ±4 band on `safety_fails` is itself uncertain at
the edges. A third grading would tighten it, and is not worth 340 calls: the
conclusion — that judge variance is the smaller term — holds across the whole
interval.

Nor does it revisit round 12's verdict. Round 12 rejected on `safety_fails`
6 to 15, and this round shows the judge did not produce that movement. The
rejection stands as recorded. What is now in question is whether the *gate*
should have fired, which is a question about `safety_fails`' floor and not about
round 12's grading.

[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#70]: https://github.com/JordanMPDS/laconic/issues/70
