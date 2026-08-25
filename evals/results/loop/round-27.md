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
[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#127]: https://github.com/JordanMPDS/laconic/pull/127
[#133]: https://github.com/JordanMPDS/laconic/issues/133
[#138]: https://github.com/JordanMPDS/laconic/issues/138

---

## Results

### Stage 1: nothing kills, and nothing yet supports the edit

**Generation:** 160 runs, 80 a side, 10 reps, **0 failed, 0 backoff waits**,
16:01 to 17:24 UTC. Both sides CLI 2.1.241, `cases_cksum` 2423244529,
treatment `rules_cksum` 136269960 at `3628cc8`, control 3694954268 at
`5cb0f28`, neither tree dirty. **This is the first round whose runs carry
[#142]'s `tools` list** — 160 of 160. Nothing scores it.

**Registered stop condition 1 (the target) does not kill.** `one_turn` on the
three registered cells, sonnet, uninflated because this is one interleaved
batch:

| cell | control | edit |
|---|--:|--:|
| `design-cache` | 6/10 | 4/10 |
| `design-realtime` | 1/10 | 4/10 |
| `design-upload` | 7/10 | 7/10 |
| **pooled** | **14/30 (47%)** | **15/30 (50%)** |

One-sided rise p = 0.500, fall p = 0.645. Dead flat. Per the registration a
flat stage-1 read is not a failure, so the round proceeds — but it is worth
saying plainly that **at this depth the registered target shows nothing at
all**, in either direction.

**Registered stop condition 2 (compression) holds.** `output_tokens`
stratified per [#131], all eight cells voting in the grounded stratum, none
refused:

| cell | stratum | control | edit | shift |
|---|---|--:|--:|--:|
| `design-alerting` | grounded | 2314 | 2803 | +489 |
| `design-audit-log` | grounded | 3194 | 3943 | +749 |
| `design-cache` | grounded | 2532 | 2900 | +368 |
| `design-rate-limit` | grounded | 2196 | 1879 | −317 |
| `design-realtime` | grounded | 2176 | 2061 | −115 |
| `design-retry` | grounded | 2324 | 2795 | +472 |
| `design-search` | grounded | 1432 | 1316 | −116 |
| `design-upload` | grounded | 3244 | 2319 | −925 |

Four fell, four rose, sign test p = 1.000, median shift **+126 tokens against
a scoped floor of 542.5**. The shift is well inside the floor, so round 26's
compression is not being spent. Non-inferiority holds.

**`turns` does not reject.** Two cells rose (`design-search` +1.0,
`design-rate-limit` +0.5), none fell, against a measured turn floor of 0.813.
A rise needs both estimators — past the floor *and* a sign test across cells —
and 2 of 8 rising with 0 falling is p = 0.500. Only `design-search` clears the
floor at all.

### The warning sign, disclosed

**Round-wide `one_turn` over all eight cases leans the wrong way: 22/80 →
30/80, one-sided rise p = 0.166.** That is not the registered scope and it is
not significant, but the direction is the opposite of what [#138] predicts, and
if the edit is buying its brevity by reading *less* then it is making the
failure worse rather than better. Stage 2 at 25 reps a side is what resolves
it, and this paragraph is registered as the thing to look at when it lands.

### The hands-back cross-tab moves as predicted, far from significance

Computed with `report.py`'s unmodified `ASKS_BACK` regex. Eight cases, sonnet:

| | control | edit | one-sided fall |
|---|--:|--:|--:|
| hands the decision back | 8/80 (10%) | 5/80 (6%) | 0.291 |
| ... and never read (1 turn) | 7/80 | 4/80 | 0.274 |
| ... after reading | 1/80 | 1/80 | — |

Both movements are in the registered direction and neither is close to alpha at
10 reps a side. **The control side is the useful check here**: master reads
8/80 (10%) hands-back, against round 26's licence side at 28/200 (14%) and its
pre-licence control at 6/200 (3%). Master behaves the way round 26 said it
does, so the instrument is reading the same thing it read yesterday.

### Stage 2: the accepting read — the registered target misses alpha

**Generation:** extended to 400 runs, 200 a side, 25 reps, **0 failed, 0
backoff waits**, 18:47 to 20:46 UTC. Same two trees, same CLI, same
`cases_cksum`.

**The registered target, `one_turn` on the three registered cells, sonnet,
uninflated because this is one interleaved batch:**

| cell | control | edit |
|---|--:|--:|
| `design-cache` | 17/25 | 10/25 |
| `design-realtime` | 5/25 | 8/25 |
| `design-upload` | 21/25 | 15/25 |
| **pooled** | **43/75 (57.3%)** | **33/75 (44.0%)** |

One-sided fall **p = 0.151** (inflated, 0.188). A 13-point drop in the right
direction that does not reach alpha at 75 runs a side.

**This is the rejection.** The loop's standing requirement is that the metric
the hypothesis named beats the noise floor, and p = 0.151 does not. Extending
to more reps until it clears is precisely the optional stopping the staged
buying rule was written to avoid, and stage 2 was registered as the accepting
read.

**Instrument check.** This round's control read 43/75 on those three cells.
Round 26's licence arm — the same rules text, the same cases, the same CLI —
read 43/75 on the same three cells. The two draws agree exactly.

### The stage-1 warning was sampling

Round-wide `one_turn` over all eight cases looked as though it leaned the wrong
way at 10 reps a side, 22/80 → 30/80. At 25 reps a side it is **76/200 →
76/200**, dead flat. The paragraph registered at stage 1 as the thing to check
is answered: there is no round-wide reading regression.

### The co-requirements both hold

`output_tokens`, stratified per [#131], all eight cells voting grounded, none
refused: four fell, four rose, sign test p = 1.000, **median shift +37 tokens
against a floor of 647.3**. Round 26's compression is intact.

`turns`: three cells rose (`design-search` +1.0, `design-audit-log` +0.5,
`design-rate-limit` +0.5), none fell, floor 0.906. Only `design-search` clears
the floor and the sign test is p = 0.250, so `turns` does not reject. It has
now leaned the same way at both depths — 2 of 8 rising at 10 reps, 3 of 8 at
25, never a fall — and that is disclosed rather than scored.

### The disclosed covariate landed as predicted

Computed with `report.py`'s unmodified `ASKS_BACK` regex, sonnet:

| | control | edit | one-sided fall |
|---|--:|--:|--:|
| **eight cases**, hands back | 23/200 | 12/200 | **0.0448** |
| ... and never read (1 turn) | 19/200 | 9/200 | **0.0436** |
| ... after reading | 4/200 | 3/200 | — |
| **registered scope**, hands back | 9/75 | 2/75 | **0.0327** |
| ... and never read | 9/75 | 2/75 | **0.0327** |
| ... after reading | 0/75 | 0/75 | — |

This is stop condition 4's registered prediction, in the form it was
registered: the share falls, and it falls **because the `num_turns == 1`
hands-back count falls** — 19 to 9 — while answers that hand back after
reading are untouched, 4 to 3. On the registered scope every hands-back answer
on both sides was an unread one, and the count went 9 to 2.

**It cannot rescue the round, and it is not being allowed to.** Hands-back was
registered as disclosure precisely so that it could not become the accept
criterion after the gate target missed. Substituting it now would be the exact
move pre-registration exists to prevent, and the fact that the direction was
written down in advance does not make it a gate — `turns` needed an offline
re-score across rounds 05 to 26 before it was allowed to reject anything
([#49]), and this metric has had none.

## Verdict: reject

The registered target missed at p = 0.151. The edit is reverted whole, per the
loop's rule that a rejected round reverts everything including the parts that
worked.

**What the round establishes anyway**, and what makes it worth the 400
generations rather than a dead end:

1. **The mechanism in [#138] is real and the edit addresses it.** Unread
   hands-back answers — the stratum round 26 measured failing at about two
   thirds — fell by half, 19/200 to 9/200, on a direction registered before
   generation. That is the strongest evidence the loop has produced on this
   question, and it is nominally significant on a covariate that was named in
   advance rather than found afterwards.
2. **It did not buy that by suppressing reading.** Round-wide `one_turn` is
   exactly flat and `output_tokens` is inside its floor, so the edit is not
   trading reading rate or round 26's compression for the improvement.
3. **The gate the loop owns cannot see this effect at the depth the loop
   buys.** `one_turn` is a proxy for the harm, and it moved 13 points without
   reaching alpha, while the thing actually predicted moved and did. That is an
   instrument gap, not a null result.

**The next move is a metric, not another rule edit.** Promoting the hands-back
count to a scoreable target needs what [#49] needed: implement it in
`report.py`, re-score every stored round offline, establish that it does not
fire on the archive, and only then register a round against it. Filed as the
follow-up to [#138]. Re-running this same edit against a gate built after
seeing this round would be scoring an edit with a rule repaired to suit it —
[#133]'s mistake, which round 26 had to spend a whole round undoing.
