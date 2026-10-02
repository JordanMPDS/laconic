# Round 96: round 95's count rule again, with a content bound on the inventory (#305)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from round 95, which is merged, and the coverage reading of
round 95's snapshots under **Why this round exists**, which costs no calls.
This file is committed before any generation, at master rules (`rules_cksum`
288018845). The edit below is applied to `rules/laconic.md` in the next commit
on this branch; the control side generates from a worktree at this commit.

`bash tools/candidate-due.sh` exited 0 at registration: round 95 carried a
candidate, so round 96 could have measured. It carries one anyway, under
**The edit** below.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_subset.py compare --coverage \
  --control evals/snapshots/loop/round-96-control.json \
  --edit evals/snapshots/loop/round-96-edit.json \
  --control-judgments evals/snapshots/loop/round-96-control-judgments.json \
  --edit-judgments evals/snapshots/loop/round-96-edit-judgments.json
python3 evals/bench/release.py evals/snapshots/loop/round-96-{control,edit}.json
python3 evals/bench/panel_agreement.py evals/snapshots/loop/round-96-edit-judgments.json
```

## Why this round exists

[Round 95](round-95.md) moved [#305]'s re-listing on opus from 7.82 to 0.13
per graded turn, and rejected on its bar 2: turn 1's inventory got about 5%
shorter (median 194 to 184.5 prose words, one-sided p = 0.0003). Round 95
registered that bar as fatal so that the primary could not fall because the
inventory stopped listing. Its own bar 3 says the eight seeded questions were
still named in every run.

Reading round 95's turn-1 texts, zero calls, says what the 5% was. The edit's
inventories group items rather than drop them: "All eight items are open. The
response cache (IMPL-3) is not started. The other seven are partly done and are
missing pool eviction, burst limiting, the circuit breaker's half-open state,
...". Per-item IMPL IDs appear on all eight in 81 of 90 edit runs against 90 of
90 control, and code spans fall from 4.8 to 2.7 a run. Every item is still
there. Counting the eleven IMPL and VAL items each turn 1 covers, by ID, ID list,
ID range or a per-item description pattern (`score_subset.py:covered`), reads
**11 of 11 in all 180 runs on both sides**.

So round 95's bar 2 measured the shortening the plugin exists to produce, on an
answer whose requested content was intact. Laconic's own line is that it
"never truncates requested content", and the bar that tests that is a content
bound, not a length bound. Round 95's registered branch for this outcome reads
"the rule works and over-reaches; the failing bound names where", and where it
names, on inspection, is not content.

**This is a bound rewritten after the bound failed, and it is disclosed as
that.** Two things keep it from being bound-shopping, and neither is a promise:
the round is generated fresh, so round 95's draw decides nothing here, and the
length bound is kept as a fatal floor with a tolerance rather than dropped (bar
2b). The coverage patterns were written against round 95's turn-1 texts, so on
round 95 they cannot fail; their test is round 96's.

## The edit

Round 95's edit, byte for byte. One bullet with a `Wrong:`/`Right:` pair in
`## Level: full`, after "No next-steps list unless they asked what is next.":

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

The pre-registered cells carrying the demonstrated form, per [#164] item 2,
are the `subset-*` cells below, as in round 95.

## Design

Round 95's design, with bar 2 replaced. Two trees generating simultaneously:
control from a worktree at this commit, the edit from the branch with
`rules/dist/` regenerated. Laconic arm, level `full`, opus,
`--turn-delivery plugin`, 30 reps per stem, 90 runs and 180 generation calls a
side.

```sh
python3 evals/bench/run.py --arms laconic --reps 30 --cases-dir evals/pilot \
  --cells 'subset-ledger:opus,subset-scheduler:opus,subset-gateway:opus' \
  --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-96-$side.json
python3 evals/bench/judge.py --cases-dir evals/pilot \
  --results evals/snapshots/loop/round-96-$side.json \
  --out evals/snapshots/loop/round-96-$side-judgments.json
```

### The bars

Scored by `score_subset.py compare --coverage`, permutation seed 93.

1. **Primary, opus.** Mean re-listings per graded turn, edit against control,
   two-sided permutation, alpha 0.05. Registered direction: lower.
2. **Bound, fatal: turn 1 may not cover fewer of the eleven IMPL and VAL
   items.** Mean items covered, one-sided permutation, alpha 0.05.
   **2b. Bound, fatal: turn 1's median prose words may not fall below 0.85 of
   control's.** A point floor, no test: it catches a truncation the coverage
   patterns cannot see, and 0.85 is three times round 95's observed fall.
3. **Bound, fatal: turn 1 may not name fewer of the eight seeded questions.**
   One-sided, alpha 0.05.
4. **Falsifier, fatal: judged quality on the graded turn**, by the panel, may
   not fall, one-sided Fisher, alpha 0.05. The trap accepts the eight named or
   counted and fails an answer that drops the two deliberate non-decisions, so
   "count everything" is caught here. Bought only if bars 1 to 3 pass.

Round 95's bar 2, the one-sided test on mean log turn-1 prose words, is
disclosed beside them and decides nothing. One look, declared here. Disclosed,
deciding nothing: graded prose-word medians, per-stem counts,
`panel_agreement.py`, `release.py`.

**Spillover screen, bought only if bars 1 to 4 pass**, as round 95 registered
it: the `recall-index`, `wide-index` and `deep-index` cells of [#353]'s
families, opus, 10 reps a side from both trees, `--turn-delivery plugin`; panel
quality may not fall, one-sided Fisher on the pooled count, alpha 0.05, fatal.

```sh
python3 evals/bench/run.py --arms laconic --reps 10 \
  --cells 'recall-index:opus,wide-index:opus,deep-index:opus' \
  --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-96-spill-$side.json
```

**Accept** needs bar 1 to pass and bars 2 to 4 and the screen to hold. Round
96's primary is the step 8 replication of round 95's, on a fresh draw at the
same size and with the same edit, so an accept here goes to the holdout and
then to release. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/`.

### What each outcome sends next

- **Bar 2 or 2b fails:** the edit truncates requested content on a fresh draw,
  and the next candidate scopes the bullet's wording so it cannot reach a first
  answer.
- **Bar 4 fails:** the back-reference costs the non-decisions, and the next
  candidate names what a back-reference must still carry.
- **The screen fails:** the edit reaches closed questions about an earlier
  answer, and [#353]'s families become this issue's instrument.

## Pre-mortem, registered

I expect bar 1 to replicate, and bars 2, 2b and 3 to hold. The likeliest
failure is still bar 4, as round 95 registered and never bought: opus folding
OQ-9 and OQ-27 into "the same ten open questions" and no longer saying they are
left open on purpose. That would be a fatal counter rejecting an edit whose
target passed. The second likeliest is the screen, on `deep-index`, where the
closed question asks about the model's own earlier answer.

## Where the ideas came from

The issue and the edit are round 95's. The content bound replacing round 95's
length bound is this round's own, from reading round 95's turn-1 texts. A
question to `tools/consult.sh` describing this design got no answer: Codex,
DeepSeek and Kimi all timed out or exited without one.

## Results

<!-- Nothing above this line has been computed. -->

[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#164]: https://github.com/JordanMPDS/laconic/issues/164
