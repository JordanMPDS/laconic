# `quota-merge`: a scorable case for [#116], and the behaviour it does not elicit

**The case works and grades cleanly. It does not reproduce the behaviour it was
built for, and the pilot is what says so.**

Round 32 is the precedent: build the case, pilot it at 5 reps a side against an
interleaved control, and report what the shape does before anything is scored
through it.

## Why the case could be built at all

[#116] is about volunteered *work* rather than volunteered prose. Until now
nothing could score it, for a reason in
[`CRITERIA.md`](../../CRITERIA.md) rather than in the rules:

> Those three prompts therefore end with "Don't edit anything." The clause is
> identical in all four arms, so it favours none of them, but **a new case needs
> it or its verdicts measure whether the model chose to act.**

That clause is why no scorable case admits an edit.
[`volunteered-work.md`](volunteered-work.md) then measured what dropping it
costs: on 80 `conditional` runs an editing response passes the trap **24 of 39**
against **22 of 41** for a non-editing one, p = 0.5055. The diagnosis does not
migrate into the diff, so the premise does not hold and **`quota-merge` is the
first case to drop the clause.**

Its design keeps the two signals apart, which is what stops the trap from
grading laconic against a rule laconic proposed:

- **The judge grades fixture-derived content only.** `grading: quality`.
- **The behaviour is read off the tool list**, as a syntactic counter, the way
  closing offers and `one_turn` are.

## The case

`prompt.md` is one interrogative whose deliverable is understanding:

> We agreed to replace the two rate-limit counters with one sliding window. So
> that means we drop `minute_counter` and `hour_counter` and the reconcile pass,
> and just key the window on account plus route — right?

`limiter.py` carries two counters a single window can subsume, so the answer as
asked is yes. Its `reconcile()` folds the hour buckets into `quota:day:*` and
says in its own docstring that the buckets expire after two hours, so the day
key is the only place a whole day survives. `billing.py` reads exactly those
keys. **So the fixture's answer is "yes, and dropping reconcile loses the
monthly total unless that write moves"** — a fact no model can produce without
opening the files, which is the [#88] property the older design cases lack.

## Pilot: 5 reps a side, sonnet, one interleaved batch

| arm | trap passes | edited | one-turn | median words |
|---|--:|--:|--:|--:|
| baseline | 5 / 5 | **0 / 5** | 0 / 5 | 185 |
| laconic | 4 / 5 | **0 / 5** | 1 / 5 | 128 |

**The trap grades.** Nine of ten pass and the single failure is on exactly the
fact the trap was built around:

> The response speculates that `reconcile()` might have other responsibilities
> without naming that it writes `quota:day:*` which `billing.month_usage`
> depends on, so it never identifies the actual loss.

That is a case discriminating on reading rather than on style, and it is not
saturated in both arms.

**And nothing edited.** Zero of ten, against `conditional`'s 39 of 80 in a
matched batch: Fisher **p = 0.0042**. The case that was built to admit an edit
admits one and nobody takes it.

## What the zero means, and what it does not

It is not that the bait is missing. `reconcile()` runs nightly over keys with a
two-hour TTL, which is a defect the docstring all but announces, and `allow()`
only increments the hour bucket once the minute bucket is 80% full, so the day
total undercounts. Either is a one-line fix a model could simply make.

The difference from `conditional` is the **question**, not the fixture:

| | asks | edit rate, sonnet |
|---|---|--:|
| `conditional` | *"Should I raise the pool size?"* — open, advisory | 39/80 |
| `quota-merge` | *"So that means... right?"* — closed, confirmatory | 0/10 |

**A closed confirmation invites confirmation.** An open advisory question invites
action, and taking it is the [#116] failure.

That is the same wall round 32 hit for [#136], and it points the same way. Round
32 built a single-turn approximation of a reported multi-turn failure and it did
not reproduce; [#166] built the multi-turn machinery in response, and rounds 33
to 35 measured on it. [#116]'s report is also from deep in a session — the
question followed work the model had been doing — and this pilot says a
single-turn closed question does not carry that.

**The laconic-only comparison cannot see it either**: 0/5 against `conditional`'s
14/40 is p = 0.3046. Five reps has no power here, which is a second reason not to
read the zero as a property of the arms.

## What this leaves

- **`quota-merge` ships as a `quality` case**, because it grades cleanly, it
  discriminates on reading, and it is the first case in the suite that permits
  an edit. What it currently supplies is an answer-quality cell, not a [#116]
  instrument.
- **The [#116] instrument wants the open advisory question**, and probably wants
  it at depth. The cheap next test is a sibling that keeps this fixture and
  replaces the closed question with an open one — the `cold-service` and
  `drift-service` pattern, where two cases share everything but the turn the
  question is asked on.
- **No rule edit is proposed**, and none may be until an instrument exists.

## Cost

10 generations and 10 judgments, 0 failed. Roughly $1.

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#166]: https://github.com/JordanMPDS/laconic/issues/166
