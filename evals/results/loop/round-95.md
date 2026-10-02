# Round 95: the narrowing follow-up with a count rule and a demonstration pair, on opus (#305)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from rounds 93 and 94, which are merged. This file is
committed before any generation, at master rules (`rules_cksum` 288018845).
The edit below is applied to `rules/laconic.md` in the next commit on this
branch; the control side generates from a worktree at this commit.

`bash tools/candidate-due.sh` exited 1 at registration: round 94 measured, so
round 95 carries a rule edit, under **The edit** below.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_subset.py compare \
  --control evals/snapshots/loop/round-95-control.json \
  --edit evals/snapshots/loop/round-95-edit.json \
  --control-judgments evals/snapshots/loop/round-95-control-judgments.json \
  --edit-judgments evals/snapshots/loop/round-95-edit-judgments.json
python3 evals/bench/release.py evals/snapshots/loop/round-95-{control,edit}.json
```

## Why this round exists

[#305]'s narrowing follow-up re-lists, on opus, items its own inventory had
already listed. On `subset-*` the graded turn named the eight seeded open
questions again in 87 of 90 control runs in [round 93](round-93.md) and 29 of
30 at each depth in [round 94](round-94.md). Round 94's registered null branch
sends round 95 here.

Round 93's bullet, "wants that subset and anything that changed since, not the
earlier answer again", moved mean re-listings 7.91 to 7.73, p = 0.622. Round 93
left two readings open: (a) opus does not regard naming the eight as "the
earlier answer again", because the eight are also the subset asked for; (b) one
abstract bullet weighs too little against an inventory in context. This edit
answers both: it says what to do with the already-listed items, and it adds a
demonstration pair.

## The edit

One bullet with a `Wrong:`/`Right:` pair in `## Level: full`, after "No
next-steps list unless they asked what is next.":

```diff
 - No next-steps list unless they asked what is next.
+- A follow-up that narrows a question you already answered wants that subset
+  and what changed since. Items you already listed by name get a count or a
+  back-reference, not their names again.
+  - Wrong: after listing six failing tests by name, answering "what is left in
+    the API layer?" with the six names again.
+  - Right: "The same six failing tests, unchanged, plus `auth_retry`, which
+    broke since."
```

The pair is off-domain on purpose: a fixture-shaped example could move the
counter by teaching "count OQ IDs" rather than the rule. Per [#164] item 2 the
cells carrying the demonstrated form are pre-registered, and they are the
`subset-*` cells below. #305's item 1, the closing recap, stays out for round
92's reason.

## Design

Round 93's stage 2, unchanged apart from the edit. No fire precheck: the
control side is generated beside the edit and is itself the fire check, and
the re-listing has fired 116 of 120 at master rules on CLI 2.1.287.

Two trees generating simultaneously, per [round 38](round-38.md): control from
a worktree at this commit, the edit from the branch with `rules/dist/`
regenerated. Laconic arm, level `full`, opus, `--turn-delivery plugin`, 30 reps
per stem, 90 runs and 180 generation calls a side.

```sh
python3 evals/bench/run.py --arms laconic --reps 30 --cases-dir evals/pilot \
  --cells 'subset-ledger:opus,subset-scheduler:opus,subset-gateway:opus' \
  --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-95-$side.json
python3 evals/bench/judge.py --cases-dir evals/pilot \
  --results evals/snapshots/loop/round-95-$side.json \
  --out evals/snapshots/loop/round-95-$side-judgments.json
```

### The bars

Scored by `score_subset.py compare`, permutation seed 93.

1. **Primary, opus.** Mean re-listings per graded turn, edit against control,
   two-sided permutation, alpha 0.05. Registered direction: lower.
2. **Bound, fatal: turn 1's inventory may not get shorter.** One-sided
   permutation on mean log prose words, alpha 0.05.
3. **Bound, fatal: turn 1 may not name fewer of the eight.** One-sided, alpha
   0.05. Without it the primary could fall because the inventory stopped
   listing.
4. **Falsifier, fatal: judged quality on the graded turn**, by the panel, may
   not fall, one-sided Fisher, alpha 0.05. The trap accepts the eight named or
   counted but fails an answer that drops the two deliberate non-decisions, so
   "count everything" is caught here. Bought only if bar 1 passes.

One look, declared here. Disclosed, deciding nothing: graded prose-word
medians, per-stem counts, `panel_agreement.py`, `release.py`.

**Spillover screen, bought only if bars 1 to 4 pass.** The edit's precondition
is a question already answered, so the cases it can reach are the multi-turn
ones. The `*-index` cells of [#353]'s families (`recall-index`, `wide-index`,
`deep-index`), opus, 10 reps a side from both trees; panel quality may not
fall, one-sided Fisher on the pooled count, alpha 0.05, fatal. A back-reference
answering a closed question about the model's own earlier answer is the
nearest harm the edit could do.

**Accept** needs bar 1 to pass, bars 2 to 4 and the screen to hold, then step
8's replication at the same size and bars, and the holdout. Anything else
rejects and reverts `rules/laconic.md` and `rules/dist/`.

### What each outcome sends to round 96

- **Bar 1 fails near round 93's size:** reading (b) gains nothing from a pair
  and reading (a) is not answered by saying what to do. The next candidate on
  this issue is a fixture-shaped pair, which discriminates "the example's form"
  from "the rule's content".
- **Bar 1 passes and a bound fails:** the rule works and over-reaches; the
  failing bound names where.

## Pre-mortem, registered

I expect **bar 1 to move with the registered direction and separate**, the
first such move on this issue, because "a count or a back-reference" now names
the replacement behaviour that round 93's bullet left implicit. The likeliest
failure is the opposite of a weak edit: a fall in bar 4, where opus counts the
two deliberate non-decisions into a back-reference ("the same ten open
questions") and stops identifying them. If bar 1 fails instead, it will be
moving with the direction and not separating, as round 93 did.

## Where the ideas came from

The issue is round 94's registered null branch. Through `tools/consult.sh`,
Kimi and DeepSeek both proposed widening "a count" to "a count or a
back-reference", which was taken. DeepSeek argued that the control side makes
a separate fire precheck redundant, which was taken. Kimi proposed
pre-committing the fixture-shaped pair as the next step if this one fails,
which is the round 96 branch above, and a spillover screen on multi-turn cells
rather than a round-wide arm, which was taken in the form above. Codex did not
answer.

[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#164]: https://github.com/JordanMPDS/laconic/issues/164

## Results

<!-- Nothing above this line has been computed. -->
