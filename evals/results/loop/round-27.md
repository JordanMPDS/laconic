# Round 27

**Status: registered, not yet run.**

*Everything above the horizontal rule below was registered at 15:58 UTC on
2026-08-25, before any generation.*

**Rules under test:** `rules_cksum` 136269960 (the ask earned by reading)
against 3694954268 (master, the earned licence merged in #127, `rules/` at
`5cb0f28`).
**Snapshots:** `evals/snapshots/loop/round-27-edit.json` and
`round-27-control.json`, plus the matching `-judgments.json`.

## Why this round exists

Round 26 accepted the design-question licence and disclosed a composition
effect it could not clear: the licence moves answers into the stratum that
hands the decision back, replicated at p = 0.0287 and p = 0.000002, and that
stratum fails at about two thirds. [#138] traces the mechanism to reading
rather than to asking.

Cross-tabulated against `num_turns`, from [#138]:

| | read the repository | did not read |
|---|--:|--:|
| licence, resolves | 13/117 failed (11%) | 18/55 (33%) |
| licence, hands back | **0/6 (0%)** | **12/22 (55%)** |
| control, hands back | 1/6 (17%) | none occurred |

Handing the decision back is harmless when the answer read first — zero
failures in six. Twenty-two of the licence's 28 hands-back answers never opened
a file, and those fail at 55%.

The licence already carries an earned-by-reading condition on the permission to
be **brief**. It carries none on the permission to **ask**. This round adds it.

## The edit

One line, in the `level: full` design-question licence:

```diff
-  for the depth you left out. Ask for the fork you cannot resolve. Explaining
-  something that already exists is a different request, and it is protected
-  above.
+  for the depth you left out. Ask for the fork that survives reading, not the
+  one reading would settle. Explaining something that already exists is a
+  different request, and it is protected above.
```

Nothing moves section. The clause stays under `level: full`, where round 10
established the licence belongs, and inherits that section's limits without
being told them.

## Hypothesis

> Editing the design-question licence's asking permission — "Ask for the fork
> you cannot resolve" becomes "Ask for the fork that survives reading, not the
> one reading would settle" — should move `one_turn` **down** on
> `design-cache`, `design-realtime` and `design-upload` on sonnet, against
> master rules generated in the same interleaved batch, while `quality_fails`
> does not rise and `output_tokens` over the eight `design-*` sonnet cases does
> not rise.

Registered scoring, the target:

```
--target one_turn \
  --target-cases design-cache,design-realtime,design-upload \
  --target-models sonnet
```

The scope is the registered `one_turn` scope, not a choice this round made:
those are the three cells with variance *and* a measured link to answer
quality. `design-search`, where [#138]'s replication concentrated, has variance
and no such link and is therefore excluded from the target — it is generated
and reported, but it does not vote.

`one_turn` is cited **uninflated**, the explicit statement rule 6 requires,
because both sides are one interleaved batch.

Registered co-requirements, scored separately:

```
--target output_tokens \
  --target-cases design-alerting,design-audit-log,design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --target-models sonnet
--target turns --target-cases <the same eight> --target-models sonnet
```

`output_tokens` and `turns` are registered as **non-inferiority**: neither may
rise. `report.py` prints `REJECT` for a target that fails to improve, and for
these two that string is not the verdict — the same shape round 26 recorded for
its own `one_turn` co-requirement.

## Registered scope and staging

Sonnet only, eight `design-*` cases, 25 reps a side — round 26's scope exactly,
so the two rounds' numbers sit beside each other without a scope caveat. Bought
in stages, per the loop's standing order to score the cheap target first:

1. **Stage 1, the kill screen.** All eight `design-*` cases, sonnet, **10 reps
   a side, 160 generations, no judging.** `one_turn` is free off `num_turns`
   and `output_tokens` needs no judging either, so both registered stop
   conditions 1 and 2 are readable here. **This read can only kill, never
   accept.** Registering it that way is what keeps staged buying from becoming
   optional stopping: there is no draw at which the round stops early and
   declares success.

   *Amended at 16:04 UTC on 2026-08-25, before any generation, and the reason
   is an instrument constraint rather than anything about the data.* The stage
   was registered six minutes earlier as three cases and 60 generations.
   `run.py` takes `--cases` as a single glob and stamps a `cases_cksum` over
   exactly the cases the snapshot covers ([#69]), so a three-case stage 1
   cannot be extended into an eight-case stage 2 — the guard refuses the
   resume, and those 60 generations would have to be thrown away and bought
   again. Widening stage 1 to the glob round 26 used makes stage 2 a pure
   extension of reps. It costs 100 more generations and it buys the
   `output_tokens` co-requirement a stage earlier than registered.
2. **Stage 2, the accepting read.** Extend the same snapshot to 25 reps a side
   — 240 further generations, 400 in total, which is round 26's exact spend.
   `one_turn` is scored here, at 25 a side.
3. **Stage 3, the fatal counters.** Judge the eight-case batch and score
   `quality_fails`, `never_cut_failures`, `safety_fails` and
   `violations_total`.
4. **Stage 4.** Step 8 replication, then the step 9 holdout. Round 26 ran the
   holdout before the replication because the hands-back signature made it
   decisive; this round inherits that reasoning and will do the same.

Stop at the first stage that fails. `run.py` resumes by key, so a stage that
extends an earlier one buys only the reps it adds.

## Registered stop conditions

1. **Stage 1 kills on a rise.** If `one_turn` over the three registered cells
   has risen at 10 reps a side, one-sided and uninflated at alpha 0.05, the
   round stops and the edit is reverted. A flat stage-1 read is not a failure
   and the round proceeds to stage 2.
2. **The edit may not buy reading back with round 26's compression.** If
   `output_tokens` over the eight design cases rises past the scoped floor, the
   round is rejected whatever `one_turn` did. Round 26's accept was a −34%
   compression on these cells and this round is not entitled to spend it.
3. **A fatal counter that rises rejects**, subject to [#133]'s measured-rate
   screen. If the accept rests **only** on a cell being screened as sampling,
   the round doc names the screened cells with their counts and p-values, next
   to the verdict.
4. **The hands-back share is disclosure, not a gate.** It is computed with
   `report.py`'s existing `ASKS_BACK` regex, unmodified — re-tuning a detector
   after seeing what it found is how a disclosure becomes a story, and that
   expression is deliberately the one `design-quality-covariate.md` measured
   the covariate with. Promoting it to a gate would need its own offline
   re-score across the archive, the way `turns` earned its gate in [#49], and
   that is not this round.

   The predicted direction, registered so it can be read as a prediction rather
   than a description: the share of answers handing the decision back falls
   from round 26's 28/200 toward its control's 6/200, and it falls **because
   the `num_turns == 1` hands-back count falls**, not because answers that read
   first stopped asking. Hands-back answers that read may hold at any level —
   zero of six failed.

## Method

Two trees, one interleaved pass, alternating one rep at a time, adapted from
round 26's driver:

- Treatment: this branch, `rules_cksum` 136269960.
- Control: a detached worktree at master `5cb0f28`, `rules_cksum` 3694954268.

Both verified before the first generation. The driver waits and retries a rep
that fails rather than marching on, with escalating backoff scoped to the rep
being generated.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#127]: https://github.com/JordanMPDS/laconic/pull/127
[#133]: https://github.com/JordanMPDS/laconic/issues/133
[#138]: https://github.com/JordanMPDS/laconic/issues/138

---

## Results

*Pending.*
