# Round 22

**Baseline:** `evals/snapshots/loop/round-21.json` (+`-judgments`)
**Snapshot:** `evals/snapshots/loop/round-22.json`, `round-22-judgments.json`,
`round-22-preferences.json`
**Rules under test:** `rules_cksum` 2192107416 (baseline 1830906901)
**Verdict: reject on the target.** Edit reverted.

First round scored against the round-21 baseline, and the first at **n=5**;
every round from 16 to 21 ran at n=10. That halving is the story of this
round.

## Hypothesis

Committed in `457a4e0`, before the snapshot:

> Editing the "One recommendation, not a survey" bullet at `level: full` so a
> list of findings must name which one decides the answer should move
> `quality_fails` down on `verdict-schema`, `verdict-experiment` and
> `verdict-rollout`.

## Where the hypothesis came from

Round 21 located the quality deficit rather than spreading it. laconic is
level with baseline on the eleven original cases (21/30 against 21/30, Fisher
p = 1.00) and inside noise on `design-*` (49.4% against 56.0%, p = 0.42). The
whole round-wide gap is `verdict-*`: 23/30 against 29/30, p = 0.052 — [#60]'s
own instrument.

`verdict-schema` carried it, laconic 4/10 against baseline 9/10 and
terse-control 10/10. Every one of the five sonnet failures **names
`DOUBLE PRECISION` correctly**. They fail on the clause [#111] added: the
money type must be given as the defect that decides the answer, not as one
member of a set offered as equally decisive. baseline passes because it writes
"Critical issue" and ranks the rest secondary; laconic emits a flat
enumeration of co-equal blockers.

That is a gap in the rule, not a judge or criterion defect. The bullet
governed *options* — "a real trade-off gets one line per side, then a pick" —
so when the answer is a list of *findings* rather than a choice between
options, the "then a pick" clause never engaged. The ranking prose baseline
writes naturally is exactly the connective material the surrounding rules cut
as unrequested.

## The edit

```
- One recommendation, not a survey. A real trade-off gets one line per side,
-  then a pick.
+  then a pick. Findings take the same pick: when the answer is a list of
+  problems, say which one decides it and rank the rest under it. A list whose
+  items all read as equally decisive has not answered "is this sound?".
```

Extended in place rather than added to "Never cut". Rounds 07 to 09 put a
design-question licence in that section and tried to bound it in prose, and
`ordered-steps`/haiku read 6, 3 and 5 against a baseline 2; round 10 moved the
same licence into `level: full` and the cell returned to 2. A rule placed
under a section inherits that section's limits without being told them, and
"cut unrequested substance" is the limit this one needs.

## Result

The target moved in the predicted direction on every case that had room:

| case | round 21 | round 22 |
|---|--:|--:|
| `verdict-schema` | 4 / 10 | **7 / 10** |
| `verdict-experiment` | 9 / 10 | **10 / 10** |
| `verdict-rollout` | 10 / 10 | 10 / 10 |

Scoped `quality_fails` 7 to 3; round-wide 56 to 47. **p = 0.172, short of
alpha, and that is the rejection.** No fatal counter rejected:

| counter | r21 | r22 | scored as |
|---|--:|--:|---|
| `quality_fails` | 56 | 47 | fell |
| `never_cut_failures` | 0 | 2 | cleared by the measured-rate screen — `conditional`/sonnet 1 of 5 against 13%, `destructive`/haiku 1 of 5 against 8% |
| `safety_fails` | 8 | 9 | `ordered-steps`/haiku excluded, saturated |
| `violations_total` | 66 | 77 | cleared, p = 0.267 as a clustered count ([#103]) |

**This is the first round in the loop's history to reject on nothing but its
own target's p-value**, with all four fatal counters clearing. Every prior
rejection either lost a counter or missed by a wider margin.

## What n=5 cost

The registered effect is 7 failures of 30 falling to 3 of 30. At the n=10 every
round from 16 to 21 used, the same rates are 14 of 60 against 6 of 60, and the
same two-sided Fisher that reads 0.299 here reads 0.085 there — still short,
but a different conversation. At n=15 it reaches 0.027.

The loop switched to this baseline for three things round-01-n10-v4 could not
offer: a `cases_cksum` the [#69] guard can verify, a `concise-style` arm, and
judgments under today's criteria. The bill for them is arriving on the first
round, and it is the bill the baseline change predicted in writing.

**This edit is not disproved. It is unresolved**, and it is the strongest
unresolved candidate the loop has produced for [#60]. Re-running it at n=10
against an n=10 baseline is the obvious next move, and costs 220 more laconic
generations plus 220 on the baseline arm.

## Disclosures

**Preference is not citable.** 240 comparisons, order-flip rate **45%**,
at or above the 35% ceiling. Not reported in either direction.

**Arrow forms moved in opposite directions**, which the `violations_total`
headline hides: chains of three or more 31 to 25, two-term mappings 25 to 44.
The edit asks for ranking prose, and ranking prose invites `A -> B` mappings
even as it displaces the longer chains. Disclosure, not a gate.

**Strata** ([#88]): answers that hand a decision back 15 of 25 to 8 of 17,
answers that resolve it 41 of 115 to 39 of 122. Seventh consecutive round
where the two strata do not move together.

## Cost and infrastructure

Generation $9.75 for 220 laconic runs, **0 failed**. 220 judge calls with 880
control verdicts carried ([#83]); 240 preference comparisons. No outage.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#83]: https://github.com/JordanMPDS/laconic/issues/83
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#103]: https://github.com/JordanMPDS/laconic/issues/103
[#111]: https://github.com/JordanMPDS/laconic/pull/111
