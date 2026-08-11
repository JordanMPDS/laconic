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

## The judge disagrees with itself at 5.3%, not 9.6%

Round 13 re-judged round 12's 340 laconic responses a second time under
identical criteria. It is the same experiment the carried control arm provides
for free, run directly on the arm the gates actually read.

| | control arm (r10 vs r11) | **laconic arm (round 13)** |
| --- | --: | --: |
| responses graded twice | 415 | 340 |
| verdict agreement | 90.4% | **94.7%** |
| `pass` to `fail` | 8.8% | **3.1%** |
| `fail` to `pass` | 12.0% | **8.6%** |

The two arms differ: 18 of 340 against 40 of 415, Fisher p = 0.028. Laconic
responses are shorter by construction and are graded more consistently, so
extrapolating the control arm's rates onto them overstates judge noise about
four-fold. [#70] made exactly that extrapolation and predicted a `safety_fails`
drift of +7.5; the measured value is +1.4, sd 1.9.

Under re-grading of a fixed set of responses, the two judge-verdict counters
move within about ±4 (`safety_fails`) and ±5 (`quality_fails`) at two sigma.

**The noise that has been rejecting rounds is upstream of the judge.** Rounds 10
and 12 ran byte-identical rules and read `safety_fails` 7 and 15, a movement of
8. Re-grading round 12's own responses moved it 15 to 12, a movement of 3. So
generation sampling contributes roughly twice what the judge does, and a floor
built by re-judging would be too small to gate on.

What `safety_fails` needs is the treatment [#66] gave `never_cut_failures`: a
per-cell failure rate measured under master rules across many generations, and a
screen that asks whether a round's count exceeds that rate. The three cells that
rejected round 12 — `destructive`/sonnet, `ordered-steps`/haiku and
`ordered-steps`/sonnet — have no measured rate. `ordered-steps`/haiku alone has
read 2, 6, 3, 5, 2, 5, 5 across the baseline and six rounds under three
different rule texts.

**Done on 2026-08-11 ([#78]), in [`safety-rates.md`](safety-rates.md).** The
three rates are 24.6%, 48.3% and 3.3%, and the screen activated with no code
change. `ordered-steps`/haiku was saturated the same day, for the reason that
measurement surfaced and deliberately did not settle:
[`ordered-steps-haiku.md`](ordered-steps-haiku.md).

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

~~Re-scoring rounds 07 to 11 with the screen active reverses no verdict. All five
still reject; the screen changes which cells carry the rejection.~~

**Corrected 2026-08-11: round 10 reverses to accept, and did so the day [#66]
merged.** The re-score above was run without round 10's arbitration snapshot,
which round 10's own scoring used. Supplied with it, the screen removes
`destructive`/haiku at 1 of 10 against the measured 8% — the one cell the
replication reproduced — leaving only `conditional`/haiku, which the
replication cleared. The paragraph immediately above this one had already
concluded that `conditional`/haiku "is therefore what a re-run of round 10 is
now judged on"; the re-score simply did not pass the flag that would have shown
it. Rounds 07, 08, 09 and 11 do still reject. Working in
[`safety-rates.md`](safety-rates.md).

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

[#70]: https://github.com/JordanMPDS/laconic/issues/70
