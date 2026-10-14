# Round 105: an either/or question is answered by naming one option (#384)

**Registration. Nothing below the results line has been computed**, except the
opus figures quoted from rounds 91 and 92, which are merged. This file, the
six pilot cases, `evals/pilot/score_choice.py` and the layout test are
committed before any generation. The edit and the regenerated
`rules/dist/*.md` are committed only if stage 1 fires, and before stage 2
generates.

`bash tools/candidate-due.sh` exited 0 at registration (round 104 carried a
candidate), and `bash tools/release-due.sh` exited 0. This round carries a
rule edit anyway, under **The edit** below, because the maintainer asked for
the next rule item in the backlog.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_choice.py --precheck $OUT/round-105-precheck.json
python3 evals/pilot/score_choice.py $OUT/round-105-{control,edit}.json \
    $OUT/round-105-{control,edit}-judgments.json
python3 evals/bench/release.py $OUT/round-105-{control,edit}.json
```

## Why this round exists

[#384] was filed on 2026-10-06 from an Opus 5.5 session at level `full`. The
user asked an either/or question that named both options, and got 156 words in
four paragraphs. The first sentence, 8 words, was the whole answer. The rest
was proof that the answer was right (46%), a likely cause inside the chosen
stage with a caveat on it (24%), and a topic from an earlier turn (24%). The
user's verdict: *"Your first sentence answered my question, the rest of it was
unnecessary explanation i did not ask for."*

The rules' only worked closed question is a confirmation ("..., correct?"
answered "Yes."), and on opus it works: `settled-failover` reads a median of
**1 word** at master rules in rounds 91 and 92. Nothing in the rules names the
either/or shape, and no case in this repository asks it. So this round builds
the instrument and tests the issue's first suggested direction. Its other two
directions, scoping check 3 to the current question and scoping the
uncertainty item to the answer, are separate edits and are not taken here.

## The edit

One paragraph, appended after the confirmation example's closing paragraph,
in the section every level carries:

```diff
 The one word is the whole answer, not the opening of one. Everything after it
 is appended rather than part of it: no "Yes, that's correct" followed by their
 own sentence in your words, because the premise is what you are confirming.
+
+A question that names its options is closed the same way: *"Was the worker
+killed by its own memory limit, or by the node running out?"* — "Its own
+memory limit." Naming the option that holds is the whole answer, and the
+evidence for it is appended rather than part of it. If neither holds, say so
+and name what does.
```

The example stays inside the scenario the file already uses, so it teaches
the shape and not a new domain, and its answer is a verbatim slice of the
option it names, so the example and the sentence after it agree on what
compliance looks like. The last sentence is there for [#353]'s
failure in this shape: a closed question whose premise is wrong answered with
a bare denial and no working answer.

`rules_cksum` is stamped into each snapshot at generation.

## The instrument

Six single-turn pilot cases over the three `deep-*` fixtures, by symlink, each
ending `Don't edit anything.`:

| case | options named | the record says |
|---|---|---|
| `choose-index` | the query itself, or queueing behind the 30-second poll | the query; the poll is under "Not the cause" |
| `choose-metric` | unbalanced arms, or only four control purchases | the four purchases; assignment "looks clean" |
| `choose-rollback` | after the revert, the mode assertion or the NOT NULL column | the NOT NULL column |
| `neither-index` | a saturated pool, or a bloated table | neither; a sequential scan from the `date_trunc` predicate |
| `neither-metric` | ad-blocker losses, or the logged-out exclusion | neither; too few purchases |
| `neither-rollback` | an overloaded database, or the payment provider | neither; migration 0042's NOT NULL column |

`choose-*` has a one-option answer by construction, which is what [#384]
describes. `neither-*` is its falsifier: the same question shape where naming
one option is wrong and a complete answer has to say what does hold.
`confirm-{index,metric,rollback}` are symlinked in from the scored suite as a
second falsifier: wrong-premise confirmations, the shape [#353]'s bare "No"
was seen on, and the likeliest place for the edit's last sentence to spill.

## Stage 1: does #384 fire on opus? (60 calls)

Master rules, the laconic arm, opus, 10 reps per case, `--turn-delivery
plugin`, four shards:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
C='choose-index:opus,choose-metric:opus,choose-rollback:opus'
N='neither-index:opus,neither-metric:opus,neither-rollback:opus'
for cells in "$C" "$N"; do for off in 0 5; do
  python3 evals/bench/run.py --arms laconic --reps 5 --rep-offset $off \
    --cases-dir evals/pilot --cells "$cells" --turn-delivery plugin \
    --concurrency 4 --snapshot $OUT/round-105-precheck-${cells%%-*}-$off.json &
done; done
wait
python3 evals/bench/merge.py $OUT/round-105-precheck-*-{0,5}.json --out $OUT/round-105-precheck.json
python3 evals/pilot/score_choice.py --precheck $OUT/round-105-precheck.json
```

**Registered pass condition: at least 10 of the 30 `choose-*` runs exceed 45
prose words, and at least 3 of the 10 in every stem do.** The rules give a
closed question "a word or a line", and [#384]'s answer was 8 words before the
proof began; 45 words is that answer with two or three sentences of evidence
attached. The per-stem floor keeps one fixture from buying a round whose
primary is stratified by stem. `neither-*` is generated beside it and
disclosed, deciding nothing; so are the per-stem medians the primary will
start from.

**If it does not fire**, the edit is not committed, stage 2 is not generated,
this document records the precheck, and the round is recorded as measuring.

## Stage 2: the edit on opus, only if stage 1 fires (300 generation calls)

Two trees generating simultaneously: control from a worktree at this branch's
registration commit (master rules), edit from this branch with the edit
committed. Laconic, opus, `--turn-delivery plugin`, 20 reps per case on the
six new cases and 10 on the three `confirm-*` cells: 150 runs a side, two
shards a side.

```sh
K='confirm-index:opus,confirm-metric:opus,confirm-rollback:opus'
for side in control edit; do for off in 0 10; do
  cells="$C,$N"; [ $off = 0 ] && cells="$cells,$K"
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$cells" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-105-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-105-$side-shard{0,10}.json --out $OUT/round-105-$side.json
python3 evals/bench/judge.py --results $OUT/round-105-$side.json --out $OUT/round-105-$side-judgments.json
```

### The bars

1. **Primary: prose words on `choose-*` fall**, opus, by
   `score_settled.stratified`: the mean over the three stems of (edit median
   minus control median), side label permuted within each stem, one-sided,
   seed 105, alpha 0.05. A stem whose reading rate differs between the sides,
   or that holds a mutating run, does not vote.
2. **Bound, fatal: `neither-*` answers naming the record's actual cause may
   not fall**, pooled over the three stems, by `score_choice.MECHANISM` (the
   sequential scan or `date_trunc`; the four purchases or the sample size;
   the NOT NULL column or migration 0042), one-sided Fisher, alpha 0.05.
3. **Falsifier, fatal: panel-judged pass rate may not fall** on `choose-*`,
   `neither-*` and `confirm-*`, each pooled per family, one-sided Fisher,
   alpha 0.05. `choose-*` passes on naming the right option; `neither-*` on
   rejecting both and naming the cause, so an answer that satisfies bar 2's
   pattern while equivocating between the two options fails here;
   `confirm-*` on its scored trap, a denial with the fixture's reason and a
   working fix.
4. **Bound, fatal: `date_trunc`** kept on `confirm-index`.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`.

**Disclosed, deciding nothing:** per-stem medians and two-sided permutations;
`neither-*` prose words, edit against control (a fall there is not a harm if
bar 2 and bar 3 hold); `panel_agreement.py`; `release.py`.

**Replication, bought only if everything above passes:** a fresh 150 runs a
side from the same two trees, scored on bars 1 to 4 at the same alphas. Then
step 9's holdout: all reserved cases, opus, 10 reps, both trees; no reserved
case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and bars 2 to 4 to hold, twice, and the
holdout. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/` before the merge.

## Pre-mortem, registered

The likeliest outcome is that **stage 1 does not fire**. The fixtures put the
wrong option on an explicit ruled-out list, so the answer is a lookup rather
than [#384]'s inference, and opus may answer a lookup in a line. If it fires,
the likeliest failure is **bar 2**: "naming the option that holds is the whole
answer" read as licence for "Neither." with nothing after it, which is
[#353]'s bare "No" in this shape and the reason the edit's last sentence
exists.

## What this round cannot establish

- **Opus only.** The edit ships to every model; sonnet and haiku have no runs
  on this instrument.
- **One turn.** [#384]'s third paragraph came from an earlier turn's topic, and
  a single-turn case cannot produce that. Scoping check 3 to the current
  question is the issue's second direction and needs a multi-turn family.

## Where the ideas came from

The edit is [#384]'s first suggested direction. Through `tools/consult.sh`,
Codex supplied the per-stem floor in the stage-1 condition; Kimi supplied the
lower word bar, the `confirm-*` falsifier, and the rewording that makes the
example's answer a verbatim slice of its option. Codex's suggestion to move
the example to a pipeline, close to the field report's own question, was not
taken: an example copied from the report is fitted to the report. DeepSeek did
not answer within the timeout.

[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#384]: https://github.com/JordanMPDS/laconic/issues/384

## Results

<!-- Nothing above this line has been computed. -->

### Stage 1: it fires

60 runs, 0 failed, at master rules, `cases_cksum` 3884565116 over the six
cases.

| case | n | median prose words | over 45 words | read the fixture |
|---|--:|--:|--:|--:|
| `choose-index` | 10 | 101.0 | 10 | 10 |
| `choose-metric` | 10 | 92.0 | 10 | 10 |
| `choose-rollback` | 10 | 114.0 | 10 | 10 |

**30 of 30 over 45 words, every stem at 10 of 10: the condition is met and
stage 2 is bought.** The edit and the regenerated `rules/dist/*.md` were
committed after this table and before stage 2 generated.

Disclosed: `neither-*` reads medians of 83.0 (`index`), 141.0 (`metric`) and
68.0 (`rollback`), and every one of the 30 names the record's cause.
