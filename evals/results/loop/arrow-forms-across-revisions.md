# Arrows do not relocate, and the forms do not trade

**Date:** 2026-08-13
**For:** [#34], and a correction to [`round-18.md`](round-18.md)
**Cost:** zero calls. Every number is computed from committed snapshots.

## What this was meant to settle

The [#34] design registered a round targeting the two-term mapping form, on the
strength of one observation: across rounds 16, 17 and 18 the chain form fell and
the mapping form rose. Two readings were possible and three rounds could not
separate them. Either the forms **trade** — pressing on chains produces mappings,
which would make the proposed round unwinnable by construction — or mappings are
**unruled and drifting**, which would make it a fair test.

The same split can be computed on every laconic response this repository has
committed, at every rules revision, for nothing. That is 6,434 responses after
deduplication by text, 288 case/model/revision points at n ≥ 10, and 15 rules
revisions rather than four.

**Neither reading survived, and the observation that motivated them was an
artifact.**

## 1. The forms do not trade

Within each case/model cell, across the revisions that cell was measured under —
which removes the case effect, the dominant confounder, since `walkthrough` is
arrow-heavy at every revision and `conditional` produces no chains at any:

| | |
| --- | --: |
| cells measured under three or more revisions | 44 |
| observations in those cells | 264 |
| correlation of chain rate with mapping rate | **+0.153** |
| permutation p, negative direction | 0.988 |
| permutation p, positive direction | **0.012** |

Trading predicts a negative correlation. The measurement finds a small
**positive** one, significant in that direction.

The variance decomposition says the same thing. If the forms traded, the total
would vary less than its parts:

| | per response |
| --- | --: |
| variance of chain deviations | 0.0366 |
| variance of mapping deviations | 0.0115 |
| sum, if independent | 0.0481 |
| **observed variance of the total** | **0.0544** |
| ratio | **1.13** |

Trading predicts a ratio well below 1. It is slightly above.

## 2. Mappings are not rising

Over the 28 cells common to all seven revisions measured at 20 or more cells:

| `rules_cksum` | chains/response | mappings/response | total | runs |
| --- | --: | --: | --: | --: |
| **1830906901 (master)** | **0.129** | **0.060** | **0.188** | 839 |
| 4146642931 (round 18) | 0.097 | 0.059 | 0.156 | 320 |
| 1497646142 (rounds 16, 17) | 0.082 | 0.065 | 0.147 | 558 |
| 3980812364 (rounds 10, 12, 14, 15) | 0.075 | **0.033** | 0.108 | 1317 |
| 1264799532 (round 07) | 0.075 | **0.025** | 0.100 | 280 |
| 3956310624 (round 11) | 0.071 | 0.032 | 0.104 | 280 |
| 1823644123 (rounds 08, 09) | 0.048 | 0.055 | 0.104 | 560 |

**One of six revisions has a mapping rate above master's**, by 0.005. The
relocation edit nearly halved mappings, 0.060 to 0.033, and round 07's edit put
them at 0.025.

Every revision lowers the total arrow rate, master being the worst of the seven.

## 3. Where the apparent rise came from

The rise is real on the 22-case set and it is not distributed. Round 18 against
the `-v4` baseline, per cell:

| | net change in mappings |
| --- | --: |
| cells in the original 14-case set | **−12** |
| cells added since | **+34** |

and the added cells are dominated by two whose baseline draw was low against
independently measured master-rules runs:

| cell | `-v4` baseline | independent master-rules (n = 30) | round 18 |
| --- | --: | --: | --: |
| `design-cache`/haiku | 0.20 | **0.83** | 1.20 |
| `design-upload`/sonnet | 0.00 | **0.43** | 0.50 |

`design-cache`/haiku alone accounts for +10 of the +34. Its baseline drew 0.20
mappings per response where 30 independent master-rules runs give 0.83, and
round 18's 1.20 is a modest step above master's real rate rather than a jump
from near zero.

This is the same low-baseline artifact recorded in [#103]: on those six design
cells the `-v4` baseline's total violations sit at the 3rd percentile of what
master rules actually produce.

## The correction to round 18

[`round-18.md`](round-18.md) and its pull request both state that the arrows
relocated from list items into running prose, and quantify it as "sixteen of the
twenty-six arrows that left a list item reappeared in a sentence".

**That is wrong, and the error is mine.** I computed the position table with a
line-level regex for `→` and `->` instead of the detector's own hits. The
detector exempts quoted numeric progressions such as `7 → 11 → 14`, and
`violations_total` has never counted them.

| position | baseline | round 18 | |
| --- | --: | --: | --- |
| bullet item | 50 | 37 | −13 |
| numbered list item | 42 | 29 | −13 |
| **running prose** | **48** | **45** | **−3** |
| total | 140 | 111 | −29 |

**Arrows fell in every position.** Nothing relocated. The apparent rise in prose
— 76 to 92 under the raw scan — is entirely a rise in quoted numeric
progressions, which are not violations and never were.

What round 18 actually established about position is stronger than what it
claimed: its edit lowered arrows everywhere, and most in the position it named.

## What this means for [#34]

[#34]'s founding observation is that rounds 01 and 03 each fixed the position
they named and each saw arrows appear where the other edit had been pointing. It
concluded that an enumeration is beatable by finding position *n+1*.

**Six rules revisions and 6,434 responses do not show that happening.** Arrows
fall in every position under every revision, the two forms move weakly together
rather than trading, and the apparent counter-example was a low baseline draw on
three cases that did not exist when [#34] was written.

Three consequences:

1. **The registered [#34] round should not run as designed.** Its target was the
   mapping form, chosen because mappings looked like a growing unruled residual.
   They are not growing. An edit aimed at them would be aimed at 0.06 arrows per
   response that six revisions have already moved as low as 0.025.
2. **The open question is not the rule's form.** Every revision tested lowers
   arrows, some by more than half. Nine rounds have been rejected on other
   counters. The arrow rule is not what is failing.
3. **[#34]'s bullet 3 gets an answer.** It asked whether rounds would continue
   relocating arrows indefinitely, which would say the enumeration cannot close.
   They do not relocate. The bar of zero per cell remains unreached in
   aggregate, but not for the reason [#34] proposed.

## Method

`evals/bench/metrics.py:arrow_forms`, shipped in
[#106](https://github.com/JordanMPDS/laconic/pull/106), applied to every
committed snapshot carrying a `rules_cksum` and a laconic arm. Responses are
deduplicated by text within a cell and revision, because several snapshots carry
each other's runs. A point needs 10 runs to be counted, and a cell needs three
revisions to enter the correlation. Correlations use within-cell deviations and
a 20,000-draw permutation test; no dependency was added.

[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#103]: https://github.com/JordanMPDS/laconic/issues/103
