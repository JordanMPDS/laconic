# Proposal: one routing table keyed on service and severity

**Status:** proposed, not started. **Owner:** platform team.

## Today

`route.py` routes an alert in three steps: it looks up the owning team in
`service_owners.csv` (9 services), looks up the channel in
`severity_channels.csv` (4 severities), and then runs
`apply_payments_override`, which sends sev1 and sev2 alerts from `payments`
and `ledger` to `finance-oncall` by page instead of to billing.

The override was added after an overnight ledger outage paged nobody, because
billing's rotation is not staffed at night. It is the one route that is not
the plain pair of lookups, and it is the step people forget when they read the
two tables on their own.

## The change

Replace `service_owners.csv`, `severity_channels.csv` and
`apply_payments_override` with a single `routes.csv` keyed on
`(service, severity)`, one row per pair, 36 rows, each holding the team and
the channel. The four override rows hold `finance-oncall` and `page`.
`route()` becomes one table lookup.

The table is generated once from the current three pieces, so every alert
routes exactly as it does today. After that, the table is the source of truth
and is edited directly; a routing change is a reviewed edit to the rows it
touches.

September's 812 alerts are in `alerts_2026-09.csv` for checking the
generated table against.

## Why

Two of this quarter's missed pages came from the same pattern: someone moved
a service to a new team in `service_owners.csv` and did not know the override
still applied. A single table shows where each alert goes, in one place.
