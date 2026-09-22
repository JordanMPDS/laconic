# Pilot cases

Cases under test, not in the scored suite. Reached only by
`--cases-dir evals/pilot`; the default glob does not see them, so nothing here
changes `cases_cksum`, joins a round's fatal counters, or appears in a
published table.

A case lives here while the question is whether it measures anything. It moves
to `evals/cases/` only with a pilot behind it and a seeded baseline — adding one
there changes the checksum every future round carries, and a case absent from
the baseline reads as a rise on every counter it touches rather than as
unchanged. `tests/test_evals_layout.sh` holds these to the same `expect.json`
contract as the scored cases, including the rule that a `quality` trap may not
grade form.

## `authored-file` and `authored-reply`

A minimal pair for [#150]'s second half — whether the rules reach a file the
model authors, or stop at the response. Same fixture, same question, same trap,
byte for byte. They differ in where the answer is meant to go:

- `authored-reply` asks for the explanation in the response, and ends
  `Don't edit anything.` like every other case in the suite.
- `authored-file` asks for `ONBOARDING.md` written into the workspace, and
  carries `grade_artifacts` so the judge is shown the file rather than the
  one-line reply that usually accompanies it.

[#150]: https://github.com/JordanMPDS/laconic/issues/150

## `register-index`, `register-metric`, `register-rollback`

The matched pair for [#136]'s remaining gap, and the reason `deep-index`,
`deep-metric` and `deep-rollback` are symlinked in here: `run.py` takes one
`--cases-dir`, and the two families have to be generated in one interleaved
pass or era does the comparing. The symlink is not a copy, so the control
cannot drift from the case the scored suite ships.

Each `register-*` case is its `deep-*` twin with turns 1 and 5 byte-identical
and turns 2 to 4 asking the same three questions verbatim, plus an explicit
request for the full form — a complete checklist, the whole argument step by
step, a table with the evidence for each row. `rules/laconic.md` licenses all
three at length, so a correct laconic run answers them long. The graded turn is
then the same closed confirmation asked after four of the model's own answers
in two different registers, which is the mechanism [#136] reports and which
`deep-*` alone cannot produce.

`tests/test_evals_layout.sh` holds the pair to that contract. Scored by
`score_register.py`; the result is in
[`register-inheritance-136.md`](../results/loop/register-inheritance-136.md).

**The pilot answered its question and the pair stays here.** Laconic's graded
turn reads 31.0 words after `deep-*`'s short stretch and 52.0 after
`register-*`'s licensed one, permutation p < 0.00001 on 30 runs a side and
three stems of three; the baseline arm reads 185.5 against 190.5, p = 0.9135,
zero stems of three. Promoting to `evals/cases/` is a decision for the rule
edit that wants to be scored here — [#60]'s persistence clause — because it
moves `cases_cksum` for every future round and needs a seeded baseline first.

**It has since carried a scored round without being promoted, which is what the
directory is for.** [Round 70](../results/loop/round-70.md) targeted the
licensed stretch itself — prose summed over `register-*`'s turns 2 to 4, with
`deep-*` as the unlicensed discriminator — and the same pair supplied both the
effect and the control that made it readable. The scoped arm accepted at 0.903
(p = 0.0247) with `deep-*` flat at 1.040; the replication read 0.946 (p = 0.0721)
with `deep-*` falling 0.945 alongside it, and the edit reverted. The pair is
sound and the round is the thing that failed, so nothing here changed.

**Two families are borrowed rather than resident.** `register-*` and `deep-*`
are also `fullexplain-*`'s and `deepexplain-*`'s source of middle turns, so an
edit to either changes three designs at once, and `tests/test_evals_layout.sh`
holds every one of those contracts.

[#60]: https://github.com/JordanMPDS/laconic/issues/60

## `work-index`, `work-metric`, `work-rollback`

`register-*`'s sibling, and the same pair shape against the same `deep-*`
control: turn 1 and turn 5 byte-identical, one fixture by symlink, the trap and
the grading unchanged, and only turns 2 to 4 manipulated. Where `register-*`
lengthens those turns, `work-*` moves their deliverable out of the reply and
into the fixture file — the same three questions, answered by writing a section
into `FINDINGS.md`, `ANALYSIS.md` or `INCIDENT.md`.

It exists for the one explanation
[`over-length-cluster.md`](../results/loop/over-length-cluster.md) has left for
the gap between the field reports and the instrument: *a real session
interleaves work with questions*, and every turn of the scored suite ends
`Don't edit anything.` The graded turn keeps that clause, which is what holds
`CRITERIA.md`'s rule — turn 5 is the only turn that produces a verdict — and
which incidentally holds standing permission constant on the turn being
measured, so a movement there cannot be the permission.

`tests/test_evals_layout.sh` holds the pair to the same contract as
`register-*`, plus a second check that the editing prohibition is on the graded
turn and on no other. Scored by `score_register.py <snapshot> 67 work`;
registered in [`round-67.md`](../results/loop/round-67.md).

[#136]: https://github.com/JordanMPDS/laconic/issues/136

## `explain-*`, `reexplain-*`, `deepexplain-*`, `fullexplain-*`

One graded question per stem, asked after four different stretches of the
model's own output. All four families share one fixture with `deep-*` by symlink
and one byte-identical trap, and the graded question is byte-identical across
all four — `explain-*` differs only by carrying the read instruction that
`reexplain-*`'s turn 1 already carried, exactly as `confirm-*` is `recall-*`'s
cold twin.

| family | turns | the graded turn arrives after |
|---|--:|---|
| `explain-*` | 1 | nothing; asked cold |
| `reexplain-*` | 2 | one turn that delivered the material |
| `deepexplain-*` | 5 | four turns, ordinary register (`deep-*`'s questions) |
| `fullexplain-*` | 5 | four turns the rules license at length (`register-*`'s) |

`explain-*` and `reexplain-*` are [#298]'s pair, built for
[round 68](../results/loop/round-68.md), which **refuted the report's premise**:
on the laconic arm the already-told question runs 27.0 prose words against the
cold question's 65.0, a ratio of 0.415 at p < 0.0001 and three stems of three.
Given the material once, the model does not restate it — it points back, and
its graded turn makes zero tool calls in 90 of 90 runs where the cold family
makes one or two.

`deepexplain-*` and `fullexplain-*` are [round 69](../results/loop/round-69.md)'s
two depth twins of `reexplain-*`, and they exist because round 68's result and
[#298]'s report are only compatible if the behaviour is a function of session
depth. Each borrows turns 2 to 4 verbatim from an existing five-turn family, so
the three-family design decomposes depth from register: `reexplain-*` against
`deepexplain-*` is depth alone, `deepexplain-*` against `fullexplain-*` is
register alone at fixed depth, and `reexplain-*` against `fullexplain-*` is the
composition the report describes. The third family is `kimi`'s recommendation
through `tools/consult.sh`, against a two-family design that could read neither
a rise nor a null.

`tests/test_evals_layout.sh` holds both contracts: the cold pair, and the two
twins against `reexplain-*` and against the family each borrows its middle turns
from. Scored by `score_register.py <snapshot> 69 fullexplain reexplain` and the
same command with `deepexplain` — the graded turn is the run's last turn, which
is what lets one scorer compare a two-turn family against a five-turn one.

**Read the interaction line off the corrected null.** The arm-label permutation
these rounds registered builds a null about 1.9x wider than the statistic's own
sampling distribution, at a measured false-positive rate of 0.000. The scorers
now print `metrics.interaction_permutation` beside it, and
[`../results/loop/interaction-null-298.md`](../results/loop/interaction-null-298.md)
carries the calibration and the re-scored archive.

[#298]: https://github.com/JordanMPDS/laconic/issues/298

## `settled-*` and `unsettled-*`

The true-premise instrument for [#136] and [#305], registered in
[`../results/loop/true-premise-136.md`](../results/loop/true-premise-136.md).
Three decision records, each asked about twice: once with a premise the record
supports, where a bare confirmation is the complete answer, and once with a
premise it contradicts, where a denial and a correction are. The twin shares its
fixture by symlink and differs from its settled half only in the premise, which
`tests/test_evals_layout.sh` holds it to.

Every closed question in the scored suite carries a false or partial premise, so
a complete answer there is 80 to 145 words of required correction and no count
endpoint can convict one response. These are the first cases where surplus is
unrequested by construction rather than by a redundancy judgement.

[#305]: https://github.com/JordanMPDS/laconic/issues/305

## `edit-service`, and `drift-service` symlinked beside it

[#113]'s editing regime, registered in
[`../results/loop/closing-edit-113.md`](../results/loop/closing-edit-113.md).
`drift-service` asks five design questions and forbids editing on every turn,
which is why laconic's 0 of 525 closing offers on it says nothing about the
editing session the report came from. `edit-service` is the same five questions
over the same fixture with "Don't edit anything." replaced by "Go ahead and make
the change." on turns 1, 2, 4 and 5, and dropped on turn 3, a walk-through with
no change to make. The scored case is symlinked in, not copied, so both halves
are generated in one interleaved pass and the control cannot drift from the case
the suite ships. `tests/test_evals_layout.sh` holds the pair to that contract.
Scored by `score_closing_edit.py`.

[#113]: https://github.com/JordanMPDS/laconic/issues/113
