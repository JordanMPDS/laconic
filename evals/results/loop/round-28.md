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
