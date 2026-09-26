# Round 85: the one-word licence, scoped to a premise that holds

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 83 and 84, which are merged. This file, the edit
and the regenerated `rules/dist/*.md` are committed in one commit before any
generation, following [round 38](round-38.md) through [round 84](round-84.md).

`bash tools/candidate-due.sh` exits 1: round 84 measured, so this round has to
carry a candidate. It is the one [round 84](round-84.md) registered for its
reading B.

## Why this round exists

[#353]: on a follow-up turn that proposes a fix as a closed question with a
wrong premise, sonnet answers "No" plus the reason in one line and drops the
fix that works. [Round 83](round-83.md) added a sentence arguing against that
line and moved sonnet `quality_fails` on the four cases from 26 to 18 in 60,
p = 0.146; every failure it left was the same one line. [Round 84](round-84.md)
ruled out round 81's length paragraph as the cause: the rules before it fail
28 of 60 against master's 27 of 59, p = 0.611.

That leaves the closed-question specimen from rounds 71 and 73, and its
licence is unconditional: *"The one word is the whole answer, not the opening
of one."* The example above it is a true premise, but the sentence itself
does not say so, and a model answering "No" can read it as covering that word
too. This round narrows the licence instead of arguing against what it
produces.

## The edit

`rules/laconic.md`, the first sentence of the specimen's second paragraph,
inside `## Never cut` and above every level marker:

```diff
-The one word is the whole answer, not the opening of one. Everything after it
-is appended rather than part of it: no "Yes, that's correct" followed by their
-own sentence in your words, because the premise is what you are confirming.
+When the premise holds, the one word is the whole answer, not the opening of
+one. Everything after it is appended rather than part of it: no "Yes, that's
+correct" followed by their own sentence in your words, because the premise is
+what you are confirming.
```

Four words added, none removed. `rules_cksum` on the `full` slice goes
**288018845 to 1629894331**. No paired copy moves: the specimen appears only
in `rules/laconic.md` and its generated slices.

## The hypothesis

> Scoping the one-word licence to a premise that holds should move
> `quality_fails` on `recall-index`, `wide-index`, `deep-index` and
> `recall-metric`, on sonnet, **down**.

The scope, the scorer and the reps are round 83's, unchanged, so the two
edits are compared at equal power against controls generated the same way.

## The instrument

Two trees, control at `master` and edit at this branch, generating at the
same time, laconic arm only, `--turn-delivery plugin`, four shards at
`--concurrency 4`.

| snapshot | cells | reps | runs a side | graded by |
|---|---|--:|--:|---|
| dev | the four target cases on sonnet and opus; `conditional` on sonnet and opus; `confirm-index`, `confirm-metric`, `confirm-rollback` on sonnet | 15 | 195 | the panel, sonnet + opus + kimi |
| pilot | `settled-*` and `contra-*` on haiku; `unsettled-*` on haiku and sonnet | 20 | 240 | deterministic, `score_echo.py` |

870 generations and about 1,170 judge calls, 390 of them kimi's.

## The bars

One look each; no extension is registered.

1. **Primary.** `report.py --target quality_fails --target-cases
   recall-index,wide-index,deep-index,recall-metric --target-models sonnet`,
   edit against control, `--looks 1`, alpha 0.05. The target must fall and
   separate.
2. **Fatal: the four counters over the dev snapshot's cells**, as `report.py`
   gates them in the same call. This includes the four target cases on opus,
   where a correct "No" plus a fix must not become a worse answer.
3. **Fatal: the `contra-*` deny rate on haiku must not fall.** Imported from
   rounds 72 and 73 through `score_echo.py` unchanged. The edit makes the
   licence depend on whether the premise holds, and `contra-*` is where a
   model that stops checking the premise would confirm a false one.
4. **Fatal: `settled-*` prose words on haiku must not rise.** The same
   stratified permutation `score_echo.py` computes for a fall, run with the
   sides swapped so that it tests a rise, one-sided, alpha 0.05. Round 73's
   gain was the true-premise answer ending at "Yes"; an edit that weakens the
   licence where the premise does hold would undo it.

**Disclosed, deciding nothing:** `conditional` pass rates on both models (it is
`rule-adherence` and may not be optimized against, though round 83's control has it
failing 15 of 15 on sonnet); the `unsettled-*` twins' deny and correction
rates; median words on the target cases' graded turn, which the edit is
expected to raise; `panel_agreement.py` on both judgment files; and
`release.py` across all four shards.

**Accept** needs bar 1 to pass and bars 2 to 4 to hold. Then step 8's
replication and step 9's holdout. Anything else rejects and reverts every file
the edit touched.

## Power, stated before the numbers

Round 83's simulation holds unchanged: at 60 sonnet runs a side, one-sided
Fisher at alpha 0.05 has power 0.98 against a fall from 0.40 to 0.10, 0.72
from 0.40 to 0.20 and 0.83 from 0.30 to 0.10. Round 83's and round 84's
master controls read 26 of 60 and 27 of 59.

## Pre-mortem, registered

The likeliest failure is **the same one as round 83: moving the right way and
not separating.** A four-word condition is a smaller change than round 83's
sentence, and round 60 priced prose next to a demonstration well below the
demonstration itself. If the one-line "No" is a sonnet response template
rather than something this sentence licenses, neither edit reaches it, and
the next move is out of the rules text altogether. The second risk is **bar 4
in the other direction from round 83**: making the licence conditional could
weaken it for the true premise too, lengthening `settled-*`. Bar 4 is a rise
test, so it sees that. I expect the target to move further than round 83's
did, because this edit removes the licence where round 83 only argued
against it, and I expect it still not to separate at this size.

## Consultation

None. `tools/consult.sh` was not run for this round.

## Buying order

Round 83's: all four shards generate in one pass, the pilot snapshot is scored
first, and the dev snapshots are judged with `--judge-all` either way.

## One interleaved pass, four shards

```sh
git worktree add --detach /home/jordan/projects/laconic-r85-control master
git worktree add /home/jordan/projects/laconic-r85-edit round-85
OUT=/home/jordan/projects/laconic-r85-edit/evals/snapshots/loop
DEV='recall-index:sonnet,wide-index:sonnet,deep-index:sonnet,recall-metric:sonnet,recall-index:opus,wide-index:opus,deep-index:opus,recall-metric:opus,conditional:sonnet,conditional:opus,confirm-index:sonnet,confirm-metric:sonnet,confirm-rollback:sonnet'
PILOT='settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,contra-retention:haiku,contra-failover:haiku,contra-rounding:haiku,unsettled-retention:haiku,unsettled-failover:haiku,unsettled-rounding:haiku,unsettled-retention:sonnet,unsettled-failover:sonnet,unsettled-rounding:sonnet'

for side in control edit; do
  tree=/home/jordan/projects/laconic-r85-$side
  ( cd $tree && python3 evals/bench/run.py --arms laconic --cells "$DEV" --reps 15 \
      --turn-delivery plugin --concurrency 4 --snapshot $OUT/round-85-$side-dev.json ) &
  ( cd $tree && python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
      --cells "$PILOT" --reps 20 --rep-offset 220 --turn-delivery plugin \
      --concurrency 4 --snapshot $OUT/round-85-$side-pilot.json ) &
done
wait
```

`--rep-offset 220` starts above every rep rounds 72, 73 and 83 used on the
pilot cells.

Scoring:

```sh
python3 evals/pilot/score_echo.py --title 'Round 85: bar 3' \
  --control $OUT/round-85-control-pilot.json --edit $OUT/round-85-edit-pilot.json
python3 evals/pilot/score_echo.py --title 'Round 85: bar 4, sides swapped' \
  --control $OUT/round-85-edit-pilot.json --edit $OUT/round-85-control-pilot.json
for side in control edit; do
  python3 evals/bench/judge.py --judge-all --results $OUT/round-85-$side-dev.json \
    --out $OUT/round-85-$side-dev-judgments.json
done
python3 evals/bench/report.py \
  --results $OUT/round-85-edit-dev.json --judgments $OUT/round-85-edit-dev-judgments.json \
  --against $OUT/round-85-control-dev.json \
  --against-judgments $OUT/round-85-control-dev-judgments.json \
  --target quality_fails --target-cases recall-index,wide-index,deep-index,recall-metric \
  --target-models sonnet --looks 1
python3 evals/bench/release.py $OUT/round-85-{control,edit}-{dev,pilot}.json
```

## Results

<!-- Nothing above this line has been computed. -->

## Result: nothing moved, and the one cell that changed went the wrong way

**Reject. The edit reverts in full.** Bar 1 fails with the point estimate
against the registered direction. Bars 2 to 4 held.

870 runs, 0 failed, all four shards on CLI **2.1.282** per `release.py`, which
finds no release span. `rules_cksum` 288018845 on the control and 1629894331 on
the edit. The control worktree was added with `--detach` at `316da57`, as in
round 83.

**The panel ran in two sittings again.** Kimi hit its 5-hour quota during the
first pass. `judge.py` resumed at 19:40 UTC after the reset and re-asked the
14 control and 13 edit judgments that lacked a majority, so every judgment
below has one. The verdict was scored once, on the complete files.

| bar | control | edit | p | reading |
|---|--:|--:|--:|---|
| 1 primary, `quality_fails`, four cases, sonnet | 26 | 27 | 0.608 | **fails, wrong direction** |
| 2 the four fatal counters, dev cells | | | | held |
| 2 [#49] turn gate | | | | held, +0.0 turns over 5 cells |
| 3 `contra-*` deny, haiku | 60/60 | 59/60 | 0.50000 | held |
| 4 `settled-*` words rise, haiku | | | 0.80982 | held; the pooled edit median fell 3.83 words |

Per cell, sonnet, pass / fail:

| case | control | edit |
|---|--:|--:|
| `recall-index` | 0 / 15 | 0 / 15 |
| `wide-index` | 8 / 7 | 3 / 12 |
| `deep-index` | 11 / 4 | 15 / 0 |
| `recall-metric` | 15 / 0 | 15 / 0 |

`recall-index`, the cell [#353] was filed on, reads 15 of 15 failing on both
sides. The two cells that moved moved in opposite directions by about the
same amount.

### Disclosures

| | control | edit |
|---|--:|--:|
| `conditional`, sonnet, pass / fail / not exercised | 3 / 11 / 1 | 4 / 11 / 0 |
| `conditional`, opus, pass / fail | 2 / 13 | 3 / 12 |
| the four cases, opus, fails | 3 of 60 | 1 of 60 |
| `unsettled-*` pooled deny | 118/120 | 119/120 |
| median words, four target cases, sonnet | 23.5 | 28.0 |
| median words, four target cases, opus | 56.5 | 60.0 |

Panel agreement, pairwise:

| pair | control | edit |
|---|--:|--:|
| sonnet / opus | 162/195, kappa 0.554 | 163/195, kappa 0.536 |
| sonnet / kimi | 103/134, kappa 0.396 | 105/139, kappa 0.346 |
| opus / kimi | 124/134, kappa 0.834 | 131/139, kappa 0.867 |

## The verdict

**Reject, labelled `idea-defect`**: the registered primary moved against the
registered direction. The pre-mortem expected a move with the direction that
did not separate. What came back was no move at all.

Rounds 83, 84 and 85 together give [#353] a clean negative. The one-line "No"
on `recall-index`/sonnet does not come from round 81's length paragraph
(round 84, 27 of 59 against 28 of 60). Narrowing the specimen's licence does
not reach it (this round, 15 of 15 failing on both sides). Arguing against it
in the rules text reduced it without removing it (round 83, 26 to 18,
p = 0.146). The median sonnet answer on `recall-index` is 17 to 19 words
under all four rules texts tested and has the same shape each time. Baseline
sonnet, with no rules, passes the same case 5 of 5 in the 2026-09-24 benchmark,
so the rules do produce it, but not through any sentence these rounds edited.
The next step for [#353] is the delivery rather than the text: the rule slice
arrives on turn 1, and the graded follow-up turn adds only the one-line
per-turn reminder. A round that varies the reminder separates the two.

`rules/laconic.md` and `rules/dist/*.md` are restored to `master`.

[#353]: https://github.com/JordanMPDS/laconic/issues/353
