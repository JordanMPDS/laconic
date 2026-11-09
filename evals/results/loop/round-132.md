# Round 132: an explanation of what you read gets a word count per part (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds. This file is committed first, with
`plugin/rules/laconic.md` at master, so the control worktree is that commit;
the edit and the regenerated `plugin/rules/dist/*.md` are committed after it.
Both commits precede any generation.

`bash tools/candidate-due.sh` exited 1 at registration: round 131 measured
and proposed no rule edit, so this round has to carry a candidate, which is
under **The edit** below. `bash tools/release-due.sh` exited 0: v0.7.0,
which ships round 129's bullet, is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document. The answer ran 620
words and relayed the document. The 122-word answer the user wanted held
what each stage is, what it must show to pass, and the one caveat that
changes how to read the second stage.

Four rounds have tested edits on it:

| round | edit | factor on prose words | verdict |
|---|---|--:|---|
| [126](round-126.md) | "the scope the question needs, not the scope of the source" | 0.909 | accepted |
| [128](round-128.md) | a shape: what each part is, what decides it, any caveat | 0.977 | rejected |
| [129](round-129.md) | at most three sentences or list items a part, plus one caveat | 0.633, 0.622 | accepted |
| [130](round-130.md) | at most three sentences a part, counting those in lists | 1.001 | rejected |

Round 130 found that opus does not keep a sentence count. Its edit answers
carried 16 to 23.5 median sentences on the relay cells against an allowance
of seven, as its control and round 129's edit side did, at the same words a
sentence. So round 129's factor of 0.63 came from a bullet pressing on
length, not from a count opus kept. Master's answers still run 244 to 316
median prose words on the three cells, 1.5 to 1.9 times the cases'
163-word reference answer.

Where the length now sits is visible in round 130's median
`relay-rollout`/opus control answer (319 prose words): the shadow stage gets
143 words, the A/B stage 126, and the caveat 50. The
reference gives each stage about 65 and the caveat about 35. The excess is
in the parts, so this round bounds the parts, in the unit the primary
measures.

## Fire rate: no precheck

Master's rules (`rules_cksum` 1610267591) were round 130's control,
generated today on CLI 2.1.319, the release this round registers on. It
read 316, 244 and 270 median prose words on the three `relay-*`/opus cells,
every one above the 163-word reference. A precheck would buy 30 opus calls
to re-read that, so none is run. The round's own control measures the
defect on whatever release stage 2 runs on, and the pre-mortem names a
control that no longer runs long.

## The instrument

Round 126's, as rounds 128 to 130 used it: the three pilot cases
`evals/pilot/relay-{rollout,migration,retention}`, the bounds cells, and
`evals/pilot/score_relay.py` with its seed (126) and its bars, with
`walkthrough`/opus at 20 runs a side as in round 130. No pilot case or
criterion has changed since round 130 ran.

One bar is added, in this commit, before any generation:
`score_relay.py readability`. A word cap is the edit likeliest to buy length
with grammar, which the rules forbid ("No dropped articles. No telegraphic
fragments."), and none of round 126's bars reads grammar. The bound uses
`metrics.score`'s deterministic violations, the validated detectors behind
the ruleset's own policy ranks: an arrow inside a sentence, a shortened word,
a sentence that starts in lowercase. Re-scored on the archive, it holds on
round 129 (60 of 60 clean answers on both sides) and round 130 (60 of 60 on
both).

## The edit

Round 129's bullet in `level: full`, with the unit changed and nothing else:

```diff
-- Explaining what you read gets at most three sentences or list items for
-  each part the question names, plus at most one caveat that changes how to
-  read it.
+- Explaining what you read gets at most 60 words for each part the question
+  names, plus at most one caveat that changes how to read it.
```

Two named parts allow 120 words, and a caveat brings that to about the
cases' 163-word reference and #500's 122-word answer. The caveat clause is
byte for byte master's, so the unit is the only variable: round 130 already
bounded the caveat, to one sentence, and moved nothing. It is still a
ceiling. The `explain-*` answers already run 76 to 130 words in total. The
bullet stays at `full`, where #500 was observed, and reaches `ultra` by
inheritance. It removes 18 characters from every slice it is in.

A user who fixes the scope is still governed by the never-cut explain
bullet, which outranks every level, and the bullet carries no precedence
sentence ([round 10](round-10.md)).

## Hypothesis

> Changing round 129's bullet to "Explaining what you read gets at most 60
> words for each part the question names, plus at most one caveat that
> changes how to read it." should move median prose words on
> `relay-rollout`, `relay-migration` and `relay-retention` on opus
> **down**, without lowering the panel pass rate on those cells, on the
> same three on sonnet, on `explain-index`, `explain-metric` and
> `explain-rollback` on opus, or on `walkthrough`/opus, and without
> lowering the share of `relay-*`/opus answers free of readability
> violations.

## Stage 2: the edit on opus (280 calls, 220 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r132-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r132-edit` at the edit commit. Both
are on disk rather than under `/tmp`, which is memory on this machine. Two
shards a side, four `run.py` processes:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='relay-*:opus,walkthrough:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r132-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-132-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r132-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-132-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-132-$side-{target,bounds}.json \
      --out $OUT/round-132-$side.json
done
python3 evals/bench/release.py $OUT/round-132-{control,edit}.json
python3 evals/pilot/score_relay.py words $OUT/round-132-{control,edit}.json
python3 evals/pilot/score_relay.py readability $OUT/round-132-{control,edit}.json
```

**The primary and the readability bound are scored before any judging is
bought**: if either fails, the round rejects and nothing is judged. If both
pass:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-132-$side.json --out $OUT/round-132-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-132-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-132-{control,edit}-judgments.json
```

### The bars

Round 126's, unchanged, plus the readability bound.

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
3. **Readability, fatal:** the share of `relay-*`/opus answers with no
   `metrics.score` violation may not fall, pooled over the three cells (60
   a side), one-sided Fisher at alpha 0.05. Against a control at 60 of 60
   it rejects at 55 of 60 (p = 0.029) and not at 56 (p = 0.059).

**Disclosed, deciding nothing:** median planted identifiers relayed per
cell, the median article rate per cell, median total words, list items and
sentences, prose words on the `explain-*` and `walkthrough`/opus cells on
each side, the share of edit answers at or under 163 and at or under 326
prose words, `release.py`, `panel_agreement.py`, and each control cell
beside round 130's control, which ran the same rules on the same cases.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-132-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and
opus, 5 reps, both trees, judged, scored with `score_relay.py holdout`: no
reserved case worse at one-sided p < 0.05.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md` and
`plugin/rules/dist/` are reverted before the merge.

## Origin

The word cap is round 130's held-back alternative: Kimi, through
`tools/consult.sh` for that round, preferred sentences and kept a word cap
for the successor. Round 130's result is the reason to take it now: opus
did not keep the sentence count, so the remaining candidate unit is the
one the primary measures. The readability bound is mine. I put this design
to the delegate targets through `tools/consult.sh`. Codex and DeepSeek did
not answer within 240 seconds; Kimi answered and argued against the unit
change, on two grounds. First, that the parts already run about 60 words
and the excess is the caveat; round 130's median control answer gives the
stages 143 and 126 words and the caveat 50, so that is not adopted, and
round 130 had already bounded the caveat to no effect. Second, that a digit
word budget reads as a quota when an answer is under it, padding the
`explain-*` answers toward the allowance. That prediction is adopted into
the pre-mortem and the disclosures (prose words on the `explain-*` cells on
each side). Kimi also endorsed the readability bound.

## Pre-mortem, registered

The likeliest rejection is the second class, the estimate moving with the
direction and not separating: opus treats "60 words" as loosely as it
treated "three sentences", and the bullet's pressure on length is the same
as master's, so the factor lands near 1. Round 130 is the precedent, and a
word constant is no easier to keep mid-generation than a sentence count.
The second likeliest is the third class, on two bounds: `walkthrough`/opus,
if 60 words a step reads as licence to summarise a whole flow the user
asked for, and the relay traps, if a 60-word part drops the criterion the
judge needs or the caveat loses its "a flat reading is not evidence" half.
The readability bound firing on clipped, article-less prose is possible
and less likely, since the file's grammar rules sit above this bullet. Kimi
predicts padding on the `explain-*` cells; that would show in the
disclosures and decides nothing unless it costs a verdict. A control that
stopped running long would leave the primary nothing to move. I give the
estimate moving against the direction little weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

### Stage 2

Control from `laconic-r132-control` (`da4183c`, `rules_cksum` 1610267591,
master), edit from `laconic-r132-edit` (`c6ea4eb`, `rules_cksum`
1859532872), four shards at once, 140 runs a side, 0 failed, all CLI
2.1.319, 2026-11-09 09:23 to 10:02 UTC. The first launch ran under a
600-second tool timeout that killed all four shards after 136 runs; the
identical commands resumed them by key at 09:33, on the same release.
`release.py`: no unreadable span, no arm imbalanced across a release.

**Primary: passes.** Mean log ratio −0.318 (factor **0.728**), one-sided
**p < 0.00001**.

| cell | control prose words | edit prose words | control relayed | edit relayed |
|---|--:|--:|--:|--:|
| `relay-rollout`/opus | 322 | 208 | 2.0 | 0.0 |
| `relay-migration`/opus | 252 | 192 | 8.0 | 7.0 |
| `relay-retention`/opus | 246 | 191 | 14.0 | 13.0 |

Medians over 20 runs a cell. Each control cell reads within 24 words of
round 130's control, which ran the same rules on the same release.

**Readability: holds.** 60 of 60 answers free of violations on both sides,
one-sided p = 1.0. Median article rate 0.091, 0.090 and 0.103 on the
control against 0.081, 0.094 and 0.104 on the edit.

**Bounds: all hold.** Every one of the 280 verdicts passes, so each cell
reads one-sided p = 1.0, `walkthrough`/opus at 20 of 20 on both sides.
The panel decided all 140 records a side with no three-way split, and
every member agreed with the majority wherever it voted; kimi cast no vote
on 3 control and 1 edit records, which sonnet and opus decided together.

**Opus does not keep 60 words a part either.** The median
`relay-rollout`/opus edit answer (210 prose words) is two bold-labelled
paragraphs of 97 and 113 words, the caveat folded into the second, and no
list. Against round 130's median control answer it drops the sign-off and
the definition of a successful search and cuts the overlap band's gloss
from three sentences to two: the parts lost elaboration, and neither
reached 60. 3 of the 60 edit
answers on the relay cells ran 163 prose words or fewer, against 0 of 60 on
the control; 60 of 60 edit answers ran 326 or fewer, against 48.

Disclosed, deciding nothing, medians. Sentences are this round's count
(prose after list markers and headings are dropped, split by
`metrics.SENTENCE_SPLIT`), which reads round 130's control at 19.0, 16.5,
16.0 and 23.0, a little under that round's own figures:

| cell | control sentences | edit sentences | control words a sentence | edit words a sentence |
|---|--:|--:|--:|--:|
| `relay-rollout`/opus | 18.0 | 13.0 | 17.5 | 15.8 |
| `relay-migration`/opus | 17.5 | 15.0 | 15.0 | 12.7 |
| `relay-retention`/opus | 14.0 | 14.0 | 16.4 | 13.0 |
| `walkthrough`/opus | 24.5 | 21.5 | 14.4 | 13.7 |

| cell | control prose | edit prose | control items | edit items |
|---|--:|--:|--:|--:|
| `relay-rollout`/sonnet | 299 | 195 | 13.0 | 4.0 |
| `relay-migration`/sonnet | 288 | 234 | 10.0 | 8.0 |
| `relay-retention`/sonnet | 221 | 178 | 6.0 | 0.0 |
| `explain-index`/opus | 94 | 90 | 2.0 | 2.0 |
| `explain-metric`/opus | 82 | 78 | 0.0 | 0.0 |
| `explain-rollback`/opus | 128 | 130 | 0.0 | 0.0 |
| `walkthrough`/opus | 328 | 286 | 7.0 | 2.0 |

Kimi's padding prediction did not appear: the `explain-*` answers moved by
−4, −4 and +2 words.

### Replication

A fresh 140 runs a side from the same two trees, reps 20 to 39 on the
target cells and 10 to 19 on the bounds, 0 failed, all CLI 2.1.319,
10:32 to 11:11 UTC. `release.py`: no unreadable span, no arm imbalanced.

**Primary: passes again.** Mean log ratio −0.337 (factor **0.714**),
one-sided **p < 0.00001**.

| cell | control prose words | edit prose words | control relayed | edit relayed |
|---|--:|--:|--:|--:|
| `relay-rollout`/opus | 324 | 208 | 1.5 | 0.0 |
| `relay-migration`/opus | 264 | 185 | 8.0 | 7.0 |
| `relay-retention`/opus | 242 | 196 | 14.0 | 13.0 |

**Readability: holds again**, 60 of 60 on both sides. **Bounds: all hold
again**, every one of the 280 verdicts a pass, `walkthrough`/opus 20 of 20
on both sides. The panel decided every record with no split; kimi cast no
vote on 3 control and 1 edit records.

Disclosed, deciding nothing, medians: `walkthrough`/opus 372 against 260
prose words; `explain-index`, `explain-metric` and `explain-rollback`/opus
98, 82 and 129 against 106, 68 and 122; the sonnet relay cells 290, 278 and
226 against 217, 242 and 188. 1 of 60 edit relay answers ran 163 prose
words or fewer, against 0; 60 of 60 ran 326 or fewer, against 50.

### Holdout

All six reserved cases, sonnet and opus, 5 reps, from both trees at once:
60 runs a side, 0 failed, CLI 2.1.319, `cases_cksum` 3353367341 on both,
11:42 to 12:00 UTC. This is the second consultation of the five cases
authored in #566 and the first of `holdout-scratch`, which replaced
`holdout-namespace` in #589; all six are within their budgets. The panel
decided all 60 records a side with no split. `score_relay.py holdout`:
**no reserved case is worse under the edit.** Every case passed 10 of 10
on both sides.

### Disclosed, deciding nothing

- **The pre-mortem's likeliest class did not arrive.** Opus did not keep
  60 words a part, as it did not keep three sentences, but this bullet
  pressed where round 130's did not: 0.728 and 0.714 against round 130's
  1.001, at the same control.
- **`walkthrough`/opus shortened within its bound**, 328 to 286 and 372 to
  260 prose words, with 40 of 40 edit verdicts passing. The user fixed that
  scope at "the whole flow", and the edit answers still cover it; the bound
  this round buys cannot see a loss smaller than about five verdicts of 20.
- **`relay-retention` still relays 13 of its 20 planted identifiers** on
  both samples, and `relay-migration` 7; only `relay-rollout` fell to 0.
  Relaying is disclosed, not a bar.
- **The edit cells still run 1.1 to 1.3 times the 163-word reference.**
  #500 is narrower than it was and still open.
- **Cost.** $46.21 of generation across the 560 stage-2 and replication
  runs and $6.89 across the 120 holdout runs, and the panel's judging on
  top.

## Result: accepted

The primary passed twice, at factors 0.728 and 0.714 (p < 0.00001 both),
every bound held on both samples at 100%, the readability bound held at 60
of 60 on both, and the holdout held. `plugin/rules/laconic.md` ships the
edit; a release is owed.

[#500]: https://github.com/JordanMPDS/laconic/issues/500
