# Public API rate limits: observe mode, then enforce mode

Owner: api-platform. Reviewers: SRE (api), developer relations, support.
Status: observe mode approved, 2026-11-05.

The public API has no per-key limit today, so one key can take the whole
cluster, and twice this quarter a single customer's retry loop did. The new
limiter, `quota-gate`, runs as a sidecar on each of the 24 API gateway nodes
and counts requests per API key in the shared Redis cluster `rl-redis-3`. The
default limit is 600 requests a minute per key, with a burst of 100. It goes
live in two modes, observe and then enforce, and enforcement does not start
until observe mode has passed.

## Mode 1: observe

### What runs

- `quota-gate` counts every request against its key's limit. When a request
  would have been rejected, it logs the request to the stream
  `rl.would_reject` instead of rejecting it, and the request is served
  exactly as it is today.
- The job `rl_rollup` aggregates the stream every 15 minutes into the table
  `rl_would_reject_15m`, by key and endpoint, and `rl_daily_digest` mails a
  summary to the team at 03:45 UTC.
- Developer relations emails the owner of every key that would have been
  rejected on more than 1% of its requests, with the template
  `rl-heads-up-v1`, so customers can fix retry loops before anything is
  enforced.

No request is rejected in this mode. If a limit were set wrong, nobody would
be refused because of it.

### Exit criteria

All of these must hold before enforce mode starts:

1. 21 days of observe data, including one month-end billing peak.
2. Under 0.5% of keys would have been rejected on more than 1% of their
   requests.
3. `quota-gate` adds under 2 ms to the gateway's p99 latency.
4. Redis CPU stays under 60% at peak.

### Alerts

- `API-150`: `quota-gate` p99 overhead above 3 ms for 10 minutes.
- `API-151`: Redis error rate above 0.1%.

Both page `#api-oncall`. The board `rl-observe-board` in Grafana shows
would-reject counts by tier.

## Mode 2: enforce

### What runs

1. **Tier by tier.** The flag `ratelimit.enforce` turns on for the free tier
   first, then paid, then enterprise, one week apart.
2. **Rejection.** A request over its limit gets HTTP 429 with a Retry-After
   header, and the client is expected to back off.
3. **Exceptions.** Keys with a signed exception get custom limits, listed in
   `rl_exceptions.yaml`. Requests for one go through the ticket queue
   `DEVREL-88`.

Rollback is turning `ratelimit.enforce` off for a tier, which returns it to
observe mode within a minute.

### Exit criteria

Enforcement is done when every tier has enforced for 14 days, 429s are under
0.3% of all requests, and no escalation about a wrongly rejected key is open.

### The fail-open caveat

**Observe mode undercounts would-be rejections at peak, so its figures are a
floor, not a forecast.** The sidecar fails open: when Redis is slow to answer,
`quota-gate` serves the request without counting it, so that the limiter can
never take the API down. Redis is slowest at peak, and peak is when keys hit
their limits, so the uncounted requests cluster exactly where the rejections
would be. In the two-day pilot, 8% of month-end requests went uncounted. The
0.5% exit criterion therefore says little about month-end, and the first
month-end under enforcement is the first real measurement of how many
customers the limits refuse. That is why enterprise is enabled last, and why
on-call is doubled for the first month-end after it.

### Alerts

- `API-210`: 429s above 1% of a tier's requests for 15 minutes.
- `API-211`: a key with a signed exception receives a 429.

Both page `#api-oncall` and post to `#ratelimit-rollout`.

## Timeline

| step | dates |
|---|---|
| observe mode starts | 2026-11-10 |
| month-end peak observed | 2026-11-30 |
| observe mode ends | 2026-12-01 at the earliest |
| free tier enforced | 2026-12-02 |
| paid tier enforced | 2026-12-09 |
| enterprise enforced | 2026-12-16 |
| first month-end under enforcement | 2026-12-31 |

The API change freeze runs 2026-12-20 to 2027-01-04. A tier that has not been
enforced by 2026-12-19 waits until January, under change ticket `CHG-7731`.
