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
