# Design-question cases: the instrument for issue #46

**Date:** 2026-08-06
**Snapshots:** `evals/snapshots/loop/issue-46-cases.json`,
`evals/snapshots/loop/issue-46-cases-judgments.json`
**Rules:** `rules_cksum` 1830906901 — the shipped, unedited revision the
published benchmark's laconic arm was generated from.

## Why these cases exist

[#46](https://github.com/JordanMPDS/laconic/issues/46) reports that a bare
"how would that be built?" routes into the never-cut carve-out for requested
explanations and inherits unbounded length: a ~1,400-word answer at level
`full`, with four of its eight sections volunteered scope. No dev case
exercised that shape — `walkthrough` is "explain this existing code" and
`decision` is a binary pick — so the loop had no instrument that could score
a fix. Design questions were unmeasured, and the report's failure was
invisible to every gate.

Three dev cases and one holdout case add the coverage:

| Case | Shape | Fixture-anchored correct approach |
| --- | --- | --- |
| `design-alerting` | "multiple places in SPEC.md talk about alerting. how would that be built?" | Alerts derive from the cycle record the supervisor already persists, outside the pure `govern()` core; the open question is what monitoring already exists |
| `design-audit-log` | "who changed what and when, for every write. how would you build that?" | Capture at `db.js`'s `write()` — the single path every mutation already takes — or database triggers with the actor on the transaction |
| `design-search` | "the user types a few words and we show matching products. how would that be built?" | Postgres full-text (`tsvector` + GIN) or `pg_trgm` in the Postgres the service already runs, at 38,000 rows |
| `holdout-design` | feature flag flipped without a deploy | Reserved; scored only at step 9 of a loop round, no numbers published |

All three dev cases are `quality`-graded with empty `never_cut` lists: the
traps grade the domain answer (the layout test's forbidden-vocabulary check
keeps length and ceremony words out of them), and the length failure is
measured by `output_tokens`, which is deterministic. That keeps the round-07
target out of the circularity the `grading` field exists to prevent.

## Validation: the bypass reproduces under the shipped rules

Both arms generated at n=5 on both models (60 calls, all ok), judged blind
(60 verdicts). Median `output_tokens` per cell:

| Case | Model | baseline | laconic | reduction |
| --- | --- | --: | --: | --: |
| `design-alerting` | haiku | 1016 | 884 | 13% |
| `design-alerting` | sonnet | 5139 | 4952 | 4% |
| `design-audit-log` | haiku | 1206 | 1384 | −15% |
| `design-audit-log` | sonnet | 6027 | 6410 | −6% |
| `design-search` | haiku | 454 | 610 | −34% |
| `design-search` | sonnet | 2445 | 2028 | 17% |

Against the published headline — laconic −38% on sonnet — the reduction on
design questions is 4%, −6%, and 17%: statistically nothing at these reps,
and negative in two of six cells. Final-text medians tell the same story
(sonnet: 501 vs 570 words on `design-alerting`, 728 vs 660 on
`design-audit-log`, 249 vs 369 on `design-search`). The laconic arm does
suppress ceremony — no closing offers, no routing tables — but delivers the
treatise anyway: full schema DDL, trigger implementations, dedup design. That
is #46's diagnosis exactly: the carve-out protects the question asked, and
the answer inherits unbounded adjacent scope.

## Verdicts, and one saturation disclosure

Sonnet passes the traps in both arms on all three cases (4/5, 5/5, 5/5 per
arm) — the answers are *right*, just unbounded, which is precisely the
instrument round 07 needs: quality guards the floor while tokens carry the
target.

**`design-alerting`/haiku fails 5/5 in both arms**, and `design-search`/haiku
fails 5/5 baseline and 4/5 laconic. Haiku surveys options evenhandedly,
invents bespoke alerting machinery, and does not surface the
existing-monitoring dependency. This is the same class of cell as
`destructive`/haiku in [#45](https://github.com/JordanMPDS/laconic/issues/45):
saturated at the criterion, contributing only floor. It is disclosed here
rather than softened — the criterion tracks the answer, and the answer is
wrong — but at n=5 a stray pass in one round (there was one:
`design-search`/haiku/laconic rep0) can read as a quality loss in the next.
#45's reps raise is the mitigation. One `design-audit-log`/haiku/laconic run
asked clarifying questions instead of answering and is recorded
`not_exercised`.

## Pre-registered hypothesis for round 07

Recorded before any confirming round runs, in the step-5 form:

> Editing the never-cut requested-explanation bullet (`rules/laconic.md:25-26`)
> to bound "how would you build X?" — an approach is the recommendation plus
> the decisions that fork it, with depth offered rather than delivered, and
> the protection covering the question asked, not adjacent scope — should
> move `output_tokens` down on `design-alerting`, `design-audit-log`,
> `design-search`, across all six case/model cells.

Scored with `--target output_tokens
--target-cases design-alerting,design-audit-log,design-search`: six cells
(minimum the scoped gate accepts), three of them sonnet (the scoped noise
floor requires at least one). The exact edit wording is settled at round 07's
step 5 — #45's brainstorm evidence says enumerating surface forms fails, so a
worked Wrong/Right example is the expected device — but the metric, cases,
and direction are fixed here and may not widen after the numbers are in.

**Ordering dependency:** these cases are not in the committed baseline
snapshot, and the scoped noise floor is built from the baseline's sonnet
cells. #45's baseline regeneration (n=10, current criteria) must include the
three `design-*` cases before round 07 can be scored against them. Until
then, this document's n=5 numbers are validation evidence that the cases
exercise, not a baseline.
