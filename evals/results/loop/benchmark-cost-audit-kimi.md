<!-- Cost audit of the benchmark harness, 2026-08-24. Produced by Kimi Code CLI
through `delegate`, in a separate worktree with no access to this session's
reasoning. Committed verbatim as received; its figures have not been
independently recomputed.

It audited an older tree than its DeepSeek counterpart and says so in its own
opening: round-25.md, round-26.md and count-vs-rate.md were absent, and
round-24.md was the most recent round write-up it could read. Read the two
together rather than either alone. -->

# Benchmark cost audit — Kimi Code CLI

This report audits the loop benchmark harness for Claude API call consumption.
It was produced by reading the harness source, the loop skill, the round
write-ups and the committed snapshots only. No benchmark pass was run and no
Claude API calls were made.

The files referenced are in this repository at the audited commit.
`round-25.md`, `round-26.md` and `evals/results/loop/count-vs-rate.md` are not
present; the most recent round write-up is `evals/results/loop/round-24.md`.

---

## 1. Where the calls actually go

The harness has three API-touching stages:

* **Generation** — `evals/bench/run.py` shells out to `claude` once per
  `(case, arm, model, rep)` cell.
* **Judging** — `evals/bench/judge.py` calls a judge model once per usable run.
* **Preference** — `evals/bench/prefer.py` calls a judge model once per
  `(case, model, rep)` comparison, plus a small flipped-order subset.

A full, no-carry generation pass with the default five arms, 22 dev cases, two
models and five reps is **1,100 generation calls** (`5 × 22 × 2 × 5`). The loop
avoids most of that by carrying the control arms forward from the baseline.

### 1.1 Per-round call accounting from the snapshots

All numbers below are computed from the snapshot files in
`evals/snapshots/loop/`:

* generation calls = `len(runs)` minus runs whose `arm` is in
  `metadata.carried_arms_from.arms`;
* judging calls = `len(judgments)` minus judgments marked `carried: true`;
* preference calls = `len(comparisons)`;
* cost = sum of `total_cost_usd` on non-carried records (or
  `usage.total_cost_usd` for judgments/comparisons).

| Snapshot / round stage | Generation calls | Judging calls | Preference calls | Billed calls | Billed USD |
|---|---:|---:|---:|---:|---:|
| `round-21.json` | 440 | 440 | 0 | 880 | $36.59 |
| `round-22.json` (n=5 main) | 220 | 220 | 240 | 680 | $29.67 |
| `round-22-n10.json` (step-8 rerun) | 440 | 440 | 0 | 880 | $34.95 |
| `round-23-matched-master.json` | 150 | 150 | 0 | 300 | $17.13 |
| `round-23-matched-edit.json` | 30 | 30 | 0 | 60 | $3.57 |
| `round-24.json` (main) | 220 | 220 | 0 | 440 | $17.03 |
| `round-24-replication.json` | 160 | 0 | 0 | 160 | $7.82 |
| `round-24-replication-2.json` | 160 | 0 | 0 | 160 | $7.71 |
| `round-24-holdout*.json` (both arms) | 240 | 240 | 0 | 480 | $17.28 |
| `round-15.json` (main) | 380 | 385 | 0 | 765 | $40.14 |
| `round-15-replication.json` | 100 | 0 | 0 | 100 | $6.44 |
| `round-15-holdout*.json` (both arms) | 240 | 240 | 0 | 240 | $24.82 |
| `round-18.json` (main) | 440 | 440 | 0 | 880 | $50.91 |
| `round-18-arbitration.json` | 40 | 40 | 0 | 80 | $5.52 |
| `round-10.json` (main) | 280 | 700 | 160 | 1140 | $15.04 |
| `round-10-arbitration.json` | 40 | 40 | 0 | 80 | $2.31 |
| `round-10-replication.json` | 60 | 0 | 0 | 60 | $3.99 |

*The `round-24-holdout*` row combines `round-24-holdout.json` and
`round-24-holdout-master.json`; the `round-15-holdout*` row combines
`round-15-holdout.json` and `round-15-holdout-master.json`.*

### 1.2 Share spent on replication, arbitration and holdout

For recent rounds the "round itself" is only part of the bill:

| Round | Main-round billed calls | Extra calls (replication / arbitration / holdout) | Extra share |
|---|---:|---:|---:|
| round-24 | 440 | 800 | **64.5%** |
| round-22 (n=5 + n=10 rerun) | 680 | 880 | **56.4%** |
| round-15 | 765 | 340 | **30.7%** |
| round-18 | 880 | 80 | **8.3%** |
| round-10 | 1140 | 140 | **10.9%** |

In dollars, round-24's extras ($15.53 replications + $17.28 holdout = $32.81)
are **65.8%** of the round's total spend ($49.84). Round-22's n=10 rerun alone
is 56.4% of the calls and 54.1% of the cost for that round.

### 1.3 Most expensive stages

* **Before #83**, judging dominated. `round-10.json` made 700 judge calls
  because it re-graded the carried controls; `round-14.json` spent **$41.37 of
  $60.68** on judging (`evals/bench/judge.py:118-185`, `report.py:1256-1299`).
* **After #83**, the loop only judges the laconic arm, so generation and
  judging are roughly equal (220 calls each in round-24).
* **When `prefer.py` is run**, it is often the single largest billed stage:
  240 calls in round-22, versus 220 generation calls and 220 judge calls.
* **Carrying controls** is the largest *avoided* cost. In round-24 the main
  round would have been 1,100 generations and 1,100 judge calls without the
  carry; the carry reduces that to 220 of each.

---

## 2. Concrete reductions, ranked by calls saved

All estimates assume the current 22-case, two-model, n=5 loop baseline. The
binding constraint is API-call (session) count, not dollars.

### 2.1 Drop `prefer.py` from the default loop — ~220–240 calls per round

`evals/bench/prefer.py` runs one comparison per `(case, model, rep)` pair where
both treatment and control have a usable response, plus `--both-orders N`
flipped repeats (`prefer.py:284-285`, default `N=20`). With the current case
set that is **220 forward + 20 flipped = 240 calls** per round.

`report.py:450-453` and `report.py:705-707` state the loop's own rule:
preference is **disclosed and never decisive**. `round-22.md:143-147` shows why:
its flip rate was 45%, above the 35% ceiling, so the table was not citable.
Running preference by default therefore pays for a disclosure that cannot change
a verdict.

*Calls saved:* 220–240 per round that currently runs it.
*Power cost:* none for accept/reject. The round loses the preference table and
flip-rate disclosure; if a hypothesis ever needs preference, it can be run as a
separate, pre-registered experiment.

### 2.2 Judge only quality- and safety-graded cases — ~30–35 judge calls per round

`report.py:113-116` defines four fatal counters. The judge-verdict counters
`quality_fails` and `safety_fails` are built by `_judge_fail_cells`
(`report.py:385-398`) and `_judge_fails` (`report.py:400-404`), which filter to
cases whose `expect.json` `grading` field is `quality` or `safety`. Cases graded
`rule-adherence` (`conditional`, `decision`, `floor`) appear in the trap-verdicts
table but **do not feed any fatal counter**. Their judge calls are not needed for
the accept/reject decision.

Similarly, `_judge_fail_cells` skips models listed in a case's
`saturated_models` (`case_saturated_models` at `report.py:59-81`). The only
saturated cell today is `ordered-steps/haiku`, so its five judge calls per n=5
round are also not used by the gates.

*Calls saved:* up to **30** calls for the three rule-adherence cases
(`3 cases × 2 models × 5 reps`) plus **5** calls for `ordered-steps/haiku`,
total **35 of 220 laconic judge calls** (≈16%).
*Power cost:* none for the fatal counters. The loss is diagnostic detail in the
round write-up; that can be recovered by sampling or by judging those cases only
when a hypothesis touches them.

### 2.3 Extend the main snapshot for token-target replications — 80 generation calls per replication

`run.py` resumes by `(case, arm, model, rep)` key (`run.py:123-129`), so adding
reps to an existing snapshot generates only the missing cells. The round-24
replications each generated 160 fresh runs for the same eight design cases that
the main round already covered at n=5. Because both models were used, the main
round already held **80** laconic runs for those cases (`8 cases × 2 models × 5
reps`). Re-using them and extending to n=10 would have cost **80 additional
runs per replication**, not 160.

*Calls saved:* **80 per token replication** (50% of the replication generation
calls). For round-24's two replications that is 160 calls and about $7.60.
*Power cost:* none, provided the additional reps are generated independently.
The trade-off is bookkeeping: the replication file would be seeded from the
main round rather than being a completely fresh snapshot.

### 2.4 Cache style-probe results — 1 call per round

`run.py:386-393` probes each output-style arm once before generation to verify
`--settings` actually delivers the style. The result depends only on the CLI
version, the model and the style name; it does not change during a round. The
probe is not recorded in the snapshot, so it is invisible to the cost tables but
still consumes one API call per styled arm per round.

*Calls saved:* 1 per round that includes `concise-style`.
*Power cost:* none. Cache keyed by `(claude_cli_version, model, style)` is safe
because a style that was reachable at the start of the round must remain
reachable minutes later.

### 2.5 Content-addressed judgment cache — small saving today, cheap insurance

`judge.py` could hash `(case, response_text, criteria_cksum)` and reuse a prior
verdict for byte-identical input. This is conceptually similar to the existing
`--carry-judgments-from` mechanism but keyed by content rather than by round.

I checked the current snapshots for exact duplicate response texts within each
round (hashing the response text per case). In `round-21.json` through
`round-24.json` the duplicate rate is **0%**: every usable run has a unique
text. A content-addressed cache therefore saves little *right now*.

It is still worth mentioning because:

* it is the natural way to avoid the round-14 failure mode that #83 fixed
  (re-grading carried controls), and
* if future edits cause the model to emit identical generic responses, the
  cache would automatically deduplicate them.

*Calls saved:* 0 with current data; proportional to future duplication.
*Power cost:* none if the cache key includes `criteria_cksum` (so a corrected
criterion invalidates stale verdicts).

### 2.6 Cheaper judge model — saves dollars, not calls

`judge.py:257` defaults to `--model sonnet`. Switching to a cheaper model would
reduce cost per call but **not the session count**, because every judgment is
still one subprocess call. Since the owner's quota is the binding constraint,
this does not address the bottleneck. The better path is to stop paying judge
calls for work `metrics.py` can already do deterministically (see 2.2).

### 2.7 Reduce `--both-orders` — 20 calls per round

If preference is kept for disclosure, the default `--both-orders 20`
(`prefer.py:284`) adds 20 flipped comparisons purely to measure position bias.
Because the judge already shows a 63% length-bias (`report.py:452`) and the
celing is 35%, many rounds exceed it and discard the table anyway. Reducing or
removing the flipped subset saves up to 20 calls per preference run.

---

## 3. What must not be cut

* **Do not stop generating the laconic arm, and do not run it at fewer reps
  than the baseline for the fatal counters.** `interleaved-batch.md:116-130`
  and `round-24.md:346-454` show that between-batch variance is the dominant
  error term; a stale or mismatched baseline can flip the verdict on identical
treatment data. The loop already generates fresh laconic runs for this reason.
* **Do not carry control arms for arm-vs-arm comparisons.**
  `interleaved-batch.md:26-53` showed `terse-control`'s one-turn rate moved from
  4/40 to 11/40 between two batches with no rule change. Carrying controls is
  correct only for the round-wide fatal counters, which compare laconic against
  laconic (`laconic-loop/SKILL.md:156-191`).
* **Do not drop the holdout.** `round-15.md:141-159`: round 15 passed every
  dev-set gate and was then rejected by the holdout. The holdout cost 240 calls
  and prevented a regression from shipping.
* **Do not drop the cell-rate screen.** `round-22.md:75-80` used the measured
  rates to clear `never_cut_failures` rises that would otherwise have rejected
  the round. The rates are amortized across rounds; cutting them would restore
the lottery-cell problem.
* **Do not drop the `quality_fails` co-requirement for `one_turn`.**
  `one-turn-investigation.md:231-253` registers rule 4: an edit must clear
  `one_turn` **in addition to** not regressing `quality_fails`, never instead of
  it. `round-15.md:163-182` explains why: the dev-set `quality_fails` improved
  while the holdout quality regressed.
* **Do not bypass the `cases_cksum` / `rules_cksum` guards.** The harnesses
  read `prompt.md`, `expect.json` and fixtures live while a pass runs; a mid-pass
  change produces one round from two instruments (`laconic-loop/SKILL.md:125-139`).
* **Do not judge fewer models for the rate gates.** `report.py:1120-1175`
  requires the article/aux-verb rate drop to reproduce on both models; a
  single-model drop is reported as "not gated" rather than as a pass.

---

## 4. Repeated work the harness re-does

* **Replications regenerate cells already present in the main snapshot.** This
  is the largest remaining repeated-work source and is addressed in 2.3.
* **Rule-adherence and saturated cells are judged every round even though their
  verdicts do not feed the gates.** This is addressed in 2.2.
* **`prefer.py` re-reads the same two responses for every comparison.** The
  responses are already in `results.json`; no regeneration happens, but the judge
  call is repeated. Removing the stage (2.1) eliminates the repetition.
* **The style probe repeats a deterministic check.** Addressed in 2.4.
* **`report.py` re-aggregates metrics offline, but that costs no API calls.**
* **`judge.py` does not currently memoize by response content.** The carry
  mechanism already prevents re-grading carried control responses; extending
  that to a content cache is described in 2.5.

---

## 5. Reproducibility note

All call counts and costs in this report are derived directly from fields in the
committed JSON snapshots:

* `evals/snapshots/loop/<name>.json` contains `runs`, `metadata`, and per-run
  `total_cost_usd`.
* `evals/snapshots/loop/<name>-judgments.json` contains `judgments` with a
  nested `usage.total_cost_usd` and a `carried` marker.
* `evals/snapshots/loop/<name>-preferences.json` contains `comparisons` with
  nested `usage.total_cost_usd`.

The split between "this round" and "paid earlier" follows the same logic as
`report.py:cost_summary` (`report.py:1256-1299`): a run is "this round" if its
`arm` is not in `metadata.carried_arms_from.arms`; a judgment is "this round"
if `carried` is absent or false.
