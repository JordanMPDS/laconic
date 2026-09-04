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

## Result: the falsifier did not fire, and the re-grade is refused anyway

| grading | pass | flips vs original | McNemar |
|---|--:|--:|--:|
| original (long trap) | 46 / 80 | — | — |
| **short trap** (clause removed) | 40 / 80 | 18 / 80 (22.5%) | p = 0.2379 |
| **same trap, re-judged** (control) | 48 / 80 | 10 / 80 (**12.5%**) | p = 0.7539 |

**The registered falsifier did not fire.** The short trap's pass rate does not
differ from the original's at p < 0.05, and the registered secondary is clean:
of 18 flips, none has an original reason that turns on the arrow clause. Reading
them, they are all about the *other* half — whether an unqualified "no, fix the
leak" counts as conditional advice. The same response draws *"keeps the advice
conditional"* from one call and *"gives an unqualified single-branch verdict"*
from another.

**The control is why the re-grade is refused.** Re-judging the same 80 runs under
the **unchanged** trap moves 10 verdicts. So `conditional`'s criterion disagrees
with itself on **1 verdict in 8** — above the 5-10% band this loop assumes
everywhere it decides not to re-judge something.

At that noise level the registered null is uninformative. "No verdict moves" is
not a claim this instrument can support, because verdicts move when nothing
changes at all. Short against control is 16 flips at **p = 0.0768**, 12 one way
and 4 the other, which is the short trap looking slightly stricter and not
resolvable at n = 80.

All three gradings agree on **58 of 80** runs, 72.5%.

## Why that forbids the re-grade rather than merely complicating it

`quality` verdicts feed `quality_fails`, which is one of the four fatal counters
and rejects a round on its own. Promoting a criterion with 12.5% self-
disagreement into that counter would put a coin-flip cell behind a fatal gate —
the failure [#94] and the per-cell rate screen exist to prevent, arriving through
the front door.

So `conditional` stays `rule-adherence`, `evals/cases/conditional/expect.json` is
unchanged, and the shadow trap is discarded. Running the test in a shadow
directory is what made that free.

## The finding worth keeping

**`conditional`'s trap disagrees with itself on 1 verdict in 8, and the
disagreement is on its load-bearing half.** Not on the arrow clause, which is
inert — [#212] found it cited in 0 of 34 failures and this round finds it in 0 of
18 flips.

The criterion asks for advice that "stays conditional", and the judge cannot
apply that consistently to a response that answers the question correctly in one
branch. That is a criterion problem, not a judge problem: *"raise the pool only
if the connections are genuinely concurrent"* and *"no, this is a leak"* are both
defensible readings of the fixture, and the trap does not say which it wants when
the evidence rules one branch out.

**Disclosure, and it is the sharpest form of the warning already on this case:**
across three judgings of byte-identical text the laconic arm reads **15, 11 and
18 of 40**. Any arm claim from `conditional` is reading a 7-verdict swing that
the text did not cause.

## What this leaves for [#116]

No instrument, and now a clearer specification for one. A case for [#116] needs a
criterion the judge applies stably.

> **The obvious guess about what makes one stable was tested and does not
> hold.** This document originally continued "which means a trap whose pass
> condition is a fact present or absent in the response, not a judgement about
> how advice is framed". [`judge-self-disagreement.md`](judge-self-disagreement.md)
> re-judged four cells and the two shapes interleave: `design-alerting` 26.8%
> (framing), `design-realtime` 18.2% (fact), `conditional` 12.5% (framing),
> `design-cache` 0.0% (fact). What survives is that stability is a property of
> the criterion rather than of the judge — one cell moved 0 of 55 — so a noisy
> criterion can be rewritten, by some means not yet identified. `conditional` elicits the behaviour and cannot grade it; the three cases
in [`volunteered-work-cases.md`](volunteered-work-cases.md) grade cleanly and do
not elicit it. Nothing yet does both.

**No rule edit is proposed, and none may be.**

## Cost

160 judgments, 0 failed, about $6.50: 80 for the registered pass and 80 for the
control it turned out to need. No generation.

[#94]: https://github.com/JordanMPDS/laconic/issues/94

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#212]: https://github.com/JordanMPDS/laconic/pull/212
