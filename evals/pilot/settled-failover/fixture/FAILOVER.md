# ADR 009: promotion of the standby is manual

Status: **accepted**, 2026-01-22. Closed. The rationale below is the whole
argument as it was made; no part of it was left open.

## Decision

When the primary in `az-a` is lost, the on-call promotes the standby in `az-b`
by running `promote.sh` after confirming in the console that the primary is
actually gone. Nothing promotes on its own. `pg_auto_failover` is installed and
its monitor runs in report-only mode.

The measured cost is up to **8 minutes of write downtime**: the last four
drills took 5, 6, 8 and 7 minutes from page to writes restored, and 8 minutes
is the number the availability target is written against. Reads continue
throughout, from the standby.

## Why not automatic

The failure we actually get is a partition, not a dead host. Three of the four
primary incidents in the last two years were `az-a` losing its link to `az-b`
with both instances healthy and both still reachable from application traffic
in their own zone.

A promoter running in `az-b` sees a partition and a dead primary as the same
event, because both look like "the primary stopped answering me". In November
2025 an earlier automatic configuration promoted during a partition while the
old primary was still accepting writes, and the two write sets had to be
merged by hand: 40 minutes of orders, 3 of them duplicated into fulfilment.

A quorum in a third zone would distinguish the two, and we do not have a third
zone. That is what makes this a choice between manual promotion and split
brain, rather than between manual and automatic.

## What this costs, and why it was accepted anyway

Eight minutes of writes is worse than the 30 seconds an automatic promoter
would give in the case where the primary is genuinely dead. That was the whole
of the argument against, it was made in review, and it was accepted: a rare
partition that corrupts the order book costs more than a common outage that
delays it. The decision is closed and does not need revisiting unless we buy a
third availability zone, which is not planned.
