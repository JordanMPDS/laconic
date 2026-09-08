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
