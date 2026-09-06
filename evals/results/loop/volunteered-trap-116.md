# The [#116] fact trap: `conditional` can carry a score after all

**No generation calls.** Every number below is computed from committed
snapshots and from 158 archived responses read by hand.

## What was blocking

[`conditional-retrap.md`](conditional-retrap.md) left [#116] with a stated
impasse and a specification for the way out:

> - **`conditional` elicits the behaviour and cannot grade it** — 39 of 80
>   edits, 12.5% criterion noise.
> - **The three purpose-built cases grade cleanly and do not elicit it** —
>   `quota-merge` 9/10 grading, 0 of 50 edits; the other two withdrawn.
> - **Nothing yet does both.**
>
> What is needed is a trap whose pass condition is a **fact present or absent
> in the response** — a named identifier, a stated consequence — rather than a
> judgement about how advice is framed.

This unit builds that trap and measures what it says. It is deterministic, so
it has no criterion noise to measure; what it has instead is a recall limit,
and the limit is not uniform across the strata it compares.

## The trap

`evals/cases/conditional/fixture/db.js` releases the client on the success path
only:

```js
async function withClient(fn) {
  const client = await pool.connect();
  const result = await fn(client);
  client.release();
  return result;
}
```

So a client is leaked whenever `fn` throws. That is the one fact the case
hides, and `prompt.md` does not contain it: the prompt names `db.js` and
`pool.log` and nothing inside either, so a response saying `fn` opened the
file.

`evals/pilot/score_volunteered.py` passes a response when a release token sits
within 120 characters of both a subject and a fault — where the subject is
`fn`, the callback, or a query the sentence says is failing. Nothing is
stripped: a rendered `} finally {` block is the answer as delivered.

**The distinction the trap draws is between a diagnosis and a checklist.**
These two are both about releases and errors, and only the first passes:

| | verdict |
|---|---|
| "The bug is in `withClient` (db.js:11-16): if `fn(client)` throws, `client.release()` on line 14 never runs." | passes |
| "Check for places where `client.release()` isn't being called: anywhere you call `pool.connect()` directly, or error paths that don't release." | fails |

The second is advice recalled from general practice, and a model that never
opened `db.js` can produce it. That is the same line
[`design-discrimination.md`](design-discrimination.md) draws between a derived
answer and a recalled one, applied to a trap.

**It reads `text` and never `artifacts`.** A response whose explanation is in
the diff has not explained anything to the person who asked a question, which
is exactly what [#116] reports. `metrics.graded_text` exists for the opposite
case and `conditional` does not opt into it.

## Validation: 158 responses, read by hand

The corpus is every `conditional` run in the archive — 2,354 runs, 1,273
distinct responses. Samples are seeded and drawn from distinct responses, since
carried arms repeat text.

| | responses | hits | precision | recall |
|---|--:|--:|--:|--:|
| development | 118 | 63 | **63 / 63** | 63 / 67 = 94% |
| out of sample | 40 | 22 | **22 / 22** | 22 / 25 = 88% |

**85 of 85 hits are genuine, in and out of sample.** That clears the bar
[#155]'s restatement metric could not at 55.3% and matches
[`closing-offers.md`](closing-offers.md)'s 30 of 30 — and for the same reason:
the pass condition is an identifier rather than a judgement.

**The first draft of the pattern scored 20 of 30, and the ten misses share one
shape.** Keying on `finally` or on any negated release admits the checklist
answers above — "Error handling that bypasses release", "error paths that skip
the `client.release()`" — including four that name the mechanism while
explicitly clearing `withClient` of it. Requiring the fixture's own subject is
what excludes them.

**Admitting a bare `query` costs 9 false positives**, all of the form "are
queries slow? … are connections being released?". The fault has to attach to
the query — a *failing* query — rather than sit near it. That seam is a
regression test.

### Recall is not uniform, and the direction matters

Out of sample, by stratum:

| stratum | gold | detector | recall |
|---|--:|--:|--:|
| the response edited `db.js` | 11 / 20 | 8 | **8 / 11 = 73%** |
| the response only answered | 14 / 20 | 14 | **14 / 14 = 100%** |

All three misses are the same sentence written without the fixture's subject —
"once callers reliably release clients on error", "a leak from unreleased
clients on error". Adding "callers" as a subject catches them and readmits the
checklist answers, so the miss is kept.

**This matters because the two strata are what the trap is used to compare.**
The first pattern read 21.2% against 74.5%; widening it to the faulting-query
form moved only the editing side, to 33.9%. A rate from this detector is a
floor, and the floor is lower on the side that edits. Every arm figure below is
reported with its hand-labelled correction beside it.

## Stability: nothing to measure, which is the point

`evals/CRITERIA.md` registered a prediction on 2026-09-04:

> A criterion whose pass condition is a named fact tends to reproduce; one
> asking whether an answer is *framed* correctly tends not to. Registered as a
> prediction and only weakly supported.

`conditional`'s judged trap is the framing case and re-judging the identical 80
runs under it moved **10 verdicts, 12.5%**. This trap is a regex over stored
text: re-running it moves nothing, by construction. The prediction's two ends
are now both instantiated on the same case.

**The two traps are also independent, which is why the fact trap adds
something.** Over the 80 judged runs of `volunteered-work-conditional.json`:

| | names the defect | does not |
|---|--:|--:|
| judged **pass** | 30 | 16 |
| judged **fail** | 22 | 9 |

Agreement 39 of 77, Fisher **p = 0.629**. Whether the advice stays conditional
and whether the reader is told what is broken are unrelated properties of these
responses.

## The rules' worked example does not drive it

`rules/laconic.md` carries a worked OOM answer that
[`conditional-homology-116.md`](conditional-homology-116.md) showed is this
case with the domain swapped — "a climbing curve means a leak", "a bigger limit
only delays the next kill". The laconic arm is handed it and the controls are
not, which is the standing objection to scoring anything on this case.

That batch generated a third tree with the example's domain swapped away, and
it can be re-scored here at no cost:

| laconic arm, sonnet, 40 runs | names the defect | edited |
|---|--:|--:|
| master rules | 33 / 40 (82.5%) | 8 / 40 |
| worked example's domain swapped | 29 / 40 (72.5%) | 14 / 40 |

Fisher **p = 0.422** on the fact rate. The example is not what puts the
diagnosis in the response, exactly as it was not what suppressed the editing
(p = 0.0120 for the arm gap with the homology removed).

## What the trap measures

**The harm [#116] reports, on the model that exhibits it.** Every archived
`conditional` run carrying a `tools` list, 580 of them:

| model | stratum | names the defect |
|---|---|--:|
| sonnet | edited `db.js` | **56 / 165 = 33.9%** |
| sonnet | only answered | **215 / 215 = 100%** |
| haiku | only answered (haiku has never edited) | 74 / 180 = 41.1% |
| opus | only answered | 20 / 20 |

Corrected by hand for the recall gap, on the labelled sonnet samples: **24 of
45 editing runs state the diagnosis against 36 of 36 that answered**, Fisher
p = 3.0e-07. The gap is about half what the raw detector reports and it does
not go away.

**Zero of 215 is the striking cell.** On sonnet, an answer that did not touch
the file has never once failed to say what was wrong. The failure is not
distributed across responses; it is confined to the ones that did the work.

In the one interleaved batch, 40 a side on the same day:

| arm | edited | names the defect |
|---|--:|--:|
| baseline | 25 / 40 (62.5%) | 24 / 40 (60.0%) |
| laconic | 14 / 40 (35.0%) | 30 / 40 (75.0%) |

Fisher p = 0.0247 on editing, reproducing
[`volunteered-work.md`](volunteered-work.md), and **p = 0.232 on the fact
rate** — laconic's higher fact rate is what its lower edit rate implies, not a
separate effect. Within that batch the editing stratum names the defect 13 of
39 against 41 of 41, p = 1.1e-11.

## What a round can now do

The two counters are scorable where the judged trap is not, and the reason is
that neither reads it. `edited` is a tool list; `locates_defect` is a fact only
`db.js` supplies. The `rule-adherence` marking is about criteria restating the
rules the treatment was handed, and the one remaining route by which
`rules/laconic.md` reaches this case — its worked example — is measured above
and does not move either counter.

A round proposing [#116]'s third pre-send check would register:

- **Target: the laconic edit rate on `conditional`, sonnet**, against its own
  interleaved control, per the rule that a count target takes its baseline from
  the round's own control.
- **Bound: an answer that did not edit must still name the defect.** That cell
  is 0 failures in 215 runs, so any occurrence is new behaviour and needs no
  noise floor.
- **Disclosure: the fact rate overall**, which moves with the stratum mix and
  is a floor.

**Size it before buying it.** A binary rate at 35% is expensive to move
detectably: at 40 runs a side, halving it to 17.5% is detected 35% of the time,
at 60 a side 51%, and reaching 0.8 needs about **120 a side — 240 runs**. The
published 62.5% to 35.0% arm gap was detectable at 40 because it is 27.5
points. A round that opens at 40 and reads a null has measured very little,
which is worth knowing before it is run rather than after.

## What this does not establish

- **No rule edit is proposed here, and none is scored.** This is an instrument.
- **Recall on the editing stratum is 73% out of sample**, estimated from 11
  gold positives. Every editing-side rate is a floor and the correction above
  is a point estimate from 45 hand-labelled runs.
- **The trap is one case's fact.** It transfers to no other case, which is what
  a trap keyed on a named identifier costs. `evals/CRITERIA.md` already applies
  the same admission rule to never-cut keywords.
- **The haiku cell is not the same phenomenon.** Haiku has never edited in 180
  runs and states the defect 41% of the time, so on that model the case
  measures whether the fixture was read, not whether work displaced the answer.
- **Nothing about `quota-merge`.** The closed-confirmation half of
  [`question-shape.md`](question-shape.md) is untouched; this unit is about the
  advisory interrogative that already elicits the behaviour.

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#209]: https://github.com/JordanMPDS/laconic/issues/209
