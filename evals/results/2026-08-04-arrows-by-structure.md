# Arrows are a property of structured answers, not of the level

Closes [#20](https://github.com/JordanMPDS/laconic/issues/20). No API calls: this
re-reads the three committed level snapshots
(`evals/snapshots/levels-{lite,full,ultra}.json`, 330 laconic responses, 11 cases
× 5 reps × 2 models × 3 levels) with the detector the repository ships today.

Reproduce with `python3 evals/bench/levels.py`, section **Arrows against
structure, not level**.

## What #20 asked

The three-level run reported 12 arrow violations at `lite` against 0 at `full`
and 0 at `ultra`, all of them on sonnet. The issue proposed a hypothesis and a
test that costs nothing: score arrows per response against that response's own
scaffolding count, and see whether the arrows follow the level or follow the
shape of the answer.

## The premise is already gone

The `lite` 12 / `full` 0 split was a detector artifact. That detector skipped
bullets, numbered steps and blockquotes, which is exactly where a runbook arrow
lives; [#29](https://github.com/JordanMPDS/laconic/pull/29) fixed it and
recounted. Both counts, from the same snapshots:

| level | arrows, detector as of 2026-07-31 | arrows, detector today | responses carrying one |
| --- | --: | --: | --: |
| `lite` | 12 | 25 | 9 / 110 |
| `full` | 0 | 23 | 5 / 110 |
| `ultra` | 0 | 16 | 4 / 110 |

`lite` 9 responses against `full` 5, Fisher's exact two-sided **p = 0.41**;
`lite` against `ultra`, p = 0.25. There is no level effect to explain. The old
zero at `full` was the detector not looking, not the model not writing.

Per model, the direction does not even hold: haiku writes its most arrows at
`full` (18, against 9 at `lite`), sonnet at `lite` (16, against 5 at `full`).

## Where the arrows actually are

Bucketing the same 330 responses by how much scaffolding each one carries —
bullets, numbered steps and bold labels, counted on code-stripped prose by
`metrics.structure_markers`:

| structure markers | responses | with an arrow | arrows |
|---|--:|--:|--:|
| 0 | 111 | 0 | 0 |
| 1-4 | 87 | 1 | 1 |
| 5-9 | 70 | 0 | 0 |
| 10-19 | 45 | 11 | 32 |
| 20+ | 17 | 6 | 31 |

By case, all three levels pooled:

| case | responses | with an arrow | arrows | mean structure |
|---|--:|--:|--:|--:|
| walkthrough | 30 | 11 | 46 | 19.3 |
| ordered-steps | 30 | 6 | 14 | 16.0 |
| destructive | 30 | 1 | 4 | 5.4 |
| the other eight cases | 240 | 0 | 0 | 0.6 - 4.9 |

Pearson r between a response's structure count and its arrow count is **0.41**
over 330 responses. Outside `walkthrough` and `ordered-steps`, **one response of
270 carries an arrow** — the four in `destructive`/sonnet the issue quoted. Inside
those two cases, 17 of 60 do, at every level: `lite` 21 arrows, `full` 23,
`ultra` 16.

## What this does and does not establish

It rules out the level. Same prohibition text above the first level marker, same
violation rate either side of it, and the per-model directions disagree. #20
should not be worked as a level-boundary problem, and the loop should not spend a
350-call round on one.

It does **not** establish that scaffolding causes the arrow. Structure count and
case identity are nearly collinear here: only two of eleven cases carry heavy
structure, so "an answer with a runbook in it draws arrows" and "these two
prompts draw arrows" fit this data equally well. Separating them needs cases that
vary structure within a task, which the benchmark does not have. r = 0.41 is a
correlation across 330 responses drawn in one generation, not an effect size.

## Verdict

Recorded as a rate too low to act on **as a level phenomenon**, which is one of
the two outcomes #20 allows. `rules/laconic.md` is unchanged, so
`tests/test_rules.sh` needs no new assertion.

The arrow problem itself is real and stays open, but it belongs to the two
structured cases rather than to `lite`. That target is already the loop's:
round 03 edited the arrow headline to say a bullet and a numbered step are prose
too, aimed at exactly `walkthrough` and `ordered-steps`, and it was rejected and
reverted ([ledger](loop/LEDGER.md)). The next attempt on arrows should be scoped
to those cases and judged there, not at a level boundary.
