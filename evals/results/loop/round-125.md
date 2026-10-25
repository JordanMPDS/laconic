# Round 125: the findings below the decider get one sentence each (#113)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds and from round 124's committed
snapshot. This file is committed before any generation, with
`rules/laconic.md` at master; the edit is committed after it, so the control
worktree is this commit.

`bash tools/candidate-due.sh` exited 1 at registration: rounds 123 and 124
both measured, so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0: v0.3.10 is tagged and current.

## Why this round exists, and why it has no withdrawing precheck

Every open `rules` issue reads zero on the current CLI in its own precheck
([round 124](round-124.md) lists them), and round 124's whole-benchmark pass
found no sonnet or opus failure the rules cause. Two rounds in a row have
measured. A third round that registers an edit behind a fire-rate precheck
and withdraws it unrun would be a third measuring round, which is the drift
the cap exists to stop. So this round takes a target that has measurable room
on the deciding model today, and its edit is generated whatever the room
turns out to be.

The room is length on evaluative questions, on opus. [#113] reports a
feasibility question ("is it possible to test this on X?") answered at about
600 words, and puts it in one family with [#60]'s "is this sound?" at 650. Its
proposal C is that such a question "is answerable as a verdict plus the
constraint that decides it". [Round 111](round-111.md) shipped half of that
shape for a list of findings: *"say which one decides it and rank the rest
under it"*, which cut `verdict-schema`/sonnet's quality fails 28/30 to 6/30.
It says nothing about how much of the answer the rest may take, and on opus
the rest is most of it. Round 124's committed opus answers at v0.3.10, 5 a
cell:

| cell | prose words | list items |
|---|---|---|
| `verdict-experiment`/opus | 432, 549, 439, 445, 505 | 7, 13, 14, 9, 13 |
| `verdict-rollout`/opus | 309, 274, 210, 329, 270 | 3, 4, 5, 5, 6 |
| `verdict-schema`/opus | 268, 246, 283, 288, 235 | 7, 8, 9, 8, 9 |

Round 124's stage 1b put `verdict-experiment`/opus at a median 480.5 words
over 20 answers, against 863.5 on the no-rules arm. A typical
`verdict-experiment` answer names the stopping rule as decisive and then
gives three further problems at 60 to 80 words each and a four-item "Add"
list; `verdict-schema` follows the float money type with five ranked issues
at 30 to 50 words each and three smaller gaps. `verdict-rollout` has the
least room, because its list items are the expand-and-contract fix for the
decider rather than lesser problems, which the edit does not reach.

[#113] was observed on opus, so opus decides the round.

## The edit

The findings sentence in `level: full`, extended by its last three words:

```diff
 - One recommendation, not a survey. A real trade-off gets one line per side,
   then a pick. Findings take the same pick: when the answer is a list of
-  problems, say which one decides it and rank the rest under it.
+  problems, say which one decides it and rank the rest under it, one sentence
+  each.
```

The decider and its fix are left alone: they are the answer to "is this
sound, or should we change something?". What the edit caps is the ranked
remainder, which the user asked about only as "or should we change
something", and which the never-cut list still protects where it holds a
security warning or bad news.

## Hypothesis

> Extending round 111's findings sentence with "one sentence each" should
> move median prose words on `verdict-experiment`, `verdict-rollout` and
> `verdict-schema` on opus **down**, without lowering the panel pass rate on
> those cells, on `destructive`/opus, or on the three `verdict-*` cells on
> sonnet.

## Design

Two trees generating at once: the control from a worktree at this commit
(master rules, `rules_cksum` 1540384109), and the edit from this branch with
the edit committed and `rules/dist/` regenerated. Laconic arm only. Two shards
a side, four `run.py` processes, `--concurrency 4` on each:

```sh
OUT=evals/snapshots/loop
T=verdict-experiment:opus,verdict-rollout:opus,verdict-schema:opus
B=destructive:opus,verdict-experiment:sonnet,verdict-rollout:sonnet,verdict-schema:sonnet
common="--arms laconic --turn-delivery plugin --concurrency 4"
for side in control edit; do   # control from /tmp/laconic-control-125
  ( cd <tree for $side> && python3 evals/bench/run.py $common --reps 20 \
      --cells "$T" --snapshot $OUT/round-125-$side-target.json ) &
  ( cd <tree for $side> && python3 evals/bench/run.py $common --reps 10 \
      --cells "$B" --snapshot $OUT/round-125-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-125-$side-{target,bounds}.json \
      --out $OUT/round-125-$side.json
done
python3 evals/bench/release.py $OUT/round-125-{control,edit}.json
python3 evals/pilot/score_findings_length.py words \
    $OUT/round-125-control.json $OUT/round-125-edit.json
```

100 generations a side, 70 of them opus. **The primary is scored before any
judging is bought**, because it reads prose words only: a primary that fails
rejects the round and nothing is judged. If it passes:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-125-$side.json --jobs 2 \
      --out $OUT/round-125-$side-judgments.json
done
python3 evals/pilot/score_findings_length.py bounds \
    $OUT/round-125-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-125-{control,edit}-judgments.json
```

### The bars

1. **Primary: prose words fall on the three `verdict-*` cells on opus.**
   One-sided stratified permutation of the side label within each cell;
   statistic the mean over the three cells of (median log edit words −
   median log control words); seed 125, 200,000 resamples, alpha 0.05.
   Words are `score_compression.words`, the loop's prose counter, which
   counts list items and drops fenced and inline code.
2. **Bounds, fatal, each one-sided Fisher on the panel pass rate at alpha
   0.05, uncorrected, per cell:** `verdict-experiment`, `verdict-rollout`
   and `verdict-schema` on opus (20 a side); `destructive`/opus (10), whose
   answer passes only when it names both foreign keys the drop breaks, so a
   ranking that demotes one shows here; and the three `verdict-*` cells on
   sonnet (10 each), including `verdict-schema`/sonnet, the cell round 111's
   sentence was shipped to fix.

One look, declared here. `evals/pilot/score_findings_length.py` implements
both bars and its `--selftest` runs in CI.

**Disclosed, deciding nothing:** per cell, median total words (whitespace
tokens of the whole response, so a fall that comes from moving prose into
code spans shows), median list items, `release.py`, `panel_agreement.py`,
and a hand read of 10 edit answers across the three opus cells for whether
each ranked item still names a concrete change.

**Replication, bought only if the primary passes and every bound holds:** a
fresh 100 runs a side from the same two trees (`--rep-offset 20` on the
target shard, `--rep-offset 10` on the bounds shard, into `round-125-rep-*`),
scored on the same bars. **Then step 9's holdout:** all six reserved cases,
sonnet and opus, 5 reps, both trees, judged, scored with
`score_findings_length.py holdout`: no reserved case worse at one-sided
p < 0.05, directions only.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `rules/laconic.md` and `rules/dist/` are
reverted before the merge.

## Origin

I put the design to the delegate targets through `tools/consult.sh`; Codex
and DeepSeek timed out, Kimi answered. Adopted from Kimi: "one sentence each"
in place of my "at a line each", which depends on layout; bounds per cell
rather than pooled, so the cell round 111 was shipped to fix cannot regress
inside a pool; checking that the word counter counts list items, and
disclosing total words beside it so a fall from moving prose into code spans
or headings shows; and the hand read for whether the one-sentence items stay
actionable. Not adopted: capping the decider at one paragraph, which would
pull a second lever, and an escape clause I had drafted ("a problem that
needs more than a line to act on is a second decider"), which I dropped
before registering so that one sentence changes, and so the edit cannot
license the "equally decisive" list `verdict-schema`'s criterion fails.

## Pre-mortem, registered

I expect the primary to pass: the remainder is 60 to 80 words an item on
`verdict-experiment` and 30 to 50 on `verdict-schema`, and a sentence is about
20. If the round rejects, the likeliest way is the third class, a fatal bound
rejecting an edit whose target passed, and the likeliest bound is
`destructive`/opus, where the second foreign key becomes a one-sentence lesser
item and the panel stops reading it as a blocker, or `verdict-experiment`,
where a one-sentence item asks for a change to a settled point without the
qualification that kept it passing. The point estimate moving against the
registered direction would mean opus treats "one sentence each" as licence to
promote items into the decider, and I give it little weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#113]: https://github.com/JordanMPDS/laconic/issues/113
