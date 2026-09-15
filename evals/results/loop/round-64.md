# Round 64: the rule with no worked example, and the one instrument where it is measurably broken

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are the reason this round takes the
shape it does. This file, the edit and the regenerated `rules/dist/*.md` are
committed before any generation, following [round 38](round-38.md) through
[round 63](round-63.md).

## Why this round exists

`bash tools/candidate-due.sh` exits 1. Rounds 56 through 63 were eight
instrument rounds in a row and `rules/laconic.md` has not moved since
[round 55](round-55.md) on 2026-09-08. Under the cap merged as #292, round 64
has to carry a rule edit, and it comes from an open issue labelled `rules`.

It comes from [#136](https://github.com/JordanMPDS/laconic/issues/136), whose
report is the strongest lead this loop gets — a user-visible failure of an
**explicit** rule, rather than a gap in an ambiguous one:

> **Length scales to the request, at every level.** A yes/no question gets a word
> or a line.

The reporter asked an eight-word closed confirmation question — *"you mentioned
Lift is the wrong metric correct?"* — and got roughly 400 words across three
`##` sections, re-deriving an argument already delivered in the same session to
the same person, who was quoting it back. The issue's own diagnosis is what
makes it worth a round:

> So this is not a gap in the rules. It is an existing, explicit, unambiguous
> rule failing to fire. That is a different defect from the three above, and
> arguably a worse one, because no rewrite of the carve-out would have prevented
> it.

## The edit

`rules/laconic.md`, immediately after the demonstration block's coda and above
every level marker, so it reaches `lite`, `full` and `ultra` alike — the rule it
demonstrates says "at every level", and where a rule lives outranks what it says
about where it lives (rounds 07 to 10):

```diff
 Ultra kept the conditional because dropping it would give wrong advice half the time.
+
+Same scenario, asked as a closed question: *"So the fix is bumping the limit,
+correct?"* — "Only if memory is flat. A climbing curve is a leak, and a bigger
+limit only delays the next kill." A closed question gets the answer and the
+correction that makes it true, then stops.
```

51 words. The `full` slice goes from 1,041 to 1,092 and `rules_cksum` from
**594915793** to **245017430**.

### Why a worked example rather than another sentence

This is [#136]'s proposal 1, and the reason to prefer it over its proposal 2 is
a measurement that did not exist when the issue was filed.

Seven rounds in the over-length cluster have added a sentence telling the model
to check its own length, or reworded the length licence, and all seven were
null. [Round 48](round-48.md) named the class:

> Six nulls through two channels is a negative result about the intervention
> class: instructing the model to check its own length does not change its
> length.

[Round 60](round-60.md) then took the file's one demonstration block apart
against three word-matched replacement rungs and found which of its three
properties carries the effect:

| rung | property removed | vs ceiling | share of the gap |
|---|---|--:|--:|
| `repl-told` | rendered | 0.960x (p = 0.1774) | **−0.16** [−0.47, +0.07] |
| `repl-unlabelled` | mapped to a level | 1.057x (p = 0.0515) | **+0.22** [+0.01, +0.41] |
| `repl-unframed` | worked from a question | **1.140x** (p = 0.0000) | **+0.52** [+0.33, +0.72] |

> **The worked question is the largest single thing the block does, and it is
> about half of it.** … An example needs a question to be an example of.
>
> **Rendering as such is none of it.** … Showing rather than telling is not the
> mechanism.

So the file contains exactly one worked question, it is open-ended, and the rule
this round is about — the one governing *closed* questions — is stated once in
the abstract and never worked from a question. That is the gap round 60's own
result points at, and it is a different intervention class from the seven nulls.

The same result is why [#136]'s proposal 2, *"say explicitly that confirming a
claim is not a request to re-justify it"*, is **not** in this edit. It is a
telling sentence, and telling measured at −0.16 of the gap. `tools/consult.sh`
reached the same conclusion independently and the wording of the edit's final
clause is `codex`'s:

> "Add only what…" is good intent, but this version makes the required two-part
> response visible. The final "Confirming a claim…" sentence is the weakest
> part: it drifts back toward telling. I'd cut it.

Both consulted targets, `codex` and `kimi`, independently made the same
correction to the draft — that the prescribed *shape* (the answer plus the
correction that makes it true) has to be visible rather than inferred from the
example — and `kimi` named the reason this round's harm check exists:

> The real risk is not that the clause is too short; it is that the original
> rule *"A yes/no question gets a word or a line"* is still in the file and now
> conflicts with the example. If the model weights the abstract rule above the
> concrete example, you get the harm condition: a bare "yes/no" with the
> qualification dropped.

### Why the OOM scenario and not the issue's own

The example reuses the scenario already in the file, changing only the request
shape from open advice to closed confirmation, so it introduces no new subject
matter at all. **The issue's own lift/metric example was ruled out because
`confirm-metric`'s fixture is that scenario**, and putting it in the system
prompt would hand a scored case its graded answer. Both consulted targets
endorsed the reuse; `codex` checked the scored confirmation prompts and
expectations for OOM wording and found none.

## The instrument

`confirm-index`, `confirm-metric` and `confirm-rollback`: three scored cases,
single turn, each a closed `correct?` question over a fixture the model must
read. They are the only cells in the suite whose graded question has the shape
[#136] reports.

Laconic on sonnet spends this much on them (computed 2026-09-15 over every
stored snapshot, `rules_cksum` 136269960, which is the rules text before round
55's pre-action check):

| cell | n | median words | sd |
|---|--:|--:|--:|
| `confirm-index` | 50 | 72.0 | 10.8 |
| `confirm-metric` | 50 | 81.0 | 13.2 |
| `confirm-rollback` | 270 | 82.0 | 15.9 |

Against a rule that says "a word or a line". **No `confirm-*` run exists at
master's current `rules_cksum` 594915793**, which is why the round generates its
own control rather than scoring against these — per the standing rule that a
count target takes its registered baseline from the round's own control.

## The registered hypothesis

> Adding a worked closed question to `rules/laconic.md` should **reduce median
> prose words on `confirm-index`, `confirm-metric` and `confirm-rollback`**,
> laconic arm, sonnet, against this round's own simultaneously generated master
> control.

**Endpoint:** prose words by `metrics.score`, per cell, 40 runs a side,
two-sided permutation of the side label over per-run counts at 200,000
resamples, seed 64. **Scored per cell and combined by a two-sided exact sign
test over the three cells**, not on a pooled median — `codex`'s correction, and
the reason is that the three cells sit at different levels and a pooled median
lets one fixture decide the round. The pooled figure is printed as disclosure.

**Falsifier, registered in advance: fewer than 3 of 3 cells falling, or any
cell separating upward at p < 0.05.** Three cells is the smallest scope a sign
test can speak for, so the primary requires a clean sweep and says so in
advance; the per-cell permutation p-values are the resolution.

**[#131] stratification.** `confirm-*` read their fixture on the graded turn in
60 of 60 runs in [round 42](round-42.md). A cell whose reading rate crosses
between the two sides does not vote, and the round reports the rates whether or
not any crossed.

## The harm this edit can do, and what the round can see of it

Every one of the three target cells is graded on a trap where **the correct
answer is emphatically not one word**. It is the verdict plus the qualification
the fixture attaches, and the qualification is the load-bearing half:

- `confirm-rollback` — yes, the config change was the trigger, **and** reverting
  it could not restore service, because migration 0042 had already added a
  `NOT NULL settlement_currency` with no default. An answer that confirms the
  config change and stops "has confirmed the part the question already assumed".
- `confirm-metric` — the lift figure is unusable, **and** the absolute
  difference is not a safe substitute.
- `confirm-index` — the proposed index does not fix it, **and** here is one of
  the two shapes that does.

So the target and the harm are separated by one clause of the edit, and the same
240 responses carry both. This is the round's central risk and it is registered
as a bound rather than a significance test, following [round 49](round-49.md)'s
precedent of converting a fatal check into a stated bound when the test cannot
separate the intended effect from the harm.

**Fatal: the pooled trap pass rate over the three cells falling by more than 10
points against this round's own control**, judged over all 240 runs, blind, with
`--judge-all` on both sides so the coverage matches.

**What that bound can and cannot see, stated before the numbers.** `codex`
priced it: at 40 a side against a control passing around 37 of 40, Fisher at
α = 0.05 rejects only at 30 of 40 or worse. So this is a **cliff detector**, not
a general qualification-safety test. It catches the edit collapsing answers to a
bare yes or no; it does not certify that a 3-point fall did not happen. The
round says so rather than implying more, and a pass here is reported as "no
cliff", not as "no harm".

**Also fatal, round-wide, and unchanged:** a never-cut verdict lost, a quality
verdict lost, a safety verdict lost, or readability violations up, all scored at
stage 2 by `report.py` against `round-21.json`.

## The discriminant

**`fail-open`, `silent-success` and `stale-cache`**, 30 runs a side in the same
interleaved batch. Single-turn open diagnostic questions on their own fixtures,
each ending `Don't edit anything.`, so no stratum can mix ([#209]). They are the
cells rounds 51, 52 and 55 registered against and they are measured at master's
current `rules_cksum` 594915793 — 70.0, 70.0 and 139.0 median words over n = 225,
215 and 235 — which is the property that makes them usable as a discriminant at
all.

Three readings, registered:

1. **`confirm-*` falls and the discriminant does not.** The mechanism is closed
   questions specifically, and the cluster has its first positive result.
2. **Both fall by similar proportions.** A general compression edit rather than a
   closed-question edit. It would then have to be judged as an ordinary length
   edit against the round-wide fatal counters, and the round says so.
3. **Neither moves.** The eighth null in this cluster, and the first about a
   worked example rather than a sentence.

**A deviation from the consultation, disclosed.** Both `codex` and `kimi`
independently asked for a *within-fixture* open control — the same three
fixtures asked open-endedly — as the stronger specificity check, and they are
right that it holds domain constant where this one does not. It was not bought.
The within-fixture version exists only as turn 1 of `wide-*`, `recall-*` and
`deep-*`, which costs two calls per rep and whose turn-1 history is n = 5 per
cell at the wrong `rules_cksum`; the cells above cost one call per rep and carry
n ≥ 215 at the right one. For a claim about *length*, a measured baseline buys
more than a matched domain. The confound the within-fixture control would close
better — "the file simply got 51 words longer" — is separately bounded by round
59 at 1.070x per 100 words (95% upper), so 51 words bounds a bulk-length
artefact at about **1.036x**, which is smaller than the fall this round is
powered for.

## Power, stated before the numbers

Taking sd = 15 words, which is the largest of the three archive figures and
larger than anything the current rules have produced on the comparable
single-turn cells (12.1 to 21.8): 40 runs a side detects a 10-word shift at
about 0.90 power and a 15-word shift at above 0.99. The gap between the measured
~78 words and the rule's "a word or a line" is roughly 60, so this round is
powered for a fifth of the effect the issue describes. A null here is a null on
a large effect.

The discriminant at 30 a side, with its measured sd of 12.1 to 21.8, detects
about 11 words on `fail-open` and `silent-success` at 0.90. A "did not move"
there is therefore a bound of roughly 11 words, not a claim of zero, and is
reported that way.

## What this round does not claim

**The instrument does not reproduce [#136]'s session.** `codex` raised this and
it is right, and [round 32](round-32.md) already says it: these are cold,
single-turn fixtures, and the reported failure was a licensed-long register
inherited across turns from an argument the model had itself produced. What this
round tests is whether the edit improves a **generic closed confirmation**, not
whether it fixes the conversational failure the issue opens with. Those are
different claims and only the first is on the table.

## Buying order, stopping at the first failure

Per the skill's standing order:

1. **Stage 1, 420 generations.** `confirm-*` at 40 a side and the discriminant
   at 30 a side, both sides, scored on the target. No judging.
2. **Stage 1b, 240 judgments.** The scoped trap bound on the `confirm-*` runs
   already generated, both sides, `--judge-all`. Bought only if stage 1 passes.
3. **Stage 2, 220 generations and 185 judgments.** The round-wide laconic arm
   for the four fatal counters. Bought only if 1 and 1b pass.
4. **Stage 3.** Replication and holdout, for an edit that has passed all three.

## Two trees, generated simultaneously

Round 38's design, unchanged. The edit side runs from this branch and the
control side from a `master` worktree writing back into this tree, launched
together, so era and CLI release cancel between the sides instead of confounding
them — [round 37](round-37.md) measured a syntactic behaviour moving 4.7x in
five days at byte-identical rules.

```sh
git worktree add /tmp/laconic-control master
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases 'confirm-index,confirm-metric,confirm-rollback' --concurrency 2 \
  --snapshot evals/snapshots/loop/round-64-edit-confirm.json &
python3 evals/bench/run.py --arms laconic --models sonnet --reps 30 \
  --cases 'fail-open,silent-success,stale-cache' --concurrency 2 \
  --snapshot evals/snapshots/loop/round-64-edit-open.json &
# and the same two from /tmp/laconic-control, writing round-64-control-*.json
```

Four shards, inside [#255]'s ceiling of four. `--concurrency 2` is declared on
each, per [#120]. The two sides are separated by `rules_cksum`, **594915793** on
the control against **245017430** on the edit.

`python3 evals/bench/release.py` is run over the four snapshots before any
contrast is read out of them, per [#272].

## A harness change this round had to make first, and why it is not scope creep

**Every rule edit from here on was blocked, and this is the first rule edit since
the block was built.** Seven arms in `evals/arms/` — `laconic-abl-*`,
`laconic-repl-*`, `laconic-precheck-*` — are each defined as a transformation of
the shipped `full` slice, and `tests/test_bench.py` checked them against the
*live* slice. Rounds 59, 60 and 63 built them; round 55 was the last rules edit
and predates all of them. So this edit failed nine checks that no rules edit
could ever pass, and the cap merged as #292 requires a rules edit every other
round.

The tests' own comment names the intended remedy — "the arm has to be rebuilt" —
and rebuilding is the wrong answer here. Round 60's ladder is word-matched to
within 20 words of the slice it ran against; rebuilding it against this slice
would require authoring new substitute prose for two rungs, producing texts
round 60 never ran while `evals/arms/README.md` went on describing the old ones.
That is indistinguishable from rewriting the record of a completed round.

So staleness became a third state, recorded rather than repaired:

- **`evals/arms/BUILT-FROM.json`** records the `rules_cksum` of the slice each
  derived arm was cut from. All seven read `594915793`, the slice rounds 59
  through 63 measured. The `laconic-min-*` arms carry no entry, because they are
  rewrites to a content specification rather than transformations.
- **`tests/test_bench.py` skips a stale arm's invariants** rather than failing
  them. "Removes exactly 209 words" is a claim about a file that is no longer
  there.
- **`run.py` refuses to generate with a stale arm**, naming it and both
  checksums, before anything is written. `--allow-stale-arm` is the deliberate
  override.

The refusal is what replaces the skipped checks, so the protection moves rather
than lapsing — and it is tested end to end through a subprocess, because a
predicate that is correct and never consulted would leave exactly the hole the
skip opens. Rebuilding a stale arm is now a deliberate act belonging to whichever
round next needs one.

[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272

<!-- RESULTS BELOW THIS LINE -->
