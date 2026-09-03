# Round 36: the rule does not decay, and it has nothing to decay from

> **Partially corrected 2026-09-03 by round 40, and the headline is not the part
> that moves.** The closing-offer result — no decay, the movement running the
> other way, and laconic reading 0 of 125 turn-responses — is a rate on a rule
> holding, and nothing since has disturbed it. What does not survive is the
> unregistered second result below, the replication of round 35's word-count
> inflation at +38.4%. This round ran `repeat` delivery, re-appending the whole
> rule slice on every turn. Round 40's control batch carries these two cells at
> 10 reps under `--turn-delivery plugin` and the same rules, and computed from
> `round-40-control.json` the laconic medians read **284 words cold and 134.5 at
> turn 5** — a 53% fall where this round measured a 38% rise. `cold-service` is
> one turn, so delivery cannot reach it, which makes it the internal control:
> 263 against 284 is between-batch variation. Two families reversing together is
> the same finding twice rather than two findings, and what round 35 and this
> round replicated was a property of the delivery mode. See
> [`round-40.md`](round-40.md) and [`turn-delivery.md`](turn-delivery.md).

**This round proposes no rule edit.** It answers [#113]'s question — does the
no-closing-offers rule break down as a session goes on — and the answer is no, in
a direction the issue did not anticipate.

It also reproduces round 35's mechanism on a family that shares nothing with
round 35 except the harness.

## The question

[#113] reports a `lite` rule breaking on one turn and holding on the next, same
level, same session, adjacent turns, same request shape, and argues the binary
signal is worth more than the length one it accompanies:

> word count is a judgment call — two readers can reasonably disagree about
> whether 600 words was right for a given question — whereas *"did the last
> sentence offer to do more work"* is binary and needs no interpretation.

[`closing-offers.md`](closing-offers.md) built that detector and could not answer
the drift question with it, because the only multi-turn corpus read 0 of 315 in
both arms. [`preamble.md`](preamble.md) then established why, and corrected an
earlier wrong explanation of it: **offers appear where the answer names something
buildable the model has not built, and vanish where the deliverable is the
answer.** So the family this round needed had to be design-shaped.

## The instrument

`cold-service` and `drift-service` share a fixture — a five-file Express service
with Postgres — and a **byte-identical final question**:

```
POST /orders has no idempotency. how would you add it? Don't edit anything.
```

`cold-service` asks it alone. `drift-service` asks it as turn 5, after four
design questions about the same code: account scoping on the routes, the
`deleted_at` column nothing reads, what `write()` does when the pool drops
mid-transaction, and request logging.

The four earlier turns are deliberately off what the trap grades, so the closed
question stays fresh. `Don't edit anything.` stays on every turn — CRITERIA.md
requires it so the diagnosis lands in the response rather than the diff, and
`preamble.md` measured that the clause costs the offer signal little.

25 reps a side, sonnet, both cases in one interleaved batch, 100 runs, 0 failed.

## The registered question

> Asking the same design question at turn 5 instead of turn 1, with four of the
> model's own design answers in between, the closing-offer rate should rise if
> the `lite` rule decays within a session as [#113] reports. A flat rate is
> evidence for [#113]'s own alternative — that the flicker is turn-local rather
> than monotonic decay.

## Result: no decay, and the movement runs the other way

Closing-offer rate on the identical question:

| | asked cold | asked at turn 5 | |
|---|--:|--:|--:|
| baseline | 17/25 — **68.0%** | 5/25 — **20.0%** | Fisher **p = 0.0014** |
| laconic | 1/25 — 4.0% | 0/25 — 0.0% | p = 1.000 |

And by turn index inside `drift-service`:

| Arm | t1 | t2 | t3 | t4 | t5 |
|---|--:|--:|--:|--:|--:|
| baseline | 32.0% | 24.0% | 12.0% | 28.0% | 20.0% |
| **laconic** | **0.0%** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |

Turn 1 against turn 5 on baseline is p = 0.52 — no trend either way.

**Two things follow, and neither is the hypothesis.**

**Conversational depth suppresses the offer rather than eroding the rule.** The
same question that draws an offer 68% of the time asked cold draws one 20% of the
time at turn 5, p = 0.0014. A model four turns into a design discussion treats
the fifth question as part of that discussion rather than as a fresh consult to
be closed with an offer of work.

**Laconic has nothing to decay from.** Zero closing offers in 125 turn-responses
— every turn, every rep — and one in 25 cold. A rule that is never broken cannot
break down as the session lengthens, so [#113]'s drift question is not answerable
on this arm because the phenomenon is absent, not because the instrument is blind.

That was checked rather than assumed. The laconic responses end on substance:

> …the sketch above does the latter, which is simplest but hides the mismatch.

against baseline's:

> Want me to implement this (the migration, a `db.transaction()` helper, and the
> updated handler)?

## The largest arm separation the loop has measured

`cold-service` is a matched interleaved batch, one CLI, one day:

| | closing offers | rate |
|---|--:|--:|
| baseline | 17 / 25 | **68.0%** |
| **laconic** | **1 / 25** | **4.0%** |

Fisher **p < 0.0001**. On `drift-service`, 5/25 against 0/25, p = 0.0502.

The archive reads this contrast at 25.9% against 5.9%
([`closing-offers.md`](closing-offers.md)); a task built to invite the behaviour
reads it at 68.0% against 4.0%. The direction and the ordering are the same and
the magnitude is much larger, which is what a properly powered version of an
archive result should look like.

## Round 35 reproduces on a family that shares nothing with it

Not registered, and the stronger result for it. Median words on the graded turn:

| | cold | turn 5 | shift |
|---|--:|--:|--:|
| baseline | 405 | 542 | **+33.8%** |
| laconic | 263 | 364 | **+38.4%** |

Round 35 measured **+30.8%** and **+36.8%** for the same manipulation. Rep-paired
here, the turn-5 answer is longer in **45 of 50** pairs, two-sided exact
**p < 0.00001**.

Round 35 ran three analysis documents with closed confirmation questions.
This ran one code fixture with open design questions. Different cases, different
fixture, different question type, different trap — and the accumulated-own-output
effect lands within three points of the original. **That is the first independent
replication of a mechanism in this loop's history**, and it is worth more than
the round's registered question.

## Checks

Traps grade **100 of 100**, both arms, both cases, on a criterion shared byte for
byte between them. Four turns of prior design discussion made the idempotency
question neither easier nor harder, and the extra words at turn 5 were not buying
correctness.

99 of 100 runs called a tool. Preamble reads **0 of 100** in both arms, which is
what [`preamble.md`](preamble.md) predicts for a task whose answers are designs
rather than walkthroughs.

The judging pass stopped once on an outage at 44 of 100, recording 17 judgments
as failed rather than as verdicts. Re-running the same command retried exactly
those, which is the resume path working as documented.

100 generations for `cold-service` plus 125 for `drift-service`, 100 judgments,
0 generation failures, $19.29.

## What this leaves for [#113]

The issue's length half is untouched — nothing here measures whether answers grow
over a session, only whether the ceremony rule holds, and it holds completely.

Its binary-signal argument is vindicated in an unexpected way: the signal is
clean enough to show that **there is no decay to detect on the treatment arm**,
which no amount of word counting could have established.

What remains unexplained is the *original report* — a closing offer on one turn
and not the adjacent one, at `full`, in a real session. Nothing in 125
turn-responses reproduces it. The difference between that session and this
instrument is the same one [`preamble.md`](preamble.md) named: a real session
interleaves work with questions, and every turn here forbids editing.

[#113]: https://github.com/JordanMPDS/laconic/issues/113
