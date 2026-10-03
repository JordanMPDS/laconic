# Ingest throughput governor — design

Status: draft for review. Owner: platform ingest team. Reviewers: tenant
operations, finance, on-call leads.

## 1. Background

Every tenant on the ingest platform buys two things in its contract: a daily
processing quota, measured in records, and a contractual minimum throughput
floor, measured in records processed by the end of the tenant's business day.
The quota is a ceiling we bill against; the floor is a commitment we owe.

Today both are managed by hand. Each tenant has a static ingest concurrency cap
that tenant operations sets once at onboarding and revisits only when a tenant
complains. The result is predictable. Tenants with bursty arrival patterns
spend their quota by mid-afternoon and are hard-stopped for the rest of the
day, and their support tickets land on tenant operations the next morning.
Tenants with slow, steady arrivals sit far under their cap while the backlog
grows, and twice last quarter a tenant missed its floor without anyone
noticing until the monthly statement went out. Finance had to issue service
credits both times.

The cap is the only lever we control. Raising it drains the backlog faster and
spends quota faster; lowering it does the opposite. The right cap therefore
changes over the day, and nobody is in a position to change it by hand every
few minutes.

## 2. Goals and non-goals

Goals:

- Spend each tenant's daily quota on pace across its business day, so that a
  tenant is not hard-stopped at 3pm by a morning burst.
- Never miss a floor silently. Either the floor is met, or the right people
  know early enough in the day to act.
- Keep the controller simple enough that a reviewer can predict its output for
  a given cycle by reading the code.
- Make every decision the controller takes reproducible offline from recorded
  inputs.

Non-goals:

- Changing what tenants are billed or how quota is metered. Metering stays in
  the billing service.
- Autoscaling the ingest worker fleet. The governor sets per-tenant caps on a
  fleet whose size is managed elsewhere.
- Predicting arrival volume. The controller reacts to what has arrived; it does
  not forecast.

## 3. Glossary

- **Cap**: the maximum number of ingest workers a tenant may hold at once.
- **Band**: the per-tenant allowed range for the cap, `[cap_min, cap_max]`,
  set in tenant config.
- **Pace**: the fraction of the daily quota the tenant should have consumed by
  now, given how far through its business day it is.
- **Pace error**: actual consumption minus paced consumption, as a fraction of
  the daily quota.
- **Floor projection**: processed count so far plus the current processing
  rate extrapolated to the end of the business day.
- **Cycle**: one five-minute evaluation of one tenant.
- **Fleet default**: the configuration every tenant falls back to when its own
  config cannot be used.

## 4. Control loop

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

Tenants are evaluated independently. A failure evaluating one tenant is logged
and skipped; it never blocks the others in the same cycle.

## 5. Core purity

`govern()` is a pure function: state and inputs in, decision out, no clock, no
network, no storage. The supervisor owns every read and write. The whole test
ladder stands on this property — unit tests enumerate guardrail edges, and the
simulation harness replays recorded production days through `govern()` at
thousands of cycles per second, which is only possible because the core
performs no I/O.

The current time is passed in as part of `inputs`, never read inside the
function. So is the tenant's config. If a future change needs anything else
from the outside world, it is added to `inputs` by the supervisor.

## 6. The controller

Inside `govern()`, once no guardrail has fired, the cap is computed in three
steps.

**Pace target.** The paced consumption at time `t` is the daily quota times the
fraction of the business day elapsed, shaped by the tenant's arrival profile.
The profile is a 24-bucket curve learned from the tenant's last 28 days and
stored in config; a tenant with no history uses a flat profile.

**Correction.** The pace error drives a proportional-integral correction. The
proportional gain `kp` and integral gain `ki` are per-tenant config with fleet
defaults of 0.6 and 0.05. The integral term is stored in controller state and
is clamped to ±0.25 to stop wind-up after a long stall.

**Floor term.** When the floor projection falls below the floor, a second
correction is added that pushes the cap up in proportion to the projected
shortfall. When the floor projection is comfortably above the floor, this term
is zero.

The raw output is the previous cap scaled by the sum of both corrections. It is
then rounded to a whole number of workers and checked against the band.

**Tolerance zone.** Near the end of the business day, the last 10% of it, the
pace target relaxes: the controller accepts finishing up to 5% under quota
rather than spiking the cap to consume the remainder. Entering the tolerance
zone is recorded in the cycle record so that the end-of-day review can see it.

**Override.** Tenant operations can arm a manual override for a tenant, which
pins the cap to a stated value for a stated number of cycles. While an override
is armed `govern()` still computes what it would have done and records it, but
the supervisor applies the override value instead. An override that expires
returns the tenant to normal control on the next cycle. Operations have asked
to be told when an override has been armed for more than four hours, since
that usually means someone forgot to remove it.

## 7. Guardrails

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

Notes on each:

`quota_exceeded` is the only guardrail that takes a tenant to zero. Because it
stops a paying tenant's ingest outright, it is the one the pseudocode above
already alerts on, and tenant operations want to hear about it within minutes,
not at the end of the day.

`feed_stale` protects against acting on old numbers. The feed metrics come from
the ingest gateway's counters, which are scraped on their own schedule; if the
scrape falls behind, the controller would otherwise steer on a stale backlog.
A stale count resets as soon as one fresh reading arrives. A stale feed that
outlasts three cycles is an incident on the gateway side, and whoever owns the
gateway needs to know.

`cap_clamped` on its own is normal: a tenant whose band is narrow will clamp
often. Clamping that persists means the band, the gains or the arrival profile
is wrong for that tenant, which is a tuning problem rather than an outage.

`floor_at_risk` is the early warning. It fires hours before the floor is
actually missed, which is the point: someone can still widen the band, raise
the tenant's priority on the shared fleet, or call the tenant.

`floor_unreachable` is the controller giving up. It is usually a supply
problem — not enough arrivals to process — and it is not something on-call can
fix. It is a business conversation with the tenant about the floor in their
contract.

`config_invalid` keeps one bad config from taking a tenant down, but it means
the tenant is being governed by numbers that were not chosen for it. Someone
has to fix the config, and until they do the tenant's caps are generic.

## 8. Configuration

Per-tenant config lives in the tenant config store and is read by the
supervisor at the start of every cycle. Fields:

| field | meaning | fleet default |
|---|---|---|
| `quota_daily` | records per business day | none, required |
| `floor_daily` | records the contract commits to | none, required |
| `business_day` | start and end, tenant time zone | 00:00–24:00 |
| `cap_min`, `cap_max` | the band | 1, 32 |
| `cap_default` | cap used after a stale feed outlasts three cycles | 8 |
| `kp`, `ki` | controller gains | 0.6, 0.05 |
| `profile` | 24-bucket arrival curve | flat |

Validation rejects a config where `floor_daily` exceeds `quota_daily`, where
`cap_min` exceeds `cap_max`, where `cap_default` falls outside the band, or
where the profile does not sum to one. A rejected config raises
`config_invalid` on the next cycle. Changes to the config store are audited by
the store itself; the governor does not keep its own history of config.

## 9. Cycle record

At the end of every cycle the supervisor writes one cycle record per tenant to
the governor's own table. It holds the cycle timestamp, the inputs `govern()`
was given, the cap it returned, the cap actually applied (which differs while
an override is armed), the guardrail that fired if any, the pace error, the
floor projection, and whether the tenant was in the tolerance zone. The record
is the system of record for what the governor did and why, and it is what the
simulation harness replays.

## 10. Failure modes

- **Supervisor down.** If the supervisor process stops, caps stay wherever they
  were last applied; nothing drives them to zero or to default. A tenant can
  therefore spend its quota early, or miss its floor, with nobody watching. The
  supervisor writes a heartbeat at the start of every run so that a missing run
  can be detected from outside it.
- **Supervisor slow.** A cycle that takes longer than five minutes delays the
  next one. Overlapping runs are prevented by a lease; a run that cannot take
  the lease exits immediately.
- **Feed gateway down.** Covered by `feed_stale`.
- **Config store down.** The supervisor uses the last config it read
  successfully for up to an hour, then treats the tenant as `config_invalid`.
- **Worker pool cannot honour the cap.** `apply_cap` is best-effort; if the
  pool has fewer free workers than the cap allows, the tenant gets fewer. The
  pace error will show it, and the controller will push the cap up, which can
  pin it at the band edge.

## 11. Observability

The following conditions must raise alerts:

- Supervisor heartbeat missed (the loop did not run).
- `feed_stale` persisting past three cycles.
- `quota_exceeded` (the loop is now holding the cap at zero).
- Cap pinned at a band edge for two consecutive cycles.
- Pace error above 15% for two consecutive cycles.
- `floor_at_risk`.
- `floor_unreachable`.
- `config_invalid` (the tenant is running on the fleet default).
- Override armed for more than four hours.

Beyond alerts, each tenant needs an end-of-day view: quota consumed against
quota, records processed against the floor, how long the tenant spent in the
tolerance zone, which guardrails fired, and whether an override was armed.
Tenant operations review it each morning for the previous day.

## 12. Operations and ownership

The platform ingest team owns the governor, the supervisor and the cycle record
table, and carries the on-call rotation for them. The ingest gateway, which
produces the feed metrics, is owned by the gateway team, which has its own
rotation. The tenant config store is owned by tenant operations.

Tenant operations also own the relationship with each tenant, and they are the
ones who act on a floor that is going to be missed: they can widen a band, arm
an override, or call the tenant. Finance needs to know about any floor that is
actually missed, because it may owe a service credit, but finance does not need
to hear about anything during the day.

Several of the alerts above are therefore not for the governor's on-call at
all. Who receives each one is not settled; see open questions.

## 13. Testing

The test ladder has four rungs, and the governor does not reach production
until each one passes.

1. **Unit tests** on `govern()` enumerate every guardrail edge: each guardrail
   firing alone, each pair in the same cycle to confirm priority order, and
   each boundary value of the band, the stale count and the tolerance zone.
2. **Property tests** assert that the cap always lies in the band unless
   `quota_exceeded` has set it to zero, and that the same state and inputs
   always produce the same result.
3. **Simulation.** The harness replays 90 recorded production days for every
   tenant through `govern()` and compares quota spend and floor attainment
   against what actually happened under static caps.
4. **Shadow.** See rollout. The shadow week's recorded cycles are replayed
   through the harness, which must reproduce the caps the shadow run computed
   exactly.

Alerts are tested at the shadow rung: every alert in section 11 must have
fired at least once during the shadow week, from a real condition or a
synthetic one, and been received by whoever is meant to receive it.

## 14. Rollout

One week shadowing production (computing caps, not applying them), then five
pilot tenants, then the fleet. The simulation harness must replay the shadow
week's recorded cycles and reproduce the caps the shadow run computed.

Gates between stages:

- **Shadow to pilot**: the replay reproduces every shadow cap; every alert has
  fired at least once and reached its recipient; tenant operations have
  reviewed a week of end-of-day views.
- **Pilot to fleet**: two weeks on the five pilot tenants with no missed floor
  that the governor did not warn about at least two hours ahead, and no
  `quota_exceeded` before 18:00 tenant time.

Rollback at any stage is a config flag that makes the supervisor apply each
tenant's static cap instead of the governor's output. The governor keeps
computing and recording while rolled back, so the shadow comparison continues.

## 15. Open questions

1. Who receives each alert? The governor's on-call, the gateway team, tenant
   operations and finance all appear somewhere above, and none of the alerts
   has an owner written down.
2. Should `cap_clamped` alert at all, or only feed the end-of-day view?
3. Is two cycles the right persistence for the pace-error alert, given that
   the integral term takes several cycles to settle after a burst?
4. Does a tenant on `config_invalid` need to be told, or only tenant
   operations?
5. How long are cycle records retained? The simulation harness wants 90 days;
   the table will grow by roughly 290 rows per tenant per day.
