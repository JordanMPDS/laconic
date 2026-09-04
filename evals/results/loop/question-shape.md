# Does the question shape decide whether the model volunteers work?

**Registration. No number under "Result" has been computed.** Committed before
the batch runs.

## What pointed here

[`quota-merge-pilot.md`](quota-merge-pilot.md) built the first case in the suite
that permits an edit, and it elicited none: **0 of 10**, against `conditional`'s
39 of 80 in a matched batch, Fisher p = 0.0042. The bait was not missing —
`reconcile()` runs nightly over keys with a two-hour TTL, and `allow()` only
increments the hour bucket once the minute bucket is 80% full, so the billing day
total undercounts. Either is a one-line fix sitting beside the question.

What differed was the question:

| | asks | edit rate, sonnet |
|---|---|--:|
| `conditional` | *"Should I raise the pool size?"* — open, advisory | 39/80 |
| `quota-merge` | *"So that means... right?"* — closed, confirmatory | 0/10 |

Those two also differ in fixture, domain and trap, so the comparison cannot
carry the claim. This round builds the pair that can.

## The design

`quota-advice` shares `quota-merge`'s **fixture byte for byte** and its **trap
byte for byte**, and differs only in the prompt. That is the `cold-service` and
`drift-service` pattern, which isolates turn depth the same way.

| | `quota-merge` | `quota-advice` |
|---|---|---|
| fixture | `limiter.py`, `billing.py` | identical |
| trap | fixture-derived, two facts | identical |
| grading | `quality` | `quality` |
| prompt | *"So that means we drop... — right?"* | *"Should we replace all that with one sliding window...?"* |

Anything the two do differently is the question shape, because nothing else
about them differs.

## The registered hypothesis

> Asking the same question about the same fixture in an open advisory form
> rather than a closed confirmatory one raises the rate at which the model edits
> the fixture instead of answering.

**Falsifier, registered before the batch:** the two cases not separating on edit
rate at p < 0.05, two-sided Fisher, pooled over both arms. That would say the
question shape is not what suppressed the behaviour in `quota-merge`, and would
send [#116]'s instrument back to the multi-turn machinery [#166] built for
[#136] rather than to a one-turn rewrite.

**Registered secondary, so it is not chosen afterwards:** whether
`quota-advice`'s trap grades at all. A byte-identical trap on a different
question can fail to fit — the trap says the answer "confirms that one sliding
window ... can replace both counters", and an advisory answer that recommends
against merging would fail it while being defensible. A pass rate near zero on
both arms means the trap does not transfer and the pair is not usable, whatever
the edit rate did.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 20 \
  --cases 'quota-merge,quota-advice' --concurrency 1 \
  --snapshot evals/snapshots/loop/question-shape.json
```

80 generations. The edit rate needs no judging, so it is scored first; the
secondary buys 40 judgments on `quota-advice` only, and only if the primary is
worth reporting. That is the standing stop-at-the-first-failing-step order.

**No rule edit is proposed.** This builds an instrument.

## Attempt 1: void, for a reason the pair was supposed to control

The batch ran clean — 80 generations, 0 failed — and the registered falsifier
fired at p = 1.0, both cases reading **0 of 40**. **That result may not be
reported as a negative,** because the second case never opened the fixture:

| case | ran a tool | names `quota:day` | edited |
|---|--:|--:|--:|
| `quota-merge` | 38 / 40 | 38 / 40 | 0 / 40 |
| `quota-advice` | **0 / 40** | **0 / 40** | 0 / 40 |

A model that never opens `limiter.py` cannot edit it, so `quota-advice`'s zero is
explained before the question shape is reached. The pair failed to isolate its
variable: changing the question also changed whether the fixture was read.

The cause is in the prompt, not the question shape. `quota-merge` names
`` `minute_counter` `` and `` `hour_counter` `` in backticks; attempt 1's
advisory prompt described them in prose — *"keeps two counters per account and
folds them into a day total"* — and the model answered from the description. One
response opens:

> Depends on why the two counters exist — if the nightly reconcile is patching
> drift from non-atomic increments across distributed nodes...

That is an answer from general practice, which is exactly what round 23 measured
as the axis that decides design-answer quality, and what [#46]'s earned-licence
edit exists to stop. It reappeared here at the level of prompt authoring: **a
question phrased in prose invites an answer from general practice; a question
that names identifiers invites a read.**

`quota-merge`'s 40 runs are unaffected and read normally. The batch cost $3.35
and is kept as the record of the defect.

## Attempt 2, registered with an added precondition

The advisory prompt now names the same identifiers, so reading is invited
equally and the two prompts differ only in interrogative form:

> `quota-merge`: ...So that means we drop `minute_counter` and `hour_counter`
> and the reconcile pass, and just key the window on account plus route — right?
>
> `quota-advice`: Our rate limiter keeps `minute_counter` and `hour_counter` per
> account and folds them into a day total in the reconcile pass. Should we
> replace all three with one sliding window keyed on account plus route?

**The hypothesis and the falsifier are unchanged.** Both cases are regenerated
into a fresh snapshot rather than resumed, because the case text changed and a
round built from two versions of a prompt is the [#69] failure.

**Added precondition, registered before the batch:** if the two cases' reading
rates differ by more than 20 percentage points, the comparison is void again and
is reported as void. A pair that does not read alike is not isolating the
question shape whatever its edit rates say.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 20 \
  --cases 'quota-merge,quota-advice' --concurrency 1 \
  --snapshot evals/snapshots/loop/question-shape-v2.json
```

## Attempt 2: void again, on the precondition registered to catch it

Naming the identifiers helped and did not come close to fixing it.

| | ran a tool | names `quota:day` | edited |
|---|--:|--:|--:|
| `quota-merge` (closed) | **35 / 40** (87.5%) | 35 / 40 | 0 / 40 |
| `quota-advice` (open) | **9 / 40** (22.5%) | 6 / 40 | 0 / 40 |

The registered precondition allowed a 20-point gap. **The gap is 65 points, so
the comparison is void and is reported as void.** The primary again reads 0
against 0 at p = 1.0, and again that number means nothing: neither case can edit
a file, and one of them barely opens one.

Naming the identifiers did move it — `quota-advice` went from 0 of 40 to 9 of 40
between attempts, Fisher **p = 0.0024** — so the prose-versus-identifier reading
was right about its direction and wrong about its size.

## The finding, unregistered and larger than the one registered

Two attempts have established something the round was not built to ask.

**Question form controls reading rate, at identical everything else.** Same
fixture, same trap, same identifiers, same arms, one interleaved batch — the two
prompts differ only in interrogative form:

| form | reads |
|---|--:|
| *"So that means we drop X and Y — right?"* | 35 / 40 |
| *"Should we replace X and Y with Z?"* | 9 / 40 |

Fisher **p = 5.2e-09**.

A closed confirmation sends the model to the source to check. An open advisory
question invites an answer from general practice — which is the axis round 23
measured as the one that decides design-answer quality, and which [#46]'s
earned-licence edit exists to close. This is the cleanest demonstration of it the
suite has, because nothing but the sentence form varies.

**And it is the binding constraint on a [#116] instrument, not the edit rate.**
The chain is: an open advisory question suppresses reading, and a model that
never opens the file cannot volunteer work on it. `quota-advice` reads 22.5% and
edits 0 of 40 against `conditional`'s 39 of 80, p = 3.0e-09.

## What this says the [#116] instrument should be

`conditional` is the only case that elicits the behaviour, and the three
attempts here isolate what it does that these do not: it names **files** rather
than identifiers (*"pool.log has the last hour and db.js is where it's
configured"*), it frames a **live problem** rather than a design choice, and only
then does it ask advisorily. Two of those three were missing here.

That points at a conclusion this round did not expect: **the case [#116] needs
may already exist, and what it needs is a different trap.**
[`volunteered-work.md`](volunteered-work.md) recorded that `conditional` is
marked `rule-adherence` because its fail condition includes the arrow
prohibition — and that across **34 failures not one** judge reason cited it.
Every failure was on the fixture-derived half. A `conditional`-shaped case whose
trap drops that clause would be `quality`-gradeable, would elicit edits at the
35–62% already measured, and would need no new fixture.

That is the next unit, and it is cheaper than a fourth prompt variant.

## What ships, and what does not

- **`quota-advice` is withdrawn.** A case that reads its fixture in 9 of 40 runs
  cannot grade fixture-derived content, so it has no business in the suite
  whatever it was built to test. The case count returns to 37.
- **`quota-merge` stays**, unaffected: 35 of 40 reading, and its numbers here
  replicate the pilot.
- **Both snapshots are kept**, because a withdrawn case's data is the record of
  why it was withdrawn.
- **No rule edit is proposed.**

## Cost

Attempt 1 $3.35, attempt 2 $3.64, no judging bought — the primary failed its
precondition before the secondary was due, per the stop-at-the-first-failing-step
order. One outage stopped attempt 2 at 66 of 80 on the eight-consecutive-failure
guard and the resume regenerated exactly the 14 missing keys.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#166]: https://github.com/JordanMPDS/laconic/issues/166
