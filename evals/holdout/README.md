# Reserved holdout cases

Scored once, at step 9 of a loop round, and never during development. Nothing
here appears in a published benchmark table: a holdout case that shows up in a
table stops being a holdout the moment somebody optimizes against it.

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
