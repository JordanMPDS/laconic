# Four case designs for [#116], and why `conditional` is still the only one

**No new case ships from this.** Three purpose-built cases were authored and
withdrawn. What they establish is a negative worth having: the property that
makes a model answer a question by editing the file is not any of the three
things that looked most likely, and the instrument [#116] needs is probably
`conditional` itself with a different trap.

## The target

[#116] reports a question answered correctly and then substantiated with work
nobody asked for. [`volunteered-work.md`](volunteered-work.md) found the
behaviour already in the suite: every `Edit` call across 5,557 archived runs is
on `conditional`, at **39 of 80** in a matched batch. But `conditional` grades
`rule-adherence`, so no rule edit may be proposed from it, and the issue has been
uninstrumented since it was filed.

## What was tried

| case | shape | reads | edits |
|---|---|--:|--:|
| `conditional` | names files, live problem, advisory question | 40/40 | **39 / 80** |
| `quota-merge` | names identifiers, design choice, closed confirmation | 35/40 | 0 / 50 |
| `quota-advice` | names identifiers, design choice, advisory question | 9/40 | 0 / 40 |
| `queue-lag` v1 | names files, live problem, advisory, **design-tradeoff defect** | 10/10 | 0 / 10 |
| `queue-lag` v2 | names files, live problem, advisory, **mechanical defect** | 10/10 | 1 / 10 |

Three hypotheses were tested in that order and each was eliminated.

**1. The question form.** `quota-merge` asks a closed confirmation; a closed
confirmation invites confirmation. Its pair `quota-advice` asked the same thing
advisorily — and read the fixture 9 times in 40 against 35 in 40, Fisher
**p = 5.2e-09**. That is a real finding about reading, recorded in
[`question-shape.md`](question-shape.md), but it made the edit comparison void
rather than answering it: a model that never opens a file cannot edit it.

**2. Reading.** `queue-lag` copied `conditional`'s prompt shape exactly — names
both files, frames a live incident, then asks advisorily — and **reading went to
10 of 10**. That confirms the shape diagnosis. Edits stayed at 0.

**3. The kind of defect.** `conditional`'s editing runs are applying a textbook
fix: of 39, **22 open with "Fixed" or "Applied"** and 12 name `finally`
explicitly. `queue-lag` v1's defect was a design tradeoff with a stated
invariant, which a model reasons about rather than acts on. v2 swapped it for a
mechanical leak — a session closed only on the success path — the same shape as
`conditional`'s. **It read 1 of 10.** Against v1 that is p = 1.0, against
`quota-merge` pooled p = 0.167, and it remains significantly below `conditional`
at **p = 0.038**.

So the mechanical-defect theory is not supported either.

## What also went wrong, and is worth recording

Both `queue-lag` fixtures graded **10 of 10 in both arms**. A case at the ceiling
detects a fall and not a rise ([#94]), so even had it elicited edits it could not
have compared arms on quality. Writing a trap that the model passes every time is
easy and it was not noticed until the pilot — which is the argument for piloting
every new case at 5 reps a side before it enters the suite, as round 32 did.

`quota-advice` and `queue-lag` are both withdrawn. A case that reads its fixture
in 9 of 40 runs cannot grade fixture-derived content; a case saturated in both
arms cannot compare them. Neither earns its place in every future round's bill.
`quota-merge` stays: it reads 35 of 40 and grades 9 of 10.

All snapshots are kept, because a withdrawn case's data is the record of why it
was withdrawn.

## Where this leaves [#116]

**Stop rebuilding `conditional` and re-trap it.**

[`volunteered-work.md`](volunteered-work.md) already recorded the opening:
`conditional` is marked `rule-adherence` because its fail condition includes the
arrow prohibition, and across **34 failures not one** judge reason cited it.
Every failure was on the fixture-derived half — the advice given unqualified, or
the `withClient` leak never named.

So removing that clause is testable the way [#209] and `turns` were: re-judge the
stored `conditional` verdicts under the shortened trap and confirm none moves. If
none does, the case can be re-graded `quality` without invalidating anything, and
[#116] gets an instrument at 39-of-80 sensitivity that needs no new fixture, no
new prompt, and no fourth guess about what elicits the behaviour.

That is the next unit. It is also the cheapest of everything tried here: it buys
judgments on runs that already exist.

## Cost

`queue-lag` two pilots, 20 generations and 20 judgments, about $2. The
`quota-advice` batches are costed in [`question-shape.md`](question-shape.md).

[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#209]: https://github.com/JordanMPDS/laconic/issues/209
