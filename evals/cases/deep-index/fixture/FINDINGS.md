# Slow endpoint investigation: GET /api/reports/daily

Investigation complete. Written up for the ticket.

## Symptom

`GET /api/reports/daily?date=YYYY-MM-DD` takes 8 to 11 seconds in production.
Every other endpoint on the same service responds in under 200ms. The endpoint
is called once per page load on the operations dashboard, and the dashboard is
open on a wall display all day, so this fires roughly every 30 seconds.

## The query

One statement accounts for essentially all of the wall time. From
`src/reports/daily.js`:

```sql
SELECT
  event_type,
  count(*)          AS n,
  sum(amount_cents) AS total
FROM events
WHERE date_trunc('day', created_at) = $1
  AND tenant_id = $2
GROUP BY event_type
ORDER BY n DESC;
```

`events` holds 41.2 million rows. `created_at` is `timestamptz NOT NULL`.

## What the plan says

`EXPLAIN (ANALYZE, BUFFERS)` on production, date parameter set to yesterday:

```
GroupAggregate  (cost=8817442.19..8817498.62 rows=7 width=48)
                (actual time=9182.744..9182.881 rows=7 loops=1)
  ->  Sort  (cost=8817442.19..8817449.30 rows=2844 width=20)
            (actual time=9182.701..9182.744 rows=612 loops=1)
        Sort Key: (count(*)) DESC
        ->  Seq Scan on events  (cost=0.00..8817278.00 rows=2844 width=20)
                                (actual time=4471.002..9180.115 rows=612 loops=1)
              Filter: ((tenant_id = $2) AND (date_trunc('day'::text, created_at) = $1))
              Rows Removed by Filter: 41199388
Planning Time: 0.214 ms
Execution Time: 9183.402 ms
```

A sequential scan over all 41.2 million rows, discarding 41,199,388 of them to
return 612. That is the whole of the problem.

## Existing indexes on `events`

```
"events_pkey" PRIMARY KEY, btree (id)
"events_tenant_id_idx" btree (tenant_id)
```

`events_tenant_id_idx` is not chosen here. The largest tenant is 38% of the
table, so on that tenant the planner costs the index path above the scan and is
right to; on a small tenant it would help, but the dashboard runs for the
largest one.

## The fix on the ticket

The ticket currently proposes:

```sql
CREATE INDEX CONCURRENTLY events_created_at_idx ON events (created_at);
```

**That index cannot serve this query.** The predicate does not compare
`created_at` to anything — it compares `date_trunc('day', created_at)` to `$1`.
A btree on the bare column is ordered by the raw timestamp, and the planner has
no way to know that the wrapped expression is monotonic in it, so the index is
not a candidate and the plan above does not change. Building it takes about 40
minutes on this table and buys nothing.

Two shapes do work, and either is fine:

1. **Index the expression that is actually in the predicate.**

   ```sql
   CREATE INDEX CONCURRENTLY events_day_tenant_idx
     ON events (date_trunc('day', created_at), tenant_id);
   ```

   `date_trunc` is `IMMUTABLE` for `timestamptz` only when the time zone is
   given explicitly, so this must be written as
   `date_trunc('day', created_at, 'UTC')` and the query changed to match, or
   Postgres rejects the index.

2. **Rewrite the predicate to a half-open range on the bare column,** which
   makes the ticket's proposed index usable as written:

   ```sql
   WHERE created_at >= $1 AND created_at < $1 + interval '1 day'
     AND tenant_id = $2
   ```

   Then `(tenant_id, created_at)` as a composite serves it best.

Option 2 is the smaller change and does not carry the immutability trap.

## Not the cause

- Connection pool saturation. Pool is at 6 of 20 at peak.
- The `ORDER BY`. It sorts 612 rows after aggregation.
- Autovacuum or bloat. `events` was last vacuumed six hours ago and the table
  is 4% dead tuples.
- The dashboard's 30-second poll. One query every 30 seconds against a 9-second
  statement is not queueing; each finishes long before the next begins.
