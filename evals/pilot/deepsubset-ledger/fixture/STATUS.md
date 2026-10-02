# tally — status

Tracker for `tally`, the double-entry ledger service. Work sits in three
buckets: the specification (`SPEC.md`), the implementation, and the
conformance validator. Last updated 2026-09-28.

## SPEC

All twelve sections of `SPEC.md` are closed. Each passed review, none has a
pending change, and Appendix C (unresolved text) is empty.

The spec carries ten open questions, recorded in §12. None of them blocks a
section.

- **OQ-3 `posting_batch_size`.** Seeded at 500 postings per commit. The
  number is a placeholder until the load-test measurement pass shows where
  commit latency bends.
- **OQ-7 `idempotency_window_s`.** Seeded at 86400. Keep it until the
  measurement pass reports how long clients actually retry.
- **OQ-9 `rounding_mode`.** Deliberate non-decision. Rounding is the
  deployer's to set per jurisdiction, and §6 says so in as many words. Not
  to be decided here.
- **OQ-11 `reconcile_interval_s`.** Seeded at 300 seconds; the load test
  will say whether reconciliation keeps up at that interval.
- **OQ-14 `hold_expiry_h`.** Seeded at 72 hours. Waiting on the measurement
  pass for the real distribution of authorisation-to-capture times.
- **OQ-18 `snapshot_every_n`.** Seeded at one balance snapshot per 10,000
  entries, pending the load-test numbers on replay cost.
- **OQ-21 `fx_quote_ttl_s`.** Seeded at 30 seconds. To be confirmed or moved
  once the measurement pass has run.
- **OQ-25 `max_entries_per_txn`.** Seeded at 64 entries. The load test
  decides whether that ceiling ever binds.
- **OQ-27 `archive_backend`.** Deliberate non-decision. The spec defines the
  archive interface in §10 and leaves the backend to the operator.
- **OQ-30 `retry_backoff_ms`.** Seeded at 250 ms doubling to 8 s; final
  values come from the measurement pass.

## Implementation

- **IMPL-1** Posting engine: multi-currency postings are not written yet.
- **IMPL-2** Holds: expiry sweeper is stubbed.
- **IMPL-3** Reconciliation job: runs, but has no alerting.
- **IMPL-4** Snapshots: writer done, replay from snapshot not done.
- **IMPL-5** FX quotes: client exists, no cache.
- **IMPL-6** Idempotency store: in-memory only; needs the Postgres table.
- **IMPL-7** Archive interface: no adapter yet.
- **IMPL-8** Metrics: posting latency histogram missing.

## Validator

- **VAL-1** Three conformance vectors for §8 still fail on the stub engine.
- **VAL-2** The validator does not check §11's audit-trail ordering.
- **VAL-3** CI does not run the validator on pull requests.
