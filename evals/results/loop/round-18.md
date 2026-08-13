# Round 18 — a bullet is prose, and the rule's own remedy was the escape hatch

**Date:** 2026-08-13
**Rules under test:** `rules_cksum` 4146642931
**Baseline:** `evals/snapshots/loop/round-01-n10-v4.json` (+`-judgments`)
**Round artefacts:** `evals/snapshots/loop/round-18.json`, `round-18-judgments.json`
**Depends on:** [#103], which must be merged before this round can be scored the
way it is registered here.
**Status:** hypothesis registered here, and the edit committed, before any round
call was made. Results are appended below the line.

## Why readability, and why not the edit that produced it

Round 17 named the target: *"The edit's reproducible effect is on readability,
not on design quality. `violations_total` 158 → 125 and 158 → 121 across two
rounds. If this rule is worth another attempt, that is the target to register."*

Registering it turned up a problem with the instrument first, and then a better
edit than the one that suggested the target.

**The instrument.** `violations_total` was scored by `_count_p`, which assumes
one event per run. It is not that shape: a response that reaches for an arrow
reaches for several, and the per-response counts have a variance three times
their mean. Rounds 16 and 17 read p = 0.029 and p = 0.016 under that test and
p = 0.052 and 0.042 under one that resamples whole responses. **A round
registering this target against the old test would have accepted at 0.016 on an
effect the honest test cannot separate from noise.** Filed and fixed as [#103],
re-scored across all 13 stored edit rounds with 0 verdicts moved.

**The edit.** Rounds 16 and 17 lowered violations as a side effect, and their
own registered target failed twice. Carrying that edit forward would be
carrying the weakest readability effect the loop has produced. The composition
points somewhere else.

## What the violations actually are

`violations_total` on the `-v4` baseline is 158, of which **140 are symbol
connectors** — literal `→` and `->`. The rest are 12 abbreviations and 6
sentence-initial lowercase starts. This metric is an arrow counter.

Every arrow-bearing prose line in the baseline, by the position it sits in:

| position | baseline | round 16 | round 17 |
| --- | --: | --: | --: |
| **bullet item** | **50** | 44 | 49 |
| **numbered list item** | **42** | 27 | 24 |
| running prose | 76 | 81 | 76 |
| table row | 0 | 0 | 1 |

**A list item carries 92 of 168, and the rule never says a list item is
prose.** It says "Never use `→` or `->` in prose", enumerates six positions, and
then — in its own worked example — offers *"Use a numbered list instead when the
user will follow the steps one at a time."*

That sentence is the remedy, and it is being read as an exemption. The model
takes the runbook out of the sentence, puts it in a numbered list, and keeps the
arrow:

```
1. Request arrives → check client identity (key/IP)
3. If yes → return 429 with   header
4. If no → decrement quota, forward request, update state
```

Those three lines are one `design-rate-limit`/haiku response. Nothing in the
rule's enumeration reaches them, because they are not a "quick runbook line" or
a "bold label" or a "quoted flow" — they are a numbered list, which is what the
rule told the model to use.

[#34] asks whether an enumerated prohibition can ever close, on the evidence
that rounds 01 and 03 each fixed the position they named and each saw arrows
appear in the position the other covered. This round is not another position
added to the enumeration. It is the one place the rule created the position
itself.

## The edit

One edit, at the governing sentence rather than in the examples, because where a
rule lives outranks what it says about where it lives.

```diff
-**No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
-steps, stages, states or causes, not to show that one thing maps to or becomes
-another, not after a bold label, not in a "quick runbook" line, not inside a
-quoted flow.
+**No arrows inside a sentence.** Never use `→` or `->` in prose, and a bullet
+or a numbered step is prose: not to chain steps, stages, states or causes, not
+to show that one thing maps to or becomes another, not after a bold label, not
+in a "quick runbook" line, not inside a quoted flow.
```

Round 03 carried a version of this clause — "a bullet and a numbered step are
prose too" — as part of a larger edit, and moved `walkthrough` and
`ordered-steps` **21 arrows to 5**, the largest movement the loop has measured
on a named target. That round was rejected on never-cut, on quality, and on a
round-wide target it could not reach; the clause itself was never the reason.
`--target-cases` did not exist then. This is that clause on its own, scored on
the cells it targets.

**Table cells are deliberately not named.** They carry 1 arrow across three
rounds and 1,320 responses. Naming an unmeasured position is the enumeration
trap [#34] describes.

## Hypothesis, registered before the round ran

> Editing the arrow prohibition's governing sentence to say that a bullet or a
> numbered step is prose moves `violations_total` **down** on `walkthrough`,
> `design-retry`, `design-upload`, `ordered-steps` and `design-alerting`, while
> `never_cut_failures`, `quality_fails` and `safety_fails` hold at the
> baseline's values.

Scope: `--target-cases walkthrough,design-retry,design-upload,ordered-steps,design-alerting`.
Both models. Named here, before the round.

Those five cases hold **81 of the baseline's 92 list-item arrows (88%)** and
**117 of its 158 total violations (74%)** in 10 of the 44 cells.

## What the round has to reach, registered before it ran

Baseline scoped cells, `laconic` arm:

| cell | violations in 10 responses |
| --- | --: |
| `walkthrough`/haiku | 26 |
| `walkthrough`/sonnet | 23 |
| `design-retry`/sonnet | 22 |
| `design-retry`/haiku | 13 |
| `ordered-steps`/sonnet | 11 |
| `design-upload`/sonnet | 6 |
| `design-alerting`/haiku | 5 |
| `design-upload`/haiku | 5 |
| `ordered-steps`/haiku | 4 |
| `design-alerting`/sonnet | 2 |
| **scoped total** | **117** |

Thinning the baseline's own per-response counts and re-running [#103]'s
bootstrap gives the threshold, computed before any round data existed:

| scoped count | reduction | bootstrap p |
| --: | --: | --: |
| 111 | 5% | 0.402 |
| 95 | 19% | 0.147 |
| **83** | **29%** | **0.043** |
| 70 | 40% | 0.005 |
| 57 | 51% | 0.000 |

**The round needs the scoped count at 83 or below.** Eliminating every
list-item arrow in the scope would put it near 36; halving them puts it near 77.
So the edit has to remove roughly half the arrows sitting in list items, and
round 03's precedent on two of these five cases was a 76% removal.

## What each outcome means

- **Scoped 83 or below, no fatal counter lost** — goes to step 8 and step 9.
  Round 15 is the reason step 9 decides this and not step 7.
- **Scoped 84 to 110** — reject. The clause moves arrows but not enough to
  separate from a metric this noisy, and the write-up says so rather than
  reaching for a softer test.
- **Scoped above 110** — the clause does nothing, and [#34]'s question about
  whether enumeration can close gets its clearest answer yet: even closing the
  rule's own escape hatch does not.
- **A fatal counter lost** — reject on its own terms, whatever the scope did.

## Registered risks

- **The round-wide readability counter can no longer reject on noise**, which is
  half of [#103]. Before it, a scoped edit with no round-wide margin had about a
  coin flip's chance of a fatal rise. That is a change to a fatal gate made in
  the same session as this round; it was re-scored across 13 stored rounds
  before this round was registered, and 0 verdicts moved.
- **The baseline's own violations draw is low.** On the six cells where
  `quality-rates-design.json` holds 30 more master-rules runs each, the baseline
  drew 19 against a bootstrap mean of 35.0 (sd 9.4) — the 3rd percentile. Only
  `design-upload` of those six is in this scope, so the effect on the scoped
  number is small, but a low baseline makes any improvement harder to show, not
  easier.
- **`ordered-steps`/haiku is in the scope and carries `saturated_models`.** That
  exclusion covers the judge-verdict counters only; `violations_total` is a
  deterministic detector and the cell votes here. It holds 4 of 117.
- **Arrows may relocate rather than disappear.** Between the baseline and round
  17, numbered-list arrows fell 42 to 24 while numeric progressions rose 28 to
  40. If the scoped count falls and running prose rises by the same amount,
  the round-wide number will say so and it will be reported.

## Secondary observations, not targets

- **Numeric progressions** (`7 → 28 over 2.5 minutes`) are the one position the
  rule never addresses, and the only one growing. `conditional` produces 28 of
  them and 0 list-item arrows. Not in this scope, not this edit, reported.
- The [#88] strata line.
- `output_tokens` on the five older design cases, reported and not targeted.

[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#103]: https://github.com/JordanMPDS/laconic/issues/103
