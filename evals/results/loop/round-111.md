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

## Registered after stage 1 was scored

Everything in this section was written once stage 1's verdicts were in (see
**Results**) and committed before any stage-1b or stage-2 generation.

### The target, and where it departs from the rule above

Four opus cells qualify: `stale-cache` 5/5, `deep-rollback` 5/5,
`recall-rollback` 5/5 and `confirm-rollback` 3/5. Rule 3 ranks them above
every sonnet cell, and **none of them is chosen**, because none is something
the rules cause. `benchmark-2026-09-24-judgments.json`, under the same panel
and criteria, failed all four 5/5 in the no-rules `baseline` arm and in all
four control arms. The three rollback cells also sit on the fixture [#388]
reports as stating a migration Postgres would reject, so a rule aimed at
them would teach opus to accept that record.

That is a criterion the registration did not state, and it is added here
rather than presented as rule 3's output: **a cell the no-rules arm fails at
the same rate is not a rules defect.** On sonnet it removes `stale-cache`
(5/5 here, 5/5 in the September `baseline` arm). Of the two sonnet cells
left, `verdict-schema` has more failing runs (4/5, against `design-realtime`
3/5), and the rules are associated with its failure. Under its current
criterion ([#111]) the `baseline` arm read 0/5 in rounds 20 to 24 and 2/5 on
2026-09-24, while laconic read between 2/10 and 7/10, 3/5 on 2026-09-24, and
4/5 here. Opus passes it 5/5, so **sonnet is the observed model and decides
the round.** Opus is a fatal bound, because it is the model the plugin is
run on.

The defect, from the panel's reasons: four of five sonnet answers name the
`DOUBLE PRECISION` money columns, but as item 1 of a five- to eight-item
"change these first" list. None of them says which change the ledger's
`sum(amount)` balance depends on, and the criterion fails exactly that.

### The edit

```diff
 - One recommendation, not a survey. A real trade-off gets one line per side,
-  then a pick.
+  then a pick. Findings take the same pick: when the answer is a list of
+  problems, say which one decides it and rank the rest under it.
```

**Origin.** This is [round 22](round-22.md)'s edit for #60, less its third
sentence. Round 22 moved `verdict-schema`/sonnet from 6/10 to 3/10 failing
and its scoped target from 7 to 3 at p = 0.172 with every fatal counter
clear, and it was rejected on its own target's p-value alone. Its third
sentence, *"A list whose items all read as equally decisive has not answered
'is this sound?'"*, quotes the verdict cases' own question, so it is dropped.
This is a new test on fresh data, and no run of round 22's enters a number
here.

I sent the edit and the test to Codex and Kimi through `tools/consult.sh`;
Kimi did not answer. Adopted from Codex: a bound where two problems are
co-equal blockers, which is `destructive`. That case asks "anything I should
know before I do?" about a `DROP TABLE` and passes only when both foreign
keys it breaks are named. Not taken: Codex's rewording, which adds a sentence
protecting safety and irreversible-action warnings. "Never cut" already
protects them at every level, and it outranks a `full` bullet by where it
lives. Rounds 07 to 09 wrote precedence into prose and lost, and round 10
relied on placement and won. Codex's other point, that 24/30 against 17/30
is the smallest fall the primary can see (p = 0.047), is the power this round
accepts.

**Hypothesis.** Editing "One recommendation, not a survey" so a list of
findings names the one that decides it should move the panel-judged fail
rate on `verdict-schema`/sonnet down.

### Stage 1b: does it fire at master rules? (20 generation calls)

```sh
OUT=evals/snapshots/loop
python3 evals/bench/run.py --arms laconic --reps 20 --rep-offset 5 \
    --cells verdict-schema:sonnet --snapshot $OUT/round-111-precheck.json
python3 evals/bench/judge.py --results $OUT/round-111-precheck.json --jobs 2 \
    --out $OUT/round-111-precheck-judgments.json
python3 evals/pilot/score_findings.py --precheck $OUT/round-111-precheck-judgments.json
```

**Fires at 10 or more failing of the 20 decided verdicts.** Below half, the
primary at 30 a side has little room: 15/30 against 6/30 is one-sided
p = 0.015.

### Stage 2: the edit, only if stage 1b fires (140 generation calls)

Two trees generating simultaneously: the control from a worktree at this
section's commit (master rules), and the edit from this branch with the edit
committed and `rules/dist/` regenerated. Laconic: `verdict-schema`/sonnet at
30 reps, and `verdict-experiment`/sonnet, `verdict-rollout`/sonnet,
`destructive`/sonnet and `verdict-schema`/opus at 10. That is 70 runs a side,
in two shards a side.

```sh
T=verdict-schema:sonnet
B=verdict-experiment:sonnet,verdict-rollout:sonnet,destructive:sonnet,verdict-schema:opus
for side in control edit; do
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --cells "$T,$B" --concurrency 4 \
      --snapshot $OUT/round-111-$side-shard0.json ) &
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 20 \
      --rep-offset 10 --cells "$T" --concurrency 4 \
      --snapshot $OUT/round-111-$side-shard10.json ) &
done
wait
python3 evals/bench/merge.py $OUT/round-111-$side-shard{0,10}.json --out $OUT/round-111-$side.json
python3 evals/bench/judge.py --results $OUT/round-111-$side.json --jobs 2 \
    --out $OUT/round-111-$side-judgments.json
python3 evals/pilot/score_findings.py $OUT/round-111-{control,edit}-judgments.json
```

### The bars

1. **Primary: the `verdict-schema`/sonnet fail rate falls**, one-sided
   Fisher, alpha 0.05.
2. **Bounds, fatal: the pass rate may not fall** on `verdict-experiment` and
   `verdict-rollout` on sonnet, pooled; on `destructive`/sonnet; or on
   `verdict-schema`/opus. Each is one-sided Fisher, alpha 0.05.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`. **Disclosed, deciding nothing:** prose words,
`panel_agreement.py` and `release.py`.

**Replication, bought only if both bars pass:** a fresh 70 runs a side from
the same two trees, scored on the same bars at the same alphas. Then step 9's
holdout: all six reserved cases, sonnet and opus, 5 reps each, both trees; no
reserved case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and bar 2 to hold, twice, and the holdout.
Anything else rejects and reverts `rules/laconic.md` and `rules/dist/` before
the merge.

### Pre-mortem

I expect stage 1b to fire. If stage 2 rejects, the likeliest way is round
22's: the primary moves and does not separate. "Rank the rest under it" can
be met by numbering the same list in priority order, which the panel may
still read as weighing the items alike. The fatal risk is `destructive`: an
answer that names one foreign key as the deciding problem and drops the
other.

[#111]: https://github.com/JordanMPDS/laconic/pull/111
[#388]: https://github.com/JordanMPDS/laconic/issues/388

## Results

<!-- Nothing above this line has been computed, except the section
"Registered after stage 1 was scored", which was written from stage 1's
results below and committed before anything it registers was generated. -->

### Stage 1: the whole benchmark at master rules

555 runs, 0 failed, every one on CLI 2.1.302, in four shards from 01:57 to
04:15 UTC on 2026-10-17. `release.py` finds no release boundary.

The panel judged 505 of them; 50 feed no gate (`conditional`, `decision`,
`floor` and `ordered-steps`/haiku) and were skipped. 13 verdicts were
undecided on the first pass and all 13 were decided on the retry. kimi did
not vote on 209 records, so those were decided by sonnet and opus agreeing.
Agreement with the majority: sonnet kappa 0.959, opus 0.849, kimi 0.818.

One registered command did not run as written. `judge.py` refused
`--carry-judgments-from` because the snapshot carries no arms, so the opus
judgments file was copied to `round-111-judgments.json` and the full pass
resumed into it. The verdicts are the same ones. `round-111-opus.json` and
its judgments are not committed, because every run and verdict in them is in
`round-111.json` and `round-111-judgments.json`.

| model | failing verdicts | cells failing at least 2 of 5 |
|---|--:|---|
| opus | 20 of 170 | `stale-cache` 5, `deep-rollback` 5, `recall-rollback` 5, `confirm-rollback` 3 |
| sonnet | 14 of 170 | `stale-cache` 5, `verdict-schema` 4, `design-realtime` 3 |
| haiku | 22 of 165 | `design-realtime` 5, `stale-cache` 5, `verdict-schema` 3, `design-alerting` 2, `verdict-experiment` 2 |

Every other judged cell failed once or not at all. The qualifying cells
against the September arms, from `benchmark-2026-09-24-judgments.json`:

| cell | here | laconic, 09-24 | baseline, 09-24 |
|---|--:|--:|--:|
| `stale-cache`/opus | 5/5 | 4/5 | 5/5 |
| `deep-rollback`/opus | 5/5 | 5/5 | 5/5 |
| `recall-rollback`/opus | 5/5 | 5/5 | 5/5 |
| `confirm-rollback`/opus | 3/5 | 5/5 | 5/5 |
| `stale-cache`/sonnet | 5/5 | 5/5 | 5/5 |
| `verdict-schema`/sonnet | 4/5 | 3/5 | 2/5 |
| `design-realtime`/sonnet | 3/5 | 4/5 | 1/5 |

**The deterministic detectors found almost nothing.** No response on any
model carried a readability violation. Four never-cut findings: one on
`conditional`/sonnet, a rule-adherence case, and three on haiku missing
`date_trunc` (`recall-index` rep 2, `wide-index` reps 2 and 3), which is
[#353]'s omission. `wide-index`/haiku qualifies at 2/5 and is haiku-only.

**Disclosed, deciding nothing: answers are longer than at round 73.** The
median of per-cell median words is 230 on haiku against round 73's 102, and
167 on sonnet against 84; opus reads 166. Some of the rise is not the rules.
`code-fidelity`/sonnet went from a median 55.5 words on 2026-09-24 to 133 on
2026-10-01 at the same `rules_cksum` (288018845), adding requested detail
about each flag rather than unrequested content. Nothing here separates the
rules' share from the CLI's.

### Stage 1b: it fires

20 runs, 0 failed, CLI 2.1.302: **18 of 20 decided verdicts fail**, against a
line of 10. The edit was committed in 9fa8b37 with `rules/dist/` regenerated,
at `rules_cksum` 529118877.

### Stage 2, first sample

70 runs a side, 0 failed, every run on CLI 2.1.302, the control from a
worktree at 6bc3375 (`rules_cksum` 4228464778) and the edit from 9fa8b37.
`release.py` finds no boundary. A Claude usage limit stopped all four shards
a few runs in; the same commands resumed them, and every failed key was
regenerated.

```
## Primary: verdict-schema/sonnet fails less, one-sided
   verdict-schema/sonnet fails  control  27/29   edit   6/30   one-sided p = 0.0000  FIRES
## Bounds (fatal): the pass rate may not fall
   verdict-experiment+rollout   control  13/16   edit  13/14   one-sided p = 0.9336  holds
   verdict-schema/opus          control   8/9    edit  10/10   one-sided p = 1.0000  holds
   destructive/sonnet           control  10/10   edit  10/10   one-sided p = 1.0000  holds
## accept basis met
```

**Bar 1 passes and bar 2 holds.** Six verdicts a side are undecided after
two retries, all but two on `verdict-experiment`/sonnet. In each, sonnet and
opus split, and kimi had no vote: its Kimi Code subscription hit its 5-hour
usage cap during this stage, and it voted on 19 control records and no edit
record. Every decided verdict here is therefore sonnet and opus agreeing. No
outcome of the undecided ones changes a bar: if every control one passed and
every edit one failed, the sibling bound would read 17/20 against 13/20,
p = 0.137.

What changed, from the edit's answers: the float money type is still item 1,
but the answer now says so before the list, as in *"The deciding problem is
that money is stored as `DOUBLE PRECISION`."*, and the other defects follow
under a heading that ranks them below it. The median length on the target
cell fell from 409.5 to 362 words; the other cells moved by less than 30.

### Replication

A fresh 70 runs a side from the same two trees, 0 failed, CLI 2.1.302,
`release.py` clean:

```
## Primary: verdict-schema/sonnet fails less, one-sided
   verdict-schema/sonnet fails  control  23/27   edit   0/29   one-sided p = 0.0000  FIRES
## Bounds (fatal): the pass rate may not fall
   verdict-experiment+rollout   control  11/11   edit  11/11   one-sided p = 1.0000  holds
   verdict-schema/opus          control  10/10   edit  10/10   one-sided p = 1.0000  holds
   destructive/sonnet           control  10/10   edit  10/10   one-sided p = 1.0000  holds
## accept basis met
```

**Bar 1 passes again, and the target fell further: 0 of 29.** Kimi still
had no vote, and 9 `verdict-experiment`/sonnet verdicts a side are undecided.
Unlike stage 2, the worst case here would fire the sibling bound, so these
verdicts are retried once kimi's window resets and this section is updated
then. The splits run the same way on both sides and in every sample: sonnet
votes pass and opus votes fail on all 9 a side here, and on 4 control and 6
edit in stage 2. Opus's reasons fail answers that reopen points
`EXPERIMENT.md` has already settled. That is a disagreement between judges
about the criterion, present at master rules, rather than anything the edit
did, so the holdout was generated while the splits wait.

### Holdout

All six reserved cases, sonnet and opus, 5 reps from both trees: 60 runs a
side, 0 failed, CLI 2.1.302, `release.py` clean. **Every verdict passed on
both sides, 60 of 60 against 60 of 60, with none undecided.** No reserved
case is worse under the edit. Directions only, as step 9 requires.
