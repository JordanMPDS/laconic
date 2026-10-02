# Round 93: an open narrowing follow-up over a three-bucket status file, decided on opus (#305)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from rounds 91 and 92, which are merged. This file, the
`subset-*` cases, their layout test and `evals/pilot/score_subset.py` are
committed before any generation. The edit is registered here as text and is
applied to `rules/laconic.md` only if stage 1 fires, so stage 1 runs at master
rules (`rules_cksum` 288018845) from the branch that adds the cases.

`bash tools/candidate-due.sh` exited 1 at registration: rounds 91 and 92 both
measured, so round 93 carries a rule edit, under **The edit** below. If stage 1
does not fire, the edit is withdrawn unrun as round 92's was, and this
document says so in its results.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_subset.py precheck evals/snapshots/loop/round-93-precheck.json
```

## Why this round exists

[#305] was reported on Opus 5: after a full "what is left?" inventory, the
user asked an eleven-word follow-up scoped to one of its three buckets, and
got 309 words where about 40 were right. 76 of them re-listed, by name, eight
open questions the inventory two turns earlier had already listed, unchanged.

Round 92 asked a closed one-word question after an inventory of a
one-decision record, and 0 of 30 opus graded turns ran over 80 words; no
graded turn repeated the inventory. It named the two differences from the
report that remained: the report's narrowing question was open, and its
record held many items in several buckets. `subset-*` carries both.

Each stem is a `STATUS.md` with three buckets. SPEC: every section closed,
and ten open questions, of which eight are seeded values awaiting the same
load-test measurement pass and two are deliberate non-decisions. IMPL: eight
open items. VALIDATOR: three. Turn 1 is "read STATUS.md — what is left with
`<project>`? Don't edit anything."; turn 2 is "what is left at the SPEC level
to finish `<project>`? Don't edit anything." The eight seeded questions share
one status, so the narrowed answer can count them, as the report's own
40-word ideal did.

**The counter is redundancy, not naming.** A re-listing is a seeded question
the graded turn names that the same run's turn 1 had already named, by ID, by
its snake_case key, or inside an ID range. Naming the eight is not wrong on
its own, since they are the SPEC subset; naming them again after the
inventory already did is #305's 25%. No judge is needed to count it.

The deciding model is opus, the model the report came from, and the defect has
to fire there before the edit is bought, per [round 89](round-89.md).

## The edit

One bullet in `## Level: full`, after "No next-steps list unless they asked
what is next.", byte-identical to round 92's unrun candidate:

```diff
 - No next-steps list unless they asked what is next.
+- A follow-up that narrows a question you already answered wants that subset
+  and anything that changed since, not the earlier answer again.
```

This is [#305]'s item 2. Item 1, the closing recap, is not in the edit, for
round 92's reason: [`closing-recap-305.md`](closing-recap-305.md) found no
deterministic detector for it.

## Stage 1: does the open narrowing follow-up re-list on opus? (60 opus calls)

Master rules, the laconic arm, opus, 10 reps per stem, `--turn-delivery
plugin`, one shard.

```sh
python3 evals/bench/run.py --arms laconic --reps 10 --cases-dir evals/pilot \
  --cells 'subset-ledger:opus,subset-scheduler:opus,subset-gateway:opus' \
  --turn-delivery plugin --concurrency 1 \
  --snapshot evals/snapshots/loop/round-93-precheck.json
python3 evals/pilot/score_subset.py precheck evals/snapshots/loop/round-93-precheck.json
python3 evals/bench/release.py evals/snapshots/loop/round-93-precheck.json
```

**Registered pass condition.** At least **9 of the 30** graded turns re-list
at least **5 of the 8** seeded questions. Graded-turn prose words and the
number turn 1 names are printed beside it and decide nothing.

**If it does not fire**, stage 2 is not generated, the edit is never applied,
and this document records the precheck. A null where turn 1 names the eight
says the open question and the buckets are not enough; a null where turn 1
does not name them says the instrument never set up the re-listing, and the
results say which.

## Stage 2: the edit on opus, only if stage 1 fires (about 720 opus calls)

Two trees generating simultaneously, per [round 38](round-38.md): control from
a worktree at this branch's registration commit, master rules; edit from the
branch with the bullet applied and `rules/dist/` regenerated. 30 reps per
stem, 90 runs and 180 generation calls a side, then the panel on each side's
graded turns.

```sh
python3 evals/bench/run.py --arms laconic --reps 30 --cases-dir evals/pilot \
  --cells 'subset-ledger:opus,subset-scheduler:opus,subset-gateway:opus' \
  --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-93-$side.json
python3 evals/bench/judge.py --cases-dir evals/pilot \
  --results evals/snapshots/loop/round-93-$side.json \
  --out evals/snapshots/loop/round-93-$side-judgments.json
python3 evals/pilot/score_subset.py compare \
  --control evals/snapshots/loop/round-93-control.json \
  --edit evals/snapshots/loop/round-93-edit.json \
  --control-judgments evals/snapshots/loop/round-93-control-judgments.json \
  --edit-judgments evals/snapshots/loop/round-93-edit-judgments.json
```

### The bars

1. **Primary, opus.** Mean re-listings per graded turn, edit against control,
   two-sided permutation (`metrics.permutation`), seed 93, alpha 0.05.
   Registered direction: lower.
2. **Bound, fatal: turn 1's inventory may not get shorter.** One-sided
   permutation on mean log prose words, alpha 0.05. The user asked for it.
3. **Bound, fatal: turn 1 may not name fewer of the eight.** One-sided
   permutation on the count, alpha 0.05. Without it the primary could fall
   because the inventory stopped listing, which is the opposite of the fix.
4. **Falsifier, fatal: judged quality on the graded turn**, by the panel, may
   not fall, one-sided Fisher, alpha 0.05. The trap fails an answer that drops
   the two deliberate non-decisions, so an edit that removes the eight by
   removing everything is caught here.

One look, declared here. Disclosed, deciding nothing: graded prose-word
medians, per-stem counts, `panel_agreement.py`, `release.py`. **Accept** needs
bar 1 to pass and bars 2 to 4 to hold, then step 8's replication at the same
size and bars, and the holdout. Anything else rejects and reverts
`rules/laconic.md` and `rules/dist/`.

There is no cold placebo arm. With a redundancy counter a cold answer reads 0
by construction, so it would add nothing to the primary; bars 2 and 4 are the
over-breadth checks instead.

## Pre-mortem, registered

The likeliest outcome is again that **stage 1 does not fire**, for the reason
round 92 could not rule out: two turns are not the report's long session, and
the open question and the buckets were only named as the remaining
differences, never shown to be the cause. The second likeliest is that turn 1
summarises the eight as one group, leaving nothing to re-list. If it fires,
the likeliest failure is **bar 1 moving with the registered direction and not
separating**, since one rule bullet competes with an inventory sitting in
context.

## Where the ideas came from

The family follows round 92's stated next step. Through `tools/consult.sh`,
DeepSeek proposed scoring redundancy against the run's own turn 1 rather than
naming, expanding ID ranges, and dropping the cold arm from the precheck;
all three were taken, and its argument that a redundancy counter makes a cold
placebo inert is why stage 2 has none. Kimi proposed non-contiguous IDs with
the two non-decisions interleaved, a different status sentence on each seeded
question, longer entries, and a turn 2 that does not point back at the list;
all were taken. Kimi's word-ratio fire condition was not, because it needs a
segmentation of turn 1's SPEC section that no deterministic rule gives, and
its claim that a placebo cancels in a difference of differences assumed the
placebo is identical on both sides, which it is not when the rules differ.
Codex did not answer.

[#305]: https://github.com/JordanMPDS/laconic/issues/305

## Results

<!-- Nothing above this line has been computed. -->
