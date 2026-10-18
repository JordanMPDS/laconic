# Round 113: the rollback cells on the corrected record (#388, #353)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file is
committed before any generation. No harness, scorer or case changes since
[#398], which corrected the record these cases read.

`bash tools/candidate-due.sh` exited 1 at registration: [round 112](round-112.md)
measured, so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0: v0.3.8 is tagged and current. As in
[round 110](round-110.md), the edit sits behind a precheck. If no cell
qualifies, or the precheck does not fire, the edit is withdrawn unrun, the
heading is renamed `## No edit`, and the line **This round proposes no rule
edit.** is added to this preamble, so round 114 owes a candidate. Both
changes are registered here.

**This round proposes no rule edit.** Added after stage 1 found no qualifying
cell, as **No edit** below registered in advance: the edit was withdrawn
unrun, so the round is recorded as measuring and round 114 owes a candidate.

**Seen before registration, and used in no count below.** While checking
#398, five `recall-rollback`/opus answers were generated at master rules on
a draft of the corrected record, one clause short of the merged one. All
five confirm the config change as the trigger and name migration `0042` as
why the revert and the rollback failed. One of them also names the not-null
column. (Corrected after registration from "two": a second says only that
`v411` code failed once `0042` ran.) They are not committed. They are why the edit below is registered
now rather than chosen after stage 1.

## Why this round exists

[Round 112](round-112.md) found the four opus rollback cells failing, every
failure a dispute of the incident record: `deep-rollback` and
`recall-rollback` 5/5, `confirm-rollback` 3/5, `wide-rollback` 2/5. The
no-rules arm failed them at the same rate on 2026-09-24, so its rule 5
excluded them. All 13 failed deep-, recall- and confirm-rollback answers
argued from the timeline: the error rate rose as instances moved onto
`v412`, which points at `v412`, not at the config change. #398 made the
record's timeline agree with its account. codex and kimi each find nothing
impossible in it.

So the cells can now measure what they were built for: a closed question
whose premise is half right. *"The config change was the cause, correct?"*
The config change was the trigger, and the migration is why neither the
revert nor the rollback worked. An answer that confirms the premise and
stops has missed the half the record establishes. That is the shape [#353]
reports for a wrong-premise question, and the edit round 112 registered for
#353 but never ran is written for it.

Every earlier rollback measurement read the old record, so no baseline
exists. Stage 1 generates the no-rules arm beside the laconic arm.

## Stage 1: the four rollback cells, both arms (about 200 generation calls)

`confirm-`, `recall-`, `wide-` and `deep-rollback` on sonnet and opus, the
`laconic` and `baseline` arms, 5 reps, `--turn-delivery plugin`. Four
shards, each holding both arms, because `merge.py` refuses shards whose arm
definitions differ.

```sh
OUT=evals/snapshots/loop
S=<scratchpad>
for m in sonnet opus; do
  cells=confirm-rollback:$m,recall-rollback:$m,wide-rollback:$m,deep-rollback:$m
  common="--arms laconic,baseline --turn-delivery plugin --concurrency 4 --cells $cells"
  python3 evals/bench/run.py $common --reps 3 --snapshot $OUT/round-113-${m}0.json &
  python3 evals/bench/run.py $common --reps 2 --rep-offset 3 --snapshot $OUT/round-113-${m}3.json &
done
wait
python3 evals/bench/merge.py $OUT/round-113-{sonnet0,sonnet3,opus0,opus3}.json \
    --out $OUT/round-113.json
python3 evals/bench/judge.py --results $OUT/round-113.json --jobs 2 \
    --out $OUT/round-113-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-113-judgments.json
python3 evals/bench/release.py $OUT/round-113.json
```

## How the target is chosen, registered

1. **Only a cell that reproduces.** A case/model cell qualifies when at
   least 2 of its 5 laconic runs fail the panel's `quality` verdict.
2. **Only a rules defect.** It also has to fail at least 2 more laconic runs
   than `baseline` runs, both arms generated in this round.
3. **Opus first, then sonnet.**
4. **Within a model,** the most failing laconic runs, then the largest gap
   over `baseline`, then the order confirm, recall, wide, deep.

Every cell is listed in the results, chosen or not.

## No edit

The closed-question passage of `rules/laconic.md`, which every level
carries, gains round 112's wrong-premise specimen, unchanged:

```diff
 memory limit." Naming the option that holds is the whole answer, and the
 evidence for it is left out unless the user asked why. If neither holds, say
 so and name what does.
+
+A closed question with a wrong premise is where the one word stops being
+enough: *"So the fix is raising the limit to 1Gi, correct?"* — "No. Memory
+climbs without levelling off, so it is a leak, and a higher limit only delays
+the next kill. Find the leak first." The fact that breaks the premise is part
+of the answer, and so is what works instead.
```

**It fits only one failure shape**: an answer that confirms or denies the
premise without the fact that breaks it, here migration `0042` and why it
made the revert and the rollback fail. If the target's failing answers fail
some other way, such as disputing the record or blaming the lock, the edit
does not address them and is withdrawn unrun. Which shape they have is read
from the panel's reasons and recorded with the target.

**Hypothesis.** Adding the wrong-premise specimen to the closed-question
passage lowers the target cell's panel failure rate.

### Stage 1b: does it fire? (up to 100 generation calls)

The target cell, laconic arm, 20 more reps:

```sh
python3 evals/bench/run.py --arms laconic --turn-delivery plugin --reps 20 \
    --rep-offset 5 --cells <target> --concurrency 2 \
    --snapshot $OUT/round-113-precheck.json
python3 evals/bench/judge.py --results $OUT/round-113-precheck.json --jobs 2 \
    --out $OUT/round-113-precheck-judgments.json
```

**It fires when at least half of the decided verdicts fail.** Below that,
the edit is withdrawn unrun.

### Stage 2, only if stage 1b fires

Two trees at once: the control at this file's commit, and the edit with
`rules/dist/` regenerated. The target cell at 30 reps, the other three
rollback cells on the target's model at 10, and `recall-metric` on that
model at 10. The edit goes to codex through `tools/consult.sh` before
stage 2 generates, and any change to it is registered then.

1. **Primary:** the target cell's panel failure rate falls, one-sided Fisher,
   alpha 0.05.
2. **Bounds, fatal, each one-sided Fisher at alpha 0.05:** the panel pass
   rate on the other three rollback cells pooled may not fall, and neither
   may the pass rate on `recall-metric`, whose second turn is a closed
   question with a right premise. Median words on both are disclosed.

Replication and the holdout follow as in [round 111](round-111.md).

## Pre-mortem, registered

I expect no cell to qualify. The five informal answers all named the
migration, and both arms are likely to now that the record no longer invites
a dispute. If a cell does qualify, I expect `deep-rollback`/opus: five turns
of its own output is the most the model carries into the closed question.
The likeliest way the edit fails is the `recall-metric` bound: a specimen
saying the one word stops being enough can teach opus to append reasons to
right-premise answers too.

## Results

<!-- Nothing above this line has been computed, except the two changes the
preamble registered for an edit withdrawn unrun: the line added to the
preamble, and the heading renamed **No edit**. -->

### Stage 1: the four rollback cells, both arms

80 runs, 0 failed, every one on CLI 2.1.302, in four shards from 04:48 to
05:06 UTC on 2026-10-18. `release.py` finds no release boundary. The merged
file carries `rules_cksum` 529118877 and `cases_cksum` 1599015634. Its
`metadata.reps` reads 3, copied from the first shard, but it holds reps 0 to 4
on every cell.

The panel judged all 80 and none is undecided. Agreement with the majority:
sonnet 78 of 80, opus 79, kimi 79.

| cell | laconic fails | baseline fails | laconic median words | baseline median words |
|---|--:|--:|--:|--:|
| `confirm-rollback`/opus | 0/5 | 0/5 | 129 | 400 |
| `recall-rollback`/opus | 1/5 | 0/5 | 42 | 196 |
| `wide-rollback`/opus | 1/5 | 0/5 | 41 | 206 |
| `deep-rollback`/opus | 0/5 | 0/5 | 28 | 261 |
| `confirm-rollback`/sonnet | 0/5 | 0/5 | 91 | 251 |
| `recall-rollback`/sonnet | 0/5 | 0/5 | 28 | 193 |
| `wide-rollback`/sonnet | 0/5 | 0/5 | 34 | 206 |
| `deep-rollback`/sonnet | 0/5 | 0/5 | 31 | 206 |

**No cell qualifies.** Rule 1 needs 2 of 5 laconic failures, and the most
any cell has is 1.

The two failures are both opus, laconic, rep 2, and they share one shape:

> It was the trigger, not the whole cause. Migration `0042` is why the outage
> outlasted the config revert at 14:21. Reverting the config alone would have
> ended it there. (`recall-rollback`)

> It started the outage, but it isn't the whole cause. On its own, the 14:21
> configuration revert would have fixed it. Migration `0042` is why the revert
> and the release rollback both failed, and why the outage lasted 45 minutes.
> (`wide-rollback`)

The panel failed both under the trap's "claims reverting the config would
have worked". Each says it as a counterfactual without the migration, which
is the record's own sentence: "the config change alone is fixed by the 14:21
revert". Under either reading, each cell stays at 1 of 5.

**Against round 112, on the old record**, the opus laconic arm went from
`deep-rollback` 5/5, `recall-rollback` 5/5, `confirm-rollback` 3/5 and
`wide-rollback` 2/5 to 0, 1, 0 and 1. No failure in this round disputes the
record.

## Result: no cell qualifies, and the edit was withdrawn unrun

**The corrected record ends the disputes.** Opus failed 15 of its 20 laconic
rollback runs in round 112, every one arguing with the record. It fails 2 of
20 here, and the no-rules arm fails none on either model.

**On these cells the rules cost nothing the panel can see.** Laconic answers
the half-right closed question at the no-rules arm's pass rate on both
models, at 11% to 36% of its median words. Neither arm confirms the
premise and stops, so [#353]'s edit has nothing here to address.

Round 114 owes a candidate. Between round 112's whole benchmark and this
round, the existing cases show no rules defect that reproduces on sonnet or
opus, so the lead is a new case built to reproduce an open `rules` issue.

[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#398]: https://github.com/JordanMPDS/laconic/pull/398
