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

## Result: depth does not inflate the already-told answer, and the register inflates it on both arms

**Decision rule branch 2 fires.** The primary rises — the laconic median goes
from 27.0 prose words to 49.5, a ratio of **1.833 at p = 0.0010** — and the
baseline arm rises with it, 141.5 to 184.5, **1.304 at p = 0.0027**. Round 67's
clause was carried forward verbatim and governs: *a movement that appears on
both arms is the case, not the rules.* The registered log-scale interaction is
null at **p = 0.3375**, so nothing in the registered test set separates the two
arms' rises.

**The decomposition says which factor moved it, and it is not depth.** Four
ordinary prior turns in place of one leave the laconic answer where it was:
27.0 to 30.5, **1.130 at p = 0.1962**, and the small rise it does show is the
same rise the baseline arm shows (ratio of ratios 0.929). The whole of the
primary's movement is the register of the intervening turns, at fixed depth.

180 runs, 90 a side, 0 failed. Nothing judged, because branch 1 did not fire.

### The two contrasts

| contrast | arm | n | `reexplain` | treatment | ratio | p |
|---|---|--:|--:|--:|--:|--:|
| depth alone (`deepexplain`) | baseline | 30 | 141.5 | 170.5 | 1.205 | 0.0008 |
| depth alone (`deepexplain`) | laconic | 30 | 27.0 | 30.5 | 1.130 | **0.1962** |
| depth and register (`fullexplain`) | baseline | 30 | 141.5 | 184.5 | 1.304 | 0.0027 |
| depth and register (`fullexplain`) | laconic | 30 | 27.0 | 49.5 | **1.833** | **0.0010** |

    fullexplain  interaction, log words: ratio of ratios 1.484, p = 0.3375
                 interaction, raw words:                         p = 0.5049
    deepexplain  interaction, log words: ratio of ratios 0.929, p = 0.8725
                 interaction, raw words:                         p = 0.3230

On geometric means, with 95% bootstrap intervals from
`evals/pilot/round69_supplement.py`:

| arm | `deepexplain`/`reexplain` | `fullexplain`/`reexplain` |
|---|---|---|
| baseline | 1.225, 1.105 to 1.361 | 1.212, 1.092 to 1.342 |
| laconic | 1.138, 1.041 to 1.245 | **1.799, 1.564 to 2.058** |

**Depth alone moves the two arms by the same proportion and the register does
not.** The ratio of ratios is 0.929 (0.807 to 1.068) for depth and 1.484 (1.245
to 1.759) for the composition. That second interval excludes 1 while the
registered permutation of the same quantity reads p = 0.3375, and the next
section is why.

### The registered interaction test could not have decided this

The registration moved the interaction to the log scale because round 42 had
recorded the raw-word version being swamped, and said the raw one "carries
nothing" for that reason. **The log scale does not escape it.** The test
shuffles the arm label inside each family, and the arms on this instrument sit
**7.97x apart** on the reference family, so every shuffled group is a mixture of
two separated modes:

| family | log difference of differences | permutation null sd | sampling sd | ratio |
|---|--:|--:|--:|--:|
| `deepexplain` | −0.074 | 0.458 | 0.241 | 1.9x |
| `fullexplain` | +0.395 | 0.410 | 0.216 | 1.9x |

The null the registered test builds is **1.9 times wider than the sampling
distribution of the statistic it is testing**. An effect has to be roughly twice
as large as the data actually require before that test can see it, which is why
a point estimate of 1.484 with a bootstrap interval of 1.245 to 1.759 lands at
p = 0.3375.

**This does not promote the round to branch 1.** The bootstrap interval is a
figure the registration said would be reported beside the test, not the test,
and reading a verdict off it after seeing the registered one come back null is
the exact move pre-registration exists to prevent. The honest statement is the
one branch 2 licenses — the movement appears on both arms — with the disclosure
that the registered control was too blunt to say more, and that **the bluntness
is a property of the instrument rather than of this round's data**: the same
1.9x applies to every arm-label permutation this cluster has run on an
instrument whose arms are 8x apart.

### The magnitude, against the report

[#298] describes 342 prose words where 66 would do. The composition that
inflates this instrument reaches **49.5 words at the median and 71 at the
maximum** on the laconic arm. The longest answer any of the 90 laconic runs
produced is a fifth of the report's, and the largest movement the round can
attribute to anything is 1.833x against the report's 5.2x.

| arm | family | min | median | max |
|---|---|--:|--:|--:|
| laconic | `reexplain` | 5 | 27.0 | 44 |
| laconic | `deepexplain` | 5 | 30.5 | 54 |
| laconic | `fullexplain` | 5 | 49.5 | 71 |
| baseline | `reexplain` | 65 | 141.5 | 196 |
| baseline | `deepexplain` | 108 | 170.5 | 234 |
| baseline | `fullexplain` | 75 | 184.5 | 276 |

**It is not a markup artefact.** Raw whitespace tokens read 36.0, 41.0 and 62.0
on the laconic arm against prose's 27.0, 30.5 and 49.5, so the raw ratio for the
composition is 1.72 against prose's 1.83. The two counts agree.

**It is not the model going back to the file either.** The graded turn carries
`Don't edit anything.` and makes **no tool call in 30/30 runs in five of the six
cells**. The exception is `baseline reexplain`, where 7 of 30 runs call `Bash`
— the unruled arm at one turn of depth sometimes re-reads what it was given.
Neither deeper family does it on either arm, so the rise is not a re-read.

### The three free checks, and what the per-stem table shows

**The manipulation fired, far above its registered bar.** Prose words over the
middle turns, laconic arm: `deepexplain` 157.0 against `fullexplain` **1135.5**,
a factor of **7.2** where the registration required at least 2. On the baseline
arm it is 1002.5 against 2337.5. `reexplain` has no middle turns and reads 0 by
construction. No run in any cell called an editing tool on a middle turn
(0/30 everywhere), so the licence lengthened the reply rather than moving the
work into a file, which is what separates this manipulation from round 67's.

**The never-cut keyword is clean at ceiling.** `date_trunc` is present in
**10/10** graded turns in all six `index` cells. Nothing was compressed away.

**The floor stem replicates and then rises only under the register.**
`reexplain-metric` reads a median of **5.0** prose words here against the 6.0
round 68 measured on its own 30 runs. It does not move at depth (5.0, p =
0.5117) and it does move under the composition (13.0, p = 0.0003).

| arm | stem | `reexplain` | `deepexplain` | p | `fullexplain` | p |
|---|---|--:|--:|--:|--:|--:|
| laconic | `index` | 35.5 | 46.5 | 0.0349 | 56.0 | 0.0054 |
| laconic | `metric` | 5.0 | 5.0 | 0.5117 | 13.0 | 0.0003 |
| laconic | `rollback` | 28.0 | 38.5 | 0.0134 | 51.5 | 0.0001 |
| baseline | `index` | 141.0 | 189.5 | 0.0081 | 184.5 | 0.0028 |
| baseline | `metric` | 136.0 | 151.0 | 0.1525 | 140.0 | 0.8767 |
| baseline | `rollback` | 164.5 | 191.5 | 0.0367 | 227.0 | 0.0001 |

Three of three laconic stems rise under the composition and the pooled null is
not a floor hiding two movers. The registration wrote in advance that three
cells cannot reach alpha on a sign test, so this table is consistency and
carries no verdict.

**The extra words are not obviously restatement.** The round does not measure
restatement and cannot, but the median `fullexplain-index` answer is worth
reading beside the median `reexplain-index` one, because the difference is what
the whole result is made of:

> `events_tenant_id_idx` is an existing btree index on `tenant_id` alone; it's
> not chosen for this query because the target tenant is 38% of the table.
> `events_day_tenant_idx` is the proposed new index from option 1, on
> `(date_trunc('day', created_at), tenant_id)`, which would match the query's
> actual predicate.

> `events_tenant_id_idx` is the existing btree index on `events(tenant_id)` —
> it's in production already but unused by this query, since a tenant matching
> 38% of the table makes the planner prefer a sequential scan.
> `events_day_tenant_idx` is not built yet — it's one of the two fixes
> FINDINGS.md proposes: `CREATE INDEX CONCURRENTLY events_day_tenant_idx ON
> events (date_trunc('day', created_at), tenant_id)`, indexing the actual
> expression the query filters on (written with an explicit `'UTC'` argument to
> satisfy `IMMUTABLE`).

Twenty-two more prose words, and they carry the DDL, the planner's reason and
the `IMMUTABLE` argument. That is a longer answer, not a padded one. #298's harm
is 239 restated words inside 342; nothing of that shape is present at 49.5.

### What this closes and what it does not

**Depth is refuted as the mechanism, on the instrument built to test it.** Round
68 named session depth as the cluster's only remaining candidate and said so
explicitly. Four ordinary turns of it move the laconic already-told answer by
1.130 (p = 0.1962), against the baseline arm's 1.205 on the same contrast. The
answer stays short because the material has already been delivered, and adding
turns does not undo that. [`over-length-cluster.md`](over-length-cluster.md) is
updated: the candidate it named is measured and it is not the one.

**The register effect travels to this question, and it is the third instrument
to show it.** [`register-inheritance-136.md`](register-inheritance-136.md)
measured 1.677 on a closed confirmation with the baseline arm flat at p =
0.9135. Here the same three licensed-long turns produce 1.833 on an already-told
definition request — and the baseline arm is **not** flat. That difference is
the round's most useful unpublished lead: the same manipulation separates the
arms on one question type and does not on another, and nothing in the archive
says why.

**Round 70 should not aim a rule edit at this.** `bash tools/candidate-due.sh`
requires the next round to carry one, and this round's result says where not to
point it. There is no measured laconic-specific inflation to remove: the one
contrast that moves the laconic arm moves the unruled arm too, the movement
tops out at 71 words, and the answers that carry it are correct and dense. An
edit aimed at the composition would be aimed at a case effect. Round 70's
candidate belongs on a different `rules` issue.

**What the round leaves open is the interaction test, not the rule.** The
cluster has now run at least four arm-label permutations across an 8x arm gap
and read nulls off all of them. The 1.9x figure above says those nulls bound
less than they appear to. A paired or stratified interaction statistic — the
bootstrap used here, or a within-stem pairing — is a harness change of maybe
fifty lines and it would re-decide, cheaply, several rounds' worth of stored
interaction nulls. That is a backlog issue, not a round.

**Bought 2026-09-22, and this round's reading survives it.**
[`interaction-null-298.md`](interaction-null-298.md) built the corrected test
and measured the legacy one's false-positive rate at **0.000 in a thousand
draws** — so the "too blunt to say more" above is blunter than it reads: that
test fires on nothing at alpha 0.05 and needs about 1.75x before it detects an
effect half the time. Under a correctly sized null this round's `fullexplain`
interaction moves **0.3375 to 0.0737** and still does not cross alpha, and
`deepexplain` moves 0.8725 to 0.7638. **Branch 2 stands unchanged**: the
movement appears on both arms. One stored interaction elsewhere did cross, and
it is `register-inheritance-136`'s, which its own document had already reported
as post-hoc and declined to lean on. Neither the paired statistic nor the
within-stem pairing this paragraph proposed is what shipped — both were
measured to be the same defect pointed at the other label.

**Four prior turns is still not a multi-hour session.** The registration said
so before the numbers and it is still true. The round establishes that depth
does not inflate the already-told answer at the depths this repository can
generate, and it cannot speak to hour-long sessions. The difference from round
68 is that the follow-up is no longer "build a deeper instrument": depth now has
a measured null at the depth the cluster could reach, so a deeper instrument
buys a bound rather than a candidate.

## Registration and generation notes

**The round was sharded three ways, which the registration's command was not.**
The registered command names one snapshot at `--concurrency 3`; the round ran
as three `run.py` processes at rep offsets 0, 4 and 7, each generating both arms
and all nine cells, unioned by `python3 evals/bench/merge.py
evals/snapshots/loop/round-69-{a,b,c}.json --out evals/snapshots/loop/round-69.json`.
Every shard interleaves the two arms, so the simultaneity [round 38](round-38.md)
requires holds inside each shard rather than only in aggregate. All three
declare `--concurrency 3`.

**Generation was interrupted by a usage limit and resumed.** The first pass
started at 00:02:44Z on 2026-09-16 and all three shards stopped between 01:20
and 01:21Z, each after 8 consecutive empty-text failures, which is
`--max-consecutive-failures`' default and the guard working as designed: the
window had emptied and every shard was failing instantly. 24 failed keys were
left recorded as `ok: false`. The second pass ran from 04:13Z to 04:47Z and
regenerated all 24 rather than carrying them, because a failed key is not
recorded as done. Both passes are named in every shard's `generators` list and
the round finishes at **180 runs, 0 failed**, 10 reps in every one of the 18
cells.

**One instrument throughout.** `rules_cksum` 594915793 and `cases_cksum`
3922452357 on all three shards and on the merge, which is the [#69] guard
saying the two passes are one instrument. All 180 runs are stamped CLI
**2.1.272**; `python3 evals/bench/release.py evals/snapshots/loop/round-69.json`
reports no unreadable span and no arm imbalanced across a release.
`python3 evals/bench/concurrency.py` reconstructs a peak of 1 CLI invocation in
flight per shard arm-day and 3 on the merged file against a declared 3, so
nothing here is in the audit's failure list; its 19 flagged arm-days are the
August snapshots that predate the flag.

**Nothing was judged**, per the registration: the quality verdict is bought only
if branch 1 fires.

**One file was added after generation and it computes no verdict.**
`evals/pilot/round69_supplement.py` produces the geometric means, the bootstrap
intervals, the raw-token column, the tool-call counts and the resolution table
above. It imports `score_register.graded_words` rather than reimplementing the
graded turn, so the figures beside the test are extracted by the same code as
the test. `score_register.py` itself is byte-identical to the version committed
with the registration.

**The round cost $28.88** over 180 runs and 720 CLI calls: $18.05 on the
baseline arm and $10.83 on the laconic one, of which the `fullexplain` family is
$15.84 — the licensed-long middle turns are most of the bill, which is what the
third family was bought with.

[#69]: https://github.com/JordanMPDS/laconic/issues/69
