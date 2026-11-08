# Round 128: an explanation of what you read gets a shape, not only a scope (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds. This file is committed first, with
`plugin/rules/laconic.md` at master, so the control worktree is that commit;
the edit and the regenerated `plugin/rules/dist/*.md` are committed after it.
Both commits precede any generation.

`bash tools/candidate-due.sh` exited 1 at registration: round 127 proposed no
rule edit, so this round has to carry one, and it does, under **The edit**
below. `bash tools/release-due.sh` exited 0: v0.6.0 is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document. The answer ran 620
words and relayed the document. The 122-word answer the user wanted held
what each stage is, what it must show to pass, and the one caveat that
changes how to read the second stage.

[Round 126](round-126.md) accepted a one-phrase edit to the shared length
paragraph: a requested explanation "gets the scope the question needs, not
the scope of the source you read to answer it". It moved opus by a factor of
0.909 and then 0.945, and every edit cell in both samples still ran more
than twice the 163-word reference answer (`relay-rollout` 546 and 557). That
edit is master now. The merge of its pull request closed #500 against the
round's own result, and the issue was reopened for this round.

Round 126's edit tells the model what scope an explanation does not take. It
says nothing about what an explanation of a source does contain, so a model
holding a detailed spec still has every fact in it as a candidate. The
design-question bullet at `full` already solves the same problem for "how
would that be built?" by naming the answer's parts (the recommendation, the
one or two decisions that fork it) and giving the rest an exit ("a name for
the depth you left out"). Five instruments on [#46] have read null on opus
since. This round gives a requested explanation of a source the same kind of
shape.

## Fire rate: no precheck

Round 126's edit side is master's rules (`rules_cksum` 2442620433), and it
was generated today on CLI 2.1.319, the release this round registers on.
Over its two samples **120 of 120** `relay-*`/opus answers ran 300 prose
words or more (the shortest 321), and **120 of 120** carried two or more of
their fixture's planted identifiers, the two conditions round 126's
precheck registered. A precheck now would buy 30 calls to re-read a rate
measured at 120 the same day, so none is run. If the CLI moves before stage
2, the round's own control measures the defect on the new release, and a
control that no longer runs long leaves the primary nothing to move, which
the pre-mortem below names.

## The instrument

Round 126's, unchanged: the three pilot cases
`evals/pilot/relay-{rollout,migration,retention}`, the bounds cells, and
`evals/pilot/score_relay.py` with its seed (126) and its bars. This round
edits none of them. The three relay cases have not changed since round 126
ran, so its edit side and this round's control can be read against each
other on words. Two bound criteria have: `walkthrough`'s trap gained the
fixture facts it grades in [#552], and `explain-metric`'s record was
corrected in [#582]. Both sides here are judged under today's criteria, and
round 126's verdicts on those two cells are not compared with them. Prompts
take the form:

> read ROLLOUT.md — explain the shadow stage and the live A/B stage. Don't
> edit anything.

## The edit

One bullet in `level: full`, after the design-question bullet and its
example pair:

```diff
   - Right: "Derive alerts from the log row the loop already writes, in
     whatever monitoring you already run — which stack is that? The schema
     and the dedup rules are the next level down."
+- Explaining what you read gets what each part is, what decides it, and any
+  caveat that changes how to read it. Name the depth you left out.

 Typical shape: one to three sentences, or a short list. One sentence is a
 complete answer.
```

The three parts are #500's own: the issue's suggested rule names "what it
is, what it is for, what decides it", and its 122-word answer carried the
caveat. "Name the depth you left out" is the design bullet's exit, reused
word for word. The bullet sits at `full` because #500 was observed there,
and `lite` cuts ceremony only. It reaches `ultra` by inheritance. A user
who fixes the scope is still governed by the never-cut explain bullet,
which outranks every level. The delivered `full` slice grows by 143
characters to 8,855 and `ultra` to 9,315, as `tests/test_laconic.sh`
counts them, against the 9,500 budget. An example pair would take most of
the 185 that remain, so none is added.

## Hypothesis

> Adding "Explaining what you read gets what each part is, what decides it,
> and any caveat that changes how to read it. Name the depth you left out."
> to `level: full` should move median prose words on `relay-rollout`,
> `relay-migration` and `relay-retention` on opus **down**, without lowering
> the panel pass rate on those cells, on the same three on sonnet, on
> `explain-index`, `explain-metric` and `explain-rollback` on opus, or on
> `walkthrough`/opus.

## Stage 2: the edit on opus (260 calls, 200 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r128-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r128-edit` at the edit commit. Two
shards a side, four `run.py` processes:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='relay-*:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus,walkthrough:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r128-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-128-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r128-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-128-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-128-$side-{target,bounds}.json \
      --out $OUT/round-128-$side.json
done
python3 evals/bench/release.py $OUT/round-128-{control,edit}.json
python3 evals/pilot/score_relay.py words $OUT/round-128-{control,edit}.json
```

**The primary is scored before any judging is bought**: if it fails, the
round rejects and nothing is judged. If it passes:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-128-$side.json --out $OUT/round-128-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-128-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-128-{control,edit}-judgments.json
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
cell, median total words and list items, `release.py`, `panel_agreement.py`,
the `walkthrough`/opus prose words on each side, and each control cell
beside round 126's edit side, which ran the same rules on the same cases.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-128-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and
opus, 5 reps, both trees, judged, scored with `score_relay.py holdout`: no
reserved case worse at one-sided p < 0.05. This is the first consultation of
the second-generation set authored at the [#566] refresh.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md` and
`plugin/rules/dist/` are reverted before the merge.

## Origin

I put the design to the delegate targets through `tools/consult.sh`. Codex
and DeepSeek did not answer within 300 seconds, and Kimi answered. Adopted
from Kimi: "any caveat" in place of "the caveat", because a definite article
makes the caveat a slot that a source with no such caveat would have filled
with an invented one; and "Name the depth you left out" in place of my
draft's "The rest stays in the source", which restated round 126's scope
sentence, where the design bullet's exit is already in the file. Not
adopted: "Explaining part of what you read", meant to keep the bullet off
`walkthrough`'s whole-flow request, because each relay spec has two parts
and its question asks for both, so the narrowed trigger would miss the
target cells; and "what it is judged on" for "what decides it", which fits
a rollout stage and not a purge or a cutover. Kimi also noted that the
never-cut list's fixed-scope examples ("in full", "complete", "every
check") do not include "the whole flow", which makes `walkthrough`/opus the
bound this edit is likeliest to fail.

## Pre-mortem, registered

The likeliest rejection is the third class, a fatal bound rejecting an edit
whose target passed, on `walkthrough`/opus: it is an explanation of a file
the model read, so the bullet applies to it word for word, and "Name the
depth you left out" invites a summary of the flow where its criterion fails
one. The second likeliest is the point estimate moving with the direction
and not separating. That would mean naming an explanation's parts does no
more than round 126's scope sentence did, and opus keeps every criterion
and identifier as part of "what decides it". The third is a control that no
longer runs long because the CLI moved, which would leave the primary
nothing to move. I give the estimate moving against the direction little
weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#500]: https://github.com/JordanMPDS/laconic/issues/500
[#552]: https://github.com/JordanMPDS/laconic/pull/552
[#582]: https://github.com/JordanMPDS/laconic/pull/582
[#566]: https://github.com/JordanMPDS/laconic/issues/566
