# Round 43: does an unruled arm's extra 180 words at depth buy anything?

**Registration. No verdict below this line has been computed** — this file is
committed before the judging pass runs, so the hypothesis provably predates the
numbers.

**This round proposes no rule edit.** It closes the one hole
[`round-42.md`](round-42.md) left open, on the snapshot round 42 already
generated. No generation is bought.

## What round 42 established, and what it could not say

Round 42 generated `baseline` beside `laconic` at depth under
`--turn-delivery plugin` and found the arms moving in opposite directions:

| arm | turn 1 (`confirm-*`) | turn 5 (`deep-*`) | change |
|---|--:|--:|--:|
| baseline | 139.0 | 210.5 | +51.4% |
| laconic | 98.0 | 30.5 | −68.9% |

At turn 5 laconic is 0.11 to 0.18 of baseline — a 180-word gap on the median
cell. Round 42 bought no judging, so **it cannot say whether those 180 words
carry anything.** Its own "what this round did not buy" section names this as
the limit, and it is the difference between two claims the plugin would like to
make:

- **The compression at depth is free.** Laconic answers the same question
  correctly in a seventh of the words.
- **The compression at depth costs correctness.** The gate would then be
  measuring a harm the plugin is causing, and 30.5 median words at turn 5 is too
  few.

Round 41 rules this out on the laconic side alone: on these same cells at this
same revision and delivery it grades 30/30 at turn 1 and 28/30 at turn 5,
p = 0.4915, so laconic does not fall with depth *against itself*. What no batch
has is **an unruled arm graded beside it**, which is the comparison that says
whether the words are doing work.

## The registered hypothesis

> Judging both arms of `round-42.json` will show baseline's turn-5 pass rate no
> higher than laconic's, on the identical final question.

**Falsifier, registered before the pass:** baseline's turn-5 pass rate exceeding
laconic's at p < 0.05 on a two-sided Fisher exact test. That would mean laconic's
85% compression at depth is bought with correctness, and it would make the
turn-5 behaviour a defect in `rules/laconic.md` rather than the plugin working.

Three secondary readings, registered here so they are not chosen afterwards:

1. **Each arm against itself, turn 1 to turn 5.** Round 41 read laconic 30/30 to
   28/30. Whether baseline holds across depth is unmeasured, and a baseline that
   *falls* would say the depth manipulation costs an unruled model something.
2. **The arms at turn 1**, which is the internal control. Both arms answer the
   same question from the same fixture with no depth, so a difference there is
   about the rules rather than about depth.
3. **The failure mode, read by hand rather than counted.** Round 41 found every
   edit-side failure was a correct answer missing a required clause, one of them
   the single word *Yes.* Whether laconic's turn-5 failures look like that
   matters more than the count.

## What is bought

```sh
python3 evals/bench/judge.py --results evals/snapshots/loop/round-42.json \
  --judge-all --jobs 6 \
  --out evals/snapshots/loop/round-43-judgments.json
```

120 judgments, both arms, `--judge-all` so the coverage matches round 41's on the
same cells — the skill requires it when a snapshot will be compared against
another. Sonnet judge, per the standing rule that a judge is not the hypothesis.
No generation, so `rules_cksum` and `cases_cksum` are round 42's unchanged.

**This round cannot be re-run to a different answer.** There is one snapshot, one
pass, and the falsifier is written above.

## Result

_To be filled in by the pass._
