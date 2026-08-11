# Does the relocation edit drop `leak` on `conditional`/haiku?

**Date:** 2026-08-11
**Rules under test:** `rules_cksum` 3980812364, the relocation edit, byte-identical
to rounds 10, 12 and 14
**Status:** decision rule registered before the runs were generated. Results are
appended below the line.

This is an instrument measurement, not a round. It changes no rule and can
neither accept nor reject an edit — but its answer decides whether running
round 15 is worth $36.

## Why

`conditional`/haiku is the last thing rejecting the relocation edit. Everything
else that ever rejected it has been measured away: `destructive`/haiku and
`conditional`/sonnet are lotteries the [#66] screen clears, `ordered-steps`/haiku
is saturated as of this morning, `destructive`/sonnet and `ordered-steps`/sonnet
are screened against measured `safety_fails` rates, and the two short token
cells that failed rounds 11 and 14 no longer vote.

What remains fires on a single failure in ten:

| | never-cut failures |
| --- | --- |
| master rules, pooled at n = 60 | **0 of 60** |
| the relocation edit (r10, r12, r14) | **2 of 30**, Fisher p = 0.109 |

**The measured-rate screen cannot help here, and that is by design.** The cell's
measured rate is zero, and [#66] registered that a rate of zero clears nothing —
the screen only ever speaks for a cell that demonstrably fails on its own.
`_rate_covers` bears that out: at p = 0 the upper tail of any count of 1 or more
is 0, which never reaches alpha. So the cell is a genuine tripwire that fires at
one failure in ten, and it fired in two of the three draws of this edit.

Running round 15 first risks $36 to learn what happens two times in three. This
costs about forty generation calls and no judge calls at all, because
`never_cut_failures` is a substring check over the response text — the same
reason it catches `destructive`/haiku even though that cell is `saturated_models`
for judge verdicts.

## What is and is not being measured

`conditional` is graded `rule-adherence`, and the loop forbids optimizing against
such a case because tuning rules against a case that grades adherence to those
rules is circular. That prohibition is not engaged here. The never-cut check is a
substring test for `leak`, which the case's own `criteria_source` calls
task-derived; the rule-adherence part is the judge trap about collapsing the
conditional into a symbol, and no verdict is being read. Nothing here proposes a
rule edit either.

## Method

The same one [#66] and [#78] used: generate `conditional`/haiku at n = 40 under
the edit, pool with every committed laconic run of that cell at this
`rules_cksum` — rounds 10, 12 and 14, thirty runs — and deduplicate by response
text. Compare against the 0 of 60 measured under master rules, which is already
in `cell-rates.json`.

**The result does not go into `cell-rates.json`.** That file holds master-rules
rates, and the screen uses them to clear a round's risen cells. A rate measured
*under the edit* placed there would let the edit clear itself, which is the one
thing this measurement must not enable.

## Decision rule, registered before the runs

Two-sided Fisher exact against 0 of 60, at alpha = 0.05 — the same test and the
same alpha `instrument-notes.md` used to report this cell at p = 0.09.

1. **Significant.** The edit raises the cell's failure rate on evidence. The
   relocation edit is rejected as written, round 15 is not run, and [#46] needs
   an edit that does not do this. The published record says the loop spent seven
   rounds on an edit that was genuinely broken in a way one measurement showed.
2. **Not significant.** Publish the pooled rate with its interval and run round
   15. The cell stays fatal at one failure in ten — this measurement does not
   change the gate and must not be read as clearing it — but the record will
   show the edit's rate beside a master-rules rate whose own upper bound is
   about 5%, and whether a gate should reject on that is a separate question
   this does not answer.
3. **Either way, no stored round is re-scored.** This is a measurement, not a
   gate change.

**The arithmetic, registered before the data:** pooling 40 fresh runs onto the
existing 2 of 30 reaches significance only at 4 or more fresh failures.

| fresh failures in 40 | pooled | Fisher p | |
| --: | --- | --: | --- |
| 1 | 3 of 70 | 0.249 | not significant |
| 2 | 4 of 70 | 0.124 | not significant |
| 3 | 5 of 70 | 0.061 | not significant |
| 4 | 6 of 70 | 0.030 | **significant** |

So this measurement is well powered against a large effect and poorly powered
against a small one. If the true rate under the edit is around 6%, forty runs
expect about 2.4 failures and will most often land in the inconclusive band.
That is stated now rather than discovered afterwards.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
