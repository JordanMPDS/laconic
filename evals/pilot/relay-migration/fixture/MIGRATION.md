# Orders store migration: legacy Postgres to orders-v2

Owner: commerce-platform. Reviewers: DBA team, SRE (commerce).
Status: dual-write approved, 2026-11-02.

The orders service stores every order in the legacy Postgres cluster
`pg-orders-1`, a single primary with two replicas, now at 4.1 TB and 78% of
its write capacity at the November peak. The new store, orders-v2, is a
sharded cluster keyed on `customer_id`. The move happens in two phases, a
dual-write phase and a cutover, and the second does not start until the first
has passed.

## Phase 1: dual-write

### What runs

The orders service keeps writing every create, update and cancel to the
legacy store, and every read still comes from legacy. Each write also goes to
orders-v2, asynchronously, through an outbox:

- The service writes the order and an outbox row in one legacy transaction;
  the outbox table is `orders_outbox`.
- The worker `outbox-relay` reads `orders_outbox` in commit order and applies
  each row to orders-v2. It runs 6 replicas and is idempotent on
  `(order_id, version)`.
- Historical orders are copied by the backfill job `backfill_orders_v2`, which
  runs 01:00 to 05:00 UTC in batches of 50,000 rows, oldest first. At the
  current rate it finishes in 11 nights.

Nothing reads from orders-v2 in this phase. If it is wrong, no customer can
see it.

### Consistency checking

The checker `order-diff` runs hourly. It compares every order touched in the
last 24 hours, plus a 1% random sample of all orders, field by field between
the two stores, and writes mismatches to `order_diff_results`.

### Exit criteria

All of these must hold before the cutover starts:

1. The backfill is complete: every order in legacy exists in orders-v2.
2. `order-diff` mismatch rate under 0.01% for 3 consecutive days.
3. `outbox-relay` lag p99 under 2 seconds for the same 3 days.
4. A full-table checksum comparison, run once after the backfill finishes,
   matches. The hourly checker only samples old orders, so this is the one
   check that covers all of them.

### Alerts

- `ORD-310`: outbox lag p99 above 2 seconds for 10 minutes.
- `ORD-311`: `order-diff` mismatch rate above 0.01% in any hourly run.
- `ORD-315`: `outbox-relay` replicas below 4.

All page `#commerce-oncall`. Dashboard: "Orders migration" in Grafana.

## Phase 2: cutover

### What runs

Reads move to orders-v2 first, then writes to legacy stop.

1. **Read ramp.** The flag `orders.read_from_v2` moves reads to orders-v2 in
   steps of 1%, 10%, 50% and 100% of requests, one step a day, holding a step
   if the error rate or p99 read latency moves. Writes still go to both
   stores throughout the ramp.
2. **Soak.** Reads stay at 100% on orders-v2 for 48 hours with the service's
   error budget intact.
3. **Write stop.** The flag `orders.write_legacy` is turned off. From then on
   orders-v2 is the only store receiving writes, and `outbox-relay` is scaled
   to zero.
4. **Retirement.** `pg-orders-1` stays up read-only for 30 days for audit
   queries, then is decommissioned under change ticket `CHG-4471`.

### Exit criteria

The cutover is done when the write stop has held for 7 days with no
`ORD-4xx` incident, and the order-history page's p99 latency is at or under
its legacy figure of 180 ms.

### Rollback

During the read ramp and the soak, rollback is turning
`orders.read_from_v2` back to 0. It takes effect within a minute, and because
legacy has kept receiving every write, nothing is lost.

**Rollback ends at the write stop.** Once `orders.write_legacy` is off,
legacy no longer receives writes, and there is no sync from orders-v2 back to
legacy. Falling back to legacy after that point would lose every order
written since the flag was turned off. The read ramp is reversible; the write
stop is one-way, which is why it waits for the 48-hour soak and needs sign-off
from the DBA lead and the commerce director.

### Alerts

- `ORD-410`: orders-v2 read error rate above 0.5% for 5 minutes.
- `ORD-411`: order-history p99 above 250 ms for 15 minutes.

Both page `#commerce-oncall` and post to `#orders-migration`.

## Timeline

| step | dates |
|---|---|
| dual-write starts | 2026-11-09 |
| backfill complete | about 2026-11-20 |
| checksum comparison | 2026-11-21 |
| read ramp | 2026-11-24 to 2026-11-27 |
| soak | to 2026-11-29 |
| write stop | 2026-11-30, needs sign-off |
| legacy decommissioned | 2026-12-30 |

The commerce code freeze runs 2026-12-01 to 2027-01-05. If the write stop
misses 2026-11-30 it waits until January, and dual-write continues through
the freeze at its current cost of 6 relay replicas and the outbox's write
load on legacy.
