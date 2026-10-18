# Incident 2026-08-21: checkout 500s, 14:02–14:47 UTC

Severity 1. Written up same day; timeline reconstructed from the deploy log,
the migration log and Grafana.

## Timeline

| Time (UTC) | Event |
| --- | --- |
| 14:02 | Release `v412` starts by publishing its config bundle, while all four instances still run `v411`. 500s on `POST /checkout` begin at once. Error rate 100%. |
| 14:05 | Migration `0042_add_settlement_currency` runs, the `v412` release job's second step, as designed. |
| 14:06 | The release job starts replacing instances with `v412`, one at a time. |
| 14:09 | Paged. Two of four instances now on `v412`; error rate down to 50%. On-call pauses the release. |
| 14:14 | On-call identifies the config value `PAYMENTS_SETTLEMENT_MODE` changed from `legacy` to `split` in the `v412` config bundle. |
| 14:21 | Config reverted to `legacy` in the running instances. **Error rate does not recover.** Holds at 50%. |
| 14:33 | Attempt to roll back the release to `v411`. Instances that come up on `v411` also 500. Error rate back to 100%. |
| 14:41 | Root cause understood. Release resumed forward to `v412`, config left at `legacy`. |
| 14:47 | All four instances on `v412`. Error rate 0%. |

## What broke

`v412` changed `PAYMENTS_SETTLEMENT_MODE` from `legacy` to `split`. Under
`split`, `chargeOrder()` writes two ledger rows per order instead of one. In
either mode, `v412` writes `settlement_currency` on every ledger row. The
handler was shipped correct for `split`.

The 500s at 14:02 are the config change. The release job publishes the config
bundle before it replaces any instance, so all four instances were running
`v411` code with `v412`'s config. `v411` does not know the `split` value, and
its `assertSettlementMode()` throws on any value it does not recognise. That is
the trigger, and it is what on-call correctly identified at 14:14. Each
instance the release replaced with `v412` stopped failing, which is why the
error rate had fallen to 50% by 14:09.

## Why reverting the config did not fix it

Migration `0042` ran at 14:05, three minutes after the errors started and
sixteen minutes before the config was reverted. In one transaction it adds the
column, fills it on the rows already in the table, and then requires it:

```sql
ALTER TABLE ledger_entries ADD COLUMN settlement_currency char(3);
UPDATE ledger_entries SET settlement_currency = 'USD';
ALTER TABLE ledger_entries ALTER COLUMN settlement_currency SET NOT NULL;
```

No default, and `NOT NULL`. Every insert into `ledger_entries` from that moment
must supply the column.

`v411`'s `chargeOrder()` does not write `settlement_currency` — the column did
not exist when it was built. So from 14:05 onward, reverting to `legacy` mode
put the old insert path back in service on the two `v411` instances, against a
schema that rejects it, and their checkouts failed on a not-null violation
instead of on the mode assertion. The error changed; the error rate did not.
The same reasoning explains 14:33: rolling the release back to `v411` could not
work either, for exactly this reason.

**The config change is the trigger. The migration is what made it
unrecoverable by rollback.** Either alone would have been a short incident: the
config change alone is fixed by the 14:21 revert, and the migration alone fails
only the instances still on `v411`, until the release replaces them.

## The forward fix

Rolling forward. `v412` writes `settlement_currency` in either mode, so at
14:41 the release was resumed instead of reversed, with the config left at
`legacy`. Once all four instances were on `v412`, no insert omitted the column.

## Ruled out

- Database CPU and connections. Both flat across the window.
- The payment provider. Their status page is clean and our provider-side
  latency did not move.
- The 14:05 spike in `pg_stat_activity`. That is the migration itself taking
  the ACCESS EXCLUSIVE lock for 1.2 seconds.
- Load. Traffic was within a normal Friday band throughout.

## Action items

1. A migration that adds a `NOT NULL` column without a default must not run in
   the same release as the code that first populates it. Expand and contract.
2. The release job publishes the config bundle before any instance runs the
   new code, which is what exposed `v411` to `split`. Publish it after the last
   instance is replaced.
3. `assertSettlementMode()` should treat an unknown mode as `legacy` and warn,
   not throw.
