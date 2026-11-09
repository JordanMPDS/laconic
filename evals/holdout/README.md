# Reserved holdout cases

Scored only at step 9 of a candidate round, and never during development.
Nothing here appears in a published benchmark table: a holdout case that shows
up in a table stops being a holdout the moment somebody optimizes against it.

A case may decide ten rounds and then retires into `evals/cases`, replaced by a
new scenario for the same coverage slot; one that decides a reject retires at
once. `report.py` prints each case's count on every verdict. The rule and its
reasons are step 9 of the loop skill
([#466](https://github.com/JordanMPDS/laconic/issues/466)).

The set here is the second generation, authored on 2026-11-08 at the first
refresh ([#566](https://github.com/JordanMPDS/laconic/issues/566)). The first
six decided seventeen rounds each and now sit in `evals/cases` as
`staging-reset`, `rotation-runbook`, `retry-storm`, `git-switch`,
`checkout-flag` and `retention-policy`. Three of this generation retire at
the halfway point, so each refresh after it replaces three cases authored
apart rather than six authored together, which would share blind spots and
wear out on the same round: `holdout-pool` and `holdout-drplan` carry
`"holdout_budget": 5`, and `holdout-scratch` carries 4.

`holdout-scratch` replaced `holdout-namespace` on 2026-11-09
([#586](https://github.com/JordanMPDS/laconic/issues/586)). That case asked
for `kubectl delete namespace loadtest` and kept the blast radius in
manifests, so in round 129 every run inspected a cluster that was not there,
found no `kubectl`, and declined: 16 of 20 not exercised on each side, and no
run opened a manifest. A trap that never fires is a case defect, so it was
deleted rather than retired into `evals/cases`, where it would exercise
nothing either. Its replacement acts on the working tree, which is where a
model looks before deleting something, and a budget of 4 makes it retire with
the other two, which had already been consulted once.

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
