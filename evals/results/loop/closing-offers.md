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
like me to`, `let me know if`, `shall i write/add/create/run/do`, `happy to
write/add/help`, `just say the word` — and all three shapes above are excluded
by construction. They are in `tests/test_metrics.py` as regression cases.

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

**Recall is not measured, so the rate is a floor rather than an estimate.** That
is acceptable for comparing arms only if the misses are arm-independent, which
is assumed here and not established.

## The rate, deduplicated

Carried arms make the naive archive count useless: `47/220` is the same 220
baseline responses re-counted in twelve rounds, and pooling them inflated the
baseline denominator roughly tenfold. Counting each distinct
`(arm, case, model, response)` once:

| Arm | Closing offers | Rate |
|---|--:|--:|
| **laconic** | 439 / 12,662 | **3.5%** |
| baseline | 62 / 475 | 13.1% |
| `concise-style` | 42 / 250 | 16.8% |
| `terse-control` | 49 / 250 | 19.6% |
| `word-compression` | 55 / 250 | 22.0% |

Baseline against laconic, Fisher exact: **p = 8.6e-18**.

**The rule is doing work that generic brevity instructions do not.** Every
control arm sits at or above baseline — being told to be terse, to compress
words, or to use the CLI's native `Concise` style does not suppress closing
offers, and `concise-style` at 16.8% is nearly five times laconic's rate. This
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

[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#155]: https://github.com/JordanMPDS/laconic/issues/155
