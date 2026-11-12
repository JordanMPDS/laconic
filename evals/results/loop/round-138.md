# Round 138: a feasibility question gets a word count (#113)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds. This file is committed first, with
`plugin/rules/laconic.md` at master, so the control worktree is that commit;
the edit, the regenerated `plugin/rules/dist/*.md` and the slice budget are
committed after it. Both commits precede any generation.

`bash tools/candidate-due.sh` exited 1 at registration: round 137 proposed no
rule edit, so this round has to carry one, and does, under **The edit**
below. `bash tools/release-due.sh` exited 0: v0.10.0 is tagged and current.

Decided on **opus**: [#113] was observed on Opus at level `full`.

## Why this round exists

[Round 136](round-136.md) gave the cold feasibility question of [#113]'s item
C a shape bullet, *"A feasibility question gets the verdict, the constraint
that decides it and its consequences, and at most one caveat."*, and it
failed its primary at a factor of 0.977. Opus obeyed the shape and kept the
length: the median `coldfeasible-state` answer led with the verdict and then
wrote out every consequence as a bolded list. [#500]'s explanation answers
did the same: [round 128](round-128.md)'s shape bullet (*"what each part is,
what decides it, and any caveat"*) moved them by a factor of 0.977, the
figure round 136 read, while [round 129](round-129.md)'s count per part and
[round 132](round-132.md)'s *"at most 60 words for each part the question
names"* were accepted. A count moved opus where a shape did not, so this
round tests round 136's bullet with a word count in place of its caveat
limit. Words rather than sentences, because [round 130](round-130.md) found
opus keeps no sentence count.

Every other open `rules` issue is behind a precheck its defect no longer
passes ([#46], [#264], [#298]); [#353] closed in round 137. This is the one
candidate with a reading that fires.

**No sizing look.** Round 136's control measured the three cold cells at
medians of 157.5, 169.5 and 204.0 prose words, at 14:12 UTC today, on CLI
2.1.321, which is still the release. Master's rules have moved once since,
[#438]'s *"configuration"* for *"config"* in the never-cut list
(`rules_cksum` 2816272927 to 303191222), which no cold answer can reach. A
look would buy the reading round 136 made four hours ago.

## The instrument

Round 136's, unchanged: the same cells, reps, shards, bars and scorer. No
pilot case, criterion or scorer is edited for this round.
`evals/pilot/score_feasible_edit.py` scores every bar, with round 136's seed,
and imports round 131's references from `score_feasible.py`.

| role | cells | reps a side |
|---|---|--:|
| primary | `coldfeasible-{replay,shadow,state}`/opus | 20 |
| bounds | `coldfeasible-*`/sonnet; `keep-cdc`, `keep-disk`, `keep-checkout`/opus; `walkthrough`/opus | 10 |
| bound | `feasible-{replay,shadow,state}`/opus, the four-turn session | 5 |

Round 136 describes each cell. The two that matter most here: the
`coldfeasible-state` trap fails an answer that drops the integral term and
the stale count, which is the consequence chain #113 says a fix must not
cost, and `keep-cdc` and `keep-disk` fail a flat yes or no where the right
answer is conditional.

## The edit

One bullet appended to `level: full`, after the explanation bullet:

```diff
   description of what they name: say what happens, not which component
   does it.
+- A feasibility question gets the verdict, the constraint that decides it
+  and its consequences, in at most 80 words.
```

- **Round 136's bullet with its caveat limit replaced by a word count.** Its
  trigger and its three slots stay, so the treatment differs from the one
  round 136 rejected by the number alone, and a result here reads as the
  number's.
- **"and its consequences" stays.** Round 136 found it read as a licence to
  list every consequence, but without a length bound; under a count the list
  has to fit. Dropping it would leave the consequence chain #113 protects in
  no slot.
- **80 words**, against round 131's references of 82, 65 and 60, which are
  complete answers. The explanation bullet's 60 is a count *per part*, and a
  feasibility question names no parts, so this bullet carries its own.

**The slice budget rises with it, from 9,500 to 9,700 characters**, as in
round 136. The hook's `ultra` output measures 9,487 at master, against the
9,500 `tests/test_laconic.sh` enforces, and every `full` bullet reaches
`ultra` by inheritance. Cutting text elsewhere would put a second edit in the
treatment. 9,700 stays 300 under Claude Code's 10,000-character cap, and a
rejection reverts the budget with the bullet.

## Hypothesis

> Appending "A feasibility question gets the verdict, the constraint that
> decides it and its consequences, in at most 80 words." to `level: full`
> should move prose words on `coldfeasible-replay`, `coldfeasible-shadow` and
> `coldfeasible-state` on opus **down**, to a factor of 0.80 of the control or
> less, without raising prose words on the three `keep-*`/opus cells, without
> lowering the panel pass rate on any bounds cell or on the `feasible-*`
> sessions, without lowering the share of `coldfeasible-*`/opus answers free
> of readability violations, and without lowering the share of
> `walkthrough`/opus answers carrying `401`.

## Stage 2: the edit on opus

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r138-control` at this registration commit, the
edit from `/home/jordan/projects/laconic-r138-edit` at the edit commit, both
on disk rather than under `/tmp`. Two shards a side, so four `run.py`
processes at most; each side's bounds shard runs its session cells after its
single-turn cells, in the same shell.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='coldfeasible-*:opus'
B='coldfeasible-*:sonnet,keep-cdc:opus,keep-disk:opus,keep-checkout:opus,walkthrough:opus'
S='feasible-*:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r138-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-138-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r138-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-138-$side-bounds.json \
    && python3 evals/bench/run.py \
      $common --reps 5 --cells "$S" --snapshot $OUT/round-138-$side-session.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-138-$side-{target,bounds,session}.json \
      --out $OUT/round-138-$side.json
done
python3 evals/bench/release.py $OUT/round-138-{control,edit}.json
S=evals/pilot/score_feasible_edit.py
python3 $S words $OUT/round-138-{control,edit}.json
python3 $S longer $OUT/round-138-{control,edit}.json
python3 $S readability $OUT/round-138-{control,edit}.json
python3 $S nevercut $OUT/round-138-{control,edit}.json
```

That is 160 opus calls and 30 sonnet calls a side, the 15 sessions counted
at four turns each. **The primary and the three deterministic bounds are
scored before any judging is bought**: if any fails, the round rejects and
nothing is judged. If all pass:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-138-$side.json --out $OUT/round-138-$side-judgments.json
done
python3 $S bounds $OUT/round-138-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-138-{control,edit}-judgments.json
```

### The bars

Round 136's, unchanged.

1. **Primary: prose words fall on `coldfeasible-*`/opus.** One-sided
   stratified permutation of the side label within each cell, on median log
   prose words (`score_compression.words`, inline code out); seed 136,
   200,000 resamples, alpha 0.05; **and** the factor, exp of the mean log
   ratio, at 0.80 or less. One look, declared here.
2. **Prose words, fatal:** may not rise on the three `keep-*`/opus cells, the
   same statistic with the sides swapped, one-sided at alpha 0.05.
3. **Readability, fatal:** the share of `coldfeasible-*`/opus answers with no
   `metrics.score` violation may not fall, pooled, one-sided Fisher at alpha
   0.05.
4. **Never-cut keywords, fatal:** `walkthrough`/opus answers carrying `401`,
   one-sided Fisher at alpha 0.05.
5. **Bounds, fatal:** the panel pass rate may not fall on any of the ten
   single-turn cells, each a one-sided Fisher at alpha 0.05, uncorrected, nor
   on the three `feasible-*`/opus cells pooled.

**Disclosed, deciding nothing:** per cold cell, the median against round 131's
reference, median bold labels and headings, and closing offers; how many cold
answers exceed 80 prose words; prose words on every other cell, and on the
session's turns 3 and 4; which `keep-*` answers give a flat yes or no, read by
hand; how many `coldfeasible-state` answers name both the integral term and
the stale count; `release.py` and `panel_agreement.py`.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard and `--rep-offset 5` on its session
cells, into `round-138-rep-*`), scored on the same bars. **Then step 9's
holdout:** all six reserved cases, sonnet and opus, 5 reps, both trees,
judged with `--cases-dir evals/holdout`, scored with `score_feasible_edit.py
holdout`: no reserved case worse at one-sided p < 0.05. The snapshots are
named `round-138-holdout-{control,edit}.json` so that `report.py`'s wear count
reads them. Round 136 consulted no holdout, so this would be the fourth
consultation of the five cases authored in #566 and the third of
`holdout-scratch`, whose budget is four; all six are within their budgets.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md`,
`plugin/rules/dist/` and the slice budget are reverted before the merge.

## Origin

The number is this round's own, from rounds 129 and 132 on [#500]. I put the
design to the delegate targets through `tools/consult.sh`, leaning then
towards *"A feasibility question gets the verdict and what decides it, in at
most 80 words."* Codex and DeepSeek did not answer within 240 seconds; Kimi
answered. Adopted from Kimi: **keeping "and its consequences"**, on its
reading that round 136 failed for want of a length bound rather than for
naming consequences, so a count bounds the list while the slot keeps the
chain #113 protects; and **a bullet with its own number** rather than
widening the explanation bullet's trigger, since a feasibility question names
no parts for "60 words for each part" to count. Not adopted: Kimi's *"its two
consequences"*, which is the `coldfeasible-state` trap's own count written
into the rules.

## Pre-mortem, registered

The likeliest rejection is the third class on bound 5 at `coldfeasible-state`:
80 words holds the verdict and the lease constraint, and opus cuts one of the
two consequences the trap needs, the stale count before the integral term.
The second likeliest is the third class on bound 5 at `keep-cdc`, where a cap
makes a bare "No." opening more common, 3 of 10 in round 136's edit already,
and the cause the record does not establish is what fills the remaining
words. A second-class rejection, the factor near 0.85, would come from opus
not reading the cold question as a feasibility question at all; round 136's
edit restructured every cold answer around a verdict, so I give that little
weight. I give the first class almost none.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#438]: https://github.com/JordanMPDS/laconic/issues/438
[#500]: https://github.com/JordanMPDS/laconic/issues/500
