# Round 130: an explanation's count reaches the sentences inside its list items (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds. This file is committed first, with
`plugin/rules/laconic.md` at master, so the control worktree is that commit;
the edit and the regenerated `plugin/rules/dist/*.md` are committed after it.
Both commits precede any generation.

`bash tools/candidate-due.sh` exited 0 at registration: round 129 tested a
rule candidate, so this round could have measured. It carries a candidate
anyway, under **The edit** below, because [#500] is still the one open rules
issue whose defect fires at master rules. `bash tools/release-due.sh` exited
0: v0.7.0, which ships round 129's bullet, is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document. The answer ran 620
words and relayed the document. The 122-word answer the user wanted held
what each stage is, what it must show to pass, and the one caveat that
changes how to read the second stage.

[Round 129](round-129.md), accepted and shipped in v0.7.0, put a count on
it: "Explaining what you read gets at most three sentences or list items for
each part the question names, plus at most one caveat that changes how to
read it." Prose words on the three `relay-*`/opus cells fell by a factor of
0.633, then 0.622. The edit cells still ran 258 to 345 median words, 1.6 to
2.1 times the cases' 163-word reference answer.

How they stayed long is visible in the answers. Round 129's median
`relay-rollout`/opus edit answer (338 prose words) keeps exactly three
bullets for each stage, and each bullet is a paragraph of two to four
sentences behind a bold label ("**Duration and pass criteria:** It runs for
at least 7 days and must include a full weekend. Every day in
`ranker_shadow_daily` must show…"); its caveat is three sentences more. The
median `relay-retention`/opus answer (281) has the same shape, with a
four-sentence caveat. The bullet counted list items as units, and opus kept
the units and lengthened each one: round 129's pre-mortem named this, "opus
honours the count's letter and expands inside it", as its likeliest
rejection, and it arrived inside an accept.

This round closes that route. The count stays the issue's own ("two or
three sentences per stage, plus the one caveat"), and it is made to reach
the sentences inside a list item and the caveat.

## Fire rate: no precheck

Master's rules (`rules_cksum` 1610267591) are round 129's edit side, which
was generated twice today on CLI 2.1.319, the release this round registers
on. It read 337, 264 and 280, then 345, 270 and 258 median prose words on
the three `relay-*`/opus cells, every one above the 163-word reference. A
precheck would buy 30 opus calls to re-read that, so none is run. The
round's own control measures the defect on whatever release stage 2 runs
on, and the pre-mortem names a control that no longer runs long.

## The instrument

Round 126's, unchanged, as rounds 128 and 129 used it: the three pilot
cases `evals/pilot/relay-{rollout,migration,retention}`, the bounds cells,
and `evals/pilot/score_relay.py` with its seed (126) and its bars. This
round edits none of them, and no pilot case or criterion has changed since
round 129 ran. One allocation changes, below: `walkthrough`/opus moves from
10 runs a side to 20.

## The edit

Round 129's bullet in `level: full`, rewritten in place:

```diff
-- Explaining what you read gets at most three sentences or list items for
-  each part the question names, plus at most one caveat that changes how to
-  read it.
+- Explaining what you read gets at most three sentences for each part the
+  question names, counting those in lists, plus one for a caveat that
+  changes how to read it.
```

Two things move. The unit is the sentence wherever it sits, so a list item
of three sentences spends the whole part's allowance; "counting those in
lists" is what round 129's "sentences or list items" let opus read the
other way. And the caveat gets one sentence rather than one caveat of any
length. The size does not change: two named parts still allow six sentences
and the caveat a seventh, about the length of #500's 122-word answer and
the cases' 163-word reference. It is still a ceiling: the `explain-*`
answers already run one to three sentences a part. The bullet stays at
`full`, where #500 was observed, and reaches `ultra` by inheritance. It
adds 9 characters to every slice it is in, which leaves `ultra` at 9,487
of the 9,500 that `tests/test_laconic.sh` allows.

A user who fixes the scope is still governed by the never-cut explain
bullet, which outranks every level, and the bullet carries no precedence
sentence ([round 10](round-10.md)).

## Hypothesis

> Rewriting round 129's bullet to "Explaining what you read gets at most
> three sentences for each part the question names, counting those in
> lists, plus one for a caveat that changes how to read it." should move
> median prose words on `relay-rollout`, `relay-migration` and
> `relay-retention` on opus **down**, without lowering the panel pass rate
> on those cells, on the same three on sonnet, on `explain-index`,
> `explain-metric` and `explain-rollback` on opus, or on `walkthrough`/opus.

## Stage 2: the edit on opus (280 calls, 220 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r130-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r130-edit` at the edit commit. Both
are on disk rather than under `/tmp`, which is memory on this machine. Two
shards a side, four `run.py` processes. `walkthrough`/opus runs in the
target shard so it gets 20 runs a side:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='relay-*:opus,walkthrough:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r130-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-130-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r130-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-130-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-130-$side-{target,bounds}.json \
      --out $OUT/round-130-$side.json
done
python3 evals/bench/release.py $OUT/round-130-{control,edit}.json
python3 evals/pilot/score_relay.py words $OUT/round-130-{control,edit}.json
```

**The primary is scored before any judging is bought**: if it fails, the
round rejects and nothing is judged. If it passes:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-130-$side.json --out $OUT/round-130-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-130-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-130-{control,edit}-judgments.json
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
   `walkthrough`/opus (20), where the user fixed the scope at "the whole
   flow" and a safety criterion fails a summary or a dropped branch.

`walkthrough`/opus gets 20 a side because it is the bound this edit is
likeliest to reach. At 10 a side a one-sided Fisher cannot reject 10 of 10
against 7 of 10 (p = 0.105). At 20 a side it still cannot reject 20 of 20
against 16 of 20 (p = 0.053), and it rejects 15 of 20 (p = 0.024). That is
coarse, and it is the resolution this round buys.

**Disclosed, deciding nothing:** median planted identifiers relayed per
cell, median total words, list items and sentences, the share of edit
answers at or under 326 prose words, `release.py`, `panel_agreement.py`,
the `walkthrough`/opus prose words on each side, and each control cell
beside round 129's edit side, which ran the same rules on the same cases.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-130-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and
opus, 5 reps, both trees, judged, scored with `score_relay.py holdout`: no
reserved case worse at one-sided p < 0.05.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md` and
`plugin/rules/dist/` are reverted before the merge.

## Origin

Counting sentences inside list items is this round's reading of round 129's
answers, and the size is #500's suggested Right answer. I put the design to
the delegate targets through `tools/consult.sh`, with a word cap ("at most
60 words for each part") as the alternative. Codex and DeepSeek did not
answer within 240 seconds; Kimi answered. Adopted from Kimi: sentences
rather than a word cap, because a sentence is the unit opus tracks most
reliably and a word constant varies widely per part, with the word cap held
back for a successor if this round's answers cluster at three long
sentences a part; and no carve-out for a user-fixed scope, since the
never-cut list already outranks the bullet and the carve-out would spend
the slice's remaining characters restating it. Kimi's nit that "plus one
for" reads ambiguously is not adopted: "plus one sentence for" costs 9 of
the 22 characters left, and here "one" follows "three sentences" in the
same clause. Adapted from Kimi: it suggested gating on `walkthrough`/opus at
20 of 20; this round keeps the registered Fisher bar and doubles the cell's
runs instead, so the bound is the instrument's and not one chosen for this
edit.

## Pre-mortem, registered

The likeliest rejection is the second class, the estimate moving with the
direction and not separating: opus keeps three sentences a part and makes
each one carry a part's whole list, joined by semicolons and comma series
("must show p99 at or under 45 ms, errors at or under 0.1%, overlap between
55% and 85%, and no null over 2%"), so sentences fall by half and words by
far less. A disclosed mean sentence length above round 129's would be that
failure's mark. The second likeliest is the third class on
`walkthrough`/opus: nine sentences for a whole-flow walkthrough with two
named branches may read to the judge as the summary its criterion fails,
and this round has doubled that cell's runs to see it. A relay trap failing
because one caveat sentence drops the "a flat reading is not evidence"
half is possible and less likely. A control that stopped running long would
leave the primary nothing to move. I give the estimate moving against the
direction little weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->
