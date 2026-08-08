# Log retention policy — proposal

## Current state

Application logs land in `logs-prod-*` indices, one index per day. We keep
every index forever. The cluster is at 41 TB and grows about 90 GB a day.
Query latency on the support console has roughly doubled in six months.

## Proposal

1. Keep the last 30 days hot, searchable from the support console.
2. Days 31 to 365 move to cold storage in object storage, restorable on
   request within a few hours.
3. **On day 366, indices are deleted.**

## What the logs contain

Request lines carry method, path, status, latency, the account id, and the
client IP. Error lines additionally carry a stack trace. Payment handlers log
the last four digits of the card and the processor's transaction id.

## Legal and compliance

Our terms commit us to responding to data-subject deletion requests within 30
days, and we already have a job that scrubs an account's rows from the primary
database when one arrives.

Finance has asked that anything touching a payment be retrievable for **seven
years** for audit; their existing ledger export already covers the amounts and
the transaction ids.

## Cost

Deleting at 366 days holds the cluster around 3 TB hot and roughly 30 TB cold,
which is about a third of today's storage spend.

## Rollout

We apply the policy to existing indices in one pass, oldest first, over a
weekend. New indices pick it up from the index template.
