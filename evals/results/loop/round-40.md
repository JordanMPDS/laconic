# Round 40: a third pre-send check, and what faithful delivery does to the turn chain

**Status: registered, round in flight.** This section was written and committed
before either side finished generating. The results follow below it.

## The edit

`rules/laconic.md`, the pre-send checks:

```diff
-Two checks before sending:
+Three checks before sending:

 1. What is the smallest set of claims that fully answers this?
 2. Is anything here something the user did not ask for?
+3. Would this be the same answer if this were the session's first turn?
+   Earlier turns set the subject, never the length.
```

Structural rather than another sentence bounding a licence, which
[`over-length-cluster.md`](over-length-cluster.md) records as having failed four
times. It adds a step to the checklist the model runs rather than qualifying the
paragraph below it.

## The registered hypothesis

> Editing the pre-send checks to add a third check that recalibrates the answer
> against the current turn alone should reduce `output_tokens` on the multi-turn
> sonnet cells `drift-service`, `deep-metric`, `deep-index`, `deep-rollback`,
> `recall-metric`, `recall-index`, `recall-rollback`.

Seven cells, all of them cases whose graded answer carries at least one prior
answer of the model's own. The one-turn twins — `cold-service`,
`confirm-metric`, `confirm-index`, `confirm-rollback` — run in the same batch as
a **specificity control** and are deliberately outside the target scope: the
edit is supposed to remove an inherited register, not shorten a cold answer.

10 reps a side, sonnet, laconic arm only, two trees generated simultaneously
(edit from the branch, control from a `master` worktree), `--concurrency 2`
declared on both, following round 38.

## Delivery: `plugin`, not `repeat`

`run.py`'s own docstring settles this, and it was written for this issue:

> a persistence clause of the kind [#60] asks for cannot be tested under
> `repeat` at all, because `repeat` already over-delivers persistence.

So both sides run `--turn-delivery plugin`: the rule slice once on turn 1, then
only the one-line reminder, which is what the shipped hook wiring sends.

## The second comparison, registered before the numbers

The control side alone answers a question no round has asked, and it answers it
without any cross-batch comparison, because `confirm-*` asks the question at
turn 1, `recall-*` at turn 2 and `deep-*` at turn 5 while sharing a fixture, a
final question and a trap.

> Does the accumulated-own-output inflation that rounds 33, 35 and 36 measured
> under `repeat` delivery survive `plugin` delivery?

Round 35 read that chain as `confirm-*` 93 words, `recall-*` 127 and 114,
`deep-*` 156 — **+68% end to end** — and round 36 replicated it on a different
fixture at +38.4%. [#192]'s commit message concluded from this that the effect
is **a lower bound rather than an estimate**, on the reasoning that those rounds
measured it while the whole rule set was being re-asserted every turn and a real
session re-asserts one sentence.

**The falsifier, registered here:** if the chain under `plugin` delivery is flat
or descending — the graded turn no longer than at turn 1 — then the effect is
not a lower bound, and the mechanism the over-length cluster settled on does not
survive faithful delivery.

A pilot exists and points that way. `round-39-plugin.json` and
`round-39-repeat.json` were generated on 2026-09-01 at the same commit and the
same `rules_cksum`, at ragged and unequal reps (15 a case against 8) and with no
write-up, and their per-turn medians on `deep-metric` read 137/274/295/239/157
under `repeat` against 182/30/84/17/35 under `plugin`. That is a pilot, not a
result: unequal n, three cases, one arm, no one-turn control in the same batch.
This round's control side supplies all four of those.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#192]: https://github.com/JordanMPDS/laconic/pull/192
