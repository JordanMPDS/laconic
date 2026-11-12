# Team plan pricing: v2 to v3

Owner: monetization. Reviewers: finance, billing engineering, support.
Status: grandfather period approved, 2026-11-03.

The Team plan costs $12 per seat per month on v2, with unlimited projects.
Team v3 costs $15 per seat and adds audit logs, SSO and a 50 GB storage
allowance per seat. About 41,000 v2 seats are billed today. The change runs
in two stages, a grandfather period and then a forced migration, and the
second does not start until the first has passed.

## Stage 1: grandfather period

### What runs

- New signups and upgrades get v3 only. The price book entry is
  `team_v3_2026`, and v2's entry `team_v2_2024` is hidden from checkout.
- Existing v2 subscriptions renew unchanged. The billing service marks each
  one `grandfathered=true` in the table `billing_subscriptions`.
- A v2 customer can opt in to v3 early from the plan page. An opt-in is
  final.
- The job `plan_mix_report` runs at 04:30 UTC and writes v2 and v3 seat
  counts, conversion and churn to the table `plan_mix_daily`.

Nothing changes for a v2 customer in this stage. If v3's price were wrong,
only new customers would have paid it.

### Exit criteria

All of these must hold before stage 2 starts:

1. 60 days have passed since launch.
2. v3's new-customer conversion is within 10% relative of v2's trailing
   90-day rate.
3. Monthly churn among v3 customers is no higher than v2's 2.1%.
4. Support tickets tagged `pricing-v3` stay under 150 a week for 4
   consecutive weeks.

### Alerts

- `BIL-120`: checkout errors on v3 above 0.5% for 15 minutes.
- `BIL-121`: an invoice total that differs between `invoice-svc` and the
  ledger.

Both page `#billing-oncall`.

## Stage 2: forced migration

### What runs

1. **Notice.** Every remaining v2 customer is emailed 60 days ahead, through
   the campaign `mig-notice-v3`, with their new monthly total.
2. **Migration.** At each subscription's first renewal after its notice
   period, the job `migrate_v2_to_v3` moves it to v3, in batches of 2,000
   subscriptions a night.
3. **Bridge credit.** A customer whose bill rises by more than 30% gets the
   difference back as a credit for 3 months, through the coupon
   `V3-BRIDGE`.

Accounts on a custom quote, marked by `quote_override`, are outside both
stages and are handled by their account manager.

### Exit criteria

The migration is done when no v2 subscription remains and net revenue
retention for migrated accounts is at or above 98% after 90 days.

### The annual-contract caveat

**The migration reaches an annual contract only at its renewal, and 38% of
v2 seats are on annual contracts.** An annual contract fixes its price for
its term, and moving it mid-term would breach the contract. So those seats
move on their renewal dates, which for some fall 11 months after the
migration starts, and the migration finishes about a year after it begins,
not 60 days. The same split runs through the numbers: the first two
quarters' revenue uplift comes from monthly seats only, and the 90-day
retention figure in the exit criteria describes monthly customers alone
until the annual renewals arrive. Finance's forecast for those quarters
counts monthly seats only.

### Alerts

- `BIL-210`: migration batch failures above 1% of a night's batch.
- `BIL-215`: churn among migrated accounts above 4% in any 30 days.

Both page `#billing-oncall` and post to `#team-plan-rollout`.

## Timeline

| step | dates |
|---|---|
| v3 launch, grandfather period starts | 2026-11-17 |
| grandfather period ends | 2027-01-16 at the earliest |
| notices sent | 2027-01-18 |
| first migrations | 2027-03-19 |
| last monthly subscription migrated | about 2027-04-18 |
| last annual contract migrated | about 2028-03 |

The billing freeze for the fiscal year-end runs 2027-01-25 to 2027-02-08. No
notice is sent during it, so a grandfather period that ends later than
2027-01-24 pushes every date after it by two weeks.
