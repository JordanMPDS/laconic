# Round 43: the extra 180 words buy nothing, on a comparison at its ceiling

**The registration below was committed in `d77769d`, before the pass ran.** The
result section is the only thing added afterwards.

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

## Result: 120 of 120, both arms, both depths

| arm | turn 1 (`confirm-*`) | turn 5 (`deep-*`) | median words at turn 5 |
|---|--:|--:|--:|
| baseline | **30/30** | **30/30** | 210.5 |
| laconic | **30/30** | **30/30** | 30.5 |

Every one of the six cells is 10 of 10. No judgment came back `not_exercised`,
and no judge call failed.

**The registered falsifier did not fire.** Baseline's turn-5 pass rate does not
exceed laconic's: 30/30 against 30/30, two-sided Fisher p = 1.0. Baseline spends
180 more words per answer at turn 5 and the judge cannot tell the difference.

The three secondary readings, all registered above:

1. **Each arm against itself.** Baseline 30/30 to 30/30 and laconic 30/30 to
   30/30, p = 1.0 both. Neither arm falls with depth.
2. **The arms at turn 1**, the internal control: 30/30 against 30/30, p = 1.0.
3. **The failure mode.** There are no failures to read.

## What this can and cannot claim, because it is a ceiling

A comparison at 100% on both sides detects a fall and nothing else, which is
[#94]'s level-versus-variance distinction. It is worth saying exactly how large a
fall it could have seen. Against a baseline at 30/30:

| laconic | Fisher p |
|---|--:|
| 28/30 | 0.4915 |
| 26/30 | 0.1124 |
| 25/30 | 0.0522 |
| **24/30** | **0.0237** |

So this round rules out a laconic deficit of **six failures in thirty, a 20%
share of correctness**, and cannot see anything smaller. In particular it could
not have detected 28/30 — which is precisely what
[`round-41.md`](round-41.md) measured for the laconic arm on these same cells at
this same revision and delivery.

**Stated at the strength the evidence supports: laconic's 85% compression at
depth does not cost a fifth of correctness.** It is not evidence that the cost is
exactly zero, and this instrument cannot become that evidence by adding reps —
the constraint is that baseline has no headroom to fall from either.

## An unregistered replication, worth recording

Round 41 read the laconic arm at turn 5 as 28/30 on `round-40-control.json`.
This round reads 30/30 on `round-42.json`. Same cells, same `rules_cksum`
136269960, same `--turn-delivery plugin`, different batch three days apart.

Two verdicts of thirty is inside the judge's disagreement with itself on
identical text, which this loop puts at 5 to 10%. So the two readings agree, and
**round 43 is an independent replication of round 41's laconic-at-depth quality
that also carries the baseline arm round 41 lacked.**

## What this settles for round 42

Round 42's result was that depth inflates an unruled answer by +51.4% while
laconic runs −68.9% against it, and its own limits section named the missing
piece: whether baseline's extra words carry anything. They do not, down to the
resolution stated above.

The pair now reads: **at turn 5 an unruled model writes seven times as much and
answers the same question no better.** That is the strongest statement this loop
has made about the plugin's multi-turn behaviour, and it rests on a length
measurement with p = 5e-06 and a quality comparison at its ceiling — the second
being the weaker half, which is why the bound is written out above rather than
rounded to "no difference".

## Cost

120 judgments, 0 failed, $3.25. No generation. `rules_cksum` and `cases_cksum`
are round 42's, unchanged, because nothing was generated.

## Ledger

No rule edit. Recorded in [`LEDGER.md`](LEDGER.md).

[#94]: https://github.com/JordanMPDS/laconic/issues/94
