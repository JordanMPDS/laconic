# Round 50: the check that fires before the tool call

**Registration. Nothing below the results line has been computed.** This file,
the edit, the regenerated `rules/dist/*.md` and the scoring code are committed
in the same commit, before any generation, following [round 38](round-38.md),
[round 47](round-47.md), [round 48](round-48.md) and [round 49](round-49.md).

## The hypothesis

> Editing `rules/laconic.md:7-10` — adding a check that fires before a tool
> call rather than before sending — should move the **edit rate** on
> `conditional`/sonnet **down**, against this round's own interleaved control.

Two bounds, registered here and scored by the same code:

- **An answer that did not edit must still name the defect.** The archive reads
  215 of 215 on sonnet ([`volunteered-trap-116.md`](volunteered-trap-116.md)),
  so the number to beat comes from this round's control.
- **The reading rate must not fall.** `conditional` hands the model two files
  and hides its one fact inside one of them.

## The edit

```diff
-Two checks before sending:
+One check before acting, and two before sending:

+1. Does answering this require changing anything? A question asks for an
+   answer, not a work product. Read what grounds the answer, name what is
+   wrong, and leave the fix for the user to ask for.
-1. What is the smallest set of claims that fully answers this?
-2. Is anything here something the user did not ask for?
+2. What is the smallest set of claims that fully answers this?
+3. Is anything here something the user did not ask for?
```

It sits above the `<!-- level:lite -->` marker, so it reaches all three slices.
That is the placement [#116] asks for — its own suggested table gives the
behaviour a row at every level — and it is what the section headers already
encode, per the rule that where a rule lives outranks what it says about where
it lives.

**Every clause of the new check maps to exactly one registered quantity, and
this is the whole reason it is worded the way it is.**

| clause | quantity |
|---|---|
| "leave the fix for the user to ask for" | the target: `edited` |
| "name what is wrong" | the bound: `locates_defect` in the non-editing stratum |
| "Read what grounds the answer" | the bound: the reading rate |

The second and third clauses are not padding and they are not hedging. A check
reading only "do not do the work" wins the target trivially by making the model
do nothing at all, and on this benchmark that failure would score as a triumph
twice over: it would take the edit rate to zero, and — because an answer that
edits runs 45 median words against 144 — it would also read as excellent
compression on every length metric the loop has ([#209]). The clauses are the
edit refusing the two cheap wins in advance.

## Why this issue, and why now

[#116] reports a question answered with a work product: the model confirmed the
user's understanding and then started running analysis to substantiate it, and
the user's reply was *"you dont need to do it i didnt ask for that"*. The prose
was terse; the behaviour was not.

The issue has been uninstrumented for most of its life, and the four attempts
to instrument it are worth stating because they bound what this round can
claim:

| attempt | result |
|---|---|
| [`volunteered-work.md`](volunteered-work.md) | `conditional` is the only case in a 5,557-run archive that exhibits it, at 39 of 80 |
| [`quota-merge-pilot.md`](quota-merge-pilot.md) | a purpose-built case grades cleanly and elicits nothing: 0 of 10 |
| [`conditional-retrap.md`](conditional-retrap.md) | `conditional`'s judged trap disagrees with itself on 1 verdict in 8, so it cannot be promoted |
| [`volunteered-trap-116.md`](volunteered-trap-116.md) | two deterministic counters, 85 of 85 hits genuine, neither reading the judged trap |

The fourth is the instrument this round spends. It is scorable on a
`rule-adherence` case for the reason recorded there and in `evals/CRITERIA.md`:
the prohibition is about criteria that restate the rules the treatment was
handed, and neither counter reads the criterion. One reads a tool list; the
other reads a fact only `db.js` supplies.

## Design

**Both sides generated simultaneously, 120 runs each.** The control runs from a
`master` worktree and the edit from this branch, writing into two snapshots,
per round 38. A count target takes its registered baseline from the round's own
control and never from a prior snapshot — round 31 registered 46 arrows off a
three-day-old control whose matched replacement read 31.

**120 a side is the size the instrument asked for, and it was chosen before the
round rather than after.** From
[`volunteered-trap-116.md`](volunteered-trap-116.md): a binary rate at 35% is
expensive to move detectably, and halving it to 17.5% is detected 35% of the
time at 40 runs a side, 51% at 60, and about 80% at 120. A round that opened at
40 and read a null would have measured very little.

```sh
# edit side, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 120 \
  --cases conditional --concurrency 2 \
  --snapshot evals/snapshots/loop/round-50-edit.json

# control side, from a master worktree, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps 120 \
  --cases conditional --concurrency 2 \
  --snapshot <abs path>/evals/snapshots/loop/round-50-control.json
```

**No judging is bought.** Both counters are deterministic, so the scoped batch
costs 240 generations and nothing else. That is the standing buy sequence: score
the cheap target first, and buy the round-wide arm and its judgments only for an
edit that survives it.

## Scoring

```sh
python3 evals/pilot/score_volunteered.py \
  evals/snapshots/loop/round-50-edit.json \
  --against evals/snapshots/loop/round-50-control.json
```

The target accepts on a fall at p < 0.05, two-sided. Either bound falling at
p < 0.05 rejects the round whatever the target did — the same shape as the
fatal counters, which reject an edit that fixes two cases and breaks a third.

Five regression tests in `tests/test_bench.py` cover the comparison, including
the two ways a round could win the target by cheating: a batch that stopped
reading the fixture and a batch that stopped naming the defect each have to trip
their bound.

## What this round cannot establish

- **One case, one model.** `conditional` is the only case in the archive that
  exhibits the behaviour, and a rate measured on it transfers nowhere by itself.
  Haiku has never edited in 180 runs and is not in scope.
- **The closed-confirmation half of [#116] is untouched.**
  [`question-shape.md`](question-shape.md) split the issue's class in two, and
  this round is the advisory interrogative only. The user's own report was a
  closed question deep in a session, which no single-turn case reproduces.
- **Recall on the editing stratum is 73%**, so every editing-side rate is a
  floor. The floor is lower on exactly the side the target measures, which
  makes the target conservative rather than flattering.
- **A pass here is not an accept.** The round-wide fatal counters have not been
  bought, and step 8's replication has not been run. Both are conditional on
  this batch.

---

## Results

*Not yet computed. Generation had not started when this file was committed.*

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#209]: https://github.com/JordanMPDS/laconic/issues/209
