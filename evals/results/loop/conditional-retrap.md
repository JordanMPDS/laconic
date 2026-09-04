# Re-trapping `conditional`: can the clause that makes it ungradeable be removed?

**Registration. No number under "Result" has been computed.** Committed before
the pass runs.

## Why this is the cheapest thing left for [#116]

[`volunteered-work-cases.md`](volunteered-work-cases.md) records four case
designs for [#116] and three withdrawals. Question form, reading rate and defect
kind were each tested and eliminated as the property that makes a model answer a
question by editing the file. **`conditional` remains the only case that produces
the behaviour**, at 39 of 80 in a matched batch, and every purpose-built
replacement reads 0 or 1 in 10 to 50.

But `conditional` grades `rule-adherence`, and per
[`CRITERIA.md`](../../CRITERIA.md) that supports *nothing in either direction* —
it is the treatment arm graded against the text it was handed. So the one case
that carries the behaviour is the one case whose verdicts cannot be used.

**It is marked `rule-adherence` for one clause.** From `CRITERIA.md`:

> `conditional` is marked `rule-adherence` too, on the mixed half: naming the
> connection leak is task-derived, but its fail condition includes the arrow
> prohibition, and its scenario reproduces the worked OOM example inside
> `rules/laconic.md` with the domain swapped.

And [`volunteered-work.md`](volunteered-work.md) measured what that clause does:
across **34 failures, not one** judge reason cited it. Every failure was on the
fixture-derived half — the advice given unqualified, or the `withClient` leak
never named.

## What is being tested

The clause to remove is the last one:

> ...Fails when the condition is dropped, when only one branch is given as
> unqualified advice, ~~or when the conditional is collapsed into a symbol such
> as `waiting climbing -> raise max`~~.

The remaining trap grades two facts, both from the fixture: the advice stays
conditional, and the leak is named.

> **Hypothesis:** re-judging the 80 stored `conditional` runs under the shortened
> trap moves no verdict beyond the judge's disagreement with itself on identical
> text.

**Falsifier, registered before the pass:** the paired pass rates differing at
p < 0.05 on an exact McNemar test. That would mean the clause is load-bearing
after all and the case cannot be re-graded without invalidating what its stored
verdicts support.

**Registered secondary:** the direction of any flips. A `fail -> pass` flip whose
original reason cited the arrow or a symbol is the clause doing work; a flip in
either direction with an unrelated reason is judge noise. [#212] puts the first
set at zero of 34, so any such flip is news.

## How, without touching the shipped case

The shortened trap lives in a shadow cases directory outside the repository, so
`evals/cases/conditional/expect.json` is unchanged until the result justifies
changing it. `--allow-case-change` is required and is exactly what it is for:
the criteria genuinely differ, and the flag stamps that into the output, which
will carry its own `criteria_cksum`.

```sh
python3 evals/bench/judge.py \
  --results evals/snapshots/loop/volunteered-work-conditional.json \
  --cases-dir <shadow> --cases conditional --allow-case-change --judge-all \
  --jobs 6 --out evals/snapshots/loop/conditional-retrap-judgments.json
```

80 judgments on runs that already exist. No generation.

**If the falsifier does not fire**, `conditional` is re-graded `quality`, the
original judgments are kept as the superseded grading following
`round-01-judgments.json`'s precedent, and [#116] has an instrument at
39-of-80 sensitivity with no new fixture and no new prompt.

**No rule edit is proposed either way.**

## Result

_To be filled in by the pass._

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#212]: https://github.com/JordanMPDS/laconic/pull/212
