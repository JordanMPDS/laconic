# The n=10 loop baseline, and the destructive/haiku exclusion (#45)

**Date:** 2026-08-06
**Snapshots:** `evals/snapshots/loop/round-01-n10.json`,
`evals/snapshots/loop/round-01-n10-judgments.json`
**Rules:** `rules_cksum` 1830906901 — unchanged; this is instrument work, not a
rule edit.

## What changed and why

[#45](https://github.com/JordanMPDS/laconic/issues/45): rounds 05 and 06 both
partly died on measurement noise. At n=5, `walkthrough`/sonnet's reps spanned
1520–4573 and its headline −1947 drop did not replicate; the safety lottery
(one stray verdict flip per round) rejected rounds on its own. Two changes:

1. **The loop baseline is regenerated at n=10** over all 14 cases — the 11
   pre-#47 cases plus the three `design-*` cases #46's round will target.
2. **`destructive`/haiku is marked saturated** in its `expect.json` and
   excluded from the fatal judge-verdict counters (see
   `evals/results/2026-08-06-design-question-cases.md`'s sibling change in
   `evals/CRITERIA.md` for the bar). 30/30 fails across six gradings; the
   response text was re-read against the criterion — haiku frames `sessions`'
   `ON DELETE CASCADE` as exempting it from the drop, which the PostgreSQL 16
   verification behind #18 settled as wrong. Capability floor; the cell stays
   generated, judged, and displayed.

## How the snapshot was built

- laconic arm: 280 fresh calls (14 cases × 2 models × 10 reps), sharded by
  case, generated 2026-08-06 under the shipped rules.
- Controls for the 11 pre-#47 cases: carried at n=5 from
  `evals/snapshots/results.json`, per the loop's standing carry rule; their
  judgments seeded from `evals/snapshots/judgments.json` (same criteria, same
  `rules_cksum`, byte-identical responses).
- Controls for the three `design-*` cases: 90 fresh calls at n=5, matching
  the other controls' reps; judged fresh.
- Coverage: 700 runs, 0 failed; 700/700 judged.
- `prefer.py` pairs only reps present in both arms, so preference in future
  rounds covers laconic reps 0–4 against the n=5 controls; reps 5–9
  contribute to tokens, verdicts, and readability only.

## The new noise floor

`report.py`'s `NOISE` stdev — the median per-cell output-token stdev over the
laconic arm's sonnet cells — moves 209 to **260** (14 cells at n=10, from 11
cells at n=5). The rise is honest: the three design-question cells disperse at
322–954, among the widest in the suite. The scoped floor for
`design-alerting`, `design-audit-log`, `design-search` comes out at **575
tokens** — a round-07 edit must move the scoped median past that, which a real
effect on cells sitting at 2264–6544 median tokens can clear and a noise
wobble cannot.

Per-cell sonnet stdevs, n=10: badnews 67, code-fidelity 60, conditional 78,
decision 162, design-alerting 575, design-audit-log 954, design-search 322,
destructive 1203, fail-open 202, floor 14, ordered-steps 318, silent-success
101, stale-cache 842, walkthrough 1167.

## The counters round 07 will be compared against

From `round_summary` over this baseline (laconic arm, 280 runs):

| counter | value | notes |
| --- | --: | --- |
| `never_cut_failures` | 2 | both `conditional`/sonnet dropping "leak" — the known lottery cell, now measured at n=10 |
| `quality_fails` | 41 | 25 from the three `design-*` cases; `stale-cache` contributes 16 (7 haiku, 9 sonnet) |
| `safety_fails` | 6 | `destructive`/haiku's 10 fails are excluded and disclosed; `destructive`/sonnet 3, `ordered-steps` 3 |
| `violations_total` | 78 | the design cases add arrow violations — the long design answers bring arrow habits with them |

Two cells the n=10 view sharpens, disclosed for round 07's reading:

- **`design-alerting`/sonnet fails quality 4/10** (the n=5 validation read
  1/5). The cell is live, not saturated — sonnet sometimes builds the alert
  evaluation into the pure core. A rule edit about length must not be
  credited or blamed for movement here; the quality gate stays round-wide.
- **`design-alerting`/haiku and `design-search`/haiku fail 9/10** — nearly
  saturated, as the validation predicted, but not constant. They stay in the
  counters; if they stay pinned across future rounds the `saturated_models`
  bar in `evals/CRITERIA.md` applies.

## What this unblocks

Round 07, pre-registered in
`evals/results/2026-08-06-design-question-cases.md`: target `output_tokens`
on `design-alerting,design-audit-log,design-search`, scored against this
baseline with the scoped floor above. The loop skill now points `PREV` at
this snapshot and carries arms from it — carrying from
`evals/snapshots/results.json` would drop the design-case controls.

The public benchmark tables in `docs/benchmark.md` still describe the 11-case
n=5 published run; they refresh at the next full benchmark publish, not here.
