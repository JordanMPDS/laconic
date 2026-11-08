# Disaster recovery plan — proposal

## What we have to survive

Losing all of us-east-1, where everything runs today. Our enterprise contracts
commit us to losing **at most 15 minutes of orders** in a regional outage, and
to serving again within **four hours**.

## Current state

The orders database is PostgreSQL on RDS in us-east-1, Multi-AZ. Automated
snapshots run daily at 03:00 UTC and are kept for 14 days. Point-in-time
recovery is enabled, so we can restore to any moment in the last 14 days to
within about five minutes. The snapshots and the transaction logs that
point-in-time recovery replays are both stored in us-east-1.

## Proposal

1. A scheduled job copies each night's snapshot to us-west-2 once it
   completes, re-encrypted with a us-west-2 KMS key.
2. In a regional outage, restore the newest us-west-2 copy into a new
   instance, then point `orders-db.internal` (TTL 60 seconds) at it.
3. Run the restore as a timed drill every quarter. The last manual restore of
   a snapshot this size took 70 minutes end to end.

## Cost

The copies add about $180 a month of storage in us-west-2. A standing
cross-region replica would be about $2,100 a month, which we would rather not
pay.
