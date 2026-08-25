# The token target scored the marginal median, which pays for not reading

**Date:** 2026-08-25
**Issue:** [#131]
**Cost:** no generations. Every number below is computed from stored snapshots.
**Code:** `_stratum_of`, `_stratum_tokens`, `_counterfactual_line` and
`_stratum_note` in `evals/bench/report.py`, gated by `GROUNDED_MIN_RUNS`.

## The defect

`output_tokens` was scored as the per-cell median over every run in the cell,
whether or not the answer opened a file. Round 23 measured that reading is the
axis: pooled over 150 verdicts, answers that read the repository failed quality
4 of 93 and answers that did not failed 55 of 57, Fisher **p = 1.5e-33**. An
answer that never opened a file is also several times shorter than one that
did.

So the median moves when the *mix* moves. An edit that suppresses reading
shortens the marginal median without compressing a single sentence, and the
gate could not tell the two apart. Every token target the loop has scored
across 26 rounds was read off that statistic.

## The fix: every voting cell is compared inside one stratum

A cell is split on `num_turns`, the same proxy the `one_turn` counter uses: an
answer that called no tool never opened a file.

| the cell's two rounds | how it votes |
| --- | --- |
| both have a grounded stratum | grounded medians |
| neither has one | unread medians |
| one has one and the other does not | **it does not vote**, and is named |

The third row is the defect itself. When a cell reads 6 of 10 in the control
and 1 of 10 in the round, its grounded median has nothing to be compared
against, and the marginal comparison it used to cast is exactly the mix-shift
this issue is about. It is refused rather than approximated, and the verdict
prints the cell and both reading rates.

The second row is what keeps the rest of the benchmark working. Four cases have
no fixture directory, so every one of their answers is unread by construction;
they have no mix to shift, their marginal median *is* their within-stratum
median, and nothing about them changes.

The floor follows the statistic, the way [#51] made it follow the shift: it is
built from the dispersion of the stratum the cells voted in. That is a smaller
number than the marginal dispersion, because the marginal spread includes the
gap between a read answer and an unread one — in round 26, 1032.5 against
661.5. The shift shrinks or grows with it, and both are reported.

Three things print beside the target line, whatever the target did:

1. **Where every cell voted**, and which cells were refused with the reading
   rates that refused them.
2. **The marginal shift, and the same shift with each cell's reading rate held
   at the baseline's.** The gap between those two is the mix. Both are computed
   over the cells a counterfactual can be built for, so the comparison is not
   between two different sets of cells.
3. **The unread stratum's median, both rounds.** The target is scored inside
   the grounded stratum wherever a cell has one, so without this an edit could
   compress only the answers that never opened a file and the verdict would say
   nothing about it.

## Why the bar is two runs and not five

`GROUNDED_MIN_RUNS` asks whether a stratum exists, not whether it is powered.
Two is what the floor's standard deviation needs, and the sampling error of a
two-run median already sits inside the floor it is gated against. Bootstrapped
over the round-25 and round-26 control cells that have at least ten grounded
runs, 4000 draws each, the standard deviation of the resampled median:

| subsample | n=2 | n=3 | n=4 | n=5 | n=6 | n=8 | n=10 |
| --- | --: | --: | --: | --: | --: | --: | --: |
| round 26, median over cells | 455 | 478 | 394 | 399 | 340 | 279 | 250 |
| round 25, median over cells | 526 | 578 | 466 | 452 | 385 | 330 | 291 |

The floors built from those same cells are 679 and 767, so every column is
inside the dispersion the gate already tolerates.

Raising the bar does not buy a better estimate — it refiles cells into the
wrong stratum. At three, a cell that read 4 of 10 is classed "unread" and its
four grounded answers are dropped from a comparison of unread ones, which is a
worse statistic than a noisy median. Round 24's eight scoped cases go from 8
grounded cells and 2 unread at a bar of two, to 3 and 10 at a bar of five; the
target does not get stricter, it gets answered by the wrong stratum.

## Round 20, cell by cell

Round 20's headline was a median shift of 2414 tokens, 6 of 6 voting cells,
p = 0.031. It is the clearest case of the defect in the stored rounds.

| cell | read, baseline | read, round | marginal | stratified | stratum |
| --- | --: | --: | --: | --: | --- |
| `design-alerting`/haiku | 10 of 10 | 10 of 10 | 978 → 982 | 978 → 982 | grounded |
| `design-alerting`/sonnet | 10 of 10 | 10 of 10 | 4651 → 2235 | 4651 → 2235 | grounded |
| `design-audit-log`/haiku | 6 of 10 | 1 of 10 | 1486 → 759 | — | **refused** |
| `design-audit-log`/sonnet | 10 of 10 | 9 of 10 | 6544 → 3122 | 6544 → 3161 | grounded |
| `design-rate-limit`/haiku | 1 of 10 | 0 of 10 | 654 → 611 | 643 → 611 | unread |
| `design-rate-limit`/sonnet | 8 of 10 | 3 of 10 | 4012 → 1413 | 4041 → 2418 | grounded |
| `design-retry`/haiku | 2 of 10 | 0 of 10 | 702 → 628 | — | **refused** |
| `design-retry`/sonnet | 6 of 10 | 1 of 10 | 3842 → 1613 | — | **refused** |
| `design-search`/haiku | 1 of 10 | 0 of 10 | 587 → 601 | 559 → 601 | unread |
| `design-search`/sonnet | 7 of 10 | 1 of 10 | 2264 → 1226 | — | **refused** |

`design-rate-limit`/sonnet is the mechanism in one line: marginally it fell
4012 to 1413, a 65% cut, and inside the grounded stratum it fell 4041 to 2418,
40%. The other 25 points are five of eight answers leaving the stratum. Four
cells fell so far that they have no grounded stratum left to compare at all.

Scored this way round 20 reads **4 of 6 cells improved, p = 0.688**. The target
does not pass.

## Re-scoring every stored `output_tokens` round

The target line `report.py --against` prints, before and after, for all fifteen
rounds that named `output_tokens`. Same snapshots, same scopes, same code path.

| round | target line, as scored on the day | target line, stratified |
| --- | --- | --- |
| 05 | reject, 10 of 22 cells, p = 0.832 | unchanged |
| 06 | reject, 5 of 6 cells, p = 0.219 | unchanged |
| 07 | **pass**, shift 711, 6 of 6, p = 0.031 | **reject**: 5 voting cells, under the six a sign test needs |
| 08 | **pass**, shift 504, 6 of 6, p = 0.031 | **reject**: 5 voting cells |
| 09 | pass, shift 663, floor 380.5 | pass, shift 303, floor 242.9 |
| 10 | pass, shift 722, floor 380.5 | pass, shift 435, floor 242.9 |
| 11 | reject, 5 of 6, p = 0.219 | reject: 5 voting cells |
| 12 | pass, shift 722, floor 380.5 | pass, shift 500, floor 242.9 |
| 14 | reject, 5 of 6, p = 0.219 | reject: 4 voting cells |
| 15 | **pass**, shift 2288, 6 of 6, p = 0.031 | **reject**: 7 of 8 cells, p = 0.070 |
| 19 | reject, 11 of 15, p = 0.118 | reject: shift 180 inside a 478.4 floor |
| 20 | **pass**, shift 2414, 6 of 6, p = 0.031 | **reject**: 4 of 6 cells, p = 0.688 |
| 24 | pass, shift 1452, 8 of 9, p = 0.039, floor 895.0 | pass, shift 1949, 7 of 7, p = 0.016, floor 448.3 |
| 25 | pass, shift 1562, 8 of 8, p = 0.008, floor 1236.0 | pass, shift 1616, 8 of 8, p = 0.008, floor 766.8 |
| 26 | pass, shift 1294, 8 of 8, p = 0.008, floor 1032.5 | pass, shift 1703, 8 of 8, p = 0.008, floor 661.5 |

**Four target lines flip, and all four flip the same way — from pass to
reject.** No round moves from reject to pass, at any of the bars tried. The
correction only ever takes a token claim away.

**No round's verdict changes.** Rounds 07, 08, 15 and 20 were all rejected on
other counters and all four edits were reverted; what is withdrawn is the
sentence in each round file saying the target passed. Round 07's "the named
target itself passed for the first time in the loop's history" and round 20's
"the target passed again" are the two that were quoted afterwards, and neither
survives.

**The rounds that carried an accepted edit pass harder, not softer.** Rounds 24
and 26 are the two edits the loop has shipped, and both grow: 1452 to 1949 and
1294 to 1703. Their compression is compression.

## What it says about the licence in 0.2.2

Round 26 is the round that shipped, and it is the round the correction was most
likely to catch, because it moved 14% of answers into handing the decision back
([#138]). It does not catch it.

| cell | read, control | read, licence | marginal | stratified |
| --- | --: | --: | --: | --: |
| `design-alerting`/sonnet | 25 of 25 | 25 of 25 | 4410 → 2690 | 4410 → 2690 |
| `design-audit-log`/sonnet | 25 of 25 | 25 of 25 | 6090 → 3369 | 6090 → 3369 |
| `design-cache`/sonnet | 13 of 25 | 13 of 25 | 4030 → 2768 | 4776 → 3330 |
| `design-rate-limit`/sonnet | 17 of 25 | 17 of 25 | 3252 → 1906 | 3721 → 2221 |
| `design-realtime`/sonnet | 15 of 25 | 13 of 25 | 3266 → 1747 | 3385 → 2299 |
| `design-retry`/sonnet | 9 of 25 | 10 of 25 | 2571 → 2023 | 4379 → 2563 |
| `design-search`/sonnet | 17 of 25 | 14 of 25 | 2087 → 1286 | 2260 → 1367 |
| `design-upload`/sonnet | 13 of 25 | 6 of 25 | 3248 → 1651 | 3977 → 2387 |

Every cell keeps its grounded stratum on both sides, and the reading rate holds
in six of eight. Over the six cells where the counterfactual can be built, the
shift is **1364 tokens with each cell held at the control's own reading rate,
against a marginal 1424** — the mix accounts for 60 tokens of it, 4%. Round 25
reads 1377 either way.

The unread stratum moved too, 1825 to 1181 over the same six cells, so the
licence shortened the answers that never opened a file by about a third as
well. The compression is in both strata, which is what an edit that shortens
prose rather than suppressing work should look like.

Two cells are worth naming individually. `design-upload`/sonnet is where reading
fell furthest, 13 of 25 to 6 of 25, and its stratified shift is 1590 against a
marginal 1597: even there the compression is not the mix. `design-realtime`
/sonnet is the one cell that moves the way the defect predicts, 1519 marginal
against 1086 stratified, and it is not enough to change the round.

The hands-back finding in [#138] stands on its own evidence and is not touched
by this. What is settled is the narrower question: **round 26's token win is not
mix-shift**, and neither is round 24's.

## Limits

- **`num_turns` is a proxy for reading, and it leaks on haiku.** On sonnet the
  separation is clean — 0 of 41 one-turn design responses name a fixture file
  against 151 of 159 multi-turn ones — while 8 of 183 one-turn haiku runs quote
  fixture-only content. A haiku cell can therefore be filed as unread when it
  read. This is the same limit that already forces `--target one_turn` to name
  a model scope, and it is an argument for scoping token targets to sonnet too.
- **The counterfactual covers only cells that have both strata in the round.**
  Round 26 has six of eight; round 20 has two of six. It prints its own
  coverage, as does the unread median beside it, and both are disclosures
  rather than gates. Nothing scores the unread stratum: a round that compresses
  only unread answers is visible in the verdict and still fails its target.
- **A scope whose reading rate collapses can now be refused for want of voting
  cells**, which is what happened to rounds 07, 08, 11 and 14. That is the
  instrument reporting that it cannot measure this scope, not a rejection of the
  edit. The design that avoids it is the one rounds 25 and 26 already used:
  more reps, one model, eight cases. At 25 reps a side no cell in either round
  lost its stratum.
- **This does not fix [#132].** The floor still gates on a level rather than on
  dispersion; it is now built from within-stratum dispersion, which is the right
  input for the statistic it gates, but the shape of the rule is unchanged.
- **It does not fix [#139] either.** `one_turn` remains the co-requirement that
  guards the mix, and at 75 runs a side it still cannot see the rise it watches
  for.

[#51]: https://github.com/JordanMPDS/laconic/issues/51
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#132]: https://github.com/JordanMPDS/laconic/issues/132
[#138]: https://github.com/JordanMPDS/laconic/issues/138
[#139]: https://github.com/JordanMPDS/laconic/issues/139
