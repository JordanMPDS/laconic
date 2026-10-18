# Trial funnel

`events.csv` has one row per trial started between 2026-08-01 and 2026-09-15:
the acquisition channel, the trial's first and last day (trials last 14
days), and when the user was first charged, blank if never.

Billing runs nightly at 02:00 UTC, so an upgrade made on a trial's last day is
charged after the trial has ended.

Lifecycle email starts re-engaging lapsed trial users three days after their
trial ends.
