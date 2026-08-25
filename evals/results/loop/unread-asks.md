# `unread_asks`: the archive re-score

Working notes for [#146]. Establishes what the counter reads across every
stored round **before** it is allowed to gate anything, which is the sequence
[#49] followed for `turns`.

## What it counts

An answer that handed the decision back **and** never opened a file: the
intersection of `ASKS_BACK` and `num_turns == 1`. Both facts are already on
every stored run, so the whole re-score below is offline and cost no
generations.

It is a **subset of `one_turn`**, and it carries `one_turn`'s exposure and its
fixture-only filter for that reason. A case with no `fixture/` directory is
one-turn by construction, so every question it asks would count here
spuriously.

**The detector is `_quality_strata`'s, unmodified.** Two counters reading one
behaviour through two regexes would drift, and re-tuning a detector after
seeing what it found is how a disclosure becomes a story. Its known limits are
in the open questions below.

## Why not just use `one_turn`

`one_turn` counts every answer that opened no file, whether or not it then
handed the decision back. Round 26 measured the difference directly:

| round 26, licence arm | failed |
|---|--:|
| hands back, read the repository | **0/6 (0%)** |
| hands back, did not read | **12/22 (55%)** |

Round 27 rejected an edit on the proxy at p = 0.151 while the effect it was
aiming at moved at p = 0.044 on this intersection.

## Independence rules, applied before any statistic

- `round-01-n10`, `-v2` and `-v3` are prefixes of `-v4`. Only `-v4` is counted.
- `round-21` (n=5) and `round-22` (n=5) are subsets of their own `-n10` files.
  Only the `-n10` files are counted.
- **Arbitration snapshots are excluded.** An arbitration regenerates only the
  cells that rose, so it is a biased subset by construction and cannot serve as
  a random redraw. `round-25-arbitration` and `round-10-replication` are out.

## Between-round dispersion at identical rules text

Comparing only rounds that share a `rules_cksum` **and** a case-scope size:

| rules text | scope | rounds | pooled | chi2 | df | phi |
|---|--:|--:|--:|--:|--:|--:|
| 1497646142 | 8 | 2 | 2/160 | 2.03 | 1 | 2.03 |
| 1823644123 | 3 | 2 | 3/60 | 0.35 | 1 | 0.35 |
| 1830906901 | 3 | 2 | 6/105 | 0.44 | 1 | 0.44 |
| 1830906901 | 8 | 4 | 13/560 | 9.84 | 3 | 3.28 |
| 3694954268 | 8 | 6 | 75/800 | 4.25 | 5 | **0.85** |
| 3980812364 | 3 | 3 | 8/90 | 3.57 | 2 | 1.78 |
| 3980812364 | 5 | 2 | 11/100 | 0.10 | 1 | 0.10 |
| **pooled** | | **19** | | **20.58** | **14** | **1.47** |

**phi = 1.47**, against `ONE_TURN_PHI` = 3.39 for the counter it is a subset
of. Chi-square 20.58 on 14 df is p ≈ 0.11, so the archive does not show
significant overdispersion at all — the point estimate is the honest number to
carry, not evidence of a problem.

The best-populated group is the most reassuring: six independent rounds of the
current master text, 800 runs, **phi = 0.85** — no overdispersion above
binomial.

## The false-accept rate matches nominal alpha

A target must *improve* to clear, so the failure mode is a gate that passes on
noise. Every ordered pair of rounds at identical rules text and identical
scope, scored one-sided at alpha 0.05:

**3 of 56 pairs reach alpha (5.4%), against a nominal 5%.** Inflating at
phi = 1.47 leaves it at 3 of 56.

All three involve `round-26-control` reading **0/200**, and that zero is real
rather than an artifact: every one of its 200 runs carries text, 66 of them are
one-turn, and the pre-licence rules simply produced 6 questions in 200 with
none in a one-turn answer.

**The honest caveat is era, not sampling.** The 1830906901 group spans
2026-07-31 to 2026-08-24 — the same window in which `terse-control`'s one-turn
rate moved 4/40 to 11/40 with nothing changed but the calendar and the CLI. All
three false accepts are cross-era pairs, so 5.4% is if anything an
over-estimate of the sampling component.

## It separates the rules texts the loop has already judged

Eight-case design scope, sonnet:

| rules text | | rate |
|---|--:|--:|
| round 20's edit (3980812364) | 15/80 | **18.8%** |
| the licence, current master (3694954268) | 75/800 | **9.4%** |
| round 27's edit (136269960) | 9/200 | **4.5%** |
| round 18's edit (4146642931) | 2/80 | 2.5% |
| round 19's edit (2970727293) | 2/80 | 2.5% |
| pre-licence (1830906901) | 13/560 | **2.3%** |
| round 16/17's edit (1497646142) | 2/160 | 1.2% |
| round 22's edit (2192107416) | 0/80 | 0.0% |

- pre-licence to licence: **p = 8.0e-08**. This is round 26's disclosed
  composition effect, read directly by a counter instead of inferred from a
  stratum split.
- licence to round 27's edit: **p = 0.018**, on 800 runs against 200 rather
  than round 27's own 200 against 200.
- Round 20's edit sits highest of all eight texts at 18.8%, p = 0.016 against
  master. Round 20 was never scored on this behaviour.

## Open questions before this gates anything

1. **The detector is crude and this is its weakest point.** `ASKS_BACK` is
   `^[^\n]*\?\s*$` — any line that is a whole question. It cannot separate
   "which monitoring stack do you run?", a fork reading cannot settle, from
   "is there a logged-in state on these pages?", which the fixture answers.
   That distinction is the entire point of the metric. Validating it needs
   hand-labelled responses, and the labels must be assigned blind to the
   detector's verdict and never against round outcomes.
2. **Target-only, and it stays that way for now.** The archive null above is
   about false *accepts*. Making it fatal asks a different question — the false
   *rejection* rate — and that has not been measured.
3. **Whether the era confound needs its own correction.** Three of three false
   accepts are cross-era. A within-era estimate needs rounds close in time at
   fixed rules text, which the archive has few of.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#146]: https://github.com/JordanMPDS/laconic/issues/146
