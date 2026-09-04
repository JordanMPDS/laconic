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

## Result

_To be filled in by the batch._

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#166]: https://github.com/JordanMPDS/laconic/issues/166
