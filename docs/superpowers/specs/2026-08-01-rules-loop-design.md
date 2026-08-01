# Rules improvement loop — design

**Date:** 2026-08-01
**Status:** approved, not implemented

A closed loop over `rules/laconic.md`: benchmark, review the failures, propose
one rule edit, confirm it, and either open a PR or throw it away. The loop
proposes; a human merges.

## Why this needs guardrails before it needs an engine

The loop optimizes the rule set against the benchmark that grades it. Three
properties of the existing suite make a naive version worse than no loop at all:

- **Eight of the eleven cases cannot support a comparison between arms.** Five
  grade the never-cut contract the treatment was explicitly instructed to
  follow; three grade adherence to laconic's own style prohibitions. Tuning
  rules against a case that grades adherence to those rules is circular.
  `evals/CRITERIA.md` already records which is which in each case's `grading`
  field, and the loop reads it.
- **The preference judge has a measured 63% length bias and a 35% flip rate**
  ([`evals/results/2026-08-01-preference.md`](../../../evals/results/2026-08-01-preference.md)).
  A loop that maximizes preference chases that noise.
- **Repeated hypothesis tests against one metric manufacture winners.** Twenty
  candidate edits scored at p < 0.05 produce one significant result from noise
  alone.

The design answers each: `grading` decides what may be optimized, preference is
admissible only under a flip-rate condition and can never reject on its own, and
every attempt is logged with an independent replication required before a
proposal reaches a human.

## Decisions

| Decision | Choice |
|---|---|
| What counts as better | Everything: deterministic metrics, never-cut gate, quality verdicts, and preference — the last constrained (see below) |
| Who edits `rules/laconic.md` | The loop proposes a diff on a branch with its evidence; a human merges or rejects |
| Cost per round | A full round every time: laconic arm regenerated at n=5 on both models, judge and preference against carried controls |
| Overfitting defense | A reserved holdout **and** replication on a fresh sample |
| Holdout source | Four to five newly authored cases, never shown to the loop |
| Architecture | A skill over the existing scripts, plus two offline analyses. No orchestration engine |

Approach C — a multi-agent workflow generating and adversarially verifying
candidate edits in parallel — is deferred to its own issue. The bottleneck is
the confirmation round, not candidate generation, so it earns its cost only once
idea quality is the constraint.

## Round anatomy

Nine steps. Only 1–3 and 6 spend money.

| # | Step | Command | Calls |
|---|---|---|--:|
| 1 | Generate | `run.py --arms laconic --carry-arms-from evals/snapshots/results.json --snapshot evals/snapshots/loop/round-NN.json` | 110 |
| 2 | Judge | `judge.py --results <round> --out <round-judgments>` | 110 |
| 3 | Prefer | `prefer.py --results <round> --control baseline --jobs 6` | 130 |
| 4 | Review | `review.py <round>` | 0 |
| 5 | Propose | reasoning step — one rule edit, hypothesis written first | 0 |
| 6 | Confirm | steps 1–3 against the edited rules | 350 |
| 7 | Compare | `report.py --against <round N>` | 0 |
| 8 | Replicate | fresh generation of the affected cases | ~110 |
| 9 | Holdout | `run.py --cases-dir evals/holdout` + judge | ~100 |

Roughly 900 calls per accepted change, about 1.5 to 2 hours at six workers. A
rejected candidate stops after step 7 at roughly 700.

### Why controls are carried, not regenerated

A rule edit changes the `laconic` arm and nothing else — `baseline`,
`terse-control` and `word-compression` carry no rules in their system prompts.
Regenerating them each round would triple the cost to reproduce runs that cannot
have moved.

`run.py` gains `--carry-arms-from <snapshot>`: it copies every run whose arm is
not in `--arms` into the new snapshot and stamps
`metadata.carried_arms_from = {path, rules_cksum}`. The mixed-snapshot caveat
the benchmark already discloses by hand then travels with the data instead of
depending on someone remembering it.

`prefer.py` and `report.py` need no change — they read one snapshot containing
both arms, which is what this produces.

## Step 4: `review.py`, the failure inventory

Offline, no calls. Input is a round's snapshot plus its judgments and
preferences; output is a ranked markdown inventory, one entry per failure:

- **What failed** — case, model, rep, and the failing excerpt verbatim: the
  sentence carrying the arrow, the response missing the never-cut keyword, the
  trap verdict with the judge's `quote` field, the preference loss with its
  `reason`.
- **Which rule governs it** — the bullet from `rules/laconic.md` that the
  failure sits under, resolved from the never-cut item or the metric class. A
  failure with no governing rule is itself a finding and is ranked first: it
  means the rule set is silent where the benchmark expects it to speak.
- **Whether it is new** — carried over from the previous round, or introduced by
  the last accepted edit.

Ranking is by class, not by count: never-cut failures, then quality, then
readability, then preference. A single never-cut failure outranks any number of
preference losses.

`review.py` refuses to rank a `rule-adherence` case as an optimization target
and says so in the output, reading the `grading` field rather than a hardcoded
list.

## Step 5: the proposal

One minimal rule edit per round, with a hypothesis recorded **before** the
confirming round runs:

> Editing `<bullet>` should move `<metric>` on `<cases>` in `<direction>`.

Written afterwards, a hypothesis is indistinguishable from a story about
whatever moved. The ledger stores it with a timestamp preceding the round-N+1
snapshot, which makes the ordering checkable rather than asserted.

## Step 7: the accept rule

**Fatal — any one rejects the edit:**

- A never-cut verdict lost, on dev or holdout.
- A quality verdict lost, on dev or holdout.
- Readability violations up, on dev or holdout.

**Required to accept:**

- The hypothesis's named target metric moves past the noise floor.
- The move survives replication on a fresh sample (step 8).

**The noise floor is the published dispersion, not a new invention.** laconic's
stdev is 175 output tokens on Sonnet, and `levels.py` already implements a
two-sided exact sign test over the 22 case/model cells. A median shift inside
one stdev, or a sign test at p ≥ 0.05, is not an improvement.

**Preference is admissible and constrained.** It may support acceptance only in
a round whose flip rate is below 35% — the value measured on 2026-08-01 — with
that round's length bias printed beside it. It can never on its own reject an
edit that passed every deterministic gate. The judge that produces it favours
the longer answer 63% of the time, and laconic is the short arm by construction.

## The ledger

`evals/results/loop/LEDGER.md` carries one line per attempt, **including
rejected ones**: round number, hypothesis, target metric, verdict, and the
commit of the rules revision it was tested against. `round-NN.md` carries the
full record — diff, before-and-after tables, replication, holdout.

Recording rejections is the point. An accept rate visible next to a claim is
what lets a reader discount it; twenty attempts and one acceptance is a
different result from one attempt and one acceptance, and only the ledger can
tell them apart. Replication is the defense against noise; the count is the
disclosure.

## Holdout cases

Four to five new cases under `evals/holdout/<case>/`, same `prompt.md` +
`expect.json` + optional `fixture/` contract as `evals/cases/`. Outside
`run.py`'s default glob, so no ordinary run touches them.

Coverage: at least two exercising never-cut items (a destructive action and an
ordered procedure), one requested explanation, and one ordinary short question
where the correct answer is brief. They are scored only at step 9.

**Holdout verdicts never appear in the published benchmark tables.** A holdout
case that shows up in a table is a case someone will optimize against, and it
stops being a holdout the moment it does.

## Components

| File | Status | Purpose |
|---|---|---|
| `evals/bench/review.py` | new | Failure inventory with governing rule text |
| `evals/bench/report.py` | changed | `--against <snapshot>` round-over-round deltas and the accept verdict |
| `evals/bench/run.py` | changed | `--carry-arms-from`, `--cases-dir` |
| `evals/holdout/<case>/` | new | Reserved cases |
| `evals/results/loop/` | new | Ledger and per-round records |
| `skills/laconic-loop/SKILL.md` | new | The procedure |
| `tests/test_bench.py` | changed | Rule attachment, accept/reject truth table, carried-arm metadata |
| `tests/test_evals_layout.sh` | changed | Holdout exists and the default glob does not reach it |

## Testing

- **Rule attachment.** A synthetic failure resolves to the expected bullet, and a
  failure with no governing rule ranks first.
- **The accept/reject truth table.** Every fatal condition rejects on its own; a
  target move inside the noise floor rejects; a preference-only signal in a
  high-flip round neither accepts nor rejects.
- **`grading` is honoured.** A `rule-adherence` case cannot be named as an
  optimization target.
- **Carried arms.** A snapshot built with `--carry-arms-from` contains the
  control runs, and its metadata names the source snapshot and that snapshot's
  `rules_cksum`.
- **Layout.** Holdout cases exist, carry `expect.json`, and are absent from the
  default case glob.

No live model calls in any of it, matching `tests/test_bench.py`'s existing
contract.

## Out of scope

- **Autonomous merging.** The loop never changes shipped behavior on its own.
- **The haiku adherence ceiling.** laconic's compression is a Sonnet result;
  whether haiku's -1% is a model-capability floor or a fixable rule-text problem
  is a separate question, and this loop will not answer it by accident.
- **Multi-agent candidate generation.** Approach C, deferred to its own issue.
