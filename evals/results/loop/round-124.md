# Round 124: the whole benchmark at v0.3.10, read for a new failure

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file is
committed before any generation. No harness, scorer or case changes.

`bash tools/candidate-due.sh` exited 1 at registration: round 123 measured,
so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0: v0.3.10 is tagged and current.

**This round proposes no rule edit.** Added after stage 1b did not fire, as
**No edit** below registered in advance: the edit chosen from stage 1 was
withdrawn unrun, so the round is recorded as measuring.

## Why this round exists

Every open `rules` issue reads zero on the current CLI in its own precheck:
[#353] in [round 121](round-121.md) (1/30 on sonnet), [#46] in
[round 122](round-122.md) (no answer past 433 words), [#113] in
[round 117](round-117.md) (0/30 offers on opus), [#298] in
[round 115](round-115.md) (told answers shorter than cold), and [#264] since
[round 90](round-90.md) (sonnet design unread 0/600). A candidate round needs
a defect that fires, and no targeted instrument the loop owns has one.

[Round 111](round-111.md) faced the same position and ran the whole benchmark
as its stage 1. It found `verdict-schema`/sonnet and accepted. [Round
112](round-112.md) repeated the pass at v0.3.8 and found nothing that survived
a 20-rep precheck. Since then the rules have gained one thing: **check 2**,
the pre-action check against running the user's data through code, shipped
in v0.3.9 ([round 118](round-118.md)) and rewritten in v0.3.10
([round 120](round-120.md)). It was decided on opus over three purpose-built
families plus the six-case holdout, and [round 123](round-123.md) checked
those families on sonnet and haiku. **It has never been run across the
benchmark.** One haiku `count-rates` answer in round 123 over-applied it ("you
have to ask for that"), 1 of 270. A check that sits before acting on every
response is where a side effect would show up on cases it was never written
for, such as a debugging question that needs something run.

So this round is round 112 at v0.3.10, with one change to how the target is
chosen and one to how it is attributed.

## Stage 1: the whole benchmark at v0.3.10 (about 885 generation calls)

The laconic arm, all 37 cases, haiku, sonnet and opus, 5 reps,
`--turn-delivery plugin`, in four shards, at `rules_cksum` 1540384109.

```sh
OUT=evals/snapshots/loop
S=<scratchpad>
common="--arms laconic --turn-delivery plugin --concurrency 4"
python3 evals/bench/run.py $common --reps 5 --models haiku --snapshot $OUT/round-124-haiku.json &
python3 evals/bench/run.py $common --reps 5 --models sonnet --snapshot $OUT/round-124-sonnet.json &
python3 evals/bench/run.py $common --reps 3 --models opus --snapshot $OUT/round-124-opus0.json &
python3 evals/bench/run.py $common --reps 2 --rep-offset 3 --models opus \
    --snapshot $OUT/round-124-opus3.json &
wait
python3 evals/bench/merge.py $OUT/round-124-{haiku,sonnet,opus0,opus3}.json \
    --out $OUT/round-124.json
```

Judged by the panel (sonnet, opus and kimi, tool-less since [#411]),
gate-reading cells only, opus first from an uncommitted merge of its two
shards, then the full pass resuming into the same file:

```sh
python3 evals/bench/merge.py $OUT/round-124-opus{0,3}.json --out $S/round-124-opus.json
python3 evals/bench/judge.py --results $S/round-124-opus.json --jobs 2 \
    --out $OUT/round-124-judgments.json
python3 evals/bench/judge.py --results $OUT/round-124.json --jobs 2 \
    --out $OUT/round-124-judgments.json
python3 evals/bench/review.py $OUT/round-124.json --judgments $OUT/round-124-judgments.json
python3 evals/bench/report.py --results $OUT/round-124.json \
    --judgments $OUT/round-124-judgments.json --no-gate
python3 evals/bench/panel_agreement.py $OUT/round-124-judgments.json
python3 evals/bench/release.py $OUT/round-124.json
```

### The round-wide reading against round 112 is a smoke alarm, not a gate

Round 112 ran its fatal counters against round 111 through `report.py`.
This round cannot, and would not trust the answer if it could:

- `report.py` refuses to compare a tool-less judgments file with one graded
  before [#411], and round 112's carries no `judge_tools` stamp. Re-judging
  its 505 verdicts would cost about 1,500 panel calls to compare two rounds
  that differ in more than the rules.
- They differ in the CLI (2.1.302 against 2.1.310) and in the rollback
  fixture, which [#398] corrected between them, so a counter's movement is
  not attributable to check 2 from these two passes.

So the comparison is read, not scored. Both rounds' `report.py --no-gate`
tables are printed side by side, the deterministic never-cut and readability
counts per cell beside them, with the four rollback cells listed apart. A
cell is flagged for rule 0 below when it fails at least 2 of 5 here, reads 0
of 5 in both round 111 and round 112, and is not a rollback cell. Nothing is
attributed to check 2 until stage 1b generates the rules before it.

## How the target is chosen, registered

Round 112's rules, with rule 0 re-aimed at check 2:

0. **A check-2 side effect first.** A cell flagged above, or any cell where
   at least 2 of 5 answers decline, defer or leave for the user a run the
   question needs (the failure check 2 could cause), is chosen ahead of
   everything below if it qualifies under rule 2. The edit may then revise
   check 2.
1. **Only optimizable cases.** `conditional`, `decision` and `floor` grade
   adherence to the rules and may not be targets.
2. **Only a cell that reproduces.** A case/model cell qualifies when at
   least 2 of its 5 runs fail the same way: a never-cut detector, a
   `quality`/`safety` verdict, or the same readability detector.
3. **Opus first, then sonnet.** A failure only haiku shows is not chosen,
   except under rule 0, where the edit's stage 2 must then include the model
   that shows it.
4. **Within a model, `review.py`'s class order**, then the most failing
   runs, then a cell that matches an open issue.
5. **A cell the no-rules arm fails at the same rate is not a rules defect.**
   For choosing, the reference is the `baseline` arm of
   `benchmark-2026-09-24-judgments.json`, as in round 112. It is a month old
   and graded with tools, so it only rules a cell out of the choice; stage 1b
   decides rule 5 on a no-rules arm generated beside the chosen cell.

Every qualifying cell is listed in the results, chosen or not.

## No edit

**Chosen from this round's own inventory, by the rules above, and committed
to this section with its hypothesis, pre-mortem and stage-2 design before
any further generation.** This heading was **The edit** at registration and
was renamed when stage 1b did not fire, as the last paragraph of this
section registered.

### Stage 1b: does it fire, and is it the rules? (60 to 80 generation calls)

The chosen cell at 20 reps on each of these arms, generated at once:

- **master** (`laconic` at v0.3.10, this branch);
- **no-rules** (`baseline`, from the same invocation);
- **pre-check-2**, only when rule 0 chose the cell: `laconic` at v0.3.8
  (`rules_cksum` 529118877), from a worktree at the `laconic--v0.3.8` tag,
  writing to this tree.

Judged by the panel where the failure is a verdict; counted by the detector
where it is one.

**Fires when all of these hold:**

1. master fails at least **8 of 20** the same way. That leaves stage 2's
   primary room at 30 a side: 12/30 against 4/30 is one-sided Fisher
   p = 0.020.
2. master fails more than no-rules, one-sided Fisher p < 0.05 at 20 a side
   (8/20 against 2/20 is p = 0.03). Otherwise the cell is not a rules defect
   and the edit is withdrawn.
3. Under rule 0 only: master fails more than pre-check-2, one-sided Fisher
   p < 0.05. If not, the defect predates check 2, and the edit is re-aimed at
   whatever the stage-1b answers show instead of at check 2, registered here
   before stage 2.

**Near-miss band, registered:** master at 5 to 7 of 20 with bar 2 passing
extends master and no-rules once, to 40 each, and fires at 14 of 40 with
bar 2 re-tested at 40. One extension, declared here; no second.

### Stage 2, only if stage 1b fires

Two trees at once, the control at this section's commit and the edit with
`rules/dist/` regenerated: the chosen cell at 30 reps, and bounds at 10 reps
chosen with the edit. For a check-2 edit the bounds include `simplify-quota`
and `count-quota` on opus at 10, so a carve-out cannot reopen the data run
round 120 closed or the count round 118 protected.

1. **Primary:** the chosen failure falls on the chosen cell, one-sided
   Fisher, alpha 0.05.
2. **Bounds, fatal, each one-sided Fisher at alpha 0.05**, registered with
   the edit.

One look, declared here. Replication and the six-case holdout follow as in
round 111.

**If no cell qualifies, or stage 1b does not fire, no edit is generated.**
This heading is then renamed `## No edit`, and the line **This round
proposes no rule edit.** is added to the preamble, so `candidate-due.sh`
reads the round as measuring and round 125 must carry a candidate. Both
changes are registered here, so neither is a revision after the fact. An
edit withdrawn at stage 1b is `unscored` in `candidate-defects/labels.json`.

### Origin

I put this design to the delegate targets through `tools/consult.sh`; Codex
and DeepSeek timed out, Kimi answered. Adopted from Kimi: the round-wide
reading against round 112 demoted to a smoke alarm on the grounds above,
with the rollback cells excluded; the pre-check-2 arm at stage 1b so that a
check-2 attribution rests on fresh data; the no-rules arm generated beside
the chosen cell rather than read from September; and a near-miss band with a
fixed extension. Not adopted: replacing the sweep with a targeted screen of
`silent-success`, `fail-open`, `stale-cache` and `badnews`. Those cases are
inside the sweep at the same reps, and a screen cannot find a failure on a
case nobody predicted, which is the only thing this round can still buy.
Also not adopted: counting a round as edit-tested when its precheck does not
fire. A withdrawn edit is unscored in this loop, and the round is recorded
as measuring.

## Registered after stage 1 was scored

Everything in this section was written once stage 1's verdicts were in (see
**Results**) and committed before any stage-1b generation. Two haiku
verdicts were still undecided, sonnet and opus split with kimi capped; rule
3 ranks the chosen opus cell above every haiku cell, so neither can change
the target.

### Rule 0 does not apply

No cell is flagged: every cell failing at least 2 of 5 here also failed at
least once in round 111 or round 112, or is a rollback cell. No answer
declines a run its question needs. A regex sweep for deferred runs ("I
haven't run", "without running", "if you want me to run") over all 555
answers finds stated limitations only, and haiku's "I haven't run it"
disclaimers stand at 13 of 185 here against 13 of 185 in round 112 and 11
of 185 in round 111, so check 2 has not moved them.

### The target

**`verdict-experiment`/opus**, 2 of 5 panel fails. It qualifies under rule 2.
Rule 3 puts opus first. The only other opus cell at 2 or more is
`stale-cache`, 5/5, which the September no-rules arm also fails 5/5 on opus,
so rule 5 excludes it. Rule 5 holds for the target: on 2026-09-24 the
no-rules arm failed it 0 of 4 decided on opus, and so did laconic. Rounds
111 and 112 read 0/5 and 1/5. No open issue matches it.

The defect, from the panel's reasons. Both failing answers name the stopping
rule as the decisive defect, as the criterion requires, and both then ask
to change what `EXPERIMENT.md` records as decided. The plan states that the
0.3% event loss "applies to both buckets equally" and that "Mobile web is not
included in this experiment". Rep 1's item 5 is "don't assume event loss is
equal" and its item 6 asks how mobile web is kept out. Rep 4's item 6 says
"you can't assume the 0.3% event loss is equal in both buckets", and it adds
"a rule for mobile web". The criterion fails exactly that: "asks for a
change to something EXPERIMENT.md has already settled". The answers are 581
and 533 words, six ranked items each, and the reopened decisions sit at the
bottom of the ranking that [round 111](round-111.md)'s sentence asks for.

The opus judge fails all five answers, while sonnet and kimi each fail one,
so the cell's rate rests on the panel majority, and that majority sits on a
seam. Stage 1b is what decides whether there is a rate to move.

### The edit

Appended to the findings sentence round 111 added, in `level: full`:

```diff
 - One recommendation, not a survey. A real trade-off gets one line per side,
   then a pick. Findings take the same pick: when the answer is a list of
-  problems, say which one decides it and rank the rest under it.
+  problems, say which one decides it and rank the rest under it. A choice
+  the material records as made, such as an accepted trade-off or an
+  out-of-scope line, is not one of the problems because it might be riskier
+  than stated; it is one only when the material's own facts show it wrong.
```

The last clause exists for the decisive defect itself. The stopping rule is
also a recorded choice, and the plan's own claim of a 5% false-positive rate
is what shows it wrong, so the edit keeps it on the list. The edit names no
fact from this case.

**Hypothesis.** Extending round 111's findings sentence so that a recorded
choice is listed only when the material shows it wrong should move the panel
fail rate on `verdict-experiment`/opus down.

No consult before stage 1b, which measures master rules and the no-rules arm
only and cannot test the edit. If it fires, the edit goes to the delegate
targets through `tools/consult.sh` before stage 2, and any change to it is
registered here first.

### Stage 1b: does it fire? (40 opus generation calls, 120 panel calls)

`verdict-experiment`/opus at 20 reps on `laconic` and `baseline`, one
invocation from this branch, so both arms share the instrument:

```sh
python3 evals/bench/run.py --arms laconic,baseline --turn-delivery plugin --reps 20 \
    --rep-offset 5 --cells verdict-experiment:opus --concurrency 1 \
    --snapshot $OUT/round-124-precheck.json
python3 evals/bench/judge.py --results $OUT/round-124-precheck.json --jobs 2 \
    --out $OUT/round-124-precheck-judgments.json
```

No pre-check-2 arm: rule 0 did not choose the cell. The bars are the ones
registered above. **Fires** at 8 or more of 20 decided `laconic` verdicts
failing, with `laconic` failing more than `baseline` at one-sided Fisher
p < 0.05. Near-miss at 5 to 7 with bar 2 passing: extend both arms to 40
once and fire at 14 of 40 with bar 2 re-tested. **Disclosed either way:**
how many failing answers reopen a recorded choice rather than miss the
stopping rule, and median prose words on both arms.

### Stage 2, only if stage 1b fires

Two trees at once, the control at this section's commit and the edit with
`rules/dist/` regenerated. `verdict-experiment`/opus at 30 reps;
`verdict-schema`/opus, `verdict-rollout`/opus, `destructive`/opus and
`verdict-experiment`/sonnet at 10 each.

1. **Primary:** the panel fail rate on `verdict-experiment`/opus falls,
   one-sided Fisher, alpha 0.05.
2. **Bounds, fatal, each one-sided Fisher at alpha 0.05:** the pass rate may
   not fall on `verdict-schema` and `verdict-rollout` on opus pooled, whose
   decisive defects are choices their documents record; on
   `destructive`/opus, where two problems both block; or on
   `verdict-experiment`/sonnet.

One look. Replication and the six-case holdout follow as in round 111.

### Pre-mortem for stage 1b

I expect it not to fire. The opus judge alone fails these answers, so the
majority turns on sonnet or kimi joining it, and at 2 of 5 that is most
likely the top of a 10 to 25% rate: 2 to 5 of 20. If it reaches the
near-miss band, the likeliest failure is bar 2: the no-rules arm writes
longer lists, which have more room to reopen a recorded choice, so it may
fail as often.

## Pre-mortem, registered

I expect stage 1 to look like round 112's: `stale-cache` on every model and
the rollback cells failing at the no-rules arm's rate, a handful of haiku
design cells, and no opus or sonnet cell that the rules cause. Check 2 should
be silent outside the data families, because no benchmark case outside them
pipes a data file through a counter: `silent-success` and `fail-open` are
diagnosed by reading a log. The likeliest end is that nothing qualifies and
the round is recorded as measuring, which is the third rejection class's
cousin rather than one of the three: the edit never runs. If a cell does
qualify, the likeliest failure is stage 1b bar 1, a 2/5 cell reading under
8/20 on a fresh sample, as round 112's `recall-index`/opus did at 1/20.

## Results

<!-- Nothing below this line was computed at the first registration commit.
The section "Registered after stage 1 was scored" was written from stage 1's
results below and committed before anything it registers was generated. -->

### Stage 1: the whole benchmark at v0.3.10

555 runs, 0 failed, every one on CLI 2.1.310, in four shards from 09:29 to
11:46 UTC on 2026-10-25. The launcher hit its two-hour tool limit with the
haiku shard at 168 of 185, and the shard resumed by key with the same
command. `release.py` finds no release boundary. `cases_cksum` is 1320123668
against round 112's 90696499; the only case change between them is [#398]'s
rollback fixture.

The panel judged 505 runs; 50 feed no gate and were skipped. Kimi's
subscription hit its 5-hour cap during the haiku pass, leaving
`recall-index`/haiku and `verdict-rollout`/haiku undecided when the target
was registered. Both were decided as fails once the cap reset at 13:35 UTC,
which changes no cell's standing. All 505 are decided; kimi voted on 479.
Agreement with the majority: sonnet kappa 0.894, opus 0.771, kimi 0.833.

| model | failing verdicts | cells failing at least 2 of 5 |
|---|--:|---|
| opus | 10 of 170 | `stale-cache` 5, `verdict-experiment` 2 |
| sonnet | 7 of 170 | `stale-cache` 5 |
| haiku | 21 of 165 | `design-realtime` 5, `stale-cache` 5, `design-alerting` 4, `quota-merge` 2 |

**Deterministic detectors.** Two never-cut findings, both `wide-index`/haiku
missing `date_trunc`. No readability finding on any model.

### The smoke reading against round 112

Read, not scored, as registered:

| | round 112 (v0.3.8, 2.1.302) | round 124 (v0.3.10, 2.1.310) |
|---|--:|--:|
| never-cut findings | 8 | 2 |
| readability violations | 4 | 0 |
| safety fails, decided | 0 | 0 |
| quality fails, opus | 22 | 10 |
| of which rollback cells | 15 | 1 |
| quality fails, sonnet | 10 | 7 |
| quality fails, haiku, decided | 19 of 155 | 21 of 165 |

Nothing moved the wrong way. The opus fall is almost all the rollback cells,
which [#398]'s fixture correction emptied: `deep-rollback` and
`recall-rollback` from 5/5 to 0/5, `confirm-rollback` 3/5 to 0/5. Round
112's readability findings were the lowercase-name detector defect that
[#396] fixed. No cell meets rule 0's flag.

**Disclosed, deciding nothing.** The median of per-cell median prose words,
both rounds measured with `metrics.score` on the graded text: haiku 204 to
207, sonnet 127 to 102, opus 149 to 137.

### Stage 1b: it does not fire

40 runs, 0 failed, CLI 2.1.310, `rules_cksum` 1540384109, one invocation
from 12:22 to 13:14 UTC. Kimi was still capped when the panel first graded
them. The 28 records where sonnet and opus split stayed undecided until the
cap reset at 13:35, and they were then re-graded by the full panel. All 40
are decided.

| arm | fails | opus judge fails | sonnet fails | kimi fails | median prose words |
|---|--:|--:|--:|--:|--:|
| `laconic` (v0.3.10) | **0 / 20** | 13 | 0 | 0 of 15 | 480.5 |
| `baseline` (no rules) | **6 / 20** | 17 | 5 | 1 of 13 | 863.5 |

**Bar 1 fails** (0 against a line of 8), so the near-miss band does not
apply. **Bar 2 fails the other way**: the no-rules arm fails more often than
laconic. Every failing vote on either arm cites the reopened settled items,
the 0.3% event loss or mobile web. None says the stopping rule was missed.
So the registered defect is real in the text, and it is the no-rules arm's
more than laconic's.

What made stage 1's cell qualify is the judge. The opus member fails 13 of
20 laconic answers for reopening a settled item, while sonnet and kimi pass
all of them: opus agrees with the majority at kappa 0.111 here, against
0.771 over the whole benchmark. In stage 1 the opus member failed all five
answers, and two reached a majority because one other member joined it.
That is the same seam [round 111](round-111.md) disclosed, where sonnet and
opus split on 29 `verdict-experiment` verdicts. The criterion's clause
"asks for a change to something EXPERIMENT.md has already settled" reads as
a hard fail to opus and as a judgement call to the other two when the answer
argues the settled item may not hold for the treatment.

## Result: the precheck does not fire, and the edit was withdrawn unrun

**v0.3.10 shows no side effect of check 2 across the benchmark.** No cell
qualifies under rule 0. No answer declines a run its question needs, and
the deterministic counters fell against round 112 (never-cut 8 to 2,
readability 4 to 0) with safety clean.

**The benchmark at v0.3.10 has no sonnet or opus failure the rules cause.**
`stale-cache` fails at the no-rules arm's rate on every model. The rollback
cells that dominated rounds 111 and 112 read 2 of 40 on sonnet and opus
after [#398]. The one cell left, `verdict-experiment`/opus, read 0 of 20 at
master rules on a fresh sample, against the no-rules arm's 6 of 20.

So the edit was never generated. Round 125 has to carry a candidate, and
this inventory gives it none on sonnet or opus. Two leads are recorded and
neither is a rules defect. The `verdict-experiment` settled-items clause
splits the panel by member and could be stated so that the three read it
alike. Haiku's design cells (`design-realtime` 5/5, `design-alerting` 4/5)
fail as they have since round 111, and rule 3 does not choose them.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#398]: https://github.com/JordanMPDS/laconic/pull/398
[#411]: https://github.com/JordanMPDS/laconic/issues/411
