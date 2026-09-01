# Incident 2026-08-21: checkout 500s, 14:02–14:47 UTC

Severity 1. Written up same day; timeline reconstructed from the deploy log,
the migration log and Grafana.

## Timeline

| Time (UTC) | Event |
| --- | --- |
| 13:58 | Release `v412` starts rolling out. Four instances, one at a time. |
| 14:02 | First 500s on `POST /checkout`. Error rate 0% to 34% in ninety seconds. |
| 14:05 | Migration `0042_add_settlement_currency` runs, triggered by the `v412` release job as designed. |
| 14:09 | Paged. Error rate 61% — three of four instances now on `v412`. |
| 14:14 | On-call identifies the config value `PAYMENTS_SETTLEMENT_MODE` changed from `legacy` to `split` in the `v412` config bundle. |
| 14:21 | Config reverted to `legacy` in the running instances. **Error rate does not recover.** Holds at 58%. |
| 14:33 | Attempt to roll back the release to `v411`. Instances that come up on `v411` also 500. |
| 14:41 | Root cause understood. Forward fix written. |
| 14:47 | Forward fix `v413` deployed. Error rate to 0% within two minutes. |

## What broke

`v412` changed `PAYMENTS_SETTLEMENT_MODE` from `legacy` to `split`. Under
`split`, `chargeOrder()` writes two ledger rows per order instead of one and
requires each to carry a settlement currency. The handler was shipped correct
for `split`.

The 500s at 14:02 are the config change: three instances were still running
`v411` code, which does not know the `split` value, and its
`assertSettlementMode()` throws on any value it does not recognise. That is the
trigger, and it is what on-call correctly identified at 14:14.

## Why reverting the config did not fix it

Migration `0042` ran at 14:05, three minutes after the errors started and
sixteen minutes before the config was reverted. It adds:

```sql
ALTER TABLE ledger_entries
  ADD COLUMN settlement_currency char(3) NOT NULL;
```

No default, and `NOT NULL`. Every insert into `ledger_entries` from that moment
must supply the column.

`v411`'s `chargeOrder()` does not write `settlement_currency` — the column did
not exist when it was built. So from 14:05 onward, reverting to `legacy` mode
put the old insert path back in service against a schema that rejects it, and
every checkout failed on a not-null violation instead of on the mode assertion.
The error changed; the error rate did not. The same reasoning explains 14:33:
rolling the release back to `v411` could not work either, for exactly this
reason.

**The config change is the trigger. The migration is what made it
unrecoverable by rollback.** Either alone would have been a short incident.

## The forward fix

`v413` kept `split` mode and the new column, and added the backfill the
migration should have carried:

```sql
ALTER TABLE ledger_entries ALTER COLUMN settlement_currency DROP NOT NULL;
UPDATE ledger_entries SET settlement_currency = 'USD' WHERE settlement_currency IS NULL;
```

then re-applied `NOT NULL` once all instances were on `v413`.

## Ruled out

- Database CPU and connections. Both flat across the window.
- The payment provider. Their status page is clean and our provider-side
  latency did not move.
- The 14:05 spike in `pg_stat_activity`. That is the migration itself taking
  the ACCESS EXCLUSIVE lock for 1.2 seconds.
- Load. Traffic was within a normal Thursday band throughout.

## Action items

1. A migration that adds a `NOT NULL` column without a default must not run in
   the same release as the code that first populates it. Expand and contract.
2. The release job runs migrations after the first instance is healthy, which
   is what put the schema change inside the rollback window. Move it.
3. `assertSettlementMode()` should treat an unknown mode as `legacy` and warn,
   not throw.
