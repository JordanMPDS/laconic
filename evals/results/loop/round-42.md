# Round 42: depth inflates an unruled answer, and the plugin is what reverses it

**This round proposes no rule edit.** It buys the one measurement
[`over-length-cluster.md`](over-length-cluster.md) registered before it: a
baseline arm at depth under the delivery mode the plugin actually ships.

## The question, and why nothing in the archive could answer it

Round 40 measured the laconic arm under `--turn-delivery plugin` and found the
turn chain descending where `repeat` has it ascending. Round 41 established the
fall is not harm — 30/30, 28/30 and 28/30 on the identical final question at
three depths, p = 0.4915.

Neither could say **whose** the fall is. Every `plugin`-delivery run in the
archive was a laconic run: round 39's 45 and round 40's 220. So 17 words at
turn 2 had two readings and nothing separated them:

- **The plugin is working.** Laconic holds the level as a session deepens.
- **The harness gets terse at depth regardless.** An unruled model in the same
  five-turn chain would also answer in 17 words, and laconic is being credited
  with something the setup produces.

## The registered design

From [`over-length-cluster.md`](over-length-cluster.md), written before the batch:

> **Hypothesis:** generating `baseline` beside `laconic` under
> `--turn-delivery plugin` will show the depth fall on the laconic arm only. The
> falsifier is a baseline arm that falls by a comparable proportion, which would
> mean the shipped multi-turn behaviour is the harness rather than the plugin,
> and would retire this cluster's whole multi-turn instrument.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 10 \
  --cases 'confirm-*,deep-*' --turn-delivery plugin --concurrency 1 \
  --snapshot evals/snapshots/loop/round-42.json
```

`confirm-*` is one turn and `deep-*` is five, sharing a fixture, a final question
and a byte-identical trap, so depth is the only variable. 360 calls, no judging,
scored on median words per cell — [#131] and round 33's boundary lesson both
forbid an `output_tokens` target across the single-turn/multi-turn line, and this
round confirms why: `confirm-*` reads the fixture on its graded turn in 60 of 60
runs and `deep-*` in 0 of 60, because the reading happened on turn 1.

**One deviation from the registered command**, recorded because deviations are
how a registration stops meaning anything: `--concurrency 1` rather than the
anticipated `2`. One invocation loops arms innermost, so `baseline` and `laconic`
are sampled at adjacent moments, and 1 is what is true of the file. Sharding
would have halved the wall time and bought nothing else.

## The result: the arms move in opposite directions

Median words on the graded turn, n = 10 per cell, sonnet, `rules_cksum`
136269960:

| cell | baseline | laconic | laconic / baseline |
|---|--:|--:|--:|
| `confirm-index` | 128.5 | 100.5 | 0.78 |
| `confirm-metric` | 138.0 | 89.5 | 0.65 |
| `confirm-rollback` | 143.5 | 109.0 | 0.76 |
| `deep-index` | 210.5 | 38.0 | **0.18** |
| `deep-metric` | 244.0 | 33.0 | **0.14** |
| `deep-rollback` | 184.0 | 20.5 | **0.11** |

Pooled by family:

| arm | turn 1 | turn 5 | change |
|---|--:|--:|--:|
| baseline | 139.0 | 210.5 | **+51.4%** |
| laconic | 98.0 | 30.5 | **−68.9%** |

**The falsifier did not fire. Baseline does not fall at depth — it rises by half
again.** Every stem agrees in both arms: baseline +64%, +77%, +28%; laconic
−62%, −63%, −81%. Six of six cells move as the hypothesis predicted, two-sided
exact sign test **p = 0.0312**.

The arm gap widens with depth, which is the same statement paired within cells:

| | laconic − baseline, per cell | laconic lower in |
|---|--:|--:|
| turn 1 | median **−39.5** words | 29 of 30 |
| turn 5 | median **−181.0** words | 30 of 30 |

Shuffling the family labels across those 60 paired differences puts the widening
at **p = 5e-06**, the resolution floor of 200,000 resamples.

## Baseline is a delivery-invariant control, and it replicates

This is the part that makes the round worth more than its own numbers.
`arms["baseline"]` carries `system_prompt: None`. In `call_turns` that means
`sp = None` on every turn under **both** modes, and the `plugin` reminder is
prepended only `if system_prompt and level`, so it is never added. The baseline
arm therefore receives byte-identical treatment under `repeat` and `plugin`, on
every turn, by construction rather than by measurement.

So its depth effect should be the same in both, and it is — across two
independent batches four days and several CLI releases apart:

| baseline, turn 1 to turn 5 | delivery | batch | change |
|---|---|---|--:|
| 136.0 to 225.0 | `repeat` | rounds 33 and 35 | **+65.4%** |
| 139.0 to 210.5 | `plugin` | round 42 | **+51.4%** |

That is a genuine replication of the depth effect on the unruled arm, and it is
the strongest evidence this cluster has that the effect is real rather than a
harness artifact.

## What this does to the cluster, and to [#136]

[#204] corrected rounds 33 to 36 because their inflation figures are `repeat`
figures, and [#206] rewrote the cluster index on the strength of that. Both are
right, and both left [#136] *less* explained than before — the mechanism it
named had been measured on the laconic arm, and that measurement was withdrawn.

This round puts the mechanism back, on the other arm:

- **Conversational depth inflates an unruled answer by about half.** [#136] and
  [#60] both describe exactly this, and it now has a matched control and a
  replication.
- **What rounds 33 to 35 actually measured is laconic failing to resist it.**
  Under `repeat`, laconic ran +36.8% at depth; under `plugin` it runs −68.9%
  against a baseline running +51.4%. The rules text is identical in both. What
  differs is how it arrives.
- **Under the shipped wiring the rule binds hardest exactly where the report
  says it fails.** At turn 5 laconic is 0.11 to 0.18 of baseline; at turn 1 it is
  0.65 to 0.78.

So the honest statement about [#136] is no longer "three candidates measured, two
real, one null". It is: **the mechanism the issue names is real and measured, and
the plugin already reverses it on this instrument.** What the instrument still
does not reproduce is the reported failure itself — a laconic session going long
at depth — and after this round that is a gap between the report and the product
rather than a gap in the diagnosis.

## What this round did not buy

- **No judging.** The registered scope was length. The quality claim on the
  laconic side comes from [`round-41.md`](round-41.md), which judged these exact
  cells at this exact revision and delivery: 30/30 at turn 1 and 28/30 at turn 5,
  p = 0.4915. **Baseline's quality at depth is unjudged**, so this round cannot
  say whether its extra 180 words buy anything.

  > **Answered by [`round-43.md`](round-43.md), on this snapshot.** Both arms
  > grade **120 of 120**, every cell 10/10, so at turn 5 baseline writes seven
  > times as much and answers no better. The comparison is at its ceiling: it
  > rules out a laconic deficit of 6 failures in 30 and cannot see anything
  > smaller.
- **Sonnet only**, 10 reps, one rules revision.
- **`recall-*` was omitted** to keep the round at one contrast, so the two-turn
  midpoint is not measured under a matched baseline.

## An instrument note: the first permutation design was wrong

The obvious test — permute arm labels within each cell, recompute the difference
of medians — returned **p = 0.37** on an effect visible in every cell of the
table above. The design is at fault, not the effect. Swapping labels within a
cell builds each permuted group as a 50/50 mixture of two well-separated modes
(`deep` baseline runs 161 to 278 words, `deep` laconic 11 to 57), and the median
of such a mixture lands in whichever mode happens to draw more than half the
values. The permuted statistic therefore has enormous variance and the test has
almost no power.

Reducing to the within-cell difference first, then shuffling the family label
across those 60 differences, removes the mixture and gives p = 5e-06. **A median
statistic under a permutation that creates bimodality is not a conservative test,
it is a broken one** — worth knowing, because the medians-across-cells shape is
what this loop reaches for by default.

## Cost

$12.57 for 360 generations, 0 failed, about 1h36m wall on one process. Cheaper
than the $27 the registration estimated, because laconic's answers at depth are
short enough to cost noticeably less than baseline's: `deep-*` cost $6.40 on
baseline against $3.61 on laconic.

## Ledger

No rule edit. Recorded in [`LEDGER.md`](LEDGER.md).

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#204]: https://github.com/JordanMPDS/laconic/pull/204
[#206]: https://github.com/JordanMPDS/laconic/pull/206
