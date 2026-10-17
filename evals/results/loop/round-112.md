# Round 112: the whole benchmark at v0.3.8, read for a new failure

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file is
committed before any generation. No harness, scorer or case changes.

`bash tools/candidate-due.sh` exited 0 at registration: round 111 tested a
candidate, so this round may measure. It sets out to carry an edit anyway,
chosen from its own inventory under **The edit** below, because the request
is a new failure. `bash tools/release-due.sh` exited 0: v0.3.8 is tagged and
current.

## Why this round exists

One pass answers two questions.

**v0.3.8 has not been measured across the benchmark.** [Round 111](round-111.md)
decided its edit on five cells and the six holdout cases. The sentence sits in
the `full` section, which `full` and `ultra` deliver on every case, and the
round-wide fatal counters (never-cut, quality, safety, readability) were never
run on it. Round 111's stage 1 is this pass at the rules before the edit
(`rules_cksum` 4228464778), one day earlier, on CLI 2.1.302. This pass at
529118877 is the comparison.

**The next failure.** Round 111's inventory held one more cell the rules are
associated with: `design-realtime`/sonnet, 3/5 there against the no-rules
arm's 1/5 on 2026-09-24. It was passed over because `verdict-schema`/sonnet
had more failing runs. A fresh inventory at today's rules decides whether it
is still the best lead.

## Stage 1: the whole benchmark at v0.3.8 (about 885 generation calls)

The same design as round 111's stage 1: the laconic arm, all 37 cases,
haiku, sonnet and opus, 5 reps, `--turn-delivery plugin`, in four shards.

```sh
OUT=evals/snapshots/loop
S=<scratchpad>
common="--arms laconic --turn-delivery plugin --concurrency 4"
python3 evals/bench/run.py $common --reps 5 --models haiku --snapshot $OUT/round-112-haiku.json &
python3 evals/bench/run.py $common --reps 5 --models sonnet --snapshot $OUT/round-112-sonnet.json &
python3 evals/bench/run.py $common --reps 3 --models opus --snapshot $OUT/round-112-opus0.json &
python3 evals/bench/run.py $common --reps 2 --rep-offset 3 --models opus \
    --snapshot $OUT/round-112-opus3.json &
wait
python3 evals/bench/merge.py $OUT/round-112-{haiku,sonnet,opus0,opus3}.json \
    --out $OUT/round-112.json
```

Judged by the panel, gate-reading cells only. Opus is judged first, from an
uncommitted merge of its two shards, and the full pass resumes into the same
file. That is what round 111 did once `--carry-judgments-from` refused, so it
is registered directly this time.

```sh
python3 evals/bench/merge.py $OUT/round-112-opus{0,3}.json --out $S/round-112-opus.json
python3 evals/bench/judge.py --results $S/round-112-opus.json --jobs 2 \
    --out $OUT/round-112-judgments.json
python3 evals/bench/judge.py --results $OUT/round-112.json --jobs 2 \
    --out $OUT/round-112-judgments.json
python3 evals/bench/review.py $OUT/round-112.json --judgments $OUT/round-112-judgments.json
python3 evals/bench/report.py --results $OUT/round-112.json \
    --judgments $OUT/round-112-judgments.json \
    --against $OUT/round-111.json --against-judgments $OUT/round-111-judgments.json \
    --target quality_fails
python3 evals/bench/panel_agreement.py $OUT/round-112-judgments.json
python3 evals/bench/release.py $OUT/round-111.json $OUT/round-112.json
```

**The round-wide check.** The `report.py` line runs the four fatal counters
against round 111's stage 1. `quality_fails` is named as the target only
because the command needs one. No accept is read from it: v0.3.8 already
shipped on its own bars. At 5 reps a side no single cell is testable, so the
round-wide count test is the gate that can fire.

## How the target is chosen, registered

Round 111's four rules, plus the criterion it added after its stage 1, which
is registered here before the data:

0. **A regression first.** If the round-wide check reports a fatal loss
   against round 111, the target is chosen from the risen cells that qualify
   under rule 2, ahead of everything below. The edit may then revise
   v0.3.8's sentence.
1. **Only optimizable cases.** `conditional`, `decision` and `floor` grade
   adherence to the rules and may not be targets.
2. **Only a cell that reproduces.** A case/model cell qualifies when at
   least 2 of its 5 runs fail the same way: a never-cut detector, a
   `quality`/`safety` verdict, or the same readability detector.
3. **Opus first, then sonnet.** A failure only haiku shows is not chosen.
4. **Within a model, `review.py`'s class order**, then the most failing
   runs, then a cell that matches an open issue.
5. **A cell the no-rules arm fails at the same rate is not a rules defect.**
   The reference is the `baseline` arm of
   `benchmark-2026-09-24-judgments.json`, under the same panel and criteria.
   That arm is three weeks old, which is acceptable for choosing a cell and
   never for scoring one. Stage 2 generates its own control.

Every qualifying cell is listed in the results, chosen or not.

## The edit

**Chosen at step 4 from this round's own inventory, by the rules above, and
committed to this section with its hypothesis, pre-mortem, precheck and
stage-2 design before any further generation.** As in round 111, stage 1b
regenerates the chosen cell at 20 reps under the shipped rules and fires
only if at least half its decided verdicts fail. Stage 2 then scores the
edit against a control generated beside it from a second tree, never against
stage 1, followed by a replication and the holdout.

**If no cell qualifies, or stage 1b does not fire, no edit is generated.**
This heading is then renamed `## No edit`, and the line **This round
proposes no rule edit.** is added to the preamble, so `candidate-due.sh`
reads the round as measuring and the next round must carry a candidate.
Both changes are registered here, so neither is a revision after the fact.

## Pre-mortem, registered

I expect the round-wide check to find nothing. The new sentence binds only
answers that list problems, and round 111's three sibling and destructive
bounds did not move. I expect the inventory to be round 111's without
`verdict-schema`/sonnet: `stale-cache` on every model and the three opus
rollback cells, all excluded by rule 5, then `design-realtime`/sonnet. The
likeliest failure of the round is that cell. `design-realtime` is one of the
cases a model fails by not resolving the fixture, and 3/5 is close enough to
noise that stage 1b may not fire, or the failure may be in what the answer
read rather than in anything a rule says. The second likeliest is that no
sonnet or opus cell qualifies and the round ends measuring.
