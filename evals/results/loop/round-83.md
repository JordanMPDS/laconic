# Round 83: a wrong premise gets what is true instead, not a bare "No"

**Registration. Nothing below the results line has been computed**, except the
benchmark figures marked as such, which come from the committed
`benchmark-2026-09-24` snapshot and are why this round exists. This file, the
edit and the regenerated `rules/dist/*.md` are committed in one commit before
any generation, following [round 38](round-38.md) through
[round 82](round-82.md).

`bash tools/candidate-due.sh` exits 1: round 82 measured, so this round has to
carry a candidate, and it does.

## Why this round exists

[#353]. The [2026-09-24 benchmark](../../../docs/benchmark.md) put laconic
behind baseline on sonnet quality, 80.6% against 90.3% (z = -2.34), and the
largest block of that gap has one shape. The user proposes a fix as a closed
question, the premise is wrong, and laconic answers "No" with the reason and
stops. It never says what works instead. Computed from the committed
snapshot, laconic arm against baseline, sonnet, five reps each:

| case | baseline pass | laconic pass | what the failures drop |
|---|--:|--:|---|
| `recall-index` | 5/5 | 1/5 | both working fixes the fixture supplies |
| `wide-index` | 5/5 | 3/5 | the same |
| `deep-index` | 5/5 | 4/5 | the same |
| `recall-metric` | 5/5 | 4/5 | that the proposed replacement metric does not fix the readout either |

That is 8 failures in 20 runs against 0 in 20. The single-turn
`confirm-index` asks the same question as the first turn and passes 5/5 on
every model, so the failure is in the follow-up turn, where the fix was
already discussed and the rules read as licensing a bare denial.

The rules file says what a closed question with a *true* premise gets, the
specimen [round 71](round-71.md) and [round 73](round-73.md) wrote:
*"The one word is the whole answer, not the opening of one."* It says nothing
about a false one. Check 1 adds the other push: *"Diagnosing it is the answer;
fixing it is not … leave the fix for the user to ask for."* A user who asks
"so the fix is X, correct?" has asked about the fix, but the question's shape
is a confirmation.

## The edit

`rules/laconic.md`, one paragraph appended to the closed-question specimen,
inside `## Never cut` and above every level marker, so it reaches `lite`,
`full` and `ultra`:

```diff
 The one word is the whole answer, not the opening of one. Everything after it
 is appended rather than part of it: no "Yes, that's correct" followed by their
 own sentence in your words, because the premise is what you are confirming.
+
+When the premise is wrong, "No" is the opening, not the answer. The answer is
+what is true instead: why the premise fails and, when the question proposed a
+fix, the fix that works.
```

`rules_cksum` on the `full` slice goes **288018845 to 1309967557**. It sits
beside the specimen it qualifies, since [round 10](round-10.md) showed that
where a rule lives outranks what it says about where it lives. No paired copy
moves: the specimen appears only in `rules/laconic.md` and its generated
slices.

## The hypothesis

> Appending the wrong-premise paragraph to the closed-question specimen should
> move `quality_fails` on `recall-index`, `wide-index`, `deep-index` and
> `recall-metric`, on sonnet, **down**.

The scope is named here, before any generation, and passed to `report.py` as
`--target-cases` and `--target-models sonnet`. The registered baseline is this
round's own control side, not the benchmark.

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
   rounds 72 and 73 through `score_echo.py` unchanged. The edit talks about
   wrong premises, and `contra-*` is where a model that stops checking the
   premise would confirm a false one.
4. **Fatal: `settled-*` prose words on haiku must not rise.** The same
   stratified permutation `score_echo.py` computes for a fall, run with the
   sides swapped so that it tests a rise, one-sided, alpha 0.05. Round 73's
   gain was the true-premise answer ending at "Yes"; an edit about "No" that
   leaks into "Yes" would undo it.

**Disclosed, deciding nothing:** `conditional` pass rates on both models (it is
`rule-adherence` and may not be optimized against, though the benchmark has it
failing 5/5 on sonnet and opus); the `unsettled-*` twins' deny and correction
rates; median words on the target cases' graded turn, which the edit is
expected to raise; `panel_agreement.py` on both judgment files; and
`release.py` across all four shards.

**Accept** needs bar 1 to pass and bars 2 to 4 to hold. Then step 8's
replication and step 9's holdout. Anything else rejects and reverts every file
the edit touched.

## Power, stated before the numbers

Simulated, 2,000 draws per point, seed 83, one-sided Fisher on 60 sonnet runs
a side (four cells at 15 reps):

| control fail rate | edit fail rate | power |
|--:|--:|--:|
| 0.40 | 0.10 | 0.98 |
| 0.40 | 0.20 | 0.72 |
| 0.30 | 0.10 | 0.83 |

The benchmark read the control at 8 of 20, 0.40. The round is powered for an
edit that removes most of the failure, and has 0.72 power for one that
halves it.

## Pre-mortem, registered

The likeliest failure is **the target moving the right way and not
separating**, because the control reads lower than the benchmark's 8 of 20.
That was one five-rep draw per cell, and rounds 70 to 73 read the same three
index cells at 12 to 15 of 15 passing under the single-sonnet judge. If the
control comes back near 3 of 60, there is nothing to move, and the round can
only show the edit does no harm. The second failure is **bar 4**: "No" and
"Yes" sit in adjacent paragraphs, and a model that reads the new paragraph as
permission to append would lengthen the true-premise answer too. I expect the
target to pass and bar 4 to hold, because the edit names a condition the
`settled-*` prompts do not meet.

## Consultation

None. `tools/consult.sh` was not run for this round.

## Buying order, stopping at the first failure

All four shards generate in one pass, because the two trees must run at the
same time. The pilot snapshot is scored first, since it needs no judge. The
dev snapshots are then judged and scored. If bars 3 or 4 have already
rejected, the dev snapshots are still judged, because the primary is what
[#353] needs to know.

## One interleaved pass, four shards

```sh
git worktree add /home/jordan/projects/laconic-r83-control master
git worktree add /home/jordan/projects/laconic-r83-edit round-83
OUT=/home/jordan/projects/laconic-r83-edit/evals/snapshots/loop
DEV='recall-index:sonnet,wide-index:sonnet,deep-index:sonnet,recall-metric:sonnet,recall-index:opus,wide-index:opus,deep-index:opus,recall-metric:opus,conditional:sonnet,conditional:opus,confirm-index:sonnet,confirm-metric:sonnet,confirm-rollback:sonnet'
PILOT='settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,contra-retention:haiku,contra-failover:haiku,contra-rounding:haiku,unsettled-retention:haiku,unsettled-failover:haiku,unsettled-rounding:haiku,unsettled-retention:sonnet,unsettled-failover:sonnet,unsettled-rounding:sonnet'

for side in control edit; do
  tree=/home/jordan/projects/laconic-r83-$side
  ( cd $tree && python3 evals/bench/run.py --arms laconic --cells "$DEV" --reps 15 \
      --turn-delivery plugin --concurrency 4 --snapshot $OUT/round-83-$side-dev.json ) &
  ( cd $tree && python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
      --cells "$PILOT" --reps 20 --rep-offset 200 --turn-delivery plugin \
      --concurrency 4 --snapshot $OUT/round-83-$side-pilot.json ) &
done
wait
```

`--rep-offset 200` starts above every rep rounds 72 and 73 used on the pilot
cells.

Scoring:

```sh
python3 evals/pilot/score_echo.py --title 'Round 83: bar 3' \
  --control $OUT/round-83-control-pilot.json --edit $OUT/round-83-edit-pilot.json
python3 evals/pilot/score_echo.py --title 'Round 83: bar 4, sides swapped' \
  --control $OUT/round-83-edit-pilot.json --edit $OUT/round-83-control-pilot.json
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-83-$side-dev.json \
    --out $OUT/round-83-$side-dev-judgments.json
done
python3 evals/bench/report.py \
  --results $OUT/round-83-edit-dev.json --judgments $OUT/round-83-edit-dev-judgments.json \
  --against $OUT/round-83-control-dev.json \
  --against-judgments $OUT/round-83-control-dev-judgments.json \
  --target quality_fails --target-cases recall-index,wide-index,deep-index,recall-metric \
  --target-models sonnet --looks 1
python3 evals/bench/release.py $OUT/round-83-{control,edit}-{dev,pilot}.json
```

## Results

<!-- Nothing above this line has been computed. -->

[#353]: https://github.com/JordanMPDS/laconic/issues/353
