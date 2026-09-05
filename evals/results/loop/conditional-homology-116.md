# The worked OOM example is `conditional` with the domain swapped

**Registration. No number under "Result" has been computed.** Committed before
the batch runs.

## The homology, which the case file already records and nothing has tested

`evals/cases/conditional/expect.json` says, in `criteria_source`:

> Mixed, and treated as contaminated. Naming the leak is task-derived, but
> "collapsed into a symbol" is the arrow prohibition from rules/laconic.md, and
> **the scenario reproduces that file's worked OOM example with the domain
> swapped.**

Two of those three clauses have been tested.
[`volunteered-work.md`](volunteered-work.md) found the arrow prohibition cited
in 0 of 34 failures, and
[`conditional-retrap.md`](conditional-retrap.md) removed it and found it inert
in 0 of 18 flips. **The third clause has never been tested at all**, and it is
the one that bears on what [#116] measured.

Side by side:

| | `rules/laconic.md` lines 33 to 41 | `evals/cases/conditional/prompt.md` |
|---|---|---|
| question | "Our deploy failed with an OOM kill on the worker. Should I bump the memory limit?" | "Our Postgres connection pool keeps hitting max ... Should I raise the pool size?" |
| shape | advisory yes/no about raising a resource limit | advisory yes/no about raising a resource limit |
| diagnosis | "a climbing curve means a **leak**" | `withClient` never releases on throw, a **leak** |
| consequence | "a bigger limit only **delays the next kill**" | "a bigger pool just **delays the same failure**" |
| instruction | "`kubectl top pod` over a few minutes tells you which one you have" | `pool.log` has the last hour |

The example sits above the `<!-- level:lite -->` marker, so every level of the
slice carries it. **The laconic arm is handed a worked answer to `conditional`
in its system prompt. The baseline arm is not.**

## What is at stake

[#116] reports a question answered correctly and then substantiated with work
nobody asked for. Its single measured effect is
[`volunteered-work.md`](volunteered-work.md)'s matched batch, 40 a side on
sonnet, at `rules_cksum` 136269960 and `cases_cksum` 2155887303:

| arm | edits | rate |
|---|--:|--:|
| baseline | 25 / 40 | 62.5% |
| laconic | 14 / 40 | 35.0% |

Two-sided Fisher **p = 0.0247**, published as *"laconic nearly halves the rate
at which a question gets answered by editing the user's file."*

That reading takes the suppression to be a property of the ruleset. The
homology admits a narrower one: the ruleset demonstrates a prose-only answer to
this exact question, and what the laconic arm is following is the
demonstration. **Those two readings are the same number and different claims**,
and only the first supports the general pre-send check [#116] proposes.

## What the homology cannot explain, so the hypothesis is scoped to the arm gap

`conditional` is the only case in the archive that elicits editing at all: all
81 `Edit` calls in 5,557 runs are on it, and
[`volunteered-work-cases.md`](volunteered-work-cases.md) records four
purpose-built replacements reading 0 or 1 in 10 to 50. The homology cannot be
why, because **the baseline arm edits on `conditional` too**, at 62.5%, and the
baseline arm carries no rules and has never seen the example.

So the claim under test is only about the gap between the arms, never about the
level of either.

## Hypothesis and falsifier

> **Hypothesis:** the laconic arm's suppressed `Edit` rate on `conditional` is
> produced by the worked OOM example's homology with the case. Replacing the
> example with one that teaches the same thing in a domain the suite does not
> contain should raise the laconic `Edit` rate.

**Falsifier, registered before the batch:** the two laconic cells not
separating at p < 0.05 on a two-sided Fisher exact test. That leaves the
published reading standing, and the suppression a property of the ruleset
rather than of one example.

**Direction is registered too**, because a fall would refute the hypothesis
just as a flat result does: the prediction is `swapped` **above** `master`.

**Registered secondary, from the same runs at no extra cost:** the read rate
and the median words of the non-editing stratum. A swap that moved those
wholesale would be changing more than the homology, and the primary would not
be readable.

## The manipulation

The replacement holds the example's function fixed and changes only its
subject: three levels, a conditional answer, an evidence check the reader can
run, and the closing sentence that ultra kept the conditional because dropping
it would give wrong advice half the time. It changes the question away from
raising a resource limit, the diagnosis away from a leak, and the consequence
away from delaying the same failure.

**The replacement is a probe and is not proposed for the product.**
`conditional` is a `rule-adherence` case and may not be optimized against, so
no rule edit follows from this batch in either direction. What the result buys
is the validity of a published number, which is the same thing
[`turn-delivery.md`](turn-delivery.md) bought for rounds 33 to 36.

The probe lives on a scratch branch in a `git worktree`, never merged, so
`rules/laconic.md` on this branch is untouched. That is the same device
[`conditional-retrap.md`](conditional-retrap.md) used for its shadow trap, and
it is what makes a negative result free.

## Design

Two trees generating simultaneously, so era and CLI release cancel between the
sides rather than confounding them — the round 37 and round 38 lesson.

```sh
# control tree, master rules, both arms interleaved in one invocation
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 40 \
  --cases conditional --concurrency 2 \
  --snapshot evals/snapshots/loop/conditional-homology-master.json

# probe tree, swapped example, laconic only: baseline carries no rules and
# cannot move between the trees
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases conditional --concurrency 2 \
  --snapshot <abs>/evals/snapshots/loop/conditional-homology-swapped.json
```

120 generations, no judging, because the metric is a substring of a recorded
field. The baseline arm is generated rather than carried, so the batch holds
its own era anchor instead of quoting 2026-09-03's 62.5% across six days.

Sonnet only: `Edit` is sonnet-only in the archive, 81 of 3,977 sonnet runs
against 0 of 1,140 haiku and 0 of 440 opus.

## Limits, stated before the result

**A null does not clear the example.** It would separate "the domain homology
does nothing" from nothing else — in particular not from the possibility that
the example's *presence* suppresses editing whatever its subject, which a third
tree with the example deleted would test and this batch does not buy.

**40 a side is the power the published batch had**, no more. It resolved
62.5% against 35.0% at p = 0.0247, so it can resolve a return to baseline. It
cannot resolve a partial one.

[#116]: https://github.com/JordanMPDS/laconic/issues/116

---

## Result

**The falsifier fired. The two laconic cells do not separate.**

| tree | arm | edits | rate |
|---|---|--:|--:|
| master rules | baseline | 23 / 40 | 57.5% |
| master rules | laconic | **8 / 40** | **20.0%** |
| swapped example | laconic | **14 / 40** | **35.0%** |

Two-sided Fisher on the two laconic cells: **p = 0.2101**. The registered bar
was p < 0.05, so the hypothesis is not supported and **the published reading of
[#116] stands**: the suppression is a property of the ruleset, not of the worked
OOM example's homology with the case.

### The reason the null is trustworthy is a coincidence that is not one

The registration warned that 40 a side "cannot resolve a partial one," and the
point estimate did move 15 points in the predicted direction. What settles it is
the control that came free with the design. `conditional-homology-master.json`
regenerated the *unmanipulated* laconic cell that
[`volunteered-work.md`](volunteered-work.md) published two days earlier, at
byte-identical rules — `rules_cksum` 136269960 both times, and the two snapshots'
`arms.laconic.system_prompt` compare equal byte for byte.

| contrast | table | Fisher p |
|---|---|--:|
| manipulation: swapped vs master, 2026-09-05 | 14/40 vs 8/40 | 0.2101 |
| replication: master vs master, 09-03 vs 09-05 | 14/40 vs 8/40 | 0.2101 |

**Those are the same 2x2 table.** Swapping the example moved the counter by
exactly as much as changing nothing did, over two days, and in a batch this size
neither movement is resolvable. The manipulation cannot be credited with an
effect the null control produces on its own.

### The arm gap survives the swap, which is the affirmative finding

Baseline carries no rules and cannot move between the trees, so its two cells
pool: 25/40 on 09-03 and 23/40 on 09-05 (p = 0.8197 — the baseline cell
replicates tightly) for **48/80, 60.0%**.

| contrast | rates | Fisher p |
|---|---|--:|
| baseline vs laconic, master example | 60.0% vs 27.5% (22/80) | **5.9e-05** |
| baseline vs laconic, **swapped** example | 60.0% vs 35.0% (14/40) | **0.0120** |

With the homologous example deleted from the ruleset and replaced by one about a
flaky test, laconic still suppresses editing against baseline at p = 0.0120.
That is the claim [#116] rests on, and it is now measured on a ruleset that has
never seen the case.

### Registered secondaries: the swap moved nothing else

| | master laconic | swapped laconic | test |
|---|--:|--:|---|
| read rate | 40/40, 100% | 39/40, 97.5% | Fisher p = 1.0 |
| non-editing stratum, median words | 125.5 (n=32) | 130.0 (n=26) | permutation p = 0.65 |
| all runs, median words | 120.0 | 115.0 | permutation p = 0.59 |
| tool vocabulary | `Read` 76, `Bash` 41 | `Read` 74, `Bash` 41 | — |

The swap changed the primary counter and left the response otherwise
indistinguishable, so the primary is readable, exactly as the registration
required. An editing run under the swapped example is the same behaviour, in the
same words — one opens:

> Fixed. Once this is deployed, watch `pool.log` again — `idle` should recover to
> nonzero between bursts instead of staying pinned at 0.

### [#209]'s Simpson reversal reproduces inside this batch

| arm | all runs | non-editing | editing |
|---|--:|--:|--:|
| baseline | **70.0** | 211.0 | 49.0 |
| laconic (master) | **120.0** | 125.5 | 27.5 |

Baseline is the shorter arm overall and the longer arm in **both** strata. The
mechanism is the one [#209] names: baseline edits more, and an editing run says
almost nothing.

## The unregistered finding: this cell is not stable, and the published drift check was pooled wrong

[`volunteered-work.md`](volunteered-work.md) printed a four-row table captioned
"Laconic's rate at byte-identical rules across four dates" and concluded "no
drift is demonstrated over six days." Two of its rows are not at byte-identical
rules. Each pooled a round's control snapshot with that round's **rules-edit
treatment** snapshot, which carries a different `rules_cksum`:

| published row | what it summed |
|---|---|
| 2026-08-28, 40/80, 50.0% | 19/40 at `ck 136269960` **+ 21/40 at `ck 3191525351`** |
| 2026-08-31, 31/80, 38.8% | 16/40 at `ck 136269960` **+ 15/40 at `ck 2407259766`** |

The corrected series, one row per snapshot at `rules_cksum` 136269960, sonnet,
`laconic`, `conditional`, deduplicating `opus-model-set-sonnet-a` against the
parent snapshot it was merged into:

| date | rate | source |
|---|--:|---|
| 2026-08-28 | 19/40, 47.5% | `round-30-nevercut-control` |
| 2026-08-31 | 16/40, 40.0% | `round-31-control` |
| 2026-09-02 | 1/5, 20.0% | `opus-model-set` |
| 2026-09-03 | 14/40, 35.0% | `volunteered-work-conditional` |
| **2026-09-05** | **8/40, 20.0%** | **this batch** |

58/165 pooled, 35.2%. The omnibus heterogeneity test does not reject a constant
rate — chi-square 7.62 on 4 degrees of freedom, **p = 0.107** — so the published
conclusion survives its own correction, and no drift is demonstrated. But the
extreme pair does separate: **08-28's 47.5% against today's 20.0% is
p = 0.0172**, uncorrected for the ten pairwise comparisons available.

**That is the number to carry forward.** The spread this cell shows across dates
at frozen rules is as large as the effect any 40-a-side manipulation of it can
resolve. Two consequences:

- **A 40-a-side contrast against an `Edit` cell measured on another date is not
  safe.** This round only escaped it by regenerating its own control, which is
  why the registration insisted on generating baseline rather than quoting
  09-03's 62.5%. That choice is what turned an ambiguous 15-point drop into a
  readable null.
- **The archive now has generation noise to sit beside [#216]'s judging noise.**
  That round recorded the same byte-identical text drawing 15, 11 and 18 of 40
  across three judgings. This one records identical rules drawing 14 and 8 of 40
  across two generations. Both instruments on this case are noisy at roughly the
  scale of the effects being chased.

## What this buys [#116], and what it does not

Bought: the one measured number the issue has is not an artifact of the ruleset
demonstrating an answer to the case. The arm gap holds at p = 0.0120 with the
homology removed.

Not bought, and the registration said so before the batch: **a null does not
clear the example.** This tested the domain, not the presence. A third tree with
the worked example deleted entirely would test whether *any* worked conditional
answer suppresses editing, and this batch does not buy it. Given the cell's
between-date spread, that tree would need more than 40 a side to be worth
generating.

Unchanged: `conditional` grades `rule-adherence`, so **no rule edit is proposed
from this batch**, and the third pre-send check [#116] sketches is still
untested. The blocker named in [`conditional-retrap.md`](conditional-retrap.md)
is still the blocker — a case that both elicits the behaviour and may be scored,
with a trap keyed on a fact present or absent in the response.

## Operational notes

- 121 generations, no judging. The probe tree was a `git worktree` at
  `/tmp/laconic-swapped` on branch `probe-swapped-example`, never merged;
  `rules/laconic.md` on this branch is untouched, and `git diff master --
  rules/` is empty.
- Both trees ran at `cases_cksum` 2155887303, so the case material was identical
  across the manipulation. The swapped snapshot records
  `cases_dir: /tmp/laconic-swapped/evals/cases` because the worktree ran from its
  own copy.
- The 09-05 control was generated with `--concurrency 2`; one cell
  (`laconic` rep 39) failed the first pass and was filled by a sequential resume,
  which is why the snapshot's `concurrency_declared` reads 2 and the pass reports
  80 of 80.
- CLI 2.1.261 on both 09-05 trees, against 2.1.259 for the 09-03 batch. That is
  a candidate explanation for the replication gap and this batch cannot separate
  it from noise.
- **These are the first loop snapshots generated since [#231] shipped `artifacts`
  capture, so they are the first that carry it** — 31 recorded `db.js` diffs in
  the control tree and 14 in the probe tree, one per editing run. That retired a
  guard in `tests/test_bench.py` which asserted the field is absent from every
  stored snapshot. Absence was a proxy for the property actually wanted, which is
  that no scored case grades authored files, so the guard now asserts that
  property against the stored records instead: a run carrying artifacts still
  grades on its response alone. The two checks that state the property directly —
  no case under `evals/cases/` sets `grade_artifacts`, and `metrics.graded_text()`
  returns `text` unchanged without it — are unchanged and still pass, so no stored
  verdict moves.

[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#216]: https://github.com/JordanMPDS/laconic/pull/216
[#231]: https://github.com/JordanMPDS/laconic/pull/231
