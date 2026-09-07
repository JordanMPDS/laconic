# Round 53: what the fatal quality gate does when nothing changed

**Registration. Nothing below the results line has been computed**, with one
exception that is marked as computed and dated in place, because it comes from
already-committed snapshots and is the reason this round exists. This file and
`evals/pilot/score_aa.py` are committed in the same commit, before any
generation, following [round 38](round-38.md), [round 47](round-47.md),
[round 48](round-48.md), [round 49](round-49.md), [round 50](round-50.md),
[round 51](round-51.md) and [round 52](round-52.md).

**This round proposes no rule edit.** `rules/laconic.md` is untouched and
`rules_cksum` stays at master's 136269960 throughout. It is an instrument
round: it measures the gate rather than the rules.

## The hypothesis

> Running the loop's fatal `quality_fails` gate on two arms that differ in
> **nothing** — two 5-rep blocks drawn from one interleaved master-rules batch
> — reports a fatal quality loss on a substantial share of draws, and a
> substantial share of those still stand after the [#52] arbitration
> replication is offered from a third block of the same batch.

Two registered readings, fixed before the numbers, on **bar B** — the share of
null draws where the loss still stands after arbitration, which is the exact
procedure that rejected [round 51](round-51.md) and [round 52](round-52.md):

- **B ≥ 0.20.** The procedure fires on nothing at least one draw in five. The
  rejection rule has to be repriced before another round is spent against it,
  and the two rejects it produced cannot be read as evidence of harm.
- **B ≤ 0.05.** The procedure is sound at 5 reps. Rounds 51 and 52's rejects
  stand on their own, and [#116]'s next round must buy its compression from a
  sentence outside that family, exactly as round 52 said.
- **Between.** The round reports the number and proposes nothing. A gate that
  fires on nothing between 5% and 20% of the time is neither sound nor clearly
  broken, and picking a side after seeing which side the number landed on is
  the thing this registration exists to prevent.

**Bar A** — the share of draws where the gate reports the loss at all, before
arbitration — is registered as a reported quantity with no threshold attached.
It is the numerator bar B is a fraction of, and it is not independently
interesting: `accept_verdict` only examines cells once the round-wide total has
risen, so bar A is bounded above by the probability that one block's total
exceeds another's, which under a symmetric null is a little under one half
whatever the cells do.

**Registered secondary**, no threshold: the share of null draws whose
round-wide difference reaches round 51's observed **+7** and round 52's
observed **+4**.

**Registered bound, fatal to the round rather than to a hypothesis.** The pool
must come back with **0 failed runs** and a single `rules_cksum`. A pool
holding failures has a different exposure per cell across blocks, and the
counter is a count. If either fails the round is void and re-bought, not
reinterpreted.

## Why this round exists

Rounds 51 and 52 both passed their registered target and both died on the same
counter. Quoting round 51's own statement of what its reject was:

> The gate is a strict count over harm, and round-wide the *rate* does not
> separate: quality fails 47 of 133 against 54 of 135, Fisher **p = 0.4516**.
> So this round is not evidence that the sentence makes answers wrong at a
> measurable rate. It is a rise on a counter the loop treats as fatal without a
> significance test, offered one replication, and not cleared by it.

Round 52 repeated the shape at a different wording — 41 to 45, Fisher
p = 0.6977, three of four risen cells reproducing — and closed with the fork
this round takes:

> A fourth round wanting the compression has to buy it from a sentence that is
> not this family, or else **establish that the cost is real and price it**.

Neither round could take the second branch, because neither had a null. A round
compares an edit against a control and reads the difference; nothing in the
loop's history has ever run the comparison with the edit removed. That is the
missing measurement, and it is cheap.

### The mechanism this round expects to find, stated in advance

`report.CELL_TEST_MIN_RUNS` is **20**. Below it, `_sample_covers` returns
`False` and a risen cell keeps the bare count comparison — one 5-run draw
against another, with no interval. `cell-rates.json` screens six of the
round-wide scope's 28 quality cells (`design-cache`, `design-realtime` and
`design-upload`, both models). **The other 22 are scored by comparing two
integers out of five.**

For a cell failing at 40% under master rules, one 5-run draw exceeds another
about a third of the time. With 22 such cells the chance that none rises is
negligible, so the gate should fire whenever the round-wide total rises at all,
and clearing should require every risen cell to replicate at or below its
control — roughly a coin flip per cell, compounding.

That prediction is written here so that confirming it is worth something. It is
also why bar B and not bar A carries the threshold: bar A is nearly determined
by the arithmetic above, and bar B is not.

## The one figure computed before this round, and where it came from

**Computed 2026-09-07, from committed snapshots, before any generation.** Two
round-wide master-rules control arms exist: `round-51-wide-control.json`
(2026-09-06) and `round-52-wide-control.json` (2026-09-07). Both are the
`laconic` arm at 5 reps, both at `rules_cksum` 136269960, both judged 220 of
220 at `criteria_cksum` 5539815, and both generated under CLI 2.1.263. They
differ in the calendar and nothing else.

Scored against each other by `report.py` exactly as a round is scored, in the
direction that makes the later one the baseline:

```
REJECT: quality lost (41 -> 47); cells: design-alerting/sonnet +2,
design-audit-log/haiku +4, design-rate-limit/haiku +2, design-retry/sonnet +2,
verdict-rollout/haiku +1, verdict-schema/haiku +1; within the measured
master-rules rate: design-upload/haiku 5 of 5 against 70%
```

Six risen cells and +6 round-wide, from an edit that does not exist. Three of
the six — `design-alerting`/sonnet, `design-audit-log`/haiku and
`verdict-schema`/haiku — are three of the four cells that rejected round 52,
and `design-audit-log`/haiku rises further here (+4) than it did there (+3).

Pooling the two arms into a 10-rep corpus and resampling 200 two-block draws
with `score_aa.py --blocks 2` gives a firing rate of **39.0%**, with 31.0% of
draws reaching round 52's +4 and 15.0% reaching round 51's +7.

**That pool is not the measurement, and this round does not rest on it.** Its
two halves are a day apart, so it carries era drift on top of sampling, and the
loop has known since [round 37](round-37.md) that a sequential comparison is
exactly the exposure to avoid — a syntactic behaviour moved 4.7x in five days
there at byte-identical rules. Rounds 51 and 52 both generated their two sides
simultaneously and are not vulnerable to it. So the cross-era number motivates
this round and cannot substitute for it: **the pool bought below is one batch,
and its blocks are separated by nothing at all.**

It does reach one thing the bought pool will not, and it is worth saying now.
Rounds 51 and 52 generated their two sides simultaneously but bought their
[#52] arbitration afterwards, as a separate later batch. The clearing rule
compares that later batch against the earlier control, so **arbitration is a
sequential comparison even in a round whose main contrast is not.** Whatever
this round measures for bar B is therefore a floor on what the loop's real
arbitration does, not an estimate of it.

## Design

**One arm, one batch, no edit side.** The pool is the `laconic` arm at master
rules, 15 reps, over the **14 quality-graded cases inside the round-wide
22-case scope**, both models. 420 generations.

| | |
|---|--:|
| cases | 14 |
| models | 2 |
| reps | 15 |
| generations | **420** |
| judgments | **420** |

The 14 are the quality-graded members of the scope rounds 51 and 52 scored:

```
design-alerting, design-audit-log, design-cache, design-rate-limit,
design-realtime, design-retry, design-search, design-upload, fail-open,
silent-success, stale-cache, verdict-experiment, verdict-rollout, verdict-schema
```

**Restricting to them changes no number.** `quality_fails` is
`_judge_fails(judg, "quality", ...)`, a sum over quality-graded cells only, so
the eight rule-adherence and safety cases in the 22 contribute exactly zero to
it. 14 cases × 2 models × 5 reps is 140 judgments per block, which is the
denominator round 52 reported (41 of 140 against 45 of 140). What the
restriction gives up is the other three fatal counters, and this round does not
measure them or claim anything about them.

**15 reps, because a draw needs three disjoint blocks of five.** Five is the
unit every round since 21 buys per side, and the whole question is what the
gate does at that unit; four blocks of four would measure a gate the loop does
not run. The three blocks are labelled control, edit and arbitration, which are
the three roles a round uses, and nothing distinguishes them but the label.

**Four shards, per [#255].** Each shard declares `--concurrency 4`.

```sh
python3 evals/bench/run.py --arms laconic --models haiku,sonnet --reps 15 \
  --concurrency 4 --cases <shard cases> \
  --snapshot evals/snapshots/loop/round-53-pool-<n>.json
python3 evals/bench/merge.py evals/snapshots/loop/round-53-pool-[1-4].json \
  --out evals/snapshots/loop/round-53-pool.json
python3 evals/bench/judge.py --results evals/snapshots/loop/round-53-pool.json \
  --jobs 6 --out evals/snapshots/loop/round-53-pool-judgments.json
```

## Scoring

```sh
python3 evals/pilot/score_aa.py evals/snapshots/loop/round-53-pool.json \
  --judgments evals/snapshots/loop/round-53-pool-judgments.json \
  --draws 500
```

500 draws at seed 53, three 5-rep blocks each. **The gate is imported, not
reimplemented**: `score_aa.py` calls `report.round_summary` and
`report.accept_verdict` on sub-snapshots, with `cell-rates.json` loaded through
`report.load_cell_rates`. A second copy of the counter would be a second thing
to keep in sync, and a drift between the two would produce a null describing a
gate the loop does not run — the same argument `AGENTS.md` already makes about
the level-slicing marker living in `hooks/laconic.sh` and only there.

## What this round cannot establish

- **It cannot show rounds 51 and 52's edits were harmless.** A gate that fires
  on nothing is uninformative about the rounds it rejected; it does not follow
  that those rounds had nothing to reject. Both claims are about the same two
  rounds and only the first is measured here.
- **The 500 draws are re-partitions of one 15-rep batch**, not 500 independent
  experiments. The quantity is the gate's behaviour conditional on this batch,
  which is the right conditional — sampling inside a round is precisely what a
  round is exposed to — but its own uncertainty is not 1/sqrt(500), and no
  interval is quoted from the draw count.
- **One model pair, one scope, one batch, one day.** A second batch would
  estimate the between-batch part, and this round does not buy one.
- **It measures `quality_fails` only.** The other three fatal counters have
  different exposures and are not in the pool's scope.
- **It proposes no change to the gate.** If bar B fires, the fix is a change to
  a fatal counter, which would re-score the archive and needs its own
  registration and its own bar — the standing rule is that no stored round's
  verdict may move without that being the round's declared purpose. This round
  files the number and the issue.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#52]: https://github.com/JordanMPDS/laconic/issues/52
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#133]: https://github.com/JordanMPDS/laconic/issues/133
[#255]: https://github.com/JordanMPDS/laconic/issues/255
