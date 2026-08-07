# Round 09 — the round-08 edit under the matched instrument

**Date:** 2026-08-07
**Rules under test:** `rules_cksum` 1823644123 — byte-identical to round 08's edit
**Baseline:** `evals/snapshots/loop/round-01-n10.json`
**Status:** hypothesis registered, confirming round not yet generated

## Hypothesis (registered before generation; this commit precedes the snapshot)

> The round-08 edit unchanged — the design-question bound plus mutual
> exclusion with ordered instructions — moves `output_tokens` down on
> `design-alerting`, `design-audit-log`, `design-search` across all six
> cells past the matched all-cells scoped floor (#51, merged before this
> commit), with `safety_fails` and `never_cut_failures` holding at baseline;
> any fatal count loss composed entirely of +1 flips goes to one replication
> arbitration (#52) and is expected not to reproduce.

Round-08's own sample is not reused: #51 and #52 were derived from its
failures, and scoring the sample that tuned the instrument would be
circular. Fresh generation, same procedure as rounds 07 and 08.
