# Round 104: replace the never-cut explain item with a guarantee of answering, on non-inferiority (#378)

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 89, 100 and 103, which are merged. This file, the
edit, the regenerated `rules/dist/*.md` and `evals/pilot/score_noninferior.py`
are committed in one commit before any generation.

`bash tools/candidate-due.sh` exited 1 at registration: round 103 measured, so
round 104 has to carry a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0.

**The issue is owner-requested.** [#378] was filed on 2026-10-03 from a review
of the never-cut list with the maintainer, who asked for it to be the next
candidate, stopped the loop after round 103, and had this round started by
hand. It runs unconditionally, with no fire-rate precheck, for the reason
round 100 gave: every open `rules` issue has read zero on opus for two weeks.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_noninferior.py --register-family fullexplain $OUT/round-104-{control,edit}.json 104
python3 evals/pilot/score_claims.py --register-family fullexplain $OUT/round-104-{control,edit}.json 104
python3 evals/pilot/score_reexplain.py --told fullexplain $OUT/round-104-{control,edit}.json 104
python3 evals/bench/release.py $OUT/round-104-{control,edit}.json
```

## Why this round exists

One line of the never-cut list is the common cause of [#46] and [#298]:

> - Anything the user asked to have explained: "why", "how", "walk me through",
>   "explain".

In #46 opus quoted it in its own reasoning — *"this is an explanation the user
asked for, so give full detail ... a small concrete schema/pseudocode since
that's never-cut content"* — and answered "how would that be built?" in about
1,400 words. In #298 a seven-word definition request was 70% restatement. The
`full` design-question bullet's *"Explaining something that already exists is
a different request, and it is protected above"* exists to fence this one
line. The other six never-cut items are implicated by no open issue and do not
move.

Neither symptom fires on opus at master rules. #46 read 0/72, 0/20, 0/20 and
0/20 over 600 prose words in rounds 82, 91, 98 and 101, and round 103's long
document did not fire it either. #298 withdrew at round 89's precheck, and
round 100's control read the told answer at 0.377 of the cold one, with no
headroom. A round that requires the symptom to fall rejects at the noise
floor, as rounds 100 and 102 did.

## The edit

```diff
-- Anything the user asked to have explained: "why", "how", "walk me through",
-  "explain".
+- An explanation the user asked for ("why", "how", "walk me through",
+  "explain") is given, not declined or deferred. Being asked to explain is not
+  a licence for length: when the user fixes the scope ("in full", "complete",
+  "every check"), give that scope; otherwise it gets the smallest set of
+  claims that fully answers it.
```

and in `## Level: full`, the design-question bullet:

```diff
   one reading would settle. Explaining something that already exists is a
-  different request, and it is protected above.
+  different request, and it is answered rather than redirected.
```

The item keeps its floor (an explanation is not declined) and loses its
ceiling (protected meant unbounded). The scope clause is Kimi's: without it,
*"the smallest set of claims"* collides with a turn that asks for the full form
in so many words, which is exactly what the primary measures. No
`Wrong:`/`Right:` pair, so no cells are pre-registered under [#164] item 2.

`README.md` and `skills/laconic-help/SKILL.md` paraphrase the old item; they
change only if the round accepts.

## Design

Round 100's cells and commands, unchanged except for the round number: two
trees generating simultaneously, control from a worktree at master
(`rules_cksum` 3660436060, released in 0.3.4), the edit from this branch.
Laconic arm, level `full`, opus, `--turn-delivery plugin`, 20 reps per stem on
`fullexplain-{index,metric,rollback}` (five turns) and
`explain-{index,metric,rollback}` (one turn): 120 runs and 360 generation calls
a side, 720 in all, as four shards inside [#255]'s ceiling.

```sh
CELLS='explain-index:opus,explain-metric:opus,explain-rollback:opus,fullexplain-index:opus,fullexplain-metric:opus,fullexplain-rollback:opus'
for side in control edit; do for off in 0 10; do
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$CELLS" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-104-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-104-$side-shard{0,10}.json --out $OUT/round-104-$side.json
```

Then `walkthrough` (from `evals/cases`), opus, 20 reps a side from both trees
into `round-104-walkthrough-{control,edit}.json`, the one dev case whose
criterion grades a requested explanation.

### Why non-inferiority is the accept rule

The edit deletes a licence. The direction it is meant to move does not fire
on any instrument here, so there is no directional target it could pass. The
direction that *can* fail is the harm: a requested explanation getting cut.
So the round accepts on ruling out a pre-specified harm, not on detecting a
benefit. This is new in the loop, and it is stated here so it is not
re-argued after the numbers:

- **An underpowered round does not accept.** The accept is the rejection of
  "the edit is worse than the margin", so too few reps leave that null
  standing and the round rejects.
- **The margin is 0.95 and fixed.** A round that fails to show it buys reps
  under a new round; it does not re-argue the margin.
- **Inconclusive is a reject**, and no stem is re-run until it passes.

Sanity, at registration, on round 100's committed data: its control read
against itself gives ratio 1.053 at p = 0.0023 (non-inferior); its edit, which
lost 5.2% coverage, gives 0.998 at p = 0.536 (not shown). The scorer separates
the two cases this rule exists to separate.

### The bars

1. **Primary, accept basis: fixture-token coverage over `fullexplain-*` turns
   2 to 4 is non-inferior at 0.95**, edit against 0.95 x control,
   stem-stratified permutation, one-sided, alpha 0.05, by
   `score_noninferior.py`. Those turns ask for the full form verbatim: *"the
   complete checklist, every check written out in full"*, *"walk me through
   why ... step by step, in full"*, *"the full assessment as a table"*.
2. **Bound, fatal: coverage over the same turns may not fall**, one-sided,
   alpha 0.05, by `score_claims.py`, as round 100 registered it.
   **2b. Bound, fatal: prose words over the same turns at least 0.85 of
   control's**, stem-stratified ratio, point floor.
3. **Bound, fatal: `date_trunc`** kept on the `index` graded turn, both
   families.
4. **Falsifier, fatal: panel quality may not fall** on the `explain-*` graded
   turn, the `fullexplain-*` graded turn, and `walkthrough`, each one-sided
   Fisher, alpha 0.05. These are the "is given, not declined" half of the
   edit. Bought only if bars 1 to 3 pass.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`.

**Disclosed, deciding nothing:** graded-turn prose words on `explain-*` and
on `fullexplain-*`, edit against control (the field reports' direction, down);
the control's told/cold ratio; `walkthrough` prose words and its `401`
never-cut keyword; `panel_agreement.py`; `release.py`.

**Replication, bought only if everything above passes:** a fresh 120 runs a
side on the same cells from the same two trees, scored on bars 1 and 4 at the
same alphas. Then step 9's holdout: all reserved cases, opus, 10 reps, both
trees; no reserved case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and every other bar to hold. Anything else
rejects and reverts `rules/laconic.md` and `rules/dist/` before the merge.

## Pre-mortem, registered

The likeliest failure is **bar 1 not separating with the point estimate near
1**: a 5% margin at 20 reps per stem is close to the resolution round 100
found (it detected 5.2% at p = 0.021), so a true ratio of 1.00 passes perhaps
two times in three. That is the noise-floor class, and it sends the next round
to buy reps, not to change the margin. The second likeliest is **bar 2b or
bar 4 on `walkthrough`**: "not a licence for length" read as a length cap on
a whole-flow walkthrough that names no scope word, which is a fatal bound
rejecting an edit whose target passed. A point estimate *below* 0.95 would
mean the scope clause did not hold and the floor-and-ceiling wording is the
wrong lever; deletion outright would then be strictly worse.

## Where the ideas came from

The non-inferiority frame and the deletion reading are from the maintainer's
review that filed #378. Through `tools/consult.sh`, Kimi supplied the scope
clause in the edit, the three pre-commitments under the accept rule, and the
advice to keep the replacement rather than delete the item. Codex and
DeepSeek did not answer within the timeout.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#378]: https://github.com/JordanMPDS/laconic/issues/378

## Results

<!-- Nothing above this line has been computed. -->

### First sample

240 runs on the pilot cells and 40 on `walkthrough`, 0 failed after one
resume: the `walkthrough` pass hit a usage limit on its last four control and
three edit runs, and the same command resumed them by key. `rules_cksum`
3660436060 on every control and 3769556782 on every edit; every run on CLI
2.1.288, so `release.py` finds no span on either pair. `merge.py` notes 120
runs against a declared 60 per shard pair, which is the two `--rep-offset`
shards and not a gap.

| bar | control | edit | p | |
|---|--:|--:|--:|---|
| 1. coverage, `fullexplain-*` turns 2-4, edit / (0.95 x control) | | 1.045 | 0.018 (one-sided) | **passes** |
| 2. coverage, same turns, may not fall | | ratio 0.993 | 0.300 (one-sided) | holds |
| 2b. prose words, same turns, floor 0.85 | | ratio 0.991 | | holds |
| 3. `date_trunc` on the `index` graded turn, `fullexplain` / `explain` | 20/20, 20/20 | 20/20, 20/20 | | holds |
| 4. panel quality, `explain-*` graded turn | 60/60 | 60/60 | 1.000 | holds |
| 4. panel quality, `fullexplain-*` graded turn | 60/60 | 60/60 | 1.000 | holds |
| 4. panel quality, `walkthrough` | 20/20 | 20/20 | 1.000 | holds |

Per stem, turns 2-4: coverage 17.0 / 17.0 (`index`, of 37), 15.0 / 15.0
(`metric`, of 24), 24.0 / 23.5 (`rollback`, of 30); prose words 1623.0 /
1582.5, 1273.5 / 1246.5, 865.0 / 882.0.

Every bar-4 cell is at ceiling on both sides, so per [#94] it can detect a
fall and not a rise, and it saw none. The panel was unanimous wherever all
three voted; kimi returned no vote on 14 control and 11 edit pilot verdicts,
which sonnet and opus decided together.

**Disclosed, deciding nothing.**

- Graded-turn prose words: `explain-*` 143.0 to 144.0 (ratio 1.007,
  p = 0.906), `fullexplain-*` 57.5 to 54.0 (0.939, p = 0.828). The field
  reports' direction does not appear, as registered: the control's told/cold
  ratio is 0.402, so opus still has no #298 headroom here.
- **`walkthrough` is 14% shorter under the edit**, median prose words 618.0
  to 533.5, one-sided permutation p = 0.001, ranges 483-751 and 457-654. That
  case names no scope word, so it is where the pre-mortem's second risk
  lives, and the length moved. Its quality did not: 20/20 on both sides, the
  `401` keyword kept 20/20, and every panel reason names both requested
  branches. The edit read "walk me through the whole flow" as a request for
  the whole flow and stopped volunteering past it. This is not a registered
  bar, and it is recorded here so the replication can be read against it.
