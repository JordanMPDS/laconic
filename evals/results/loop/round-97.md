# Round 97: the count rule, with a back-reference that accounts for the whole subset (#305)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from rounds 95 and 96, which are merged. This file is
committed before any generation, at master rules (`rules_cksum` 288018845).
The edit below is applied to `rules/laconic.md` in the next commit on this
branch; the control side generates from a worktree at this commit.

`bash tools/candidate-due.sh` exited 0 at registration: round 96 carried a
candidate, so round 97 could have measured. It carries one anyway, under
**The edit** below, because round 96 registered this candidate as its next
step on a bar 4 failure.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_subset.py compare --coverage \
  --control evals/snapshots/loop/round-97-control.json \
  --edit evals/snapshots/loop/round-97-edit.json \
  --control-judgments evals/snapshots/loop/round-97-control-judgments.json \
  --edit-judgments evals/snapshots/loop/round-97-edit-judgments.json
python3 evals/bench/release.py evals/snapshots/loop/round-97-{control,edit}.json
python3 evals/bench/panel_agreement.py evals/snapshots/loop/round-97-edit-judgments.json
```

## Why this round exists

[Round 96](round-96.md) replicated round 95's count-or-back-reference bullet:
re-listings on [#305]'s narrowing follow-up fell from 8.00 to 0.53 per graded
turn on opus, and turn 1 kept all eleven IMPL and VAL items. It rejected on its
fatal bar 4, graded-turn panel quality 90/90 to 83/90 (p = 0.0069). All seven
failures were one failure: the back-reference collapsed to the largest group
that shared a status ("only the eight seeded values from my last answer
remain") and dropped the two deliberate non-decisions, which the trap requires.

Round 96 registered the branch this round takes: "the next candidate names what
a back-reference must still carry". The fire rate needs no precheck. Round 96's
control re-listed at 8.00 per graded turn on these cells, on opus, on CLI
2.1.287, earlier today, and `claude --version` still reads 2.1.287.

## The edit

Round 95's bullet, with one sentence added and the `Right:` example extended.
In `## Level: full`, after "No next-steps list unless they asked what is
next.":

```diff
 - No next-steps list unless they asked what is next.
+- A follow-up that narrows a question you already answered wants that subset
+  and what changed since. Items you already listed by name get a count or a
+  back-reference, not their names again. The back-reference has to account
+  for the whole subset: an item in it that differs from the rest keeps its
+  own mention.
+  - Wrong: after listing six failing tests by name, answering "what is left in
+    the API layer?" with the six names again.
+  - Right: "The same six failing tests, unchanged, plus `auth_retry`, which
+    broke since. `flaky_dns` stays quarantined."
```

The added sentence is deliberately not about the fixture. It does not say
"left open on purpose", which is the trap's distinguishing property; it says
an item that differs from the rest of the subset keeps its mention, whatever
the difference is. The example's outlier differs by status (quarantined rather
than failing) and is not new, which is the case round 96's example lacked: its
only outlier, `auth_retry`, was something that changed, and opus generalised
to "name what changed" rather than "name what differs".

The pre-registered cells carrying the demonstrated form, per [#164] item 2,
are the `subset-*` cells below, as in rounds 95 and 96.

## Design

Round 96's design unchanged. Two trees generating simultaneously: control from
a worktree at this commit, the edit from the branch with `rules/dist/`
regenerated. Laconic arm, level `full`, opus, `--turn-delivery plugin`, 30
reps per stem, 90 runs and 180 generation calls a side.

```sh
python3 evals/bench/run.py --arms laconic --reps 30 --cases-dir evals/pilot \
  --cells 'subset-ledger:opus,subset-scheduler:opus,subset-gateway:opus' \
  --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-97-$side.json
python3 evals/bench/judge.py --cases-dir evals/pilot \
  --results evals/snapshots/loop/round-97-$side.json \
  --out evals/snapshots/loop/round-97-$side-judgments.json
```

### The bars

Scored by `score_subset.py compare --coverage`, permutation seed 93, exactly
as round 96 registered them.

1. **Primary, opus.** Mean re-listings per graded turn, edit against control,
   two-sided permutation, alpha 0.05. Registered direction: lower.
2. **Bound, fatal: turn 1 may not cover fewer of the eleven IMPL and VAL
   items.** Mean items covered, one-sided permutation, alpha 0.05.
   **2b. Bound, fatal: turn 1's median prose words may not fall below 0.85 of
   control's.** A point floor, no test.
3. **Bound, fatal: turn 1 may not name fewer of the eight seeded questions.**
   One-sided, alpha 0.05.
4. **Falsifier, fatal: judged quality on the graded turn**, by the panel, may
   not fall, one-sided Fisher, alpha 0.05. This is the bar the added sentence
   exists to pass. Bought only if bars 1 to 3 pass.

One look, declared here. Disclosed, deciding nothing: round 95's bar 2 (mean
log turn-1 prose words), graded prose-word medians, how many graded turns name
the two non-decisions, per-stem counts, `panel_agreement.py`, `release.py`.

**Spillover screen, bought only if bars 1 to 4 pass**, as rounds 95 and 96
registered it: the `recall-index`, `wide-index` and `deep-index` cells of
[#353]'s families, opus, 10 reps a side from both trees,
`--turn-delivery plugin`; panel quality may not fall, one-sided Fisher on the
pooled count, alpha 0.05, fatal.

```sh
python3 evals/bench/run.py --arms laconic --reps 10 \
  --cells 'recall-index:opus,wide-index:opus,deep-index:opus' \
  --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-97-spill-$side.json
```

**Replication, bought only if everything above passes.** The added sentence is
new, so bar 4 has one sample, and step 8 requires another before anything
ships. A fresh 90 runs a side on the same cells from the same two trees, into
`round-97-rep-{control,edit}.json`, scored on bars 1 and 4 at the same alphas.
Then step 9's holdout: all six reserved cases, opus, 10 reps, both trees;
no reserved case worse at p < 0.05, directions only.

**Accept** needs every bar above to pass or hold, and only then does the PR
merge with the edit in it. Anything else rejects and reverts
`rules/laconic.md` and `rules/dist/` before the merge.

### What each outcome sends next

- **Bar 1 fails:** naming the differing items brought the re-listing back, and
  the sentence is the wrong lever; the next candidate leaves the bullet as
  round 95 had it and moves the accounting into the `Right:` example alone.
- **Bar 2, 2b or 3 fails:** the edit truncates requested content, and the next
  candidate scopes the bullet so it cannot reach a first answer.
- **Bar 4 fails again on the non-decisions:** an abstract "differs from the
  rest" does not reach the case, and #305 goes back to the loop's queue with
  the count rule's measured cost recorded on the issue.
- **The screen fails:** the edit reaches closed questions about an earlier
  answer, and [#353]'s families become this issue's instrument.
- **The replication or the holdout fails:** reject, as step 8 and step 9 say.

## Pre-mortem, registered

I expect bar 1 to pass at a smaller effect than round 96's, because an answer
that names OQ-8 and OQ-22 is not a re-listing of the eight but the sentence
may also let some runs name the eight again as "items that differ". Bars 2 to
3 should hold, as twice before. The likeliest failure is bar 4 again, through
the mechanism the consult named: opus reads "differs from the rest" and still
answers "the same ten open questions", folding the two non-decisions into one
count with the eight, which the trap fails because it no longer says they are
left open on purpose. That would be a fatal counter rejecting an edit whose
target passed.

## Where the ideas came from

The issue and the bullet are round 95's. That the next candidate should name
what a back-reference must still carry is round 96's registered branch. The
added sentence's general wording, dropping a case-shaped "such as one left open
on purpose" from my draft, and the advice not to add a second `Wrong:` that
mirrors the fixture's eight-and-two, came from DeepSeek through
`tools/consult.sh`; DeepSeek also named the pre-mortem's mechanism. Its draft
kept "stays skipped on purpose" in the example; replacing that with
"quarantined", so the example's outlier does not share the trap's property
either, is this round's own. Codex timed out and Kimi was at its usage limit.

## Results

<!-- Nothing above this line has been computed. -->
