# Round 89: round 68's scoped explain bullet, decided on opus (#298)

**Registration. Nothing below the results line has been computed**, except
round 68's figures, which are merged. This file, the edit and the regenerated
`rules/dist/*.md` are committed in one commit before any generation.

`bash tools/candidate-due.sh` exits 1: [round 88](round-88.md) was the one
measuring round the cap allows, so round 89 has to carry a rule edit. It does,
under **The edit** below.

## Why this round exists

[#298] was reported from a Claude Code session on **Opus 5**. [Round 68](round-68.md)
tested a scoped version of the never-cut explain bullet against it, **on sonnet
only**, and was rejected on a null that its own descriptive check explained: on
sonnet at master rules the already-told question is answered at **0.415** of the
cold one's length, so there was nothing for the edit to remove. That rejection
bounds the wording on sonnet. It says nothing about the model the report came
from, and the instrument has never been run on opus.

This round changes two things about how the loop takes an issue, and it is the
first round to do either:

1. **The deciding model is the model the issue was observed on.** #298 was seen
   on opus, so opus carries the primary and every fatal bound. Sonnet decides
   nothing here; round 68 already measured it.
2. **The defect has to fire on that model before the edit is tested.** Stage 1
   below is a cheap fire-rate check at master rules, with its pass condition
   registered here. If it does not pass, stage 2 is never generated.

## The edit

Round 68's sentence, byte for byte, appended to the bullet that grants the
cover:

```diff
 - Anything the user asked to have explained: "why", "how", "walk me through",
-  "explain".
+  "explain". Explain what is new; where the answer needs something you have
+  already said this session, point back to it rather than saying it again.
```

It is the same text because round 68 never tested it on a model where the harm
exists, so reusing it is the one choice that makes the two rounds readable
together. Round 68's argument for this wording over #298's own proposal
(positive framing, no precedence claim, a back-reference keeps the claim
findable) is unchanged.

`rules_cksum` is stamped into each snapshot at generation.

## Stage 1: does #298 fire on opus? (180 calls, 90 of them opus)

Master rules, the laconic arm, `evals/pilot/{explain,reexplain}-*`, 10 reps,
`--turn-delivery plugin`, one shard running sonnet then opus. Words only; no
judge is bought.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
cd /home/jordan/projects/laconic   # master rules
for m in sonnet opus; do
  python3 evals/bench/run.py --arms laconic --models $m --reps 10 \
    --cases 'explain-index,explain-metric,explain-rollback,reexplain-index,reexplain-metric,reexplain-rollback' \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 1 \
    --snapshot $OUT/round-89-precheck-$m.json
done
python3 evals/pilot/score_reexplain.py $OUT/round-89-precheck-{sonnet,opus}.json 89
```

With sonnet in the scorer's "control" slot and opus in its "edit" slot, its
interaction is the model-by-family contrast: how much longer opus's warm answer
is relative to its cold one than sonnet's is. The scorer's same-`rules_cksum`
warning is expected here and ignored.

**Registered pass condition.** The log ratio of ratios is **above 1** (opus's
warm/cold ratio exceeds sonnet's) and the aligned-residual interaction
(`interaction_corrected`) reads **p < 0.05**. Opus's own warm/cold ratio is
printed beside it.

At 10 reps a group the scorer's power table detects a ratio of ratios of about
1.85 at 80%, which from sonnet's 0.415 is an opus warm/cold ratio near 0.77.
**A precheck that does not fire is not evidence the harm is absent on opus**,
only that it is smaller than that; it is read as "not worth a 540-call opus
round", which is what the check is for.

**If it does not fire**, stage 2 is not generated, the edit is reverted
unrun, this document records the precheck, and the candidate allowance stays
unspent: round 89 is re-registered on the next candidate, which is
[round 88](round-88.md)'s #353 follow-up.

## Stage 2: the edit on opus, only if stage 1 fires (about 840 opus calls)

Round 68's instrument and endpoints, with opus in place of sonnet and one bound
added. Two trees generating simultaneously, per [round 38](round-38.md):
control from `/home/jordan/projects/laconic` at master rules, edit from
`/home/jordan/projects/laconic-r89`.

```sh
for side in control edit; do
  case $side in control) tree=/home/jordan/projects/laconic ;;
                edit) tree=/home/jordan/projects/laconic-r89 ;; esac
  ( cd $tree &&
    python3 evals/bench/run.py --arms laconic --models opus --reps 30 \
      --cases 'explain-index,explain-metric,explain-rollback,reexplain-index,reexplain-metric,reexplain-rollback' \
      --cases-dir evals/pilot --turn-delivery plugin --concurrency 2 \
      --snapshot $OUT/round-89-$side-opus.json &&
    python3 evals/bench/run.py --arms laconic --models opus --reps 10 \
      --cases 'deep-index,deep-metric,deep-rollback' \
      --cases-dir evals/pilot --turn-delivery plugin --concurrency 2 \
      --snapshot $OUT/round-89-$side-deep-opus.json ) &
done
wait
python3 evals/pilot/score_reexplain.py $OUT/round-89-{control,edit}-opus.json 89
python3 evals/pilot/score_claims.py $OUT/round-89-{control,edit}-deep-opus.json
python3 evals/bench/release.py $OUT/round-89-{control,edit}-opus.json
```

`explain-*`/`reexplain-*`: 180 runs and 270 calls a side. `deep-*`: 30 runs and
150 calls a side. Two shards, inside [#255]'s ceiling.

### The bars

1. **Primary, opus.** Round 68's: prose words on the graded turn, laconic, as a
   log-scale difference of differences
   `(reexplain_edit − reexplain_control) − (explain_edit − explain_control)`,
   aligned-residual permutation (`interaction_corrected`, which superseded the
   label permutation round 68 registered), seed 89, two-sided, alpha 0.05.
   Registered direction: negative.
2. **Falsifier, fatal.** Judged quality on the `reexplain-*` graded turn, by the
   panel: the edit side's pass rate may not fall below the control's,
   one-sided Fisher, alpha 0.05. Bought only if bar 1 passes.
3. **Bound, fatal: `deep-*` fixture-token coverage over turns 2 to 4 must not
   fall on opus**, one-sided, alpha 0.05, by `score_claims.py`. This is the
   bound [round 80](round-80.md) died on when it deleted this bullet, and a
   sentence telling the model to point back at what it already said is the
   likeliest thing in this edit to cost later turns their facts.
4. **Bound, fatal: `date_trunc`** kept on the `index` stem's graded turn, both
   families.

Disclosed, deciding nothing: per-stem cells (three cannot reach alpha),
the precheck's figures, `panel_agreement.py`, `release.py`.

**Accept** needs bar 1 to pass and bars 2 to 4 to hold, then step 8's
replication at the same size and bars, and the holdout. Anything else rejects
and reverts `rules/laconic.md` and `rules/dist/`. Round 68's four-branch
decision rule applies unchanged.

## Pre-mortem, registered

The likeliest outcome is that **stage 1 does not fire**. Round 80 found opus
two to three times longer than sonnet, but on both families at once, and a
model that is longer everywhere has the same warm/cold ratio. If it does fire,
the likeliest failure is **bar 3**: round 80 showed opus reading this bullet as
the thing that protects later-turn facts, and "point back rather than saying it
again" is an instruction to drop facts from a later turn. That would be a fatal
bound rejecting an edit whose target passed.

## What this round cannot establish

- **It does not measure restatement.** As in round 68, the endpoint is words
  on the graded turn, and the cold family is the only thing separating a
  scoped effect from general brevity.
- **Opus only.** The edit ships to every model. Sonnet is covered by round 68's
  null, which found nothing to remove rather than harm, and haiku has no runs
  on this instrument.

[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#298]: https://github.com/JordanMPDS/laconic/issues/298

## Results

<!-- Nothing above this line has been computed. -->
