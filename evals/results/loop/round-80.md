# Round 80: the explanation licence deleted, measured where the reports came from

**Registration. Nothing below the results line has been computed**, except
round 70's figures, which are merged. This file, the edit, the regenerated
`rules/dist/*.md`, the paired copies and the two scorer changes are committed
in one commit before any generation, following [round 38](round-38.md) through
[round 78](round-78.md).

`bash tools/candidate-due.sh` exits 0, and this round carries a candidate
anyway.

## Why this round exists

[#150], [#298] and [#305] are three field reports of the same thing: an
answer to a request for an explanation or a status that ran four to five times
the length the model itself later called correct. In two of them the model
defended the length by citing `rules/laconic.md` — *"laconic exempts what you
asked to have explained"* in #150. Two passages carry that reading:

- the never-cut bullet *"Anything the user asked to have explained: 'why',
  'how', 'walk me through', 'explain'"*, and
- the length paragraph's *"gets full detail … it never truncates requested
  content"*.

The bullet protects nothing that check 2 does not already protect. An answer
to "why" that leaves out the why is not "the smallest set of claims that fully
answers this". So the bullet's only independent effect is the licence
reading, and the paragraph states the same licence more strongly.

**The harness has never reproduced the harm, and this round changes where it
looks.** [Round 68](round-68.md) found a repeated explanation at master rules
answered in less than half the words of a cold one. [Round 70](round-70.md)
moved the licence sentence into check 2, passed at 0.903 (p = 0.0247), and
failed its replication at 0.946 (p = 0.0721). Both ran sonnet. All three field
reports ran Opus 5. So opus is the primary here, under `--allow-opus`, with the
reason recorded in the snapshot.

## The edit

`rules/laconic.md`, the length paragraph and the never-cut list, above every
level marker:

```diff
 **Length scales to the request, at every level.** A yes/no question gets a word
 or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets full detail. Laconic governs volunteered content; it never truncates
-requested content.
+gets the scope it needs, and no claim in it twice. Laconic governs volunteered
+content.
 
 ## Never cut (every level, including ultra)
 
@@
   it. Telling the user to go check for themselves is not a confirmation.
-- Anything the user asked to have explained: "why", "how", "walk me through",
-  "explain".
 - Ordered instructions: every step, and the words that fix their order
```

The slices lose 11 words each: `full` goes from 1,157 to 1,146.

**Paired copies, changed in the same commit.** `skills/laconic/SKILL.md`
carries its own copy of the licence under "The one rule that overrides
terseness" and ships with the plugin, so it gets the same wording. The help
card and `README.md` drop the explain item from their never-cut summaries, and
`tests/test_rules.sh` stops requiring it. None of these reach the harness,
which delivers `rules/laconic.md` through the hook; they are changed so that a
revert or a ship moves them all at once.

## The instrument

Round 70's, unchanged: `evals/pilot/register-*` and `deep-*`, five turns,
`--turn-delivery plugin`, the laconic arm, both sides generated at the same
time from two trees. Turns 2 to 4 of `register-*` ask in as many words for the
full form (a complete checklist, the whole argument step by step, a table with
the evidence per row), so they are where the licence is invoked. `deep-*` asks
the same questions without asking for the full form.

| cell | model | reps per stem per side | runs | calls |
|---|---|--:|--:|--:|
| primary | opus | 10 | 120 | 600 |
| secondary | sonnet | 20 | 240 | 1,200 |
| bound | `walkthrough`, `code-fidelity` on haiku and sonnet | 20 per cell | 160 | 160 + 160 judged |

About 2,120 calls, 600 of them opus. The opus justification recorded in
`metadata.opus_justification` is: *every field report behind #150, #298 and
#305 was Opus 5, and the harness has never reproduced the harm on sonnet*.

## The bars

Scored with `evals/pilot/score_claims.py` per model, and
`evals/pilot/score_explain_bound.py` for the dev-set bound. One look each; no
extension is registered, so a decision to extend would be a new round.

1. **Primary, opus.** Prose words over turns 2 to 4 of `register-*`, laconic,
   down. Stem-stratified mean of the shift in each stem's median log words,
   permuted within stem, 50,000 resamples, two-sided, seed 70, alpha 0.05.
2. **Secondary, sonnet, directional only.** The same statistic must have a
   point estimate at or below 1.00. It is not tested for significance, because
   round 70 already measured this cell and it is not where the reports came
   from.
3. **Bound, fatal, both models: fixture-token coverage over turns 2 to 4 of
   `register-*` must not fall**, one-sided, alpha 0.05. Fewer words bought by
   saying less would otherwise score as a win.
4. **Bound, fatal, both models: fixture-token coverage over turns 2 to 4 of
   `deep-*` must not fall**, one-sided, alpha 0.05. New in this round, from the
   consultation. Round 70's replication was read as a failure partly because
   `deep-*` fell too. This edit plausibly shortens every answer, not only the
   licensed ones, and that is acceptable if nothing is lost. So `deep-*` words
   are disclosed, not a bar, and its coverage is the bar.
5. **Bound, fatal: requested explanations still survive.** `walkthrough` and
   `code-fidelity` are the dev-set cases whose criteria cite the deleted
   bullet. The judged safety verdict and the substring never-cut count must
   not fall, one-sided Fisher per case and pooled, alpha 0.05, uncorrected.
6. **Bound, fatal: `date_trunc` on the graded turn of `index`**, carried from
   round 70.

**Dropped from round 70: the licence ratio floor** (register over deep words
at 5.0x or more). It measured that the licence still fires, and this edit
removes the licence deliberately. Round 70 already warned that another edit of
this size would break the floor. It is printed as a disclosure.

**Accept** needs bar 1 to pass, bar 2 to hold, and bars 3 to 6 to hold. Then
step 8's replication (a fresh opus generation at the same size, same bars) and
the holdout. Anything else rejects and reverts every file the edit touched.

## Power, stated before the numbers

Round 70's scorer documents 0.90 power at ten runs per stem against #150's
17.2% harm on sonnet, which is what sets opus at 10 per stem. Opus's own
variance is unmeasured in this instrument, so that figure is borrowed. If opus
varies more than sonnet between stems, power is lower than stated.

## Consultation

`tools/consult.sh` on the design above. `kimi` answered; `codex` and
`deepseek` did not answer within the timeout. From kimi:

- **Adopted:** bar 4, reading `deep-*` falling as acceptable when its coverage
  holds, instead of as a failure of specificity.
- **Adopted:** opus as the single primary rather than co-primary with sonnet.
- **Not adopted:** replacing bar 5 with a claim-coverage or pairwise
  preference measure. The `walkthrough` trap is already a completeness rubric
  ("fails when it is compressed to a summary, or when either of the two named
  branches is silently dropped"), and preference is not part of a round.

## Pre-mortem, registered

The likeliest failure is the one round 70's replication had: the primary moves
the right way on opus and does not separate. That would mean the licence
reading is real in long field sessions and absent from a five-turn pilot even
on opus, and the next move is an instrument that reproduces the session, not a
seventh edit to this paragraph. The second likeliest is that opus is already
short at master rules on turns 2 to 4, so there is nothing to remove, which is
round 68's result on a different model. The least likely, and the most
expensive if it happens, is bar 5 firing: haiku cutting a requested walkthrough
to a summary once the bullet is gone. That would be a fatal rejection with the
target passing.

## Buying order, stopping at the first failure

All three cells generate in one pass, because the two sides must run
simultaneously and the bound shares the pass at little cost. Judging the bound
cells (160 calls) happens only after the primary is scored; if bar 1 fails,
the bound is not judged, and the round records that it was not.

## One interleaved pass, four shards

```sh
# control side: a worktree at master, on disk rather than /tmp
git worktree add /home/jordan/projects/laconic-r80-control master
OUT=/home/jordan/projects/laconic-r80/evals/snapshots/loop
WHY='every field report behind #150, #298 and #305 was Opus 5, and the harness has never reproduced the harm on sonnet'

for side in edit control; do
  tree=/home/jordan/projects/laconic-r80; [ $side = control ] && tree=$tree-control
  ( cd $tree && python3 evals/bench/run.py --arms laconic --models sonnet --reps 20 \
      --cases 'register-*,deep-*' --cases-dir evals/pilot --turn-delivery plugin \
      --concurrency 4 --snapshot $OUT/round-80-$side-sonnet.json ) &
  ( cd $tree && python3 evals/bench/run.py --arms laconic --models opus --allow-opus "$WHY" \
      --reps 10 --cases 'register-*,deep-*' --cases-dir evals/pilot --turn-delivery plugin \
      --concurrency 4 --snapshot $OUT/round-80-$side-opus.json \
    && python3 evals/bench/run.py --arms laconic --reps 20 \
      --cells 'walkthrough:haiku,walkthrough:sonnet,code-fidelity:haiku,code-fidelity:sonnet' \
      --concurrency 4 --snapshot $OUT/round-80-$side-bound.json ) &
done
wait
```

Scoring:

```sh
for m in opus sonnet; do
  python3 evals/pilot/score_claims.py $OUT/round-80-control-$m.json $OUT/round-80-edit-$m.json
done
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-80-$side-bound.json \
    --out $OUT/round-80-$side-bound-judgments.json
done
python3 evals/pilot/score_explain_bound.py $OUT/round-80-{control,edit}-bound.json \
  $OUT/round-80-{control,edit}-bound-judgments.json
python3 evals/bench/release.py $OUT/round-80-{control,edit}-{opus,sonnet}.json
```

## Results

<!-- Nothing above this line has been computed. -->

## Result: the licence is real on opus, and deleting it cuts facts, not only repetition

**Rejected on bar 4. The edit reverts in full.** The primary passed clearly and a
fatal bound fired, which is the third class the pre-mortem named and the one it
called least likely: a fatal counter rejecting an edit whose target passed.

880 runs, 0 failed, both sides simultaneous from two trees. Every snapshot spans
CLI 2.1.280 and 2.1.281, and `release.py` finds no arm imbalanced across the
boundary (opus 33/27 on both sides, sonnet 58/62 on both sides). `rules_cksum`
3285158247 on the control and 1320927575 on the edit; `cases_cksum` 1852778470
on both multi-turn pairs.

| bar | model | control | edit | ratio | p | reading |
|---|---|--:|--:|--:|--:|---|
| 1 primary, `register-*` words, turns 2-4 | opus | 1782.0 / 1487.5 / 1012.5 | 1586.5 / 1252.5 / 900.5 | **0.874** | **0.0010** | passes |
| 2 secondary, directional | sonnet | 1438.0 / 1082.0 / 538.5 | 1450.0 / 1001.5 / 502.5 | 0.955 | 0.1824 | holds (at or below 1.00) |
| 3 `register-*` coverage | opus | 17.5 / 15.5 / 25.0 | 17.5 / 15.0 / 23.0 | 0.962 | 0.0578 | holds |
| 3 `register-*` coverage | sonnet | 18.0 / 16.0 / 23.0 | 17.0 / 15.0 / 23.0 | 0.960 | 0.0559 | holds |
| **4 `deep-*` coverage** | **opus** | | | **0.845** | **0.0009** | **fires** |
| 4 `deep-*` coverage | sonnet | | | 0.955 | 0.2106 | holds |
| 5 never-cut keyword, `walkthrough` + `code-fidelity` | haiku + sonnet | 80/80 | 80/80 | | 1.0000 | holds |
| 5 judged safety | haiku + sonnet | | | | | not judged: bar 4 had already rejected |
| 6 `date_trunc` on `index` | both | 30/30 | 30/30 | | | holds |

Word columns are per-stem medians, index / metric / rollback. Every p is the
stem-stratified permutation `score_claims.py` computes, two-sided for the
target and one-sided down for coverage.

**What the round establishes.** Opus at master rules is the model the reports
describe. On the requested turns it writes 1,000 to 1,800 words per stem where
sonnet writes 540 to 1,440, and the licence ratio this round dropped as a bar
reads 3.09 on opus against 6.24 on sonnet, because opus is long on the
*unrequested* `deep-*` turns too (576.5 / 422.0 / 334.0 median words). The
edit took 12.6% off opus's requested turns at p = 0.0010, far past round 70's
sonnet effect, and sonnet here reproduced round 70's replication almost
exactly (0.955 against 0.946).

**What kills it.** On `deep-*`, opus lost 10% of its words (0.903, p = 0.0058)
and 15.5% of the fixture facts those words carried (0.845, p = 0.0009). Those
turns never invoked the licence, so the edit was not removing a licensed
restatement there. It was making opus say less of what the fixture contains.
The same edit on the requested turns lost 3.8% of coverage for 12.6% of words
(p = 0.0578), which is the trade the round wanted, and it only just held.
Deleting the bullet reads to opus as "explain less", not "repeat less".

**What it does not say.** It does not show the explain bullet is load-bearing
for the requested explanations bar 5 guards: `walkthrough` and `code-fidelity`
kept every never-cut keyword, and their judged verdict was never bought. The
loss is on unlicensed turns, which the bullet does not name.

**Next.** The effect on opus is large enough to be worth separating. The
edit changed two things at once, and the untested half is the one [#150]
proposed: keep the bullet, and rewrite only the paragraph so the licence covers
scope and not repetition. The instrument is this one, opus primary, with bar 4
kept.

Label: `failed-gate` in `candidate-defects/labels.json`.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
