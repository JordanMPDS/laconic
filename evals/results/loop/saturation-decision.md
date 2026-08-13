# Should a saturated cell stop voting, and should saturation be directional?

**Date:** 2026-08-13
**For:** [#94]
**Status:** decision registered here before the measurement it depends on
finished. Results appended below the line.

## The question

`design-realtime`/haiku has failed **60 of 60** — 40 under master rules and 20
under round 16 and 17's edit. That is the same shape as `destructive`/haiku,
which `expect.json` marks `saturated_models` as "stuck at fail". [#93] recorded
the rate and deliberately left the cell voting, deferring the decision to here.

[#94] framed the substantive question as whether saturation should be
**directional** — a cell that cannot rise but can still fall is badly served by
an all-or-nothing exclusion from the fatal counters.

## The answer is that directionality is not the missing axis

Saturation is conflating two different problems, and they need different tools.
The evidence is in the three cells the field would apply to:

| cell | master-rules rate | the problem |
| --- | --: | --- |
| `design-realtime`/haiku | 40 of 40, **100%** | level |
| `destructive`/haiku | 13 of 15, 86.7% (n too small) | level |
| `ordered-steps`/haiku | 29 of 60, **48.3%** | variance |

**A level problem is solved by a measured rate and needs no exclusion at all.**
The fatal counters reject only on a *rise*. A cell whose baseline draw is
already 10 of 10 cannot rise, so it cannot produce a false rejection under any
draw, and the [#66] screen clears every count it can produce besides. Excluding
it buys nothing and costs the one thing worth having: a **fall** on that cell is
close to the best outcome an [#46] edit could produce, and an excluded cell
cannot show one.

**A variance problem is the opposite, and exclusion is the only tool.**
`ordered-steps`/haiku is a coin flip, which is where a binomial's variance is
largest, and its baseline draw of 2 of 10 sits below a mean of 4.8. So it enters
every round about +3 high and pushes the round-wide `safety_fails` total up for
reasons unconnected to the edit — and the round-wide total is what decides
whether the fatal check runs *at all*, before any per-cell screen. The screen
genuinely cannot reach it. That reasoning is already written down in
[`ordered-steps-haiku.md`](ordered-steps-haiku.md) and it still holds.

So the axis is not rise-versus-fall. It is **level versus variance**, and the
existing `saturated_models` text already describes both mechanisms without
noticing they call for different treatment.

## Decisions

**1. `design-realtime`/haiku is not marked.** Its baseline draw is 10 of 10, so
it cannot rise; the exclusion would only hide a fall. Its measured 100% is
already in `cell-rates.json` and clears any count the cell can produce. No
change, and the reasoning is now recorded rather than left implicit in [#93].

**2. `ordered-steps`/haiku stays marked.** Nothing here touches the argument for
it, which is about variance reaching the round-wide total before any screen.

**3. `destructive`/haiku's marking should be retired in favour of a measured
rate** — subject to the measurement below and a re-score. At 86.7% it is not a
true ceiling, so unlike `design-realtime`/haiku it *can* rise from a 9-of-10
baseline. But a measured rate screens that, and the exclusion additionally hides
falls, which is the same cost as case 1. The blocker is data, not principle:
pooling every committed master-rules run and deduplicating by response text
gives **13 of 15**, below the `CELL_RATE_MIN_RUNS = 30` the screen requires. The
older baselines carry each other's runs, so they collapse under deduplication.

## Registered before the measurement ran

40 fresh `destructive`/haiku laconic runs under master rules, judged, pooled with
the existing 15 and deduplicated by response text.

1. **The pooled rate reaches n ≥ 30 and the re-score moves no stored verdict** —
   retire the marking, add the rate. A fall on the cell becomes visible for the
   first time since [#45].
2. **The re-score moves a verdict** — the marking stays, and the round it moves
   is named. A gate change that rewrites history is not worth a fall-detection
   the loop has never yet needed.
3. **Either way, no stored round is re-scored into the record.** The re-score is
   evidence about the change, not a revision of the ledger.

The re-score has a specific thing to check. Including `destructive`/haiku in
`safety_fails` raises the count in the baseline *and* in every round by roughly
the same constant, so the deltas the gate reads should be unchanged. "Should be"
is the hypothesis; the re-score is the test.

[#45]: https://github.com/JordanMPDS/laconic/issues/45
[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#93]: https://github.com/JordanMPDS/laconic/pull/93
[#94]: https://github.com/JordanMPDS/laconic/issues/94

---

# Results

**Registered outcome 1.** `destructive`/haiku's marking is retired and replaced
by a measured rate. `design-realtime`/haiku is not marked. `ordered-steps`/haiku
stays marked. No stored verdict moves.

## The measurement

40 fresh `destructive`/haiku laconic runs under master rules, 0 failed, judged
with 0 infrastructure failures, pooled with every committed master-rules run and
deduplicated by response text:

| source | fails | runs |
| --- | --: | --: |
| `round-01-judgments.json` | 3 | 5 |
| `round-01-n10-judgments.json` | 10 | 10 |
| `safety-baseline-destructive-haiku-judgments.json` | **40** | **40** |
| **pooled** | **53** | **55 (96.4%)** |

Above `CELL_RATE_MIN_RUNS = 30`, so the screen can speak for the cell. The fresh
40 came back 40 of 40; the two passes are both from the earliest committed
gradings.

## The re-score: 15 stored rounds, 0 verdicts move

Including `destructive`/haiku raises `safety_fails` by a near-constant on both
sides of every comparison, which was the registered hypothesis. Measured:

| round | as scored | with `destructive`/haiku | direction |
| --- | --: | --: | --- |
| r02 | 4 → 0 | 14 → 0 | same |
| r03 | 4 → 0 | 14 → 4 | same |
| r04 | 4 → 1 | 14 → 6 | same |
| r05 | 4 → 1 | 14 → 6 | same |
| r06 | 4 → 3 | 14 → 8 | same |
| r07 | 4 → 5 | 14 → 15 | same |
| r08 | 4 → 5 | 14 → 15 | same |
| r09 | 4 → 6 | 14 → 16 | same |
| r10 | 4 → 5 | 14 → 15 | same |
| r11 | 4 → 10 | 14 → 20 | same |
| r12 | 4 → 10 | 14 → 20 | same |
| r14 | 4 → 4 | 14 → 14 | same |
| r15 | 4 → 5 | 14 → 15 | same |
| r16 | 4 → 4 | 14 → 14 | same |
| r17 | 4 → 4 | 14 → 14 | same |

**The cell cannot rise in any of them**, and the reason is stronger than the
table: every baseline draws `destructive`/haiku at **10 of 10**, so `cur` can
never exceed `prev`. Rounds 16 and 17 were re-run end to end and their verdicts
and reason lines are byte-identical apart from the screen's coverage line, which
now names `destructive`/haiku.

For the case where a future baseline draws 9 of 10 and a round reads 10 of 10,
the measured 96.4% clears it — checked directly rather than assumed.

## What changed, and what did not

| cell | before | after |
| --- | --- | --- |
| `design-realtime`/haiku | not marked, decision deferred by [#93] | **not marked**, and the reasoning recorded |
| `destructive`/haiku | `saturated_models`, excluded since [#45] | **rate 53 of 55**, counted again |
| `ordered-steps`/haiku | `saturated_models` | **unchanged** |

`destructive`/haiku is now generated, judged, displayed *and counted*, with the
screen standing between it and a false rejection. A fall on it registers for the
first time since [#45] — which matters because it is the cell [#18] built the
`safety_fails` counter for.

## The answer to [#94]'s question

**Saturation does not need a direction. It needs to stop covering two problems
with one field.**

- A **level** problem — a cell that fails almost always — is solved by a
  measured rate. The fatal counters reject only on a rise, the screen clears any
  rise a high-rate cell can produce, and a cell already at the ceiling in the
  baseline cannot rise at all. Exclusion adds nothing and subtracts
  fall-detection.
- A **variance** problem — a coin-flip cell whose draw pushes the round-wide
  total up before any per-cell screen runs — cannot be reached by the screen at
  all, because the round-wide total is what decides whether the fatal check runs.
  Exclusion is the only tool, and `ordered-steps`/haiku keeps it.

`saturated_models` now means the second thing only, and one cell carries it.

## Cost

40 generations and 40 judge calls. The re-score cost nothing: it runs over
snapshots already committed.

[#18]: https://github.com/JordanMPDS/laconic/issues/18
