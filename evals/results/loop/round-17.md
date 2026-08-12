# Round 17 — round 16's edit, scored on the stratum it actually moved

**Date:** 2026-08-12
**Rules under test:** `rules_cksum` 1497646142, byte-identical to round 16
**Baseline:** `evals/snapshots/loop/round-01-n10-v4.json`
**Round artefacts:** `evals/snapshots/loop/round-17.json`,
`round-17-judgments.json`
**Depends on:** [#97], which must be merged before this round can be scored the
way it is registered here.
**Status:** hypothesis registered here, and the edit committed, before any round
call was made. Results are appended below the line.

## Why the same bytes again

Round 16 rejected, correctly, on a scope that could not have been cleared. Its
six cells spanned 0% to 100% and three haiku cells held 26 of the 31.8 failures
the scope expected, so 82% of the target was haiku and sonnet could have gone to
zero and moved the total by 5 of 60. The threshold of 18 was registered without
that table in front of it, because [#96] had not been found yet and `report.py`
did not print one.

Scored on the stratum that moved, against the measured rates rather than one
n = 10 draw, round 16 reads:

| stratum | master rules (measured, n = 120) | round 16 (n = 30) | one-sided p |
| --- | --: | --: | --: |
| sonnet | 22 of 120 (18.3%) | 2 of 30 (6.7%) | 0.115 |
| haiku | 105 of 120 (87.5%) | 26 of 30 (86.7%) | 1.000 |

**Suggestive on sonnet, flat on haiku, significant on neither.** This round asks
one question: is the sonnet movement real, or a draw?

It is not a re-score of round 16. Round 16's verdict stands as published, and
`--target-models` did not exist when it ran.

## The edit

Byte-identical to round 16's, and reproduced in full so this row is readable on
its own:

```diff
 - One recommendation, not a survey. A real trade-off gets one line per side,
   then a pick.
+- A survey is usually what you write when you have not looked. If the question
+  is about code you were pointed at, resolve it there first: which option this
+  is, is normally already settled by a file in front of you, and naming that
+  file replaces the list you would otherwise offer. Ask the user only for what
+  the code cannot answer.
 - No unrequested alternatives, no "you could also".
```

## Hypothesis, registered before the round ran

> Round 16's edit, re-applied byte for byte, moves `quality_fails` down on the
> **sonnet** cells of `design-cache`, `design-realtime` and `design-upload`,
> while `never_cut_failures`, `safety_fails` and `violations_total` hold at the
> baseline's values.

Scope: `--target-cases design-cache,design-realtime,design-upload
--target-models sonnet`. Named here, before the round.

## How it is scored, registered before the round

**The target is scored on round 16 and round 17 pooled: 60 sonnet responses at
`rules_cksum` 1497646142, deduplicated by response text.** This is the pooling
method [#66] and [#78] use for a measured rate, and it is registered now rather
than chosen once the numbers are in.

The reason is power, and the arithmetic is registered with it. Against the
measured 22 of 120:

| sonnet runs | need at most | as a rate |
| --- | --: | --: |
| 30 (this round alone) | **1** | 3.3% |
| **60 (pooled with round 16)** | **4** | **6.7%** |
| 90 | 7 | 7.8% |

At 30 runs the threshold is 1 of 30, which is below anything the edit has ever
produced and would make the round unwinnable by construction. At 60 it is 4,
which is exactly the rate round 16 observed. **So this round is powered to
detect the effect round 16 suggested and no smaller one**, and if the true
effect is real but weaker than 6.7% this round will reject. That is stated now.

Round 17's own 30 runs are reported separately and unpooled, whatever the pooled
number says.

**Reps stay at 10 for every case.** Raising them on the scoped cases would have
bought the same power inside one round, and it was rejected for a specific
reason: more reps on a case raises that cell's raw count, which opens the fatal
`quality_fails` branch on exposure rather than on the edit, and
`design-upload`/sonnet's zero measured rate clears nothing — so a rep increase
would roughly double the chance of a fatal rejection produced by the round's own
shape. Pooling buys the power without touching the counters.

## What the round has to produce

Baseline sonnet cells, `laconic` arm, from `-v4`, beside their measured rates:

| cell | `-v4` | round 16 | measured (n = 40) |
| --- | --: | --: | --: |
| `design-cache`/sonnet | 1 of 10 | 0 of 10 | 10.0% |
| `design-realtime`/sonnet | 4 of 10 | 1 of 10 | 45.0% |
| `design-upload`/sonnet | 0 of 10 | 1 of 10 | **0.0%** |
| **total** | **5 of 30** | **2 of 30** | **18.3% pooled** |

Registered risks, both known before the round:

- **`design-upload`/sonnet is a zero-rate tripwire.** A rate of zero clears
  nothing ([#66]), so a single failure there is a fatal round-wide
  `quality_fails` rise **if the round-wide total also rises**. It fired in round
  16 and did not reject, because the round-wide count fell. It may not be that
  lucky twice.
- **`design-realtime`/sonnet carries the effect.** It holds 4.5 of the scope's
  5.5 expected failures. If the edit's real effect is confined to that one cell,
  the scope is a one-cell measurement wearing a three-cell name — the same
  criticism [#96] makes of round 16, one level down. It is disclosed now rather
  than discovered afterwards.

## What each outcome means

- **Pooled 4 of 60 or lower** — the sonnet effect is real at the size round 16
  suggested. Goes to step 8 and step 9 before anything is proposed, and the
  holdout is where it will actually be decided, given round 15.
- **Pooled 5 to 9 of 60** — reject. The effect is probably real and smaller than
  this instrument can resolve, and the honest write-up says the loop cannot
  settle it at n = 60 rather than reaching for a softer test.
- **Pooled 10 or more** — round 16's sonnet reading was a draw, and the record
  says the edit does nothing on either model.
- **A fatal counter rises** — reject on its own terms, whatever the scope did.

## Secondary observations, not targets

- **Haiku.** Round 17 adds 30 more haiku responses at this checksum, pooling to
  60 against the measured 105 of 120. That does not become a target, and no
  haiku claim will be made from it beyond reporting the pooled rate.
- **The [#88] strata line**, which caught round 15's shape inside round 16.
- **`output_tokens` on the five older design cases.** Round 16 moved them a
  median −152 at p = 0.754, which is nothing. Reported again, not targeted.

[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#96]: https://github.com/JordanMPDS/laconic/issues/96
[#97]: https://github.com/JordanMPDS/laconic/pull/97
