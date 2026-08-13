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

---

# Results

**Reject, on two grounds.** Edit reverted; master stays at 1830906901.

```
verdict: reject (target quality_fails on design-cache, design-realtime,
                 design-upload (sonnet only), against round-01-n10-v4.json)
  REJECT: never-cut lost (2 -> 3); cells: walkthrough/haiku +1 (arbitrable)
  REJECT: quality_fails 5 -> 3 on design-cache, design-realtime, design-upload
          (sonnet only), p = 0.234; scored against the measured rate 22 of 120
```

## The registered target: 5 of 60, against a threshold of 4

| | sonnet fails |
| --- | --: |
| round 16 | 2 of 30 |
| round 17 | 3 of 30 |
| **pooled, deduplicated by response text** | **5 of 60 (8.3%)** |
| master rules, measured | 22 of 120 (18.3%) |

Nothing deduplicated away; all 60 responses are distinct. One-sided
**p = 0.072** against a registered threshold of **4 of 60**.

**This is registered outcome 2, word for word**: *"Pooled 5 to 9 of 60 — reject.
The effect is probably real and smaller than this instrument can resolve, and
the honest write-up says the loop cannot settle it at n = 60 rather than
reaching for a softer test."*

The rate halved, 18.3% to 8.3%, in the same direction across two independent
rounds, and it missed alpha by 0.022. That is the most likely reading and it is
not evidence.

## The other rejection, and why it was not arbitrated

`never_cut_failures` 2 → 3, all of it `walkthrough`/haiku going 0 → 1.

**That cell has no measured rate.** `cell-rates.json` covers `conditional`/haiku,
`conditional`/sonnet and `destructive`/haiku for never-cut, so `walkthrough`
/haiku is still scored the pre-[#66] way: one n = 10 baseline draw against one
n = 10 round draw. It is exactly the situation [#66] describes and deliberately
left in place for cells nobody has measured.

The loss is arbitrable by replication. **It was not arbitrated**, because the
round rejects on its target independently and arbitration could not change the
verdict — only the reason list. Spending ~20 calls to remove one of two
rejections would buy nothing. If a future round wants `walkthrough`/haiku
screened, the fix is 40 generations to measure it, not an arbitration.

## Round-wide

| metric | `-v4` | **r17** | r16, same edit |
| --- | --: | --: | --: |
| `never_cut_failures` | 2 | **3** | 2 |
| `quality_fails` | 83 | 77 | 74 |
| `safety_fails` | 4 | 4 | 4 |
| `violations_total` | 158 | **121** | 125 |

The readability improvement reproduces: 158 → 125 in round 16 and 158 → 121
here, on byte-identical rules. That is the most consistent thing this edit does,
and it is not what the edit was written for and was never its target.

## Haiku, pooled, still flat

Secondary and not a target, reported because it was registered:

| | haiku fails |
| --- | --: |
| pooled r16 + r17 | 51 of 60 (85.0%) |
| master rules, measured | 105 of 120 (87.5%) |

Fisher **p = 0.647**. At n = 60 the reading is unchanged from round 16's n = 30:
no detectable movement. Round 16's write-up said the effect was "unmeasured on
haiku" rather than absent; doubling the sample did not change that, and it is
now a 60-run null rather than a 30-run one.

## The registered risk that materialised

`design-upload`/sonnet, the zero-rate tripwire, contributes **2 of the 5 pooled
failures** — 2 of 20 against a measured 0 of 40, Fisher p = 0.107.

So the scope's improvement is being partly offset by the one cell that fails
never under master rules. Two readings, and n = 20 cannot separate them: the
edit slightly harms that cell, or a 0-of-40 measurement understated a small
non-zero rate. Either way the cell is doing the opposite of what the scope
needs, and it was named as a risk before the round rather than after.

Per cell, pooled: `design-cache`/sonnet 1 of 20, `design-realtime`/sonnet 2 of
20, `design-upload`/sonnet 2 of 20. **The effect is not concentrated in
`design-realtime` after all**, which was the other registered worry, and that
one did not materialise.

## Tokens, reported because registered

Seven of ten older design cells down, sign test p = 0.344, median shift 53
tokens. Nothing, and consistent with round 16's −152 at p = 0.754. **This edit
does not shorten design answers**, across two rounds and 20 cell-measurements.

## The [#88] strata line

```
answers that hand a decision back 22 of 47 -> 25 of 47,
answers that resolve it 61 of 233 -> 52 of 233; the two strata moved in
OPPOSITE directions
```

Third round running, third time the same shape: resolving answers improve,
asking answers get worse. Round 16 read 22 of 47 → 28 of 44 and this reads 22 of
47 → 25 of 47, so the effect is smaller here but the sign is identical.

## What this round establishes

1. **The sonnet effect is probably real and this instrument cannot prove it.**
   Two rounds, same direction, 18.3% to 8.3% pooled, p = 0.072. The registration
   said a smaller-than-6.7% effect would reject, and an 8.3% one did.
2. **Settling it costs more than it is worth at this scale.** At the observed
   8.3%, the expected count sits just above the threshold at every sample size
   worth running:

   | sonnet runs | threshold | expected at 8.3% |
   | --: | --: | --: |
   | 90 | 7 | 7.5 |
   | 120 | 11 | 10.0 |
   | 240 | 26 | 20.0 |

   120 runs is the first size where the expected count clears, and that is 60
   more generations plus 60 judge calls for a coin-flip on a rule that does not
   shorten anything.
3. **The edit's reproducible effect is on readability, not on design quality.**
   `violations_total` 158 → 125 and 158 → 121 across two rounds. If this rule is
   worth another attempt, that is the target to register, and it is a different
   hypothesis from the one this round tested.

## Costs and the outage

440 generations and 440 judge calls, with 660 control verdicts carried ([#83]).
Fourth service outage in two days: 100 of 440 generations failed and [#61]'s
resume repaired all of them, after which judging ran with 0 infrastructure
failures.

**One near-miss worth recording.** `git rebase` was run against this branch while
generation was in flight, which briefly left the working tree at master's rules —
[#69] exactly. No run was contaminated: `run.py` resolves the system prompt once
at startup, so the five in-flight processes kept the edit's text, and every one
of the 22 shard files is stamped 1497646142. The window was short enough that no
new shard started under master's rules, which was luck rather than design. #69 is
still open and this is the second time it has nearly cost a round.

[#61]: https://github.com/JordanMPDS/laconic/issues/61
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#83]: https://github.com/JordanMPDS/laconic/issues/83
