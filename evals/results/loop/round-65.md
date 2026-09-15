# Round 65: the shipped check already suppresses the work, and nobody scored it

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are the reason this round takes the
shape it does. This file is committed before any generation, following
[round 38](round-38.md) through [round 64](round-64.md).

**This round proposes no rule edit.** `bash tools/candidate-due.sh` exits 0:
[round 64](round-64.md) carried a candidate and rejected it, so the cap merged
as #292 allows round 65 to measure. Round 66 will have to carry one.

## Why this round exists

[#116](https://github.com/JordanMPDS/laconic/issues/116) is one of the two
user-visible failure reports this loop treats as its strongest leads. It reports
a question answered correctly and tersely and then *substantiated with work
nobody asked for*:

> The prose was terse. The behavior was not. Laconic caught neither, because it
> was never pointed at this.

The issue has an instrument — [`volunteered-trap-116.md`](volunteered-trap-116.md),
merged 2026-09-05 — and a registered endpoint, from
[round 50](round-50.md): **the edit rate on `conditional`, sonnet, against the
round's own interleaved control.** Round 50 scored it and read a null.

What has not happened is anyone scoring that endpoint on the rounds that came
after. Rounds 51, 52 and 55 carried the same edit forward and registered a
*compression* endpoint instead, and round 55's version of the sentence was
accepted and shipped. So the counter #116 exists for has been sitting in four
committed snapshot pairs, unread.

## The archive figure this round is built on, and why it is not the result

**Computed 2026-09-15 from committed snapshots, no generation calls.** Each row
is one round's own interleaved two-tree batch, `conditional`, sonnet, the
`laconic` arm on both sides, scored with `evals/pilot/score_volunteered.py`:

| round | control rules | control `edited` | treatment rules | treatment `edited` | Fisher p |
|---|---|--:|---|--:|--:|
| [50](round-50.md) | 136269960 | 26/120 (21.7%) | 3623489520 | 19/120 (15.8%) | 0.3211 |
| [51](round-51.md) | 136269960 | 12/40 (30.0%) | 3623489520 | 7/40 (17.5%) | 0.2933 |
| [52](round-52.md) | 136269960 | 37/160 (23.1%) | **594915793** | **6/160 (3.8%)** | 3.0e-07 |
| [55](round-55.md) | 136269960 | 20/80 (25.0%) | **594915793** | **3/80 (3.8%)** | 0.00018 |

The split is not between rounds, it is between the two *sentences*. Rounds 50
and 51 tested the check whose trigger reads *"Does answering this require
changing anything?"* (`rules_cksum` 3623489520) and it moved the counter
26/160 against 38/160, which is nothing. Rounds 52 and 55 tested the trigger
that shipped — *"Is the question about something that is broken? Diagnosing it
is the answer; fixing it is not"* (594915793) — and it reads **9/240 (3.8%)
against 57/240 (23.8%)**, Fisher p = 7.6e-11, a factor of six, in two
independently timed interleaved replications. The pair that did not ship reads
26/160 (16.3%) against 38/160 (23.8%), p = 0.124.

**This is the hypothesis's origin and explicitly not its evidence.** Round 50
registered this endpoint in advance and rounds 51, 52 and 55 did not; applying
a previously registered endpoint to later replications of the same edit is
better than fishing and it is still not a pre-registration. The whole point of
this round is to buy the number prospectively. Nothing in the table above is
cited as a result below the results line.

Two further facts about the table are worth stating because they are what makes
it worth confirming rather than dismissing:

- **The detector predates the runs it scores.** `score_volunteered.py` and its
  hand validation (85/85 precision in and out of sample) were merged
  2026-09-05; rounds 52 and 55 generated on 09-06 to 09-08. The criterion could
  not have been tuned to them.
- **The control arm is the same instrument in every row**, `rules_cksum`
  136269960, and this round reconstructs that exact text rather than
  approximating it (below).

## The design

Round 38's simultaneous two-tree batch, which is what makes era and CLI release
cancel between the sides instead of confounding them.

| arm | tree | `rules_cksum` | words |
|---|---|--:|--:|
| `check` | master, unmodified | 594915793 | 1041 |
| `nocheck` | master with the pre-action check deleted and nothing else | 136269960 | 1000 |

The `nocheck` tree is master's `rules/laconic.md` with exactly this reverted,
which is the whole diff between the two trees:

```diff
-One check before acting, and two before sending:
+Two checks before sending:

-1. Is the question about something that is broken? Diagnosing it is the
-   answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
-2. What is the smallest set of claims that fully answers this?
-3. Is anything here something the user did not ask for?
+1. What is the smallest set of claims that fully answers this?
+2. Is anything here something the user did not ask for?
```

**That the result is `rules_cksum` 136269960 is verified, not assumed** — the
same value the control arm of rounds 50, 51, 52 and 55 carries, so this round's
control side is byte-identical to theirs while its `evals/cases/` tree is
today's. A worktree checked out at the round-54 commit would have given the
same rules and an older case suite, which is a second difference nobody wants.

The `nocheck` tree is a diagnostic tree and never a merge candidate, the way
round 57's arm C was. `rules/laconic.md` on this branch is byte-identical to
master and no rule edit is proposed, so there is nothing to revert at the end.

**Scope: `conditional`, sonnet, 120 reps a side. 240 generations, no
judgments.** Every endpoint and every bound below is deterministic, so the
round buys no judge calls at all. Single-turn, so `--turn-delivery` does not
apply. Both sides declare `--concurrency 2`.

## What is registered

**Primary, and the decision endpoint: `edited`** — whether the response
invoked any of `Edit`, `Write`, `MultiEdit` or `NotebookEdit`, read off the
`tools` list [#142] records. Fisher exact, two-sided, alpha 0.05. The predicted
direction is down: the arm carrying the check edits less.

**Two bounds, each fatal on its own**, both of them round 50's, registered
unchanged:

1. **An answer that did not edit must still name the defect.**
   `locates_defect` within the non-editing stratum. Suppressing the edit is
   only an improvement if the reader is still told what is wrong, and the
   archive reads 215/215 on this cell, so any occurrence is new behaviour and
   needs no noise floor.
2. **The reading rate must not fall.** A check that bought its number by
   stopping the model opening `db.js` has won nothing — that is the [#131]
   stratum-crossing failure and the [#46]/[#138] one at the same time.

**Falsifier, registered in advance:** the primary failing to separate at
p < 0.05, or either bound falling at p < 0.05. A null here says the effect the
archive shows does not reproduce prospectively at this date, and that is the
publishable outcome — the archive table above would then be read as an artefact
of its window, exactly as round 63 read round 56's.

**Disclosures, gating nothing:**

- Median prose words, reported overall and separately inside the non-editing
  stratum. [#209] is the reason both are needed: on this case an answer that
  edits `db.js` runs 45 median words against 144 for one that does not, so an
  overall median tracks the edit rate rather than the compression, and this
  round is about to move the edit rate hard. Round 51 registered the stratified
  number and read 83.0 to 62.0; whether that reproduces is a reading, not a
  gate.
- The tool-call count distribution on both sides, which is what says whether
  the check removed the work or displaced it into more reading.
- `locates_defect` pooled over all runs, which moves with the stratum mix and
  is a floor rather than a rate (editing-stratum recall is 73% against 100%).

## Power, sized against the archive's lowest control

[Round 46](round-46.md)'s rule, restated by round 50 after it cost round 50 the
round: size against the archive's **lowest** control, not its pooled one,
because a registered baseline fixes the number a hypothesis is scored against
and cannot fix a power calculation, which precedes the control.

`conditional`/sonnet `edited` at `rules_cksum` 136269960, by snapshot, every
batch of 20 runs or more (computed 2026-09-15):

| date | snapshot | `edited` |
|---|---|--:|
| 2026-08-28 | `round-30-nevercut-control.json` | 19/40 (47.5%) |
| 2026-08-31 | `round-31-control.json` | 16/40 (40.0%) |
| 2026-09-03 | `volunteered-work-conditional.json` | 14/40 (35.0%) |
| 2026-09-05 | `conditional-homology-master.json` | **8/40 (20.0%)** |
| 2026-09-06 | `round-50-control.json` | 26/120 (21.7%) |
| 2026-09-06 | `round-51-control-conditional.json` | 12/40 (30.0%) |
| 2026-09-06 | `round-52-control-conditional.json` | 17/75 (22.7%) |
| 2026-09-07 | `round-52-control-conditional.json` | 20/85 (23.5%) |
| 2026-09-08 | `round-55-control-conditional.json` | 20/80 (25.0%) |

Pooled 26.5%, lowest 20.0%, and **the series is falling at byte-identical
rules** — the drift [round 37](round-37.md) measured on a different counter and
[round 50](round-50.md) was caught by on this one. The last control is seven
days old, so this round assumes it can have fallen further and sizes below the
archive's floor:

| assumed control | n = 40 | n = 60 | n = 80 | n = 100 | n = 120 |
|---|--:|--:|--:|--:|--:|
| 23.8% (archive pooled control of rounds 52 and 55) | 0.68 | 0.88 | 0.96 | 0.99 | 1.00 |
| 15% (below every control the archive holds) | 0.23 | 0.43 | 0.61 | 0.73 | **0.82** |

Fisher exact, two-sided, alpha 0.05, against a treatment rate of 3.8%, 4,000
simulations a cell. **120 a side is bought for the pessimistic row**, and if
the control lands anywhere near the archive it is heavily overpowered — which
is the correct way round for a counter whose base rate has halved in ten days.

## What this round deliberately does not do

- **It proposes no rule edit, and #116's untested proposal 2 is the reason.**
  The issue asks for a second thing this loop has never tested: an explicit
  *"Do not volunteer work"* prohibition under **Never do this**. If the archive
  figure reproduces there is no headroom left for it — halving 3.8% needs about
  1,100 runs a side for 0.75 and 1,500 for 0.86 — so testing it is not deferred for cost reasons but
  because the harm it targets would already be gone. If the archive figure does
  *not* reproduce, proposal 2 becomes the next candidate and this round has
  sized it.
- **It scores one cell.** `conditional` is the only case in 37 that elicits the
  behaviour at all; three purpose-built alternatives were authored and withdrawn
  ([`volunteered-work-cases.md`](volunteered-work-cases.md)), so the scope is
  not a choice. The claim is therefore about the `conditional` scenario and not
  a general property of advisory questions, and the round document will say so
  in those words. The interleaved control protects against drift; it does not
  establish transport.
- **It buys no judgments.** `conditional` grades `rule-adherence` and may not be
  optimized against. Neither registered counter reads that criterion — one is a
  tool list and one is a fact only `db.js` supplies — which is the argument
  `volunteered-trap-116.md` makes and this round inherits rather than re-makes.

## Origin of the design

`bash tools/consult.sh` was run before this round was committed to. `deepseek`
and `kimi` were both asked and neither answered inside the timeout, which is
recorded here rather than left as silence.

`codex` answered and three things it said are in the design above:

- **It confirmed the power arithmetic that nearly killed the round** — about
  258 per arm for 16% against 8% at 0.8, and that round 50's 120 a side had
  roughly 0.5 to 0.6 power, so round 50's null "does not meaningfully rule out"
  either proposal.
- **It proposed a higher-prevalence composite endpoint**, `no_volunteered_tool_use
  AND locates_defect`, to escape a rare binary. **Declined, and checking why is
  what found this round.** On `conditional` reading is required to answer at
  all and is a registered bound, so "no tool use" is the wrong target here; the
  archive's whole tool mix across 1,702 sonnet runs is `Read` 3,159, `Bash`
  1,788 and `Edit` 335, with no `Grep` or `Glob` at all, so there is no
  continuous precursor to find. Going to the archive for that prevalence is what
  surfaced the 3.8%.
- **Its closing condition is the one this round is built to satisfy**: do not
  spend 600 generations on an underpowered single-cell binary, and make round
  65 an instrument round unless the archive says the endpoint is affordable.
  The archive says it is affordable, at 240 generations rather than 600,
  because the effect is six times larger than the halving round 50 was sized
  for. Its list of what a one-cell round must carry — a narrow pre-registered
  claim, an interleaved control, a deterministic primary, diagnosis as a
  guardrail, an independent replication — is the registered design, and the
  replication is rounds 52 and 55 already being two.

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#138]: https://github.com/JordanMPDS/laconic/issues/138
[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#209]: https://github.com/JordanMPDS/laconic/issues/209

---

## Results
