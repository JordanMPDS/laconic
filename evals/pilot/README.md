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

[#136]: https://github.com/JordanMPDS/laconic/issues/136
