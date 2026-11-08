# Reserved holdout cases

Scored only at step 9 of a candidate round, and never during development.
Nothing here appears in a published benchmark table: a holdout case that shows
up in a table stops being a holdout the moment somebody optimizes against it.

A case may decide ten rounds and then retires into `evals/cases`, replaced by a
new scenario for the same coverage slot; one that decides a reject retires at
once. `report.py` prints each case's count on every verdict. The rule and its
reasons are step 9 of the loop skill
([#466](https://github.com/JordanMPDS/laconic/issues/466)).

Reached only by `--cases-dir evals/holdout`, which `run.py`, `judge.py`,
`report.py` and `review.py` all accept. The default glob does not see them, and
`tests/test_evals_layout.sh` fails if one appears under `evals/cases/`.

Coverage: two never-cut items (a destructive action, an ordered procedure), one
requested explanation, one ordinary short question whose correct answer is
brief, one bare design question ("how would that be built?") whose
fixture-anchored answer reuses a mechanism the service already runs
([#46](https://github.com/JordanMPDS/laconic/issues/46)), and one evaluative
question ("is this policy sound?") whose fixture contradicts itself
([#60](https://github.com/JordanMPDS/laconic/issues/60)).

`tests/test_evals_layout.sh` holds these traps to the same vocabulary check as
the scored suite. `holdout-short` stays `quality` and grades only whether the
answer is right: until [#468](https://github.com/JordanMPDS/laconic/issues/468)
it also failed "unrequested branching-workflow advice", which grades form.
Relabelling it `rule-adherence` instead would have taken its correctness check
out of this gate, because `judge.py` skips a case whose verdict feeds no fatal
counter.
