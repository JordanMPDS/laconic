# Round 08 — mutual exclusion between the approach license and ordered steps

**Date:** 2026-08-07
**Rules under test:** `rules_cksum` 1823644123
**Baseline:** `evals/snapshots/loop/round-01-n10.json`
**Status:** hypothesis registered, confirming round not yet generated

## Hypothesis (registered before generation; this commit precedes the snapshot)

> Round 07's design-question bound, plus mutual exclusion written into both
> bullets — "an ordered procedure is never a design question: if the user
> will execute the answer as steps, the next bullet governs", and the
> ordered-instructions bullet declaring it outranks the approach license —
> should move `output_tokens` down on `design-alerting`, `design-audit-log`,
> `design-search` across all six cells (round 07 showed the bound does this),
> while `ordered-steps` stops regressing: `safety_fails` and
> `never_cut_failures` hold at or below the baseline's 6 and 2.

Scored with `--target output_tokens
--target-cases design-alerting,design-audit-log,design-search` against
`round-01-n10`. The exclusion is worded generically on purpose: naming key
rotation would teach to `ordered-steps`' and `holdout-ordered`'s shared
domain.
