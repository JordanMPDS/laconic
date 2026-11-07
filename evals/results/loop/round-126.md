# Round 126: an explanation of a spec just read relays the spec (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds and the reference answer's word count.
This file and the instrument are committed first, with `rules/laconic.md` at
master, so the control worktree is that commit; the edit and the regenerated
`rules/dist/*.md` are committed after it. Both commits precede any
generation.

`bash tools/candidate-due.sh` exited 0 at registration: round 125 carried a
rule edit, so this round may measure. It carries one anyway, under **The
edit** below, behind a stage-1 precheck that can withdraw it unrun.
`bash tools/release-due.sh` exited 0: v0.4.5 is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document describing two rollout
stages. The answer ran 620 words, two headed sections, 15 bullets and a
lettered sub-list, and relayed most of the document: every pass criterion,
numbered alerts, table and flag names, scheduling mechanics, sample sizes,
the stop list and a timeline. Asked why it was so long, the model wrote 122
words that answered the question: what each stage is, what it must show to
pass, and the one caveat that changes how to read the second stage.

The model's own account names the sentence it misread. The shared length
paragraph says a requested explanation "gets the scope it needs", and with a
detailed source freshly in context it read "the scope it needs" as the scope
the source has. Every fact in the document looked needed because the
document contained it. The never-cut explain bullet already says an
explanation otherwise gets "the smallest set of claims that fully answers
it", and that did not stop it.

No instrument the loop owns asks this. `explain-*` asks "what is X and what
is Y" about two named objects in an incident write-up, which bounds the
answer by its question; `walkthrough` fixes its scope ("the whole flow");
[#298]'s families measure restatement of earlier turns, and none of this is
restatement, because the user had never seen the document.

## The instrument

Three new pilot cases, `evals/pilot/relay-{rollout,migration,retention}`.
Each is a two-part spec of 107 to 141 lines and a prompt in [#500]'s shape:

> read ROLLOUT.md — explain the shadow stage and the live A/B stage. Don't
> edit anything.

`MIGRATION.md` asks for the dual-write phase and the cutover, and
`RETENTION.md` for the soft-delete window and the hard purge. Each spec holds
what #500's did: pass criteria with numbers, a metric definition with its
rationale, mechanics, alerts, owners' channels, run times and a timeline. Each
carries one caveat that changes how to read its second part (the A/B test
cannot detect the revenue drop its guardrail names; the write stop is
one-way; backups are not purged), and the quality trap requires the two parts
explained and that caveat carried, with the fixture facts written into the
criterion because no judge can open a file ([#411]).

Each spec also plants 18 to 20 identifiers no explanation needs: alert ids,
tables, flags, job and channel names, run times, batch sizes.
`evals/pilot/score_relay.py` counts how many of its fixture's planted strings
an answer carries (`relayed`), and its selftest checks every planted string is
in its fixture.

A reference answer to `relay-rollout` that explains both stages, names all
four shadow criteria and carries the revenue caveat is 163 prose words.

## The edit

The shared length paragraph, which every level carries:

```diff
 **Length scales to the request, at every level.** A yes/no question gets a word
 or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets the scope it needs, and no claim in it twice. Laconic governs volunteered
-content.
+gets the scope the question needs, not the scope of the source you read to
+answer it, and no claim in it twice. Laconic governs volunteered content.
```

It replaces the phrase the model said it misread, in the place it misread it,
and caps nothing: a question that asks for the whole flow still needs the
whole flow. The slices grow by 61 characters, to 6,581 (`lite`), 8,886
(`full`) and 9,351 (`ultra`), under the 9,500 budget.

## Hypothesis

> Replacing "gets the scope it needs" with "gets the scope the question
> needs, not the scope of the source you read to answer it" should move
> median prose words on `relay-rollout`, `relay-migration` and
> `relay-retention` on opus **down**, without lowering the panel pass rate on
> those cells, on the same three on sonnet, on `explain-index`,
> `explain-metric` and `explain-rollback` on opus, or on `walkthrough`/opus.

## Stage 1: does #500 fire on opus? (30 opus calls)

Master rules, from the control worktree, the laconic arm, 10 reps a cell.
Words and planted identifiers only; nothing is judged.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
cd /home/jordan/projects/laconic-r126-control      # this commit: master rules
python3 evals/bench/run.py --arms laconic --cells 'relay-*:opus' --reps 10 \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 1 \
    --snapshot $OUT/round-126-precheck.json
python3 evals/pilot/score_relay.py precheck $OUT/round-126-precheck.json
```

**Registered pass condition: both of these, over the 30 answers.**

1. At least 15 run **300 prose words or more**, about 1.8 times the reference
   answer. This is the room the primary needs. [Round 122](round-122.md) was
   rejected for registering a length edit against answers that turned out
   not to be long.
2. At least 15 carry **2 or more** of their fixture's planted identifiers.
   This is what makes the room #500's: an answer can be long because it is
   thorough about what was asked, and the edit is not about that.

Each condition is P(Binomial(30, p) >= 15) at a true per-answer rate p:
**0.017** at p = 0.3, 0.175 at 0.4, **0.572** at 0.5, 0.903 at 0.6 and 0.994
at 0.7 (`score_relay.py --selftest` prints them). So the precheck mostly
withdraws an edit whose defect sits in fewer than four answers of ten, and
mostly buys one where it sits in more than six. A precheck that does not fire
is not evidence #500 is absent on opus, only that it is too rare here to buy
a round on.

**If it does not fire**, stage 2 is not generated, the edit is reverted
unrun, this document records the precheck and becomes a measuring round, and
round 127 owes a candidate.

## Stage 2: the edit on opus, only if stage 1 fires (260 calls, 200 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r126-control` at the registration commit, the
edit from this branch. Two shards a side, four `run.py` processes:

```sh
T='relay-*:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus,walkthrough:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do   # control from laconic-r126-control
  ( cd <tree for $side> && python3 evals/bench/run.py $common --reps 20 \
      --cells "$T" --snapshot $OUT/round-126-$side-target.json ) &
  ( cd <tree for $side> && python3 evals/bench/run.py $common --reps 10 \
      --cells "$B" --snapshot $OUT/round-126-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-126-$side-{target,bounds}.json \
      --out $OUT/round-126-$side.json
done
python3 evals/bench/release.py $OUT/round-126-{control,edit}.json
python3 evals/pilot/score_relay.py words $OUT/round-126-{control,edit}.json
```

`walkthrough` is borrowed into `evals/pilot` by symlink so one `--cases-dir`
reaches it. **The primary is scored before any judging is bought**: if it
fails, the round rejects and nothing is judged. If it passes:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-126-$side.json --out $OUT/round-126-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-126-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-126-{control,edit}-judgments.json
```

### The bars

1. **Primary: prose words fall on the three `relay-*` cells on opus.**
   One-sided stratified permutation of the side label within each cell;
   statistic the mean over cells of (median log edit words − median log
   control words); seed 126, 200,000 resamples, alpha 0.05. Words are
   `score_compression.words`, which counts list items and drops fenced and
   inline code. One look, declared here.
2. **Bounds, fatal, each a one-sided Fisher on the panel pass rate at alpha
   0.05, uncorrected, per cell:** the three `relay-*` cells on opus (20 a
   side), whose trap fails an answer that drops its caveat, which is where an
   edit that cuts too far shows first; the three on sonnet (10); the three
   `explain-*` cells on opus (10), where the question bounds the answer and
   the fixture's facts are the answer; and `walkthrough`/opus (10), where
   the user fixed the scope at "the whole flow" and a safety criterion fails
   a summary.

**Disclosed, deciding nothing:** median planted identifiers relayed per
cell, median total words and list items, `release.py`, `panel_agreement.py`,
and the `walkthrough`/opus prose words on each side.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-126-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and opus,
5 reps, both trees, judged, scored with `score_relay.py holdout`: no reserved
case worse at one-sided p < 0.05.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `rules/laconic.md` and `rules/dist/` are
reverted before the merge.

## Origin

I put the design to the delegate targets through `tools/consult.sh`; Codex
and DeepSeek did not answer within the timeout, Kimi answered. Adopted from
Kimi: the precheck has to show relaying and not only length, which became
condition 2, with the planted-identifier counter it proposed as the matcher;
and keeping the edit in the shared sentence rather than the `full` section,
because the misread sentence is shared and would stay misreadable at every
other level. Not adopted: a non-inferiority margin on the bounds in place of
the one-sided Fisher, which `AGENTS.md` fixes for fatal screens; a word-floor
bound on `walkthrough`, which its safety criterion already covers by failing
a summary; and bounds at `lite` and `ultra`, which this round does not buy and
discloses instead: the edit reaches every level and is tested at `full` only.

## Pre-mortem, registered

The likeliest outcome is that stage 1 does not fire: every open `rules` issue
read zero in its own precheck before round 125, and opus may explain two
parts of a spec in under 300 words without being told to. If it fires, the
likeliest rejection is the third class, a fatal bound rejecting an edit whose
target passed: the shortened answer drops the caveat, and a `relay-*`/opus
cell's pass rate falls, because "not the scope of the source" reads as
licence to leave the source's warning behind. The second most likely is the
point estimate moving with the direction and not separating, because the
never-cut bullet's "smallest set of claims" already says this and did not
stop #500. I give the estimate moving against the direction little weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#411]: https://github.com/JordanMPDS/laconic/issues/411
[#500]: https://github.com/JordanMPDS/laconic/issues/500
