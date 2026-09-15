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

**accept — the registered primary fired and both bounds held.** The shipped
pre-action check cuts `conditional`'s sonnet edit rate from **30.0% to 5.8%**,
a fall of 24.2 points, Fisher two-sided **p = 1.1e-06**. No rule edit was
proposed, so nothing ships from this round; what it buys is that [#116]'s
reported harm is measured, prospectively, against the rule already in the
product.

240 generations, 0 failed, 0 judgments. Both sides on CLI 2.1.272 with no
release boundary to stratify on.

## The primary

| | `nocheck` (136269960) | `check` (594915793, master) |
|---|--:|--:|
| `edited` | **36/120 (30.0%)** | **7/120 (5.8%)** |

Fisher exact, two-sided, **p = 1.1e-06**. Reduction **24.2 points**, Newcombe
95% CI **[14.8, 33.4]**. The round was bought for 0.82 power against a
pessimistic 15% control; the control came in at 30.0%, so it was heavily
overpowered, which is the direction a round should err in on a counter whose
base rate had halved in ten days.

## Both bounds held, and neither cheap win was taken

| bound | `nocheck` | `check` | p |
|---|--:|--:|--:|
| `locates_defect` given the answer did not edit | 84/84 (100%) | 113/113 (100%) | 1.0000 |
| read the fixture | 120/120 (100%) | 120/120 (100%) | 1.0000 |

**Not one answer stopped opening `db.js`** and **not one non-editing answer
failed to say what was wrong.** Those are the two ways this target can be won
without improving anything — suppress the reading, or suppress the explanation
along with the edit — and both are closed at the ceiling on both sides.

## The check removed the work; it did not displace it

The full tool inventory, all 240 responses:

| | `nocheck` | `check` |
|---|--:|--:|
| `Read` calls | 230 | 222 |
| `Bash` calls | 127 | 128 |
| `Edit` calls | **36** | **7** |
| tool-count distribution | 2:1, 3:88, 4:28, 5:3 | 2:12, 3:99, 4:9 |
| median tool calls | 3 | 3 |

`Read` and `Bash` are within eight and one call of each other across 120 runs a
side. **The only tool that moved is `Edit`**, and the tool-count distribution
moves with it: the `nocheck` side's 31 responses at four or five calls become
nine. So the check did not buy its number by trading a mutation for extra
reading, and it did not buy it by reading less — it removed the fourth call and
left the first three alone.

## Disclosures, gating nothing

**Prose words** (`metrics.split_text`, permutation on the median at seed 65,
50k draws):

| stratum | `nocheck` | `check` | delta | p |
|---|--:|--:|--:|--:|
| all runs | 73.0 | 59.5 | −13.5 | 0.00014 |
| did not edit | **84.0** | **61.0** | −23.0 | 0.00002 |
| edited | 20.5 | 20.0 | −0.5 | 0.9932 |

**[Round 51](round-51.md)'s stratified compression replicates almost exactly.**
It registered the answering stratum and read 83.0 to 62.0; seven days and one
`rules_cksum` later this round reads 84.0 to 61.0 on a control it generated
itself. The editing stratum does not move at all, which is [#209] stated as a
measurement rather than a caution: an editing answer runs 20 median words on
both sides because the work product *is* the answer, so the marginal median
tracks the mixture and only the stratified number is about compression.

**`locates_defect` pooled** — a floor, not a rate, since editing-stratum recall
is 73% against 100%:

| | `nocheck` | `check` |
|---|--:|--:|
| all runs | 98/120 (81.7%) | **118/120 (98.3%)** |
| within the editing stratum | 14/36 | 5/7 |

The 16.6-point rise is the stratum mix and not a separate effect: the check
moves responses out of the stratum that fails this counter, and inside each
stratum the rates are what the archive already said they were.

## The archive figure reproduced, and the drift did not continue

The round was designed around the possibility that it would not. `edited` on
this cell had fallen from 47.5% to 20.0% over eleven days at byte-identical
rules, which is why the sizing went below the archive's floor. It did not fall
further:

| | this round | rounds 52 + 55 | Fisher p |
|---|--:|--:|--:|
| control (136269960) | 36/120 (30.0%) | 57/240 (23.8%) | 0.2045 |
| treatment (594915793) | 7/120 (5.8%) | 9/240 (3.8%) | 0.4185 |

Neither arm is distinguishable from its archived counterpart, and the control
is also indistinguishable from all 876 archived runs at that `rules_cksum`
(232/876 = 26.5%, p = 0.4425). **Pooled across all three rounds the check reads
16/360 (4.4%) against 93/360 (25.8%), p = 1.6e-12** — quoted as a summary of
three independently timed interleaved batches, not as this round's result,
which is the line above it.

## What [#116] gets, and what it does not

**Its reported harm is answered on the instrument built for it.** The issue
asked for a rule that governs volunteered *work* rather than volunteered prose.
One shipped in [round 55](round-55.md) — accepted there on compression, because
that is what round 55 registered — and it turns out to cut the behaviour the
issue actually reports by a factor of five, with reading and diagnosis
untouched. That was true when 0.3.0 shipped on 2026-09-14 and nobody could say
so.

**Its proposal 2 is now a bad candidate rather than an untried one.** The issue
also asks for an explicit *"Do not volunteer work"* prohibition under **Never do
this**. At a treatment rate of 5.8% there is almost nothing left to remove:
halving it needs about 1,100 runs a side for 0.75 power and 1,500 for 0.86,
against a round-65 cost of 240. That is the registration's stated condition,
and it resolved in the direction that closes the proposal rather than the one
that promotes it.

**Three things this round does not establish:**

- **It is one cell**, and the claim is about the `conditional` scenario rather
  than a general property of advisory questions. `conditional` is the only case
  of 37 that elicits the behaviour, and three purpose-built alternatives were
  authored and withdrawn ([`volunteered-work-cases.md`](volunteered-work-cases.md)),
  so the scope is a constraint rather than a choice. The interleaved control
  protects against drift; nothing here protects against the cell.
- **It says nothing about the register #116 reports from.** The issue's failure
  came deep in a session, after work the model had been doing; these are cold
  single-turn fixtures. That is the same wall [round 32](round-32.md) hit for
  [#136] and it is unmoved.
- **The editing-side detector figures are floors.** `locates_defect` recalls 73%
  on the editing stratum against 100% on the answering one, so 14/36 and 5/7 are
  lower bounds. The primary and both bounds are unaffected: `edited` is a tool
  list, and the bound is scored inside the stratum where recall is 100%.

## Audits

- **Release** — `evals/bench/release.py` on both snapshots: 120 runs each, both
  per-run stamped, both entirely on 2.1.272. No unreadable span and no arm
  imbalanced across a release.
- **Concurrency** — each snapshot reconstructs to 1 invocation in flight against
  2 declared, so the declaration is conservative. `evals/bench/concurrency.py`
  flags the same 19 pre-existing arm-days it flags on master and neither of
  this round's.
- **Trees** — `rules_cksum` 594915793 and 136269960 as registered, the second
  verified against the control arm of rounds 50, 51, 52 and 55 rather than
  assumed. `cases_cksum` identical on both sides. `rules/laconic.md` on this
  branch is byte-identical to master.

## Cost

240 generations, 0 judgments, 0 failed calls. Roughly 21 and 23 minutes of wall
clock, run simultaneously.
