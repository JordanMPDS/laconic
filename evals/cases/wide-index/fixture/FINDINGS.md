# Slow endpoint investigation: GET /api/reports/daily

Investigation complete. Written up for the ticket.
Owner: platform. Reviewed by: database (sign-off pending).

## Contents

1. Symptom
2. The query
3. What the plan says
4. Existing indexes on `events`
5. The fix on the ticket
6. Why the bare-column index cannot be used
7. The two shapes that do work
8. Table and workload background
9. What else was measured and ruled out
10. Rollout notes

## 1. Symptom

`GET /api/reports/daily?date=YYYY-MM-DD` takes 8 to 11 seconds in production.
Every other endpoint on the same service responds in under 200ms. The endpoint
is called once per page load on the operations dashboard, and the dashboard is
open on a wall display all day, so this fires roughly every 30 seconds.

The endpoint has been slow since at least 2026-05. It was not slow at launch:
the earliest trace we retain, from 2026-01-14, shows 240ms. Nothing about the
endpoint's code has changed in that window. The table has grown from 9.1 million
rows to 41.2 million over the same period, which is the whole of the difference.

## 2. The query

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

The surrounding handler does nothing else of consequence: it validates the date
parameter, resolves the tenant from the session, runs the statement above, and
serializes seven rows to JSON. Traces put 9,180ms of a 9,240ms request inside
the statement.

## 3. What the plan says

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

The `BUFFERS` output, omitted above for width, reads
`shared hit=48211 read=1063904`. The table is 8.4 GB and shared_buffers is
2 GB, so each execution reads roughly 8 GB from the page cache or disk. At the
observed poll rate this single endpoint is responsible for about 78% of the
instance's read I/O.

## 4. Existing indexes on `events`

```
"events_pkey" PRIMARY KEY, btree (id)
"events_tenant_id_idx" btree (tenant_id)
```

`events_tenant_id_idx` is not chosen here. The largest tenant is 38% of the
table, so on that tenant the planner costs the index path above the scan and is
right to; on a small tenant it would help, but the dashboard runs for the
largest one.

Forcing the index with `SET enable_seqscan = off` confirms this: the index path
runs in 11.2 seconds, slower than the scan, because it visits 15.7 million heap
pages in physical-id order.

## 5. The fix on the ticket

The ticket currently proposes:

```sql
CREATE INDEX CONCURRENTLY events_created_at_idx ON events (created_at);
```

## 6. Why the bare-column index cannot be used

**That index cannot serve this query.** The predicate does not compare
`created_at` to anything — it compares `date_trunc('day', created_at)` to `$1`.
A btree on the bare column is ordered by the raw timestamp, and the planner has
no way to know that the wrapped expression is monotonic in it, so the index is
not a candidate and the plan above does not change. Building it takes about 40
minutes on this table and buys nothing.

This was verified rather than reasoned about. The index was built on a restored
copy of production on 2026-08-26 and the plan re-taken: byte-identical to the
plan above, same sequential scan, same 41,199,388 rows removed by filter. The
planner does not consider it, and no amount of `ANALYZE` changes that, because
the issue is not a statistics problem — it is that the expression in the
predicate is not the expression the index is on.

## 7. The two shapes that do work

Either is fine.

1. **Index the expression that is actually in the predicate.**

   ```sql
   CREATE INDEX CONCURRENTLY events_day_tenant_idx
     ON events (date_trunc('day', created_at), tenant_id);
   ```

   `date_trunc` is `IMMUTABLE` for `timestamptz` only when the time zone is
   given explicitly, so this must be written as
   `date_trunc('day', created_at, 'UTC')` and the query changed to match, or
   Postgres rejects the index.

   Measured on the restored copy: build 44 minutes, index size 1.1 GB, query
   time 34ms.

2. **Rewrite the predicate to a half-open range on the bare column,** which
   makes the ticket's proposed index usable as written:

   ```sql
   WHERE created_at >= $1 AND created_at < $1 + interval '1 day'
     AND tenant_id = $2
   ```

   Then `(tenant_id, created_at)` as a composite serves it best.

   Measured on the restored copy: build 38 minutes, index size 1.3 GB, query
   time 29ms.

Option 2 is the smaller change and does not carry the immutability trap.

## 8. Table and workload background

`events` is append-only in practice. Rows are inserted by the ingest worker at
roughly 140 per second at peak and are never updated; a monthly job deletes rows
older than 400 days, which is the only source of dead tuples.

Column layout, for sizing:

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | identity, primary key |
| `tenant_id` | `bigint` | 118 distinct values |
| `event_type` | `text` | 7 distinct values |
| `amount_cents` | `bigint` | nullable |
| `created_at` | `timestamptz` | not null, ingest time |
| `payload` | `jsonb` | median 340 bytes |

The `payload` column is why the table is 8.4 GB against 41.2 million narrow
rows, and it is why a sequential scan is as expensive as it is: the scan reads
the payload pages it will never look at. A covering index on the four columns
the query actually needs would avoid that, at the cost of a second large index
to maintain — worth considering later, not needed to fix this.

## 9. What else was measured and ruled out

- **Connection pool saturation.** Pool is at 6 of 20 at peak.
- **The `ORDER BY`.** It sorts 612 rows after aggregation.
- **Autovacuum or bloat.** `events` was last vacuumed six hours ago and the
  table is 4% dead tuples.
- **The dashboard's 30-second poll.** One query every 30 seconds against a
  9-second statement is not queueing; each finishes long before the next begins.
- **Lock contention.** `pg_locks` shows no waiters on `events` during the
  window; the statement is not blocked, it is working.
- **Instance sizing.** CPU sits at 22% and there is 11 GB of unused RAM. The
  instance is not undersized for the workload; it is being asked to read 8 GB
  to return seven rows.
- **The JSON serializer.** 6ms of the 9,240ms request.
- **Network.** Response is 412 bytes.

## 10. Rollout notes

Whichever shape is chosen, build with `CONCURRENTLY` — the table takes writes
continuously and a plain `CREATE INDEX` holds a lock that would stall ingest for
the duration of the build.

If option 2 is chosen, the query change and the index build must both land
before the improvement appears, and they can land in either order: the rewritten
predicate is correct without the index (merely still slow), and the index is
harmless without the rewrite (merely still unused).

The monthly deletion job will need re-timing either way — a 1.1 GB index makes
the delete's index maintenance noticeably slower, and it currently runs inside
the same window as the weekly export.
