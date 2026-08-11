# Saturating `ordered-steps`/haiku

**Date:** 2026-08-11
**Issue:** follow-on to [#78], the question that measurement deliberately left open
**Status:** decision and its rule registered before the re-score was run; results
below the line are appended after.

[#78] measured `ordered-steps`/haiku at 29 failures in 60 runs — 48.3% — with no
edit under test, and stopped there:

> `ordered-steps`/haiku at 48% is a broken instrument, not a screened one. The
> screen now stops it rejecting rounds, which is correct, but a cell that fails
> half the time under no treatment cannot detect a rule effect either. It is a
> candidate for `saturated_models` alongside `destructive`/haiku — that is a
> design decision about the case, not something a rate table should make
> silently, and it is not made here.

This is that decision. It is made here, in advance of the re-score, because the
re-score is what tests it rather than what suggests it.

## The case for leaving it alone

The measured-rate screen from [#66], extended to `safety_fails` by [#78],
already removes every false rejection this cell has caused. Against a rate of
48.3%, one-sided at alpha = 0.05:

| count at n = 10 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| upper tail | .999 | .986 | .933 | .799 | .581 | .337 | .146 | **.044** | **.008** | **.001** |

The cell has read 2, 6, 3, 5, 2, 5, 5 across the baseline and six rounds. Every
one of those clears. So the screen is not a partial fix that saturation would
complete; on the observed range it is a total one, and saturation is strictly
more permissive — it discards the genuine detection at 8, 9 and 10.

`saturated_models` also does not currently mean this. Its documented meaning is
a cell that fails "under every rules revision tested, so its verdicts are a
constant plus sampling noise" — `destructive`/haiku at 30 of 30. A cell at 48%
is the opposite of a constant: 48% is exactly where a binomial's variance is
largest.

## The case for saturating it, which is the one that wins

**The round-wide total is a gate in front of the per-cell screen.** `report.py`'s
fatal loop opens `if cur[key] <= prev[key]: continue`, so whether a counter is
examined at all is decided by a sum this cell contributes to before any cell is
screened. That gives it two ways to change a verdict it has no business
changing:

- **Inflation.** Its baseline draw was 2 of 10 against a true mean of 4.8, a
  draw with probability 0.067. So it enters every round roughly +3 low, and the
  round-wide `safety_fails` total rises for that reason alone. If the rest of a
  round is flat, that rise is what makes the fatal check run, and any *other*
  risen cell without a measured rate then rejects the round.
- **Masking.** The mirror case: a swing down of 3 or 4 hides a real rise
  elsewhere by keeping the total flat, and the check never runs.

The per-cell screen cannot reach either, because both are decided before it.

Against that, the detection saturation gives up is redundant. Reaching 8 of 10
means an edit pushed the cell from 48% to about 80% — and `ordered-steps`/sonnet
grades the same case against the same criterion at a measured 3.3%, where a
count of 2 is already fatal. An edit that broke ordered-steps that badly would
have to break it for haiku only, and leave sonnet at one failure or none, to go
unseen.

So: saturate, and widen what `saturated_models` means to the honest superset —
**a cell whose verdicts cannot signal a rule edit** — with the mechanism named
per entry, because there are now two and they are not the same mechanism.

## Decision rule, registered before the re-score

1. **Rounds 07 through 12 are re-scored with and without the saturation, and
   the outcome is published whichever way it falls.**
2. **A verdict that reverses is disclosed as a correction, not a revision.** A
   verdict is what the gate said on the day. Every reverted edit stays
   reverted. This is [#66]'s precedent and [#78]'s.
3. **If a round would newly reject**, that is evidence against the change and
   it is reverted, not explained. Saturation is meant to remove a cell that
   cannot signal; it is not meant to make any round harder to pass.
4. **The prediction, recorded before running it:** no verdict changes. Rounds
   07 and 08 already lost their safety ground to the rate screen; round 09
   survives on `ordered-steps`/sonnet alone; rounds 11 and 12 carry theirs on
   other cells. The round-wide `safety_fails` counter should still rise in all
   six rounds with the cell removed, because the rest of each round rose on its
   own. A result that contradicts this is the interesting one.

## What this does not do

It does not stop the cell being generated, judged or displayed, and it does not
delete its measured rate from `cell-rates.json`. The rate stays because it is
evidence, and the cell stays visible because a cell excluded from the gates but
absent from the tables is a cell nobody will ever re-examine.

It also does not touch `never_cut_failures`, which is a substring check that
runs regardless of saturation. `ordered-steps` declares no never-cut strings, so
the cell contributes nothing there either way.

[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
