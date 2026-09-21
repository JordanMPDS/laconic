# ADR 009: promotion of the standby is automatic

Status: **accepted**, 2026-01-22. Closed. The rationale below is the whole
argument as it was made; no part of it was left open.

## Decision

When the primary in `az-a` is lost, `pg_auto_failover` promotes the standby in
`az-b` on its own. Nobody is paged to run anything, and `promote.sh` is kept
only as the manual fallback for a promotion the monitor declines. The monitor
runs in active mode with its quorum member in `az-c`.

The measured cost is up to **30 seconds of write downtime**: the last four
drills took 18, 24, 30 and 22 seconds from fault injection to writes restored,
and 30 seconds is the number the availability target is written against. Reads
continue throughout, from the standby.

## Why not manual

The failure we actually get is a dead host, not a partition. Seven of the eight
primary incidents in the last two years were the instance itself going away,
and in every one of them the on-call took between four and eleven minutes to
reach a console and confirm what the monitor already knew.

The partition case is the one manual promotion is usually argued for, and the
quorum member in `az-c` settles it: a promoter that cannot reach the quorum does
not promote, so a partition between `az-a` and `az-b` leaves the old primary
serving and no second write set is created.

Split brain is therefore not the trade being made here. The trade is between
thirty seconds unattended and eight minutes of a person's reaction time, and
the third zone is what turns it into that trade.

## What this costs, and why it was accepted anyway

An automatic promoter will occasionally promote for a fault that would have
cleared on its own, and each of those costs a reseed of the demoted node. That
was raised in review, priced at about one spurious promotion a quarter, and
accepted: a reseed is planned work and a nine-minute write outage is not. The
decision is closed and does not need revisiting.
