# Round 38: the rendered specimen is not the carrier

**Rejected. The edit is reverted.** Replacing the two rendered arrow specimens in
`rules/laconic.md` with prose descriptions did not reduce arrows in prose, and
the point estimate moves the wrong way.

The registration and the rules text under test were committed before any
generation, in the same commit.

## What it was testing

[#164] observes that `rules/laconic.md` teaches by `Wrong:`/`Right:` pairs, and
that **half of such a pair is a rendered instance of the form it prohibits**.
Round 31 measured that half travelling: appending one arrow pair moved
`destructive`/sonnet from 0 arrows in 40 runs to 6, with 3 responses carrying
one, on a case the hypothesis never named — and two of the three wrote the added
line's exact shape.

[#164] asked for a scoped test of the device itself:

> generate one batch against a rules file whose arrow examples are stated in
> prose rather than rendered (`a bold label, an arrow and a target` in place of
> the specimen line) and score the same cells. If the specimen is the mechanism,
> the propagation goes and the enumeration's effect stays.

This is that batch.

## The edit

Both `Wrong:` lines in the arrow paragraph, which contained literal `→`
characters, became prose descriptions of the same error. Both `Right:` lines are
unchanged, and so is the prohibition itself. The only arrow character left in the
file is the one inside backticks on the prohibition line, naming the character,
which the rule permits.

```diff
-- Wrong: **Request A**: calls `currentToken()` → token expired → calls `refresh()`
+- Wrong: a bold label, then the three calls chained with arrows between them
+  instead of verbs.
 - Right: Request A calls `currentToken()`, finds the token expired, and calls `refresh()`.
-- Wrong: Rough runbook: rotate the key → wait out the old TTL → remove it.
+- Wrong: a "rough runbook" line with the three rotation steps arrowed together.
 - Right: Rotate the key, wait out the old TTL, then remove it. Use a numbered
   list instead when the user will follow the steps one at a time.
```

## Design: both sides generated simultaneously

Round 31 ran its control and edit sides one after the other. Round 37 has since
measured a syntactic behaviour moving **4.7× in five days** at byte-identical
rules, which makes a multi-hour sequential window exactly the exposure to avoid.

So both sides ran **concurrently**, each from its own tree — the edit from this
branch, the control from a `master` worktree — with `--concurrency 2` declared on
both. Regime and era then cancel between the sides instead of confounding them.
They tracked within two runs of each other throughout.

laconic arm only, sonnet, 30 reps, three cases, 90 runs a side, 0 failed.

## Result

Arrows in prose, scored with `metrics._symbol_hits` on code-stripped text:

| Case | control arrows | edit arrows | responses carrying one | |
|---|--:|--:|:--|--:|
| `destructive` | 2 | 2 | 1/30 vs 1/30 | p = 1.000 |
| `ordered-steps` | 8 | 9 | 3/30 vs 4/30 | p = 1.000 |
| `walkthrough` | 26 | **51** | 10/30 vs 15/30 | p = 0.295 |
| **pooled** | **36** | **62** | **14/90 vs 20/90** | **p = 0.341** |

Full readability violations, all three kinds, move the same way: control 36
against edit 62, and 14 of 90 responses against 20 of 90.

**The propagation did not go, and the edit is worse on the point estimate.** Not
significantly — p = 0.341 pooled, and the largest cell movement is p = 0.295 —
so this is a null that leans the wrong way rather than a measured harm.

## What it answers

**[#164]'s item 1 is answered negatively: the rendered specimen is not the
carrier.** Removing every rendered arrow from the file left arrows in responses
unchanged.

That does not contradict round 31, and the distinction matters. Round 31
*added* a pair and saw arrows appear. This round *removed* the rendered half of
pairs that were already there. Both readings survive if the mechanism is the
recency of a newly added example rather than the standing presence of a
specimen — which is a narrower claim than [#164] proposed and is not tested here.

**A second reading is available and this round cannot separate it.** The `Wrong:`
line shows exactly what not to do; "a bold label, then the three calls chained
with arrows between them" describes it. If the concrete negative example is doing
teaching work, removing it should make arrows *more* common, which is the
direction observed. At p = 0.341 that is a hypothesis, not a finding.

## What is kept

Nothing in `rules/`. The edit reverted in full, including the parts that were
merely neutral, per the loop's rule for a rejected round.

The two snapshots are kept as evidence, and they are the first in this archive
generated as a **simultaneous** two-tree comparison rather than a sequential one.
That design is the round's reusable part: it costs nothing extra, halves wall
time, and removes the era confound round 37 found in the sequential version.

180 generations, 0 failed. The target needed no judging, but the control side was
judged afterwards for the reason below.

## What the control side says about drift, and it is reassuring

Round 37 left a hedge the skill still carries: one syntactic behaviour moved 4.7x
in five days at byte-identical rules and another did not, with nothing to say in
advance which would be which. The counters a gate actually reads are *judged*,
and that case was untested.

This round's control makes the test available. `round-30-control.json` is 80
`walkthrough` runs from 2026-08-28 at `rules_cksum` 136269960, judged **80 of
80**. This round's control is 30 `walkthrough` runs from 2026-09-01 at the same
checksum. `evals/cases/walkthrough/` has not been touched since 2026-08-27, so
the criterion is identical — today's `criteria_cksum` differs only because
eighteen *other* `expect.json` files changed in between.

| | 2026-08-28 | 2026-09-01 |
|---|--:|--:|
| `walkthrough` judged quality | 80/80 — **100%** | 30/30 — **100%** |
| `walkthrough` preamble openings (syntactic) | 31/80 — **38.8%** | 4/40 — **10.0%** |

**On the same case, across the same four days, at byte-identical rules, a
syntactic style metric moved about 4x while judged correctness did not move at
all.**

That is the sharpest statement this archive can currently make about what drifts.
Style drifted; correctness held. The fatal counters read correctness, so they are
less exposed than round 37 alone implied.

**Read with the ceiling in mind.** Both quality readings are 100%, and a cell
drawn at ceiling can only fall — per [#94] this detects a fall and not a rise, so
it is evidence of no *degradation* rather than evidence of stability in both
directions. It is one case. It does not license carrying a baseline across eras;
it narrows what the risk of doing so appears to be.

Judged with `--judge-all`, 90 calls: `walkthrough` 30/30, `ordered-steps` 26/30,
`destructive` 22/30.

[#94]: https://github.com/JordanMPDS/laconic/issues/94

[#164]: https://github.com/JordanMPDS/laconic/issues/164
