

===== T01 | case: design-alerting =====
Two of the eight alert conditions already fall out of existing guardrails (`quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid`) — `govern()` returns the guardrail, and the supervisor's existing `if result.guardrail == ...: alert(...)` pattern (SPEC.md:31-32) extends directly to those. The rest force a real decision:

- **Consecutive-cycle conditions** (`feed_stale` past 3 cycles, cap pinned at a band edge for 2, pace error >15% for 2) need counters that persist across cycles. Since `govern()` must stay pure with no I/O (that's what makes the simulation harness replay at thousands of cycles/sec), these counters belong in the persisted controller state, and `govern()` should evaluate them and return which alerts fired as data — not have the supervisor reimplement threshold logic ad hoc from raw metrics. Keep `alert()` itself as the only I/O, fired by the supervisor off `result`, exactly like the existing quota example.
- **Heartbeat missed** can't be produced this way at all — if the loop didn't run, nothing inside the loop can report it. That needs an external watchdog checking each tenant's last-successful-cycle timestamp against a threshold, independent of the control loop.

Left out: alert delivery/routing (dedup, severity, who gets paged) — that's the next layer down and isn't specified here.


===== T02 | case: design-alerting =====
Looking at SPEC.md, alerting shows up in two places: the `alert("quota exceeded", tenant)` call in the control-loop pseudocode (line 32), and the eight conditions listed under **Observability** (lines 64-73). Splitting those eight by what kind of signal they need points to a specific architecture:

**1. Single-cycle conditions — driven directly by `govern()`'s output**

`quota_exceeded`, `floor_at_risk`, `floor_unreachable`, and `config_invalid` are all guardrails `govern()` already evaluates every cycle. The supervisor just checks `result.guardrail` (or, since guardrails are "first match wins" priority-ordered, checks underlying flags — more on that below) and calls `alert()` when the condition is true. This is exactly the pattern the pseudocode already shows for `quota_exceeded`.

**2. Multi-cycle conditions — split into two different homes**

- `feed_stale` persisting past three cycles is *already* control-relevant: the spec says at three consecutive stale cycles the tenant falls back to its default cap (line 51-52). So its counter has to live in the persisted controller state regardless of alerting, and `govern()` already tracks it. Alerting here is just "read the counter `govern()` already maintains, alert when it crosses 3."
- Cap pinned at a band edge for two cycles, and pace error above 15% for two cycles, are *not* decision-relevant — nothing in the guardrail list changes behavior based on them. Stuffing counters for these into `govern()`'s state would violate the core-purity design the spec leans on hard (the whole simulation harness depends on `govern()` doing no I/O and having no bookkeeping beyond what decisions need). These belong outside the pure core, in whatever metrics/alerting system watches the supervisor's output.

**3. Heartbeat missed — has to be external by construction**

A process that has died or stalled can't alert on its own absence. This needs a dead-man's-switch pattern: the supervisor writes a "last cycle completed at T" timestamp (or emits a heartbeat metric) as part of step 4 in the control loop, and a separate watchdog — a monitoring-system rule (e.g., Prometheus `absent()`/staleness alert, a scheduled check, or an Alertmanager-style rule) fires when that timestamp goes stale beyond the expected 5-minute cadence. Worth deciding explicitly: is the heartbeat per-tenant or one global heartbeat for the whole fleet loop? If the supervisor can die partway through the tenant list, a single global heartbeat won't catch tenants that got silently skipped.

**Putting it together**

- The supervisor, after each `govern()` call, emits structured per-tenant metrics/events (guardrail fired, cap value vs. band edges, pace error %, cycle timestamp) to a metrics backend, rather than hand-rolling threshold logic inside `alert()`.
- An alerting-rules layer (Alertmanager, Datadog monitors, CloudWatch alarms — whatever the shop uses) owns the "sustained for N cycles" logic for the two alerting-only conditions, expressed as a duration threshold (5-minute cycles, so "two consecutive" ≈ a `for: 5m`-style condition, "three consecutive" ≈ `for: 10m`), plus the heartbeat-absence rule.
- `alert(message, tenant)` in the pseudocode is best read as a thin publish call into that pipeline, not the place where dedup/routing/paging logic lives.

**Two things worth flagging before building this:**

- *Alert storms*: `quota_exceeded` holds until day rollover and `floor_at_risk`/`config_invalid` can persist for many cycles too. If `alert()` fires every single cycle the condition holds, that's up to ~288 alerts/day per stuck tenant. Alerting needs to be edge-triggered (fire once on transition into the condition, resolve when it clears) rather than level-triggered on every cycle — standard Alertmanager grouping/inhibition handles this, but it needs to be a deliberate choice, not a byproduct of calling `alert()` unconditionally inside the loop.
- *Shadow week*: during the one-week shadow rollout (line 77), guardrails compute but caps aren't applied. If alerting is wired to the same `govern()` output, shadow mode will page on-call for conditions where nothing is actually being enforced yet — routing for shadow-mode alerts (lower urgency, different channel, or suppressed) needs to be decided before that week starts.

This wasn't spelled out in SPEC.md — the doc says *what* must alert, not *how* — this is inference from the surrounding architecture (core purity, priority-ordered guardrails, persisted state, rollout plan).


===== T03 | case: design-cache =====
The 0% CDN hit rate is the tell: the CDN already sits in front and honors origin headers, but `middleware/security.js` (app.js:9) forces `no-store` on every route, applied app-wide after the 2024 audit to fix an `/account` leak. That blanket rule is the actual reason nothing caches — `/p/:slug` is fully anonymous (no session read, same for every user, catalog edits only a few times a day) and doesn't need it at all.

Build it as a per-route header split, not a new cache layer:

- Keep `/account` exactly as-is — that's the audit-mandated constraint and it's a real one (cross-user leak via intermediary cache), don't touch it.
- Give `/p` its own `Cache-Control: public, max-age=<N>` (something like 5–15 min, since catalog changes are infrequent and stale-for-minutes is fine), applied instead of the shared `security` middleware for that router.
- That alone lets the CDN start serving cache hits with zero origin traffic, which removes the `relatedProducts` join (~600ms) and `stockFor` (~250ms) from the hot path entirely for any repeat view of a slug within the TTL — no Redis, no in-process cache, no new infra.

The one fork worth calling out: TTL-based staleness vs. purge-on-publish from the admin tool. TTL is simpler and matches "changes a few times a day" fine; purge-on-publish gets instant freshness but means wiring a CDN-invalidation call into the admin edit path. I'd start with TTL and only add purge if editors complain about staleness.


===== T04 | case: design-search =====
At 38k rows and low growth, Postgres full-text search on the existing `products` table is the right call — no need for Elasticsearch/Algolia/Typesense here; that infrastructure earns its keep at millions of rows or when you need faceting/analytics, not at this scale.

**Schema change** — add a generated `tsvector` column and index it:

```sql
ALTER TABLE products
  ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', name), 'A') ||
    setweight(to_tsvector('english', description), 'B')
  ) STORED;

CREATE INDEX products_search_idx ON products USING GIN (search_vector);
```

The `STORED` generated column keeps the vector in sync automatically on insert/update, so there's no trigger or app-side reindex step to maintain. Weighting `name` above `description` means a match in the name ranks higher, which is what users expect.

**Query** — use `websearch_to_tsquery`, not `plainto_tsquery` or a raw `to_tsquery`. It's built for exactly this: it takes free-typed user input (handles multiple words as AND, quoted phrases, `-word` exclusion) without throwing syntax errors on stray punctuation the way `to_tsquery` does:

```sql
SELECT id, sku, name, price_cents,
       ts_rank(search_vector, query) AS rank
FROM products, websearch_to_tsquery('english', $1) query
WHERE active AND search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

**Route** — new endpoint in `routes/products.js`, matching the existing pagination/style conventions:

```js
router.get("/search", async (req, res) => {
  const q = (req.query.q || "").trim();
  if (!q) return res.json([]);
  const rows = await db.query(
    `SELECT id, sku, name, price_cents, ts_rank(search_vector, query) AS rank
     FROM products, websearch_to_tsquery('english', $1) query
     WHERE active AND search_vector @@ query
     ORDER BY rank DESC
     LIMIT 20`,
    [q]
  );
  res.json(rows);
});
```

**Things worth deciding up front:**

- **Typo tolerance.** Plain FTS does stemming (`running` matches `run`) but not fuzzy matching — a misspelled `"widgit"` returns nothing. If that matters for the product, add the `pg_trgm` extension and a trigram GIN index on `name`, then fall back to a similarity query when the FTS query returns zero rows. If it's not a priority for v1, skip it — it's an easy follow-up, not a rewrite.
- **Debounce on the frontend.** "A few words while typing" implies live search-as-you-type; debounce requests client-side (150–250ms) so you're not firing a query per keystroke.
- **Migration cost.** Backfilling the generated column on 38k rows is instant; no need for a background migration job.
- **Search performance ceiling.** A GIN index on a ~38k-row table returns in low single-digit milliseconds. This approach comfortably scales to a few million rows before you'd need to reconsider.

That's the whole build: one migration, one indexed column, one route.


===== T05 | case: design-audit-log =====
Every write in this service already funnels through one place: `db.write()` in `db.js`, which owns the transaction boundary. That's the chokepoint to hook, not each route handler.

**Recommended shape: DB-level triggers, not app-level logging calls.**

- Add an `audit_log` table (`table_name`, `row_id`, `action`, `old_data jsonb`, `new_data jsonb`, `actor`, `changed_at`), insert-only — revoke `UPDATE`/`DELETE` on it for the app's DB role so it can't be edited after the fact.
- Attach a generic `AFTER INSERT OR UPDATE OR DELETE` trigger to each writable table (`accounts`, `orders`, ...) that writes `OLD`/`NEW` as JSONB into `audit_log`. This runs in the same transaction as the write itself, so there's no window where a write commits without an audit row, and it also catches writes that don't go through the app at all (migrations, a future admin script, a raw `db.query` someone uses instead of `db.write`).
- For "who": have `db.write()` do `SET LOCAL app.actor = <user id>` right after `BEGIN`, sourced from `req.user.id` (already populated by `sessionUser` in `auth.js` before every request reaches a handler). The trigger reads that session variable via `current_setting('app.actor')`. Make the trigger error if it's unset, so any write path that forgets to identify an actor fails closed instead of logging silently as anonymous.

**Two decisions that fork this:**

1. Trigger-based (DB-enforced, can't be bypassed by new code) vs. an app-level audit insert inside `db.write()` itself (simpler to read, but only as strong as every future write going through that function). Given "compliance" and "every write," I'd take the trigger — it doesn't depend on developer discipline.
2. Full row snapshots (`old_data`/`new_data` as JSONB) vs. a precomputed column-level diff. Snapshots are the safer default — you can compute a diff at query time later, but you can't recover a wrongly-computed diff.

Left out: retention/archival policy, whether `audit_log` needs to live in a separate DB for tamper-resistance, and how `sessionUser` failures (no `req.user`) on unauthenticated paths interact with the `SET LOCAL` requirement — worth resolving before implementation but not fork points for the core design.


===== T06 | case: design-cache =====
Cache the DB reads behind the page in Redis/Memcached, keyed by product ID, with a short TTL (minutes) as a safety net plus explicit invalidation/write-through when a product is updated — that combination gives you freshness without depending on TTLs alone catching every write.

The fork that actually matters: cache raw query results (flexible, still pays render cost) vs. cache the fully rendered page/fragment (near-zero cost on a hit, but needs per-variant keys — locale, currency, logged-in state, A/B). Since your 900ms is DB-bound rather than render-bound, start with query-result caching; move to full-page/edge caching only if render time becomes the next bottleneck.


===== T07 | case: design-rate-limit =====
Rate limiter as Redis-backed middleware in `routes/api.js`, right after the existing `X-Api-Key` lookup — it already resolves `req.client.client_id` and `plan`, which is the right key to limit on, not IP (the comment in that file notes clients share NAT addresses, so IP would both over- and under-block).

Two decisions actually fork the design:

- **Where the counter lives.** `app.js` clusters 4 workers per box with nothing shared in-process, so an in-memory limiter would let each worker allow its own quota independently — a client could get ~4x the intended limit per box, more across boxes. `redis.js` already gives you the one thing every worker and box shares, so the counter has to live there too. A Lua script (`EVAL`) doing the increment-and-check atomically is worth it here since `redis.js` uses plain `ioredis` calls with no existing pattern for atomic multi-step ops — a naive `INCR` + `PEXPIRE` has a race where a crash between the two calls leaves a key with no TTL.
- **Fixed window vs. sliding window/token bucket.** Fixed window (`INCR` on a `ratelimit:{client_id}:{minute}` key with `EXPIRE`) is simplest and matches the existing Redis usage style in `redis.js`, but lets a client burst 2x at window boundaries — fine for "stop one client from degrading everyone," probably not fine if you later want per-second smoothness. Token bucket is one Lua script away but is more to reason about for no benefit at this problem's scale.

Given the actual complaint (one client hammering, degrading others), I'd go fixed-window, keyed by `client_id`, limit sourced from `plan` (the row already carries it), returning 429 before the request reaches `db.query`. Left out: what happens if Redis itself is unreachable (fail-open vs. fail-closed), and whether limits differ by endpoint (`GET /reports` vs `POST /reports` cost very differently) — worth deciding before writing it, not architecture-forking.


===== T08 | case: design-retry =====
The core fix: on a timeout, don't treat "no response" as "failed" — treat it as "unknown," and let idempotency do the heavy lifting.

**The two decisions that shape this:**

1. **Idempotency key per charge attempt.** Generate one key when the customer clicks pay, and reuse it on every retry of that same attempt. Most processors (Stripe, Adyen, Braintree) will then return the original result instead of creating a second charge — so retrying is safe even if the first request actually succeeded on their end and only the response got lost.

2. **A third state between success and failure.** Right now the flow sounds binary (success/failed), which is why a timeout gets mapped to "failed" and shown to the customer. Add a `pending`/`processing` status: on timeout, mark the charge pending, don't tell the customer anything failed, and resolve it out of band — either a background job that re-queries the processor using the same idempotency key, or (better, if the processor supports it) a webhook that reports the true outcome once it's known. Only surface "payment failed" after that resolves to an actual decline.

For the retry job itself: async with a short exponential backoff (a few attempts over 10–30s covers a transient timeout), not an inline client-side retry — that way a slow customer connection doesn't compound the problem.

Left out: the specific backoff/attempt count, and whether to lean on webhooks vs. polling for reconciliation — that depends on which processor you're on. Which one are you using? That determines whether idempotency keys and status webhooks are already available or need to be built.


===== T09 | case: design-cache =====
Traced the actual bottleneck through `db.js` and the routes rather than guessing:

**Root cause:** `middleware/security.js` sets `Cache-Control: no-store, private` on every response, app-wide — that's why the CDN sitting in front (which honors origin headers with no path rules) has a 0% hit rate. It was a blanket fix for one leaky page (`/account/orders`, which is genuinely per-user and correctly must stay `no-store`), but it got applied to `/p/:slug` too, which is anonymous, has no session read, and is identical for every visitor. Of the 900ms, ~890ms is `productBySlug` (40ms) + `relatedProducts` (600ms, four-table join) + `stockFor` (250ms) — all three keyed only by product ID, none per-user.

**Design: two layers, in this order**

1. **Fix the edge cache first — it's a one-line header change, not new infra.** Split `security.js` so `/account` keeps the current strict policy, and `/p` gets something like `Cache-Control: public, max-age=120, stale-while-revalidate=600`. Since the CDN already terminates TLS and respects origin headers, this alone lets it serve repeat requests for the same slug with zero app or DB involvement. Catalog edits happen "a few times a day" per the comment in `products.js`, so a couple minutes of staleness is cheap; if the admin tool can call a purge API on publish, use that instead of guessing a TTL, but TTL-only is fine to start.

2. **App-layer cache (Redis) behind the edge, for what the CDN can't cover** — first hit after a purge/TTL expiry, long-tail slugs, and any client that bypasses the edge cache (e.g., `Cache-Control: no-cache` from a dev tool). Cache `relatedProducts` and `stockFor` by product ID, not the whole rendered page, so `productBySlug` (already cheap at 40ms) stays a live read and the two expensive queries get reused:
   - `relatedProducts`: long TTL (minutes), since it only moves when someone edits tags/catalog in admin. This is the 600ms line, so it's the highest-value entry to cache.
   - `stockFor`: short TTL (seconds), since inventory changes with orders and a stale count risks oversell — cache just enough to absorb request bursts, not to track inventory.

**What stays untouched:** `/account` keeps `no-store` exactly as the audit required — the fix is scoping the middleware per-route, not loosening it globally. That's the actual bug: the remediation was correct for one path and accidentally applied to a path where it costs 900ms per request for no security benefit.


===== T10 | case: design-search =====
At 38k rows on Postgres 16, this doesn't need a separate search engine — Postgres full-text search handles it and avoids syncing data to Elasticsearch/Meilisearch.

Add a generated `tsvector` column combining name and description, weighted so name matches rank higher:

```sql
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', name), 'A') ||
    setweight(to_tsvector('english', description), 'B')
  ) STORED;

CREATE INDEX products_search_idx ON products USING GIN (search_vector);
```

Then a route in `routes/products.js` alongside the existing list/get, using `websearch_to_tsquery` (handles raw user phrases like `"wireless mouse -bluetooth"` without you parsing operators) and `ts_rank` for ordering:

```sql
SELECT id, sku, name, price_cents,
       ts_rank(search_vector, websearch_to_tsquery('english', $1)) AS rank
FROM products
WHERE active AND search_vector @@ websearch_to_tsquery('english', $1)
ORDER BY rank DESC
LIMIT 50 OFFSET $2
```

The one real fork: plain `tsvector` matches whole lexemes, so it won't catch typos or mid-word prefixes ("iphon" won't match "iphone"). If that matters for this catalog, add `pg_trgm` with a GIN trigram index and blend it in or fall back to it when FTS returns nothing — that's the extra layer to size up once you know how forgiving the search needs to be.


===== T11 | case: design-retry =====
The current flow in `routes/checkout.js` and `payments.js` treats any thrown error — including a timeout — as a hard failure and returns 502. But `PROVIDER.md` is explicit that a timeout is **unknown**, not failed, and that Cardstream supports `Idempotency-Key` for exactly this case. The bug isn't "no retry loop," it's that retrying without an idempotency key on this endpoint is unsafe (could double-charge), and right now no key is ever sent.

**Core design:** generate a stable key per payment attempt — `pay-${order.id}` is enough here, since `status !== 'pending'` already guards against a second checkout call reusing the row — and send it as `Idempotency-Key` on the charge and on every retry of that same charge. On `timeout`/`ECONNRESET` specifically, retry a couple of times with backoff (2-3 attempts is plenty given the 600/min limit); on a real decline (4xx from the provider), don't retry, that's a genuine failure. This turns "retry" from risky into safe, because Cardstream dedupes on the key.

**The one fork worth deciding:** what happens if retries are exhausted and it's still unknown. Two options:
- Keep it synchronous — retry inline within the request, and if still unresolved after retries, return something other than "payment failed" (e.g. "processing", HTTP 202) and reconcile the order status later via a background check against the same idempotency key.
- Go fully async — mark the order `processing` before the first attempt, return immediately, and let a worker own the charge+retry+reconcile loop, with checkout only polling for the outcome.

Given the volume described ("a few times a day"), inline retry with a fallback to a `processing`/`payment_unknown` order status (instead of `paid`/`pending`/failure) is the smaller change and avoids ever showing "failed" for something that might actually have succeeded. The async worker is the more robust version if timeouts get more frequent or retries need to survive a server restart.


===== T12 | case: design-audit-log =====
Since every write in this service already funnels through one chokepoint — `db.write()` in `db.js` — that's where to put the audit trail, not scattered across route handlers. Two forks matter here:

**1. Trigger-based audit, not app-level logging.** Have Postgres triggers write to an append-only `audit_log` table on every INSERT/UPDATE/DELETE of an audited table, in the same transaction as the write itself. This beats logging from route handlers because it can't be skipped — a route added next month that calls `db.write()` gets audited automatically, whereas app-level logging only covers the routes someone remembered to instrument (and `accounts.js`'s `DELETE /:id` today shows how easy that is to miss). It also gives you full before/after row diffs for free via `to_jsonb(OLD)`/`to_jsonb(NEW)`, atomically consistent with the write (rollback undoes both).

```sql
CREATE TABLE audit_log (
  id           bigserial PRIMARY KEY,
  table_name   text NOT NULL,
  row_id       text NOT NULL,
  action       text NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
  actor_id     uuid,
  actor_email  text,
  old_row      jsonb,
  new_row      jsonb,
  changed_at   timestamptz NOT NULL DEFAULT now()
);
-- REVOKE UPDATE, DELETE ON audit_log FROM app role — append-only

CREATE FUNCTION audit_row() RETURNS trigger AS $$
BEGIN
  INSERT INTO audit_log(table_name, row_id, action, actor_id, actor_email, old_row, new_row)
  VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id)::text,
    TG_OP,
    NULLIF(current_setting('app.actor_id', true), '')::uuid,
    NULLIF(current_setting('app.actor_email', true), ''),
    CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,
    CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER accounts_audit AFTER INSERT OR UPDATE OR DELETE ON accounts
  FOR EACH ROW EXECUTE FUNCTION audit_row();
```

**2. Getting "who" to the trigger without touching every route.** None of the current call sites (`accounts.js`, `orders.js`) pass an actor into `db.write()`, and `sessionUser` in `auth.js` only sets `req.user`. Rather than changing every route's signature, capture the actor once in the middleware via `AsyncLocalStorage` and have `db.write()` stamp it into the transaction with `set_config` (transaction-scoped, so it can't leak across pooled connections):

```js
// auth.js
const actorContext = new AsyncLocalStorage();
async function sessionUser(req, res, next) {
  // ...existing lookup...
  actorContext.run({ id: rows[0].id, email: rows[0].email }, next);
}

// db.js
async function write(text, params) {
  const client = await pool.connect();
  const actor = actorContext.getStore();
  try {
    await client.query("BEGIN");
    if (actor) {
      await client.query(
        "SELECT set_config('app.actor_id',$1,true), set_config('app.actor_email',$2,true)",
        [actor.id, actor.email]
      );
    }
    const res = await client.query(text, params);
    await client.query("COMMIT");
    return res.rows[0];
  } catch (err) { await client.query("ROLLBACK"); throw err; }
  finally { client.release(); }
}
```

Depth left out: writes that bypass the app pool entirely (migrations, one-off admin SQL) won't have an `app.actor_id` set and need a convention (tag as `system` or a service account); retention/tamper-evidence beyond DB grants (WORM archival) if compliance needs it; and this covers writes only, not read/view auditing, which is a separate and heavier ask.


===== T13 | case: design-audit-log =====
**Recommendation:** write the audit record in the same transaction as the write itself, to an append-only table your app's write role can only INSERT into (no UPDATE/DELETE grants) — each row carrying actor, entity+id, before/after diff, timestamp, and a request/correlation id.

Two decisions actually fork this:

1. **Where you intercept the write.** Application/ORM middleware (a single hook in your repository layer or ORM interceptor) gives you clean identity (the authenticated user) and structured diffs for free, but only catches writes that go through your app. DB triggers or CDC (Postgres logical decoding, Debezium) catch everything — including migrations and direct SQL — but the DB only sees your service's connection, so "who" requires threading the user id through a session variable (`SET LOCAL app.user_id`) for triggers to read.
2. **Sync vs async.** Writing the audit row in the same transaction guarantees nothing is ever unaudited — the right default for compliance. An event/queue-based approach scales better but can drop or delay the audit record if the consumer fails, which is only acceptable if the compliance requirement tolerates eventual consistency.

For a compliance audit trail, I'd do app-layer capture for identity plus same-transaction writes, with DB triggers as a backstop for anything that bypasses the app.

Left out: retention/archival, tamper-evidence (hash-chaining or WORM storage if the regulator needs provable immutability), and the query/export interface for auditors — those depend on the actual stack. What DB and framework are you on?


===== T14 | case: design-alerting =====
Alerting has to live in the supervisor, not in `govern()` — the spec is explicit that the core is pure (no clock, no network, no storage), so anything that calls out to an alerting system belongs in the loop shown in the pseudocode, which already does this for one case:

```
if result.guardrail == "quota_exceeded":
    alert("quota exceeded", tenant)
```

The eight required conditions split into three shapes, each needing a different mechanism:

**1. Single-cycle guardrail alerts** — `quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid`. These map directly onto `result.guardrail` from a single `govern()` call, so the existing pattern generalizes: the supervisor checks `result.guardrail` each cycle and dispatches to `alert()`.

**2. Consecutive-cycle alerts** — `feed_stale` past three cycles, cap pinned two cycles running, pace error over 15% two cycles running. These need memory across cycles. The spec already implies `govern()` tracks this for `feed_stale` (it counts to three before falling back to the default cap), so the natural extension is to keep that pattern consistent: add counters like `consecutive_cap_pinned` and `consecutive_pace_error_breach` to the persisted controller state, and have `govern()` compute an `alerts` list as part of its pure output alongside `cap`, `state`, and `guardrail`. That keeps the "when does this fire" logic testable by the same unit tests and simulation harness that already cover guardrail edges, instead of duplicating threshold logic in the supervisor.

With that, the supervisor's step 4 becomes a single dispatch loop instead of a special case:

```
for a in result.alerts:
    alert(a, tenant)
```

**3. Heartbeat missed** is the odd one out — it's the *absence* of a cycle, so nothing inside the loop can raise it; the code that would raise it isn't running. This needs an external watchdog: each successful cycle writes a liveness signal (last-run timestamp or counter) to the same store as the persisted state, and a separate always-on checker (cron job, Prometheus/Alertmanager rule, cloud health check) alerts if that timestamp goes stale. Standard dead-man's-switch pattern.

**Dedup/flap control**: a condition that persists (e.g. `floor_at_risk` for three hours straight) would otherwise re-fire every five minutes. `alert()` should key on `(tenant, condition)` and fire on transition — new occurrence or newly resolved — not on every cycle it's still true. That state (what's currently alerting per tenant) is itself worth persisting alongside the controller state.

**Rollout tie-in**: during the one-week shadow phase the loop computes but doesn't apply caps, so alerting should still run but route to a non-paging channel (dashboard/log) rather than paging — otherwise the team gets paged for tenants whose caps aren't even live yet, and can't use the shadow week to calibrate real alert volume before the pilot.


===== T15 | case: design-upload =====
Recommend direct-to-storage uploads with client-side compression, not routing photo bytes through your app server:

1. **Client resizes before sending.** Phone cameras produce 3–12MB photos (often HEIC on iPhone). Downscale to something like 2000px on the long edge and re-encode as JPEG/WebP client-side (canvas or a library) before upload — this is the fork that matters most here, since skipping it means slow uploads on cellular and needless storage/bandwidth cost.
2. **Direct-to-bucket via presigned URLs**, not proxied through your API: client asks your server for a presigned S3/GCS PUT URL, uploads straight to the bucket, then calls your API with the resulting object key to attach it to the listing. This keeps large file bytes off your app servers entirely.
3. **Async variant generation** — a storage event (S3 event → Lambda/queue worker) generates thumbnail/card/full-size variants after upload, rather than blocking the upload request on processing.
4. Strip EXIF GPS data server-side (or client-side) before the photo is ever public — camera photos carry location metadata, which is a real leak for sellers listing from home.
5. For multiple photos: upload in parallel with per-file retry, since mobile connections drop mid-upload often enough to matter.

Left out: auth/permissions on the presigned URL endpoint, moderation/content scanning, and reorder/cover-photo UX — worth designing once the upload path itself is settled.


===== T16 | case: design-realtime =====
Given `PLATFORM.md`, this is a serverless-functions-only platform (10s invocation limit, no persistent process, no WebSocket upgrades — those hit a 501 before your code even runs). That rules out push-based approaches (WebSockets, SSE, long-polling) — there's no way to hold a connection open long enough to notify clients when `rollup` changes. Polling is the only option left.

The design that fits the actual update cadence:

**Client (`public/dashboard.js`)**
- Replace the click-only `load()` wiring with `setInterval(load, …)`, keeping the refresh button as a manual override.
- Since `jobs/rollup.md` says the rollup is rewritten once a minute, on the minute, polling every 15–20s gives sub-20s staleness without hammering the function. (You could instead poll once right after each minute boundary for near-zero staleness with 1/4 the requests, but that's more fragile — clock drift, job running a few seconds late — so fixed-interval polling is the safer default.)
- Compare the new `computed_at` to the last one client-side before re-rendering, so a poll that returns unchanged data doesn't cause a flicker.
- Pause the interval on `visibilitychange` when the tab is hidden, and fire one immediate `load()` on becoming visible again — avoids polling background tabs.

**Server (`api/metrics.js`)**
- No change needed functionally — it's already cheap (30ms, 4KB) and `no-store` is already set correctly for polling.
- Optional: add an `ETag` derived from `computed_at` and honor `If-None-Match` with a 304, so unchanged polls cost bandwidth-only, not a JSON re-serialize. Given the payload is already tiny, this is a nice-to-have, not a requirement.

Main tradeoff: this is polling, not real-time — there's an inherent delay up to your interval length, and every viewer's browser makes a request even when nothing changed. That's the ceiling this platform allows; the alternative (a persistent connection) isn't available under the stated constraints without the priced-and-declined platform migration.


===== T17 | case: design-upload =====
Recommended shape: client requests a presigned upload URL from your backend, uploads the photo directly to object storage (S3/GCS) from the phone, then a background worker (triggered on upload-complete) generates resized variants/thumbnails and strips EXIF (especially GPS) before the photo is marked "ready" and attached to the listing. This avoids proxying multi-MB files through your app servers and keeps the listing responsive while processing happens async.

Two decisions that actually fork this:

- **Where compression happens.** Resize client-side (e.g. to ~2000px long edge, JPEG/WebP) before upload to cut bandwidth and mobile data usage, vs. upload the raw phone photo and let a server worker downsize it. Client-side is friendlier on flaky mobile connections but adds client complexity (and HEIC-to-JPEG conversion if you support iPhone's native format); server-side is simpler on the client but means uploading full 5-12MB originals over cellular.
- **Sync vs. async attach.** Whether the listing can save with photos still "processing" (showing a placeholder until variants are ready) vs. blocking listing save until all photos are fully processed. Async is more forgiving of mobile upload flakiness and lets sellers keep adding photos while earlier ones finish.

Depth I'm leaving out: retry/resume behavior for interrupted uploads, moderation/content-safety scanning, and CDN/cache invalidation for the generated variants.


===== T18 | case: design-alerting =====
Both mentions point to the same shape: line 32's `alert(...)` call is inside the control loop, but the eight conditions at line 64-73 are a mix of single-cycle and multi-cycle triggers, plus one (heartbeat missed) that can't be detected from inside the loop at all.

**Recommendation:** don't hang alert logic off the loop's `alert()` call site — push it into `govern()` alongside the guardrails, and add a separate liveness check for the one condition the loop itself can't see.

- **Single-cycle conditions** (`quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid`) map directly to `result.guardrail`, so the existing pseudocode already covers them — the loop just needs to alert on any guardrail value, not just `quota_exceeded`.
- **Streak conditions** (`feed_stale` > 3 cycles, cap pinned 2 consecutive cycles, pace error > 15% for 2 consecutive cycles) need counters carried in the persisted state, the same way the spec already implies a stale-cycle counter for the fallback-to-default behavior. The fork: compute these streaks inside `govern()` and return them as part of `result` (e.g. `result.alerts`), versus computing them in the supervisor from the raw guardrail history. Keeping it in `govern()` wins — it's the same state the fallback logic already tracks, and it stays on the pure, replay-tested core instead of becoming untested I/O-loop logic.
- **`heartbeat missed`** can't come from `govern()` at all — if the loop doesn't run, nothing inside it fires. That needs an external dead-man's-switch: something outside the per-tenant loop (a scheduled check or monitor) comparing each tenant's last-persisted cycle timestamp against the 5-minute cadence and alerting on staleness.

Left out: the alert sink/transport itself (paging vs. log vs. metric), dedup so a streak doesn't refire every cycle, and severity/routing per condition — none of that is specified yet.


===== T19 | case: design-upload =====
Route through the pieces already here, not through nginx:

**The fork:** `nginx.conf` caps `client_max_body_size` at 1m, globally, on purpose — the payments team declined to raise it or split it per-location because this listener also fronts the card-data endpoint, and the limit is cited in their PCI paperwork. A phone camera photo routinely runs 3-8MB, so any upload proxied through the storefront route (`/`) hits that cap immediately, and it's not a limit you can touch.

**The way around it:** don't upload through nginx at all. `storage.js` already has the mechanism: `signedUrl` supports `method: 'PUT'`, unused today, and the bucket CORS already permits PUT from `market.example.com` (inherited from the same template as the internal tool's GetObject use). So:

1. `POST /listings/:id/photos` (small JSON, well under 1m) returns a signed PUT URL for a new key, following the same pattern as the existing `/invoice` route.
2. The phone uploads bytes directly to S3 against that URL — full camera resolution goes straight to the bucket, nginx never sees the body.
3. On success, the client calls back to the API with the key; the server calls `db.addPhotoKey(id, key)`, which already exists and already targets `listings.photo_keys` (a `text[]` that's sat empty since the column was added, for exactly this).

That's the whole shape: signed-PUT-then-confirm, mirroring the read side's signed-GET. The depth I'm not going into: multiple-photo ordering/cover-photo selection, client-side downscaling before upload, and validating the confirmed key actually exists in the bucket before trusting it — worth a follow-up once the basic path is agreed.


===== T20 | case: design-retry =====
The root problem: a gateway timeout is being treated as a decline. Those are different failure modes and need different handling.

**1. Don't conflate "timed out" with "failed"**
A timeout means you don't know what happened — the charge may have succeeded on the processor's side even though your request never got a response. Marking it "failed" and letting the customer retry risks a double charge. So the charge state needs a third bucket beyond succeeded/failed: `pending` or `unknown`, and the customer should see something like "confirming payment," not "failed."

**2. Idempotency keys are the foundation**
Every charge attempt (tied to the order/cart, not regenerated per retry) carries an idempotency key that gets sent to the processor. If a retry — automatic or customer-initiated — reuses that key, the processor returns the original result instead of creating a second charge. Stripe, Adyen, Braintree, etc. all support this natively; without it, retries are unsafe by construction.

**3. Reconcile before you retry**
Before firing a retry, ask the processor "what happened to charge X" (by idempotency key or reference ID) rather than blindly resubmitting. If it actually succeeded, you just mark it succeeded and move on — no retry needed. This single check eliminates most of the double-charge risk.

**4. Two tiers of retry**
- *Inline retry*: one immediate retry with the same idempotency key, short timeout, still in the request path — covers transient blips.
- *Async retry*: if that also fails, don't keep the customer's request hanging. Drop it into a background job/queue with exponential backoff + jitter and a capped attempt count (e.g., 3–5 tries over a few minutes). Each attempt does the reconcile-check first.

**5. Webhooks as source of truth**
Subscribe to the processor's async status webhooks. The synchronous response and the webhook can race (webhook confirms success after your API call already timed out) — reconciliation logic needs to treat the webhook as authoritative and update the charge state whenever it arrives, even if a retry is already in flight.

**6. Sweep job for stuck charges**
A periodic job that finds charges stuck in `pending`/`unknown` past some threshold and resolves them via the processor's status API — catches anything the retry queue or webhook missed.

**7. Customer-facing state**
Only show "payment failed" for a genuine decline (insufficient funds, fraud block, expired card). For timeouts, show "processing"/"confirming" and resolve async (poll, websocket push, or email), or hold the customer on a spinner briefly for the inline retry.

**8. Guardrails**
- Circuit breaker on the processor integration if timeout rate spikes, so you're not hammering a struggling endpoint.
- Metrics/alerting split by failure type (timeout vs. decline vs. network error) — right now they're bucketed together, which is likely why this looked like generic "payment failed" in the first place.

This is a design discussion — say the word if you want it turned into an actual implementation plan or code.


===== T21 | case: design-audit-log =====
Looked at the code: this is an Express + `pg` service where `db.write()` in `db.js` is already the single chokepoint every mutation goes through (each call gets its own `BEGIN`/`COMMIT`), and `sessionUser` in `auth.js` guarantees `req.user` is populated before any route handler runs. Those two facts shape the design.

## Where to capture it

Two options, and they're not mutually exclusive:

**App-level, in `db.write()`.** Easy, but only as complete as your discipline — it only sees writes that go through that function. Looking at the routes, that's true today (`accounts.js`, `orders.js` both call `db.write()` exclusively), but nothing stops a future PR, a migration script, or an ad-hoc `psql` fix from mutating a row outside it. For a compliance audit trail, "only as complete as your discipline" is the wrong property to depend on.

**DB-level, via triggers.** An `AFTER INSERT OR UPDATE OR DELETE` trigger on each audited table fires no matter how the row was touched — through the app, a migration, or someone at a psql prompt. That's the property auditors actually want: the audit log isn't something the application chooses to produce, it's a consequence of the write happening at all. I'd make this the source of truth, and treat app-level logging as a nice-to-have for latency/debugging, not the record of fact.

## Schema

```sql
CREATE TABLE audit_log (
  id            bigserial PRIMARY KEY,
  occurred_at   timestamptz NOT NULL DEFAULT now(),
  table_name    text NOT NULL,
  row_pk        text NOT NULL,
  operation     text NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
  actor_user_id integer,          -- nullable: NULL means "no attributable actor"
  actor_email   text,             -- denormalized, survives user deletion
  actor_account_id integer,
  request_id    uuid,             -- correlates to app/HTTP logs
  old_values    jsonb,
  new_values    jsonb
);
```

Denormalize `actor_email` at write time — if the `users` row is later deleted or edited, the audit entry shouldn't change retroactively.

## Trigger + actor propagation

A generic trigger function using `row_to_json(OLD)`/`row_to_json(NEW)`, attached per table:

```sql
CREATE FUNCTION audit_row() RETURNS trigger AS $$
BEGIN
  INSERT INTO audit_log (table_name, row_pk, operation, actor_user_id, actor_email,
                          actor_account_id, request_id, old_values, new_values)
  VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id)::text,
    TG_OP,
    NULLIF(current_setting('app.user_id', true), '')::integer,
    NULLIF(current_setting('app.user_email', true), ''),
    NULLIF(current_setting('app.account_id', true), '')::integer,
    NULLIF(current_setting('app.request_id', true), '')::uuid,
    CASE WHEN TG_OP <> 'INSERT' THEN row_to_json(OLD) END,
    CASE WHEN TG_OP <> 'DELETE' THEN row_to_json(NEW) END
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER accounts_audit AFTER INSERT OR UPDATE OR DELETE ON accounts
  FOR EACH ROW EXECUTE FUNCTION audit_row();
-- repeat for orders, users, and any other compliance-relevant table
```

The trigger reads actor identity from Postgres session variables (`current_setting`), not from an application parameter, because triggers don't know about `req.user`. So `db.write()` needs to set those at the start of its transaction:

```js
async function write(text, params, actor) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    if (actor) {
      await client.query(
        "SELECT set_config('app.user_id', $1, true), set_config('app.user_email', $2, true), set_config('app.account_id', $3, true)",
        [String(actor.id), actor.email, String(actor.accountId)]
      );
    }
    const res = await client.query(text, params);
    await client.query("COMMIT");
    return res.rows[0];
  } catch (err) { await client.query("ROLLBACK"); throw err; }
  finally { client.release(); }
}
```

`true` in `set_config` scopes it to the current transaction (`SET LOCAL` semantics), so it can't leak across pooled connections to a later, unrelated query. Every call site (`accounts.js`, `orders.js`) then needs to pass `req.user` through — that's the one real code change this design implies, and it's mechanical: `db.write(sql, params, req.user)`. If threading `actor` through every call site is undesirable, `AsyncLocalStorage` bound in `sessionUser` middleware achieves the same thing implicitly, at the cost of being a bit more "magic" — I'd only reach for it if the call-site diff turns out large.

A `request_id` generated once per HTTP request (new middleware in `app.js`, before `sessionUser`) and set the same way lets you join an audit row back to app/access logs for the same request.

## Making it tamper-resistant

This is what separates "we log changes" from "this will survive an audit":

- The app's DB role gets `INSERT` on `audit_log` only — no `UPDATE`, `DELETE`, or `TRUNCATE`. Only a separate migration/admin role can alter it.
- Writes with no `app.user_id` set (raw SQL, a forgotten migration) still get logged, just with `actor_user_id IS NULL` — that's a feature, not a gap: "unattributed change" is exactly the thing an auditor wants surfaced, not silently dropped.
- For stronger tamper-evidence, add a hash-chain column (`row_hash = hash(prev_row_hash || row content)`), and periodically verify the chain. Optional, but standard for SOC2/PCI-grade trails.
- Ship a periodic export to write-once storage (S3 with Object Lock, or a separate log aggregator) so the trail survives even a compromised DB admin, not just a compromised app.

## Retention and access

- Compliance retention windows (often multi-year) mean partitioning `audit_log` by month (`occurred_at`) so old partitions can be archived/detached cheaply instead of deleted from a single huge table.
- Auditors get a read-only role or a small reporting endpoint (`GET /audit?table=accounts&row_pk=…` / `?actor=…`) rather than direct prod DB access.
- Common queries to support explicitly: "everything done to row X," "everything done by user Y," "everything done in date range Z" — all satisfied by indexes on `(table_name, row_pk)`, `(actor_user_id, occurred_at)`, `(occurred_at)`.

That's the shape: triggers as the enforcement mechanism so nothing can write without being logged, session-scoped `SET LOCAL` to carry `req.user` from the app into the DB layer where the trigger can see it, an insert-only audit table, and partitioning/export for retention. Say the word if you want me to actually implement it (new migration, the `db.write()` signature change, and updating the two route files to pass `req.user`).


===== T22 | case: design-realtime =====
Poll, not push. The platform rules out anything else: WebSocket upgrades 501 at the edge, and functions are frozen between invocations so nothing can hold a connection or push open even if it got one. SSE dies for the same reason. And since `rollup` only changes once a minute (the finance-close job is the sole writer), sub-second push would be wasted precision anyway.

So: in `public/dashboard.js`, replace the one-shot `load()` on click/pageload with a `setInterval(load, …)`, polling `/api/metrics` every 15–20s — frequent enough to feel live against a once-a-minute source, cheap enough given the endpoint is already 4KB/30ms. Keep the `computed_at` field already in the response and skip the re-render when it hasn't changed, so the UI doesn't flicker every poll.

The one real fork is polling interval vs. keying off the rollup schedule directly (e.g. poll once a minute, offset a few seconds after `:00`, since polling faster than the data changes only buys smoother staleness perception, not fresher data). I'd default to the dumb short interval — it's simpler and self-corrects if the rollup schedule ever moves — unless request volume against serverless invocations is a cost concern, in which case align to the minute mark.

Left out: pausing the interval when the tab is backgrounded (`document.visibilityState`) and backoff on fetch failure — worth adding but secondary to the core mechanism.


===== T23 | case: design-upload =====
The pieces for this already exist and point at one answer: direct-to-S3 upload via presigned PUT.

**Flow:** client asks the app server for an upload slot (`POST /listings/:id/photos`, tiny JSON request); server generates a key and calls `storage.signedUrl(key, {method: 'PUT'})` — already implemented in storage.js:14-17, just unused; server returns that URL; client PUTs the photo bytes straight to S3, bypassing the app server and nginx entirely (CORS on the bucket already allows PUT from market.example.com per the storage.js comment); client then confirms success to the server, which calls `db.addPhotoKey(id, key)` (also already there). Reads reuse the existing signed-GET pattern from the invoice route.

**The fork this forces:** nginx.conf sets `client_max_body_size 1m` globally across storefront/payments/admin, and raising it or overriding it per-location was already declined because it's cited in the payments team's PCI paperwork. Phone camera photos routinely run 3-12MB, so routing the actual bytes through that listener isn't an option — direct-to-S3 is the only path that doesn't touch that limit, since only the small JSON slot-request crosses nginx.

**Consequence to decide:** without nginx enforcing a size cap, something else has to — either a `content-length-range` condition on the presigned POST/PUT policy, or a post-upload check that deletes oversized objects.

Left undecided: client-side compression vs. a server-side resize/thumbnail step — next layer down.


===== T24 | case: design-retry =====
Read through `payments.js`, `routes/checkout.js`, and `PROVIDER.md`. The root cause isn't really "no retry" — it's that a timeout is being treated as a definite failure when the vendor explicitly says it's **unknown**, and there's no idempotency key, so a naive retry-on-timeout would risk double-charging the customer. Here's how I'd design it:

**1. Send an `Idempotency-Key`, generated once per attempt and persisted before the call.**
`payments.js:8-13` builds the request body but never sets the header PROVIDER.md:15-20 describes. Without it, retrying a timed-out charge either double-charges (if the first attempt actually landed) or is unsafe to attempt at all. The key must be created and written to the `orders` row *before* the first network call, so a retry — or a resume after the process itself crashes — reuses the same key instead of generating a new one:
```js
// before calling payments.charge, atomically claim the order and stamp a key
const [order] = await db.query(
  `UPDATE orders SET status = 'processing', idempotency_key = coalesce(idempotency_key, gen_random_uuid())
   WHERE id = $1 AND status = 'pending' RETURNING id, idempotency_key, total_cents, currency, customer_id`,
  [orderId]
);
if (!order) return res.status(409).json({ status: "already processing or paid" });
```
The `AND status = 'pending'` guard also closes a separate gap: nothing currently stops two concurrent requests to `/pay` (e.g. a double-click) from both calling `payments.charge` at once.

**2. Classify the outcome, don't just catch-and-fail.**
`routes/checkout.js:20-30` treats every rejection the same — decline, network error, and timeout all fall into one `catch` that reports "payment failed". Those need to split three ways:
- **Definite decline** (4xx from Cardstream with a decline reason) — real failure, don't retry, tell the customer.
- **Timeout / connection error / 5xx** — unknown, per PROVIDER.md — retry with the *same* idempotency key.
- **429** — rate limited, back off and retry (not urgent given 600/min headroom, but cheap to handle the same way).

**3. Bounded retry with backoff, inside `payments.charge` (or a wrapper around it), same key every attempt:**
```js
async function chargeWithRetry(params, idempotencyKey, attempts = 4) {
  for (let i = 0; i < attempts; i++) {
    try {
      return await charge({ ...params, idempotencyKey });
    } catch (err) {
      if (isDefiniteDecline(err)) throw err;         // stop, real failure
      if (i === attempts - 1) throw new UnknownOutcome(err); // exhausted, still unresolved
      await sleep(backoff(i));                        // exponential + jitter
    }
  }
}
```
Because every attempt carries the same `Idempotency-Key`, Cardstream returns the original charge (same id, same body) rather than authorizing twice — that's what makes retrying safe at all here.

**4. Retries exhausting is not the same as failure.**
If all attempts time out, the true state is still unknown, not failed — the route shouldn't say "payment failed" in that case, since a customer told that will often retry manually and risk a real double-charge on top of a possibly-already-successful one. Leave the order in `processing` and return something like `202 { status: "processing" }`.

**5. Resolve `processing` orders out-of-band.**
Two ways, and I'd want to know if Cardstream offers webhooks before picking:
- If it does: a webhook handler resolves `processing` orders to `paid`/`declined` when the vendor's own async notification arrives — this is the authoritative fix for "unknown."
- If not (or as a backstop): a reconciliation job periodically re-issues `payments.charge` with the stored idempotency key for any order still `processing` past some age — safe to repeat indefinitely because of the key, and it converges to the same charge id.

That combination — idempotency key persisted before the first call, bounded in-request retries only for genuinely-unknown outcomes, and a reconciler/webhook to resolve whatever's left — is what actually fixes "payment failed" being shown for timeouts, rather than just retrying blindly and turning intermittent timeouts into intermittent double-charges.


===== T25 | case: design-audit-log =====
Two clean chokepoints already exist here: every write goes through `db.write()` (db.js:13), and every request's actor is resolved once in `sessionUser` (auth.js:5). The audit trail should hang off those two points rather than being bolted onto each route.

**Core mechanism:**

1. **Capture "who" without threading `req.user` everywhere.** `db.write()` has no access to `req`. Use Node's `AsyncLocalStorage` to stash `req.user` for the lifetime of a request (set it in `sessionUser`, right after you resolve the session), and read it back inside `db.write()`.

2. **Record the change at the database, not the app.** Add an `audit_log` table and a generic `AFTER INSERT OR UPDATE OR DELETE` trigger on each audited table, using Postgres's `OLD`/`NEW` row variables to capture the actual diff. To get the actor into the trigger, have `db.write()` run `SET LOCAL app.actor_id = $1` as the first statement inside the transaction (sourced from the AsyncLocalStorage context), and have the trigger read it with `current_setting('app.actor_id', true)`. `SET LOCAL` is transaction-scoped, so it's automatically reset and never leaks across pooled connections.

3. **Same transaction, always.** `db.write()` already wraps `BEGIN`/`COMMIT`/`ROLLBACK`. Because the trigger fires inside that same transaction, the audit row and the actual write commit or roll back together — there's no window where one succeeds without the other.

The one real fork here: trigger-based auditing vs. logging inside `db.write()` in JS. App-level logging is simpler to write and needs no SQL, but it's only as strong as the convention that everyone calls `db.write()`. A trigger is enforced by Postgres itself — it fires even if some future route runs a raw query or a migration touches the table directly, which is the property compliance actually wants from an audit trail. Given that "every write goes through `write()`" is currently just a comment, not a constraint, I'd trust the database over the convention.

Left out of this sketch, worth deciding separately: retention policy and making `audit_log` genuinely append-only (revoke UPDATE/DELETE on it from the app's DB role), whether any columns need redaction before logging (e.g. don't audit password fields verbatim), and whether reads need auditing too (you asked for writes only).


===== T26 | case: design-alerting =====
Two things push toward different alert conditions in the spec, and one of them can't be done the way the pseudocode implies:

The pseudocode (line 32) only shows `alert("quota exceeded", tenant)` as an inline call inside the per-tenant loop body, using `result.guardrail` from that single cycle. But the Observability section (lines 64-73) lists conditions like "`feed_stale` persisting past three cycles," "cap pinned... for two consecutive cycles," "pace error above 15% for two consecutive cycles," and "heartbeat missed." None of those are answerable from one cycle's `govern()` result — `govern()` is pure and stateless about history beyond what's in `state`, and "heartbeat missed" is by definition a case where the loop body never runs at all, so nothing inside it can raise that alert.

So this splits into two layers, not one:

1. **Per-cycle emission** — the supervisor emits a structured record every cycle it does run (tenant, guardrail fired, cap, pace error, whether the cap sat at a band edge, timestamp), alongside `persist_state`. This is pure plumbing, no alerting logic.
2. **A separate evaluator over that stream** — something that watches the record stream (and its absence) and fires the streak-based and heartbeat conditions: 3-consecutive-`feed_stale`, 2-consecutive pinned/pace-error, and missing-heartbeat via a "no record arrived in N minutes" check. `quota_exceeded` and `config_invalid` are single-cycle and can fire straight from the record.

The fork I can't resolve for you: what emits/evaluates that stream. If there's already a metrics stack (Prometheus, Datadog, CloudWatch), the per-cycle record is just tagged metrics/events and the streak logic is alerting rules in that system — no custom evaluator to write. If there's nothing yet, someone has to build the small stateful evaluator in (2). Which one is it?


===== T27 | case: design-alerting =====
Core approach: extend `govern()`'s pure output beyond the single winning guardrail (guardrails are priority-ordered, first match wins, per line 46) to a separate set of alert signals computed from the same state/inputs every cycle — since several alert conditions (cap pinned two cycles, pace error two cycles, feed_stale past three cycles) need consecutive-cycle tracking that's independent of which guardrail wins the cap decision that cycle. Add streak counters to the persisted state (feed_stale already implies one per line 51-52; add cap_pinned and pace_error streaks) so `govern()` can decide "threshold crossed" purely, with no clock or I/O — same property that makes the simulation harness work. The supervisor then loops over `result.alerts` and calls the real alert sink, generalizing the existing `alert("quota exceeded", tenant)` line to every condition in the list.

Two things that genuinely fork this:

1. **Heartbeat missed can't come from inside the loop** — if the loop didn't run, nothing executes to raise it. That needs an external dead-man's-switch: the supervisor writes a per-tenant last-run heartbeat after each successful cycle, and a separate watchdog (cron, Prometheus `absent()`, or a healthchecks.io-style pinger) fires the alert when a tenant's heartbeat goes stale past the 5-minute interval plus grace period.
2. **Dedup/resolve** — firing `alert()` every 5 minutes for an ongoing condition (e.g. `floor_at_risk` staying true for hours) pages on-call every cycle. Cleanest fix is a dedup key per (tenant, condition) at the alert sink, with an explicit resolve call when `govern()` sees the streak reset to 0.

Left out at this level: the exact streak thresholds and whether a lower-priority guardrail's streak keeps incrementing while preempted by a higher-priority one — that's the next layer down.


===== T28 | case: design-audit-log =====
Read through `db.js`, `auth.js`, and both route files. This is a small Express/Postgres service with one real chokepoint: `db.write()` opens the transaction for every write in the app. That chokepoint is the anchor for the audit trail — the question is what to attach to it.

**Recommend:** a generic Postgres trigger, not application-level logging calls.

- Add an `audit_log` table (`table_name`, `row_id`, `action`, `old_row jsonb`, `new_row jsonb`, `changed_by`, `changed_at`, `txid`), populated by one trigger function using `row_to_json(OLD)`/`row_to_json(NEW)`, attached to `accounts`, `orders`, and any other audited table.
- `changed_at` comes from the trigger (`now()`), not the app clock — an app-supplied timestamp is trivially wrong or spoofable.
- Revoke `UPDATE`/`DELETE` on `audit_log` from the app's DB role, so it's append-only even to a compromised app process.

**The one fork that matters: how "who" reaches the trigger.** A trigger has no access to `req.user`. Two ways to bridge that:
1. `db.write()` runs `SET LOCAL app.user_id = $1` right after `BEGIN`, using the same connection/transaction it already owns, and the trigger reads it via `current_setting('app.user_id')`.
2. Skip triggers, log explicitly in each route handler instead.

Go with (1). It's forced by what's already in the code: `db.write()` is the *only* place a transaction begins, so it's the only place that's guaranteed to run for every write, present and future — a route handler can forget to log, a trigger can't. It also means DB-level requirement, not per-call-site discipline, is what makes "for every write" true. The cost: every `db.write()` call site needs to start passing the acting user's id, which none currently do — `accounts.js` and `orders.js` call `db.write()` without `req.user` at all, so that plumbing is new work, not a tweak.

Depth I left out: retention/partitioning policy for `audit_log` growth, whether `sessions`/`users` writes belong in scope, and how a `req.user`-less write (migrations, cron jobs) should populate `changed_by`.


===== T29 | case: design-rate-limit =====
Grounding in what's actually here: `routes/api.js` resolves `req.client` (with a `plan` tier) from the API key before any handler runs, `redis.js` is already the one piece of state shared across all workers/boxes, and `app.js`'s own comment flags that IP is unreliable — clients share NAT'd addresses, so IP-keyed limiting would throttle innocent clients sharing an address with the offender and miss one spread across several.

**Recommendation:** a token-bucket limiter keyed on `req.client.client_id`, enforced in Redis via a Lua script (atomic `EVAL`), as a middleware inserted right after the existing auth middleware in `routes/api.js` — before any DB query runs, so a client that's over budget never touches Postgres.

Two decisions actually fork this:

- **Key by `client_id`, not IP.** The auth middleware already resolves it on every request, and it's the only identifier that's actually 1:1 with "the misbehaving caller" given shared NATs.
- **Atomic Lua script, not `INCR`+`EXPIRE`.** With 4 workers per box across multiple boxes all hitting the same Redis, two workers can each `GET`, both see room, both `INCR` — the check-then-act isn't atomic unless it's one round trip. A Lua script (or `redis-cell`/a token-bucket module) makes the check-and-decrement a single atomic op.

Left out at this depth: whether limits vary by `plan` (the column's already there, suggesting tiered limits), per-endpoint vs. account-wide budgets (`POST /reports` is presumably more expensive than `GET`), what a 429 response looks like (`Retry-After` header, body shape), and whether it's global-only or box-local-plus-global for defense in depth.


===== T30 | case: design-realtime =====
WebSockets are off the table — `PLATFORM.md` says connection upgrades 501 at the edge, and SSE is equally dead since instances freeze the moment a response is sent, killing any held-open stream. That leaves client-side polling, which fits well here: `jobs/rollup.md` says the data only changes once a minute, so sub-second push would solve a problem that doesn't exist.

The fork is polling strategy: a fixed interval (e.g. poll `/api/metrics` every 20s, compare `computed_at` client-side to skip re-rendering unchanged rows) versus adaptive polling, using the returned `computed_at` to schedule the next fetch for just after the minute boundary instead of a flat interval. Adaptive cuts request volume roughly 3x and shrinks worst-case staleness from ~interval to seconds after the rollup writes, at the cost of a little drift-tracking logic. Since `metrics.js` is already 30ms/4KB, either is cheap — I'd start with the fixed interval and only move to alignment if call volume becomes a concern.

Left out: pausing polling on a hidden tab (Page Visibility API) and backoff on fetch failure — both are small additions once the polling loop exists.


===== T31 | case: design-cache =====
The 900ms is almost entirely `db.relatedProducts` (~600ms, four-table join) plus `stockFor` (~250ms) — and `/p/:slug` is anonymous and identical for every visitor (`routes/products.js:6-8`). That makes it a textbook case for the CDN that's already sitting in front of every request, except `middleware/security.js:7-9` sends `no-store` app-wide, so the CDN never gets a chance (0% hit rate per `CDN.md`). That blanket header was a fast fix for one audit finding on `/account` (`middleware/security.js:1-6`), not a considered policy for `/p`.

The actual fork is: don't cache the page as one unit. Two things on it move at very different speeds — catalog data (product/related, edited "a few times a day") versus stock (inventory, which changes on every order). One TTL for both either shows stale "in stock" badges or caches so briefly it barely helps.

**Recommended shape:**
- Scope `Cache-Control` per-route instead of globally: `/account` keeps `no-store, private` (that data is genuinely per-user and the original leak risk is real there); `/p/:slug` gets `public, max-age=<catalog-cadence>` since nothing on it varies by session or cookie, so a shared CDN cache is safe.
- Pull `stockFor` out of the cached response — either an edge-side include / separate small endpoint the page fetches client-side, or give it its own short microcache (seconds, not minutes). Otherwise stock staleness gets bounded by whatever TTL you pick for the catalog data.
- Pick the catalog TTL against how the admin tool publishes edits: if it can call a purge endpoint on save, TTL can be long (hours) with active invalidation; if not, TTL has to be short enough that "a few times a day" staleness is tolerable (minutes).

Depth I'm leaving out: whether the admin tool has (or could get) a purge hook — that decides whether this is a pure TTL cache or needs invalidation plumbing, and I don't have that answer from what's here.


===== T32 | case: design-cache =====
The blocker isn't missing cache infrastructure — it's `middleware/security.js` forcing `no-store` on every route, including `/p`. The CDN already sits in front, already respects origin `Cache-Control`, and site-wide hit rate is 0% because of that one header. Fixing the header is the actual fix; no new caching layer needed.

Two changes:
- Scope the no-store policy to `/account` only (that's where the 2024 leak happened — per-user order data). Leave `security` applied there, or split it into a shared header set (X-Frame-Options, nosniff) plus a per-route cache directive.
- On `/p`, send `Cache-Control: public, max-age=<N>` (or `s-maxage` if you want CDN and browser TTLs to differ) sized to "catalogue changes a few times a day" — something like 5–15 minutes with `stale-while-revalidate` so an edit doesn't need a manual purge to show up.

The fork you'll need to resolve: **stock is bundled into the same page** and moves faster than the catalogue copy does. Cache the whole page at that TTL and stock can read stale for the same window, or split stock out (client-side fetch, or an edge include) so the catalogue portion gets the long TTL while stock stays near-real-time. Which one's right depends on how wrong a stale "in stock" can be for you — that's the piece I can't decide from the code alone.


===== T33 | case: design-rate-limit =====
Recommendation: a token-bucket counter in Redis, keyed by `client_id`, enforced in a new middleware in `routes/api.js` right after the existing auth middleware (`req.client` is already resolved there).

Two things this codebase specifically forces:

- **State has to live in Redis, not in-process.** `app.js` forks 4 workers per box with nothing shared in module scope, and `redis.js` is already the one thing every worker on every box has in common. An in-memory counter would only ever see one worker's slice of that client's traffic.
- **Key by `client_id`, not IP.** The auth middleware's comment says several clients can share an address behind the same NAT — rate-limiting by IP either throttles innocent tenants sharing that NAT or lets the abusive client keep switching addresses. `client_id` is already resolved before the route handlers run, so the limiter slots in as another `router.use()` right after it, using `plan` for the threshold.

The one real fork is fixed-window `INCR` + `EXPIRE` vs. a token-bucket Lua script. Fixed-window is one round trip and trivial to write, but lets a client burst up to 2x the limit across a window boundary. A Lua script (still one round trip, since Lua runs atomically in Redis) gives you a real token bucket with smooth refill and no edge-burst — worth the extra ~15 lines given this is specifically a "smooth out one noisy client" problem, not a hard quota. On limit breach, return 429 with `Retry-After` rather than queuing — queuing a hammering client just holds worker resources longer, which is the opposite of what you want here.

Left out: what the limiter does if Redis itself is slow or down (fail open and let traffic through, or fail closed and reject everyone) — that's a real decision but separate from the rate-limit design itself.


===== T34 | case: design-cache =====
Read the code — this maps cleanly onto what's there.

**The fork that matters:** `middleware/security.js` sets `no-store` app-wide because of a 2024 audit finding that was actually about `/account` leaking through an intermediary cache. It got applied globally as the fastest fix, and `/p` has been paying for it ever since — that's why the CDN sitting right in front of every request has a 0% hit rate on a page that's confirmed anonymous (no session read, same data for everyone). Split that middleware: `/account` keeps `no-store, private`, `/p` gets a real `Cache-Control: public, max-age=...`. The CDN already respects whatever origin sends and needs no path rules, so this alone lets the existing edge absorb repeat hits on the same slug — for free, without touching the DB layer.

**Second fork: page-level vs query-level caching.** `relatedProducts` (600ms, four-way join) and `stockFor` (250ms) are where the time is, and they don't age at the same rate — the catalog only changes a few times a day via the admin tool, but stock is the number most likely to go stale in a way that matters. A single edge TTL on the whole rendered page forces one expiry for both. An app-level cache (Redis, or even in-process) in front of `db.js` lets `relatedProducts`/`productBySlug` sit on a long TTL close to "until the next admin edit" while `stockFor` gets a much shorter one or gets excluded and fetched live. That's more moving parts than just fixing the header, so it's only worth it if edge caching alone doesn't get you far enough — worth measuring after step one before building it.

Left out: invalidation on admin edits (purge-on-write vs TTL-only), and how stale stock is acceptable to show on a display-only page — that's a product call, not something to default on.


===== T35 | case: design-cache =====
Root cause first: the CDN already sits in front of every request and honors origin `Cache-Control` — the 0% hit rate isn't a CDN gap, it's `middleware/security.js` sending `no-store, no-cache, must-revalidate, private` app-wide, applied to `/p` along with `/account` after the 2024 audit. The product page is fully anonymous (no session read, same price/stock/copy for everyone), so it's cacheable and just isn't being cached.

Fix: scope that middleware to `/account` only, and give `/p` a real `Cache-Control: public, max-age=...`. That alone lets the existing CDN absorb most traffic to the page whose DB cost is ~900ms (`relatedProducts` ~600ms, `stockFor` ~250ms, `productBySlug` ~40ms).

The one real fork is what TTL to use, because `stockFor` and the rest don't change at the same rate: catalog/related data only moves when admin edits a product (a few times a day), but stock moves with every order. Two options:
- **Single page-level TTL** (e.g. 30–60s): simplest, one Cache-Control line, but stock can show stale for up to the TTL window.
- **Split stock out**: cache the page (product + related) at a longer TTL, fetch stock via a separate short-TTL or uncached call. More moving parts, only worth it if a minute of stale "in stock" is actually a problem for this catalog.

For most storefronts a minute of stock staleness is fine, so I'd start with the single TTL and only split if that proves wrong in practice.

Left out: cache invalidation on admin edits (push a purge instead of waiting out the TTL) and whether misses still need an app-level cache (e.g. Redis for the `relatedProducts` join) — worth a follow-up once hit rate is measured.


===== T36 | case: design-realtime =====
WebSockets and SSE are both off the table here: `PLATFORM.md` says connection upgrades 501 at the edge, instances freeze between invocations, there's no sticky routing, and functions die at 10s — nothing can hold a connection open. And `rollup.md` shows the data itself only changes once a minute, on a fixed schedule you can't shorten, so a push channel wouldn't even buy you fresher data.

That leaves polling, which is really just deleting the "click refresh" step: in `public/dashboard.js`, replace the click-only `load()` with a `setInterval` that calls it periodically, keeping `window.addEventListener('load', load)` for the initial render.

Two things actually fork the design:

1. **Poll cadence** — a dumb fixed interval (e.g. every 20–30s) is simplest, but since `computed_at` only ever moves right after the minute boundary, you could instead poll once a minute timed a few seconds after `:00`. Fewer wasted requests, but now the client is guessing at the job's schedule instead of just being told.
2. **Re-render on every poll vs. only on change** — compare the new `computed_at` to the last one and skip `render()` if it's identical. Given the endpoint is 4KB/30ms this isn't for load, it's to stop the UI flickering or resetting scroll/selection state every poll when nothing changed.

Left out: pausing the interval on `visibilitychange` (`document.hidden`) so backgrounded tabs stop polling — worth adding, not part of the core fork.


===== T37 | case: design-cache =====
Root cause: `middleware/security.js` sets `no-store` on every route app-wide, so the CDN (which honors origin headers and nothing else) never caches anything — that's the 0% hit rate. It was written to fix a real leak on `/account`, but got applied to `/p` too, which is the actual bug here: `/p/:slug` reads no session and is identical for every visitor.

**Approach:** scope that middleware to `/account` only (or the account router specifically), and give `/p` its own policy: `Cache-Control: public, max-age=<N>, stale-while-revalidate=<M>`. That lets the CDN serve the page in ~0ms on a hit and revalidate in the background, which is where the 900ms actually goes — `relatedProducts` (600ms) and `stockFor` (250ms) are both keyed only by product id, not by user, so they're cacheable by definition, not just by convenience.

**The fork I can't resolve for you:** stock changes faster than catalog data (admin edits a few times/day vs. inventory moving on every order), but both are currently rendered into the same page. One TTL for the whole page means either:
- accept stock lagging by up to `max-age` (fine if the page shows "in stock" loosely, not exact counts), or
- split stock out of the cached shell — cache `product` + `related` at the edge with a longer TTL, fetch stock separately (client-side call, or a short-TTL app-side cache like Redis) so it stays near-live without dragging the 600ms join back onto every request.

Which one depends on how precise "in stock" needs to be on that page — that's a product call, not an engineering one.

Left out at this depth: exact TTL/SWR numbers, how a product edit invalidates the cache (purge vs. just waiting out the TTL), and whether `relatedProducts` also deserves an app-side cache (e.g. Redis) as a backstop for CDN misses/revalidation, independent of the edge policy.


===== T38 | case: design-upload =====
Direct-to-S3 is forced here, not just preferred: nginx's `client_max_body_size` is `1m` globally (nginx.conf:12), and that limit is deliberately not overridable per-location because the payments team ties it to PCI scope on the same listener. A phone camera photo (2-8MB typical) will 413 through that proxy no matter what Express does with it, so the upload can't go through `/` to the storefront at all.

The pieces for direct-to-S3 already exist, just unused for writes: `storage.js` computes signed URLs and already supports `method: 'PUT'` (storage.js:14-16), and the bucket CORS already allows PUT from `market.example.com` (storage.js:13). The pattern to follow is the same one `invoice_key` uses for reads, mirrored for writes:

1. Client asks Express for a signed PUT URL for a new key (e.g. `POST /:id/photos` generates a key like `listings/{id}/{uuid}.jpg`, calls `storage.signedUrl(key, {method: 'PUT'})`, returns `{key, url}`). This request is tiny (JSON), so it's fine going through nginx.
2. Browser PUTs the photo bytes straight to that signed S3 URL — bypassing nginx and Express entirely, so the 1MB limit never applies.
3. Server records the key against the listing, via `db.addPhotoKey(id, key)` (db.js:10-12), which already appends into `photo_keys`.

The one real fork is how step 3 gets triggered: have the client call back to Express to confirm after the PUT succeeds (simple, one more small endpoint, but a client that never calls back leaves an orphaned S3 object and a listing with no photo), or use an S3 event notification (Lambda/SQS on `ObjectCreated`) to append the key server-side (no missed writes, but new infra to stand up). For a first version, client-confirm is the shorter path; the orphan case is cheap to clean up later with a bucket lifecycle rule on unconfirmed keys.

Left out: client-side compression/resizing before upload, multi-photo ordering/cover-photo selection, and content-type/file-size validation on the signed URL (S3 supports conditions on presigned POST/PUT if that's wanted).


===== T39 | case: design-realtime =====
Since this platform can't do WebSockets (connection upgrades 501 at the edge) or hold any long-lived connection (functions die at 10s, instances freeze between calls, no sticky routing), and the underlying `rollup` table only changes once a minute on the minute, the actual answer is client-side polling against the existing `/api/metrics` endpoint — that's not one option among several here, it's what the constraints leave you.

Concretely: in `public/dashboard.js`, replace the load-once/click-to-refresh wiring with `setInterval(load, ...)`, and inside `load()` skip the re-render if the returned `computed_at` hasn't changed since last time (rows are byte-identical between rewrites, so no point diffing/rendering when the stamp is stale). `/api/metrics` is already cheap (4KB/30ms, `no-store`), so this is fine load-wise even at a short interval.

One real decision: fixed-interval polling (e.g. every 15s, simple) vs. aligning the poll to just after each `:00` since that's the only moment the answer can change. I'd align to the minute — polling faster than the rollup writes just burns invocations for a stamp that hasn't moved.

Left out: backoff/error handling on failed fetches, jittering the aligned poll across clients so you don't send a burst of requests all landing at `:00.05`, and pausing the interval via the Page Visibility API when the tab isn't foregrounded.


===== T40 | case: design-upload =====
Recommendation: client resizes/compresses the photo (and converts HEIC to JPEG) before upload, then uploads directly to object storage via a short-lived presigned URL rather than routing bytes through your app server; a background job then generates thumbnails and validates the file server-side.

Two decisions actually fork this:
- **Direct-to-storage vs. proxy through your backend** — presigned URLs (S3/GCS/R2) keep large phone-camera files (often 4–12MB, HEIC on iPhones) off your app servers and handle flaky mobile connections better with resumable/retryable puts. A proxy is simpler to build but doubles bandwidth and chokes under concurrent uploads.
- **Where compression happens** — doing it client-side (canvas/WASM resize to something like a 2048px long edge, JPEG/WebP output) cuts upload time and mobile data cost, but adds client complexity and a compatibility tail (older Android browsers, HEIC support). Skipping it and compressing server-side after upload is simpler but means sellers on weak connections wait longer and burn more data per photo.

Left out: multi-photo ordering/reordering UI, malware/content scanning, and CDN/delivery sizing for the listing page — all straightforward once the upload path above is fixed.


===== T41 | case: design-alerting =====
Looking at the doc, "alerting" shows up in two places: the pseudocode's `alert("quota exceeded", tenant)` (SPEC.md:32) and the eight-condition list in Observability (SPEC.md:64-73). Here's how I'd build it, given the constraints the doc already sets:

**1. Alerting lives in the supervisor, not in `govern()`.**
The Core purity section (SPEC.md:37-42) is explicit: `govern()` takes state+inputs and returns a decision, no I/O. Sending an alert is I/O, so it can't happen inside the core — it has to happen in the impure shell, exactly as the pseudocode already does for `quota_exceeded` (line 31-32). The other guardrail-driven alerts (`floor_at_risk`, `floor_unreachable`, `config_invalid`) are the same pattern: check `result.guardrail` after each call and fire.

**2. The eight conditions split into three buckets by what they need:**

- **Direct, single-cycle:** `quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid`. These are just `result.guardrail` values — one `if` per condition in the supervisor, same as the existing line.

- **Consecutive-cycle conditions:** `feed_stale` past three cycles, cap pinned at a band edge for two cycles, pace error >15% for two cycles. These need memory across cycles. Note the spec already implies `govern()` tracks a stale-cycle counter internally, since it's the thing deciding when to fall back to the default cap after three stale cycles (SPEC.md:50-52). The consistent move is to extend that same mechanism: carry streak counters (stale-cycles, clamp-cycles, pace-error-cycles) in the persisted `state`, compute the threshold crossings inside `govern()`, and surface them on the result (e.g. a `result.alerts` list) alongside `result.guardrail`. That keeps the core pure — counters are just state — and keeps these alert conditions inside the same simulation/unit-test ladder the doc leans on (SPEC.md:39-42), instead of needing separate supervisor-level integration tests to exercise them.

- **Absence condition:** "Supervisor heartbeat missed." This is the odd one out — nothing inside the 5-minute loop can raise it, because the loop not running is the failure. It needs an external watchdog: each successful cycle stamps a liveness marker (last-run timestamp per tenant, or a fleet-wide counter), and a separate always-on check — a dead-man's-switch alert, or a monitoring rule like Prometheus/Alertmanager's `absent()` — fires when that marker goes stale.

**3. Guard against alert storms.** Several guardrails hold for many consecutive cycles by design — `quota_exceeded` holds until day rollover, `floor_unreachable` can persist for a while. If the supervisor calls `alert()` on every cycle the condition is still true, that's a page every five minutes. Alerting should be edge-triggered (fire on transition into the condition, not on every cycle it remains true), or routed through an alert manager that dedups/groups on a `(tenant, condition)` fingerprint with its own re-notify cadence.

**4. What `alert()` actually does is unspecified.** SPEC.md never says where alerts go — pager, ticket, chat. Building it means picking a sink and a severity/routing table, e.g. page on `quota_exceeded`/`floor_unreachable` (contract-breaking), lower-severity ticket/Slack on `config_invalid`/`cap_clamped`-adjacent conditions. That's a decision the doc leaves open, not something answerable from the text alone.


===== T42 | case: design-rate-limit =====
Recommendation: enforce it at the gateway/edge, keyed by API key or auth token (not IP), using a token-bucket algorithm backed by a shared store like Redis, returning `429` with `Retry-After` when a client exceeds its bucket.

The forks that actually matter:
- **Identify by credential, not IP.** IP is unreliable — NAT, shared proxies, easily rotated. A key/token ties the limit to the actual client.
- **Enforce before the request reaches app logic**, not inside a handler. If the check happens after routing/auth/DB work has already run, the abusive client still burns the capacity you're trying to protect — the limiter has to sit in front of that, e.g. as gateway middleware.
- **Centralize the counters** (Redis `INCR`+`EXPIRE`, or a Lua script for atomicity) if `/v1` runs on more than one instance. Per-process in-memory counters let the offending client dodge the limit just by landing on a different replica via the load balancer.

Left out at this depth: the actual rate/burst numbers, whether limits are global or per-endpoint, and whether you want tiered limits by plan — those are tuning decisions once the mechanism above is in place.


===== T43 | case: design-cache =====
Traced it end to end — root cause and fix are clear.

**Root cause:** `middleware/security.js:8` applies `Cache-Control: no-store, no-cache, must-revalidate, private` to *every* route via `app.use(security)` in `app.js:9`, including `/p/:slug`. That blanket policy was the fast fix for a 2024 audit finding about `/account/orders` leaking between users — but it was never scoped down, so it also kills caching for `/p`, which is fully anonymous (`routes/products.js:6-7`: no session read, nothing varies by user). Per `CDN.md`, the CDN already sits in front of everything and honors whatever `Cache-Control` the origin sends with no path rules — so the 0% hit rate is just this header, not a CDN limitation. That's the highest-leverage fix available: it costs no new infrastructure.

**Design**

1. **Split the security middleware by route class.** Keep `/account` exactly as-is (still `no-store, private` — don't touch the thing the audit fixed). Give `/p` its own policy: `Cache-Control: public, max-age=60, stale-while-revalidate=300`. Mount it as `app.use('/account', security)` plus a separate `publicCache` middleware on the products router, rather than the current global `app.use(security)`.

2. **Let the CDN absorb almost all traffic.** Once `/p` sends a public, cacheable header, the existing edge cache starts serving hits with zero origin traffic — the full 900ms disappears for any request that lands inside the TTL window. Given catalog edits happen "a few times a day," a TTL of 30–60s with `stale-while-revalidate` is generous: it bounds staleness to under a minute without needing a purge pipeline.

3. **Decide how to handle stock.** `stockFor` (`db.js:18-20`, ~250ms) changes on every order, faster than the CDN TTL tolerates for some businesses. Two options: (a) accept the same bounded staleness as the rest of the page — most storefronts already treat "in stock" as advisory and reconcile at checkout — or (b) exclude stock from the cached HTML and fetch it as a small separate request the client makes on load, so the shell is cacheable at a longer TTL and stock stays live. (a) is simpler and matches what the code comment already implies is acceptable; only reach for (b) if product actually needs real-time inventory display.

4. **Add an application-layer cache for the CDN-miss path.** Every TTL expiry, first-touch, and long-tail/cold product still hits the origin, and `relatedProducts` (`db.js:9-16`, ~600ms — a four-table self-join) is the expensive part of that. Cache its result in Redis (or in-process LRU if single-instance) keyed by product id, TTL ~60s, so a CDN miss doesn't still cost 600ms at the DB. This also protects the DB from a thundering herd if many product pages expire around the same time.

5. **Skip building precise invalidation.** Given edits are infrequent, a purge-on-admin-write pipeline (CDN path purge + Redis key delete) is real complexity — cross-invalidating `relatedProducts` is messy since editing one product's tags can change *other* products' related lists too. The TTL + stale-while-revalidate approach sidesteps that: worst case is ~60s of staleness after an edit, which is likely fine for a catalog that changes a few times a day. Only add explicit invalidation later if that staleness window turns out to matter.

6. **Separately, `stockFor`'s 250ms is suspicious for a single-table aggregate** — worth checking for a missing index on `inventory(product_id)` regardless of caching, since that's DB tuning, not a caching problem.

Net effect: cache hits (should become the large majority of traffic) drop from 900ms to CDN latency; cache misses drop from 900ms to roughly `productBySlug`'s 40ms once `relatedProducts`/`stockFor` are Redis-cached. `/account` is untouched.


===== T44 | case: design-alerting =====
Two of the eight alert conditions are single-cycle (`quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid` — directly readable off `result.guardrail`), but three need cross-cycle memory (`feed_stale` × 3, cap pinned × 2, pace error × 2), and one (`heartbeat missed`) can't be detected from inside the loop at all, since by definition it's the case where the loop didn't run.

Build it as: add small counters (`stale_cycles`, `pin_cycles`, `pace_error_cycles`) to the persisted controller state — it's already read and written every cycle, so this is free — and evaluate all the in-loop alert conditions in the supervisor right after `govern()` returns, never inside `govern()` itself, so the pure-core/simulation-harness property in the spec stays intact. Heartbeat-missed has to be a separate watchdog outside the per-tenant loop (e.g. something checking "time since last persisted cycle" per tenant on its own schedule), since the loop alerting on its own absence is a contradiction.

Left out: actual notification routing/dedup and alert-fatigue thresholds (e.g. does pace-error-15%-for-2-cycles page someone every 5 minutes until it clears?) — that's the next layer down.


===== T45 | case: design-realtime =====
Polling is the only viable transport here — WebSockets are dead at the edge (`PLATFORM.md:9-10`, 501 on upgrade) and SSE/long-poll would just get killed by the 10s function limit (`PLATFORM.md:8`) with no sticky routing to resume on (`PLATFORM.md:11`). So the browser has to ask.

Replace the load-once-plus-button-click in `public/dashboard.js:1-11` with a `setInterval` calling the same `/api/metrics` endpoint, comparing the returned `computed_at` against the last-seen value and only re-rendering on change. Two things make this cheap rather than wasteful:

- **Poll interval vs. data cadence**: rollup only changes once a minute (`jobs/rollup.md:3`), so polling every 15-20s catches each update within seconds without needing to be faster than the source. No point polling every 2s.
- **Stop polling when nobody's looking**: pause the interval on `visibilitychange` (tab hidden) and resume + immediately fetch on visible again, so idle tabs don't keep invoking the function.

`/api/metrics` itself needs no changes — it's already a 30ms/4KB read with `Cache-Control: no-store` (`api/metrics.js:6-8`), so it can absorb the extra call volume as-is.

Left out: exponential backoff on fetch failure, and whether to surface a "data is N seconds old" staleness indicator — both are refinements, not forks.


===== T46 | case: design-cache =====
Here's what's actually happening and how I'd fix it.

**Root cause of the 0% hit rate**

`middleware/security.js:8-9` sets `no-store, no-cache, must-revalidate, private` on every response, applied app-wide in `app.js:9`. The comment explains why: an audit finding about `/account/orders` leaking between users via an intermediary cache, fixed the fast way by banning caching everywhere. `CDN.md` confirms the CDN honors whatever `Cache-Control` the origin sends — so the CDN isn't the problem, the app is telling it never to cache anything, including `/p/:slug`, which is fully anonymous and identical for every user (`routes/products.js:6-8`).

So step one, before any new caching layer: **stop applying that middleware to `/p`**. Keep it exactly as-is for `/account` — that finding was real and shouldn't be touched. Scope it to the account router only (or invert to an explicit allowlist), so `/p` is free to set its own policy.

**Edge (CDN) caching for the product page**

Since `/p/:slug` reads no session and varies by nothing user-specific, it's a textbook shared-cache candidate. Once it's out from under the blanket `no-store`:

- `Cache-Control: public, max-age=<N>, stale-while-revalidate=<M>` on the product route response.
- `stale-while-revalidate` matters most here: it lets the CDN serve the cached page instantly while refreshing in the background, so the ~900ms DB cost is paid by a background revalidation, not by a user's request.
- One thing to verify before flipping this on: nothing in the request path sets a per-request cookie (e.g., a session cookie issued even to anonymous visitors) on the `/p` response. If it does, most CDNs will either refuse to cache it or fragment the cache per cookie, silently keeping the hit rate near zero even with the right headers.

**Sizing the TTL against the two data sources**

The 900ms splits roughly into `productBySlug` (~40ms), `relatedProducts` (~600ms), `stockFor` (~250ms) (`db.js:4-20`), and they don't change at the same rate:

- Catalog/related-product data changes "a few times a day" via the admin tool — a TTL of minutes-to-an-hour is safe, or better, push-invalidate: have the admin save action purge the CDN entry (and any app-level cache key) for that slug, so edits go live immediately instead of waiting out a TTL.
- Stock (`sum(quantity)`) moves with every order, so baking it into a long-TTL cached page will show wrong availability. Two reasonable options: (a) give the whole page a short TTL (seconds, with `stale-while-revalidate` covering the rest), accepting that stock can be briefly stale, which is how most storefronts already behave; or (b) strip exact stock out of the cached HTML and fetch it client-side from a small, uncached, cheap endpoint — that keeps the expensive part of the page (the 600ms join) cacheable for a long time while stock stays live.

**App-level cache as a second line of defense**

Edge cache misses still happen — first hit per POP, purges, long-tail slugs — and those requests shouldn't fall all the way through to the 600ms join every time. Put `relatedProducts` (the dominant cost) behind an app-level cache (Redis/Memcached) keyed by product id, TTL matching the catalog change cadence, invalidated the same way as the CDN entry on admin save. `productBySlug` is cheap enough that caching it is optional, but it's free to add to the same layer since it's also not per-user.

**What stays untouched**

`/account/orders` (`routes/account.js`) keeps `no-store, private` exactly as it is — it's genuinely per-user and that's the correct policy. The fix here is narrowing the middleware's scope, not weakening it.

**Net effect**: `/p/:slug` moves from "0% hit rate, 900ms on every request" to mostly edge-served with sub-millisecond latency, cold/miss requests dropping to roughly 40-90ms via the app-level cache instead of 900ms, and the account pages' cache-proofing left exactly as strict as the audit required.


===== T47 | case: design-audit-log =====
Given this codebase (Express + Postgres, `pg` via `db.js`), the natural hook is `db.write()` at db.js:13-26 — every write already funnels through one `BEGIN`/transaction block. But logging only there is bypassable by anything that touches Postgres outside your app: migrations, an ops script, someone in `psql`. Since compliance said "every write," I'd enforce it at the database level with triggers, not just in the app.

**Design:**

1. **Actor identity rides into the transaction as a session variable.** `sessionUser` (auth.js:5-13) already resolves `req.user` before every route runs. In `db.write()`, right after `BEGIN`, add:
   ```js
   await client.query("SET LOCAL app.user_id = $1", [userId]);
   ```
   `SET LOCAL` scopes it to the transaction, so it can't leak across pooled connections. This means threading `req.user.id` into `write()` calls — a param addition, four call sites to touch (accounts.js, orders.js).

2. **A generic trigger writes to an append-only `audit_log` table**, independent of app code:
   ```sql
   CREATE TABLE audit_log (
     id          bigserial PRIMARY KEY,
     occurred_at timestamptz NOT NULL DEFAULT now(),
     actor_id    uuid,                 -- from current_setting('app.user_id', true)
     table_name  text NOT NULL,
     row_pk      text NOT NULL,
     action      text NOT NULL,        -- INSERT/UPDATE/DELETE
     old_row     jsonb,
     new_row     jsonb
   );

   CREATE FUNCTION audit_trigger() RETURNS trigger AS $$
   BEGIN
     INSERT INTO audit_log(actor_id, table_name, row_pk, action, old_row, new_row)
     VALUES (
       nullif(current_setting('app.user_id', true), '')::uuid,
       TG_TABLE_NAME,
       coalesce(NEW.id, OLD.id)::text,
       TG_OP,
       CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,
       CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END
     );
     RETURN NULL;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER accounts_audit AFTER INSERT OR UPDATE OR DELETE ON accounts
     FOR EACH ROW EXECUTE FUNCTION audit_trigger();
   -- repeat per audited table (orders, users, ...)
   ```
   This catches every write regardless of path, and it rides in the same transaction as the write it's logging — no risk of the log and the change diverging.

3. **Make it tamper-resistant**: `REVOKE UPDATE, DELETE ON audit_log FROM app_role;` so the application's own DB user can only `INSERT` into it, never rewrite history. If the compliance requirement extends to detecting tampering (not just recording it), the next level down is hash-chaining each row (`hash = sha256(prev_hash || row)`), or shipping rows to an external WORM sink — skip that unless they specifically ask for it.

The fork that matters: trigger-based (DB-enforced, catches everything, costs you the `SET LOCAL` plumbing) vs. wrapping `db.write()` in app code only (simpler, one file, but silently misses anything that writes outside that function). Given "for every write" is compliance language, I'd go with triggers.


===== T48 | case: design-alerting =====
Two categories of alert conditions in SPEC.md, and they need different mechanisms:

**1. Per-cycle conditions already visible inside `govern()`'s output** — `quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid`. These map directly to `result.guardrail`, so the supervisor step in the pseudocode (`if result.guardrail == "..."`) is the natural place to fire them, same as it already does for `quota_exceeded`.

**2. Multi-cycle conditions that need history** — `feed_stale` past three cycles, cap pinned for two consecutive cycles, pace error >15% for two consecutive cycles. `govern()` already has to track a consecutive-stale counter internally (for the three-cycle fallback-to-default logic), so the cleanest place for the *other* counters (consecutive pinned, consecutive pace-error) is the same persisted `state` object, and `govern()` should emit the resulting alert conditions as part of its return value alongside `guardrail`. That keeps alert derivation pure and inside the tested/replayable core, rather than as separate stateful logic bolted onto the supervisor — consistent with the "Core purity" section's whole point (unit tests can assert on alert conditions the same way they assert on guardrails, and the simulation harness can replay the shadow week to verify alert firing too, not just caps).

So `govern()`'s signature would grow from `(cap, state, guardrail)` to something like `(cap, state, guardrail, alerts[])`, and the supervisor becomes purely a dispatcher: for each entry in `result.alerts`, call out to whatever alert sink is in use (PagerDuty/Slack/internal alertmanager), same I/O-at-the-edge pattern as `apply_cap`/`persist_state`.

**One condition can't come from inside the loop at all: "supervisor heartbeat missed."** If the loop didn't run, nothing executes to raise that alert. That needs an external dead-man's-switch: each successful cycle writes a heartbeat timestamp (per tenant, or fleet-wide), and a separate always-on watchdog — a cron check, or a monitoring service — alerts when that timestamp goes stale, independent of the tenant control loop.

**Worth deciding explicitly: edge-triggered vs. level-triggered alerting.** The pseudocode fires `alert()` every cycle the condition is true, and `quota_exceeded` can hold for the rest of the day (~288 cycles at 5-minute intervals). Either the alert sink needs to dedupe by a fingerprint (tenant + condition) and auto-resolve when it clears, or the supervisor should only alert on the state transition (condition newly true), plus maybe a periodic re-notify. That choice belongs in the observability section but isn't currently specified.


===== T49 | case: design-cache =====
Recommendation: cache-aside at the query/object level in Redis, layered with edge caching for the parts of the page that don't vary per user, plus event-driven invalidation from the write path rather than relying on TTL alone.

**Layer 1 — CDN/edge, for the non-personalized shell**
If most of a product page (images, description, specs, static markup) is the same for every visitor, cache the rendered HTML at the edge (CDN or reverse proxy like Varnish/Nginx). Inject the personalized bits (cart count, "recently viewed," logged-in name) client-side via JS or edge-side includes. This is the single biggest win when it applies — a cache hit here never touches your app or DB.

**Layer 2 — Redis (or Memcached) for query results, cache-aside**
For the pieces that do hit the DB — product detail, price, inventory, review aggregates, related items — cache the query results keyed by `product_id:locale:currency`, not the whole page. Split by volatility instead of one blob:
- Slow-changing (description, images, specs): long TTL, minutes to hours.
- Fast-changing (price, stock): short TTL, 15–60s, or invalidate on write instead of expiring.

On a miss: read DB, write to cache, return. Simple, and it self-heals if the cache is flushed.

**Invalidation: event-driven for anything correctness-sensitive**
TTL alone means customers can see stale stock/price for the TTL window. Better: when a product is updated (price change, stock update, admin edit), publish an event that deletes/updates the relevant cache keys immediately. TTL becomes a safety net, not the primary mechanism.

**Stampede protection**
With high traffic, a popular product's key expiring causes many concurrent requests to hit the DB at once. Use either:
- a per-key lock/mutex so only one request repopulates the cache while others wait or serve stale, or
- stale-while-revalidate: serve the expired value while one background request refreshes it.
Also jitter TTLs (±10%) so hot keys don't all expire in the same instant.

**Cold start**
After a deploy or cache flush, pre-warm the top N products (by traffic) instead of letting the first wave of requests all miss simultaneously.

Trade-off worth naming: full-page caching is simpler and faster than query-level caching but only works if pages are largely non-personalized — worth checking that first, since it changes the whole design.


===== T50 | case: design-upload =====
Direct-to-storage is the way to go: the client requests a presigned upload URL from your backend, uploads the photo straight to S3/GCS, then tells the backend the upload is done so it can record the photo against the listing and enqueue thumbnail generation. Routing the bytes through your app server instead just doubles your bandwidth bill and creates memory pressure from large multipart request bodies for no benefit.

Two decisions actually fork the design:

1. **Client-side compression before upload.** Phone camera photos run 3-12MB (HEIC or high-res JPEG), and on cellular that's the real bottleneck, not your server. Resize to something like 2000px on the longest edge and re-encode as JPEG (~80 quality) in-browser/in-app before the presigned PUT. Skipping this means slow uploads and storage bloat; doing it means the client needs image-processing capability, which is well-supported (canvas/ImageBitmap on web, native APIs on iOS/Android).

2. **How variant generation is triggered.** Either the client calls an "attach" endpoint after the direct upload succeeds (simple, but relies on the client being honest/reliable), or you wire an S3/GCS event to a queue that processes new objects regardless of what the client does (more robust, one more moving piece). For a marketplace where a flaky mobile connection is the norm, the event-driven trigger is worth the extra infrastructure since it doesn't silently drop photos when the client dies mid-flow.

Depth I'm leaving out: EXIF orientation/GPS stripping, per-listing photo limits and ordering, and the actual thumbnail size set (grid/detail/zoom) — those are next-level-down details once the two forks above are settled.


===== T51 | case: design-audit-log =====
Grounded this in your actual code: every write already funnels through one function, `db.write()` (db.js:13-26), which opens the transaction. That chokepoint is the right place to build from — routes never touch `pool` directly (routes/accounts.js:7, routes/orders.js:7,15).

**Recommendation: DB-level triggers, fed by an actor ID set through the existing transaction.**

Add an `audit_log` table and an `AFTER INSERT OR UPDATE OR DELETE` trigger on each audited table (`accounts`, `orders`, ...). The trigger writes `to_jsonb(OLD)` / `to_jsonb(NEW)` — full row snapshots, not hand-maintained column diffs, so a schema change can't silently break the diff logic.

```sql
CREATE TABLE audit_log (
  id          bigserial PRIMARY KEY,
  table_name  text NOT NULL,
  row_id      text NOT NULL,
  action      text NOT NULL,        -- INSERT/UPDATE/DELETE
  actor_id    bigint,                -- null = no session, e.g. a migration
  before      jsonb,
  after       jsonb,
  occurred_at timestamptz NOT NULL DEFAULT now()
);
REVOKE UPDATE, DELETE ON audit_log FROM app_role;  -- app can only INSERT; trail can't be edited by the app
```

The trigger reads the actor from `current_setting('app.actor_id', true)`. `write()` sets that once per transaction:

```js
async function write(text, params, actorId) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("SELECT set_config('app.actor_id', $1, true)", [actorId ?? null]);
    const res = await client.query(text, params);
    await client.query("COMMIT");
    return res.rows[0];
  } ...
```

**The one real fork: trigger-based vs. inserting the audit row from `write()` itself.**

Inserting from `write()` is simpler and avoids plpgsql, but it only audits writes that go through this code path. Compliance's "for every write" reads as a guarantee, not a best-effort — someone running a one-off fix in `psql` or a migration script wouldn't show up. Triggers catch those too (actor comes back `null`, which is honest — "system/unknown" — rather than silently missing). That's why I'd pay the trigger complexity.

**Second fork: how the actor reaches `write()`.** Explicit param (as above), not `AsyncLocalStorage` set from `sessionUser` (auth.js:5). There are only two call sites today (accounts.js:7, orders.js:7 and :15) — cheap to thread explicitly, and a forgotten actor fails loudly (`undefined` param) instead of silently resolving to whatever the last request left in context.

**Left out, worth a follow-up:** retention/export policy for compliance review, and whether `row_id` needs to be a composite key for tables without a single PK. Nothing today writes outside `db.write()`, so there's no backfill gap to worry about.


===== T52 | case: design-upload =====
Client uploads directly to object storage (S3/GCS/R2) via a presigned URL, not through your app server — the server just issues the URL and later records metadata (listing id, order, uploader) once the client confirms the PUT succeeded. That keeps large images off your app server's memory/bandwidth entirely.

Two decisions actually fork this:

1. **Compress client-side or not.** Resize on-device (canvas, cap long edge ~1600–2000px, JPEG ~80%) before upload — phone cameras routinely produce 10–50MB files, and shrinking client-side cuts upload time and mobile data use dramatically. Still regenerate thumbnails/variants server-side afterward (a queue job triggered on the storage-write event) — never trust the client's resize as the only copy, since compression behavior varies by device/browser.
2. **Single presigned PUT or resumable/chunked upload.** A single PUT is simpler and fine if sellers are typically on decent connections. If spotty mobile networks are a real concern, use multipart (S3) or tus so a dropped connection resumes instead of restarting a 40MB upload from zero.

Left out at this depth: EXIF orientation handling, multi-photo reorder/primary-photo selection, upload progress UI, and any moderation/content-scan step on the async pipeline.


===== T53 | case: design-search =====
At 38k rows on Postgres 16, this doesn't need Elasticsearch or a search service — Postgres's built-in full-text search covers it, stays in the existing `db.query` pool, and needs no new infra.

**Schema**: add a generated `tsvector` column weighting name above description, GIN-indexed:
```sql
ALTER TABLE products ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (
  setweight(to_tsvector('english', name), 'A') ||
  setweight(to_tsvector('english', description), 'B')
) STORED;
CREATE INDEX products_search_idx ON products USING GIN (search_vector);
```

**Route** (new, alongside `routes/products.js`), using `websearch_to_tsquery` so users can type free-text like `"blue running shoes"`:
```js
router.get("/search", async (req, res) => {
  const q = (req.query.q || "").trim();
  if (!q) return res.json([]);
  const rows = await db.query(
    `SELECT id, sku, name, price_cents, ts_rank(search_vector, query) AS rank
     FROM products, websearch_to_tsquery('english', $1) query
     WHERE active AND search_vector @@ query
     ORDER BY rank DESC LIMIT 50`,
    [q]
  );
  res.json(rows);
});
```

The fork worth flagging: this matches on words/stems, not typos. If typo-tolerance matters, that's a small addition later — `pg_trgm` similarity on `name` — not a rewrite. That's the next-level-down decision, not this one.


===== T54 | case: design-retry =====
Looked at `payments.js`, `routes/checkout.js`, `db.js`, and `PROVIDER.md`. The current code has three compounding issues, and the retry design needs to fix all three, not just add a loop.

**What's broken today**

- `payments.js:36` treats a timeout as a plain rejected promise, same as a 4xx decline.
- `routes/checkout.js:23-31` catches everything into one `502 "payment failed"` — a real decline and an unresolved timeout look identical to the customer.
- Cardstream supports `Idempotency-Key` (per `PROVIDER.md`) but `payments.js` never sends one, and per `PROVIDER.md`'s own guidance a timeout means **unknown**, not failed — retrying blind risks a double charge, and reporting "failed" risks the customer re-submitting and paying twice through a *new* checkout attempt.

**Design**

1. **Classify the error before deciding what to do.**
   - Non-2xx response with a body (e.g. `res.statusCode` 400-499) = genuine decline. Don't retry, show the customer a real reason.
   - `req.on("timeout")`, `req.on("error")`, or 5xx = **unknown/retryable**. This is the case `PROVIDER.md` warns about.

2. **Persist an idempotency key before the network call, not after.** Add a `charge_attempts` row (order_id, idempotency_key, status: `pending`/`succeeded`/`failed`/`unknown`, attempt_count) written in the same transaction that flips the order to `processing`, *before* calling `payments.charge`. The key needs to survive a process crash mid-call, not just live in memory — otherwise a retry after a crash has nothing to dedupe against and you're back to double-charging.

3. **Send that key on every attempt for the same order**, including retries. Cardstream dedupes on it for 24h, so a retry after a timeout either: gets back the original charge if it actually succeeded server-side, or authorises fresh if it didn't. Either way you get a definitive answer without a second authorisation.

4. **Don't retry synchronously in the request path on a timeout.** A 10s provider timeout plus 2-3 retries is a customer staring at a spinner for 30+ seconds. Better: on timeout, return something like `202 {status: "processing"}` immediately, and do the retry/reconciliation as a background job (or a follow-up poll from the client) — retry with backoff (e.g. a few attempts, exponential + jitter, capped — rate limit is 600/min so headroom isn't the constraint) using the same idempotency key, then update the order row when it resolves. Declines and successes can still resolve synchronously in the request.

5. **Route handler stops collapsing outcomes.** It needs three branches instead of one catch-all: decline → `failed` with the provider's reason, unknown/timeout → `processing` (handled async, not shown as failure), success → `paid`.

6. **Reconciliation safety net.** A periodic job that finds `processing`/`unknown` orders older than N minutes and re-sends the same idempotency key closes the gap for cases where even the background retry job died (deploy, crash, etc.) — this is what actually makes "never double-charge, never lose a charge" true, not just the happy-path retry.

The core shift: retrying isn't just "call `charge` again on failure" — it's "know whether it's safe to call again" (idempotency key), "know whether you should" (error classification), and "don't lie to the customer while you find out" (processing state instead of failed).


===== T55 | case: design-audit-log =====
The natural hook is `db.write()` in `db.js:13` — it's already the single chokepoint every write goes through and it already owns the transaction boundary, so it's the one place a guarantee can actually be enforced rather than hoped for at each route.

**Recommendation:** capture the diff with a Postgres trigger, not app-level logging.

- Add an `audit_log(table_name, row_id, action, actor_id, actor_email, old_row jsonb, new_row jsonb, changed_at)` table, plus an `AFTER INSERT OR UPDATE OR DELETE` trigger on each audited table (`accounts`, `orders`, …) that writes `OLD`/`NEW` as jsonb into it.
- Thread the actor in via `write()`: have it run `SET LOCAL app.actor_id = $1` (from `req.user.id`, already resolved by `sessionUser` in `auth.js:5`) as the first statement inside the same transaction, and have the trigger read it back with `current_setting('app.actor_id')`.
- Change `write()`'s signature to take the actor explicitly (`db.write(text, params, req.user)`) rather than reaching for ambient/async-local state — everything else in this codebase passes its inputs explicitly, so that's the fit.

**The fork that matters:** app-level (insert an audit row manually inside each route, next to the `UPDATE`/`INSERT`) vs. DB-level (trigger). App-level is less migration work and keeps the diff logic in JS. But it's bypassable — a route author who forgets the extra insert, or any future write that goes around `db.write()`, produces a silent gap, and "who changed what, for every write" is exactly the kind of requirement compliance means as a hard guarantee, not best-effort. Triggers can't be skipped by a route that forgets.

**Depth left out:** immutability of `audit_log` itself (revoke `UPDATE`/`DELETE` grants on it, or ship rows to append-only storage) and how the trail gets surfaced (a `/audit` read endpoint, or just direct queries for now) are the next layer down — worth deciding once the capture mechanism is settled.


===== T56 | case: design-upload =====
**Approach:** presigned direct-to-object-storage uploads, not proxying files through your app server. Client asks your backend for a presigned PUT URL (backend records a pending photo row tied to the listing), uploads straight to S3/GCS/R2, then pings the backend to confirm — which marks it live and kicks off async derivative generation (thumbnail, listing-card size, full-size) plus EXIF-orientation fix and HEIC-to-JPEG conversion for iPhone shots.

**Two decisions that actually fork this:**

1. Compress client-side or server-side. For phone-camera photos over cellular, compress before upload — resize to something like a 2000px longest edge and re-encode as JPEG/WebP (canvas API on web, native image APIs on iOS/Android) — rather than uploading multi-MB originals and eating the bandwidth/time cost. Native apps make this nearly free; web needs a canvas step.
2. Web, native app, or both — this decides whether HEIC conversion happens client-side (iOS can export JPEG directly) or has to happen server-side (Safari can upload raw HEIC).

**Left out:** resumable/retry upload handling for flaky mobile connections (multipart or tus), moderation/scanning hooks, and photo ordering/primary-photo schema.

What's the stack — web, native, or both, and what backend/storage are you on? That'll pin down the specifics.


===== T57 | case: design-realtime =====
Given the platform constraints in `PLATFORM.md` — no WebSocket upgrades (501 at the edge), frozen/non-sticky instances that can't hold a subscription open — the only real option is client-side polling against the existing `/api/metrics` endpoint. Long-polling is also out: the rollup job (`jobs/rollup.md`) only ever changes data once a minute, so a long-poll would frequently need to hold the connection past the 10s function timeout.

So: replace the click-only `load()` in `public/dashboard.js` with a `setInterval(load, …)`, keeping the same fetch/render path already there. Two things worth deciding:

1. **Interval length.** Since `rollup` only changes once a minute, polling much faster than that just burns invocations for identical rows. 15–20s is a reasonable compromise between "feels live" and not hammering a serverless function that's billed per invocation.
2. **Skip redundant re-renders.** `computed_at` is already returned — compare it to the last-seen value and skip `render()` when unchanged, so the UI doesn't flicker every poll for a value that only actually updates every 60s.

The "Refresh" button can stay as a manual force-check; it just stops being the only way data ever updates.


===== T58 | case: design-alerting =====
Two things fork this:

**1. Where do the multi-cycle conditions (`feed_stale` >3 cycles, cap pinned 2 cycles, pace error >15% for 2 cycles) get evaluated?** Since `govern()` is pure and already tracks a feed-stale counter for the 3-cycle fallback (SPEC.md:50-52), extend that same pattern: add cap-pinned and pace-error counters to the persisted controller state, and have `govern()` return an `alerts: [...]` list alongside `cap`/`state`/`guardrail`. That keeps every alert condition deterministic, unit-testable, and replayable by the simulation harness — the same ladder that already covers guardrails covers alerting. The alternative (tracking cycle history in a stateful wrapper around the supervisor) works but duplicates state outside the tested core and can drift from what `govern()` "sees."

**2. Heartbeat-missed is fundamentally different and can't live in this design at all.** If the loop doesn't run, no code inside the loop can notice. That needs an external dead-man's-switch: persist a last-successful-cycle timestamp per tenant, and have something outside the tenant loop (a monitoring check, Healthchecks.io/Cronitor-style ping, or a Prometheus `absent()`-style rule) alert when it goes stale past 5 minutes + margin.

With that split, the supervisor loop becomes a thin dispatcher: call `govern()`, persist state, apply the cap, then fire `alert(...)` for each entry in `result.alerts` (single-cycle guardrails like `quota_exceeded`, `floor_at_risk`, `config_invalid` are just one-element cases of the same list). Left out: the actual alert sink/transport (pager vs. Slack vs. metric) and de-dup/throttling policy so a stuck tenant doesn't page every 5 minutes — that's a level below what SPEC.md specifies.


===== T59 | case: design-search =====
At 38k rows on Postgres 16, this doesn't need a separate search service (Elasticsearch, Algolia) — Postgres full-text search handles it well within the existing `pg` setup.

Add a generated `tsvector` column combining `name` (weighted 'A') and `description` (weighted 'B'), with a GIN index:

```sql
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', name), 'A') ||
    setweight(to_tsvector('english', description), 'B')
  ) STORED;

CREATE INDEX products_search_idx ON products USING GIN (search_vector);
```

Then in `routes/products.js`, a `GET /search?q=` using `plainto_tsquery` and `ts_rank`, filtered to `active`, same paging pattern as the existing list route.

The fork: plain `tsquery` only matches whole words, so "lap" won't find "laptop" and typos won't match at all. If the product picker needs prefix/typo tolerance (search-as-you-type), pair it with `pg_trgm` (trigram similarity + a GIN index on `name`) and blend or fall back to it when `tsquery` returns nothing. If users are expected to type full words and submit, skip that and keep it to `tsvector` alone — simpler, and 38k rows means either approach is fast without extra tuning.


===== T60 | case: design-alerting =====
Two different mechanisms are needed here, because the alert list (lines 64-73) mixes conditions that are visible in a single cycle with ones that aren't.

**Per-cycle guardrails map directly.** `quota_exceeded`, `floor_at_risk`, `floor_unreachable`, and `config_invalid` are exactly the guardrail `govern()` already returns in `result.guardrail` (lines 17, 48-60). The supervisor's step 4 just needs a lookup from guardrail name to alert, alongside the existing `quota_exceeded` check at line 31.

**Multi-cycle conditions can't come from a single `result.guardrail`**, since guardrails are first-match-wins (line 46) but "cap pinned two cycles" and "pace error >15% two cycles" can be true independently of whatever guardrail fired that cycle, and "`feed_stale` past three cycles" needs a streak count the doc says state already tracks for the fallback-to-default behavior (line 51-52). The fork: put that counting inside `govern()`'s persisted state rather than as ad-hoc counters in the supervisor. Extend the state struct with the streak counters it likely already half-has (feed_stale count, cap-pinned count, pace-error count), and have `govern()` return an `alerts: []` list of conditions crossing threshold this cycle — not just the single winning guardrail. That keeps alert logic on the same pure, unit-tested, simulation-replayable path the spec is built around (lines 37-42), instead of a second untested code path in the I/O-owning supervisor.

**Heartbeat-missed can't be detected from inside the loop at all** — if the loop didn't run, nothing inside it fires. That needs a dead-man's-switch outside the per-tenant control loop: each cycle stamps `last_run` in persisted state (step 4), and a separate watchdog (external cron/monitor) alerts when that timestamp goes stale, independent of `govern()` entirely.

Left out: whether alerts are edge-triggered (fire once on the transition into/out of the condition) or level-triggered (fire every 5-minute cycle the condition holds) — the spec doesn't say, and it matters a lot for `quota_exceeded`, which can hold for the rest of the day.


===== T61 | case: design-audit-log =====
Your app has a good property already: every write funnels through `db.write()` in `db.js:13`, and every request resolves an actor in `sessionUser` (`auth.js:5`) before it reaches a route. That gives two natural seams. Here's the design I'd use.

## Two failure modes to avoid

- **App-layer-only logging** (each route handler calls `logAudit(...)` after its query): misses anything that writes outside the route layer — migrations, a psql session, an admin script, a future service sharing the DB. Compliance audits get burned by exactly that gap.
- **Logging without tamper-resistance**: if the app's own DB role can `UPDATE`/`DELETE` the audit table, the audit trail isn't evidence, it's a suggestion.

So the core write-capture should live in Postgres, not in route handlers, and the audit table should be append-only even to the app.

## Architecture

**1. Capture "what" and "when" with row-level triggers, not app code.**

A generic trigger function fires on every `INSERT`/`UPDATE`/`DELETE` on the tables that matter (`accounts`, `orders`, etc.), writing the full before/after row as JSON:

```sql
CREATE TABLE audit_log (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  table_name   text        NOT NULL,
  row_id       text        NOT NULL,
  operation    text        NOT NULL,       -- INSERT / UPDATE / DELETE
  actor_id     text,                       -- see step 2
  request_id   text,
  old_data     jsonb,
  new_data     jsonb,
  changed_at   timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE FUNCTION audit_trigger() RETURNS trigger AS $$
BEGIN
  INSERT INTO audit_log(table_name, row_id, operation, actor_id, request_id, old_data, new_data)
  VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id)::text,
    TG_OP,
    current_setting('app.actor_id', true),
    current_setting('app.request_id', true),
    CASE WHEN TG_OP <> 'INSERT' THEN row_to_json(OLD) END,
    CASE WHEN TG_OP <> 'DELETE' THEN row_to_json(NEW) END
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER accounts_audit AFTER INSERT OR UPDATE OR DELETE ON accounts
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();
-- same on orders, and any other table that needs coverage
```

This catches every write to those tables regardless of code path — your `db.write()` calls, a future service, a manual fix in `psql`, all of it. `SECURITY DEFINER` lets the trigger insert into `audit_log` even if the app role has no direct grant on it.

**2. Get "who" into the trigger via a session variable, set per-transaction.**

`current_setting('app.actor_id', true)` reads a variable the trigger has no other way to know. Set it with `SET LOCAL` (not `SET`) inside the same transaction as the write, so it's scoped to that transaction and can't leak across pooled connections:

```js
// db.js
async function write(text, params, ctx = {}) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("SELECT set_config('app.actor_id', $1, true)", [ctx.actorId || null]);
    await client.query("SELECT set_config('app.request_id', $1, true)", [ctx.requestId || null]);
    const res = await client.query(text, params);
    await client.query("COMMIT");
    return res.rows[0];
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
}
```

Route handlers already have `req.user.id` — the change is threading it into `write()`'s `ctx`. If you'd rather not touch every call site's signature, use `AsyncLocalStorage` (Node's `async_hooks`) instead: `sessionUser` in `auth.js` wraps `next()` in `als.run({ actorId: req.user.id }, next)`, and `write()` reads `als.getStore()` itself. Either way, "who" travels with the request without every route explicitly passing it.

**3. Lock the audit table down.**

- App's DB role: no `INSERT`/`UPDATE`/`DELETE` grant on `audit_log` at all — writes only happen via the `SECURITY DEFINER` trigger function.
- No role (including app, including most admins) gets `UPDATE`/`DELETE` on it. It's insert-only, forever.
- A separate read-only role for compliance/audit review, distinct from the app's credentials.
- If you need cryptographic tamper-evidence (some compliance regimes want this), chain rows by including a hash of the previous row's hash in each new row, or ship a copy to an external append-only store (S3 with Object Lock, etc.).

**4. Operational concerns**

- **Growth**: partition `audit_log` by month (native Postgres partitioning) so retention/archival is a `DETACH PARTITION`, not a `DELETE`.
- **Retention**: compliance usually specifies a duration (often years) — decide it up front rather than defaulting to "forever."
- **Indexes**: `(table_name, row_id, changed_at)` for "history of this record," `(actor_id, changed_at)` for "everything this user touched."
- **Coverage drift**: add a test/CI check that diffs `information_schema.triggers` against the list of writable tables, so a new table added later doesn't silently ship without an audit trigger.
- **Reads**: this design only covers writes, as asked. If compliance later wants read access logging too, that's a different mechanism (can't use row triggers for `SELECT`) — worth flagging now so it isn't assumed to be covered.

This is a design only — I didn't modify any files. Want me to implement it (migration + `db.js`/`auth.js` changes)?


===== T62 | case: design-rate-limit =====
Key design: rate-limit per client identity (API key or auth token, not IP — IP is unreliable behind proxies and doesn't isolate a single misbehaving client from others sharing a NAT), using a token-bucket algorithm so legitimate bursts still pass but sustained hammering gets capped. On limit breach, return `429` with a `Retry-After` header rather than silently dropping requests.

The fork that matters: where the counter state lives.
- In-memory per app instance — trivial to add, but if `/v1` runs behind a load balancer with N instances, a client can burst to N× the intended limit, and it won't stop them from degrading a single hot instance.
- Centralized store (Redis, via `INCR`+`EXPIRE` or a Lua script for atomic token-bucket updates) — enforces the limit accurately across all instances, at the cost of a Redis round-trip per request and a new dependency to keep available.

For a service already showing cross-client degradation, centralized is the right call — an in-memory limiter wouldn't actually fix the problem you're describing unless `/v1` is single-instance.

What I left out: tiered limits (different caps per client/plan), and whether to enforce at the app layer vs push it to a gateway/proxy (nginx, Envoy, API gateway) in front of `/v1`. What's `/v1` running on — is there already a reverse proxy or gateway in the request path, or is this a single app process?


===== T63 | case: design-realtime =====
Given the platform constraints in `PLATFORM.md` — no WebSocket upgrades (501 at the edge), functions frozen/killed at 10s, no sticky routing — anything push-based (WebSockets, SSE) is out. Polling is the only option that fits.

Since `rollup` only changes once a minute (`jobs/rollup.md`), there's no value polling faster than that: add a `setInterval` in `public/dashboard.js` that calls the existing `load()` every 15-20s, replacing the click-only wiring. The `/api/metrics` handler needs no changes — it's already stateless, cheap (4KB/30ms), and returns `computed_at`.

The one real decision is whether to skip re-rendering when `computed_at` is unchanged from the last poll (compare it client-side before calling `render()`). Given the response is only 30ms and 4KB, that's a minor polish, not a requirement — I'd leave it out unless the re-render itself is expensive.


===== T64 | case: design-upload =====
The existing pieces answer most of this. `storage.js` already has a signed-`PUT` path (unused), `db.js` already has `addPhotoKey` (unused), and `listings.photo_keys` exists as an empty array — this was clearly scaffolded for uploads and never wired up.

The one constraint that decides the shape: `nginx.conf` caps `client_max_body_size` at 1m globally, and raising it was explicitly declined because it shares a listener with the payments service under PCI scope. A phone camera photo is routinely 2-8MB, so any upload route that proxies bytes through that listener (`POST` to storefront, which then writes to S3) will reject real photos and reopen a decision that's already been made.

So: don't send bytes through nginx at all. Have the storefront issue a presigned `PUT` (`storage.signedUrl(key, { method: 'PUT' })` — already implemented, just unused) and have the phone browser upload directly to S3. Route shape:

- `POST /:id/photos` — server generates a key like `listings/{id}/{uuid}.jpg`, returns `{ key, url }` from `signedUrl`. No body size limit applies here since no bytes cross nginx.
- Client PUTs the file bytes straight to S3 using that URL.
- `POST /:id/photos/:key/confirm` (or similar) — only after the PUT succeeds does the server call `db.addPhotoKey(id, key)`. Don't write the key on step 1, or failed/abandoned uploads leave dangling keys in `photo_keys` that `signedUrl` will happily generate broken GET links for later.

Two things that genuinely fork the design from there:
1. **Validation** — since the server never sees the bytes, content-type/size checks have to happen either via S3 bucket policy (`PutObject` conditions on `Content-Type`/`Content-Length-Range`) or an S3 event trigger after the fact, not in the Express route.
2. **CORS** — you noted CORS on the bucket already allows PUT from market.example.com, so that part's done.


===== T65 | case: design-cache =====
Looked at the actual code. This isn't really a "add a cache" problem — it's a caching *policy* problem with two layers stacked wrong. Here's what's going on and how I'd fix it.

## Why it's 900ms today

`routes/products.js` makes three DB calls per request, and `db.js:5-16` tells you exactly where the time goes: `productBySlug` ~40ms, `relatedProducts` ~600ms (four-table join), `stockFor` ~250ms. That adds to ~890ms, matching your number. The route comment confirms the page is anonymous and identical for every visitor — no session read, same price/stock/copy for everybody.

Meanwhile `CDN.md` says the CDN sits in front of every request, obeys origin `Cache-Control` with no path rules of its own, and currently has a **0% hit rate**. That's the real story: `middleware/security.js` sets `no-store, no-cache, must-revalidate, private` on *every* response via `app.use(security)` in `app.js:9`. It's not that no one built caching — it's that a blanket header is actively forbidding it, for both `/p` and `/account`.

That header exists for a real reason: an account page leaked cross-user out of an intermediary cache, and the fix was applied app-wide to close the audit finding fast. `routes/account.js` genuinely needs `no-store` — it reads `req.session.userId` and must never be cached anywhere. `routes/products.js` doesn't share that constraint at all, but it inherited the same header by accident of `app.use` ordering.

## The fix, layered

**1. Scope the no-store policy instead of removing it.** Keep `security.js`'s security headers (X-Frame-Options, X-Content-Type-Options) global — those are fine everywhere. But make `Cache-Control` per-route: leave `/account` as `no-store, private`, and give `/p` its own explicit header, e.g. `public, max-age=120, stale-while-revalidate=600`. This is the highest-leverage change — it lets the CDN, which is already on every request path, start serving repeat hits with zero app or DB involvement. Given catalogue edits happen "a few times a day," a couple of minutes of edge staleness is a fine trade, and SWR means you never make a user wait for a revalidation.

**2. Handle stock separately — it doesn't share the catalogue's freshness budget.** `stockFor` sums live inventory, which changes on every order, not a few times a day. If it rides the same edge TTL as the rest of the page, you'll show stale stock for up to the full cache window. Two reasonable options:
   - Accept eventually-consistent stock (common for e-commerce "in stock" indicators) and give it its own short TTL — seconds, not minutes — either as a separate cached fragment/endpoint the page fetches, or as a short-TTL key in an app-level cache (see below) so it's decoupled from the catalogue TTL.
   - Or exclude stock from what the edge caches at all: cache the shell at the edge, fetch stock client-side or via an edge-side include so it's always live.

**3. Add an application-level cache in front of the DB for the two slow, non-per-user queries.** This matters even with edge caching, because edge misses (first hit, purges, different query strings) still hit the app, and you want to protect the DB from the 600ms join on every one of those. Cache `productBySlug` and `relatedProducts` in Redis (or similar) keyed by slug/product id, TTL matching the catalogue's change cadence (a few minutes is generous given "a few times a day"). `relatedProducts` is the single biggest win here — it's a pure function of product id plus catalogue state, so it's an ideal cache candidate. Keep `stockFor` out of this cache or give it a much shorter TTL, for the same reason as above.

**4. Invalidate on write, don't rely on TTL alone for correctness.** Since products are edited through an admin tool, hook a purge into that save path: invalidate the Redis key for that product/slug, and issue a CDN purge for `/p/:slug`. TTL then becomes a safety net rather than the only mechanism, so an edit shows up immediately instead of waiting out the window.

**5. Guard against stampede on cache-miss.** When a Redis key or edge entry expires, don't let every concurrent request for a popular slug re-run the 600ms join simultaneously. Single-flight the DB call per key (e.g., a small in-flight-promise map, or Redis-based lock) so only one request repopulates the cache and the rest wait on it or get stale-while-revalidate content.

**What not to touch:** `routes/account.js` and its `no-store` behavior. That's the exact thing the 2024 audit flagged, and any refactor of the shared middleware needs to leave that route's headers untouched — the bug you're fixing is the *product* page inheriting a policy meant for the *account* page, not that the account page's policy is wrong.

Net effect: most real-world traffic ends up served from the CDN edge (0 DB calls), edge misses hit an app-level cache (near-0ms instead of 600ms+250ms), and only true cold entries or invalidated products pay the full ~900ms.


===== T66 | case: design-audit-log =====
Looked at the service: Express + `pg`, one `Pool`, and every write already funnels through `db.write()` in `db.js:13`, with `req.user` (id, email, accountId) resolved once by the `sessionUser` middleware in `auth.js` before any route runs. That choke point is what makes this tractable.

## Recommended approach: DB triggers for completeness, app context for attribution

Two things compliance needs are in tension with a pooled connection: Postgres triggers see every row change no matter how it happens (guaranteeing nothing slips through), but the pool uses one generic DB role, so a trigger alone has no idea *which user* issued the query. Fix that by having the app stamp actor identity into the transaction, then let a trigger do the actual logging.

**1. Append-only audit table**
```sql
CREATE TABLE audit_log (
  id bigserial PRIMARY KEY,
  occurred_at    timestamptz NOT NULL DEFAULT now(),
  table_name     text NOT NULL,
  row_pk         text NOT NULL,
  operation      text NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
  actor_user_id  uuid,
  actor_email    text,
  request_id     uuid,
  old_data       jsonb,
  new_data       jsonb
);
REVOKE UPDATE, DELETE, TRUNCATE ON audit_log FROM app_role;
```
Revoking write/delete on the table from the app's own role is what makes it "audit-grade" rather than just a log table — even a bug or a malicious app-layer actor can't edit history, only Postgres itself (via trigger) can insert.

**2. Trigger per audited table**
```sql
CREATE OR REPLACE FUNCTION audit_row_change() RETURNS trigger AS $$
BEGIN
  INSERT INTO audit_log(table_name, row_pk, operation, actor_user_id, actor_email,
                         request_id, old_data, new_data)
  VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id)::text,
    TG_OP,
    nullif(current_setting('app.current_user_id', true), '')::uuid,
    nullif(current_setting('app.current_user_email', true), ''),
    nullif(current_setting('app.request_id', true), '')::uuid,
    CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,
    CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_accounts AFTER INSERT OR UPDATE OR DELETE ON accounts
  FOR EACH ROW EXECUTE FUNCTION audit_row_change();
-- same for orders, users, and any other business table that needs coverage
```
This also solves a gap that exists today: nothing in `accounts.js`/`orders.js` reads the pre-image before an `UPDATE`, so app-level logging alone couldn't produce an old-value diff. The trigger gets `OLD`/`NEW` for free.

**3. The one required app change: pass actor identity into the transaction**

`current_setting()` inside the trigger only works if something sets it, transaction-local, before the write runs. That means `db.write()` needs to accept and forward context:
```js
async function write(text, params, ctx = {}) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query(
      "SELECT set_config('app.current_user_id', $1, true), " +
      "set_config('app.current_user_email', $2, true), " +
      "set_config('app.request_id', $3, true)",
      [ctx.userId || null, ctx.userEmail || null, ctx.requestId || null]
    );
    const res = await client.query(text, params);
    await client.query("COMMIT");
    return res.rows[0];
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
}
```
Route handlers then pass `{ userId: req.user.id, userEmail: req.user.email, requestId: req.id }` — `req.user` already exists everywhere via the existing middleware, so this is just threading one extra argument through call sites like `accounts.js:7` and `orders.js:15`. A `request_id` needs one small addition to `app.js`: a middleware that stamps `req.id = crypto.randomUUID()` before `sessionUser`, so audit rows can be correlated back to a specific HTTP request in the app logs.

## Why not app-level-only logging

The alternative — have `db.write()` itself insert an `audit_log` row alongside the caller's write, no triggers — is simpler and avoids the session-variable plumbing. But it's only as complete as "every write goes through `db.write()`," which is a convention, not a guarantee: a raw `pool.query()`, a future ORM, a one-off migration script, or a DBA running `psql` directly would all bypass it silently. For a compliance audit trail specifically, that gap is the whole risk — triggers make the guarantee structural instead of relying on every future contributor remembering to call the right helper.

## Scope and edges worth deciding explicitly

- **Which tables**: business data (`accounts`, `orders`, whatever else holds customer-facing state). `sessions` is usually excluded from this trail but auth events (login, logout, failed login) are typically their own audit stream — worth building if compliance also wants "who logged in when," separate from row-level writes.
- **Retention**: partition `audit_log` by month (`occurred_at`) so old partitions can be archived/detached without a slow delete.
- **Tamper evidence**: if the compliance regime is strict (SOX/PCI-grade), consider hash-chaining rows (`row_hash = hash(prev_hash || row_content)`) or shipping a copy to WORM storage (e.g. S3 Object Lock) so even a compromised superuser can't rewrite history undetected. Not needed for a baseline "who/what/when" trail.
- **Verification**: add a test that performs a write through each route and asserts a matching `audit_log` row with the right actor, table, operation, and diff; and a test for writes with no authenticated actor (if any system/cron job writes exist) to confirm they log explicitly rather than with a silently null actor.

If this service later grows into several services writing to several databases, WAL-based CDC (e.g. Debezium) streaming to a central audit store becomes the better fit — but for one service on one Postgres instance, triggers plus session-variable context is the least amount of new infrastructure that still gives a complete, tamper-resistant trail.


===== T67 | case: design-search =====
At this scale (38k rows, Postgres 16, growing slowly) this is a Postgres full-text search problem, not a case for a separate search service like Elasticsearch or Algolia — that infra isn't justified here.

Add a generated `tsvector` column to `products` combining `name` (weighted `A`) and `description` (weighted `B`), with a GIN index on it:

```sql
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', name), 'A') ||
    setweight(to_tsvector('english', description), 'B')
  ) STORED;

CREATE INDEX products_search_idx ON products USING GIN (search_vector);
```

Then a new route mirroring `routes/products.js`'s existing style, querying with `plainto_tsquery` and ordering by `ts_rank`, still gated on `active`.

One fork worth deciding: plain `tsvector` matching won't handle typos or mid-word partial matches (e.g. "wat bottle" → nothing, "sun scr" → nothing). If that matters for this product catalog, pair it with `pg_trgm` (trigram similarity) as a fallback or combined ranking signal — cheap to add given the row count, but it's an extra index and a second query path, so I'd only add it if product names are the kind users misspell or truncate. Worth a call from you or whoever owns the UX spec.

Left out: request-level concerns (debouncing on the frontend, min query length, rate limiting) and whether search results need the same pagination shape as the existing `GET /` listing endpoint.


===== T68 | case: design-search =====
Given the scale here (schema.sql says ~38k products, growing by a few hundred/month, on Postgres 16), Postgres's built-in full-text search is the right tool — no need for Elasticsearch/Meilisearch/Algolia as a separate service to run and keep in sync.

**1. Schema change** — add a generated `tsvector` column weighting name above description, plus a GIN index:

```sql
ALTER TABLE products ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', name), 'A') ||
        setweight(to_tsvector('english', description), 'B')
    ) STORED;

CREATE INDEX CONCURRENTLY products_search_idx ON products USING GIN (search_vector);
```

Being a generated column, it stays in sync automatically on insert/update — no trigger or app-side maintenance. `CONCURRENTLY` avoids locking `products` during index build (not strictly needed at 38k rows, but cheap insurance on a live table).

**2. Query** — `websearch_to_tsquery` parses free-text input the way users actually type ("wireless mouse", quoted phrases, `-excluded`), so the "few words" from the user go straight in without you writing a parser:

```sql
SELECT id, sku, name, price_cents,
       ts_rank(search_vector, query) AS rank
FROM products, websearch_to_tsquery('english', $1) query
WHERE active AND search_vector @@ query
ORDER BY rank DESC, name
LIMIT 50 OFFSET $2;
```

**3. Route** — new `GET /products/search?q=...&page=...` in `routes/products.js`, mirroring the existing paging pattern.

**Tradeoff worth flagging:** `to_tsvector` stems words (run/running/runs match) but won't catch typos or partial prefixes ("wireles" won't match "wireless"). If that matters for this catalog, pair it with `pg_trgm` (`CREATE EXTENSION pg_trgm` + a GIN trigram index on `name`) and blend trigram similarity into the ranking or use it as a fallback when the tsquery returns nothing. I'd ship without it first and add it only if search-quality feedback calls for it — it's extra index weight and query complexity for a catalog this size.

This scales comfortably past 38k rows into the low millions before you'd need to reach for a dedicated search engine.


===== T69 | case: design-upload =====
Here's how I'd architect it:

**Client (mobile web/app)**
- `<input type="file" accept="image/*" capture="environment" multiple>` (or native picker in an app) lets sellers snap or pick from gallery.
- Resize/compress client-side before upload — phone photos run 3-12MB (or HEIC on iPhone). Downscale to a max dimension (e.g. 2048px) and re-encode as JPEG/WebP via canvas or a lib (browser-image-compression), converting HEIC to JPEG in the process. This cuts upload size 5-10x and avoids format-support issues downstream.
- Strip EXIF (especially GPS) client-side or flag it for server-side stripping — sellers photographing items don't want their location embedded.
- Show per-photo progress and allow retry; mobile networks drop mid-upload constantly.

**Transport**
- Don't proxy image bytes through your app server. Have the client request a **presigned upload URL** (S3/GCS/R2) per photo from your API, then PUT directly to object storage.
- For flaky connections, use multipart/resumable upload (S3 multipart, or the tus protocol) rather than a single PUT — a dropped connection shouldn't mean restarting a 5MB upload from zero.
- Cap file count and size server-side when issuing the presigned URL (e.g. max 20 photos/listing, 15MB/file) so nothing enforces limits only in the client.

**Server**
- Endpoint: `POST /listings/:id/photos/presign` → returns a presigned PUT URL + a photo record created in `pending` state (id, listing_id, storage_key, uploader, order, status).
- After the client's PUT succeeds, it calls `POST /listings/:id/photos/:photoId/complete`. Server does a HEAD on the object to confirm it exists and matches expected content-type/size before marking it `active` — never trust the client's say-so alone.
- An async worker (triggered by the storage event or the complete call) generates derivatives: thumbnail, listing-card size, full-size — and strips any remaining EXIF. Store variants alongside the original key.
- Optional: basic content moderation/NSFW check in that same pipeline before a photo goes live.

**Data model**
- `listing_photos(id, listing_id, storage_key, status, sort_order, is_cover, width, height, created_by, created_at)`.
- Sort order and a designated cover photo are typically must-haves for a listing UI — worth building in from the start rather than bolting on.

**Failure modes to design for explicitly**
- Upload succeeds but "complete" call never arrives (app backgrounded) → periodic sweep of `pending` photos older than N hours, verify against storage, reconcile or expire.
- Duplicate/retry uploads → idempotency key per photo attempt.

That's the shape I'd build; happy to go deeper on any piece (e.g. presigned-URL endpoint code, the client compression step) when you're ready to write it.


===== T70 | case: design-rate-limit =====
Given your setup — Express behind `cluster` (4 workers/box, likely multiple boxes behind an LB), no shared state except Redis, and Postgres-backed API keys with a `plan` column already resolved per request — here's how I'd build it:

**Key by `client_id`, not IP.** The comment in `routes/api.js` already says one client can call from many IPs and many clients share an IP behind corporate NAT. IP-based limiting would either miss the abusive client or collateral-damage everyone behind their NAT. The auth middleware already resolves `req.client.client_id` and `plan` before any handler runs — that's the natural rate-limit key and the natural place to enforce it.

**State has to live in Redis, not process memory.** With 4 cluster workers per box (each its own heap, per `app.js`'s comment) plus however many boxes sit behind the LB, an in-memory counter (e.g. `express-rate-limit`'s default store) would let each worker/box enforce its own independent quota — a client could burst to `limit × workers × boxes` before anything blocks them. You already have one Redis shared by all workers (`redis.js`) — reuse it.

**Algorithm: sliding-window counter (or token bucket) via a Lua script.** Plain `INCR` + `EXPIRE` has a race — if the increment succeeds but the process dies before the expire, that key never resets. Do it atomically:

```lua
-- KEYS[1] = "rl:{client_id}", ARGV[1] = limit, ARGV[2] = window_seconds
local count = redis.call("INCR", KEYS[1])
if count == 1 then
  redis.call("EXPIRE", KEYS[1], ARGV[2])
end
if count > tonumber(ARGV[1]) then
  return redis.call("TTL", KEYS[1])
end
return 0
```

Fixed windows have edge-burst issues (2x limit across a window boundary); if that matters, use a sorted-set sliding-window-log or two overlapping fixed windows weighted by elapsed time instead. Token bucket is the better fit if you want to allow short bursts but cap sustained rate — probably closer to what you want for a "hammering" client, since it lets normal bursty usage through but caps sustained abuse.

**Limits scoped by plan.** `plan` is already on `req.client` — map it to a limit (e.g. `{free: 60/min, pro: 600/min}`) so you're not hardcoding one number for every client.

**Where it sits in the pipeline:** as its own middleware right after the API-key lookup, before any handler touches Postgres:

```js
router.use(auth);           // resolves req.client { client_id, plan }
router.use(rateLimit);      // Redis check keyed on req.client.client_id
router.get("/reports", ...) // never reached if throttled
```

On block, return `429` with a `Retry-After` header (use the TTL the Lua script returns) rather than a generic error — well-behaved clients back off automatically.

**One thing worth flagging while you're in there:** the auth middleware does a Postgres `SELECT` on every single request with no caching. A client hammering `/v1` is also hammering Postgres on every call before they ever reach the rate limiter. Worth caching `key → {client_id, plan, revoked_at}` in Redis with a short TTL (30–60s) so the DB isn't in the hot path at all — that's likely a bigger factor in "degrading it for everybody else" than the endpoint logic itself, since Postgres connection/query capacity is the shared resource actually getting saturated.


===== T71 | case: design-realtime =====
For read-only metrics like an ops dashboard, Server-Sent Events (SSE) is the right default over WebSocket — it's one-directional, works over plain HTTP, and reconnects automatically in the browser. Reserve WebSocket for cases where the client also needs to send commands back (acking alerts, adjusting thresholds).

The fork that actually matters: where the "push" originates.
- If the underlying metrics already flow through an event bus/queue (Kafka, Redis pub/sub, etc.), have the dashboard's backend subscribe and forward events straight to connected clients over SSE — true real-time, no polling anywhere.
- If the data only exists in a database/API that you'd otherwise poll, keep the polling on the server (short interval, one poller shared across all clients) and push diffs to clients over SSE. Never have each browser tab poll the source directly.

Client-side: React/Vue state updates from the SSE stream, with a fallback to a manual refresh button in case the connection drops — treat the live path as an enhancement, not the only path.


===== T72 | case: design-retry =====
The core problem isn't "add retries" — it's that a timeout means you don't actually know whether the charge succeeded, so retrying blind risks a double charge. Two decisions actually fork this:

1. **Idempotency key.** Generate one key per checkout attempt *before* the first charge call, and pass the same key on every retry. Almost all processors (Stripe, Braintree, etc.) dedupe on it server-side, so even a naive retry can't double-charge. Without this, nothing else below is safe.
2. **Where the retry runs.** Don't just add a "try again" client button — the customer already saw "payment failed" and may have left. Put the retry in a background job triggered off the timeout: catch the timeout, enqueue a job with backoff (e.g. 3 attempts, exponential), and have it re-query the processor for the charge's actual status via the idempotency key before assuming it needs to fire again. Update order state and notify the customer once you have a real answer.

The other piece worth fixing regardless of the above: a timeout isn't a decline, so showing "payment failed" on one is a false negative. Surface it as "processing"/"confirming payment" instead, and only say "failed" once you get an actual decline back.

What's the payment processor here — that determines exactly how idempotency keys and status lookups work.


===== T73 | case: design-audit-log =====
This service already has a single choke point for writes: `db.write()` in `db.js:13-26` opens the transaction, runs the query, and commits — every route (`accounts.js`, `orders.js`) goes through it, per the comment on `db.js:5-7`. And `req.user` is already resolved before any route runs, by `sessionUser` in `auth.js:5-13`. That combination is what should drive the design, rather than instrumenting each route.

**Recommendation: Postgres row-level triggers writing to an insert-only `audit_log` table, with actor identity threaded into the transaction via `SET LOCAL`.**

- Add a generic `audit_log(id, table_name, row_id, action, actor_id, actor_email, old_row jsonb, new_row jsonb, txid, changed_at)`.
- On each audited table, an `AFTER INSERT OR UPDATE OR DELETE` trigger writes `to_jsonb(OLD)`/`to_jsonb(NEW)` into it. This captures the *actual* column diff regardless of what shape the SQL took — important here because the three existing writes are all different shapes: a two-column `UPDATE` (`accounts.js:7-10`), a soft-delete `UPDATE` (`accounts.js:15-16`), and an `INSERT` (`orders.js:7-10`). A trigger normalizes all of them without any route author having to remember to log anything.
- Revoke `UPDATE`/`DELETE` on `audit_log` from the app's DB role, so the trail can't be edited even by a compromised app process.
- For "who": extend `write(text, params)` to `write(text, params, actor)` and, right after `BEGIN`, run `SET LOCAL app.actor_id = $1; SET LOCAL app.actor_email = $2` using `req.user.id`/`req.user.email`. The trigger function reads those via `current_setting('app.actor_id', true)`. This works because `SET LOCAL` is scoped to the same transaction `write()` already owns — no new transaction boundary needed.

**The one real fork:** trigger-based vs. logging inside `write()` in application code. App-level logging would give you semantic intent for free (e.g., "cancel order" instead of "orders row updated"), but `write()` only sees raw SQL text — it can't derive a column diff without parsing it, and it only catches writes that go through it as currently written. Triggers cost you that semantic label (you'd only recover it by also logging `req.path`/`req.method` alongside) but guarantee completeness at the schema level. For a compliance trail, completeness should win — pair the trigger with a thin `action` column populated from route context if you want the semantic label too.

**Left out on purpose:** retention/immutability policy for `audit_log`, read-side access control on who can query it, and any non-HTTP write path (migrations, admin scripts, cron) that would need to set the same session variables or fall outside the trail. None of those exist in this codebase today, but they're the first things to check before calling the trail complete.


===== T74 | case: design-realtime =====
Three ways to do it, in order of how much complexity they buy you:

- **Polling**: client re-fetches on a timer (`setInterval` + fetch, or a library like React Query/SWR with `refetchInterval`). Simplest to build and operate, works with any existing REST endpoint, and is plenty for most ops dashboards where a 5–30s staleness is fine.
- **SSE (Server-Sent Events)**: server keeps the connection open and pushes updates as they happen. One-directional (server→client), which fits a dashboard, and browsers auto-reconnect on drop. Needs the backend to know when data changed rather than just answering on request — usually backed by a pub/sub (Redis, NATS, Postgres LISTEN/NOTIFY) so any server instance can broadcast to its connected clients.
- **WebSockets**: same push model as SSE but bidirectional. Worth it only if the dashboard also needs to send things back (acking alerts, live filters) or needs updates faster/more frequent than SSE comfortably handles.

My pick: start with polling unless you already know the data changes fast enough that a few seconds of staleness matters — it's a few lines of client code and no new infra. Move to SSE only if polling starts costing too much (thousands of clients hammering the API, or users need sub-second updates), and only then add the pub/sub layer to fan out changes.

Want me to sketch the polling version for whatever framework the dashboard actually uses?


===== T75 | case: design-audit-log =====
Given the shape of this service, `db.write()` in db.js:13 is already the single chokepoint for every write — the comment even says so. That's the natural place to hook in, but two decisions fork the design:

**1. Capture at the database layer via triggers, not in application code.** Logging manually inside each route handler (accounts.js, orders.js) only catches writes that go through that code path — a future direct SQL fix, a migration, or a psql session run by an admin would silently escape it, which defeats "for every write." Instead: add a generic trigger function that fires `AFTER INSERT OR UPDATE OR DELETE` on each audited table, writes to an append-only `audit_log` (table_name, row_id, action, actor_id, actor_email, changed_at, old_row jsonb via `to_jsonb(OLD)`, new_row jsonb via `to_jsonb(NEW)`), and gets applied per-table with a migration. Revoke UPDATE/DELETE grants on `audit_log` itself so it can't be altered after the fact.

**2. Get the actor into the trigger without threading `req.user` through every call site.** Triggers can't see Express's `req`, and today nothing passes `req.user` into `db.write()` at all — that's a real gap since `sessionUser` (auth.js:11) already resolves it on every request. Fix: store `req.user` in an `AsyncLocalStorage` set by `sessionUser`, then have `db.write()` run `SET LOCAL app.actor_id = '<id>'` as the first statement inside its existing `BEGIN`/`COMMIT` (db.js:16-18), and have the trigger read it back with `current_setting('app.actor_id', true)`. This means no route handler has to remember to log anything — the guarantee lives in the one chokepoint plus the schema, not in per-call-site discipline.

Left undetailed: exact `audit_log` retention/partitioning and whether cancelled/soft-deleted rows (accounts.js:15, orders.js:16 both do soft-deletes via UPDATE) need special diffing — those are follow-on tuning, not fork points.


===== T76 | case: design-search =====
Given the scale here (38k rows, Postgres 16 on RDS, no search infra), the right move is Postgres full-text search — no need for Elasticsearch/Algolia at this size.

- Add a generated `tsvector` column to `products` combining `name` (weight A) and `description` (weight B), with a GIN index on it. Generated columns keep it in sync automatically, so no trigger/reindex job needed.
- In `routes/products.js`, add a `q` query param: when present, use `websearch_to_tsquery('english', q)` against that column instead of the current unfiltered listing query, order by `ts_rank`, keep the existing `active` filter and pagination.

The one real fork: plain FTS matches on stems/prefixes but not typos ("addidas" won't find "adidas"). If typo tolerance matters for this UI, add `pg_trgm` with a GIN trigram index on `name` and blend `similarity()` into the ranking or use it as a fallback when FTS returns nothing. Which one you need depends on whether product names are typed or picked from autocomplete — worth confirming before committing to the schema change.


===== T77 | case: design-search =====
Recommendation: Postgres full-text search — a generated `tsvector` column combining name + description, GIN-indexed, ranked with `ts_rank`, updated write-through on product save. No new infrastructure, and it's plenty fast up to a few hundred thousand products.

The real fork is DB-native FTS vs. a dedicated search service (Meilisearch/Typesense/Elasticsearch). Take the dedicated engine if you need typo-tolerance, faceted filters, or the catalog runs into the millions — those come built-in there, whereas Postgres needs `pg_trgm` bolted on for fuzzy matching and gets awkward to tune at scale. Absent a signal that catalog size or fuzzy-match quality is a real requirement, I'd start with Postgres and revisit only if relevance or latency becomes a problem.

Left out: relevance tuning (weighting name matches above description), synonym/stemming config, and frontend debounce/autocomplete behavior — worth a pass once the basic query path is live.


===== T78 | case: design-retry =====
The critical constraint: a timeout doesn't tell you whether the charge succeeded on the processor's side — only that you didn't get a response. Retrying without addressing that risks double-charging the customer. So the design has two non-negotiable pieces before "retry" is even meaningful:

1. **Idempotency keys.** Every charge attempt for a given logical transaction reuses the same idempotency key when sent to the processor (Stripe, Braintree, etc. all support this natively). A retry with the same key either replays the original result or is safely deduped server-side — it never creates a second charge.
2. **Reconcile before retry.** On timeout, first query the processor for that charge's actual status rather than assuming failure. If it succeeded, mark it succeeded and stop. Only retry if it's genuinely unresolved or failed.

The fork you actually have to decide: **synchronous retry inline in the checkout request, or async via a job queue with webhook resolution.** Inline retries are simpler but hold the customer's browser open through multiple timeout windows, which is bad UX for something already slow. The better pattern here is: return "processing" (not "failed") immediately, hand the charge off to a background worker that does reconcile-then-retry with exponential backoff (e.g. up to 3–5 attempts), and resolve the order via the processor's webhook or a status-poll endpoint the frontend checks.

Also worth encoding as a rule: only auto-retry on transient/network errors, never on hard declines (insufficient funds, fraud block) — those aren't retry-fixable and retrying just delays an accurate message to the customer.

What I'm not specifying: exact backoff/attempt-count tuning, how the charge state machine persists (DB columns vs. event log), and webhook signature/replay handling — those depend on which processor and framework you're on.


===== T79 | case: design-retry =====
The critical fact is in `PROVIDER.md`: a timeout means **unknown**, not failed — the charge may have gone through. So `checkout.js`'s current behavior (any thrown error → "payment failed") is actually wrong, independent of retries: it can tell a customer their payment failed when it actually succeeded, and if they try again on a normal (non-idempotent) call, they get charged twice.

**The fix has two parts, and idempotency has to come first:**

1. **Idempotency key, generated once per order and persisted**, not per HTTP attempt — e.g. store it on the order row when checkout starts (`orders.idempotency_key`, or a payment_attempts table). Every retry, including one triggered by the customer clicking "pay" again, must reuse that same key so Cardstream collapses it into the original authorization instead of charging again.

2. **Retry only the transport failure, not the business decision.** In `payments.js`, wrap `charge()` so that on `timeout`/connection error it retries (same key, a couple of attempts, short backoff) — but a 4xx decline from the provider is a real answer and must not be retried.

3. **Exhausting retries still isn't "failed."** If every attempt times out, the order should land in something like `payment_unknown` / `verifying`, not `paid` or `failed`. Resolve it out-of-band — a follow-up call to Cardstream with the same idempotency key returns the byte-identical original response and tells you definitively what happened, or a webhook/reconciliation job does. Only a genuine decline should ever show the customer "payment failed."

The one thing I'd want you to weigh in on: reconciliation as a synchronous poll before responding to the request (simpler, but the customer waits) vs. returning "we're confirming your payment" immediately and resolving async via webhook/job (better UX, more moving parts). Which fits how `checkout.js`'s caller expects to be answered?


===== T80 | case: design-upload =====
Given what's already in this repo, the pieces are mostly staged for this — the natural design is a **direct-to-S3 upload via presigned PUT**, not a body-forwarding upload through the app.

**Why not route photos through the app/nginx:** `nginx.conf:12` caps `client_max_body_size` at `1m` globally across storefront, payments, and admin, and the comment says raising it (or overriding per-location) was already requested and declined for PCI reasons tied to the payments listener. A phone camera photo is routinely 2–8MB+ (more for HEIC/burst shots), so any upload that proxies through `market.example.com` will hit that ceiling immediately, and it's not a limit you're allowed to touch.

**What already exists to route around that:**
- `storage.js:14` already has a `signedUrl` helper that supports `PUT`, and the comment notes the bucket's CORS already permits `PUT` from `market.example.com` — this was clearly provisioned for exactly this use case and just never wired up.
- `db.js:10` already has `addPhotoKey(id, key)` appending to `listings.photo_keys`, following the same "store the key, not the bytes" pattern used for invoices.

**The flow I'd build:**
1. `POST /:id/photos` (new route in `routes/listings.js`) — verify the requesting seller owns listing `id`, generate a key like `listings/{id}/{uuid}.jpg`, call `storage.signedUrl(key, { method: 'PUT', expiresIn: 60 })`, return `{ url, key }`.
2. Client (seller's phone browser) `PUT`s the photo bytes straight to that S3 URL — never touches nginx, so the 1MB cap doesn't apply.
3. On a 200 from S3, client calls `POST /:id/photos/confirm` with the key, which calls `db.addPhotoKey(id, key)` — mirrors the existing GET-signed-URL pattern in `listings.js:14-17`, just the write-side twin.
4. Reading photos back: a `GET /:id/photos` that maps each stored key through `storage.signedUrl` (GET) the same way `/invoice` does, since nothing serves raw bytes today.

**Things worth deciding before building:**
- Presigned `PutObjectCommand` doesn't enforce a size cap by itself — if you want the server to bound upload size, use S3's `createPresignedPost` with a `content-length-range` condition instead of a bare presigned PUT.
- Since "phone camera size" is the stated concern, consider resizing/compressing client-side (canvas downscale) before the PUT — cuts upload time on cellular and storage cost, independent of the nginx limit.
- Nothing validates the uploaded bytes are actually an image — that needs to happen after upload (e.g., an S3-event-triggered check/thumbnailer), since the app never sees the payload.
- The presign endpoint must authorize that the caller owns the listing before minting a PUT URL — I didn't see auth middleware in the snippet shown, worth confirming it's applied to this router.
