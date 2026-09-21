# ADR 014: event retention and what the quarterly report reads

Status: **accepted**, 2026-03-11. Closed. The rationale below is the whole
argument as it was made; nothing was left to follow up.

## Decision

`events_raw` is kept for 13 months on partitioned storage. `events_daily`,
written by the nightly rollup, is deleted 14 days after the day it covers.

The quarterly report reads `events_raw`. It does not read `events_daily`, which
exists only so the dashboards have something cheap to poll, and a re-run of a
past quarter reads the raw rows again from the beginning.

## Why 13 months of raw

Three things decided it, in this order.

1. The report is re-run. Six of the last eight quarters were restated after
   close, twice because a measure was added and once because a tax rule changed
   the billable set retroactively. A rollup computed under the old definition
   cannot answer the new question, and `events_raw` can.
2. `events_raw` grows at about 41 GB a day, which is 16 TB over 13 months. On
   the partitioned volume that is a tenth of the line the primary would have
   carried, and it is budgeted.
3. The audit we are assessed against samples individual events behind a
   billable count. A per-account total cannot be walked back to the events that
   produced it, so the rollup cannot serve the sample.

## What this costs, and why it was accepted anyway

The quarterly report takes about forty minutes to run instead of the ninety
seconds the rollup would give, and it holds a read replica for that time. That
was raised in review, priced at one scheduled window a quarter, and accepted.
It is not an open question and does not need revisiting: the report is a batch
job nobody waits on, not an interactive query.
