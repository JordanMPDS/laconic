# The closing-offer detector, and what it says about the arms

[#113] asked for this. It reports a `lite` rule — no closing offers, no offers
to do more work — breaking on one turn and holding on the next, same level, same
session, adjacent turns, same request shape. Its argument is that this matters
as evidence rather than as harm:

> word count is a judgment call — two readers can reasonably disagree about
> whether 600 words was right for a given question — whereas *"did the last
> sentence offer to do more work"* is binary and needs no interpretation. If
> ceremony rules and length rules decay together, the cheap binary one is a
> usable detector for the expensive judgment one.

The detector now exists as `metrics.closing_offers()`. This is what it measures,
what it cost to make it trustworthy, and the one thing it still cannot answer.

## The first draft had zero precision

The obvious pattern keys on `i can`, `should i`, `if you want`, `let me know`,
`want me to`. Run over the 210 turn-responses of round 35 it found 13 hits and
**every one was a false positive**:

> ...the doc doesn't give order counts, revenue, or customer-count figures, so
> **I can't** quantify actual business impact beyond the error-rate numbers.

> ...`INCIDENT.md` doesn't include the actual `chargeOrder()` source, so I can't
> show you the real diff — **if you** have the code elsewhere, point me at it.

The first is a stated limitation. The second is a request for what is needed to
answer at all. Both are never-cut content, and neither is an offer to do more
work. The rules also carve out the third confusable case explicitly: *"Asking
the user to confirm a destructive action is never a closing offer; offering to
go read something for them is."*

The shipped pattern requires the offer form itself — `want me to`, `would you
like to/me`, `let me know if`, `shall i write/add/create/run/do`, `should i
look/check/review/dig/go`, `i can help/walk you through/look at/sketch`, `happy
to write/add/help`, `just say the word` — and all three shapes above are excluded
by construction. They are in `tests/test_metrics.py` as regression cases, along
with the three the recall pass added.

## Precision, measured before the rate was used

30 hits drawn at random from the snapshot archive, seed fixed, hand-read:
**30 of 30 are genuine offers to do more work.**

> Want me to implement this (migration + the `context.js`/`auth.js`/`db.js`
> changes)?

> Would you like me to build this out?

> That's the shape of it — say the word if you want me to actually implement it.

That is the bar [#155]'s restatement metric could not clear at 55.3% precision,
and it is the difference between a usable metric and a parked one. The reason
this one is easy and that one is hard is that a closing offer is syntactically
formulaic while a restated claim is semantic.

### Recall, measured second, and the pattern widened

The first pattern's recall was not good enough. 40 responses it scored negative
were drawn at random from `round-21.json` and hand-read, and **three were genuine
offers it had missed**:

> Want to explore any part of this deeper, or **should I look at the actual
> codebase** to see what's already in place?

> If you show me your current auth/JWT code, **I can help wire up** the
> `kid`-based dual-key verification directly.

> Is there a specific ops dashboard you're thinking about, or **would you like to
> dig into** any of these approaches?

All three are offers to do work, not questions asking for information, which is
the line this pattern draws. They were added, and **every one of the 22 responses
the widening newly catches was hand-read**: 21 unambiguous, one borderline
("what aspect would you like to change?"). On the same 40-response sample the
widened pattern misses none.

**The widening did not move the arm ordering, and it widened the gap:**

| Arm | first pattern | widened |
|---|--:|--:|
| baseline | 21.4% | **25.9%** |
| `word-compression` | 20.9% | 22.3% |
| `terse-control` | 19.5% | 21.4% |
| `concise-style` | 13.6% | 15.5% |
| **laconic** | **5.5%** | **5.9%** |

The misses were baseline-skewed - 10 added against laconic's 1 - so **the recall
limitation was understating the difference between the arms rather than
threatening it.** That is the direction a measurement's unmeasured half should
fail in, and it was worth checking rather than assuming.

Recall is still estimated from 40 responses and is not established precisely.
The rates remain floors.

## The rate, deduplicated

Carried arms make the naive archive count useless: `47/220` is the same 220
baseline responses re-counted in twelve rounds, and pooling them inflated the
baseline denominator roughly tenfold. Counting each distinct
`(arm, case, model, response)` once:

| Arm | Closing offers | Rate |
|---|--:|--:|
| **laconic** | 517 / 12,681 | **4.1%** |
| baseline | 76 / 499 | 15.2% |
| `concise-style` | 48 / 250 | 19.2% |
| `terse-control` | 55 / 250 | 22.0% |
| `word-compression` | 58 / 250 | 23.2% |

Baseline against laconic, Fisher exact: **p = 2.1e-21**.

**The rule is doing work that generic brevity instructions do not.** Every
control arm sits at or above baseline — being told to be terse, to compress
words, or to use the CLI's native `Concise` style does not suppress closing
offers, and `concise-style` at 19.2% is nearly five times laconic's rate. This
is a cheap, binary, high-precision axis on which the plugin beats what the CLI
already ships, which is a claim the loop has otherwise struggled to make.

Read as a floor, not a level: the true rates are all higher by whatever the
detector misses.

## What it still cannot answer

[#113]'s actual question is about **drift within a session** — the rule breaking
on one turn and holding on the next. Answering that needs per-turn rates inside
multi-turn runs, and the only multi-turn corpus is `recall-*`, `wide-*` and
`deep-*`:

| Snapshot | baseline | laconic |
|---|--:|--:|
| round-33 | 0 / 45 | 0 / 45 |
| round-34 | 0 / 60 | 0 / 60 |
| round-35 | 0 / 105 | 0 / 105 |

**Zero, in both arms, across 315 turn-responses.**

### Why, corrected

The first version of this document attributed that to the prompts: every one of
those cases ends `Don't edit anything.`, so there is no work to offer. **That
explanation is wrong**, and the archive says so plainly. `design-audit-log`
carries the identical clause and reads 9.3%:

| Case | edit clause | rate |
|---|:--|--:|
| `badnews` | no | 22.8% |
| `design-audit-log` | **yes** | 9.3% |
| `walkthrough` | no | **0.1%** |
| `deep-metric` | yes | 0.0% |

Pooled, the clause moves the rate from 6.4% to 3.2% — a real effect, and far too
small to explain a floor of zero across 315 responses. A case with the clause
reaches 9.3% and a case without it sits at 0.1%.

**The driver is task shape, not the clause.** Offers appear where the answer
names something that could be built and the model has not built it — a design
(`design-*`), a bug to chase (`badnews`), a fix to apply
(`destructive`, `conditional`). They vanish where the deliverable *is* the
answer: `walkthrough`, `floor`, `code-fidelity`, `verdict-*`, and the whole
`confirm`/`recall`/`wide`/`deep` family, which asks analytical questions about a
document and gets analysis back. There is nothing to offer because the answer is
the artifact.

### What measuring drift actually needs

A five-turn family whose **turns are design-shaped** — each answer naming
something buildable — rather than a five-turn family that merely permits
editing. `Don't edit anything.` can and should stay: CRITERIA.md requires it so
the diagnosis lands in the response rather than the diff, and `design-audit-log`
shows it costs the signal little.

The detector is ready and costs nothing to apply to such a family.

### That family was built, and it has now been read

`drift-service` and `cold-service` were authored on 2026-09-01 to exactly this
specification, and three rounds have generated them since. Applying the detector
cost nothing, as predicted, and the answer is in
[`closing-drift-113.md`](closing-drift-113.md):

| | |
|---|--:|
| `laconic`, `drift-service`, all five turns | **0 / 325** |
| `baseline`, `drift-service`, all five turns | 29 / 125 (23.2%) |

So the family works where `deep-*` did not — the unruled arm fires at 23.2%
against that family's 0.0% — and on the ruled arm there is no drift to see, with
a 95% upper bound of 0.92% on any rate at any depth.

**The finding that outlives [#113]'s proposal is about the construct.** On the
arm where the signal fires, it does not vary by turn index (permutation
p = 0.266) and varies enormously by run: 21 of 25 runs sit at 0 offers or at 4
and above, at p < 1/20001 against the same hits reassigned across the same
turn-responses. A closing offer is a property of the session, so it cannot proxy
a per-turn quantity.

## A third pass, for round 117

[Round 117](round-117.md) needed the detector to see ponytail's prescribed
invitation, *"Did X; Y covers it. Need full X? Say so."*, and it did not.
Checking that turned up a larger miss: "say the word" was matched only after
"just", and *"Say the word if you want it implemented"* is in 3 of round 21's
1,100 responses, too rare for its 40-response recall sample to hold.

Three shapes were added: "say the word" on its own, a question followed by
"Say so", and "If you want ..., tell me" or "let me know". A "say the word"
followed by "and I'll run it", "go ahead", "proceed" or "execute" is left out,
because there it asks to confirm the action the user requested.

| | |
|---|--:|
| distinct non-holdout responses in the archive | 80,030 |
| newly caught | 79 |
| no longer caught | 0 |
| newly caught on the `laconic` arm | 48 |
| hand-read at seed 117 | **30 of 30 genuine offers** |

**Unlike the first widening, the misses were laconic-skewed.** With
"Want me to...?" quoted as banned, the arm reached for a closer the rule does
not quote. The `#113` families barely move: `laconic` `drift-service` stays
0 of 1,529 distinct turn-responses, `edit-service` 10 of 3,499, and
`cold-service` goes from 3 to 5 of 150. The arm table above was computed under
the first two passes and is not recomputed here; its laconic rate is a floor by
more than the recall sample suggested.

## A fourth pass: the confirmation worded with the other openers

[#471]: the third pass's carve-out covered "say the word" only, so the same
confirmation worded with "want me to" or "would you like me to" still counted.
`holdout-destructive` asks for `./deploy.sh --reset`, which drops a shared
database, and its stored answers end the way Never cut tells them to: *"Do you
want me to run it as written?"* That was scored as the ceremony `lite` forbids.

Both openers now skip a following "proceed", or a "run" or "execute" whose
object points back at what is already on the table: "it", "this", "that", "all
of it" or "the whole thing", with no "instead" after it. An optional colon and
list marker cover *"Do you want me to: 1. Run it as-is"*.

The line is drawn there because the other shapes are offers. A named object
can be anything, so *"run the full reset"* stays counted along with *"Want me
to run the full test suite?"*. "instead" brings in a command the user did not
ask for, as in *"Want me to run that instead?"* over a TRUNCATE on
`destructive`. Bare "go ahead" stays counted because *"Want me to go ahead and
implement this?"* is the commonest offer on the design cases. "proceed" is
carved out whatever follows it, so the detector now misses *"Want me to proceed
with implementing the rest?"* and, through "run it", *"run it for the other two
services as well"*. Neither shape is in the archive.

| | |
|---|--:|
| distinct responses in the archive, holdout included | 85,786 |
| responses that lose a hit | 102 |
| responses that gain one, or whose match changes | 0 |
| `holdout-destructive` answers with a hit | 170 of 430 to 69 |
| carved-out holdout answers hand-read at seed 471 | **30 of 30 confirm or narrow the requested reset** |
| genuine offers lost elsewhere | 1, on `design-upload` |

The lost offer is *"happy to implement this ... if you want me to proceed"*.
Of the 69 left on the holdout, 66 are the confirmation in words the carve-out
does not reach: 43 name the object (*"run the full reset"*, *"run the whole
script"*), and the rest are *"Should I go ahead?"*, *"want me to wipe the
shared staging database"* and the like. Two are *"I can help with that, but
first I need to confirm"*, and one is the genuine offer the rule itself names:
*"If you'd like, I can also read the script first"*. The production shapes
[`production-turns-283.md`](production-turns-283.md) found, a merge authorised
by "Want me to merge #99 and #100" and the phrase inside a quotation, are not
reached either.

**No stored verdict moves.** `report.py` discloses closing offers and gates
nothing on them, and no round document quotes a holdout count. The one gate
that reads them is the benchmark Stop hook: `stop_hook.decide()` blocks when
`metrics.decisions()` is non-empty, and closing offers are among those
decisions. None of the 510 stored Stop-hook texts changes, so the hook rounds
stand, though the hook now lets the carved-out confirmations through. The
published benchmark snapshot, `benchmark-2026-09-24.json`, holds none of the
102, so `docs/benchmark.md` and the README are unchanged. 101 of the 102 are
laconic answers to `holdout-destructive`, and the other is `word-compression`'s
offer above.

[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#471]: https://github.com/JordanMPDS/laconic/issues/471
