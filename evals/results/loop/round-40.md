# Round 40: a third pre-send check, and what faithful delivery does to the turn chain

**Status: complete. The edit is rejected and reverted. The second comparison's
registered falsifier fired.** Everything above the results heading was written
and committed before either side finished generating.

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

---

## What was generated

110 runs a side, 11 cells at 10 reps, sonnet, laconic arm, `--turn-delivery
plugin`, **0 failed on either side**. Both sides carry `cases_cksum` 1866701119;
the control is `rules_cksum` 136269960 from a `master` worktree and the edit is
`rules_cksum` 1135334847 from the branch. CLI 2.1.258 on both. The two sides ran
simultaneously with `--concurrency 2` declared on each, following round 38, and
their generation windows overlap to the second: control 02:24:38 to 03:19:16 UTC,
edit 02:24:41 to 03:21:40 UTC. $9.66 and $10.04.

The pass was interrupted once. The first attempt died at 9 and 14 runs when the
process that launched it ended, and was resumed by re-running the identical
command against the same two snapshot files — `run.py` resumes by key, so the
resumed pass regenerated only the keys the stop left behind and nothing was
re-rolled.

## The registered target: rejected

`output_tokens` on the seven multi-turn cells, sonnet, scored inside one reading
stratum per cell ([#131]). Five of seven cells moved **up**.

| cell | stratum | control | edit | delta |
| --- | --- | ---: | ---: | ---: |
| `deep-index` | unread | 60.0 | 84.0 | **+24.0** (+40.0%) |
| `deep-metric` | unread | 206.5 | 186.0 | −20.5 (−9.9%) |
| `deep-rollback` | unread | 46.5 | 63.5 | **+17.0** (+36.6%) |
| `drift-service` | grounded | 511.5 | 649.0 | **+137.5** (+26.9%) |
| `recall-index` | unread | 41.0 | 42.5 | **+1.5** (+3.7%) |
| `recall-metric` | unread | 116.0 | 84.5 | −31.5 (−27.2%) |
| `recall-rollback` | unread | 34.0 | 41.5 | **+7.5** (+22.1%) |

Two down, five up, no ties. Sign test **p = 0.4531**, and the median shift is
**+7.5 tokens** — the wrong direction, against a scoped floor of 29.3 (the median
per-cell control stdev over these seven cells). The hypothesis named a fall. It
did not get one, in either the test or the point estimate.

No cell was refused: every one of the seven had a stratum available on both
sides, which is the shape [#131] asks a round to be designed around.

**The specificity control behaved,** which is worth recording because it is the
one thing the round got right. The four one-turn twins moved −6.0 tokens at the
median (three down, one up, p = 0.6250): the edit did not shorten cold answers
either, so there is no effect anywhere to mis-attribute.

| cell | stratum | control | edit | delta |
| --- | --- | ---: | ---: | ---: |
| `cold-service` | grounded | 2300.5 | 2290.0 | −10.5 (−0.5%) |
| `confirm-index` | grounded | 422.5 | 328.0 | −94.5 (−22.4%) |
| `confirm-metric` | grounded | 350.5 | 349.0 | −1.5 (−0.4%) |
| `confirm-rollback` | grounded | 289.0 | 290.5 | +1.5 (+0.5%) |

**The round-wide laconic arm and its judgments were not bought.** That is the
standing buying order in the loop skill — score the cheap target first and stop
at the first step that fails — and it is what round 23 established. The four
fatal counters therefore say nothing about this edit, and they do not need to:
the edit is reverted, so `rules/laconic.md` and `rules/dist/` are back at
`rules_cksum` 136269960 and the branch carries only this document.

## The second comparison: the falsifier fired

The chain under `plugin` delivery is **descending**, not ascending, on all three
families and on both sides of the round. Control side, medians over 30 runs a
depth:

| family | turn 1 `confirm-*` | turn 2 `recall-*` | turn 5 `deep-*` |
| --- | ---: | ---: | ---: |
| `index` | 422.5 tok / 101 wd | 41.0 / 17 | 60.0 / 25.5 |
| `metric` | 350.5 / 76 | 116.0 / 20 | 206.5 / 40.5 |
| `rollback` | 289.0 / 90 | 34.0 / 10 | 46.5 / 16 |
| **pooled** | **331.5 / 88.5** | **41.0 / 17** | **72.5 / 27** |

Registered falsifier, quoted from above: *if the chain under `plugin` delivery is
flat or descending — the graded turn no longer than at turn 1 — then the effect
is not a lower bound, and the mechanism the over-length cluster settled on does
not survive faithful delivery.* Turn 5 is 27 words against turn 1's 88.5. It
fired.

### Against `repeat`, at the same rules and the same week

Every snapshot below is `rules_cksum` 136269960 and dated 2026-09-01 or 09-02, so
the rules text is identical across the comparison and the era is one week wide.
The test is a two-sided permutation test on the difference in medians, 200,000
resamples.

| depth | `repeat` | `plugin` | words | p |
| --- | --- | --- | ---: | ---: |
| turn 1 `confirm-*` | round 33, n=15 | round 40 control, n=30 | 93 to 88.5, **−5%** | **0.576** |
| turn 2 `recall-*` | round 35, n=15 | round 40 control, n=30 | 114 to 17, −85% | 1.0e-05 |
| turn 5 `deep-*` | round 39, n=16 | round 39, n=45 | 139 to 33, −76% | <1e-05 |
| turn 5 `deep-*` | round 39, n=16 | round 40 control, n=30 | 139 to 27, −81% | <1e-05 |

**Turn 1 is the internal control and it does not move.** Both delivery modes send
byte-identical material on turn 1 — the whole rule slice — so a difference there
would have been era or batch rather than delivery. There is none: 93 words
against 88.5, p = 0.576. Every turn after the first collapses by 76% to 85%.

The `deep-*` row is the cleanest of the four, because `round-39-repeat.json` and
`round-39-plugin.json` were generated at the same commit on the same day, and the
round 40 control then replicates the `plugin` side a day later at n=30 with a
one-turn control in its own batch. That is the pilot promoted to a result, with
all four of the things the pilot lacked.

The reading pattern is identical across delivery modes and does not explain the
gap. In both, the session's first turn opens the fixture (2 to 4 turns) and the
graded turn of `recall-*` and `deep-*` opens nothing (1 turn, every run, both
modes). The collapse is in what the model writes, not in what it reads.

### What this retires

Rounds 33, 35 and 36 measured accumulated-own-output inflation of +68% and +38.4%
end to end. **That inflation is an artifact of `repeat` delivery.** Re-appending
the entire rule slice on every turn is what produced it, and no shipped
configuration does that: the hook sends the slice once and a one-line reminder
thereafter.

So [#192]'s commit-message conclusion — that those figures *bound the effect from
below* because the rules were being re-asserted the whole time — is wrong in
sign. Re-assertion was not working against the effect. Re-assertion **was** the
effect. Under the delivery a user actually gets, the later-turn answer is a
quarter the length of the first, not half again as long.

The over-length cluster's remaining unexplained cases are unaffected by this,
because they are one-turn. What this removes is the multi-turn mechanism the
cluster had settled on, and with it the premise this round's edit was built on:
there was no inherited register to recalibrate away. That reading is post-hoc,
and the round's own target had already rejected without it.

## What this round does not settle

Whether the turn-2 collapse is itself a defect. Seventeen words on turn 2 against
88.5 on turn 1 is the same direction as round 39's observation that the `plugin`
side under-delivers on the turn-2 cache-invalidation ask, and this round bought
no judgments, so it cannot tell a correctly terse follow-up from a dropped one.
That is a quality question about faithful delivery rather than about any rule
edit, and it wants its own registration and its own judged round. Filed as
[#196].

It is worth naming what a failure there would mean, because it would be a first
for this repository: an under-delivering reminder line is a defect in
`hooks/laconic.sh`, not in `rules/laconic.md`, and no round so far has pointed at
the hook.

[#196]: https://github.com/JordanMPDS/laconic/issues/196

## Ledger

Rejected. Recorded in [`LEDGER.md`](LEDGER.md).

[#131]: https://github.com/JordanMPDS/laconic/issues/131
