# Round 26

**Verdict: accept.** The token target passed at 8 of 8, p = 0.008;
`quality_fails` fell; the holdout is level; step 8 reproduces the compression.
**The disclosed composition effect is the thing to read before citing this
round**: the licence moves answers into the hands-back stratum, replicated at
p = 0.029 and p = 0.000002, and that stratum fails at about two thirds.

*Everything above the horizontal rule below was registered at 15:09 UTC on
2026-08-24, before any generation.*

**Rules under test:** `rules_cksum` 3694954268 (the earned licence, merged in
#127) against 1830906901 (the pre-licence text, `rules/` at `6d19c5d`).
**Snapshots:** `evals/snapshots/loop/round-26-licence.json` and
`round-26-control.json`, plus the matching `-judgments.json`.

## Why this round exists

Round 25 measured the licence correctly and was rejected by a defective rule.
Its token target passed at 8 of 8 cells, p = 0.008, and both [#132] tripwires
cleared; it lost on `quality_fails` 39 → 41 whose arbitration could not clear
cells with a control count of 0. That defect is [#133], now fixed and validated
by re-scoring all 23 stored rounds, of which only round 25 moves
([`count-vs-rate.md`](count-vs-rate.md)).

**A rule repaired after seeing the round it rejected cannot also score that
round.** So round 25's data is not re-used for a verdict. This round generates
the comparison again, under the fixed gate, with the registration written
first.

## Hypothesis

> The earned licence (`rules_cksum` 3694954268) moves `output_tokens` **down on
> all eight `design-*` cases on sonnet** against the pre-licence text
> (1830906901) generated in the same interleaved batch, while `one_turn` on
> `design-cache`, `design-realtime` and `design-upload` does **not rise**, and
> the fatal counters over the generated scope hold.

Identical to round 25's hypothesis, deliberately. The only thing that changed
is the gate.

Registered scoring:

```
--target output_tokens \
  --target-cases design-alerting,design-audit-log,design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --target-models sonnet
```

and the co-requirement, scored separately:

```
--target one_turn --target-cases design-cache,design-realtime,design-upload --target-models sonnet
```

`one_turn` is cited **uninflated**, the explicit statement rule 6 requires,
because both sides are one interleaved batch.

## Registered scope

Sonnet only, eight `design-*` cases, **25 reps a side**, 400 generations, one
run in flight, both sides from one CLI build, alternating one rep at a time
between two trees. The reasons are round 25's and unchanged: seven of eight
haiku design cells never vote, `one_turn` is sonnet-only by registered rule,
and 25 reps is the depth at which the two high-dispersion cells can resolve the
effect.

**25 reps a side is also what puts this round above `CELL_TEST_MIN_RUNS`**, so
the fixed gate is in force rather than dormant. That is deliberate and is the
point of re-running rather than re-scoring.

## Registered stop conditions

1. **[#132], as in round 25.** Not scored on `report.py`'s verdict alone if the
   token result flips when `design-cache` and `design-realtime` on sonnet are
   dropped, or if the median shift lands within 15% of the scoped floor.
2. **[#133]'s own screen must not be the whole verdict.** If the round accepts
   **only** because a risen cell was screened as inside sampling, the round doc
   states which cells were screened, with their counts and p-values, next to
   the verdict. An accept that rests on the new screen is reported as resting
   on it.
3. **A quality regression that clears the screen is fatal as always.** The fix
   raised the evidence bar for calling a rise a loss; it did not remove the
   loss.

## Method

Two trees, one interleaved pass, alternating one rep at a time:

- Treatment: the repository at `795f53b`, `rules_cksum` 3694954268.
- Control: a detached worktree with `rules/` from `6d19c5d`,
  `rules_cksum` 1830906901. `rules/laconic.md` in the repository is never
  modified.

Both verified before the first generation. The driver waits and retries a rep
that fails rather than marching on, because two usage-limit windows interrupted
round 25.

---

## Results

**Generation:** 400 runs, 200 a side, 25 reps, **0 failed**. Both sides on CLI
2.1.241 at `cases_cksum` 2423244529, treatment `rules_cksum` 3694954268 and
control 1830906901, one run in flight throughout. Generated 15:09 to 21:49 UTC.

### The registered target: accept

| scope | cells improved | sign p | median shift | scoped floor |
|---|--:|--:|--:|--:|
| all eight design cases (registered) | 8 of 8 | **0.008** | **1294** | 1032.5 |
| tripwire 1: without `design-cache` and `design-realtime` | 6 of 6 | 0.031 | 1286 | 920.6 |

Tripwire 2: the shift is 25% above the floor, outside the registered ±15% band.
**Both [#132] tripwires clear, as they did in round 25.**

### `quality_fails` fell, so the [#133] screen never ran

**46 → 43.** Per case, `not_exercised` excluded from the denominator:

| cell | control | licence |
|---|--:|--:|
| `design-alerting` | 12/25 | 11/25 |
| `design-audit-log` | 0/25 | 0/25 |
| `design-cache` | 11/24 | 12/25 |
| `design-rate-limit` | 0/25 | 1/25 |
| `design-realtime` | 14/25 | 14/25 |
| `design-retry` | 0/25 | 1/25 |
| `design-search` | 1/25 | 0/25 |
| `design-upload` | 8/25 | 4/25 |
| **pooled** | **46/199 (23.1%)** | **43/200 (21.5%)** | 

Fisher p = 0.720. The round-wide counter fell, so no cell was ever screened and
`_sample_covers` was not consulted once.

**Registered stop condition 2 is satisfied in the strongest form available:
this accept reads identically under the pre-[#133] gate.** The instrument fix
is not load-bearing here, which is the cleanest possible answer to the worry
that the rule was repaired to suit a result.

### The co-requirement holds, and it is marginal

`one_turn` on `design-cache`, `design-realtime` and `design-upload`:

| | control | licence | one-sided rise |
|---|--:|--:|--:|
| round 25 | 29/75 | 33/75 | 0.310 |
| round 26 | 34/75 | 43/75 | **0.096** |
| pooled | 63/150 | 76/150 | **0.082** |

No significant rise at alpha, so the registered condition holds by the letter.
It has now leaned the same way in two independent interleaved batches, and that
is worth more than either round's p-value. Round-wide the round-26 figure is
66 → 77.

`report.py` prints `REJECT: one_turn` because a `--target` must improve to
clear; the hypothesis registered non-inferiority.

### Disclosure, and the reason the holdout matters: the hands-back shift replicated

| draw | hands-back fails | resolves fails | share handing back |
|---|--:|--:|--:|
| round 25 control | 3/16 | 36/184 | 8.0% |
| round 25 licence | 10/21 | 31/178 | 10.6% |
| round 26 control | 1/6 | 45/194 | **3.0%** |
| round 26 licence | 12/28 | 31/172 | **14.0%** |

In round 26 the **share** of answers that hand the decision back is 6 of 200
against 28 of 200, Fisher **p = 0.0001**, and that stratum fails at 12 of 28
against the control's 1 of 6. The flat quality count is a cancelling pair: the
resolving stratum improved, 45/194 to 31/172, while mass moved into the worse
stratum.

Round 25 showed the same direction on the share (16/200 against 21/200,
p = 0.31) and its failure spike did not replicate. **The share shift is what
replicated, and it is the signature `_quality_strata` exists to expose** —
round 15 passed every step-7 gate carrying it and was killed by the holdout.

### Step 9: the holdout is level

Both arms interleaved a rep at a time between the two trees, all six reserved
cases, both models, n=10. **240 generations, 0 failed, 0 backoff waits.**

Per the loop's rule, directions and significance only:

| holdout case | direction | p |
|---|---|--:|
| `holdout-design` | worse | 0.7140 |
| `holdout-destructive` | better | 0.6599 |
| `holdout-explain` | worse | 1.0000 |
| `holdout-ordered` | level | 1.0000 |
| `holdout-short` | better | 0.2049 |
| `holdout-verdict` | worse | 0.6614 |

**Round-wide: better, p = 0.7766.** No case is worse at significance, and the
licence side returned fewer failures overall. **Round 15's edit died here; this
one does not.**

Two honest limits on what that buys:

- **The holdout cannot speak to the hands-back stratum.** `_quality_strata`
  only reads quality-graded cases, and the reserved set has none, so both sides
  return 0 of 0. The signature that motivated running this step early is
  untested by it. What the holdout does establish is that nothing else
  regressed on cases the loop has never optimised against.
- **No compression on the reserved set**: median output 746 for the control
  against 752 for the licence. Only one reserved case is a design question, so
  this is expected rather than surprising, and it is disclosure, not a gate.

**Order note.** The loop numbers replication as step 8 and the holdout as step
9. This round ran the holdout first, deliberately: the hands-back replication
made it the decisive test, and round 15's precedent is that a dev-set
replication would not have caught what the holdout catches.

### Step 8: the replication, scoped to the open question

A second independent interleaved draw of both arms, `design-cache`,
`design-realtime` and `design-search`, 25 reps a side. **150 generations, 0
failed.** `cases_cksum` 2673025675 for the three-case scope, CLI 2.1.241, same
two trees.

**Scope disclosure.** The full eight-case replication was stopped after six
generations and replaced with this one, because the quota cost was not worth the
marginal information: the token target had already passed at 8 of 8, p = 0.008,
in two independent interleaved batches, so the open question was the hands-back
share alone. These three cases are where those responses concentrate in round 26
(6, 6 and 6 against a control's 0, 0 and 0). **Choosing them after seeing where
the effect appeared would be post-hoc selection for a gate; this is a disclosed
covariate and not a gate**, and the scope is named here rather than presented as
a registered replication of the whole target.

| | control | licence | Fisher |
|---|--:|--:|--:|
| share handing the decision back | 5/75 (6.7%) | **15/75 (20.0%)** | **0.0287** |
| hands-back failures | 2/5 | 10/15 | — |
| resolving failures | 26/70 (37%) | 15/60 (25%) | — |
| quality overall | 28/75 | 25/75 | 0.733 |
| median `output_tokens` | 2238 | **1476** | −34% |

The same three cells in round 26 itself read control 0/75 against licence 18/75,
p = 0.000002.

**The hands-back shift replicates.** Two independent interleaved batches, both
significant, and in both the hands-back stratum fails at about two thirds while
the resolving stratum fails at about a quarter. **The flat quality count is a
composition effect, not an absence of movement**: the licence moves answers into
the stratum that fails more, and the answers that still resolve get better, and
the two cancel.

## Verdict: accept, with the composition effect disclosed

Every registered gate passed:

- the token target at 8 of 8, p = 0.008, shift 1294 against a 1032.5 floor,
  robust to dropping the two high-dispersion cells;
- `quality_fails` **fell**, 46 → 43, so [#133]'s screen was never invoked and
  this accept reads identically under the pre-[#133] gate;
- `one_turn` did not rise significantly, though it has now leaned the same way
  twice (pooled 63/150 against 76/150, p = 0.082);
- the holdout is level, better at p = 0.7766, with no case worse at
  significance;
- step 8 reproduces the compression, −34% on its three cases.

**What a human has to weigh, because no gate scores it.** The licence makes the
model hand the decision back three to four times as often, and those answers
fail at about two thirds. The rules text licenses exactly this — "Ask for the
fork you cannot resolve" — so the behaviour is intended; what was not intended
is that the judge grades most of those answers as failures. The net quality
count is flat across three independent batches, so the trade is neutral by
measurement and a product judgment by preference.

**The loop proposes; a human merges.** The licence stays in place on this
branch. Nothing here reverts it, and nothing here claims the composition effect
is harmless.
