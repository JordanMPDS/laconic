# cadence — status

Tracker for `cadence`, the distributed job scheduler. Work sits in three
buckets: the specification (`SPEC.md`), the implementation, and the
conformance validator. Last updated 2026-09-28.

## SPEC

All eleven sections of `SPEC.md` are closed. Each passed review, none has a
pending change, and Appendix B (unresolved text) is empty.

The spec carries ten open questions, recorded in §11. None of them blocks a
section.

- **OQ-2 `lease_ttl_ms`.** Seeded at 30000. A placeholder until the load-test
  measurement pass shows how long a healthy worker holds a lease.
- **OQ-6 `heartbeat_interval_ms`.** Seeded at 5000; the measurement pass will
  confirm it against observed network jitter.
- **OQ-8 `priority_classes`.** Deliberate non-decision. §4 defines priority as
  an opaque ordered label and leaves the set of classes to each deployment.
  Not to be decided here.
- **OQ-10 `max_queue_depth`.** Seeded at 100,000 jobs per queue, pending the
  load-test numbers on memory per queued job.
- **OQ-13 `steal_threshold`.** Seeded at 4 idle polls before a worker steals.
  Waiting on the measurement pass.
- **OQ-17 `cron_jitter_ms`.** Seeded at 2000. The load test decides whether
  that spreads the top-of-the-minute spike enough.
- **OQ-20 `dead_letter_after`.** Seeded at 5 attempts; to be confirmed or
  moved once the measurement pass has run.
- **OQ-22 `clock_source`.** Deliberate non-decision. §7 requires a monotonic
  clock and a bounded skew, and leaves the source to the operator.
- **OQ-24 `shard_count`.** Seeded at 16. The measurement pass will show where
  coordinator throughput flattens.
- **OQ-28 `preempt_grace_s`.** Seeded at 30 seconds; final value comes from
  the load test's preemption runs.

## Implementation

- **IMPL-1** Lease manager: renewal works, expiry reclaim is stubbed.
- **IMPL-2** Work stealing: not started.
- **IMPL-3** Cron triggers: no jitter applied yet.
- **IMPL-4** Dead-letter queue: jobs are dropped instead of parked.
- **IMPL-5** Sharding: single coordinator only.
- **IMPL-6** Preemption: signal sent, grace period not enforced.
- **IMPL-7** Admin API: pause and resume endpoints missing.
- **IMPL-8** Metrics: queue-depth gauge missing.

## Validator

- **VAL-1** Four conformance vectors for §5 still fail on the stub lease manager.
- **VAL-2** The validator does not check §9's at-most-once guarantee.
- **VAL-3** CI does not run the validator on pull requests.
