# What the loop rejects candidates for, and why [#26]'s revisit condition cannot fire

**No generation calls.** Every number below is computed from committed round
documents by
[`candidate-defects/classify.py`](candidate-defects/classify.py) over
[`candidate-defects/labels.json`](candidate-defects/labels.json), and the whole
of it re-runs in about a second:

```sh
python3 evals/results/loop/candidate-defects/classify.py
python3 evals/results/loop/candidate-defects/classify.py --selftest
```

## Why this unit exists

[#26] proposed replacing the loop's single-candidate step with a workflow —
several proposers reading the failure inventory through different lenses, then
an adversarial panel trying to refute each candidate before it earns a
confirmation round. It was deferred on 2026-08-01 with a condition attached:

> **Why it is deferred, not rejected.** The bottleneck today is the confirmation
> round, not idea generation [...] Parallel proposers only pay off once the loop
> is reliably rejecting candidates **for being weak ideas rather than for
> landing inside the noise floor**.
>
> **Revisit when** the ledger shows several consecutive rounds rejected at step
> 7 for a **failed hypothesis rather than a failed gate**.

Four candidate rounds have rejected since the last accept — 64, 66, 68 and 70 —
and on the face of it every one died on its own registered primary rather than
on a fatal counter. That reads as the condition firing. **It is not, and the
reason is that the two sentences above name different conditions.** The first
sorts rejections three ways: weak ideas, the noise floor, and failed gates. The
second sorts them two ways and puts the noise floor on the wrong side of the
line.

Nobody had ever computed either. This unit does.

## The criterion, and why it is a named fact

The repository's standing rule, registered in `evals/CRITERIA.md` on
2026-09-04, is that a criterion keyed on a **named fact** reproduces and one
asking whether an answer is *framed* correctly does not. The archive has
instantiated both ends of it repeatedly: [#155]'s restatement metric parked at
55.3% precision, the [#305] closing-recap detector at 12%, against
[`volunteered-trap-116.md`](volunteered-trap-116.md)'s 85 of 85 and
[`closing-offers.md`](closing-offers.md)'s 30 of 30, both keyed on identifiers.

"Was this rejection about a weak idea?" is a framing question as normally
asked. It has a named-fact form, and the fact is **the sign of the registered
primary's point estimate**:

| class | condition | what more reps would do |
|---|---|---|
| **idea-defect** | the registered primary's point estimate moved *against* the registered direction, **or** a check the registration named in advance returned the reading that refutes the mechanism | nothing — the idea is wrong about the world |
| **noise-floor** | the point estimate moved *with* the registered direction and the round failed on significance, magnitude or replication | could settle it |
| **failed-gate** | the primary passed and a fatal counter rejected the round | not the candidate's problem at all |

Every round document publishes its primary's control and edit values in a table
and states the registered direction in its own registration, so each label is
read off two printed numbers. `labels.json` records the values, the p, and a
**verbatim line** from the round document; `classify.py` fails if that line
stops appearing, so a round document edited under a label breaks the test
rather than silently invalidating it.

**One tie rule, and it runs against the conclusion.** Where a round's registered
primary and its registered arbiter disagree in sign — round 48 is the only case
— the label is `noise-floor`. This unit exists to test whether idea-defects have
become the dominant rejection class, so an ambiguous round is labelled into the
class that does *not* support that. Round 70 gets the same treatment for a
different reason: its strongest refutation, the unlicensed `deep-*` family
falling by the same factor as the licensed one, is published as a disclosure
rather than as a registered check, and only registered checks count.

## Scope: round 38 onward, and the reason is the control

**Round 38 is the first round whose control was generated simultaneously with
its edit.** Before it, a round compared against a control carried from another
era — and [round 37](round-37.md) measured a syntactic behaviour moving 4.7x in
five days at byte-identical rules, while [round 50](round-50.md) watched
`conditional`'s edit rate fall 50.0% to 21.7% over nine days with the rules
untouched. The criterion here is the *sign of a point estimate*, and against a
carried control that sign is confounded with drift. So rounds 01 to 31 are out
of scope and it is not a judgement about them: they cannot be classified on this
criterion at all.

That leaves 16 candidate rounds, 15 rejections and one accept.

## The composition

```
Candidate rounds from 38: 16 (1 accept, 15 reject)

Rejections by class:
  idea-defect    9 / 15  (60%)
  noise-floor    4 / 15  (27%)
  failed-gate    2 / 15  (13%)

Longest consecutive run of idea-defect: 6
Run of idea-defect at the end of the archive: 0

Last 4 rejections: 64 noise-floor, 66 idea-defect, 68 idea-defect, 70 noise-floor
  weak ideas 2 of 4, noise floor 2 of 4
```

| round | class | registered primary | control | edit | p |
|---|---|---|--:|--:|--:|
| 38 | idea-defect | arrows in prose, three cases, down | 36 | **62** | 0.341 |
| 40 | idea-defect | `output_tokens`, seven cells, down | — | **+7.5** | 0.4531 |
| 44 | idea-defect | arrows, two cases, down | 67 | **78** | 0.498 |
| 45 | idea-defect | arrows on `confirm-rollback`, down | 21 | **23** | 0.8215 |
| 46 | idea-defect | chain-carrying on `walkthrough`, down | 4/100 | **9/100** | 0.2507 |
| 47 | idea-defect | `register-*` prose words, down | 55.5 | **58.0** | 0.9815 |
| 48 | noise-floor | `register-*` prose words, down | 59.5 | 54.5 | 0.6595 |
| 49 | idea-defect | `register-*` prose words, down | 60.5 | **62.5** | 0.7410 |
| 50 | noise-floor | `conditional` edit rate, down | 21.7% | 15.8% | 0.3211 |
| 51 | failed-gate | prose words, four cases, down | passed | passed | 0.005 |
| 52 | failed-gate | prose words, four cases, down | passed | passed | <0.00001 |
| 55 | **accept** | three registered bars | | | |
| 64 | noise-floor | `confirm-*` prose words, down | 62.0 | 57.5 | 1.000 |
| 66 | idea-defect | `design-*` bold-label share, down | 65.0% | 58.1% | 0.250 |
| 68 | idea-defect | already-told prose words, down | — | — | — |
| 70 | noise-floor | `register-*` prose words, replication | 1.000 | 0.946 | 0.0721 |

Bold marks a point estimate on the wrong side of its registered direction.
Rounds 66 and 68 are idea-defects for the other reason: each registered a check
in advance and that check returned the refuting reading. Round 66's registration
named both outcomes before the numbers were in — *"Down with the labels means
the scaffolding was carrying claims; flat means the answer was reformatted and
nothing was removed"* — and prose words read 187.5 to **197.0**. Round 68's
descriptive check was *"meant to confirm the harm and refuted it"*.

## The answer, and it depends on which sentence of [#26] is read

**By the condition sentence — "failed hypothesis rather than failed gate" — it
fired at round 40 and has been firing almost continuously since.** 13 of 15
rejections failed at step 7 on their own target; only rounds 51 and 52 were
rejected by a fatal counter. Under that reading the trigger is satisfied by the
loop's *base state*, which means it can never un-fire and is not a signal about
anything.

**By the rationale sentence — "weak ideas rather than landing inside the noise
floor" — it has not fired, and the recent rounds are the weakest case in the
archive for saying it has.** The last four rejections split 2 and 2, and the run
of consecutive idea-defects at the end of the archive is **zero**: round 70 is
the noise floor, at 0.946 with its point estimate on the registered side of 1.0.

**The archive's longest run of consecutive weak-idea rejections is six — rounds
38, 40, 44, 45, 46 and 47 — and nobody revisited [#26] then.** That is the whole
finding. If six consecutive weak-idea rejections in early September did not
trigger the revisit, four mixed ones in the middle of September do not either,
and the share they come from has not moved: 60% of rejections since round 38,
with no trend a 15-round sample can see.

## What this unit does not establish

- **Nothing about whether a panel would work.** This measures what the loop
  rejects for, not whether an adversarial reader can predict it. Those are
  different claims and the second one is the expensive one.
- **No trend test.** 15 rejections across five weeks cannot resolve a change in
  a 60% share, and none is claimed. The composition is reported; the comparison
  between "recent" and "historical" is descriptive.
- **The labels are one reader's.** They are keyed on printed numbers and carry
  their evidence, which is what makes them auditable rather than reproducible.
  A second labeller is the thing this unit does not buy.
- **Round 15's shape is absent.** It passed step 7 and died at holdout. No round
  in scope did that, so the taxonomy has no class for it and would need one.

## What to do with [#26], and the cheap prospective test

The retrospective route to validating a panel is closed, and it is worth saying
why in one place, because it is the design this unit started on:

1. **The endpoint degenerates.** 13 of 15 rejections are failed hypotheses, so a
   panel that says "this will fail" without reading the candidate scores about
   0.87. A refutation-recall endpoint measured on rejections alone has no
   false-positive leg.
2. **The specificity set does not exist.** Four accepts in the whole archive,
   one of them in scope. Nothing can be measured against that.
3. **The labels are post-hoc.** A round's stated failure reason is written after
   its author saw the result. Asking a panel to predict it measures agreement
   with the author's sense-making, not foresight, and no ablation available here
   separates that from memorisation of a public repository.

Points 1 and 3 came from the `deepseek` and `kimi` reads in
`tools/consult.sh`, which killed a design this unit was otherwise going to
build; the degeneracy arithmetic is `deepseek`'s.

**The test that is not closed costs one paragraph per round.** A round already
commits its registration before it generates anything, so a prediction written
there is blind by construction and dated by git. Adding a registered pre-mortem
— *how do I expect this to fail, and which of the three classes would that be*
— buys one prospective, uncontaminated data point per round at no extra calls,
against rounds that are being bought anyway. After a handful of rounds, [#26]
is decidable on whether the loop's own author can call a weak idea in advance;
if the author cannot, a panel of proposers reading the same inventory is very
unlikely to. That is now step 5 of the loop skill.

**[#26] stays deferred, and its revisit condition is replaced** by one this
script computes: the trailing run of weak-idea rejections exceeding the
archive's longest, which is **6**. It reads 0 today. That rule needs no tuned
constant and re-runs in a second, which is what the old condition never had.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#305]: https://github.com/JordanMPDS/laconic/issues/305
