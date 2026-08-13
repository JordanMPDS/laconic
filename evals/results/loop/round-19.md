# Round 19 — the first edit aimed at evaluative questions, and the first scope that is not eight-ninths sonnet

**Date:** 2026-08-13
**Rules under test:** `rules_cksum` 2970727293
**Baseline:** `evals/snapshots/loop/round-01-n10-v4.json` (+`-judgments`)
**Round artefacts:** `evals/snapshots/loop/round-19.json`, `round-19-judgments.json`
**For:** [#60], and [#46] by construction
**Status:** hypothesis registered here, and the edit committed, before any round
call was made. Results are appended below the line.

## Why this round exists

[#60] reported an evaluative question — "is this methodology sound?" — answered
at ~650 words, and closed with a guess: *"If [#46]'s fix generalizes, this
should fall out of it."*

**That guess is already refuted by committed data.** Round 15's edit, the
relocation tested four times and the only edit ever to pass step 7, scored on
the design and verdict cells together against the `-v3` baseline:

| cell | baseline | round 15 | |
| --- | --: | --: | --- |
| `design-audit-log`/sonnet | 6544 | 3702 | **−2842** |
| `design-alerting`/sonnet | 4651 | 2205 | **−2446** |
| `design-rate-limit`/sonnet | 4012 | 1664 | **−2348** |
| `design-retry`/sonnet | 3842 | 1614 | **−2228** |
| `design-search`/sonnet | 2264 | 1228 | **−1036** |
| `design-audit-log`/haiku | 1486 | 666 | **−821** |
| `verdict-rollout`/haiku | 1716 | 1472 | −244 |
| `verdict-rollout`/sonnet | 3286 | 3112 | −174 |
| `verdict-schema`/sonnet | 2746 | 2648 | −98 |
| `verdict-experiment`/haiku | 1568 | 1560 | −8 |
| `verdict-schema`/haiku | 1293 | 1296 | +3 |
| `verdict-experiment`/sonnet | 3048 | 3370 | **+323** |

**The design cells move by thousands of tokens. The verdict cells do not move
at all.** The [#46] fix does not generalize to evaluative questions, and it never
did. No round call was needed to learn this; it was in `round-15.json` the whole
time.

So [#60] needs its own edit, which is what this round tests.

## The verdict cases are a better token instrument than the design cases

This was the other free finding, and it changes the scope for every future
length round.

[`token-scope.md`](token-scope.md) established that a cell whose baseline is
under 1000 tokens cannot express a compression effect — its own dispersion is
the size of the effect — so those cells are dropped from the scoped sign test.
Applied to all 22 cells of the `-v4` baseline:

| scope | cells | voting | haiku : sonnet | median stdev floor |
| --- | --: | --: | --- | --: |
| design only | 16 | 9 | **1 : 8** | 954 |
| verdict only | 6 | **6** | 3 : 3 | 380 |
| **design + verdict** | 22 | **15** | **4 : 11** | **658** |

**Every verdict cell clears the floor. Seven of sixteen design cells do not.**
Design answers on haiku run 511 to 978 tokens; verdict answers on haiku run 1293
to 1716.

Adding the verdict cases to the scope does three things at once, all of them
improvements measurable before the round: it takes the voting cells from 9 to
15, it lowers the noise floor from 954 to 658, and it takes the scope from
one-haiku-to-eight-sonnet to four-to-eleven. The sign test also gets easier to
satisfy honestly — 8 of 9 cells at p = 0.039 becomes 12 of 15 at p = 0.035.

That last point matters because [#51] and [`token-scope.md`](token-scope.md) are
a long record of this scope being too small and too sonnet-shaped to say
anything. It is the first time it has been neither.

## The edit

Placed first in `Level: full`, and only there.

```diff
 ## Level: full — also cut unrequested substance

+- The subject's size does not set the answer's size; the request's does. A short
+  open question about a large system — "is this sound?", "how would that be
+  built?" — asks for the verdict or the approach and the one or two things that
+  would change it, not for a review of everything you looked at.
 - Lead with the answer or the action taken. Reasoning only if the user needs it
   to act on the answer.
```

**Why `Level: full` and not the top block.** The top block already states the
principle — *"Length scales to the request, at every level"* — and gives two
examples, a yes/no question and a requested report. A short open question about
a large subject is neither, and it falls to the long side by default. But the
top block governs every level including `lite`, and `lite` keeps full reasoning
and context by design; bounding substance there would be wrong. `Level: full` is
the section whose whole job is "also cut unrequested substance". The rule is
placed where its limits are inherited rather than asserted, which is round 10's
lesson.

**Why one bullet for both question shapes.** [#60] says the two are the same
shape with different triggers, and the bullet names both. If it moves the design
cells and not the verdict cells, or the reverse, that is a finding about how
narrow the rule is and it is disclosed either way.

## Hypothesis, registered before the round ran

> Adding a `Level: full` bullet stating that the subject's size does not set the
> answer's size moves `output_tokens` **down** on the eight `design-*` and three
> `verdict-*` cases, while `never_cut_failures`, `quality_fails`, `safety_fails`
> and `violations_total` hold at the baseline's values.

Scope:

```
--target-cases design-alerting,design-audit-log,design-search,design-rate-limit,design-retry,design-cache,design-realtime,design-upload,verdict-experiment,verdict-rollout,verdict-schema
```

Fifteen of those 22 cells vote; the other seven are below the 1000-token floor
and are dropped by the gate, which names them.

## What the round has to reach, registered before it ran

- **12 of 15 voting cells down**, which is sign-test p = 0.035.
- **A median shift larger than 658 tokens**, the median per-cell stdev over the
  scoped cells of the baseline.

For calibration, the same scope scores the three most recent rounds — none of
which targeted length — at 8, 10 and 8 cells down with shifts of +178, −162 and
+113. All three fail it. Round 15's edit on the comparable `-v3` scope reached
10 of 12 and a shift of +1258, which passes.

## Registered risks

- **The verdict cells may be flat again.** They were flat under round 15's edit,
  which is why this round exists, but "flat under one edit" does not mean "movable
  by another". If the six verdict cells hold still and the nine design cells all
  fall, the scope reads 9 of 15, sign p = 0.607, and the round rejects on a
  target that half of it met. That outcome is a real finding about the rule's
  reach and it will be reported as one, not as a near miss.
- **The `verdict-*` quality guard is saturated at pass and stays that way.**
  Across every arm and model ever graded, the three cases read **1,496 pass, 3
  fail, 1 not_exercised** — even `word-compression` passes 100%. They cannot
  discriminate between arms and are not being asked to. Their job here is a
  tripwire with maximum headroom to fall: an edit that shortens evaluative
  answers until they miss the float-money column or the drop-before-deploy
  ordering will show up as a `quality_fails` rise, which is fatal.
- **`design-cache`/haiku and `design-upload`/sonnet have low baseline draws**
  ([#103], [`arrow-forms-across-revisions.md`](arrow-forms-across-revisions.md)).
  Neither votes in this scope — both are below the token floor — so the effect
  is confined to the quality counters, where the measured-rate screen covers
  them.
- **`destructive`/haiku is the never-cut cell to watch**, on round 18's evidence
  that touching answer shape can cost it the `sessions` identifier. This edit
  does not touch the never-cut list or list structure, which is the difference.

## Secondary observations, not targets

- **The design-versus-verdict split**, which is the whole point of naming both
  families. Reported per family whatever the pooled number says.
- The [#88] quality strata line.
- The [#34] arrow-forms disclosure, newly available and reported for the first
  time in a round.

[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#51]: https://github.com/JordanMPDS/laconic/issues/51
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#103]: https://github.com/JordanMPDS/laconic/issues/103
