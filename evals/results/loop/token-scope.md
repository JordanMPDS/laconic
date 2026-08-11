# The scoped token target: more cells was the wrong fix

**Date:** 2026-08-11
**Issue:** the scope fix deferred in `instrument-notes.md` on 2026-08-10 and
made due by round 14
**Status:** criterion and decision rules registered before the re-score was run.
Results are appended below the line.

## What was deferred, and what round 14 collected

`instrument-notes.md` recorded on 10 August:

> The fix for the scope is more cells, not a different statistic. Two or three
> more design cases take it to eight or ten, where one noise cell can be
> absorbed.
>
> **Decided 2026-08-10: after the next round, not before it.** … the scope
> costs roughly one round in five.

Round 14 was the next round, and it cost it: the target failed at 5 of 6 cells,
p = 0.219, on `design-search`/haiku at **+32 tokens — 0.24 of that cell's own
standard deviation** — while the median shift reached −1008, the largest of the
three draws of those rules. Round 11 failed the same target the same way on the
other noise cell. Two of the last four rounds.

## More cells does not fix it, and eight cells fixes nothing at all

The sign test is two-sided exact, so what matters is how many wrong-way votes
the scope can absorb:

| cells | 0 wrong-way | 1 wrong-way | 2 wrong-way |
| --: | --- | --- | --- |
| 6 | p = 0.031 **pass** | p = 0.219 fail | p = 0.688 fail |
| 8 | p = 0.008 **pass** | p = 0.070 fail | p = 0.289 fail |
| 10 | p = 0.002 **pass** | p = 0.021 **pass** | p = 0.109 fail |

**Eight cells absorbs nothing** — one wrong-way cell still rejects at 0.070. Only
ten changes the tolerance, so "two or three more design cases" is really "two
more", and the two were written: `design-rate-limit` and `design-retry`.

## Then the measurement said the added cells are the problem

Both new cases were generated at n = 10 under master rules for the v3 baseline.
The laconic arm's own dispersion, beside the cells whose behaviour is already
known from rounds 07 to 14:

| cell | baseline median | stdev | sd/median | history |
| --- | --: | --: | --: | --- |
| `design-audit-log`/sonnet | 6544 | 954 | 0.15 | moves 1.4–3 sd every round |
| `design-alerting`/sonnet | 4651 | 575 | 0.12 | moves 1.4–3 sd every round |
| `design-rate-limit`/sonnet | 4012 | 775 | 0.19 | **new** |
| `design-retry`/sonnet | 3842 | 1543 | 0.40 | **new** |
| `design-search`/sonnet | 2264 | 322 | 0.14 | moves 1.4–3 sd every round |
| `design-audit-log`/haiku | 1486 | 439 | 0.30 | moves 1.4–2.0 sd every round |
| — | | | | |
| `design-alerting`/haiku | 978 | 130 | 0.13 | **never outside 1 sd, 7 rounds** |
| `design-retry`/haiku | 702 | 361 | 0.51 | **new** |
| `design-rate-limit`/haiku | 654 | 252 | 0.38 | **new** |
| `design-search`/haiku | 587 | 135 | 0.23 | **never outside 1 sd, 7 rounds** |

Each new case adds one sonnet cell that looks like the working ones and one
haiku cell that looks like the broken ones. The scope would go from 6 cells with
2 noise cells to 10 cells with 4. Modelling the pass rate against how badly a
noise cell behaves — a real cell's wrong-way rate is taken as 0.04, being 0
wrong-way in about 24 real-cell observations across rounds 07 to 14:

| scope | noise cell wrong 14% | 30% | 50% |
| --- | --: | --: | --: |
| today: 6 cells, 2 noise | 62.8% | 41.6% | 21.2% |
| 10 cells, 4 noise | 81.4% | 55.7% | 25.7% |
| **6 cells, 0 noise** | **78.3%** | **78.3%** | **78.3%** |

More cells is a bet that the noise cells drift gently rather than flipping
coins. The two existing ones have drifted gently — 12 of 14 draws negative — but
the two new ones have no draws at all, and they are the two most dispersed cells
in the table. **Dropping the noise cells is the only option whose value does not
depend on an assumption I cannot check.**

## The criterion, registered before it was applied

**A cell does not vote in the scoped `output_tokens` sign test when its baseline
laconic median is below 1200 output tokens.**

The separation is not marginal. Every cell that has ever moved outside its own
noise has a baseline median of **at least 1486**; every cell that never has is
**at most 978**. The threshold sits in the middle of a 508-token gap containing
no cells at all.

The mechanism is why the gap exists rather than a coincidence to be tuned
against: this target measures compression of design answers, and a cell whose
whole answer is 600 to 1000 tokens has a few hundred tokens of headroom, which
is the same size as its own dispersion. It cannot express the effect. That is
the reading `instrument-notes.md` gave these cells on 10 August, before round
12 or round 14 existed; the threshold states it as a rule instead of a list.

Three conditions travel with it:

1. **A dropped cell is named in the report, never silently removed.** Silently
   shrinking a gate's denominator would be the worst version of this change.
2. **The existing ≥ 6-cell floor applies after dropping, not before.** A scope
   that falls under six cells is refused, exactly as it is today, rather than
   being handed a softer test.
3. **This governs only the scoped `output_tokens` sign test.** It touches no
   fatal counter, and a dropped cell is still generated, still judged, and
   still in every table.

## Decision rules, registered before the re-score

1. **Rounds 07 to 14 are re-scored with and without the threshold, and the
   outcome is published whichever way it falls.**
2. **A verdict that reverses is disclosed as a correction, not a revision.**
   Every reverted edit stays reverted. This is [#66]'s precedent, [#78]'s, and
   the saturation's.
3. **If a round would newly reject, the change is reverted, not explained.**
4. **The uncomfortable part, stated before the numbers:** this threshold drops
   the cell that failed round 14's target, so round 14's target ground is
   expected to disappear. Round 14 also rejected on never-cut
   (`conditional`/haiku +1), which this change cannot touch, so its verdict
   should stand on that ground alone. If instead this change flips round 14 to
   accept, that is a gate change rescuing the round that motivated it, and it
   will be reported in exactly those words.
5. **The prediction:** no verdict changes in any of the eight rounds.

[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
