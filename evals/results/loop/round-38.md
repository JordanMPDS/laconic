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

180 generations, 0 failed, no judging — the metric is syntactic.

[#164]: https://github.com/JordanMPDS/laconic/issues/164
