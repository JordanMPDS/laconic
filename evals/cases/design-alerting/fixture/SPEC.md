# Ingest throughput governor — design

## Overview

Each tenant has a daily processing quota and a contractual minimum throughput
floor. A background job recomputes the tenant's ingest concurrency cap every
five minutes so the quota is consumed on pace across the day and the floor is
never silently missed.

## Control loop

Every five minutes, per tenant, the supervisor:

1. Reads the tenant's persisted controller state.
2. Reads the current feed metrics (arrival rate, backlog depth, processed
   count so far today).
3. Calls `govern(state, inputs)` and receives the new concurrency cap, the
   updated state, and which guardrail (if any) fired.
4. Applies the cap to the ingest workers, persists the state, and records the
   cycle.

Pseudocode:

```
every 5 minutes, for each tenant:
    state  = read_state(tenant)
    inputs = read_feed_metrics(tenant)
    result = govern(state, inputs)        # pure: no I/O inside
    apply_cap(tenant, result.cap)
    persist_state(tenant, result.state)
    if result.guardrail == "quota_exceeded":
        alert("quota exceeded", tenant)
```

## Core purity

`govern()` is a pure function: state and inputs in, decision out, no clock, no
network, no storage. The supervisor owns every read and write. The whole test
ladder stands on this property — unit tests enumerate guardrail edges, and the
simulation harness replays recorded production days through `govern()` at
thousands of cycles per second, which is only possible because the core
performs no I/O.

## Guardrails

Evaluated inside `govern()`, in priority order; the first match wins:

- **quota_exceeded** — the tenant's daily quota is spent. Cap goes to zero and
  the loop holds it there until the day rolls over.
- **feed_stale** — feed metrics are older than one cycle. The cap freezes at
  its last value; after three consecutive stale cycles the tenant falls back
  to its configured default cap.
- **cap_clamped** — the raw output left the allowed band and was clamped to
  the band edge.
- **floor_at_risk** — projected end-of-day throughput is below the
  contractual floor.
- **floor_unreachable** — the floor cannot be met even at the maximum cap;
  the controller stops chasing it and holds the maximum.
- **config_invalid** — the tenant's config fails validation. The tenant is
  served the fleet-default config until it is fixed.

## Observability

The following conditions must raise alerts:

- Supervisor heartbeat missed (the loop did not run).
- `feed_stale` persisting past three cycles.
- `quota_exceeded` (the loop is now holding the cap at zero).
- Cap pinned at a band edge for two consecutive cycles.
- Pace error above 15% for two consecutive cycles.
- `floor_at_risk`.
- `floor_unreachable`.
- `config_invalid` (the tenant is running on the fleet default).

## Rollout

One week shadowing production (computing caps, not applying them), then five
pilot tenants, then the fleet. The simulation harness must replay the shadow
week's recorded cycles and reproduce the caps the shadow run computed.
