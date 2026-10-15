# Round 106: an either/or answer leaves the evidence out unless asked why (#384)

**Registration. Nothing below the results line has been computed**, except the
round 105 figures quoted from its merged document. This file, the edit and the
regenerated `rules/dist/*.md` are committed before any generation.

`bash tools/candidate-due.sh` exited 0 at registration (round 105 carried a
candidate), and `bash tools/release-due.sh` exited 0. This round carries a
rule edit, under **The edit** below, because the maintainer asked for round
105's named next candidate.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_choice.py --precheck $OUT/round-106-control.json
python3 evals/pilot/score_choice.py $OUT/round-106-{control,edit}.json \
    $OUT/round-106-{control,edit}-judgments.json
python3 evals/bench/release.py $OUT/round-106-{control,edit}.json
```

## Why this round exists

[Round 105](round-105.md) built an instrument for [#384], an either/or
question answered in its first 8 words and then 148 more, and found it fires
on opus at master rules on every run: 30 of 30 `choose-*` answers over 45
prose words, stem medians of 92 to 114. Its edit named the either/or shape
and moved the stem medians by −10.5 words, p = 0.0511, with every bound
holding, and was rejected on the noise floor.

The edit side still appended the record's mechanism and a caveat after naming
the option. Round 105 traced that to its own wording: *"the evidence for it is
appended rather than part of it"* says where the evidence goes, and the model
put it there. This round tests the candidate round 105 named, the same
paragraph with that clause saying the evidence is left out unless the user
asked why.

## The edit

One paragraph, appended after the confirmation example's closing paragraph,
in the section every level carries. It is round 105's paragraph with one
clause changed, which counts as one edit:

```diff
 The one word is the whole answer, not the opening of one. Everything after it
 is appended rather than part of it: no "Yes, that's correct" followed by their
 own sentence in your words, because the premise is what you are confirming.
+
+A question that names its options is closed the same way: *"Was the worker
+killed by its own memory limit, or by the node running out?"* — "Its own
+memory limit." Naming the option that holds is the whole answer, and the
+evidence for it is left out unless the user asked why. If neither holds, say
+so and name what does.
```

Round 105's clause was *"and the evidence for it is appended rather than part
of it"*. The exception names the never-cut item a "why" already triggers, so
the clause does not withhold an explanation the user asked for.

`rules_cksum` is stamped into each snapshot at generation.

**Hypothesis.** Editing the closed-question paragraph to leave the evidence
out unless the user asked why should move prose words on `choose-*`, opus,
down.

## The instrument

Round 105's, unchanged: the six pilot cases `choose-*` and `neither-*` over
the `deep-*` fixtures, `confirm-*` symlinked in from the scored suite, and
`evals/pilot/score_choice.py` with its seed of 105. Nothing under
`evals/pilot` or `evals/cases` changes in this round.

**No separate precheck.** Master rules are byte-identical to round 105's
precheck and control, both of which fired on every `choose-*` run. As a
validity check, this round's own control is scored with `--precheck`: if it
does not meet round 105's condition (10 of its 60 `choose-*` runs over 45
words, at least 3 in every stem), the defect has stopped firing, the round is
void, and nothing is decided.

## The comparison (300 generation calls)

Two trees generating simultaneously: control from a worktree at
`origin/master` 5744a1a, edit from this branch. Laconic, opus,
`--turn-delivery plugin`, 20 reps per case on the six pilot cases and 10 on
the three `confirm-*` cells: 150 runs a side, two shards a side.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
C='choose-index:opus,choose-metric:opus,choose-rollback:opus'
N='neither-index:opus,neither-metric:opus,neither-rollback:opus'
K='confirm-index:opus,confirm-metric:opus,confirm-rollback:opus'
for side in control edit; do for off in 0 10; do
  cells="$C,$N"; [ $off = 0 ] && cells="$cells,$K"
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$cells" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-106-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-106-$side-shard{0,10}.json --out $OUT/round-106-$side.json
python3 evals/bench/judge.py --results $OUT/round-106-$side.json --cases-dir evals/pilot \
    --out $OUT/round-106-$side-judgments.json
```

### The bars

Round 105's, at the same alphas:

1. **Primary: prose words on `choose-*` fall**, opus, by
   `score_settled.stratified`: the mean over the three stems of (edit median
   minus control median), side label permuted within each stem, one-sided,
   seed 105, alpha 0.05. A stem whose reading rate differs between the sides,
   or that holds a mutating run, does not vote.
2. **Bound, fatal: `neither-*` answers naming the record's actual cause may
   not fall**, pooled over the three stems, by `score_choice.MECHANISM`,
   one-sided Fisher, alpha 0.05.
3. **Falsifier, fatal: panel-judged pass rate may not fall** on `choose-*`,
   `neither-*` and `confirm-*`, each pooled per family, one-sided Fisher,
   alpha 0.05.
4. **Bound, fatal: `date_trunc`** kept on `confirm-index`.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`.

**Disclosed, deciding nothing:** per-stem medians; the share of `choose-*`
answers at 20 words or fewer; `neither-*` prose words; `panel_agreement.py`;
`release.py`.

**Replication, bought only if everything above passes:** a fresh 150 runs a
side from the same two trees, scored on bars 1 to 4 at the same alphas. Then
step 9's holdout: all six reserved cases, opus, 10 reps, both trees; no
reserved case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and bars 2 to 4 to hold, twice, and the
holdout. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/` before the merge.

## Pre-mortem, registered

The likeliest failure is **a fatal counter rejecting an edit whose target
passed**, on bar 3's `confirm-*`. "Left out unless the user asked why" is the
first clause in the file that tells the model to withhold something, and a
wrong-premise confirmation is where withholding costs most: its scored trap
wants the denial, the fixture's reason, and a working fix. A bare "No" there
is [#353]. The second likeliest is the primary moving with its direction and
not separating, if the evidence goes and round 105's caveats ("One gap: ...")
stay, since a caveat is not evidence for the option.

## What this round cannot establish

- **Opus only.** The edit ships to every model; sonnet and haiku have no runs
  on this instrument.
- **One turn.** [#384]'s third paragraph came from an earlier turn's topic,
  which a single-turn case cannot produce.

## Where the ideas came from

The clause is round 105's named next candidate, which the maintainer asked to
be run. The rest of the paragraph, the instrument and the bars are round
105's, including what `tools/consult.sh` contributed there. No consult was
run for this round.

[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#384]: https://github.com/JordanMPDS/laconic/issues/384

## Results

<!-- Nothing above this line has been computed. -->

### Validity: the defect still fires

Round 106's own control, scored with `--precheck`: 59 of 60 `choose-*` runs
over 45 prose words, every stem at 19 or 20 of 20, with stem medians of 112.0
(`index`), 105.0 (`metric`) and 104.0 (`rollback`). The round is not void.

### First sample

150 runs a side, 0 failed, every run on CLI 2.1.300, so `release.py` finds no
span. `rules_cksum` 3769556782 on every control run and 3105749900 on every edit
run; `cases_cksum` 1267223679 over the nine cells on both sides. Panel
judgments 150 a side.

| bar | control | edit | p | |
|---|--:|--:|--:|---|
| 1. prose words on `choose-*`, mean shift of stem medians | | −58.7 words | < 0.00001 (one-sided) | **passes** |
| 2. `neither-*` names the record's cause | 60/60 | 60/60 | 1.000 | holds |
| 3. panel quality, `choose-*` | 60/60 | 60/60 | 1.000 | holds |
| 3. panel quality, `neither-*` | 60/60 | 60/60 | 1.000 | holds |
| 3. panel quality, `confirm-*` | 24/30 | 24/30 | 0.626 | holds |
| 4. `date_trunc` on `confirm-index` | 10/10 | 10/10 | 1.000 | holds |

Per stem, `choose-*` medians: 112.0 to 62.0 (`index`), 105.0 to 53.5
(`metric`), 104.0 to 29.5 (`rollback`). `neither-*`: 78.0 to 58.5, 130.5 to
99.0, 63.5 to 53.0.

**Disclosed, deciding nothing.** 16 of the 60 edit `choose-*` answers are 20
words or fewer, against none of the control's; the shortest is 4 words on the
edit and 42 on the control. The one-line answers are the option alone ("The
time is going into the query itself."), and the longer ones still carry the
record's mechanism after it, with a caveat on `metric` (the sample-size
figure the fixture states). `confirm-*` reads medians of 117.5 and 111.5
words and keeps its denial's reason on both sides. Pairwise panel agreement is
kappa 0.66 to 0.91.

Everything passed, so the replication and the holdout are bought.

### Replication

A fresh 150 runs a side from the same two trees, 0 failed, every run on CLI
2.1.300, with the same `rules_cksum` pair. The pass was interrupted twice, by
a usage limit and by a low-memory stop, and resumed by key both times; no
completed key was regenerated.

| bar | control | edit | p | |
|---|--:|--:|--:|---|
| 1. prose words on `choose-*`, mean shift of stem medians | | −65.2 words | < 0.00001 (one-sided) | **passes** |
| 2. `neither-*` names the record's cause | 60/60 | 60/60 | 1.000 | holds |
| 3. panel quality, `choose-*` | 60/60 | 60/60 | 1.000 | holds |
| 3. panel quality, `neither-*` | 60/60 | 60/60 | 1.000 | holds |
| 3. panel quality, `confirm-*` | 22/30 | 24/30 | 0.820 | holds |
| 4. `date_trunc` on `confirm-index` | 10/10 | 10/10 | 1.000 | holds |

Per stem, `choose-*` medians: 106.0 to 66.0 (`index`), 98.5 to 22.5
(`metric`), 114.5 to 35.0 (`rollback`). `neither-*`: 78.0 to 57.0, 136.0 to
97.5, 70.5 to 53.0. kimi returned a vote on only 62 control and 63 edit
verdicts, so sonnet and opus decided the rest together; they agree on 148 of
150 on each side.

### Holdout

All six reserved cases, opus, 10 reps from both trees, 0 failed, CLI 2.1.300:
every verdict passed on both sides, so no reserved case is worse under the
edit. Directions only, as step 9 requires.

## Result: accepted

**Accept.** Bar 1 passed and bars 2 to 4 held on both samples, and the holdout
held. The edit stays in `rules/laconic.md` and `rules/dist/`, at `rules_cksum`
3105749900. `README.md` now paraphrases it.

One clause separates this round from round 105's rejection. Saying where the
evidence goes moved the stem medians by 10.5 words; saying it is left out
moved them by 58.7 and then 65.2, from about 105 words to between 22 and 66.
The edit side does not reach the one-line answer on most runs: 16 of 60 are 20
words or fewer, and the rest still carry the record's mechanism, which is
[#384]'s first paragraph of proof shortened rather than removed.

The pre-mortem was wrong. `confirm-*`, where withholding should have cost most,
read 24/30 against 24/30 and then 24/30 against 22/30, and its answers kept
the denial's reason. [#384] stays open for its earlier-turn topic, which a
single-turn case cannot produce.
