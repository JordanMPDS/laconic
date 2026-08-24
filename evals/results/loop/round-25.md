# Round 25

**Verdict: reject.** `quality_fails` 39 → 41, sustained by the replication.
**The registered token target passed** — median shift 1562 on 8 of 8 cells,
p = 0.008 — and both [#132] tripwires cleared, so the floor did not decide this
round.

*Everything above the horizontal rule below was registered at 02:12 UTC on
2026-08-24, before any generation.*

**Rules under test:** `rules_cksum` 3694954268 (the earned licence, merged in
#127) against `rules_cksum` 1830906901 (the pre-licence text, `rules/` at
`6d19c5d`).
**Snapshots:** `evals/snapshots/loop/round-25-licence.json` and
`round-25-control.json`, plus the two matching `-judgments.json`.

## Why this round exists

Round 24 accepted at step 7 and survived step 8b under the baseline registered
before it ran. A third-party review then showed the step 8b gate flips when a
better-matched baseline is substituted: against `licence-vs-master-master.json`,
byte-identical baseline text generated on the same CLI build as all three
treatment generations, the same treatment data reads 8 of 8 at p = 0.0078 with a
median shift of 1089 inside a 1269.6 floor, which `report.py` rejects
(`REVIEW-step8b.md:693-712`).

The cause is baseline matching, not the edit: round 24 replicated the treatment
side three times against a baseline drawn once, eight days and one CLI build
away. **This round removes that error by construction** — both sides are
generated in one interleaved batch on one CLI build, which is the method
`interleaved-batch.md` established and the loop has never applied to a token
target.

The edit is already merged and shipping. This round decides whether it keeps its
place or is reverted.

## Hypothesis

> The earned licence (`rules_cksum` 3694954268) moves `output_tokens` **down on
> all eight `design-*` cases on sonnet** against the pre-licence text
> (1830906901) generated in the same batch, while `one_turn` on `design-cache`,
> `design-realtime` and `design-upload` does **not rise**, and the fatal
> counters over the generated scope hold.

Registered scoring, exactly as it will be run:

```
--target output_tokens \
  --target-cases design-alerting,design-audit-log,design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --target-models sonnet
```

and the co-requirement, scored separately:

```
--target one_turn --target-cases design-cache,design-realtime,design-upload --target-models sonnet
```

**`one_turn` is cited uninflated**, as `ONE_TURN_PHI` = 3.39 corrects for
between-round drift that an interleaved batch does not contain. This is the
explicit statement rule 6 requires. The inflated figure will be printed beside
it.

## Registered scope, and what it gives up

**Sonnet only, eight cases, 25 reps a side.** 400 generations, one run in flight
at any time, both sides from one CLI build.

- **Why sonnet only.** Seven of the eight haiku design cells sit below
  `TOKEN_CELL_MIN_BASELINE` and never vote (`round-24.md:128`), and the eighth,
  `design-audit-log`/haiku, clears the floor by 263 tokens on a five-rep draw,
  which is the coin flip the review named (`REVIEW-step8b.md:454-460`). The
  `one_turn` co-requirement is sonnet-only by registered rule 2 in any case. Eight
  sonnet cells clear the six-cell minimum the scoped sign test needs.
- **Why 25 reps.** This is the depth round 24 registered for its own pooled step
  8b, on the argument that pooling to 25 reps a cell more than halves
  `design-cache`/sonnet's standard error and is "the right answer to dispersion,
  not exclusion" (`round-24.md:247`). It is chosen so that the two high-dispersion
  cells (`design-cache`/sonnet at CV 0.63, `design-realtime`/sonnet at 0.50) can
  resolve the effect rather than vote noise.
- **What this round does not re-test.** The non-design cases, both models on
  everything outside the eight design cases, and the holdout. Round 24's
  full-round fatal counters and its level holdout stand; this round re-tests the
  token and reading endpoint only, and its fatal counters run over the scope it
  generates.

## Registered stop condition for #132

**If the verdict hinges on the 1200-token floor, stop and settle
[#132](https://github.com/JordanMPDS/laconic/issues/132) before scoring.**
Concretely, the round is not scored on `report.py`'s verdict alone if either
holds:

1. The accept-or-reject flips when the two high-CV cells (`design-cache` and
   `design-realtime` on sonnet) are removed from the scope.
2. The median shift lands within 15% of the scoped floor in either direction.

Registering this before the run is the point: round 24's concession was that a
dispersion criterion arrived after seeing which cells failed, and a criterion
chosen after the numbers are in scores whatever moved.

## Method

Two trees, one interleaved pass, alternating one rep at a time:

- Treatment: the repository at `823bd78`, `rules_cksum` 3694954268.
- Control: a detached worktree at `823bd78` with `rules/` checked out from
  `6d19c5d`, `rules_cksum` 1830906901. `rules/laconic.md` in the repository is
  never modified.

Both checksums were verified before the first generation. Both sides read the
same `evals/cases` and carry the same `cases_cksum`.

---

## Results

**Generation:** 400 runs, 200 a side, 25 reps, **0 failed** in the final file.
Both sides on CLI 2.1.241, both at `cases_cksum` 2423244529, treatment
`rules_cksum` 3694954268 and control 1830906901 as registered.

**The batch was interrupted and resumed.** An account usage limit hit at
05:45 UTC and every generation from rep 11 onward failed with empty text on
both sides. Reps 0 to 10 were clean and symmetric, 88 good runs a side, and the
interruption fell in the same place on both arms. `completed_keys` filters on
`ok`, so the resume regenerated exactly the failed keys; reps 11 to 24 were
generated between 06:31 and 09:00 UTC on the same CLI build. The 4.5-hour gap
between rep 10 and rep 11 is symmetric across the two arms and is recorded here
rather than being smoothed over.

### The registered target: passes

| scope | cells improved | sign p | median shift | scoped floor |
|---|--:|--:|--:|--:|
| all eight design cases (registered) | 8 of 8 | **0.008** | **1562** | 1236.0 |
| tripwire 1: without `design-cache` and `design-realtime` | 6 of 6 | 0.031 | 1572 | 1135.3 |

### Both #132 tripwires clear

1. **The verdict does not flip when the two high-CV cells are removed.** The
   token target passes at 6 of 6 without them, on a shift that is if anything
   slightly larger.
2. **The shift is 26% above the scoped floor** (1562 against 1236), outside the
   registered ±15% band.

**So the floor is not what decided this round**, and the round is scored
without waiting on [#132]. That is the question round 24 could not answer:
the licence's compression survives a baseline generated in the same batch, on
the same CLI build, against the same case material.

### The co-requirement holds

`one_turn` on the three [#88] cases went **29 to 33** (p = 0.641 inflated by
`ONE_TURN_PHI`, **0.746 uninflated**, which this round may cite because both
sides are one interleaved batch). Round-wide it went 65 to 68. No significant
rise, which is what the hypothesis registered.

`report.py` prints a literal `REJECT: one_turn` line when `one_turn` is passed
as `--target`, because a target must *improve* to clear. The hypothesis
registered non-inferiority, not improvement, and the line is read accordingly.

### What rejects the round: `quality_fails` 39 to 41

Risen cells: `design-alerting`/sonnet +3, `design-cache`/sonnet +2,
`design-rate-limit`/sonnet +2, `design-retry`/sonnet +2.

Per-cell, `not_exercised` verdicts excluded from the denominator:

| cell | control | licence | Fisher |
|---|--:|--:|--:|
| `design-alerting` | 9/25 | 12/24 | 0.393 |
| `design-audit-log` | 1/25 | 0/25 | 1.000 |
| `design-cache` | 7/25 | 9/24 | 0.551 |
| `design-rate-limit` | 0/25 | 2/25 | 0.490 |
| `design-realtime` | 14/25 | 11/25 | 0.572 |
| `design-retry` | 0/25 | 2/25 | 0.490 |
| `design-search` | 1/25 | 0/25 | 1.000 |
| `design-upload` | 7/24 | 5/23 | 0.740 |
| **pooled** | **39/199** | **41/196** | **0.803** |

The gate is a raw count comparison, so a two-verdict difference on ~200 graded
responses a side fires it. That is the [#52] situation the arbitration
mechanism exists for, and the loss is marked arbitrable.

### Disclosure: the two quality strata moved in opposite directions

`report.py` prints it and it is not a count artefact. Answers that **hand the
decision back** went **3 of 16 to 10 of 21** — worse — while answers that
resolve it went 36 of 184 to 31 of 178. A flat quality count hides this. The
licence appears to move answers into the hands-back stratum, and that stratum
fails more often.

### Arbitration: the risen cells did not clear

A second independent draw of the treatment side, same eight cases, same 25
reps, same CLI build: `round-25-arbitration.json`, 200 runs, 0 failed. It was
itself interrupted by a second usage-limit window at 11:19 UTC and resumed;
152 keys were regenerated between 13:12 and 14:28 UTC.

`report.py` clears a risen cell only when its replicated count is **at or below
the control's**. None of the four were:

| cell | control | round | replication | pooled treatment | Fisher (control vs pooled) |
|---|--:|--:|--:|--:|--:|
| `design-alerting` | 9/25 | 12/24 | 10/25 | 22/49 | 0.619 |
| `design-audit-log` | 1/25 | 0/25 | 0/25 | 0/50 | 0.333 |
| `design-cache` | 7/25 | 9/24 | 9/25 | 18/49 | 0.604 |
| `design-rate-limit` | 0/25 | 2/25 | 1/25 | 3/50 | 0.546 |
| `design-realtime` | 14/25 | 11/25 | 9/24 | 20/49 | 0.230 |
| `design-retry` | 0/25 | 2/25 | 2/25 | 4/50 | 0.294 |
| `design-search` | 1/25 | 0/25 | 0/24 | 0/49 | 0.338 |
| `design-upload` | 7/24 | 5/23 | 9/25 | 14/48 | 1.000 |
| **pooled** | **39/199 (19.6%)** | 41/196 | 40/198 | **81/394 (20.6%)** | **0.829** |

**The gate rejects and the replication sustains it. The rates do not
distinguish the arms at 394 treatment runs against 199 control runs.** Both
statements are true, and the first is the verdict: the rule is a count
comparison, and two of the four risen cells have a control count of 0, which
any failure at all exceeds. Re-specifying the rule after seeing which cells
failed is the move round 24 was criticised for, so it is not done here. It is
filed instead.

### The hands-back stratum did not replicate

Computed with `report.py`'s own `_quality_strata` over each snapshot:

| draw | hands-back | resolves | share handing back |
|---|--:|--:|--:|
| control | 3/16 (18.8%) | 36/184 (19.6%) | 8.0% |
| round | **10/21 (47.6%)** | 31/178 (17.4%) | 10.6% |
| replication | **3/23 (13.0%)** | 37/177 (20.9%) | 11.5% |

Pooled, hands-back is 13 of 44 for the treatment against 3 of 16 for the
control, Fisher **p = 0.52**, and the share of answers that hand a decision
back is 44/399 against 16/200, **p = 0.31**. **The round's opposite-direction
strata finding was a one-draw artefact and is withdrawn.** It is recorded
because it was reported before the replication existed.

## Verdict: reject

The registered hypothesis required the fatal counters to hold, and
`quality_fails` did not. The replication did not clear the risen cells, so the
loss stands under the loop's own rule.

What survives, and it is the thing round 24 could not establish: **the earned
licence compresses design answers by a median 1562 tokens, 8 of 8 cells, against
a baseline generated in the same batch on the same CLI build, and the result
does not depend on the two high-dispersion cells or on the 1200-token floor.**
Reading rate is flat. The quality endpoint is flat at 594 runs. The edit is
rejected on a count rule, not on a measured harm.

**Consequence.** A rejected round reverts the whole edit. The licence is merged
on master, so the revert is a PR against master, proposed here and merged by a
human like any other.

**Filed, not applied.** The arbitration rule and the fatal counters compare raw
counts rather than rates; at 25 reps a side with per-cell control counts of 0,
7 and 9, a cell can fail to clear by sampling alone. That belongs with [#131]
and [#132], and like them it needs the stored rounds re-scored before adoption.

[#131]: https://github.com/JordanMPDS/laconic/issues/131

**Method note, recorded because it cost a restart.** The first attempt invoked
`run.py` once per case into a shared snapshot. `cases_cksum` covers *the cases
in the invocation*, so the second case's invocation computed a different
checksum and the [#69] guard refused the resume — correctly. An arbitration
that spans several cases has to pass them in one invocation.

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#52]: https://github.com/JordanMPDS/laconic/issues/52
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#132]: https://github.com/JordanMPDS/laconic/issues/132
