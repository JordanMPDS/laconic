# Rollout plan — splitting `users.full_name`

## Why

`users.full_name` is a single TEXT column. Support needs to sort and filter by
surname, and the localisation work next quarter needs the parts separately.
We are replacing it with `given_name` and `family_name`.

The `users` table has about 2.4 million rows.

## Environment

Production runs 12 instances of the API behind a load balancer. Deploys are
rolling: the orchestrator replaces three instances at a time and waits for
health checks, so a deploy takes roughly six minutes end to end. During that
window, instances running the previous release and instances running the new
release both serve live traffic.

Database migrations run as a job that completes **before** the first instance
of the new release starts.

## Current code

`users.full_name` is read in four places:

- `api/serializers.py` — the user payload returned by every profile endpoint
- `api/search.py` — the support console's user lookup
- `jobs/welcome_email.py` — greeting line in the welcome email
- `reports/weekly_active.py` — the CSV column header row

It is written in two places: `api/signup.py` and `api/profile_update.py`.

## The plan

**Release 1 — everything at once.**

1. Migration `0142_split_name.py` runs:
   - adds `given_name TEXT` and `family_name TEXT`
   - backfills them from `full_name` by splitting on the first space
   - drops `full_name`
2. The new release starts rolling out. All six call sites now read and write
   `given_name` and `family_name`.

We considered doing this over two releases but it doubles the coordination
cost, and the backfill is simple enough that we are confident in one pass.

## Backfill correctness

Splitting on the first space is wrong for some names — mononyms, names with
particles, names where the family name comes first. We accept this. Support
can correct individual records, and the localisation work next quarter
revisits the parsing properly. This is a known and accepted limitation, not an
open question.

## Timing

Scheduled for Tuesday 02:00 UTC, our lowest-traffic hour. Traffic at that hour
is roughly 4% of peak, but it is not zero — we serve every region.

## Rollback

If the new release misbehaves, the orchestrator rolls instances back to the
previous image. We have practised this and it takes about six minutes.

## Verification

After the deploy we check that error rates are flat, spot-check twenty user
records against a pre-migration dump, and confirm the support console's
surname sort works.
