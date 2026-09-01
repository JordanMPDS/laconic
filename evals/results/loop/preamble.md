# `preamble`: a high-precision detector the archive cannot score

**Status: parked, with the numbers recorded.** The detector works. The archive
cannot separate the arms with it, and the one comparison that is properly matched
points *against* the plugin at p = 0.051 on a baseline cell of ten responses.
Settling it needs a matched batch, not another archive read.

The criterion and the measurement order were registered in [#179] before any rate
was computed.

## Why this was tried

[`deletability.md`](deletability.md) closed direction B for [#155] and left a
byproduct marked as deserving its own issue: 33 of 43 `walkthrough` responses open
with a lead-in announcing what follows, and `lite` bans exactly that —

> **No preamble.** Do not restate the question, announce what is about to happen,
> or narrate tool calls the user can already see.

The closing-offer detector ([`closing-offers.md`](closing-offers.md)) is the
precedent: a `lite` ceremony rule with a formulaic surface form turned out to be
measurable at high precision across the whole stored archive at no generation
cost, and it produced the loop's clearest arm separation. This asks whether the
other half of the same rule behaves the same way.

It does not, and the reasons are worth having written down.

## The boundary that decided the design

The registered criterion carries one rule from [`deletability.md`](deletability.md),
the single part of direction B that worked: **the unit is one complete sentence,
and a sentence that both announces and asserts is not preamble**, because deleting
it loses a claim.

That rule does most of the work here. A first pattern keyed on any `Here's …`
opening scored 57 hits on `round-21.json`, and reading 20 of them against the
criterion put precision at roughly 60–65% — [#155]'s parked territory, and the
same failure mode: the mixed sentence.

> Here's the full flow in `auth.js` (41 lines total, no other files reference it
> — this module is self-contained).

That asserts scope. It is not preamble. Against:

> Here's the complete token refresh flow:

which asserts nothing.

The shipped pattern therefore requires a **pure** announcement — short, and
carrying no parenthetical, em-dash aside, relative clause or trailing assertion.
On a fresh draw of 18 hits, **18 are pure announcements**.

One bug is worth recording because it inflated the first attempt: the sentence
terminator matched the dot inside a filename, so `Here's the full flow in
`auth.js` (41 lines…` fired. Backticked spans are blanked before matching.

## What the archive says, and why little of it can be used

Deduplicated by response text, over every stored round:

| Arm | rate |
|---|--:|
| **laconic** | 3.51% |
| `terse-control` | 3.20% |
| `concise-style` | 2.80% |
| `word-compression` | 2.40% |
| baseline | **0.76%** |

Taken at face value that says laconic breaks its own rule at 4.6× baseline's
rate, Fisher p < 0.001. **It should not be taken at face value — it is
mix-shift**, the same defect round 23 found in the compression claim.

Preamble concentrates almost entirely in `walkthrough`, and the two corpora are
weighted differently: `walkthrough` is 750 of laconic's 12,273 deduplicated
responses (6.1%) and 10 of baseline's 529 (1.9%). The deduplicated baseline arm
is small because carried arms collapse to a few hundred distinct responses, which
leaves roughly ten to twenty per case — too few to case-match against.

Held at the case level, only two cases have twenty responses in both arms and any
hit at all:

| Case | baseline | laconic |
|---|--:|--:|
| `design-cache` | 0 / 20 (0.0%) | 7 / 617 (1.1%) |
| `design-upload` | 1 / 20 (5.0%) | 23 / 567 (4.1%) |

Pooled over those two, baseline 0.37% against laconic 1.50%, **p = 0.167**. The
arms do not separate.

## The one result worth following up

> **Withdrawn 2026-09-01 by round 37.** A matched interleaved batch at 40 a side
> reads baseline 17.5% against laconic 10.0%, p = 0.518 — laconic *lower*, not
> higher, and not significant. The archive figure was not wrong about its own
> data; it was wrong about now. At byte-identical rules the laconic rate fell
> from 46.7% across August to 10.0% today, Fisher p = 1.0e-05, over five CLI
> patch releases. See [`round-37.md`](round-37.md). The section below is left
> standing because it is what prompted the round, and because its own caveat —
> that a baseline cell of ten cannot settle it — was right.


`walkthrough` alone, where the shape actually lives:

| | preamble | rate |
|---|--:|--:|
| baseline | 1 / 10 | 10.0% |
| **laconic** | **320 / 750** | **42.7%** |

Fisher **p = 0.0508**, on a baseline cell of ten responses.

That is not a finding and it is not nothing. It points against the plugin on a
rule the plugin itself states, it is the only properly matched comparison
available, and it is one response away from significance in either direction. A
baseline cell of ten cannot settle it.

**What would**: `walkthrough` and the `design-*` cases, baseline against laconic,
one interleaved batch, 40 a side. That is 80 generations and no judging, because
the metric is syntactic. It is the cheapest open question in the suite.

## What this says about ceremony rules generally

Closing offers and preamble are both `lite` rules with formulaic surface forms,
and only one of them was measurable off the archive. The difference is base rate
and corpus balance rather than detector quality — closing offers run at 5–26%
across every case, while preamble is near zero everywhere except the one case
that asks for a walkthrough.

So "a ceremony rule has a regex, therefore the archive can score it" is false,
and this is the counterexample.

[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#179]: https://github.com/JordanMPDS/laconic/issues/179
