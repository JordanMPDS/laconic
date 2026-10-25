# Round 121: a wrong-premise closed question gets the correction, not a bare "No" (#353)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds and the benchmark, which are merged.
This file is committed before any generation. The edit and the regenerated
`rules/dist/*.md` are the next commit, also before generation. No harness,
scorer or case changes.

`bash tools/candidate-due.sh` exited 0 at registration: round 120 tested a
candidate, so round 121 **may** measure. It carries an edit anyway, under
**The edit** below, because [#353] is a concentrated, user-graded quality
failure and quality outranks every open length finding. The edit sits behind
a fire-rate precheck (**Stage 1**) that can withdraw it unrun. If it
withdraws, the round is recorded as measuring; because round 120 was a
candidate, one measuring round here is within the cap and round 122 then owes
a candidate. `bash tools/release-due.sh` exited 0: v0.3.10 is tagged and
current.

Decided on **sonnet**, the model [#353] was observed on — not opus. See
*Why sonnet, not opus* below.

## Why this round exists

[#353] is the sharpest block of the 2026-09-24 benchmark's sonnet quality gap
(laconic 80.6% against baseline 90.3%). One shape carries it: **a closed
question with a wrong premise, answered with a bare "No" and its reason, and
without what works instead.**

| case / sonnet | baseline pass | laconic pass | what the laconic failures drop |
|---|--:|--:|---|
| `recall-index` | 5/5 | 1/5 | "so the fix is adding the index on created_at, correct?" answered "No, date_trunc…" with neither working fix |
| `wide-index` | 5/5 | 3/5 | the same |
| `deep-index` | 5/5 | 4/5 | the same |
| `recall-metric` | 5/5 | 4/5 | a bare "Yes" that never says the proposed replacement metric does not fix the readout either |

The fixture supplies two working fixes (an index on the `date_trunc`
expression, or a half-open range rewrite so the bare-column index serves the
query). A passing answer denies the proposed index, gives the reason, and
names one of them. The laconic failures give the reason and drop the fix.

### Why the rules produce it

Two passages point the same way and nothing points back — the issue's own
diagnosis, verified against the current text:

- **Check 1:** *"Diagnosing it is the answer; fixing it is not … leave the fix
  for the user to ask for."* The user did ask about the fix; it is phrased as a
  confirmation.
- **The closed-question specimen:** *"The one word is the whole answer, not the
  opening of one."* That paragraph is written about a closed question with
  **nothing wrong in it**. It never says what a closed question with a **wrong
  premise** gets. The named-options variant beside it already says *"If neither
  holds, say so and name what does"* — the right instinct, attached to the
  wrong shape.

The failure is a **composition** of the two: the model reads "the one word is
the whole answer" off the specimen and "fixing is not the answer" off check 1,
and the two compose into "No — reason." (This reading of the mechanism is
Kimi's, via `tools/consult.sh`; it is why the edit amends the specimen rather
than check 1 — see *The edit*.)

### Why sonnet, not opus

[#353] is a sonnet finding. Rounds 112 and 113 both attacked it and both
sidestepped the actual cells:

- **Round 112** chose `recall-index`/**opus** by its "opus first" tiebreak. On
  opus the cell behaves differently — it gives *the fix and drops the reason*,
  the opposite shape, and the panel passes it — so its stage 1b precheck did
  not fire and the edit was withdrawn. Its own inventory read the opus index
  family largely recovered (`recall-index`/opus 2/5 omitting `date_trunc`,
  `wide-index`/opus 1/5).
- **Round 113** tried the `rollback` family, a different instrument for the
  same wrong-premise shape; no cell qualified and the edit was withdrawn.

So the registered sonnet index finding has **never** been tested as a
candidate under current rules. The closed-question specimen is unchanged since
round 73 (`dae4696`), which predates the v0.3.3 benchmark rules that found the
gap, so there is no reason the sonnet gap would have closed — but era and CLI
drift since 2026-09-24 are real (one smoke run at master on CLI 2.1.310 passed),
which is why this round prechecks the fire rate before buying the full round.

## The instrument

Existing cases, no new fixtures. The final turn of each is the wrong-premise
confirmation *"so the fix is adding the index on created_at, correct?"*:

- **Primary** (sonnet): `recall-index` (2 turns), `wide-index` (2 turns, the
  expanded fixture), `deep-index` (5 turns, the depth twin).
- **Guards — panel quality may not fall** (sonnet): the adjacent confirmation
  cases the edit could over-fire on — `recall-metric`, `wide-metric`,
  `deep-metric` (the "Yes but incomplete" shape, where "name what holds" must
  **not** become presenting the bad replacement as the fix), and `quota-merge`
  (a correct confirmation that must still carry its load-bearing addition).
  `confirm-index` (single-turn) is carried as a positive control: the edit
  should help or hold it.
- **Disclosure** (opus): `recall-index`, `wide-index`, `deep-index`, so the
  round records what the edit does to the model it does not decide on. A fall
  on opus is welcome; a rise is disclosed and, if a panel-quality cell falls on
  opus, fatal.

Every graded turn is judged by the sonnet/opus/kimi panel. `never_cut` on the
index cases is `["date_trunc"]`; the edit adds the fix and must not drop the
reason, so the never-cut screen stays live.

A fixture grep (Kimi's caveat) confirmed **no case in the suite rewards a
deny-only answer against a user-proposed fix**: every confirmation case
(`index`, `metric`, `rollback`, `quota-merge`) already rewards deny/confirm
*plus* the load-bearing fact, so the edit introduces no new failure class and
reinforces the pattern the named-options variant already blesses.

## The edit

One paragraph added to the closed-question specimen, after the named-options
variant, reusing the OOM/leak example the specimen already opens with so it
teaches to no benchmark case:

```diff
 A question that names its options is closed the same way: *"Was the worker
 killed by its own memory limit, or by the node running out?"* — "Its own
 memory limit." Naming the option that holds is the whole answer, and the
 evidence for it is left out unless the user asked why. If neither holds, say
 so and name what does.
+
+A closed question can propose something that does not hold — a wrong fix, or a
+cause that is not the one — and then "No" is not the whole answer; the
+correction is. *"So the fix is bumping the memory limit, correct?"* when the
+curve is climbing: "No," the reason, and what does work — it is a leak, so a
+bigger limit only delays the next kill. The user proposed it and asked whether
+it holds, so naming what does is answering the question, not volunteering an
+unasked fix. If neither the proposal nor anything else holds, say that.
```

The guard sentence covers both the wrong-*fix* and wrong-*cause* branches, and
the closing sentence covers the case where nothing holds (the `recall-metric`
shape, where switching estimators does not fix the readout either). Both the
both-branches wording and the fixture-grep check came from Kimi via
`tools/consult.sh`; Codex and DeepSeek timed out.

**Hypothesis.** Adding the wrong-premise case to the closed-question specimen
should move `quality_fails` on `recall-index,wide-index,deep-index`/sonnet
**down** (fewer failures), without lowering the panel pass rate on the metric
guards, `quota-merge`, or the opus index cells, and without a round-wide rise
in any fatal counter.

**Pre-mortem.** The likeliest failure is the point estimate moving **with** the
registered direction and not separating: the gap is probabilistic (benchmark
pooled ~47% fail, and a master smoke run passed), so a 10-rep-a-side read could
land short of alpha and need the extension to 20. The second risk is a fatal
rejection whose target passed: the edit's "name what does work" over-fires on a
metric guard, where the correct answer must *deny* that the replacement
estimator fixes the readout — so an edit answer that confidently presents the
absolute-difference metric as the fix would fail `recall-metric` while the
index target improved. I do not expect the point estimate to move *against* its
direction; the edit only adds a licence that the fixture already rewards.

## Stage 1: precheck — does the gap still fire on sonnet? (~30 generation calls + judging)

From master rules (this branch before the edit commit):

```sh
OUT=$PWD/evals/snapshots/loop
python3 evals/bench/run.py --arms laconic --turn-delivery plugin --concurrency 3 \
  --reps 10 --cells 'recall-index:sonnet,wide-index:sonnet,deep-index:sonnet' \
  --snapshot $OUT/round-121-precheck.json
python3 evals/bench/judge.py --results $OUT/round-121-precheck.json --jobs 6 \
  --out $OUT/round-121-precheck-judgments.json
```

**Fires when the pooled panel `quality_fails` on the three cells is at least
9 of 30 (30%), with `recall-index` contributing at least 3 of 10.** The
benchmark read ~47% pooled and `recall-index` 4/5. Below the bar, the gap has
narrowed since 2026-09-24, the edit is withdrawn unrun, this heading is renamed
and the preamble gains **This round proposes no rule edit.**, and round 122
owes a candidate. The precheck measures master only and cannot test the edit.

## Stage 2: confirm, only if Stage 1 fires (~280 generation calls + judging)

Two trees simultaneously — control from a worktree at the registration commit
(master rules), edit from this branch with the edit committed and `rules/dist/`
regenerated. Laconic, `--turn-delivery plugin`, two shards a side:

- Primary: `recall-index`, `wide-index`, `deep-index` / sonnet at 20 reps (60).
- Guards: `recall-metric`, `wide-metric`, `deep-metric`, `quota-merge`,
  `confirm-index` / sonnet at 10 reps (50).
- Disclosure: `recall-index`, `wide-index`, `deep-index` / opus at 10 reps (30).

140 runs a side. Judged by the panel, then:

```sh
python3 evals/bench/report.py \
  --results   $OUT/round-121-edit.json    --judgments   $OUT/round-121-edit-judgments.json \
  --against   $OUT/round-121-control.json --against-judgments $OUT/round-121-control-judgments.json \
  --target quality_fails \
  --target-cases recall-index,wide-index,deep-index --target-models sonnet --looks 1
```

**One look, declared.** Stage 2 opens at 20 reps a side; it does not stage to a
second scoring. If Stage 1 fires weakly (near the 30% bar) the primary is still
bought at 20, because 20 is what #259/#54 says a quality counter needs to catch
a single cell.

**Accept requires:** the primary `quality_fails` falls past the one-sided gate;
**and** no fatal counter rises round-wide (never-cut, quality, safety,
readability), which includes the metric guards, `quota-merge` and the opus
index cells; **and** the replication (Stage 3) and holdout (Stage 4) hold.
A quality verdict lost on any guard rejects on its own, whatever the primary
did.

## Stage 3: replicate

Fresh generation of the three primary sonnet cells at 20 reps a side, into
`round-121-rep{,-control}.json`, judged; the fall must survive it.

## Stage 4: holdout

```sh
python3 evals/bench/run.py --arms laconic --cases-dir evals/holdout \
  --turn-delivery plugin --snapshot $OUT/round-121-holdout.json
python3 evals/bench/judge.py --cases-dir evals/holdout \
  --results $OUT/round-121-holdout.json --out $OUT/round-121-holdout-judgments.json
```

A regression here is fatal whatever the dev set says. Holdout numbers never
enter a published table.

[#353]: https://github.com/JordanMPDS/laconic/issues/353

<!-- RESULTS BELOW THIS LINE -->
