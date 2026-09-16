# Round 69: the already-told question, asked at depth (#298)

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are why this round has the scope and
the power it has. This file, the two new case families, the layout contract and
the scorer change are committed in one commit before any generation, following
[round 38](round-38.md) through [round 68](round-68.md).

**This round proposes no rule edit.** `bash tools/candidate-due.sh` exits 0:
[round 68](round-68.md) carried a candidate and rejected it, so round 69 may
measure. It is the one measuring round the cap allows, and round 70 has to carry
an edit. The reason to spend the allowance here rather than on round 70's
candidate is stated under **Why this round exists**: round 68 rejected because
the harm was absent from its instrument, and an edit cannot be scored against a
harm the instrument cannot produce.

## Why this round exists

[Round 68](round-68.md) built the cleanest pair this cluster has and refuted its
own premise. `explain-*` asks a definition question cold; `reexplain-*` asks
`deep-*`'s open diagnosis question first, so the model's own answer has already
delivered the rationale before the same definition request arrives. On the
laconic arm at master rules the already-told question is **less than half as
long** as the cold one — 27.0 prose words against 65.0, ratio 0.415,
permutation p < 0.0001, three stems of three, geometric-mean 95% interval 0.287
to 0.444.

[#298] reports the opposite, by a factor of five: seven words asked deep in a
long analytical session, answered in 342 prose words of which 239 restated
claims earlier turns had delivered, against a 66-word correct answer. Round 68's
own reading of the gap is this round's subject:

> #298's instance is **one definition request deep in a long analytical
> session**, and this instrument's is **one definition request after exactly
> one prior turn**. At one turn of depth the model compresses by 2.4x
> unprompted. The report describes 342 words where 66 would do, which is a 5.2x
> expansion, and the two observations are only compatible if the behaviour is a
> function of session depth rather than of the material having been delivered
> once.
>
> **That is a testable follow-up and this round did not test it.**

It also named where that leaves the cluster:

> Depth is now the common shape in three results, and
> [`over-length-cluster.md`](over-length-cluster.md) has no named candidate that
> is not depth.

So this round tests depth on round 68's instrument, and it is the round that
decides whether the cluster has a target left to aim a rule at.

## What the archive already says about depth, and why it does not answer this

Three committed results bear on it, and each holds one factor while moving the
other. Every figure below is the laconic arm, computed from the named snapshot.

| what moved | reference | treatment | laconic | baseline |
|---|---|---|--:|--:|
| depth, ordinary prior turns ([round 42](round-42.md)) | `confirm-*`, 1 turn | `deep-*`, 5 turns | 98.0 → 30.5 (**−68.9%**) | 139.0 → 210.5 (**+51.4%**) |
| register, depth held at 5 ([`register-inheritance-136.md`](register-inheritance-136.md)) | `deep-*` | `register-*` | 31.0 → 52.0 (**1.677x**, p < 0.00001) | 185.5 → 190.5 (p = 0.9135) |
| work in place of prose, depth held at 5 ([round 67](round-67.md)) | `deep-*` | `work-*` | 56.0 → 37.5 (0.670) | 188.5 → 145.0 (0.769) |

Read together: **depth with ordinary prior turns makes the laconic answer
shorter, and only a licensed-long stretch of the model's own prose makes it
longer.** `register-*` is the one manipulation in this cluster's history that
produced a laconic rise with the baseline arm standing still, which is what
makes it a rules effect rather than a case effect.

**None of the three asks an already-told question.** All three grade a closed
confirmation (`deep-*` turn 5: *"so the fix is adding the index on created_at,
correct?"*), which is a different request from *"what is X?"* asked about
material the transcript already holds. #298 is about the second. So the two
factors the archive has measured separately have never been composed on the
question the report is actually about, and that composition is this round.

## The instrument: one graded question, three stretches of the model's own output

Two new families in `evals/pilot`, each five turns, each sharing one fixture per
stem with `reexplain-*` by symlink:

- **`reexplain-*`** — the existing anchor. Turn 1 delivers the material, the
  graded turn is turn 2. One prior turn, ordinary register.
- **`deepexplain-*`** — turn 1 byte-identical, **turns 2 to 4 are `deep-*`'s
  three questions verbatim**, graded turn 5 byte-identical to `reexplain-*`'s
  turn 2. Four prior turns, ordinary register.
- **`fullexplain-*`** — turn 1 byte-identical, **turns 2 to 4 are `register-*`'s
  three questions verbatim**, graded turn 5 byte-identical to `reexplain-*`'s
  turn 2. Four prior turns, and `rules/laconic.md` licenses all three of those
  turns at length (*"a report, walkthrough, comparison, or explanation the user
  asked for gets full detail"*).

`deepexplain-index` against `fullexplain-index`, turn 2, in full:

    what would you check first to confirm that diagnosis? Don't edit anything.

    what would you check first to confirm that diagnosis? Give me the complete
    checklist, every check written out in full, not a summary. Don't edit
    anything.

**That is the whole difference between the two twins**, on each of three turns.
And the whole difference between `deepexplain-*` and `reexplain-*` is that three
ordinary turns sit between the material being delivered and the definition
request. So the three families decompose the two factors:

| family | prior turns | register of those turns |
|---|--:|---|
| `reexplain-*` | 1 | ordinary |
| `deepexplain-*` | 4 | ordinary |
| `fullexplain-*` | 4 | licensed long |

`reexplain-*` against `deepexplain-*` is depth alone. `deepexplain-*` against
`fullexplain-*` is register alone, at fixed depth. `reexplain-*` against
`fullexplain-*` is the composition #298 describes.

**The third family is why this round costs 180 runs rather than 120, and it is
here because `kimi` argued for it** through `tools/consult.sh`. The two-family
version was the design going in. Its objection was that a two-family round can
read neither outcome: a rise cannot separate "the register effect replicates at
depth" from "depth amplifies the register effect", and a null cannot separate
"depth suppresses it" from "the register effect does not travel to this
question". Composing two separately-measured factors does not license assuming
they are additive, and discovering the interaction structure is what the round
is for. The other two families are the same three questions and the same graded
turn, so the third family buys the decomposition at 50% more generation and no
new instrument.

Every turn of all three families carries `Don't edit anything.`, which
`CRITERIA.md` requires and which `deep-*` and `register-*` already carried.
`tests/test_evals_layout.sh` holds the contract: five turns, turn 1 and the
graded turn byte-identical to `reexplain-*`'s, turns 2 to 4 byte-identical to
the family they are borrowed from, the same trap, `never_cut` and `grading`, the
same fixture, and the two twins' middle turns not identical to each other.

## Registered endpoints

**Primary: median prose words on the graded turn, laconic arm,
`fullexplain-*` against `reexplain-*`.** Two-sided permutation on the family
label at seed 69. Registered direction: **up** — #298's expansion, if it is
reachable on this instrument, is reachable here.

**The control that says whether a movement is the rules: the same contrast on
the baseline arm, and the log-scale interaction between them.** Round 67's
clause governs and is carried forward verbatim: *a movement that appears on both
arms is the case, not the rules.* The raw-word interaction is reported beside it
and carries nothing, for the reason round 42 recorded — with the arms an order
of magnitude apart, shuffling the arm label builds each group as a mixture of
two separated modes and the null distribution is dominated by which arm drew the
long answers.

**The decomposition, registered as a second contrast and not as a second
verdict: `deepexplain-*` against `reexplain-*`, same test.** It attributes
whatever the primary finds to depth, to register, or to their interaction. It is
not a gate; the round's verdict is the primary's.

**Manipulation check, with a bar registered in advance.** Prose words summed
over the middle turns, per run, laconic arm: **`fullexplain-*` at least twice
`deepexplain-*`**. The licence has to visibly fire, or the round measured
nothing about register. `register-inheritance-136.md` read 77.5 against 704.0 on
this quantity, so the bar is far below the archive's effect and exists to catch
the licence not firing at all. `reexplain-*` has no middle turns and reads 0 by
construction.

**Floor check, free, and it is why a null is readable.** `reexplain-metric`'s
graded answer already sits at a median of **6.0 prose words** with a maximum of
11 (computed 2026-09-15 from `round-68-control.json`, n = 30), against
`reexplain-index` at 32.5 and `reexplain-rollback` at 29.0. That stem cannot
fall and has room only to rise, so a per-stem table is published and a pooled
null that is three nulls reads differently from one that is a floor plus two
nulls. Two further free checks separate "short because the rule held" from
"short because there was nothing left to say": the never-cut keyword `date_trunc`
on the `index` stem's graded turn, and the count of tool calls on the graded
turn — round 68 measured `reexplain-*` making **zero in 90/90** and `explain-*`
making one or two in 90/90, so a family that goes back to the file is behaving
differently rather than answering from context.

## The registered decision rule, written before any generation

1. **The primary rises and the interaction holds** — the laconic
   `fullexplain`/`reexplain` ratio is above 1 at p < 0.05, and the log-scale
   interaction against baseline is in the same direction. #298's mechanism
   reproduces at depth. The round reports the magnitude reached against the
   report's 5.2x, and **round 70 has a live target to aim a rule edit at**,
   which is the outcome this round is spent to buy.
2. **The primary rises and the baseline arm rises with it** — round 67's clause
   applies and the movement is the case. Reported as such, and the cluster is no
   better off than before.
3. **The primary is null.** The already-told question does not inflate at depth,
   with the register licensed, on the instrument that reproduces the report's own
   question. Taken with rounds 42, 67 and 68, **the cluster has no named
   candidate mechanism left**, and the honest conclusion is that a five-turn
   synthetic chain does not reach what a multi-hour session does. That is a
   stopping decision, not a rule edit: it says round 70's candidate should be
   aimed somewhere else, and it stops the loop buying rounds 71 and 72 against
   the same unreproduced harm. `kimi`'s framing is adopted for how to state it —
   the plausible sufficiency hypotheses are falsified, which is not the same
   claim as the rules being fine.
4. **The primary falls.** Depth compresses the already-told answer *further*.
   Reported, and it is the strongest available statement that the reported harm
   is outside this instrument class.

**Nothing is judged unless branch 1 fires.** Round 68's discipline: the quality
verdict is bought only when the primary buys it, because a null primary makes the
judge calls answer no question the round asked.

## Power, stated before the numbers

Computed 2026-09-15 by resampling `round-68-control.json`'s 90 stored
`reexplain-*` laconic runs at master rules (median 27.0, mean 22.9, sd 12.9),
2,000 trials of the registered permutation at 30 runs a side, alpha 0.05:

| true ratio | power |
|---|--:|
| 1.000 | 0.052 |
| 1.400 | 0.587 |
| 1.677 | **0.926** |
| 2.000 | 0.996 |
| 5.200 | 1.000 |

1.677 is `register-*`'s measured effect on the closed question, so the round is
powered at 0.93 to see the register mechanism carry over at its archive
magnitude, and essentially certain to see #298's reported 5.2x. It is
underpowered below about 1.4, and a null therefore bounds the effect rather than
excluding one: the interval on the ratio is reported with the result, as round 68
did.

## The command

```sh
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 10 \
  --cases 'reexplain-*,deepexplain-*,fullexplain-*' --cases-dir evals/pilot \
  --turn-delivery plugin --concurrency 3 \
  --snapshot evals/snapshots/loop/round-69.json
```

Three families, three stems, two arms, ten reps: **180 runs and 720 CLI calls**,
because `reexplain-*` is two turns and the twins are five. One snapshot and one
interleaved pass, which is what holds era: both arms share master rules, so
unlike round 68 this round needs no second worktree — the arm is the system
prompt, not the rules revision.

`--turn-delivery plugin` because every claim here is about the product, and
because `repeat` would re-assert the whole slice on the graded turn and make the
depth question unaskable. Sonnet only: the register pilot, round 42, round 67
and round 68 are all sonnet, and a haiku arm would be a second contrast with no
stored comparison to register against.

Scored by `evals/pilot/score_register.py`, run twice:

```sh
python3 evals/pilot/score_register.py evals/snapshots/loop/round-69.json 69 fullexplain reexplain
python3 evals/pilot/score_register.py evals/snapshots/loop/round-69.json 69 deepexplain reexplain
```

**That scorer is #136's, generalised rather than copied**, which its own
docstring argues for: a copy is a second place for the permutation, the
stratification and the broken-interaction note to drift. Two changes, both
committed with this file. The reference family becomes a parameter alongside the
treatment one; and the graded turn becomes the run's **last** turn rather than
turn 5, because this is the first pair whose two families have different turn
counts. On every five-turn pair the last turn *is* turn 5, so
`register-inheritance-136.md`'s and round 67's published figures reproduce
byte-for-byte from their stored snapshots — verified before this commit, and the
only diff in either scorer output is three table headings.

## What this round cannot establish

- **It does not measure restatement.** The endpoint is prose words on the graded
  turn, and #298's harm is 70% restatement specifically. [#155]'s detectors are
  parked at 55.3% precision and cannot be promoted inside a round, and as #298
  argues, its restated words are non-redundant *within* the response, so a
  single-turn judge scores them clean. A cross-turn detector is a separate unit.
  What the word count can do is say whether the answer inflates at all: #298's
  342 words cannot happen inside a 27-word answer.
- **Four prior turns is not a multi-hour session.** If depth is the mechanism,
  this round establishes its sign and not its ceiling. The report's session ran
  for hours; the largest depth any case in this repository reaches is five turns.
  A null under branch 3 is therefore a statement about this instrument class,
  which is exactly why branch 3 is written as a stopping decision rather than as
  a finding about the rules.
- **Sonnet only, and three stems.** Three cells cannot reach alpha on a sign
  test — the minimum two-sided p over three is 0.25 — so the per-stem table is a
  consistency reading and carries no verdict, as in rounds 67 and 68.
- **It tests the composition, not every composition.** `register-*`'s three
  questions are one way to license length. A null bounds this licence at this
  depth on this question.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#298]: https://github.com/JordanMPDS/laconic/issues/298

## Results

<!-- Nothing above this line has been computed. -->
