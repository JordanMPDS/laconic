# Round 22

**Baseline:** `evals/snapshots/loop/round-21.json` (+`-judgments`)
**Snapshot:** `evals/snapshots/loop/round-22.json`, `round-22-judgments.json`,
`round-22-preferences.json`
**Rules under test:** `rules_cksum` 2192107416 (baseline 1830906901)
**Verdict: reject on the target, at n=5 and again at n=10.** Edit reverted.

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

## The n=10 rerun

The n=5 round closed by saying the edit was unresolved and wanted a re-run at
n=10. That re-run was bought — both arms, not just the treatment, since an
n=10 round against an n=5 baseline gives the round twice the opportunity to
fail a cell. Snapshots `round-21-n10.json` and `round-22-n10.json`, each
carrying the original 220 laconic runs plus 220 more, 440 per side, **0
failed**. The published `round-21.json` was not touched; the n=10 files are
copies, so every figure in `docs/benchmark.md` still describes the snapshot it
was computed from.

**It rejected again, at p = 0.166 against n=5's 0.172.** Doubling the data
moved the p-value by 0.006.

The reason is not low power. It is that the effect shrank by as much as the
power grew:

| | baseline fails | edit fails | gap |
|---|--:|--:|--:|
| n=5 | 7 / 30 = 23.3% | 3 / 30 = 10.0% | 13.3pp |
| n=10 | 11 / 60 = 18.3% | 6 / 60 = 10.0% | 8.3pp |

**The edit's failure rate is stable at exactly 10.0% on both draws. The
baseline's fell.** Round 21's first five reps were an unlucky draw for master
rules, and the second five regressed it toward its mean. The n=5 round did not
merely lack power — it flattered the edit, and the round doc's own projection
("the same rates at n=10 read 0.085") was wrong because it assumed the n=5
rates were the truth.

Round-wide says it louder. `quality_fails` moved 56 to 47 at n=5, which
doubled would predict about −18; the n=10 movement is **104 to 100**.

Every fatal counter cleared again: `never_cut_failures` 0 to 4 inside the
measured rates (`conditional`/sonnet 2 of 10 against 13%, `destructive`/haiku
2 of 10 against 8%), `violations_total` 138 to 141 at p = 0.457, and
`ordered-steps`/haiku excluded as saturated.

## What it would take, and why the loop stops here

The effect is real, small, and almost entirely one case. `verdict-schema` is
10 of 20 failures against 6 of 20; `verdict-experiment` and `verdict-rollout`
sit at ceiling and contribute one failure between them across 80 responses.

| scope | observed | responses/arm for 80% power | have | reps/cell needed |
|---|---|--:|--:|--:|
| the three cases pooled | 18.3% vs 10.0% | 273 | 60 | **45** |
| `verdict-schema` alone | 50% vs 30% | 90 | 20 | **45** |

Both routes need 45 reps per cell, roughly 4.5x what has been run, on the
order of 900 further generations per side.

**The loop stops here and records it.** Two independent draws agree the edit
moves `verdict-schema` in the right direction by a margin this instrument
cannot resolve at any n worth buying. That is a finding about the benchmark's
resolution rather than about the rules, and it is the reason the row exists in
the ledger.

## Disclosures

**Preference is not citable.** 240 comparisons, order-flip rate **45%**,
at or above the 35% ceiling. Not reported in either direction.

**Arrow forms moved in opposite directions** in both draws, which the
`violations_total` headline hides: chains of three or more 31 to 25 and
mappings 25 to 44 at n=5; chains **75 to 46** and mappings **41 to 77** at
n=10.
The edit asks for ranking prose, and ranking prose invites `A -> B` mappings
even as it displaces the longer chains. Disclosure, not a gate.

**Strata** ([#88]): at n=10, answers that hand a decision back went 29 of 53
to 23 of 41 — **worse** — while answers that resolve it went 75 of 227 to 77
of 238. Seventh consecutive round where the two strata do not move together,
and the n=10 draw makes the direction unambiguous.

## Cost and infrastructure

n=5 round: generation $9.75 for 220 laconic runs, 220 judge calls with 880
control verdicts carried ([#83]), 240 preference comparisons.

n=10 rerun: $19.36 for 440 further generations across both arms, 440 further
judge calls. **0 failed generations across all 880 runs in this round**, and
no outage in either pass.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#83]: https://github.com/JordanMPDS/laconic/issues/83
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#103]: https://github.com/JordanMPDS/laconic/issues/103
[#111]: https://github.com/JordanMPDS/laconic/pull/111
