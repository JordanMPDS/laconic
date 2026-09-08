# Round 55: the round 52 edit, scored by the gate that replaced the one that rejected it

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are the reason this round takes the
shape it does. This file, the edit and the regenerated `rules/dist/*.md` are
committed together, before any generation, following [round 38](round-38.md),
[round 47](round-47.md), [round 48](round-48.md), [round 49](round-49.md),
[round 50](round-50.md), [round 51](round-51.md), [round 52](round-52.md),
[round 53](round-53.md) and [round 54](round-54.md).

## Why this round exists

[Round 52](round-52.md) passed its registered target on every bar and was
rejected by a gate that has since been retired.

Its target: the pre-action check, narrowed to the diagnostic shape, compressed
the answer on all four scoped cases at permutation p < 0.00001, with both
content bounds perfect — no run stopped opening the fixture and no answering
run stopped naming the defect. Its reject came from round-wide `quality_fails`,
41 to 45, on four risen cells of which three reproduced under arbitration.

[Round 53](round-53.md) then ran that same fatal gate on two arms that differ
in nothing and it fired on **46.2%** of draws, with the [#52] arbitration
clearing 0 of the 231 it fired on. [Round 54](round-54.md) repriced it: a risen
cell the round cannot test on its own runs is disclosed rather than fatal, and
the round-wide count is tested one-sided and exact. Round 54's bar E was
registered in advance to require that rounds 51 and 52 stop rejecting under the
repriced gate, and it holds — round 52 at round-wide p = 0.3603.

So the edit stands at "passed step 1 and, under the current gate, step 2". What
it has never had is [step 8](../../../.claude/skills/laconic-loop/SKILL.md), the
independent replication, and step 9, the holdout. This round buys both, and it
buys step 2 again for the reason in the next section.

## Why the round regenerates step 2 instead of re-scoring round 52's

[Round 26](round-26.md) states the rule and this round obeys it:

> **A rule repaired after seeing the round it rejected cannot also score that
> round.** So round 25's data is not re-used for a verdict. This round generates
> the comparison again, under the fixed gate, with the registration written
> first.

Round 54's gate was designed after rounds 51 and 52, and named them. Its bar E
is a legitimate audit of the change and is not a verdict on the edit: the same
runs cannot both motivate a gate and be cleared by it. Round 55 therefore
generates a fresh round-wide arm, both sides in one interleaved batch, and
scores that.

> **Computed 2026-09-08, before this registration, and it is why the round is
> worth running.** Re-scoring round 52's committed step-2 arm under the
> repriced gate reads:
>
> ```
> quality rise (41 -> 45) is inside the sampling noise of the round-wide count,
> p = 0.3603, and no risen cell is testable at these reps (#259)
> ```
>
> `never_cut_failures` 2 to 2, `safety_fails` 8 to 8, `violations_total` 34 to
> 31, and the [#49] turn gate held. **This is disclosure and not a verdict**,
> per the rule quoted above. It is what makes the round worth its calls, and it
> is the number the fresh batch has to reproduce.

## The edit

Byte-identical to [round 52](round-52.md)'s, at `rules_cksum` **594915793**
against master's 136269960. It is re-applied here rather than re-derived.

```diff
-Two checks before sending:
+One check before acting, and two before sending:

+1. Is the question about something that is broken? Diagnosing it is the
+   answer; fixing it is not. Read what grounds the answer, name what is
+   wrong, and leave the fix for the user to ask for.
-1. What is the smallest set of claims that fully answers this?
-2. Is anything here something the user did not ask for?
+2. What is the smallest set of claims that fully answers this?
+3. Is anything here something the user did not ask for?
```

Carrying a proven component forward and re-stating the hypothesis is the
loop's own rule for a round that resumes an earlier one. Nothing about the text
is new; what is new is the gate it is scored by and the two steps it has never
been through.

## The hypothesis

> The pre-action check, narrowed to the diagnostic shape, should keep the
> **median prose words** falling on `conditional`'s answering stratum and on
> `fail-open`, `silent-success` and `stale-cache`, sonnet, against a second
> independent interleaved control; should clear the round-wide fatal counters
> under the [#259] gate against a fresh interleaved control; and should not
> regress the reserved holdout.

## What the round buys, in order, stopping at the first failure

The loop's standing buy order puts the cheap deterministic target first, and
here that is the replication: it is generations only and no judging is bought
if the effect does not survive it.

**1. Step 8, the replication — 400 generations, no judging.**

Four cases, sonnet, both sides simultaneous, scored by
`evals/pilot/score_compression.py` at the bars round 51 registered and round 52
was scored by, unchanged.

**Sized against the least favourable estimate**, which is [round 46](round-46.md)'s
rule and the correction round 52 made to round 51's sizing. For each case that
is the smaller of the two falls the sentence has produced — round 51's for
`conditional` and `silent-success`, round 52's for the other two — never the
larger. Bootstrapped from `round-52-control-<case>.json` directly, 400 trials
per figure for `conditional` and 300 for the rest, at the permutation test
`score_compression.py` actually runs.

> **Computed 2026-09-08, before this registration.**

| case | fall assumed | control stdev | generated per side | scored per side | power |
|---|--:|--:|--:|--:|--:|
| `conditional` | 10.5 | 16.2 | **80** | ~62 | **0.88** |
| `fail-open` | 26.5 | 36.8 | **40** | 40 | **0.77** |
| `silent-success` | 14.0 | 15.7 | **40** | 40 | **0.84** |
| `stale-cache` | 30.5 | 28.6 | **40** | 40 | **1.00** |

`conditional`'s scored stratum was 123 of 160 on round 52's control and 154 of
160 on its edit, so 80 generated buys about 62 scored. Against the 2-of-3 bar
the three generalisation cells give **0.96**, and the round's registered power
is that times `conditional`'s 0.88, or **about 0.85**. Round 52 was bought at
0.81 and its realised falls were larger than the ones assumed here on every
case.

```sh
# edit side, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 80 \
  --cases conditional --concurrency 4 \
  --snapshot evals/snapshots/loop/round-55-edit-conditional.json
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases fail-open,silent-success,stale-cache --concurrency 4 \
  --snapshot evals/snapshots/loop/round-55-edit-general.json

# control side, from a master worktree, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps 80 \
  --cases conditional --concurrency 4 \
  --snapshot <abs path>/evals/snapshots/loop/round-55-control-conditional.json
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases fail-open,silent-success,stale-cache --concurrency 4 \
  --snapshot <abs path>/evals/snapshots/loop/round-55-control-general.json
```

Four processes, so `--concurrency 4` on every one of them per [#120], and four
is the ceiling [#255] enforces. Round 52 ran eight and would now be refused.

**2. Step 2, the round-wide arm — 440 generations and 440 judgments.**

All 22 cases, both models, 5 reps a side, both sides in one interleaved batch,
sharded by model so four processes cover it, judged at `--judge-all` because the
hypothesis names `conditional`.

**3. Step 9, the holdout — 240 generations and its judgments.**

All six reserved cases, both models, n=10, both arms interleaved, per
[round 26](round-26.md)'s pattern.

About 1,300 calls if every step is reached, against round 52's 1,640.

## The design-family cost, and why no affordable round settles it

Rounds 51 and 52 each put a non-significant quality rise in the `design-*`
family, and neither could establish it. Pooled over both rounds:

| | control | edit | Fisher p |
|---|--:|--:|--:|
| round 51, `design-*` | 35/73 | 41/75 | 0.5108 |
| round 52, `design-*` | 30/80 | 34/80 | 0.6285 |
| **pooled** | **65/153 (42.5%)** | **75/155 (48.4%)** | **0.3057** |

> **Computed 2026-09-08, before this registration, from the two rounds' own
> published tables.**

Two rounds in the same direction is worth disclosing and it is not evidence of
harm. It is also not something this round can fix by buying reps: detecting a
5-point shift on a 40% base at 0.80 power needs about **1,188 verdicts a side**,
against the 80 a round-wide arm buys and the 320 that 20 reps over the whole
design family would buy at 0.36. [Round 54](round-54.md) measured the same
ceiling from the other end — at five reps a side the repriced gate needs about
**+23** round-wide before it fires four times in five.

So this round does not pretend to settle it. It adds a third independent pair
to the pooled table as a **disclosure**, and it relies on step 9 for the
protection that actually applies: `holdout-design` is a reserved design question
the loop has never optimized against, and round 15's edit is the precedent for
a holdout catching what the dev set passed.

## Registered bars

**Bar 1 (fatal): the replication.** Round 51's bars, unchanged and scored by the
same script. `conditional`'s answering stratum falls at permutation p < 0.05,
and at least **2 of the 3** `Don't edit anything.` cases fall at permutation
p < 0.05.

**Bar 2 (fatal): the round-wide counters.** `report.py` accepts against this
round's own interleaved control, over all 22 cases and both models, under the
[#259] gate. That is the standing list — `never_cut_failures`, `quality_fails`,
`safety_fails`, `violations_total` — plus the [#49] turn gate.

**Bar 3 (fatal): the holdout does not regress.** No reserved case worse at
p < 0.05, and the round-wide direction not worse at significance. Per the
loop's rule, this round publishes directions and significance only.

Two bounds, each fatal on its own whatever the target did, carried unchanged
from rounds 51 and 52:

- **An answer must still name the defect.** `locates_defect` on `conditional`'s
  answering stratum.
- **The reading rate must not fall**, on any of the four scoped cases.

## What this round cannot establish

- **Whether the `design-*` rise is real.** Stated above, with the arithmetic.
- **That the repriced gate is the right price.** Round 54 bought that argument
  and disclosed what it costs; this round spends it, it does not re-audit it.
- **Anything about the wording.** Round 52 varied the trigger against round 51
  and the two rounds' targets and costs came out the same. This round varies
  nothing.
- **[#116]'s own endpoint.** The issue is about volunteered *work* displacing
  the answer, and that is a null at 0.56 power from [round 50](round-50.md).
  Four rounds have now measured the prose this family of sentences buys instead.
  An accept here ships a compression effect and leaves the issue's endpoint
  where round 50 left it.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#52]: https://github.com/JordanMPDS/laconic/issues/52
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#259]: https://github.com/JordanMPDS/laconic/issues/259

---

*Everything above this line was registered in `dfb0ce7` at 02:46 UTC on
2026-09-08, before any generation. Everything below was computed from the runs
on 2026-09-08 between 03:21 and 05:35 UTC.*

# Results: accept on all three registered bars, with the cost signal now in three places at once

**The edit passes.** The replication reproduced the compression on all four
cases and harder than round 52 did, the round-wide counters cleared the [#259]
gate, and no reserved case regressed at significance. The edit merges.

**What to read beside that.** Every judged counter that moved, on both the dev
set and the reserved set, moved the same way — worse — and not one of them
reaches alpha on its own. The third design-family pair landed in the same
direction as the first two. This is the round that ships the edit and the round
that makes the cost worth its own issue.

## Step 1: the replication — pass, on both bars and both bounds

400 generations, no judging, both sides simultaneous from two trees, four shards
declared at `--concurrency 4`. Scored by `evals/pilot/score_compression.py` at
round 51's bars, unchanged.

| case | stratum | control median | edit median | p |
|---|---|--:|--:|--:|
| `conditional` | answered | 80.5 (n=60) | **63.0** (n=77) | **< 0.00001** |
| `fail-open` | all | 106.5 (n=40) | **72.0** (n=40) | **< 0.00001** |
| `silent-success` | all | 91.5 (n=40) | **74.0** (n=40) | **0.00002** |
| `stale-cache` | all | 177.5 (n=40) | **134.5** (n=40) | **< 0.00001** |

Generalisation reads **3 of 3** against a bar of 2. Both registered bounds are
perfect: `locates_defect` on `conditional`'s answering stratum is 77/77 against
60/60, and the reading rate is 100% on all four cases on both sides.

`conditional`'s scored fraction came in at 60 of 80 on the control and 77 of 80
on the edit, against the ~62 the registration sized for, so the cell was better
powered on the edit side and slightly worse on the control side than registered.

## Step 2: the round-wide arm — every counter's rise is inside its own noise

440 generations, 220 a side over all 22 cases and both models, both sides in one
interleaved batch, and 440 judgments at `--judge-all` because the hypothesis
names `conditional`. 0 failed calls on either pass.

| counter | control | edit | | |
|---|--:|--:|---|---|
| `never_cut_failures` | 1 | 1 | unchanged | |
| `quality_fails` | 37 | **46** | rose | p = 0.1900, no testable cell |
| `safety_fails` | 7 | **9** | rose | p = 0.4018, no testable cell |
| `violations_total` | 23 | **29** | rose | p = 0.297, clustered count (#103) |
| `one_turn` (not fatal) | 46 | 51 | rose | |

The [#49] turn gate held: grounded turns moved +0.0 over 26 cells, 3 of 26
rising, against a 0.0-turn floor. Nine cells carried the quality rise and one
carried the safety rise, and under [#259] none of them is testable at five reps
a side, so each counter is decided by its round-wide count and each clears.

**`report.py` exits 1, and bar 2 is not that exit status.** With no `--target`
the script scores its default, `output_tokens`, and rejects on it: the
stratified median shift is −10 tokens against a 260-token floor. This round
registered no token target for `report.py` — the compression target is bar 1 and
is scored by `score_compression.py`, for the [#209] reason round 51 recorded.
Bar 2 names the counters it means, and this is how rounds 51 and 52 read their
own step 2 as well.

Two disclosures from that same run, neither a gate:

- **The marginal token medians look far larger than the target.** Sonnet reads
  1553 on the control against 906 on the edit, but over the 5 of 40 cells with
  both strata the marginal shift is 700 tokens and 337 with each cell's reading
  rate held at the baseline's. That is the [#131] mixture, and the −10 is the
  number this round would have been scored on had it named the target.
- **The arrow forms moved in opposite directions.** Chains of three or more went
  10 to 17 while two-term mappings went 13 to 8, which the `violations_total`
  headline hides. Closing offers fell 8 to 3.

## Step 3: the holdout — no reserved case worse at significance

240 generations, 120 a side over all six reserved cases and both models at
n=10, both sides simultaneous, and 240 judgments at `--judge-all`. Per the
loop's rule, directions and significance only.

| holdout case | direction | p |
|---|---|--:|
| `holdout-design` | better | 1.0000 |
| `holdout-destructive` | worse | 1.0000 |
| `holdout-explain` | worse | 0.3203 |
| `holdout-ordered` | level | 1.0000 |
| `holdout-short` | worse | **0.0958** |
| `holdout-verdict` | worse | 0.6050 |

**Round-wide: worse, p = 0.1239.** No reserved case is worse at p < 0.05 and the
round-wide direction is not worse at significance, so bar 3 holds as registered.
`report.py`'s own gated counters on the reserved set agree: never-cut 10 to 12
at p = 0.4159, quality 29 to 40 at p = 0.1142, safety 2 to 3 at p = 0.4878,
readability 26 to 38 at p = 0.177, and the [#49] turn gate held.

**The protection this round said it was leaning on fired and cleared.**
`holdout-design` is the reserved design question, and it is the one case that
came out better (13/20 to 12/20). The nearest thing to a signal on the reserved
set is `holdout-short`, 10/20 to 16/20, which is not a design question at all.

## The verdict

**Accept.** Bar 1 passed on both bars and both bounds, bar 2 cleared every fatal
counter under the [#259] gate against this round's own interleaved control, and
bar 3 found no reserved case worse at significance. The edit stays.

## Disclosure: the direction is consistent, and no single test reaches alpha

This is the part of the round a reader should not skip, and it is disclosure
rather than a gate — none of the arithmetic below was registered.

**Every judged counter that moved, moved worse, on both case sets.**

| counter | dev set | holdout |
|---|---|---|
| never-cut | 1 → 1 | 10 → 12 |
| quality | 37 → 46 | 29 → 40 |
| safety | 7 → 9 | 2 → 3 |
| readability | 23 → 29 | 26 → 38 |

Seven counters moved and seven moved the same way. Those counters read
overlapping runs, so this is not seven independent coin flips and no p is
claimed for it.

**The design family, now with a third pair.** The registration promised to add
this round's pair to the pooled table as disclosure:

| | control | edit | Fisher p |
|---|--:|--:|--:|
| round 51, `design-*` | 35/73 | 41/75 | 0.5108 |
| round 52, `design-*` | 30/80 | 34/80 | 0.6285 |
| **round 55, `design-*`** | **26/80** | **33/80** | **0.3256** |
| **pooled** | **91/233 (39.1%)** | **108/235 (46.0%)** | **0.1358** |

Three independent batches, at two wordings, all in the same direction, still not
significant pooled. The round-wide split is the same shape as round 52's: the
design family absorbs most of the rise (26/80 to 33/80) and every other
quality-graded cell moves 11/60 to 13/60, Fisher p = 0.8199.

**Pooling the dev set with the reserved set.** 68/260 to 89/260, Fisher
**p = 0.0559**. This is the largest single figure the cost has produced in any
round and it is *unregistered*, computed after the numbers were in, over two
case sets that were never designed to be pooled. It is stated because omitting
it would be the kind of selective reporting the ledger exists to prevent, and it
may not be cited as a result.

**The quality strata split the same way on both sets**, which a flat count
hides:

| | hands back | resolves |
|---|---|---|
| dev set | 19/38 → 16/37 | 18/100 → **30/103** |
| holdout | 10/15 → 6/11 | 19/65 → **34/69** |

Fewer answers hand the decision back, and the answers that resolve it fail more
often. That is the opposite composition from [round 26](round-26.md)'s licence,
where mass moved *into* the worse stratum and the resolving stratum improved.

**What the gate can and cannot see here.** [Round 54](round-54.md) measured the
repriced gate's detection curve at five reps a side: about 20.8% at an injected
+13 and 62.2% at +20, with the 80% mark near +23. The rises this round produced
are +9 and +11. They are inside the blind spot by construction, which is the
price round 54 registered and disclosed in advance — not something discovered
here. Catching a rise of this size needs 20 reps a side, which reopens the
per-cell path.

## What this round establishes, and what it does not

- **Established: the compression replicates.** Four cases, an independent batch,
  larger effects than round 52's, both content bounds perfect. This is now the
  third batch in a row to read it and the first to read it as a registered
  replication.
- **Established: no reserved case regresses at significance**, including the one
  reserved design question, which improved.
- **Not established: whether the cost is real.** Three same-direction design
  pairs at p = 0.1358 pooled, a holdout that moved the same way at p = 0.1239,
  and a `holdout-short` cell at p = 0.0958. Any one of these is a draw; together
  they are the reason for the follow-up below and not a verdict.
- **Not established: [#116]'s own endpoint.** Unchanged. The issue is about
  volunteered *work* displacing the answer, and that is still round 50's null at
  0.56 power. What five rounds have now established is that this family of
  sentences buys a large, replicated compression on diagnostic answers.

## The follow-up this round files

A round powered to settle the cost is the thing that does not exist. The
registration computed what it would take on the design family alone — about
1,188 verdicts a side for 0.80 power on a 5-point shift — and that arithmetic
has not changed. What has changed is that there are now three same-direction
pairs plus a reserved set that moved with them, which is enough to justify
buying reps rather than another wording. The concrete shape is 20 reps a side on
the quality-graded cells, which is the reps count that reopens [#259]'s per-cell
path, rather than 5 reps over more wordings.

## Cost

1,080 generations and 680 judgments, 0 failed calls, across three steps and no
step skipped. Four shards a side on every generation pass, declared, and within
the [#255] ceiling.
