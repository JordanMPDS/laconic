# Round 44: the first lens candidate to be scored

**Registration. Nothing below the results line has been computed.** This file and
the rules text under test are committed in the same commit, before any
generation, following [round 38](round-38.md).

## Why this edit, and why it is [#26]'s round rather than [#36]'s

[`lens-pilot-26.md`](lens-pilot-26.md) asked four blind proposers for arrow
candidates through four lenses, and six of twelve classified as new against
[`arrows.md`](arrows.md)'s five rejected edits. Its recommendation was explicit
about what to do with them:

> run the lens step by hand at step 5 of the next round that has no obvious
> edit, and leave the workflow, the panel and the multiple-comparisons
> bookkeeping unbuilt until a lens candidate has actually survived a round.

This is that round. **No lens candidate has been scored against a benchmark, so
[#26] currently rests entirely on classification** — five untried mechanisms is
a queue, and a queue nobody has drawn from is not evidence that the proposer
half works.

The candidate is the never-cut lens's candidate B, which the pilot's table
numbers 2. It is chosen over the other four because it is the one
[`arrows.md`](arrows.md) independently names as the untried direction:

> **A structural move rather than an additive one.** Round 10 remains the only
> accepted edit in the loop's history that worked by *relocating* a rule rather
> than bounding it in prose, and the over-length cluster records four wording
> attempts failing where one relocation succeeded. Nothing has tried that here.

So the round tests two things at once with one batch: whether the relocation
lowers arrows, and whether a lens candidate can survive a round at all.

## The edit

One edit. The connecting-words claim moves out of `## Never do this` and into
`## Never cut`, as its own bullet, and the sentence it replaces is deleted.

```diff
 - Ordered instructions: every step, and the words that fix their order
   ("before", "after", "first").
+- The words that join one thing to the next: what causes what, which condition
+  produces which result, what happens before what. These are claims, not
+  connective tissue, and an arrow (`→`, `->`) is how they get deleted while
+  the line still looks complete.
 - Bad news: a failure, a broken test, a limit hit, a thing not done. Omitting
   it is not terseness.
```

```diff
 **No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
 steps, stages, states or causes, not to show that one thing maps to or becomes
 another, not after a bold label, not in a "quick runbook" line, not inside a
-quoted flow. Sequencing is where an arrow is most tempting and least
-acceptable: an ordered process is exactly the content whose connecting words
-are never cut.
+quoted flow.
```

The prohibition itself, all four `Wrong:`/`Right:` lines and the fenced-code
carve-out are untouched. **The file gains no new rendered specimen**: the only
arrow characters the new bullet adds are inside backticks, naming the
characters, which is the form the prohibition line already carries. That keeps
[#164] item 2 out of this round.

**The mechanism, in the proposer's words.** The arrow prohibition currently sits
among dropped articles, telegraphic fragments and `impl`/`config` abbreviations
— things to catch while proofreading, all of which trade against the pressure to
be short. `Never cut` is the only section marked absolute at every level and the
only one about content rather than form. An arrow deletes content, so filing it
under form is a category error that costs the rule its authority. The deleted
sentence already makes that argument, but makes it as an aside at the tail of a
style paragraph.

**Round 10's lesson runs the other way here, and that is the risk.** Rounds 07,
08 and 09 put a design-question *licence* into `Never cut` and `ordered-steps`/
haiku read 6, 3 and 5 against a baseline 2; round 10 fixed it by moving the
licence out. So `Never cut` placement has propagated outside its scope before,
in the opposite direction to this move. A prohibition entering that section is
not the same object as a licence entering it, but the archive's one data point
on the section's reach is a bad one, and the round-wide propagation check below
exists because of it.

## Hypothesis

> Moving the connecting-words claim from `## Never do this` into `## Never cut`
> should lower the arrow count on `walkthrough`, sonnet.

`walkthrough` is [`arrows.md`](arrows.md)'s finding 3 residual and the case the
proposer's own prediction names first, because both sides of its arrows are
protected content: the user asked for the explanation, and the arrow sits where
the verb carrying the mechanism used to be.

## Falsifier, registered before the batch

**The two `walkthrough` cells not separating at p < 0.05, or separating upward.**
Direction is registered because a rise refutes the candidate as surely as a flat
result does, and three of the five prior arrow edits moved the wrong way.

## The discriminant, which is the reason `confirm-rollback` is in the batch

The proposer registered its own falsifier and it is sharper than the primary:

> **What would falsify it.** The `design-*` groups drop as much as
> `walkthrough`. That would mean the reclassification carried no information and
> the improvement is just the file saying "arrows" one more time.

The `design-*` cells cannot carry that test. They run at 46 arrows in 848
archived responses, about 5%, so 40 responses hold roughly two arrows and
nothing can be said to fall.

`confirm-rollback` can. It is the highest-rate arrow cell in the archive — 20 of
40 responses, 50% — and its arrows are almost entirely one shape the new bullet
does **not** cover: the value transition, `` `PAYMENTS_SETTLEMENT_MODE` → `split` ``.
That shape is the target of a *different* lens candidate (never-cut candidate C,
the pilot's 3), and the proposer predicts essentially nothing for it here.

So the registered reading is:

| `walkthrough` | `confirm-rollback` | reading |
|---|---|---|
| falls | flat | the reclassification carried information. The candidate works as described |
| falls | falls as much | generic re-emphasis, not the relocation. The cheaper edit is to say it once, well |
| flat | flat | the relocation does nothing. [#26]'s first scored candidate fails |
| flat | falls | the mechanism is not the one proposed, and candidate C's target moved without candidate C |

## Registered harm check, free with the batch

`evals/cases/walkthrough/expect.json` grades `safety` and carries never-cut item
`401`. That is a substring test, so it costs no judge calls: **a fall in the
share of `walkthrough` responses naming `401` rejects this round whatever the
arrow count does.** Registering it here because rounds 30 and 31 were both
rejected on never-cut damage outside the cells their hypotheses named, and
[`arrows.md`](arrows.md) finding 6 says that propagation, not the target, is
what has been blocking this line.

The wider propagation check — `destructive`, `ordered-steps` and the round-wide
fatal counters — is **not bought by this batch**. The skill's staged rule is to
score the cheap target first and buy the round-wide arm only for an edit that
passed it. If the scoped target fails, the round rejects and the round-wide arm
is never generated, which is what round 23 did.

## The batch

Both sides generated simultaneously, each from its own tree, so era and CLI
release cancel between them rather than confounding them — the round 37 lesson,
and the design round 38 introduced.

```sh
git worktree add /tmp/laconic-r44-control master

# edit side, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases walkthrough,confirm-rollback --concurrency 2 \
  --snapshot evals/snapshots/loop/round-44-edit.json

# control side, from the worktree, writing back to this tree
cd /tmp/laconic-r44-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 40 --cases walkthrough,confirm-rollback \
  --concurrency 2 \
  --snapshot <abs>/evals/snapshots/loop/round-44-control.json
```

160 generations, no judging. `--concurrency 2` on both, because two CLI
invocations really are in flight.

**The registered baseline is this round's own control, not a stored snapshot.**
Round 31 registered `walkthrough`/sonnet at 46 arrows off a three-day-old
snapshot at byte-identical rules and its own interleaved control read 31 over
the same 40 runs. Every number in the result table below comes from
`round-44-control.json`.

Both cases are single-turn, so `--turn-delivery` does not apply and the batch
carries no multi-turn work.

## Scoring

`metrics.score(text)["symbol_connectors"]`, the same counter round 38 published
and the same one `review.py` reads for its `arrow` violations. Reproducing round
38's table from its two committed snapshots returns its published figures
exactly — control `walkthrough` 26 arrows and 10 of 30 responses, edit 51 and 15
of 30 — so the scorer used here is the one that produced the number this round
is being compared against.

Two statistics per cell, both two-sided:

- **arrow count**, by permutation of the side label over the per-response
  counts, 200,000 resamples, seed 44. This is the primary.
- **responses carrying at least one**, by Fisher exact. Reported beside it
  because it is what rounds 30, 31 and 38 published and is the comparable
  figure.

## Power, stated before the numbers

Round 38's control read 26 arrows in 30 `walkthrough`/sonnet responses and round
31's read 31 in 40, so 40 responses should hold roughly 30. Against a control at
30 a halving is detectable and a quarter-reduction is not; the round is sized to
resolve the effect round 30 measured on this case, not a smaller one.

**Two noise results bound how a null should be read.** Round 37 measured a
syntactic behaviour on this exact case moving 4.7x in five days at byte-identical
rules, and [`conditional-homology-116.md`](conditional-homology-116.md) recorded
a counter drawing 14 and 8 of 40 across two generations of identical rules. The
simultaneous two-tree design removes the first of those by construction. It does
not remove the second, and a point estimate inside it means nothing either way.

## What this round may not claim

Not that lens candidates work. It scores one of five, on the target the pilot
itself called the sternest available, and a single result classifies that
candidate rather than the method. A rejection here is [#26]'s first real cost
datum and not a refutation of the pilot; an accept is one candidate surviving one
round, which is exactly the bar the pilot set for leaving the workflow unbuilt.

---

## Result

**Reject.** The registered falsifier fired: `walkthrough` did not separate at
p < 0.05, and its point estimate moved upward.

160 generations, 80 a side, **0 failed**. Both sides at the reps the
registration named, `--concurrency 2` declared on both, control at
`rules_cksum` 136269960 and edit at 2655028993.

| case | control arrows | edit arrows | permutation p | responses carrying one | Fisher p |
|---|--:|--:|--:|:--|--:|
| `walkthrough` | 41 | 45 | 0.830 | 14/40 vs 15/40 | 1.000 |
| `confirm-rollback` | 26 | 33 | 0.125 | 26/40 vs 33/40 | 0.126 |
| **pooled** | **67** | **78** | **0.498** | **40/80 vs 48/80** | **0.266** |

Full readability violations, all three kinds, move the same way and no further:
control 68 against edit 79, permutation p = 0.496. Nothing here separates, and
every point estimate leans the wrong way.

**The registered harm check passes.** `401` is named in **40 of 40**
`walkthrough` responses on both sides, Fisher p = 1.000. The relocation cost the
case nothing, which is the one thing rounds 30 and 31 were rejected for and this
one is not.

## Reading the registered table

The round registered four readings before the numbers were in. The one that
obtains is the third:

| `walkthrough` | `confirm-rollback` | reading |
|---|---|---|
| flat | flat | **the relocation does nothing. [#26]'s first scored candidate fails** |

Both cells are flat by the registered criterion, so the discriminant never got
to do its work. `confirm-rollback` was in the batch to separate "the
reclassification carried information" from "generic re-emphasis", and it can
only separate two effects that exist. With neither cell moving, it reports
instead that the null is not confined to the cell the hypothesis named.

The proposer's own falsifier — that the untargeted cells drop as much as
`walkthrough` — is technically satisfied and worth nothing: `confirm-rollback`
moved *more* than `walkthrough` in the wrong direction, at a p that is still not
a result. Read it as no effect anywhere, not as a discriminated one.

## What the control says about the instrument

The power section predicted a control near 30 arrows on `walkthrough` at 40
responses. It read **41**, against round 31's 31 in 40 and round 38's 26 in 30.
The cell is live and the round was not underpowered for the effect it was sized
to find: a halving off 41 would have been unmissable, and the observed movement
is +4.

`confirm-rollback` is the higher-rate cell the registration said it was — 26 of
40 responses, 65%, against the 50% the archive predicted — and its arrow shape
is exactly as described. Every one of its 26 control arrows is a mapping, none
is a chain, and sampling the lines shows one form:

```
Partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the
initial 500s at 14:02 ...
```

That is never-cut candidate C's target, not candidate B's, and it did not move.

## The component split, unregistered

`metrics.arrow_forms` separates chains from two-term mappings, and rounds 16, 17
and 18 all reported a headline that fell about 20% over components moving in
opposite directions. This round was checked for the same shape:

| case | form | control | edit | responses | permutation p |
|---|---|--:|--:|:--|--:|
| `walkthrough` | chain | 9 | 4 | 4/40 vs 2/40 | 0.517 |
| `walkthrough` | mapping | 32 | 41 | 12/40 vs 13/40 | 0.546 |
| `confirm-rollback` | chain | 0 | 0 | — | — |
| `confirm-rollback` | mapping | 26 | 33 | 26/40 vs 33/40 | 0.125 |

The chain/mapping opposition is visible on `walkthrough` and is not significant
in either component. **This is a disclosure, not a finding** — it was not
registered, it is one cell, and 9 to 4 on four responses is the kind of number
[`conditional-homology-116.md`](conditional-homology-116.md) already bounds as
noise. It is recorded because a future arrow round should check it deliberately
rather than rediscover it post hoc, as three rounds have now done.

## Scoring provenance

`metrics.score(text)["symbol_connectors"]` on code-stripped prose, permutation
of the side label over per-response counts at 200,000 resamples, seed 44, and
Fisher exact on the response-level counts. Run against round 38's two committed
snapshots the same scorer returns its published figures exactly — control 26
arrows and 10 of 30, edit 51 and 15 of 30, Fisher p = 0.295 — so the instrument
is the one that produced the numbers this round is compared against.

## What this round answers

**[#26] now has its first cost datum, and it is a rejection.** The pilot's
recommendation was to score one lens candidate before building the workflow, the
panel or the multiple-comparisons bookkeeping. That has now happened, on the
candidate the pilot itself called the sternest available and the one
[`arrows.md`](arrows.md) independently named as the untried direction, and it
produced nothing. The queue of five untried mechanisms is now a queue of four,
and the classification-only evidence [#26] rested on is one degree weaker: a
candidate can classify as new against every prior edit and still not move the
number it was proposed to move.

That does not refute the pilot, and the registration said so in advance. One
candidate of five, on one target, is a classification of that candidate. What it
does remove is the reading that the proposer half was demonstrated — it was
demonstrated to produce *novel* candidates, and novelty is now measured at one
for zero on effect.

**The structural-move hypothesis is answered negatively for this rule.** Round 10
remains the only relocation that worked, and it is now the only one of two
attempted. The distinction that survives is the one round 10's own record
suggests: it moved a *licence* out of a section whose scope was leaking, fixing a
propagation that had been measured. This round moved a *prohibition* into a
section on the theory that the section confers authority. Relocation fixing a
demonstrated over-reach is not evidence that relocation confers force, and this
round is the first test of the second claim.

**The risk the registration named did not materialise either.** `Never cut`
placement propagated badly in rounds 07 to 09; here it propagated not at all,
including onto `confirm-rollback`, which the section's reach would have touched
first. The section is narrower than its one bad data point suggested — a small
reassurance for future edits that need to live there.

## Disposition

The edit is reverted in full, `rules/laconic.md` and the three generated slices,
back to `rules_cksum` 136269960. Both snapshots are committed as evidence. No
round-wide arm was bought: the staged rule stops at the first step that fails,
and the scoped target failed.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#36]: https://github.com/JordanMPDS/laconic/issues/36
[#164]: https://github.com/JordanMPDS/laconic/issues/164
