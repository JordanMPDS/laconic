# portico — status

Tracker for `portico`, the API gateway. Work sits in three buckets: the
specification (`SPEC.md`), the implementation, and the conformance
validator. Last updated 2026-09-28.

## SPEC

All ten sections of `SPEC.md` are closed. Each passed review, none has a
pending change, and Appendix D (unresolved text) is empty.

The spec carries ten open questions, recorded in §10. None of them blocks a
section.

- **OQ-4 `conn_pool_size`.** Seeded at 128 upstream connections per host. A
  placeholder until the load-test measurement pass shows where pool waits
  begin.
- **OQ-5 `idle_timeout_s`.** Seeded at 60; the measurement pass will confirm
  it against observed client keep-alive behaviour.
- **OQ-12 `rate_burst`.** Seeded at twice the sustained rate. Waiting on the
  measurement pass.
- **OQ-15 `cache_ttl_s`.** Seeded at 10 seconds, pending the load-test
  numbers on hit rate against staleness complaints.
- **OQ-16 `auth_provider`.** Deliberate non-decision. §3 defines the token
  validation interface and leaves the identity provider to each deployment.
  Not to be decided here.
- **OQ-19 `circuit_open_ms`.** Seeded at 15000. The load test decides
  whether upstreams recover inside that window.
- **OQ-23 `max_header_kb`.** Seeded at 16 KB; to be confirmed or moved once
  the measurement pass has run.
- **OQ-26 `retry_budget_pct`.** Seeded at 10% of requests. The measurement
  pass will show whether that budget amplifies an outage.
- **OQ-29 `log_sink`.** Deliberate non-decision. §8 defines the access-log
  record and leaves where it is shipped to the operator.
- **OQ-31 `tls_session_cache`.** Seeded at 20,000 sessions; final value comes
  from the load test's handshake runs.

## Implementation

- **IMPL-1** Connection pooling: per-host pools work, no eviction.
- **IMPL-2** Rate limiter: sustained rate enforced, burst not.
- **IMPL-3** Response cache: not started.
- **IMPL-4** Circuit breaker: opens, never half-opens.
- **IMPL-5** Header limits: enforced only on requests, not responses.
- **IMPL-6** Retry budget: retries are unbounded.
- **IMPL-7** TLS: session resumption disabled.
- **IMPL-8** Metrics: upstream latency histogram missing.

## Validator

- **VAL-1** Two conformance vectors for §6 still fail against the stub cache.
- **VAL-2** The validator does not check §9's header-forwarding rules.
- **VAL-3** CI does not run the validator on pull requests.
