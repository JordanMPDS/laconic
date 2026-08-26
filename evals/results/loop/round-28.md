# Round 28

**Status: registered, not yet run.**

*Everything above the horizontal rule below was registered at 04:13 UTC on
2026-08-26, before any generation.*

**Rules under test:** the round 27 edit (the ask earned by reading) against
master, `rules/` at `ffffa39`, unchanged since `823bd78`. Treatment rules text
is byte-identical to round 27's, recovered from `3628cc8`.
**Snapshots:** `evals/snapshots/loop/round-28-edit.json` and
`round-28-control.json`, plus the matching `-judgments.json`.

## Why this round exists

Round 27 tested [#138]'s edit and **rejected**, on a registered `one_turn`
target that missed at p = 0.151. The same round measured the effect the edit
was designed to produce, on a covariate registered in advance as disclosure:
unread hands-back answers fell 19/200 to 9/200, one-sided p = 0.0436, while
hands-back answers that had read first were untouched, 4 to 3.

Round 27's own verdict named the problem and refused to rescue itself from it:

> The gate the loop owns cannot see this effect at the depth the loop buys.
> `one_turn` is a proxy for the harm, and it moved 13 points without reaching
> alpha, while the thing actually predicted moved and did. That is an
> instrument gap, not a null result.
>
> The next move is a metric, not another rule edit.

That metric is now built, and this round is the first one registered against
it.

## Why this is not scoring an edit against a gate repaired to suit it

Round 27 named this hazard explicitly — "[r]e-running this same edit against a
gate built after seeing this round would be scoring an edit with a rule
repaired to suit it — [#133]'s mistake". The objection is real and the answer
is the four-step route [#146] laid out, which is the route [#49] took before
`turns` was allowed to reject anything. All four steps are complete and
published before this registration:

1. **The counter is implemented in `report.py`** as a `COUNT_TARGETS` member,
   computed from `asks_back` crossed with `num_turns == 1`, target-only.
   Merged in [#147] at `16c0000`.
2. **Every stored round is re-scored offline and the null is published** in
   [`unread-asks.md`](unread-asks.md). The screened form rejects 0 of 18 null
   pairs. It fires on round 20's licence, which the loop condemned, and on
   round 26's, which the loop shipped — which is why it stays target-only.
3. **The between-round overdispersion is settled.** Twenty-one rounds in seven
   groups at identical rules text and identical case-scope size read
   chi-square 15.29 on 14 df, phi = 1.09 at p = 0.36, and the exact conditional
   binomial is used rather than a phi = 1.09 normal approximation, because on
   round 27's counts the approximation would turn 0.0845 into 0.0365. The
   reasoning is in `report.py` beside `ONE_TURN_PHI`.
4. **The detector was frozen before it was validated.** `detector_v2.py` was
   committed at `111723b` before the fresh 80-response sample was drawn, so its
   73.7% precision and 87.5% recall are out-of-sample rather than a re-score of
   its own training data. Both labelled batches, their blinding rule and their
   reproducers are committed under `evals/results/loop/unread-asks/` and
   `unread-asks-v2/`.

What remains, and it is registered as a limitation rather than argued away:
**the edit under test was selected because round 27 showed it moving this
metric.** That is replication, not repair — the metric was not built to make
this edit pass, and step 2 establishes it on an archive that includes texts the
loop accepted and texts it rejected. But this round is confirmatory of round
27's disclosure and may not be read as independent of it. **Round 27's data is
not pooled with this round's and is not re-scored to accept anything.** This
round buys its own generations.

## The edit

Byte-identical to round 27's, one line in the `level: full` design-question
licence:

```diff
-  for the depth you left out. Ask for the fork you cannot resolve. Explaining
-  something that already exists is a different request, and it is protected
-  above.
+  for the depth you left out. Ask for the fork that survives reading, not the
+  one reading would settle. Explaining something that already exists is a
+  different request, and it is protected above.
```

Nothing moves section. The clause stays under `level: full`, where round 10
established the licence belongs.

## Hypothesis

> Editing the design-question licence's asking permission — "Ask for the fork
> you cannot resolve" becomes "Ask for the fork that survives reading, not the
> one reading would settle" — should move `unread_asks` **down** on the eight
> `design-*` cases on sonnet, against master rules generated in the same
> interleaved batch, while `one_turn`, `output_tokens` and `turns` do not rise
> and no fatal counter rises.

Registered scoring, the target:

```
--target unread_asks \
  --target-cases design-alerting,design-audit-log,design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --target-models sonnet
```

**Why all eight cases, and not the three-cell `one_turn` scope.**
`unread_asks` is a conditional rate — its denominator is the unread stratum
itself, not the run count — so a case where nobody skips reading contributes
nothing to the numerator *and* nothing to the denominator. The dilution that
forces `one_turn` into a three-cell scope does not exist in the conditional
form. Eight is also the scope rounds 26 and 27 both used, so the three rounds'
numbers sit beside each other without a scope caveat.

Under the shipped v2 detector, round 27's data reads **p = 0.0845 on the eight
cases and p = 0.1343 on the three**. Registering the eight-case scope is
therefore registering the scope where the prior signal is stronger, and that is
stated here rather than discovered later.

`unread_asks` is cited **uninflated**, and for two reasons rather than one:
`report.py` deliberately carries no phi constant for it (measured 1.09,
p = 0.36), and both sides of this round are one interleaved batch.

Registered co-requirements, scored separately, all **non-inferiority — none may
rise**:

```
--target one_turn --target-cases design-cache,design-realtime,design-upload --target-models sonnet
--target output_tokens --target-cases <the eight> --target-models sonnet
--target turns --target-cases <the eight> --target-models sonnet
```

`one_turn` is a co-requirement here, where it was round 27's target, and it is
the guard that matters most for this metric. A conditional rate can be bought
by moving answers *into* the unread stratum without changing anyone's asking
behaviour, or by suppressing reading so hard that the remaining unread answers
are a different population. Round 27 read `one_turn` exactly flat at 76/200
against 76/200, so this guard has a measured expectation to hold against.

`report.py` prints `REJECT` for a target that fails to improve; for all three
co-requirements that string is not the verdict.

## Registered scope, depth and staging

Sonnet only, eight `design-*` cases, **56 reps a side**, treatment and control
alternating one rep at a time in a single interleaved pass.

**The depth is set by a power calculation done before generation, and it is why
this round is more expensive than round 27.** Conditioning on the unread
stratum costs about three fifths of the denominator: round 27 bought 200 runs a
side and got 76 exposed. Simulating `report.py`'s own `_count_p` against round
27's observed rates — 42.5% control against 27.0% edit — gives:

| exposed per side | power at the observed effect | power at 75% of it |
|--:|--:|--:|
| 76 — *round 27's actual depth* | **0.42** | 0.23 |
| 120 | 0.65 | 0.38 |
| 170 | **0.80** | 0.48 |
| 200 | 0.86 | 0.58 |

Round 27 ran this metric at 42% power. At round 27's measured 38% exposure, 170
exposed a side needs **448 runs a side, 896 in total**, against round 27's 400.
The second column is registered too: **if the true effect is three quarters of
round 27's point estimate, this round has about 48% power and a null read is
uninformative.** That is the winner's-curse risk, quantified in advance rather
than discovered in the verdict.

Bought in stages, per the loop's standing order. **Stage 1 can only kill, never
accept** — there is no draw at which the round stops early and declares
success:

1. **Stage 1, the kill screen.** All eight cases, sonnet, **25 reps a side, 400
   generations, no judging.** Exactly round 27's spend, and directly comparable
   to it. `unread_asks`, `one_turn` and `output_tokens` are all free of judging
   and all readable here.
2. **Stage 2, the accepting read.** Extend the same two snapshots to 56 reps a
   side — 496 further generations, 896 in total. `unread_asks` is scored here,
   at 56 a side, and nowhere else.
3. **Stage 3, the fatal counters.** Judge the batch and score `quality_fails`,
   `never_cut_failures`, `safety_fails` and `violations_total`.
4. **Stage 4.** Step 8 replication, then the step 9 holdout.

Stop at the first stage that fails. `run.py` resumes by key, so stage 2 buys
only the reps it adds.

## Registered stop conditions

1. **Stage 1 kills on a rise.** If `unread_asks` over the eight cases has
   risen at 25 reps a side, one-sided at alpha 0.05, the round stops and the
   edit is reverted. A flat stage-1 read is not a failure and the round
   proceeds to stage 2.
2. **Stage 1 also kills on either guard.** If `one_turn` over its three
   registered cells has risen at alpha 0.05, or `output_tokens` over the eight
   cases has risen past the scoped floor, the round stops. The edit is not
   entitled to spend round 26's compression or its reading rate to buy this.
3. **Stage 2 is the accepting read on `unread_asks`,** one-sided fall at alpha
   0.05, exact conditional binomial, uninflated. **Extending past 56 reps a
   side to chase alpha is optional stopping and is refused in advance.**
4. **A fatal counter that rises rejects**, subject to [#133]'s measured-rate
   screen. If the accept rests only on a cell being screened as sampling, the
   round doc names the screened cells with their counts and p-values next to
   the verdict.
5. **The detector is frozen at the v2 committed in `16c0000`.** No change to
   `asks_back`, `_quality_strata` or `_exposure` may be made while this round is
   in flight, and none may be made afterwards on the basis of what this round's
   responses look like. A v3 addressing v2's known errors — self-resolved forks
   counted as hands-back, question-less hand-backs missed — needs a third
   labelled sample, and may not be scored against these runs.
6. **`unread_asks` stays target-only whatever this round does.** An accept here
   does not make it fatal. [`unread-asks.md`](unread-asks.md) records why: the
   screened fatal form would have rejected round 26, the licence in
   `rules/laconic.md` today, and switching it on is a judgement about that trade
   rather than a statistical decision.

**Registered disclosure, not gates.** Both are computed and published whichever
way the round goes:

- The **joint** unread-hands-back count, the form round 27 reported as 19/200
  to 9/200. The registered target is the conditional rate; the joint count is
  reported beside it so the two rounds can be read against each other.
- The **hands-back-after-reading** count. Round 26 measured that stratum
  failing 0 of 6, and the edit is predicted not to touch it. A fall here would
  mean the edit is suppressing asking generally rather than the unread asking
  specifically, which is not what it was written to do.

## Method

Two trees, one interleaved pass, alternating one rep at a time:

- Treatment: this branch, the round 27 rules text.
- Control: a detached worktree at master `ffffa39`.

Both `rules_cksum` values are verified before the first generation and recorded
with the results. The driver waits and retries a rep that fails rather than
marching on, and counts failures only within the rep it is generating.

`rules/laconic.md` and `evals/cases/` are frozen for the duration of the pass,
per `AGENTS.md`: both are checksummed into every snapshot and a change to
either invalidates the round.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#133]: https://github.com/JordanMPDS/laconic/issues/133
[#138]: https://github.com/JordanMPDS/laconic/issues/138
[#146]: https://github.com/JordanMPDS/laconic/issues/146
[#147]: https://github.com/JordanMPDS/laconic/pull/147

---

## Results

*Nothing below this line was written before generation began.*

### Stage 1: nothing kills, and one registered disclosure lands the wrong way

**Generation:** 400 runs, 200 a side, 25 reps, **0 failed, 0 retries, 0 backoff
waits**, 04:16 to 07:55 UTC. Both sides CLI 2.1.241, `cases_cksum` 2423244529,
treatment `rules_cksum` 136269960, control 3694954268, neither tree dirty.
**Every one of those four provenance values is identical to round 27's**, so
the two rounds are comparable without a caveat.

Scored through `report.py`'s own `round_summary` and `accept_verdict` with
`judg=None`. The fatal counters read verdicts and are unscored here by
construction; stage 3 is the run whose verdict counts.

**Registered stop condition 1 (the target) does not kill — it falls.**
`unread_asks`, the conditional rate over the unread stratum, eight cases,
sonnet, uninflated:

| | control | edit | one-sided fall |
|---|--:|--:|--:|
| `unread_asks` | 31/74 (41.9%) | 16/67 (23.9%) | **p = 0.0432** |

Per the registration a stage-1 read may only kill. **This one clears alpha and
is not being allowed to accept anything** — stage 2 at 56 reps a side is the
accepting read, and stopping here would be the optional stopping stop condition
3 refuses in advance.

**Registered stop condition 2 (both guards) holds.**

`one_turn` over its three registered cells reads 34 → 36, and round-wide over
the eight it reads **74 → 67**: the edit opened a file slightly *more* often,
not less. Nothing approaches a significant rise, so the conditional rate is not
being bought by moving answers into its own denominator.

`output_tokens`, stratified per [#131], all eight cells voting grounded, none
refused:

| cell | stratum | control | edit | shift |
|---|---|--:|--:|--:|
| `design-alerting` | grounded | 2605 | 2725 | +120 |
| `design-audit-log` | grounded | 3508 | 3552 | +44 |
| `design-cache` | grounded | 2797 | 2998 | +201 |
| `design-rate-limit` | grounded | 2298 | 2020 | −278 |
| `design-realtime` | grounded | 2222 | 2134 | −88 |
| `design-retry` | grounded | 2360 | 2770 | +410 |
| `design-search` | grounded | 1498 | 1557 | +58 |
| `design-upload` | grounded | 2324 | 3104 | +780 |

Six of eight rose, sign test p = 0.289, **median shift +89 tokens against a
scoped floor of 548.1**. The shift is well inside the floor and the sign test
does not reach alpha, so round 26's compression is not being spent.
Non-inferiority holds.

`turns` moved +0.5 over the eight cells with 1 of 8 rising against a 0.5-turn
floor, and does not reject.

### The instrument check: both control sides agree to within a fifth of a point

Round 28's control is master rules, and so was round 27's, generated a day
apart on the same CLI over the same cases. Read with the same v2 detector:

| | round 27 | round 28 |
|---|--:|--:|
| control conditional rate | 32/76 (42.1%) | 31/74 (**41.9%**) |
| edit conditional rate | 21/76 (27.6%) | 16/67 (**23.9%**) |

Two independent interleaved batches put both sides of the contrast within two
points of each other. The metric is measuring something stable.

### The disclosure that did not go as registered

Stop condition 4's second registered disclosure was the hands-back-after-reading
count, and the registration said what a movement there would mean:

> A fall here would mean the edit is suppressing asking generally rather than
> the unread asking specifically, which is not what it was written to do.

**It fell, and it fell harder than the target did.** Both rounds under the same
v2 detector, sonnet, eight cases:

| after reading | control | edit | one-sided fall |
|---|--:|--:|--:|
| round 27 | 12/124 | 11/124 | 0.500 — flat, as registered |
| **round 28** | **17/126** | **6/133** | **0.0125** |

Round 27 read this stratum exactly flat. Round 28 reads it at p = 0.0125,
against a target that reads 0.0432. Same two rules texts, same eight cases,
same CLI, same detector, one day apart.

Three readings are open and this round cannot separate them:

1. **Chance.** This is one of several disclosures computed on this data and
   carries a multiplicity burden the pre-registered target does not. The two
   rounds' edit sides, 11/124 and 6/133, are not significantly different from
   each other; the rounds disagree because each substratum is small.
2. **A detector artifact.** v2 bought its recall by accepting false positives
   of exactly one shape — a fork posed as a question and resolved in the same
   breath. That shape lives in *grounded* answers, which is precisely this
   stratum, so an edit that discourages the rhetorical fork without
   discouraging any real hand-back would produce this reading. **Stop condition
   5 forbids testing that against these runs**: separating the two needs a
   third labelled sample, and scoring a v3 on responses whose behaviour is
   already known is what the freeze-before-draw rule exists to prevent.
3. **Real.** The edit says to ask for the fork that survives reading, and an
   answer that has read may genuinely have fewer such forks left. Round 26
   measured this stratum failing 0 of 6, so a fall here costs no measured
   quality — but it is not what the edit was written to do, and the licence's
   whole purpose is that asking after reading is legitimate.

Stage 2 roughly doubles this stratum and is where it resolves. **It changes no
registered stop condition**, and it is recorded here rather than folded into
the verdict.

### Stage 2: the accepting read — the registered target clears

**Generation:** extended to 896 runs, 448 a side, 56 reps, 07:57 to 12:55 UTC.
**One usage-limit window at rep 46 failed 6 keys on the edit side.** The driver
backed off and `run.py` regenerated exactly those 6 against 362 already in the
snapshot, which is the resume path working as designed; both snapshots finished
at **0 failed**. Same two trees, same CLI, same `cases_cksum`.

**The registered target, `unread_asks`, eight cases, sonnet, uninflated:**

| | control | edit | one-sided fall |
|---|--:|--:|--:|
| `unread_asks` | 70/165 (42.4%) | 43/153 (28.1%) | **p = 0.0199** |

Exposure landed at 165 and 153 against the 170 a side the power calculation
projected, so the round bought close to the depth it registered for.

**All three registered guards hold.**

`one_turn` **fell** rather than rose — 80 to 76 on its three cells, 165 to 153
round-wide. The conditional rate is not being bought by moving answers into its
own denominator, which was the failure mode this guard was registered against.

`output_tokens`, stratified, all eight cells voting grounded, none refused:

| cell | control | edit | shift |
|---|--:|--:|--:|
| `design-alerting` | 2298 | 2318 | +20 |
| `design-audit-log` | 3262 | 3322 | +60 |
| `design-cache` | 2954 | 3133 | +180 |
| `design-rate-limit` | 2096 | 2020 | −77 |
| `design-realtime` | 2132 | 2151 | +19 |
| `design-retry` | 2516 | 2715 | +199 |
| `design-search` | 1557 | 1492 | −65 |
| `design-upload` | 2374 | 2681 | +306 |

Six of eight rose, sign test p = 0.289, **median shift +40 against a floor of
487.0**. Non-inferiority holds and round 26's compression is intact.

`turns` moved +0.5 with 2 of 8 cells rising against a 0.9-turn floor — held.

### Stage 3: the fatal counters, and `report.py`'s verdict

Both sides judged to completion, 448 judgments each, default coverage on both
so the two carry the same grading. **`report.py` exits 0: accept.**

**`quality_fails` rose 90 to 94 and was cleared by the round's own sampling
screen**, so stop condition 4 requires the cells named here beside the verdict:

| screened cell | control | edit | p |
|---|--:|--:|--:|
| `design-alerting`/sonnet | 24 of 56 | 28 of 56 | 0.285 |
| `design-audit-log`/sonnet | 0 of 56 | 1 of 56 | 0.500 |
| `design-upload`/sonnet | 8 of 56 | 10 of 56 | 0.399 |

Round-wide the rise is one-sided p = 0.4125. `never_cut_failures` and
`safety_fails` did not rise. Readability rose 37 to 50, inside the clustered
sampling noise at p = 0.115 ([#103]).

### The composition effect, disclosed

`report.py` splits `quality_fails` on the hands-back covariate, and the two
strata moved in opposite directions:

| stratum | control | edit | |
|---|--:|--:|---|
| hands the decision back | 34/104 (32.7%) | 17/58 (29.3%) | fall p = 0.397 |
| resolves it | 56/344 (16.3%) | 77/390 (19.7%) | **rise p = 0.131** |

**The mechanism worked and the round-wide count did not follow.** The edit moved
46 answers out of a stratum that fails at about a third and into one that fails
at about a sixth, which on the control's rates predicts roughly seven or eight
fewer failures. `quality_fails` instead rose by four, because the receiving
stratum's own rate rose enough to absorb the gain. Neither rate movement is
significant on its own, and the round-wide count is flat.

This is round 26's disclosure in mirror image. Round 26 moved answers *into* the
hands-back stratum while the resolving stratum improved; this edit moves them
back out while the resolving stratum degrades. Neither round can say whether
that trade is real or whether both are reading one noisy composition.

### The after-reading disclosure, at full depth

| after reading | control | edit | one-sided fall |
|---|--:|--:|--:|
| round 27 | 12/124 | 11/124 | 0.500 |
| round 28, stage 1 | 17/126 | 6/133 | 0.0125 |
| **round 28, stage 2** | **34/283** | **15/295** | **0.0031** |

Doubling the stratum sharpened it rather than washing it out, which largely
retires the chance reading recorded at stage 1: a multiplicity artifact does not
usually strengthen with sample size. What remains is v2's known false-positive
shape — a fork posed as a question and resolved in the same breath, which lives
in exactly this grounded stratum — or a real effect. **Stop condition 5 forbids
separating them against these runs.** A v3 needs a third labelled sample.

Recorded plainly: **the edit suppresses asking after reading as well as before
it**, and the licence's whole point is that asking after reading is legitimate.
Round 26 measured that stratum failing 0 of 6, so the suppression costs no
measured quality — but it is a cost, and it is not what the edit was written to
do.

**Spend so far:** 896 generations at $65.05, plus 896 judgments.

[#103]: https://github.com/JordanMPDS/laconic/issues/103
