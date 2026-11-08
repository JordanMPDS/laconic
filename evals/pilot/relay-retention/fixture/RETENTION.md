# Account deletion: soft-delete window and hard purge

Owner: identity. Reviewers: privacy, legal, SRE (data).
Status: approved, 2026-10-29. Replaces the manual deletion queue.

A user who deletes their account goes through two steps: a soft-delete
window, during which the account is hidden but recoverable, and a hard purge,
which removes it. This document defines both, and is the reference support
and legal use when a user asks what happened to their data.

## Step 1: soft-delete window

### What happens

When a user confirms deletion in settings, or support deletes an account on
their request:

- `accounts.deleted_at` is set to the current time, and nothing is removed.
- The account disappears from every product surface. All product queries read
  through the view `active_accounts`, which excludes any row with
  `deleted_at` set.
- Login is refused with "This account has been deleted", and every session
  token is revoked through `session-revoke`.
- Marketing and notification email stop; the account is added to the
  suppression list `email_suppress`.
- Any pending data-export link expires.

### Duration

30 days from `deleted_at`. The window exists because about 4% of deletions
are reversed, most within a week, and because support needs a way to undo
deletions made by an attacker who took over an account.

### Restoring

Support restores an account during the window with
`acctctl restore <account_id>`, which clears `deleted_at`. The user then logs
in with their existing password; sessions are not restored. A restore
requires the user to pass the identity check in runbook `ID-RB-12`. After the
window, restore is impossible.

### What the window guarantees

During the window the account's data is complete and unchanged, and visible
to no one but support and the jobs below.

## Step 2: hard purge

### What runs

The job `purge_accounts` runs nightly at 02:30 UTC.

1. It selects accounts whose `deleted_at` is more than 30 days old, up to
   5,000 a night.
2. It deletes the account's rows from 14 tables in dependency order, children
   first, ending with `accounts` itself. The order is in `purge_order.yaml`.
3. It tags the account's objects in the bucket `user-media-prod` with
   `purge=1`; a bucket lifecycle rule deletes tagged objects within 24 hours.
4. It writes a tombstone to `purge_ledger`: a hash of the account id, the
   purge time and the list of tables cleared. The ledger keeps no personal
   data and is kept for 7 years for audit.

A failed account is retried on the next three nights. A fourth failure raises
alert `PRV-104`, which pages `#identity-oncall` and opens a privacy ticket.

### Verification

The job `purge_verify` runs at 04:00 UTC and checks, for every account
purged that night, that none of the 14 tables holds a row for it and that the
tombstone exists. A mismatch raises `PRV-105`.

### What a purge guarantees, and what it does not

A purged account is gone from the live database and from object storage
within 24 hours of the purge, and it cannot be restored.

**Backups are not purged.** Nightly database snapshots are kept for 35 days
and are never rewritten. A purged account therefore still exists in backups
for up to 35 days after its purge, which is up to 65 days after the user
asked for deletion. When legal confirms an erasure request, the date it gives
the user is the backup expiry, not the purge date. And because restoring a
backup would bring purged accounts back, the restore runbook `DB-RB-03`
replays `purge_ledger` against the restored database before it takes any
traffic.

## Metrics

- Deletions per day: about 1,900, peaking after price changes.
- Restores per day: about 75.
- Purge backlog: accounts past 30 days and not yet purged. Expected 0; alert
  `PRV-110` above 10,000.

Dashboard: "Account deletion" in Grafana, folder `identity`.

## Rollout

| step | date |
|---|---|
| soft-delete live for settings deletions | 2026-11-12 |
| support tooling (`acctctl restore`) | 2026-11-12 |
| first purge run, accounts deleted before 2026-10-01 | 2026-11-19 |
| manual deletion queue retired | 2026-12-03 |

Accounts deleted through the old manual queue before 2026-11-12 have no
`deleted_at`; a one-off migration sets it to their queue date, so the first
purge run clears the old backlog of about 61,000 accounts over 13 nights at
5,000 a night.
