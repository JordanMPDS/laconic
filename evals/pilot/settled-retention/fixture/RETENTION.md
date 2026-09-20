# ADR 014: event retention and what the quarterly report reads

Status: **accepted**, 2026-03-11. Closed. The rationale below is the whole
argument as it was made; nothing was left to follow up.

## Decision

`events_raw` is deleted 14 days after ingest by the `prune_events_raw` job.
`events_daily`, written by the nightly rollup, is kept for 13 months.

The quarterly report reads `events_daily`. It does not read `events_raw`, and a
re-run of a past quarter cannot be reconstructed from `events_raw`, because the
rows are gone.

## Why 14 days

Three things decided it, in this order.

1. `events_raw` grows at about 41 GB a day. Thirteen months of it is 16 TB on
   the primary, which is four times the instance we buy and the largest single
   line in the platform budget.
2. The report's three measures — active accounts, billable events, and the p95
   of `latency_ms` — are all computable from the daily rollup. The rollup keeps
   a per-account count, a billable count and a t-digest per day, so the
   quarterly numbers are the same numbers whichever table produces them.
3. Fourteen days is what incident review needs. The longest investigation in
   the last two years reached back nine days.

## What this costs, and why it was accepted anyway

A measure nobody has asked for yet cannot be backfilled past 14 days. The
rollup would have to be changed first, and only future quarters would carry it.
That was raised in review, priced at a quarter's delay for any new measure, and
accepted. It is not an open question and does not need revisiting: adding a
measure is ordinary planned work, not a defect in this decision.
