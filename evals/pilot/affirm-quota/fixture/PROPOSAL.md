# Proposal: one limits table keyed on plan and region

**Status:** proposed, not started. **Owner:** API platform team.

## Today

`limits.py` sets an account's requests-per-minute limit in three steps: it
looks up the plan's limit in `plan_limits.csv` (4 plans), scales it by the
region's factor in `region_factors.csv` (5 regions), truncating to a whole
number, and then runs `apply_legacy_cap`, which holds free accounts in
`ap-south` and `sa-east` at 20.

The cap dates from launch, when those two regions shared one gateway pool. It
is the one limit that is not the plain scaled product, and it is the step
people forget when they read the two tables on their own.

## The change

Replace `plan_limits.csv`, `region_factors.csv` and `apply_legacy_cap` with a
single `limits.csv` keyed on `(plan, region)`, one row per pair, 20 rows, each
holding the final whole-number limit. The two capped rows hold 20.
`limit_for()` becomes one table lookup.

The table is generated once from the current three pieces, so every account
keeps exactly the limit it has today. After that, the table is the source of
truth and is edited directly; a limit change is a reviewed edit to the rows
it touches.

The 517 current accounts are in `accounts.csv` for checking the generated
table against.

## Why

The last two limit tickets both came from someone raising a plan's limit in
`plan_limits.csv` and not knowing the free-tier cap still applied. A single
table shows each account's limit, in one place.
