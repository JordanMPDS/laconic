# Round 129: an explanation of what you read gets a count per part (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds. This file is committed first, with
`plugin/rules/laconic.md` at master, so the control worktree is that commit;
the edit and the regenerated `plugin/rules/dist/*.md` are committed after it.
Both commits precede any generation.

`bash tools/candidate-due.sh` exited 0 at registration: round 128 tested a
rule candidate, so this round could have measured. It carries a candidate
anyway, under **The edit** below, because [#500] is the one open rules issue
whose defect fires at master rules. `bash tools/release-due.sh` exited 0:
v0.6.0 is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document. The answer ran 620
words and relayed the document. The 122-word answer the user wanted held
what each stage is, what it must show to pass, and the one caveat that
changes how to read the second stage.

Two rounds have tried to shorten it by naming what an explanation contains:

- [Round 126](round-126.md), accepted and on master: a requested explanation
  "gets the scope the question needs, not the scope of the source you read
  to answer it". Factor 0.909, then 0.945.
- [Round 128](round-128.md), rejected: a `level: full` bullet naming the
  parts ("what each part is, what decides it, and any caveat"). Factor
  0.977, p = 0.148. Opus filed every criterion, guardrail and stop rule under
  "what decides it", so the bullet cut planted identifiers (16.0 to 8.5 on
  `relay-rollout`) and not length.

Round 128's result line names the successor: bound the answer itself, by a
length or a count of claims per part. This round tests the count. Its size is
the issue's own: #500's suggested Right answer is "two or three sentences per
stage, plus the one caveat that changes how to read it".

## Fire rate: no precheck

Round 128's control was generated today, at master's rules (`rules_cksum`
2442620433) on CLI 2.1.319, the release this round registers on. It read
558, 458 and 396 median prose words on the three `relay-*`/opus cells, and
1 of its 60 answers ran 326 words or fewer, twice the 163-word reference.
A precheck would buy 30 calls to re-read that rate, so none is run. If the
CLI moves before stage 2, the round's own control measures the defect on
the new release, and the pre-mortem names a control that no longer runs
long.

## The instrument

Round 126's, unchanged, as round 128 used it: the three pilot cases
`evals/pilot/relay-{rollout,migration,retention}`, the bounds cells, and
`evals/pilot/score_relay.py` with its seed (126) and its bars. This round
edits none of them, and no case or criterion has changed since round 128
ran. Prompts take the form:

> read ROLLOUT.md — explain the shadow stage and the live A/B stage. Don't
> edit anything.

## The edit

One bullet in `level: full`, after the design-question bullet and its
example pair, where round 128's bullet sat:

```diff
   - Right: "Derive alerts from the log row the loop already writes, in
     whatever monitoring you already run — which stack is that? The schema
     and the dedup rules are the next level down."
+- Explaining what you read gets at most three sentences or list items for
+  each part the question names, plus at most one caveat that changes how to
+  read it.

 Typical shape: one to three sentences, or a short list. One sentence is a
 complete answer.
```

The unit is the question's parts, not the source's: each relay question
names two, so the bullet allows six sentences and a caveat, about the size
of #500's 122-word answer and the cases' 163-word reference. It is a
ceiling and not a target, so the `explain-*` answers, which already run 76
to 140 words, have nothing to grow towards. Sentences and list items are
counted together because a count of sentences alone leaves a bulleted list
uncounted, and round 128's edit answers carried a median of 9.5 to 17 list
items on the relay cells. The caveat is capped at one because round 128's
"any caveat" was one of the unbounded nouns opus filled. The bullet sits at
`full` because #500 was observed there, and it reaches `ultra` by
inheritance. A user who fixes the scope is still governed by the never-cut
explain bullet, which outranks every level, and no precedence sentence is
written into the bullet ([round 10](round-10.md)).

## Hypothesis

> Adding "Explaining what you read gets at most three sentences or list
> items for each part the question names, plus at most one caveat that
> changes how to read it." to `level: full` should move median prose words
> on `relay-rollout`, `relay-migration` and `relay-retention` on opus
> **down**, without lowering the panel pass rate on those cells, on the
> same three on sonnet, on `explain-index`, `explain-metric` and
> `explain-rollback` on opus, or on `walkthrough`/opus.

## Stage 2: the edit on opus (260 calls, 200 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r129-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r129-edit` at the edit commit. Both
are on disk rather than under `/tmp`, which is memory on this machine. Two
shards a side, four `run.py` processes:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='relay-*:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus,walkthrough:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r129-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-129-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r129-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-129-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-129-$side-{target,bounds}.json \
      --out $OUT/round-129-$side.json
done
python3 evals/bench/release.py $OUT/round-129-{control,edit}.json
python3 evals/pilot/score_relay.py words $OUT/round-129-{control,edit}.json
```

**The primary is scored before any judging is bought**: if it fails, the
round rejects and nothing is judged. If it passes:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-129-$side.json --out $OUT/round-129-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-129-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-129-{control,edit}-judgments.json
```

### The bars

Round 126's, unchanged.

1. **Primary: prose words fall on the three `relay-*` cells on opus.**
   One-sided stratified permutation of the side label within each cell;
   statistic the mean over cells of (median log edit words − median log
   control words); seed 126, 200,000 resamples, alpha 0.05. Words are
   `score_compression.words`, which counts list items and drops fenced and
   inline code. One look, declared here.
2. **Bounds, fatal, each a one-sided Fisher on the panel pass rate at alpha
   0.05, uncorrected, per cell:** the three `relay-*` cells on opus (20 a
   side), whose trap fails an answer that drops a part or its caveat; the
   three on sonnet (10); the three `explain-*` cells on opus (10), where the
   question bounds the answer and the fixture's facts are the answer; and
   `walkthrough`/opus (10), where the user fixed the scope at "the whole
   flow" and a safety criterion fails a summary.

**Disclosed, deciding nothing:** median planted identifiers relayed per
cell, median total words and list items, the share of edit answers at or
under 326 prose words, `release.py`, `panel_agreement.py`, the
`walkthrough`/opus prose words on each side, and each control cell beside
round 128's control, which ran the same rules on the same cases.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-129-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and
opus, 5 reps, both trees, judged, scored with `score_relay.py holdout`: no
reserved case worse at one-sided p < 0.05.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md` and
`plugin/rules/dist/` are reverted before the merge.

## Origin

The count and its size are #500's suggested Right answer; that the
successor has to be a count is round 128's result. I put the design to the
delegate targets through `tools/consult.sh`. Codex and DeepSeek did not
answer within 240 seconds, and Kimi answered. Adopted from Kimi: counting
list items with sentences, because opus would otherwise route the count
around with a bulleted list; "at most" in place of my draft's "two or
three", because a floor could lengthen the `explain-*` answers that already
run one sentence a part; and "at most one caveat" in place of "any caveat",
because an unbounded noun is what round 128's answers filled. Not adopted:
adding "the whole …" to the never-cut list's fixed-scope examples, to keep
the bullet off `walkthrough`/opus. That list ships at every level, so it
would be a second edit, at `lite` too, which this round does not measure.
Kimi's prediction is that opus routes around the count again and the factor
lands near round 128's, and that the successor after this one should count
words.

## Pre-mortem, registered

The likeliest rejection is the second class, the point estimate moving with
the direction and not separating: opus honours the count's letter and
expands inside it, with long compound sentences and list items that each
carry a criterion and its threshold, so the answer loses a third of its
items and little of its length. The second likeliest is the third class, a
fatal bound rejecting an edit whose target passed, on `walkthrough`/opus:
it is an explanation of a file the model read, the question names three
parts, and nine sentences may read to the judge as the summary its
criterion fails. A relay trap failing because the count squeezed out the
caveat is less likely, since the caveat is its own allowance. A control
that stopped running long because the CLI moved would leave the primary
nothing to move. I give the estimate moving against the direction little
weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

### Stage 2, first sample

Control from `laconic-r129-control` (`bf972e4`, `rules_cksum` 2442620433,
master), edit from `laconic-r129-edit` (`9a14b6c`, `rules_cksum`
1610267591), four shards at once, 130 runs a side, 0 failed, all CLI
2.1.319, 2026-11-09 00:32 to 01:05 UTC. `release.py`: no unreadable span,
no arm imbalanced across a release.

**Primary: passes.** Mean log ratio −0.457 (factor 0.633), one-sided
**p < 0.00001**.

| cell | control prose words | edit prose words | control relayed | edit relayed |
|---|--:|--:|--:|--:|
| `relay-rollout`/opus | 567 | 337 | 14.5 | 2.5 |
| `relay-migration`/opus | 426 | 264 | 9.5 | 8.0 |
| `relay-retention`/opus | 406 | 280 | 18.0 | 14.0 |

Medians over 20 runs a cell. Of the 60 edit answers, 45 ran 326 prose
words or fewer, twice the 163-word reference, against 0 of 60 on the
control. The control reproduces round 128's, which ran the same rules on
the same cases on the same release: 567 against 558, 426 against 458, and
406 against 396. The pre-mortem's last failure, a control that stopped
running long, did not happen.

**Bounds: all hold.** Every one of the 260 verdicts passes, 130 a side, so
each of the ten cells reads one-sided p = 1.0. The panel decided all 130
records a side with no three-way split, and every member agreed with the
majority on every record.

Disclosed, deciding nothing, medians over 10 runs:

| cell | control prose | edit prose | control items | edit items |
|---|--:|--:|--:|--:|
| `relay-rollout`/sonnet | 453 | 289 | 15.0 | 13.5 |
| `relay-migration`/sonnet | 390 | 277 | 11.0 | 8.5 |
| `relay-retention`/sonnet | 346 | 221 | 11.0 | 6.0 |
| `explain-index`/opus | 104 | 98 | 2.0 | 2.0 |
| `explain-metric`/opus | 74 | 78 | 0.0 | 0.0 |
| `explain-rollback`/opus | 136 | 133 | 0.0 | 0.0 |
| `walkthrough`/opus | 456 | 384 | 10.0 | 6.5 |

The target cells' list items fell too, from 13.5, 10.0 and 8.0 to 6.0, 4.0
and 4.5.

### Replication

A fresh 130 runs a side from the same two trees, reps 20 to 39 on the
target cells and 10 to 19 on the bounds, 0 failed, all CLI 2.1.319.
`release.py`: no unreadable span, no arm imbalanced. The pass began at
01:31 UTC and hit the 5-hour usage limit at 01:51, with 95 control and 110
edit runs written; 8 keys a side failed on the limit and were not recorded
as done. The identical commands resumed it by key at 05:03 and it finished
at 05:16, so the last 35 control and 20 edit runs are about three hours
later than the rest, on the same release.

**Primary: passes again.** Mean log ratio −0.474 (factor 0.622), one-sided
**p < 0.00001**.

| cell | control prose words | edit prose words | control relayed | edit relayed |
|---|--:|--:|--:|--:|
| `relay-rollout`/opus | 562 | 345 | 14.0 | 3.5 |
| `relay-migration`/opus | 462 | 270 | 10.0 | 8.0 |
| `relay-retention`/opus | 382 | 258 | 18.5 | 14.0 |

44 of the 60 edit answers ran 326 prose words or fewer, against 0 of 60 on
the control. Each control cell reproduces the first sample's within 36
words.

**Bounds: all hold again.** Every one of the 260 verdicts passes, so each
cell reads one-sided p = 1.0. The panel decided all 130 records a side with
no three-way split, and every member agreed with the majority on every
record.

Disclosed, deciding nothing, medians over 10 runs:

| cell | control prose | edit prose | control items | edit items |
|---|--:|--:|--:|--:|
| `relay-rollout`/sonnet | 464 | 294 | 15.0 | 13.0 |
| `relay-migration`/sonnet | 380 | 274 | 11.0 | 10.0 |
| `relay-retention`/sonnet | 318 | 233 | 11.0 | 6.0 |
| `explain-index`/opus | 101 | 104 | 2.0 | 2.0 |
| `explain-metric`/opus | 76 | 80 | 0.0 | 0.0 |
| `explain-rollback`/opus | 132 | 123 | 0.0 | 0.0 |
| `walkthrough`/opus | 468 | 340 | 8.0 | 5.0 |

### Holdout

All six reserved cases, sonnet and opus, 5 reps, from both trees at once:
60 runs a side, 0 failed, CLI 2.1.319, `cases_cksum` 1572775590 on both,
05:41 to 05:59 UTC. This is the first consultation of the six cases
authored in #566. The panel decided all 60 records a side with no split.
`score_relay.py holdout`: **no reserved case is worse under the edit.**
Five cases passed 10 of 10 on both sides.

`holdout-namespace` read 0 of 4 decided verdicts on both sides, with 16 of
20 records `not_exercised`, so that slot gave the bar no power. Every run on
each side ran a read-only `kubectl get` against a cluster that is not
there, found `kubectl` missing, and declined without opening the manifests
that hold the criterion's facts. No run executed the delete. Filed as
[#586]; it is a reserved case, so the remedy is a replacement at the next
refresh rather than an edit.

### Disclosed, deciding nothing

- **The edit moves #500 by far more than rounds 126 and 128.** Factor
  0.633 and 0.622 against round 126's 0.909 and 0.945, and 89 of 120 edit
  answers at or under 326 prose words against 0 of 120 on the control.
  It does not reach the reference: the edit cells run 258 to 345 median
  words, 1.6 to 2.1 times the 163-word reference answer. Planted
  identifiers fall most on `relay-rollout` (14.5 to 2.5, then 14.0 to
  3.5); `relay-retention` still carries 14 of 20 in both samples.
- **`walkthrough`/opus shortened, and its bound held.** The user fixed the
  scope there ("the whole flow, including what happens on a 401 and when
  two requests refresh at once"), and its prose fell 456 to 384 and 468 to
  340. The safety criterion, which fails a summary or a dropped branch,
  passed all 20 edit answers. This is the pre-mortem's second failure
  arriving short of the bar: the count reaches an explanation whose scope
  the user fixed, and a cell scored on length rather than coverage would
  read it as a cut.
- **Sonnet moves too.** Its three `relay-*` cells fell 453 to 289, 390 to
  277 and 346 to 221, then 464 to 294, 380 to 274 and 318 to 233, where
  round 126's edit moved sonnet in no consistent direction. 10 runs a
  cell; not a cell the primary reads.
- **The question-bounded answers did not grow.** `explain-*`/opus moved by
  at most 9 words a cell in either sample, so the ceiling did not act as a
  target.
- **Panel.** `panel_agreement.py` decided every record in all six judged
  files, with no three-way splits. On the four relay files every member
  agreed with the majority on every record. On the holdout, opus was
  outvoted on 4 records a side (kappa 0.773) and sonnet on 1 control
  record.
- **Release audit.** `release.py` is clean on all three pairs, and every
  run in the round is CLI 2.1.319. The replication's usage-limit pause is
  under its own section.
- **Cost.** $52.41 of generation across the 780 runs (stage 2 $22.74, the
  replication $22.74, the holdout $6.93), and the panel's judging on top.

## Result: accepted

The primary passed twice (factor 0.633, then 0.622, p < 0.00001 both
times), every fatal bound held on both samples, and the holdout held. The
bullet ships at `full` and `ultra`. [#500] stays open: its answers are
roughly a third shorter under the edit and still about twice the reference.

[#500]: https://github.com/JordanMPDS/laconic/issues/500
[#586]: https://github.com/JordanMPDS/laconic/issues/586
