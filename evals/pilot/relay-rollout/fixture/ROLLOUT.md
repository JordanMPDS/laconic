# Ranker v7 rollout

Owner: search-ranking. Reviewers: SRE (search), data science (experiments).
Status: approved for shadow, 2026-11-04.

Ranker v7 replaces the v6 learning-to-rank model behind product search. It
adds 12 features (40 in total, from 28) and a second-stage re-ranker for the
top 50 results. Offline it improves NDCG@10 by 3.1% on the October replay set.
Offline gains have not survived contact with live traffic before (v5, 2025),
so v7 ships in two stages: a shadow stage, then a live A/B stage. Each stage
has to pass before the next one starts.

## Stage 1: shadow

### What runs

v7 scores every search request in parallel with v6. v6 still serves every
result page; v7's output is logged and never shown. No user sees v7 during
this stage, and nothing a user does can be affected by it.

- The sidecar `rank-shadow` consumes the Kafka topic `search.requests.v3` at
  100% sampling and scores each request with v7.
- v7's top 10 for each request is written to `ranker_shadow_log` in batches
  every 5 minutes, beside v6's top 10 for the same request.
- The nightly job `shadow_overlap_daily` runs at 03:10 UTC and writes per-day
  overlap, latency and null-rate figures to `ranker_shadow_daily`.
- Dashboard: "Ranker v7 / Shadow" in Grafana, folder `search-ranking`.

### Duration

At least 7 days, and the window must include a full weekend: weekend query
mix differs (more browsing, fewer exact-SKU searches) and v6 regressed on it
in 2024.

### Pass criteria

All four must hold over the whole window, read from `ranker_shadow_daily`:

1. **Latency.** p99 v7 scoring latency at or under 45 ms at daily peak.
   v6 runs at 38 ms; the page budget allows 7 ms more.
2. **Errors.** Timeout and error rate at or under 0.1% of requests.
3. **Overlap.** Top-10 overlap with v6 between 55% and 85% on every day.
   Below 55% usually means a broken feature rather than a better model; above
   85% means v7 is too close to v6 for an A/B test to see a difference, and
   the stage stops for a modelling review instead of moving on.
4. **Feature health.** No input feature null in more than 2% of requests.
   The new inventory features come from a service that has not been called at
   search volume before.

### Alerts

- `RNK-221`: v7 p99 latency above 45 ms for 15 minutes.
- `RNK-222`: v7 timeout rate above 0.1% for 15 minutes.
- `RNK-230`: any feature null rate above 2% for an hour.

All three page `#search-ranking-oncall`. They do not page during the A/B
stage, which has its own alerts.

### Exit

Sign-off by the search lead and the SRE on call at the Thursday ranking
review, with the `ranker_shadow_daily` table for the window attached.

## Stage 2: live A/B

### What runs

10% of logged-in users get v7 results; a second 10% are a holdback control
that stays on v6. The other 80% stay on v6 and are not in the experiment.
Assignment is by hashed `user_id` with salt `rk7-2026q4`, so a user keeps the
same arm across devices and sessions. The flag `search.ranker_v7_pct` goes
from 0 to 10 at the start and does not change during the test. Logged-out
traffic stays on v6 throughout.

### Primary metric

Successful-search rate (SSR): the share of a user's searches that end in a
click followed by at least 30 seconds of dwell, or an add-to-cart, within 10
minutes. It is averaged per user first and then across users, so a few heavy
searchers cannot dominate the result. Definition: `ssr_v2` in the metrics
repository. Baseline SSR is 41.2%.

### Decision rule

v7 passes if SSR improves by at least 1.0% relative (about 0.4 percentage
points), one-sided, alpha 0.05, read once at a fixed horizon of 14 days.
Nobody reads the primary for success before day 14.

### Guardrails

Each must hold at day 14:

- Zero-result rate up by no more than 0.2 percentage points.
- p99 result-page latency up by no more than 30 ms.
- Revenue per user down by no more than 1.5%.

### Sample size

A 1.0% relative change in SSR at 80% power needs about 1.9 million users per
arm, which 10% of logged-in traffic reaches in 14 days.

**Note on revenue.** The sample size was computed for SSR only. Revenue per
user is far noisier: at 14 days and 10% per arm the test can detect only a
drop of about 4%. The 1.5% revenue guardrail therefore cannot actually be
tested by this experiment, and a flat revenue reading at day 14 is not
evidence that revenue is unharmed. Finance has agreed to treat revenue as
monitored rather than gated here, and to run a dedicated revenue holdout
after launch.

### Stop rules

The test stops early only for harm, never for success:

- a guardrail breached on two consecutive daily readouts;
- a Sev-2 or worse incident attributed to v7;
- SSR down by 2% or more on any daily readout. This is a harm monitor, not a
  test of the hypothesis.

### Mechanics

- Assignments are logged to `exp_assignments` with experiment id `rk7`.
- The daily readout job `ab_readout_rk7` runs at 06:00 UTC and posts to
  `#search-experiments`.
- Analysis notebook: `rk7_readout.ipynb`, which reads `exp_assignments` joined
  to the `ssr_v2` daily table.
- Alerts `RNK-240` (zero-result rate) and `RNK-241` (page latency) replace
  the shadow alerts for the duration of the test.

## Timeline

| step | dates |
|---|---|
| shadow | 2026-11-10 to 2026-11-17 |
| shadow review | 2026-11-20 |
| A/B | 2026-11-24 to 2026-12-08 |
| readout | 2026-12-10 |
| launch decision | 2026-12-11 |

If the shadow stage fails, the A/B dates move by at least two weeks; the
holiday code freeze starts 2026-12-15, so a slip past 2026-12-01 pushes the
launch into January.
