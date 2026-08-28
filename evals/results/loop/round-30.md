# Round 30: the arrow paragraph's own remedy relocates the arrow

**Status: PRE-REGISTERED. Written and committed before any generation.**

**Date:** 2026-08-28
**Baseline rules:** `rules_cksum` 136269960 (master)
**Issue:** [#36], narrowed to `walkthrough` by
[`arrows-scope-36.md`](arrows-scope-36.md)

## Hypothesis

> Editing the numbered-list remedy in the arrow paragraph of `rules/laconic.md`,
> so that it says a bullet is prose and moving a chain into one relocates the
> arrow rather than removing it, should lower `violations_total` on
> `walkthrough`, both models.

## Why this edit and not another enumeration

[`arrows-scope-36.md`](arrows-scope-36.md) measured the target at today's rules
and found no form-shaped hole: chains against mappings and list items against
running paragraphs sit where they were at `1830906901`, so four rule revisions
have lowered every form evenly and closed none. Adding a fifth position to the
enumeration is the move rounds 01, 03 and 04 already made, and round 04 drove
`walkthrough`/haiku from 9 arrows to 17 doing it.

This edit is aimed somewhere else: at a licence the paragraph currently grants.
The last line of the `Right:` example reads

> Use a numbered list instead when the user will follow the steps one at a time.

which offers a list as the remedy for a chain. Two things say the model takes it
that way. **61% of surviving arrows are in list items or table rows**, a share
unchanged since `1830906901`. And `docs/benchmark.md` records round 01 scoring
this metric 7 to 0 while "the model went on writing the same chains one list
marker to the left" — the detector was blind to structural lines at the time, so
the relocation read as a fix.

The claim is that the remedy relocates the arrow instead of removing it, and
that closing that reading is a different mechanism from naming another position.

## The edit

One clause, appended to the existing `Right:` line. No new bullet, no new
section, nothing added to the enumeration.

## Target, scope and depth, all registered here

- **Target:** `violations_total`, `--target-cases walkthrough`, both models.
- **Why that metric reads the mechanism cleanly:** on `walkthrough`,
  `violations_total` is 22 of 22 arrows — zero abbreviations, zero
  sentence-initial lowercase — so the scoped count is the arrow count with no
  dilution.
- **Baseline, from `arrows-scope-36.json` at 20 responses:** 22 arrows,
  haiku 10 and sonnet 12; 13 chains and 9 mappings.
- **Depth: 40 reps a side, 160 generations, 0 judge calls.** Set by the power
  calculation below rather than by habit, per round 28's precedent.
- **Design:** both sides interleaved one rep at a time, master from the
  repository and the edit from a separate worktree, so `rules/laconic.md` is
  never modified in the tree the control reads. This is the method
  [`interleaved-batch.md`](interleaved-batch.md) established and
  [#120] verified as sequential.

### Power, computed against the test that will score it

`violations_total` is scored by `_cluster_count_p`, a bootstrap over responses
rather than runs ([#103]), because arrows cluster: haiku's 10 baseline arrows
come from 2 of 10 responses and one response carries 8. Resampling the observed
per-response distribution and thinning the edit side:

| reps a side | 40% reduction | 50% | 65% | 80% |
|---|--:|--:|--:|--:|
| 25 | 32% | 50% | 78% | 96% |
| **40** | **52%** | **70%** | **93%** | **100%** |

False-positive rate is 5% at zero effect, so the test is calibrated. At 25 reps
a side a halving is a coin flip, which is why this round buys 40.

**What this round can and cannot resolve, stated before it runs:** it is well
powered for a reduction of 65% or more, adequately powered at 50%, and
underpowered below 40%. A null here is not evidence that the edit does nothing
smaller than half.

## Registered outcomes

- **Accept** if the scoped `violations_total` falls at the clustered bootstrap's
  alpha of 0.05, and no fatal counter rises round-wide.
- **Reject** otherwise, and revert the edit.
- Either way this round is a fifth data point for [#34] on whether an enumerated
  prohibition can close, and the composition split will be re-measured and
  reported alongside the count.

## Results

_Not yet generated._

[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#36]: https://github.com/JordanMPDS/laconic/issues/36
[#103]: https://github.com/JordanMPDS/laconic/issues/103
[#120]: https://github.com/JordanMPDS/laconic/issues/120
