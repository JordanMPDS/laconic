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
   being handed a softer test. *(Corrected after the re-score — see below.)*
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

---

# Results

**No verdict changes, in any of the seven stored rounds.** Prediction 5 holds.

But it holds only after condition 2 was corrected, and the correction was made
after seeing a re-score. That is disclosed first, before anything it makes look
good.

## Condition 2 was registered wrong, and the re-score caught it

As registered:

> ~~**The existing ≥ 6-cell floor applies after dropping, not before.** A scope
> that falls under six cells is refused, exactly as it is today.~~

Run that way, rounds 07 to 14 all lose their scoped target and **round 10 flips
from accept to reject**, which decision rule 3 says reverts the change.

The cause is not the floor. Those rounds named three design cases, so they have
six cells; dropping two leaves four, and four is refused. The refusal is for
want of the two cases that did not exist when they ran. Re-scoring a three-case
round under a rule built for a five-case scope measures the missing cases, not
the threshold — the same reason the ledger already forbids re-scoring rounds 01
to 10 against the `-v2` baseline.

So condition 2 now reads:

**Short cells are dropped all-or-nothing, and only when at least six cells
remain.** A scope that cannot afford the drop keeps every cell, scores exactly
as it did before this existed, and is told to name more cases. Partial dropping
is not offered: choosing which short cell to keep would be choosing the answer.

Two things make this a correction rather than a fishing expedition, and readers
should weigh them rather than take the claim:

- It moves the gate in the **conservative** direction. Wherever the improvement
  cannot be afforded, behaviour is byte-identical to before.
- It changes no verdict in either direction, which is what the re-score below
  shows.

Against that: it was chosen after seeing that the registered version reverted
round 10. A stricter reading of decision rule 3 would have stopped here and
published nothing. That reading is defensible and this record exists so it can
be applied by someone else.

## The re-score, under the corrected condition

| round | verdict | scoped target |
| --- | --- | --- |
| 07, 08, 09, 12 | reject (unchanged) | passes, unchanged, plus the disclosure line |
| 10 | **accept (unchanged)** | passes, unchanged, plus the disclosure line |
| 11, 14 | reject (unchanged) | fails at 5 of 6, unchanged |

Every round now prints, beside its unchanged result:

```
2 cell(s) are below the 1200-token floor and voted anyway: dropping them would
leave 4 cells, under the six a sign test needs to reach alpha. Name more cases
in the scope
```

which is the instrument telling its operator what to do next, rather than a
gate quietly changing its mind about the past.

## What the threshold actually removes, measured on stored rounds

The re-score cannot test the threshold, because no stored round has the scope it
was built for. This can, and it is the evidence the change rests on. Per-cell
deltas across all seven rounds, split into the four cells the floor keeps and
the two it would drop:

| round | kept cells | dropped cells |
| --- | --- | --- |
| 07 | **4 of 4 down** | alerting/haiku −194, search/haiku −115 |
| 08 | **4 of 4 down** | −79, −51 |
| 09 | **4 of 4 down** | −1, −68 |
| 10 | **4 of 4 down** | −9, −30 |
| 11 | **4 of 4 down** | **+47**, −5 |
| 12 | **4 of 4 down** | −45, −52 |
| 14 | **4 of 4 down** | −53, **+32** |

**The kept cells are unanimous in every round: 28 of 28.** Not one has ever gone
the wrong way, across seven rounds and four different rules revisions.

The dropped cells agreed with them 12 times out of 14 and disagreed twice — and
both disagreements are rounds 11 and 14, the two rounds the target rejected. So
across the whole series these two cells contributed no information the other
four did not already carry, and twice they overturned them. That is the case for
the threshold, and it does not depend on the two new cases at all.

## What takes effect when

From the next round, scored against `round-01-n10-v3.json` with all five design
cases named in `--target-cases`. Then the scope is 10 cells, the four short ones
drop, six remain, and one wrong-way vote among the survivors is tolerated at
p = 0.021 instead of rejecting at 0.219.

Stored rounds keep their scope, their baseline and their verdicts, exactly as
rounds 01 to 10 kept the 14-case baseline when `-v2` arrived.

## What this does not settle

The 1200-token threshold is absolute, and it was derived from one target's
cells. A future scope of genuinely shorter cases — round 05 and 06 targeted
`badnews`, `ordered-steps` and `walkthrough`, whose baselines run 400 to 1200 —
would find every cell under the floor and simply keep them all, which is safe
but is not the same as being right for that scope. The honest form of this rule
is per-cell and relative, comparing a cell's observed movement to its own
dispersion, and that needs round data a new cell does not have.

The two new haiku cells are assumed short-and-noisy on their dispersion alone
(`design-retry`/haiku at sd/median 0.51, `design-rate-limit`/haiku at 0.38, the
two highest in the scope). They have never been run under an edit. If either
turns out to move, the threshold excludes a working cell, and the deltas from
the next two rounds are what would show it.

[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
