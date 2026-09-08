# Round 56: the pre-action check's quality cost, bought at 0.95 power on the cells that carry it

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are the reason this round takes the
shape it does. This file is committed before any generation, following
[round 38](round-38.md), [round 47](round-47.md), [round 48](round-48.md),
[round 49](round-49.md), [round 50](round-50.md), [round 51](round-51.md),
[round 52](round-52.md), [round 53](round-53.md), [round 54](round-54.md) and
[round 55](round-55.md).

**This round proposes no rule edit.** It measures one that already shipped. The
only way `rules/laconic.md` changes in this branch is by the registered revert
in "The decision rule" below, and only if the primary endpoint fires.

## Why this round exists

[#263](https://github.com/JordanMPDS/laconic/issues/263). Three rounds have put
a non-significant quality rise in the `design-*` family at two wordings of the
pre-action check, and [round 55](round-55.md) added a reserved set that moved
the same way. Every one of those rounds was powered for something else: round
55's own registration computed that settling a 5-point shift on a 40% base
needs about **1,188 verdicts a side**, against the 80 a round-wide arm buys,
and [round 54](round-54.md) measured the same ceiling from the gate's end — at
five reps a side the repriced [#259] gate needs about **+23** round-wide before
it fires four times in five, where the rises observed are +9 and +11.

A fourth underpowered round is worth nothing. This one buys the reps.

## What the archive says once it is split by model

> **Computed 2026-09-08, before this registration**, from the committed
> `round-51-wide-*`, `round-52-wide-*` and `round-55-wide-*` snapshots and
> their judgments. `report.py`'s own case-grading and saturation filters were
> used, so these are the same verdicts the fatal `quality_fails` counter reads.

Every published table so far has reported the design family pooled over both
models. Split, the three rounds agree on where the rise is and where it is not:

| | round 51 | round 52 | round 55 | pooled | Fisher (2-sided) |
|---|---|---|---|---|--:|
| `design-*`/**sonnet** | 10/40 → 16/40 | 9/40 → 11/40 | 5/40 → 11/40 | **24/120 (20.0%) → 38/120 (31.7%)** | **0.0547** |
| `design-*`/haiku | 25/40 → 25/40 | 21/40 → 23/40 | 21/40 → 22/40 | 67/120 (55.8%) → 70/120 (58.3%) | 0.7943 |
| other quality/sonnet | 7/30 → 8/30 | 7/30 → 6/30 | 6/30 → 6/30 | 20/90 → 20/90 | 1.0000 |
| other quality/haiku | 5/30 → 5/30 | 4/30 → 5/30 | 5/30 → 7/30 | 14/90 → 17/90 | 0.6935 |

The sonnet difference is +11.7 points, 95% CI [+0.7, +22.6], Mantel-Haenszel
odds ratio **1.87** across the three rounds, and it rises in all three. Haiku
sits at 56% — near maximum binomial variance, so it has room to move — and does
not move. The non-design quality cells do not move on either model.

**Pooling the two models is what has been hiding this.** `design-*` over both
models pools to 91/240 → 108/240 at p = 0.1381, which is the figure round 55
published and #263 quotes. Half of that denominator is a family with no effect
in it.

**This p = 0.0547 may not be cited as a result and is not one.** The split was
found by looking, after three rounds whose registrations named neither model.
It is the basis for this round's scope, which is the one legitimate use of a
post-hoc subgroup, and the round below is the test.

### The second thing the split shows: the reading rate falls

> **Computed 2026-09-08, before this registration**, from `num_turns` on the
> same three snapshots. No judging, no new calls.

| | round 51 | round 52 | round 55 | pooled | Fisher (1-sided) |
|---|---|---|---|---|--:|
| `design-*`/sonnet, runs that opened no file | 18/40 → 25/40 | 14/40 → 15/40 | 16/40 → 21/40 | **48/120 (40.0%) → 61/120 (50.8%)** | **0.0598** |

This matters more than its p, because on the design family the reading rate is
not one correlate of quality among several — it is the axis. That is what
[`design-discrimination.md`](design-discrimination.md) and [#88] establish: the
three cases added in `-v4` exist precisely because the five older ones cannot
tell a derived answer from a recalled one, and **no response that failed to
resolve the fixture has ever passed on them**.

So the archive offers a coherent mechanism rather than a bare correlation. The
check reads *"Read what grounds the answer, name what is wrong, and leave the
fix for the user to ask for."* Its trigger is a broken thing, and a design
question has none, so the clause the model can still apply is the one about not
acting. Answering without acting means answering without reading, and on these
cases that is the failure.

## The two forks #263 named, and how the archive settles them

**Scope: sonnet, not the family.** Pooling the flat haiku half costs power
rather than buying it. At 20 reps a side the sign is unambiguous — simulating
the registered test at the pooled rates gives **0.54** power over both models
against **0.73** on sonnet alone, at 2x the calls. Sonnet at 40 reps reaches
**0.95** for fewer calls than both models at 20.

**Endpoint: the counter, because on sonnet the fork collapses.** #263 asks
whether to register the flat `quality_fails` count or the resolving stratum.
The stratum is defined by `asks_back`, which is measured on the response, so
conditioning on it is a post-treatment adjustment and can manufacture a
difference out of a composition shift. On sonnet that risk is also
unnecessary: the hands-back stratum is **16/120 → 25/120** of design/sonnet
runs, so the flat count and the resolving count are nearly the same
measurement. Register the unconditioned one. The strata are reported below the
line as disclosure, which is all `report.py` has ever claimed for them.

## What the round buys

**640 generations and 640 judgments**, against round 55's 1,080 and 680.

Eight `design-*` cases, **sonnet only**, **40 reps a side**, both sides
generated simultaneously from two trees so era and CLI release cancel between
them rather than confounding them — the pattern [round 38](round-38.md)
established and every round since has used. Four `run.py` processes, two a
side, `--concurrency 4` declared on all four, which is exactly the [#255]
ceiling.

The control side is `4da6314` (round 54's merge), `rules_cksum` **136269960**.
The edit side is this branch, `rules_cksum` **594915793**. `git diff 4da6314
HEAD -- evals/cases` is empty, so the two trees carry byte-identical case
material and both snapshots carry `cases_cksum` 2389944869.

```sh
# edit side, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases design-alerting,design-audit-log,design-cache,design-rate-limit \
  --concurrency 4 --snapshot evals/snapshots/loop/round-56-edit-a.json
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases design-realtime,design-retry,design-search,design-upload \
  --concurrency 4 --snapshot evals/snapshots/loop/round-56-edit-b.json

# control side, from a worktree at 4da6314, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases design-alerting,design-audit-log,design-cache,design-rate-limit \
  --concurrency 4 --snapshot <abs>/evals/snapshots/loop/round-56-control-a.json
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases design-realtime,design-retry,design-search,design-upload \
  --concurrency 4 --snapshot <abs>/evals/snapshots/loop/round-56-control-b.json
```

Shards are unioned by `evals/bench/merge.py`, which recomputes `cases_cksum`
over the union and refuses a merge across `rules_cksum` — the guard that makes
a two-shard side one round rather than two.

## Registered power

> **Computed 2026-09-08, before this registration.** 8,000 simulated draws per
> figure at the pooled rates above, scored by the exact test this round
> registers.

| endpoint | assumed | n/side | power |
|---|---|--:|--:|
| **primary:** `quality_fails`, `design-*`/sonnet | 20.0% → 31.7% | 320 | **0.95** |
| secondary: unread rate, `design-*`/sonnet | 40.0% → 50.8% | 320 | ~0.93 |

The primary is sized against the pooled three-round estimate, not against round
55's own 5/40 → 11/40, which is the largest of the three. That follows
[round 46](round-46.md)'s rule: size against the least favourable defensible
estimate, never the most recent or the largest.

**0.95 is the point of the round.** At that power a null is a result rather
than another draw, which is what four rounds have failed to deliver.

## Registered bars

**Primary (fatal): `quality_fails` on `design-*`/sonnet.** Laconic arm, edit
side against this round's own simultaneous control, one-sided Fisher exact in
the direction of harm, α = 0.05. The verdicts are exactly those
`report.py`'s `quality_fails` counter reads — quality-graded, non-saturated
cells — and this round adds no case and no filter of its own.

**Secondary (registered, not fatal): the unread rate on `design-*`/sonnet**,
one-sided Fisher exact at α = 0.05, computed from `num_turns` at no call cost.
Non-fatal is the loop's standing rule for a reading-rate endpoint and is
deliberate: not opening a file is not itself harm, it is the mechanism the
harm counter is supposed to catch. Reported in the [#131]-sanctioned
`one_turn` scope (`design-cache`, `design-realtime`, `design-upload`) as well
as over the family, because that scope is the one with an established link to
answer quality and the loop's rules forbid scoring the other cells.

**Per-cell disclosure.** At 40 runs a side every cell clears
`CELL_TEST_MIN_RUNS`, so [#259]'s per-cell path is open for the first time on
this question. Per-cell counts and their one-sided tests are published whether
or not the primary fires. This round does not add a second fatal per-cell bar
on top of the primary — one registered test, one α.

## The decision rule

Registered here so that neither outcome can be argued into the other afterwards.

- **The primary fires** (one-sided p < 0.05): the cost is established. This
  branch reverts the pre-action check from `rules/laconic.md`, regenerates
  `rules/dist/*.md` with `bash tools/build-rules.sh`, and the ledger records
  the edit as accepted at round 55 and reverted at round 56 on power. That is
  the loop's standing rule — a lost quality verdict is fatal whatever the
  target did — and it is registered in advance because the edit's replicated
  compression win is exactly the kind of thing that invites re-litigation once
  the numbers are in.
- **The primary does not fire**: the edit stands, #263 closes, and the round
  publishes the difference with its 95% confidence interval. At 0.95 power
  against the pooled estimate, a null bounds the cost rather than failing to
  find it, and the interval is the number that belongs in the issue.
- **The primary does not fire and the secondary does**: the edit stands, and
  the round files the reading-rate finding as its own issue. A reading fall
  with no measurable quality cost on a case set built to make reading matter is
  a result about the metric as much as about the rule, and it is not grounds
  for a revert under any bar this loop has registered.

## What this round cannot establish

- **Anything about haiku.** The scope is sonnet, chosen because that is where
  three rounds put the effect. Haiku's evidence stays at 67/120 → 70/120 from
  those rounds and this round does not add to it. A concentrated haiku
  regression appearing later would not be contradicted by anything here.
- **Anything about the non-design quality cells**, for the same reason: 20/90 →
  20/90 and 14/90 → 17/90 stand as they are.
- **The round-wide fatal counters.** Round 55 bought those over 22 cases and
  both models and they cleared under the [#259] gate. This round does not
  re-buy them, and a null here does not re-clear them.
- **Whether the mechanism is the reading rate.** The secondary can show reading
  fell alongside quality; it cannot show reading is why. Both are measured on
  the same responses.
- **[#116]'s own endpoint**, which is volunteered *work* displacing the answer,
  and which is still [round 50](round-50.md)'s null at 0.56 power.

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#259]: https://github.com/JordanMPDS/laconic/issues/259
[#263]: https://github.com/JordanMPDS/laconic/issues/263
