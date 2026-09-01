# Incident 2026-08-21: checkout 500s, 14:02–14:47 UTC

Severity 1. Written up same day; timeline reconstructed from the deploy log,
the migration log and Grafana.
Incident commander: platform on-call. Review meeting: 2026-08-25.

## Contents

1. Summary
2. Impact
3. Timeline
4. What broke
5. Why reverting the config did not fix it
6. Why the release rollback did not fix it either
7. The forward fix
8. What the release job does, and why it matters here
9. Ruled out
10. What went well
11. Action items

## 1. Summary

A configuration value changed in the `v412` release broke checkout on instances
still running `v411`. A migration in the same release then made the incident
unrecoverable by either of the two rollback paths available to on-call, which is
why a 45-minute outage followed a trigger that was correctly identified inside
twelve minutes.

## 2. Impact

45 minutes of degraded checkout, peaking at 61% error rate.

| Measure | Value |
| --- | --- |
| Failed checkout attempts | 3,417 |
| Distinct affected customers | 2,890 |
| Estimated lost orders | 1,050 to 1,300 |
| Support tickets opened | 74 |
| Duplicate charges | 0 |
| Data loss | none |

No order was charged without being recorded and no ledger row was written in an
inconsistent state; the failures were clean rejections before the charge call.

## 3. Timeline

| Time (UTC) | Event |
| --- | --- |
| 13:58 | Release `v412` starts rolling out. Four instances, one at a time. |
| 14:02 | First 500s on `POST /checkout`. Error rate 0% to 34% in ninety seconds. |
| 14:05 | Migration `0042_add_settlement_currency` runs, triggered by the `v412` release job as designed. |
| 14:09 | Paged. Error rate 61% — three of four instances now on `v412`. |
| 14:14 | On-call identifies the config value `PAYMENTS_SETTLEMENT_MODE` changed from `legacy` to `split` in the `v412` config bundle. |
| 14:21 | Config reverted to `legacy` in the running instances. **Error rate does not recover.** Holds at 58%. |
| 14:26 | Second responder joins. Log search narrows the post-14:21 failures to a different exception than the pre-14:21 ones. |
| 14:33 | Attempt to roll back the release to `v411`. Instances that come up on `v411` also 500. |
| 14:37 | Migration log checked; `0042` identified as having run at 14:05. |
| 14:41 | Root cause understood. Forward fix written. |
| 14:47 | Forward fix `v413` deployed. Error rate to 0% within two minutes. |
| 15:10 | Backfill completes; `NOT NULL` re-applied. |

## 4. What broke

`v412` changed `PAYMENTS_SETTLEMENT_MODE` from `legacy` to `split`. Under
`split`, `chargeOrder()` writes two ledger rows per order instead of one and
requires each to carry a settlement currency. The handler was shipped correct
for `split`.

The 500s at 14:02 are the config change: three instances were still running
`v411` code, which does not know the `split` value, and its
`assertSettlementMode()` throws on any value it does not recognise. That is the
trigger, and it is what on-call correctly identified at 14:14.

The relevant lines, from `src/payments/charge.js` at `v411`:

```js
function assertSettlementMode(mode) {
  if (mode !== 'legacy') {
    throw new Error(`unknown settlement mode: ${mode}`);
  }
}
```

The configuration is delivered as one bundle per release, so an instance running
`v411` code picks up `v412`'s configuration as soon as the bundle is published,
which happens before the first instance is replaced. There is no per-version
configuration scoping.

## 5. Why reverting the config did not fix it

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
The error changed; the error rate did not.

This is visible in the logs and is what the second responder found at 14:26.
Before 14:21 the failures read `unknown settlement mode: split`. After 14:21
they read
`null value in column "settlement_currency" violates not-null constraint`.
Two different exceptions, one error rate, which is why the graph looked like the
revert had simply done nothing.

## 6. Why the release rollback did not fix it either

The same reasoning explains 14:33. Rolling the release back to `v411` restores
exactly the code path the config revert had already restored, against exactly
the same migrated schema. It could not work, and for the same reason.

**The config change is the trigger. The migration is what made it
unrecoverable by rollback.** Either alone would have been a short incident: the
config change alone is fixed by the 14:21 revert, and the migration alone is
harmless because `v412` populates the column.

## 7. The forward fix

`v413` kept `split` mode and the new column, and added the backfill the
migration should have carried:

```sql
ALTER TABLE ledger_entries ALTER COLUMN settlement_currency DROP NOT NULL;
UPDATE ledger_entries SET settlement_currency = 'USD' WHERE settlement_currency IS NULL;
```

then re-applied `NOT NULL` once all instances were on `v413`.

The `'USD'` default is correct for every row written before `0042`, because
`legacy` mode settles in the account currency and every account on this ledger
is USD. That will not remain true once the first non-USD account is onboarded,
which is tracked separately.

## 8. What the release job does, and why it matters here

The release job's order of operations is:

1. Publish the configuration bundle.
2. Replace the first instance and wait for its health check.
3. Run pending migrations.
4. Replace the remaining instances one at a time.

Step 1 before step 2 is what exposed `v411` instances to `v412` configuration.
Step 3 sitting between the first instance and the rest is what put a schema
change inside the window where a rollback is still the obvious response, and it
is the reason both of on-call's recovery paths were already closed by the time
they were tried.

Neither ordering is unreasonable on its own. Together they mean that for roughly
three minutes of every release, the system is in a state that neither a config
revert nor a version rollback can leave.

## 9. Ruled out

- **Database CPU and connections.** Both flat across the window.
- **The payment provider.** Their status page is clean and our provider-side
  latency did not move.
- **The 14:05 spike in `pg_stat_activity`.** That is the migration itself taking
  the ACCESS EXCLUSIVE lock for 1.2 seconds.
- **Load.** Traffic was within a normal Thursday band throughout.
- **The 14:11 cache eviction.** Coincidental; the cache repopulated in 40
  seconds and checkout does not read from it.
- **A bad instance.** All four failed identically; the two that came up on
  `v411` at 14:33 failed identically to each other.

## 10. What went well

- The trigger was correctly identified in twelve minutes from a cold page.
- The second responder's log search at 14:26 is what made the root cause
  findable; without noticing the exception had changed, the next step would
  likely have been another rollback attempt.
- No duplicate charges and no inconsistent ledger state, because the failures
  occur before the provider call rather than between the charge and the write.
- The forward fix was written, reviewed and deployed in six minutes.

## 11. Action items

1. A migration that adds a `NOT NULL` column without a default must not run in
   the same release as the code that first populates it. Expand and contract.
2. The release job runs migrations after the first instance is healthy, which
   is what put the schema change inside the rollback window. Move it.
3. `assertSettlementMode()` should treat an unknown mode as `legacy` and warn,
   not throw.
4. Scope configuration bundles per version, so a running instance does not pick
   up the next release's configuration before it picks up that release's code.
5. Add a pre-deploy check that fails the release when a migration in it adds a
   `NOT NULL` column without a default.
