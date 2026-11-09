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

[#500]: https://github.com/JordanMPDS/laconic/issues/500
