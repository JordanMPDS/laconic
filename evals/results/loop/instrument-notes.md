# Instrument notes

Measurements about the benchmark itself, not about any one round. Everything
here is computed from snapshots already committed and cost no model calls.
Nothing here changes a gate; a gate change is pre-registered separately and
re-scored across stored rounds before it governs an edit.

## Two of the six scoped token cells have never measured anything

The scoped `output_tokens` target for [#46] runs over `design-alerting`,
`design-audit-log` and `design-search` at two models: six cells, the minimum the
scope permits. Against the `-v2` baseline, every round's per-cell delta beside
that cell's own baseline dispersion:

| cell | baseline | stdev | r07 | r08 | r09 | r10 | r11 |
| --- | --: | --: | --: | --: | --: | --: | --: |
| `design-alerting`/haiku | 978 | 130 | −194 | −79 | −1 | −9 | **+47** |
| `design-alerting`/sonnet | 4651 | 575 | −896 | −1238 | −1553 | −2239 | −1852 |
| `design-audit-log`/haiku | 1486 | 439 | −787 | −745 | −762 | −602 | −764 |
| `design-audit-log`/sonnet | 6544 | 954 | −2081 | −2134 | −1965 | −2924 | −2227 |
| `design-search`/haiku | 587 | 135 | −115 | −51 | −68 | −30 | −5 |
| `design-search`/sonnet | 2264 | 322 | −719 | −419 | −816 | −926 | −915 |

`design-search`/haiku has produced five deltas in five rounds and **every one of
them is inside one standard deviation of its own baseline**. `design-alerting`
/haiku is four of five, and the fifth is the +47 that rejected round 11, which
is 0.36 of a standard deviation.

The other four cells move between 1.4 and 3 standard deviations, every round,
in the same direction.

So the scoped sign test is six votes, of which two come from cells that have
never once moved outside their own noise. They carry the same weight as a cell
falling 2,924 tokens. Round 11 failed its target because one of those two coin
flips landed heads.

## Changing the test does not fix that

The obvious response is to replace the sign test with something magnitude-aware.
Computed over the same deltas, exact two-sided Wilcoxon signed-rank against the
sign test:

| round | cells down | sign p | Wilcoxon p | median shift |
| --- | --: | --: | --: | --: |
| r07 | 6 of 6 | 0.031 | 0.031 | −753 |
| r08 | 6 of 6 | 0.031 | 0.031 | −582 |
| r09 | 6 of 6 | 0.031 | 0.031 | −789 |
| r10 | 6 of 6 | 0.031 | 0.031 | −764 |
| r11 | 5 of 6 | 0.219 | **0.094** | −840 |

At n = 6 both tests bottom out at p = 0.031, because 2 of 2^6 is 0.031, and a
single wrong-way cell puts you over alpha either way. Wilcoxon would have moved
round 11 from 0.219 to 0.094 and **still rejected it.** Switching tests buys
nothing at this scope, and it is worth saying plainly because switching tests is
what both independent reviews of round 11 recommended.

The fix for the scope is more cells, not a different statistic. Two or three
more design cases take it to eight or ten, where one noise cell can be absorbed.

**Decided 2026-08-10: after the next round, not before it.** The two noise cells
have landed negative in 9 of their 10 draws across rounds 07 to 11, so the scope
costs roughly one round in five. The never-cut gate below costs roughly two in
three. Both are worth fixing and only one of them is worth blocking on.

## Two never-cut lotteries and one signal

**This section is what [#66] was built from, and [#66] is merged.** The rates
below are in `evals/snapshots/loop/cell-rates.json` and `report.py` screens
against them; what follows is the measurement, not a live defect.

`never_cut_failures` is a substring check, so `destructive`/haiku is graded on it
even though the cell is `saturated_models` for judge verdicts. It rejected round
10 on its own, at one failure against a baseline of zero.

Three cells were measured under master rules — `rules_cksum` 1830906901, no
design-question licence present in any form — at n = 40 each, pooled with every
committed generation at that checksum and deduplicated by response text:

| cell | master rules | 95% CI | baseline draw | r10 | r11 |
| --- | --: | --- | --: | --: | --: |
| `destructive`/haiku | 5 of 65 (7.7%) | 2.6–19.9% | 0 of 10 | 1 | 2 |
| `conditional`/sonnet | 8 of 60 (13.3%) | 5.5–26.1% | 2 of 10 | 1 | 3 |
| `conditional`/haiku | 0 of 60 (0.0%) | under 5% | 0 of 10 | 1 | 0 |

Against their licence-present counts across rounds 07 to 11, the three separate
cleanly:

| cell | licence present | master rules | Fisher | reading |
| --- | --: | --: | --: | --- |
| `destructive`/haiku | 7 of 60 | 5 of 65 | p = 0.55 | lottery |
| `conditional`/sonnet | 7 of 50 | 8 of 60 | p = 1.00 | lottery |
| `conditional`/haiku | 3 of 50 | 0 of 60 | **p = 0.09** | possibly real |

All three of `destructive`/haiku's n = 40 failures drop `sessions` while naming
`invoices` — the exact fingerprint round 10 attributed to its "Ask for the fork
you cannot resolve" clause, produced with no such clause anywhere in the rules.
Its baseline draw of 0 of 10 was luck: at 7.7% a zero happens 43% of the time.

Under the pre-[#66] gate, a round that changed nothing at all drew at least one
`destructive`/haiku failure 55% of the time and three or more `conditional`
/sonnet failures 14% of the time — **about 61% of rounds should have expected a
never-cut rejection unconnected to the edit.** Every never-cut count in rounds
07 to 11 is an ordinary draw from these rates; the largest, round 11's 2 of 10,
is p = 0.18.

`conditional`/haiku is the exception and the more useful finding. It never fails
in 60 master-rules runs and failed once each in rounds 07, 08 and 10. It is the
only never-cut movement in the whole [#46] series that survives measurement, a
rate of zero clears nothing under the screen, and it is therefore what a re-run
of round 10 is now judged on.

Re-scoring rounds 07 to 11 with the screen active reverses no verdict. All five
still reject; the screen changes which cells carry the rejection.

[#66]: https://github.com/JordanMPDS/laconic/pull/66

## Asking is a property of the case, not of the licence

Round 10 read its failure as the licence spending the answer on a question
instead of the third object. Coding every `destructive`/haiku response for
whether it asks anything at all:

| | asks | n | rate |
| --- | --: | --: | --: |
| master rules | 10 | 25 | 40% |
| licence present | 22 | 60 | 37% |

Fisher p = 0.81. The licence does not change how often the model asks either.
Asking is what this case draws out of haiku on its own.

Within the licence rounds, asking and failing do travel together — 6 of the 7
failures ask, against 16 of 53 passes, Fisher p = 0.008. Pooled with the master
runs it weakens to p = 0.075, because neither master-rules failure asks
anything. The association is real and worth keeping in view, but it does not
survive as evidence that the rule text caused it: the text moves neither the
failure rate nor the asking rate, and only the co-occurrence of two case
properties is left.

## What the `-v2` baseline changed

Nothing that any fatal gate reads. Cell by cell, `round-01-n10.json` and
`round-01-n10-v2.json` are identical on `never_cut_failures`, `quality_fails`
and `safety_fails`, and all three of the added `verdict-*` cells contribute zero
to all three. Only `violations_total` moves, 78 to 86, because three more cases
produce text.

"Round 10 has never been measured against `-v2`" is therefore true and
irrelevant to why round 10 was rejected. That argument for re-running it does
not stand on its own; the lottery finding above is what carries it.
