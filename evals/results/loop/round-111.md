# Round 111: the whole benchmark on CLI 2.1.302, read for a new failure

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file is
committed before any generation. No harness, scorer or case changes.

`bash tools/candidate-due.sh` exited 1 at registration: rounds 109 and 110
both measured, so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0.

## Why this round exists

[Round 109](round-109.md) and [round 110](round-110.md) read every open
`rules` issue at zero on CLI 2.1.301: #353, #116, #113 and #46 do not fire,
#298 waits for a case, and #264 waits for an expensive precheck. A candidate
round needs a defect that fires, and no instrument the loop owns has one.

The whole benchmark has not been run since [round 73](round-73.md)'s wide
screen, 37 cases at 5 reps on haiku and sonnet, at `rules_cksum` 864847550.
It has never been run on opus. Since then the rules have taken every accepted
edit from round 74 to round 108, and opus became the model every round is
decided on. So this round is the skill's steps 1 to 4 at today's master: the
laconic arm over every case on all three models, then `review.py`'s failure
inventory, then one edit aimed at what it finds.

## Stage 1: the whole benchmark at master rules (about 885 generation calls)

The laconic arm, all 37 cases, haiku, sonnet and opus, 5 reps,
`--turn-delivery plugin`, in four shards: haiku, sonnet, and opus split by
rep. The 27 one-turn cases are 1 call a run, `recall-*` and `wide-*` 2, and
`deep-*` and `drift-service` 5, so a model is 295 calls.

```sh
OUT=evals/snapshots/loop
common="--arms laconic --reps 5 --turn-delivery plugin --concurrency 4"
python3 evals/bench/run.py $common --models haiku --snapshot $OUT/round-111-haiku.json &
python3 evals/bench/run.py $common --models sonnet --snapshot $OUT/round-111-sonnet.json &
python3 evals/bench/run.py --arms laconic --reps 3 --turn-delivery plugin --concurrency 4 \
    --models opus --snapshot $OUT/round-111-opus0.json &
python3 evals/bench/run.py --arms laconic --reps 2 --rep-offset 3 --turn-delivery plugin \
    --concurrency 4 --models opus --snapshot $OUT/round-111-opus3.json &
wait
python3 evals/bench/merge.py $OUT/round-111-opus{0,3}.json --out $OUT/round-111-opus.json
python3 evals/bench/merge.py $OUT/round-111-{haiku,sonnet,opus0,opus3}.json \
    --out $OUT/round-111.json
```

Judged by the panel, gate-reading cells only, opus first so the inventory the
edit is chosen from is complete on the deciding model before the other two
are bought:

```sh
python3 evals/bench/judge.py --results $OUT/round-111-opus.json --jobs 2 \
    --out $OUT/round-111-opus-judgments.json
python3 evals/bench/judge.py --results $OUT/round-111.json --jobs 2 \
    --carry-judgments-from $OUT/round-111-opus-judgments.json \
    --out $OUT/round-111-judgments.json
python3 evals/bench/review.py $OUT/round-111.json --judgments $OUT/round-111-judgments.json
python3 evals/bench/report.py --results $OUT/round-111.json \
    --judgments $OUT/round-111-judgments.json --no-gate
python3 evals/bench/panel_agreement.py $OUT/round-111-judgments.json
python3 evals/bench/release.py $OUT/round-111.json
```

## How the target is chosen, registered

The inventory is long and most of it is noise at n=5, so the choice is
fixed here rather than made once the excerpts are in:

1. **Only optimizable cases.** `conditional`, `decision` and `floor` grade
   adherence to the rules and may not be targets.
2. **Only a cell that reproduces.** A case/model cell qualifies when at
   least 2 of its 5 runs fail the same way: a never-cut detector, a
   `quality`/`safety` verdict, or the same readability detector. One failure
   in five points at nothing.
3. **Opus first, then sonnet.** A qualifying opus cell outranks any sonnet
   cell. A failure only haiku shows is not chosen: [round 16](round-16.md)
   measured haiku's design failures not moving under an edit that moved
   sonnet, which is a capability boundary rather than a rules defect.
4. **Within a model, `review.py`'s class order**, then the most failing
   runs, then a cell that matches an open issue.

Every qualifying cell is listed in the results, chosen or not.

## The edit

**Chosen at step 4 from this round's own inventory, by the rule above, and
committed to this section with its hypothesis, pre-mortem and stage-2 design
before any stage-2 generation.** Stage 2 regenerates the chosen cell at
master rules beside the edit, from two trees at once, so the edit is scored
against a control generated with it and never against stage 1. A target
whose stage-2 control does not reproduce the failure withdraws the edit
unrun.

If no cell qualifies, no edit is written, the round is recorded as measuring,
and this document says that the cap could not be met rather than inventing a
target to meet it.

## Pre-mortem, registered

I expect opus to be clean on most cells and the qualifying cells to be few:
two or three design or multi-turn cells on opus or sonnet, failing on
quality rather than on a never-cut or readability detector. The likeliest
failure of the round is that the best cell's failures are spread across
different defects, so the edit aimed at one of them has nothing to move at
stage 2. The second likeliest is that the only qualifying cells are on haiku
and the round ends measuring.

## Results

<!-- Nothing above this line has been computed. -->
