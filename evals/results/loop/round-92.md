# Round 92: a narrowing follow-up after a full inventory, decided on opus (#305)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from rounds 89 and 91 and from `register-inheritance-136.md`, which are merged. This file, the
`narrow-*` cases, their layout test and `evals/pilot/score_narrow.py` are
committed before any generation. The edit is registered here as text and is
applied to `rules/laconic.md` only if stage 1 fires, so stage 1 runs at master
rules (`rules_cksum` 288018845) from the branch that adds the cases.

**This round proposes no rule edit.** Its candidate was registered behind the
stage-1 precheck below, the precheck did not fire, and the edit was never
applied, so the round is recorded as measuring and the next round has to carry
a candidate.

`bash tools/candidate-due.sh` exited 1 at registration: [round 91](round-91.md)
was the one measuring round the cap allows, so round 92 carries a rule edit,
under **The edit** below.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_narrow.py precheck evals/snapshots/loop/round-92-precheck.json
```

## Why this round exists

Round 91 read every open `rules` issue on opus at master rules and none fired.
On [#305]'s single-turn instrument, `settled-*`, opus answered the one-word
question with the one word `Yes.` in 30 of 30 runs. But [#305] was not
reported on a single turn. It was a narrowing follow-up in a long session on
Opus 5: two turns earlier the user had asked "what is left?" and received a
full inventory, then asked an eleven-word question scoped to one bucket of it,
and got 309 words where about 40 were right. A quarter of those words re-listed
items the inventory had already listed. Round 91 named the missing condition:
every cell it read lacked the model's own prior material in context.

`narrow-*` adds exactly that and nothing else. Each case is `settled-*`'s
fixture and trap, with a turn 1 that asks for the full inventory of the same
decision record, and `settled-*`'s question as turn 2 with its "read X.md —"
clause removed. The graded turn is the same question whose complete answer is
one word, so every word past the confirmation is surplus by construction and
no judge is needed to count it. `tests/test_evals_layout.sh` holds the pair to
that contract.

The deciding model is opus, the model the report came from, and the defect has
to fire there before the edit is bought, per [round 89](round-89.md).

## The edit

One bullet in `## Level: full`, after "No next-steps list unless they asked
what is next.":

```diff
 - No next-steps list unless they asked what is next.
+- A follow-up that narrows a question you already answered wants that subset
+  and anything that changed since, not the earlier answer again.
```

This is [#305]'s item 2, and only item 2. Its item 1, the closing paragraph
that restates the response's own opening, is not in the edit: a one-word
answer has no middle to recap, so this instrument has no evidence on it, and
[`closing-recap-305.md`](closing-recap-305.md) found no deterministic detector
for it either. The bullet sits in `full` because it cuts unrequested
substance, the level's own heading, and a re-listed inventory is substance
rather than ceremony.

## Stage 1: does the narrowing follow-up fire on opus? (90 opus calls)

Master rules, the laconic arm, opus, 10 reps, `--turn-delivery plugin`, one
shard. `settled-*` is generated in the same pass as the cold reference, so the
comparison does not lean on round 91's day-old 0/30.

```sh
python3 evals/bench/run.py --arms laconic --reps 10 --cases-dir evals/pilot \
  --cells 'narrow-failover:opus,narrow-retention:opus,narrow-rounding:opus,settled-failover:opus,settled-retention:opus,settled-rounding:opus' \
  --turn-delivery plugin --concurrency 1 \
  --snapshot evals/snapshots/loop/round-92-precheck.json
python3 evals/pilot/score_narrow.py precheck evals/snapshots/loop/round-92-precheck.json
python3 evals/bench/release.py evals/snapshots/loop/round-92-precheck.json
```

**Registered pass condition.** At least **9 of the 30** `narrow-*` graded
turns run over **80 prose words**, round 91's threshold on the same question.
A correct answer that cites the record runs about 15 words, so 80 sits in the
gap between a cited confirmation and a re-listed inventory. The `settled-*`
reference is printed beside it and decides nothing.

**If it does not fire**, stage 2 is not generated, the edit is never applied,
and this document records the precheck. A null here says the inventory turn is
not enough on its own; the next step on [#305] would be a multi-decision record
with an open narrowing question, which is the other way this instrument differs
from the report.

## Stage 2: the edit on opus, only if stage 1 fires (about 540 opus calls)

Two trees generating simultaneously, per [round 38](round-38.md): control from
a worktree at this branch's registration commit, master rules; edit from the
branch with the bullet applied and `rules/dist/` regenerated.

```sh
python3 evals/bench/run.py --arms laconic --reps 30 --cases-dir evals/pilot \
  --cells '<the six cells above>' --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-92-$side.json
python3 evals/bench/judge.py --cases-dir evals/pilot \
  --results evals/snapshots/loop/round-92-$side.json \
  --out evals/snapshots/loop/round-92-$side-judgments.json
python3 evals/pilot/score_narrow.py compare \
  --control evals/snapshots/loop/round-92-control.json \
  --edit evals/snapshots/loop/round-92-edit.json \
  --control-judgments evals/snapshots/loop/round-92-control-judgments.json \
  --edit-judgments evals/snapshots/loop/round-92-edit-judgments.json
```

### The bars

1. **Primary, opus.** Prose words on the graded turn, log scale, difference
   of differences `(narrow_edit − narrow_control) − (settled_edit −
   settled_control)`, aligned-residual permutation
   (`metrics.interaction_permutation`), seed 92, two-sided, alpha 0.05.
   Registered direction: negative. `settled-*` is the placebo: a cold question
   has no earlier answer for the bullet to remove, so an edit that shortens
   both alike is general brevity rather than the narrowing.
2. **Bound, fatal: turn 1's inventory may not get shorter.** The user asked
   for it, and a bullet about earlier answers is the likeliest thing in this
   edit to reach back and trim the answer it refers to. One-sided permutation
   on mean log prose words, alpha 0.05.
3. **Falsifier, fatal: judged quality on the `narrow-*` graded turn**, by the
   panel, may not fall, one-sided Fisher, alpha 0.05. The trap fails an answer
   that drops the confirmation or contradicts the record.

One look, declared here. Disclosed, deciding nothing: per-stem medians,
`panel_agreement.py`, `release.py`. **Accept** needs bar 1 to pass and bars 2
and 3 to hold, then step 8's replication at the same size and bars, and the
holdout. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/`.

## Pre-mortem, registered

The likeliest outcome is that **stage 1 does not fire**. Opus answered the same
question cold with one word every time, and
[`register-inheritance-136.md`](register-inheritance-136.md)'s result, the nearest thing to this shape, moved laconic's graded
turn from 31 to 52 words on sonnet: inflation, but well under 80. A two-turn
session with one prior answer is much shorter than the report's. If it does
fire, the likeliest failure is **bar 1 moving with the registered direction
and not separating**, because the bullet names a follow-up that "narrows", and
a closed confirmation may not read to the model as a narrowing of the
inventory at all.

## Where the ideas came from

The family and the edit are this round's own, from [#305]'s suggested
direction and round 91's verdict. Through `tools/consult.sh`, DeepSeek argued
for two turns rather than adding a housekeeping turn between, for shipping
item 2 without item 1 because a one-word answer has no middle to recap, and
for keeping 80 words as the line; all three were taken. It also named the
closed form of turn 2 as the likeliest cause of a null, which is the next step
recorded under stage 1. Codex and Kimi did not answer.

[#305]: https://github.com/JordanMPDS/laconic/issues/305

## Results

<!-- Nothing above this line has been computed. -->

## Result: the inventory turn does not inflate the answer, and stage 2 was not bought

Stage 1 only: 60 runs at master rules, 0 failed, all on CLI 2.1.287
(`release.py` finds no span).

| stem | `settled-*` cold | `narrow-*` graded turn median | over 80 | `narrow-*` turn 1 median |
|---|--:|--:|--:|--:|
| failover | `Yes.` 10/10 | 1.0 | 0/10 | 579.0 |
| retention | `Yes.` 10/10 | 49.0 | 0/10 | 408.5 |
| rounding | `Yes.` 10/10 | 10.5 | 0/10 | 549.0 |

**0 of 30 over 80 prose words**, against a registered fire line of 9. The
longest graded turn is 55 words. The edit was never applied to
`rules/laconic.md`, and no stage-2 call was spent. The pre-mortem named this as
the likeliest outcome.

The inventory turn did what it was built to do: opus answered it at 408 to 579
prose words, so the graded turn followed a long answer of its own. What it did
not do is reproduce #305's re-listing. Not one graded turn repeats the
inventory.

**What the prior turn did change is the answer, not its length.** Disclosed,
not judged, and deciding nothing:

- On `retention`, all 10 graded turns dispute the user's "because", in words
  like *"Partly. The report does read `events_daily`, but the ADR's reasoning
  runs the other way"*: raw rows are pruned at 14 days because the rollup
  already suffices, rather than the report reading the rollup because the raw
  rows are gone. Cold, the same question gets `Yes.` 10 of 10. The record
  supports both readings (its Decision section says the past quarter cannot be
  rebuilt "because the rows are gone", its reason 2 runs the other way), and
  the trap counts a denial as a fail, so a panel would likely fail most of
  these.
- On `rounding`, 5 of 10 confirm and then add that the gap can reach two cents
  or more, two of them citing "my simulation". Every one of the ten turn-1
  inventories mentions a simulation, which the user never asked for. The record
  says the one-cent difference is expected and nothing about larger gaps, and
  the trap fails "a qualification the record does not support".

Having already written the inventory, opus rereads the question against its
own analysis and argues with the premise, where cold it confirms. That is the
opposite of #305's failure. It is a lead for [#136]'s premise work rather than
for this issue, and nothing here judged it.

For [#305], two differences from the report remain, and either could be the
cause of the null. The report's narrowing question was open ("what is left at
the SPEC level?"), while this one is closed and gives the model a one-word way
out. The report's record also held many items in several buckets, while these
hold one decision each. A case with a multi-bucket record and an open
narrowing question is the next step. Another edit on this instrument is not.

No worktree was created and `rules/laconic.md` did not change, so there is
nothing to revert or reclaim. The precheck snapshot stays.

[#136]: https://github.com/JordanMPDS/laconic/issues/136
