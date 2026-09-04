# Arrow violations in shipped laconic responses

Every line below was written by a model running the current `rules/laconic.md`
at level `full`, and every one breaks the rule that file states:
*"No arrows inside a sentence. Never use the arrow character or the ASCII
arrow in prose."* Fenced code blocks, inline code spans and URLs are excluded
before counting, so nothing here is an arrow the rule permits.

**225 of 3,017 responses carry at least one; 502 arrows in total.** Lines are
grouped by benchmark case and model, worst first. Within a case, each indented
block is one response, and a response's first four offending lines are shown.

The case names describe what the user asked for:

- `walkthrough` — "walk me through how this module works" over a small source tree.
- `ordered-steps` — a procedure the user will follow one step at a time.
- `confirm-rollback`, `deep-rollback`, `recall-rollback` — questions over an incident write-up.
- `cold-service`, `drift-service` — questions over an unfamiliar service's source.
- `design-*` — "how would X be built?" over a fixture the answer should read.
- `holdout-*` — reserved cases, same shapes.
- `verdict-*` — "is this sound?" over a document that contradicts itself.


## `walkthrough` / sonnet — 60 of the responses carry arrows, 154 offending lines

    2. Otherwise read the refresh token from the store. Missing refresh token → throws `'no refresh token; re-auth required'` immediately (no `inFlight` set, since the throw happens before the `fetch`).
    - **401** ("refresh rejected") → clears the whole store (both tokens gone) and throws `'refresh rejected; re-auth required'`. This is the only place the module reacts to a 401, and it's a 401 from the *refresh* call, not from an arbitrary API call using the access token.
    - Non-401, non-ok → throws `'refresh failed: ' + status`.
    - Ok → parses the body, writes the new access token (`value` + computed `expiresAt`) back into the store, and rotates the refresh token too if the server sent a new one (`body.refresh_token`).

    - `401` → clears the entire store and throws `'refresh rejected; re-auth required'`. This is the real "auth is dead" signal — the caller needs to force a full re-login.
    - Any other non-ok status → throws `'refresh failed: ' + status`, but leaves the store untouched (so a transient 500 doesn't nuke the existing tokens).
    - Success → writes the new access token with a computed `expiresAt`, and conditionally rotates the refresh token if the server sent one back (some OAuth servers reuse the same refresh token).

    - `401` → the refresh token itself was rejected (revoked/expired server-side). `store.clear()` wipes both tokens and it throws, forcing full re-auth.
    - Any other non-OK status → throws `'refresh failed: ' + status`, but the store is left alone, so a transient 5xx doesn't destroy valid tokens.
    - Success → writes the new access token with a computed `expiresAt`, and — only if the server rotated it — writes a new refresh token too.
    - Request A calls `currentToken` → token expired → calls `refresh`. `inFlight` is null, so it proceeds, starts the fetch, and assigns `inFlight` before yielding control.

    - Otherwise, read the refresh token from `store`. Missing refresh token → throws synchronously (`no refresh token; re-auth required`), no fetch happens.

    - Both call `currentToken` → both see the access token expired/near-expiry → both call `refresh(store)`.

    - **401** → the store is wiped entirely (`store.clear()`, dropping both access and refresh tokens) and it throws `'refresh rejected; re-auth required'`. This is the one 401 handled in this file — it means the *refresh token* itself was rejected, i.e. the whole session is dead, not just an expired access token.
    - **other non-ok status** → throws `'refresh failed: ' + status`, but leaves the store untouched (transient failure, retry-able).
    - **ok** → parses the body, writes the new access token + computed `expiresAt` into the store, and rotates the refresh token too if the server sent a new one.


## `walkthrough` / haiku — 27 of the responses carry arrows, 53 offending lines

    **1. Request comes in → `currentToken(store)` is called**
    - If 401: the refresh token itself is invalid → clears the entire store (forcing re-auth) and throws
    - **A** calls `currentToken()` → sees expired token → calls `refresh()` → fetches start
    - **B** calls `currentToken()` → sees expired token → calls `refresh()` → sees `inFlight` is set (A's fetch) → returns A's promise directly

    - Request A calls `currentToken()` → token is stale → calls `refresh()` → starts the fetch, sets `inFlight` to the promise, returns it
    - Request B (milliseconds later) calls `currentToken()` → token is still stale → calls `refresh()` → sees `inFlight` already set, returns the same promise

    1. Request A calls `refresh()` → `inFlight` is null, so it creates the fetch promise and stores it in `inFlight`
    2. Request B calls `refresh()` → `inFlight` is set, so it returns the same promise without making another request

    1. Request A calls `currentToken()` → `refresh()` is called.
    2. Request B calls `currentToken()` almost simultaneously → calls `refresh()`.

    1. **Request A calls `currentToken()`** → token expired → calls `refresh()`
    2. **Request B calls `currentToken()`** before Request A's fetch completes → also needs refresh → calls `refresh()`

    1. Request A calls `currentToken()` → token expired → calls `refresh()`, starts the fetch, sets `inFlight`
    2. Request B calls `currentToken()` → token expired → calls `refresh()`, sees `inFlight` is set, returns that same promise


## `design-upload` / sonnet — 21 of the responses carry arrows, 24 offending lines

    1. Client picks/takes the photo, resizes it on-device (canvas, long edge ~1600–2000px, JPEG quality ~80, convert HEIC→JPEG if needed) — this alone cuts most files 5–10x before they ever leave the phone.

    The one real fork is how that last step gets triggered: trust the client to call back after a successful PUT, or use an S3 event (bucket notification → SQS/Lambda) to confirm the object landed before writing `photo_keys`. Client-callback is far less code and matches the existing invoice pattern; the gap is a phone that

    The one real fork: how step 3 learns the upload actually landed. Client-reported confirmation is simplest and matches the existing code shape, but trusts the client to tell the truth about a write it made directly to storage. An S3 event notification (event → Lambda/SQS → append) is more correct — it only records keys 

    - **Sync vs async processing**: thumbnailing/validation should be async (queue + webhook), so the UI shows "uploading → processing" rather than blocking the listing save on image transforms.

    - **Sync vs async variant generation.** Once the original lands in storage, generating thumbnail/medium/full sizes as a background job (S3 event → Lambda/worker, or a queue) keeps the upload path fast and lets the UI show "processing" then swap in the real thumbnail. Doing it inline on the confirm request is simpler bu

    Left out at this depth: resumable/chunked upload for flaky connections, the exact image pipeline (sizes, HEIC→JPEG conversion), and the photo record's status states (pending/processing/ready/failed).


## `cold-service` / sonnet — 9 of the responses carry arrows, 21 offending lines

    - `status = 'completed'` → replay `response_status`/`response_body` verbatim, no new order created.
    - `status = 'in_progress'` → another request is mid-flight (concurrent retry); return `409` (or `425 Too Early`) rather than racing a second insert.
    **Handler-level requirement:** missing `Idempotency-Key` header → `400`, since silently falling back to non-idempotent behavior defeats the point.

    - 0 rows affected → key already used. Fetch the stored row; if `request_hash` matches, replay the stored `status`/`response`. If it doesn't match, return 409 (same key, different payload — client bug).
    - 1 row affected → proceed with the original `INSERT INTO orders`, then `UPDATE idempotency_keys SET status=…, response=… WHERE (account_id, key)=…` before commit, and return that response.

    - Found, `request_hash` matches → replay the stored `response_status`/`response_body` verbatim, no new insert.
    - Found, hash differs → `422`, the client reused a key for a different request.
    - Not found → do the `orders` insert, then insert the idempotency row with the response, commit.

    - **Row inserted** → you won the race: insert the order, `UPDATE idempotency_keys SET status_code=201, response_body=$1 WHERE ...`, commit, return 201.
    - **No row inserted** → key already exists: fetch it. If `request_hash` differs, return 422 (key reused for a different body). If `response_body` is still null, another request with the same key is mid-flight — return 409/retry. Otherwise replay the stored `status_code`/`response_body` verbatim; no new order is created

    - On POST: look up the key first. Found + hash matches → replay the stored response as-is (same status code, same body), no new INSERT. Found + hash differs → 422/409, key reuse with a different payload. Not found → proceed.

    **Design:** require an `Idempotency-Key` header from the client, and persist key → response atomically with the order row in one transaction, scoped by `account_id` (already on `req.user`, `auth.js:11`).
    - **`db.write()` needs to become multi-statement.** It currently opens/closes a transaction around exactly one query, so it can't wrap "claim key → insert order → store response." That means adding something like `db.transaction(fn)` that hands `fn` a client and does `BEGIN`/`COMMIT`/`ROLLBACK` around however many quer


## `confirm-rollback` / sonnet — 20 of the responses carry arrows, 20 offending lines

    Partly. The document names two separate causes: the config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02, but the migration `0042` (a `NOT NULL` column with no default, run at 14:05) is what made the incident unrecoverable by rollback — reverting the config at 14:21 and rolling back 

    Partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02 — `v411` code's `assertSettlementMode()` threw on the unrecognized value.

    Partly — the config change was the trigger, but not the whole cause. Per the doc's own conclusion: the config flip (`legacy`→`split`) caused the initial 500s at 14:02, but the migration (`0042`, adding a `NOT NULL` column with no default) is what made the incident unrecoverable — it's why reverting the config at 14:21 

    Only partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02, but the document is explicit that it's the migration (`0042`, adding a `NOT NULL` column with no default) that made the incident unrecoverable by rollback — reverting the config at 14:21 and rolling back to `v411`

    Partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02, but the migration `0042` (adding a `NOT NULL` column with no default) is what made the incident unrecoverable — it's why reverting the config at 14:21 and rolling back to `v411` at 14:33 both failed to recover the erro

    Partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02 — but the document is explicit that it's only half the story: the migration (`0042`, adding a `NOT NULL` column with no default) is what made the incident unrecoverable by rollback, since it's what kept the error rate p


## `deep-rollback` / sonnet — 17 of the responses carry arrows, 17 offending lines

    So: the config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) is what *triggered* the initial 500s at 14:02, since `v411` instances threw on the unrecognized value. But that alone would have been fixed quickly by the 14:21 config revert. What turned it into a 45-minute Sev1 was migration `0042` running at 14:05 and addi

    - The config change (`legacy` → `split`) was the **trigger** — it's what caused the first 500s at 14:02.

    The config change (`legacy`→`split`) is what **triggered** the initial 500s at 14:02 — that part's right. But the config revert at 14:21 didn't fix anything (error rate held at 58%), and the `v411` rollback at 14:33 also failed. That's because migration `0042` had already run at 14:05, adding a `NOT NULL` column with n

    Trigger, not sole cause. Doc: config change triggered it; migration's `NOT NULL` column made it unrecoverable by rollback. Either alone → short incident.

    So: the config change (`legacy`→`split`) is what started the 500s at 14:02, since `v411` instances didn't recognize `split` and threw. But that alone would've been fixed by the 14:21 config revert — and it wasn't, because migration `0042` had run at 14:05 and added a `NOT NULL` column with no default, which broke `v411

    - The config change (`legacy`→`split`) was the **trigger**: it's what caused the initial 500s at 14:02, since `v411` instances didn't recognize `split` and threw.


## `design-retry` / sonnet — 10 of the responses carry arrows, 10 offending lines

    The actual bug isn't "no retry" — it's that `checkout.js` treats a timeout as a definitive failure (`payments.js:36` → `checkout.js:31`), when PROVIDER.md is explicit that a timeout means **unknown**, never failed. Retrying blindly on top of that is dangerous, because `charge()` sends no `Idempotency-Key` — a naive ret

    1. **Where the idempotency key is generated and stored.** It has to be created *before* the first network call and persisted somewhere that survives a process crash — not just held in a local variable in `payments.js` — otherwise a retry after a restart generates a new key and you're back to double-charging. Simplest f

    1. **Generate the idempotency key before the first attempt and reuse it on every retry of that charge** — store it on the order row (e.g. `orders.idempotency_key`, set when the row moves to `pending`→charge-attempted) rather than minting one per HTTP call. That's what turns "timeout, retry" from a double-charge risk in

    - Persist charge state server-side as pending → processing → succeeded/failed/unknown, rather than deriving status from a single request/response. On timeout, land in `unknown`, not `failed`.

    **3. A state machine, not a boolean.** Charges need a status beyond succeeded/failed: `pending` → `unknown_awaiting_reconciliation` → `succeeded` / `failed`. A background job owns the `unknown` state, polls/retries with exponential backoff and jitter, caps attempts (e.g. 5 over ~10 min), and on exhaustion routes to man

    - Customer-facing state becomes "processing" → "paid" or "payment failed," never a premature "failed" during the ambiguous window.


## `verdict-rollout` / haiku — 6 of the responses carry arrows, 9 offending lines

    1. Migration runs → `full_name` is dropped
    3. Old instances still run for up to 6 minutes alongside new ones → **crash when they touch `full_name`**

    4. Old code tries to write to `full_name` → column doesn't exist → requests fail

    1. Migration runs → `full_name` is dropped
    3. Old instances still run for up to 6 minutes alongside new ones → **crash when they touch `full_name`**

    4. Old code tries to write to `full_name` → column doesn't exist → requests fail

    3. For ~6 minutes, old instances (still running) handle traffic and hit the four read paths that reference `full_name` → **404 errors or crashes**

    1. Migration runs → `full_name` is dropped, new columns backfilled
    2. Old code on all 12 instances tries to access `full_name` → fails


## `ordered-steps` / sonnet — 8 of the responses carry arrows, 8 offending lines

    A typical cadence: generate new key → dual-verify period lasting ≥ max token lifetime → cut over signing → retire old key. Tools like a KMS (AWS KMS, Google Cloud KMS, Vault) can manage this lifecycle and expose the JWKS for you.

    Practical rollout: publish new key → wait for propagation (if using a JWKS cache, respect its TTL) → start signing new tokens with it → keep old key verifiable until expiry → remove old key.

    - Automate this as a pipeline: generate → dual-verify window → cutover signing → retire, rather than manual key swaps.

    1. **Publish multiple valid keys at once.** Keep a small keyset (e.g. JWKS endpoint or config list) mapping `kid` → public key. Sign new tokens with the new key, but keep the old public key available for verification until every token signed with it has expired.

    - Automate: add new key → wait TTL → remove old key, as two separate deploys, not one.

    1. **Give every signing key an ID.** Add a `kid` claim to the JWT header when signing, and maintain a keystore (JWKS or a DB table) mapping `kid` → public key.


## `design-alerting` / sonnet — 7 of the responses carry arrows, 7 offending lines

    **Alerts need to be multi-valued, separate from `guardrail`.** `result.guardrail` is single-valued, first-match-wins — but cap-pinned-2-cycles and pace-error->15%-2-cycles aren't guardrails at all (they don't appear in the guardrail list, don't change the cap), and floor_at_risk could be true in the same cycle a higher

    2. **Edge-triggered, not level-triggered, firing.** `quota_exceeded` and `floor_unreachable` stay true every cycle once tripped — alerting on every 5-minute cycle would page continuously for the rest of the day. Fire on the OK→condition transition, then re-notify on a slower cadence (e.g. hourly) while it persists, usi

    Four map straight onto `result.guardrail` from a single cycle: `quota_exceeded`, `floor_at_risk`, `floor_unreachable`, `config_invalid`. The supervisor just checks `result.guardrail` after each call, same as the existing line, generalized to a small table of guardrail → alert.

    - **Dedup**: several conditions (`quota_exceeded`, `floor_unreachable`) hold for the rest of the day once tripped. Firing on every 5-minute cycle would page repeatedly for hours — alert on the state transition (not-firing → firing, and firing → resolved), which the persisted per-condition state already supports once yo

    **Keep alert evaluation outside `govern()`.** The "Core purity" section is explicit that `govern()` is state+inputs→decision with no I/O, and its result carries only the single guardrail that won priority order. But alerting needs things guardrails don't carry — pace-error magnitude, whether the cap is pinned at a band

    - Most of these (`quota_exceeded`, `feed_stale`×3, cap pinned×2, pace error×2, `floor_at_risk`, `floor_unreachable`, `config_invalid`) can be raised inline by the supervisor right after each cycle's `govern()` call, extending the existing `if result.guardrail == "quota_exceeded"` check into a small table of condition →


## `design-cache` / sonnet — 3 of the responses carry arrows, 5 offending lines

    - **Not personalized** → put a CDN/edge cache in front (Cloudflare, Fastly, your LB), keyed by product ID/slug. TTL as a safety net, explicit purge on product update/price/stock change. This is the only option that actually removes the 900ms rather than shaving it — a hit never reaches your origin or the DB.
    - **Personalized** → cache at the app layer instead: Redis, cache-aside pattern, keyed by product ID, caching only the parts that don't vary per user (description, images, attributes). Short TTL as backstop, invalidate on write. Keep price/stock as a separate fast lookup so you don't serve stale prices from a long-live

    Recommendation: Redis keyed by product ID, read-through (miss → hit DB → populate), invalidated on write in the product-update path. That gets you off the 900ms without relying on a timer to paper over staleness.

    - **Same for everyone** → cache the rendered page at the CDN/edge (Cloudflare, Fastly, etc.), keyed by URL, TTL a few minutes, purged on product update via webhook. This skips your app server entirely, not just the DB — bigger win than an app-level cache if it applies.
    - **Personalized** → cache at the data layer instead: Redis/Memcached, cache-aside pattern keyed by product ID (`product:1234`), app checks cache first and falls through to DB on miss. TTL as a backstop (a few minutes) plus explicit invalidation on writes — when a product's price/stock changes, delete or update that ke


## `recall-rollback` / sonnet — 5 of the responses carry arrows, 5 offending lines

    Only partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02 — that part's correct. But the migration at 14:05 is what turned it into a 45-minute Sev1: once it added the `NOT NULL` column with no default, both the config revert (14:21) and the release rollback (14:33) failed

    Partly. The doc distinguishes trigger from cause of severity: the config change (`legacy`→`split`) was the **trigger** — it's what started the 500s at 14:02, since `v411` instances didn't recognize `split`.

    Partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02, since `v411` instances threw on the unrecognized value.

    Only partly. The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02, but the migration `0042` (adding a `NOT NULL` column with no default) is what made it unrecoverable — it's why reverting the config at 14:21 and rolling back to `v411` at 14:33 both failed to fix the error rate. P

    The config change (`legacy`→`split` in `v412`) was the **trigger**: it's what caused the first 500s at 14:02, since `v411` instances didn't recognize `split`.


## `design-audit-log` / sonnet — 4 of the responses carry arrows, 4 offending lines

    Given the shape here — Express routes → `db.write()` → Postgres, with every write already funneled through the one function in `db.js:13-26` — the fork is between building the log in the app layer vs. the DB layer, and where you get "who" from.

    Given the shape here — Express routes → `db.write()` → Postgres, with every write already funneled through the one function in `db.js:13-26` — the fork is between building the log in the app layer vs. the DB layer, and where you get "who" from.

    2. **What "before" means.** `RETURNING *` (already used everywhere) gives you the *after* state for free. The *before* state requires a `SELECT ... FOR UPDATE` ahead of the `UPDATE`, inside the same transaction, which most compliance audit-trail requirements ("who changed what" implies old value → new value) actually n

    2. **Insert the audit row in the same transaction as the real write.** `write()` already does `BEGIN` → query → `COMMIT`/`ROLLBACK`; add an `INSERT INTO audit_log` before the commit, using the `RETURNING *` row it already fetches as `new_row` JSONB. Same transaction means the audit entry can't be lost to a later rollba


## `drift-service` / sonnet — 4 of the responses carry arrows, 4 offending lines

    4. No header → current behavior (always inserts), so the fix is additive.

    5. Missing header → skip the dedup path, insert as today (or reject with 400, depending on whether you want to mandate it).

    Note: this treats retries as "same key → same result" without checking `sku`/`quantity` match — good enough if the client owns key generation correctly; add a payload-hash check if that trust is unwarranted.

    - Missing header → treat as non-idempotent (current behavior) or reject with 400, depending on how strict you want it.


## `design-rate-limit` / sonnet — 3 of the responses carry arrows, 3 offending lines

    **Recommendation:** a per-`client_id` token bucket, enforced in that same auth middleware right after `req.client` is set, backed by the existing Redis instance (one Lua script per request, `EVAL`, so the check-and-consume is atomic — plain `INCR`+`EXPIRE` isn't, and you need atomicity since 4 workers × N boxes are hit

    - **Where it lives** — in-app middleware (recommended here, since Redis is already the cross-box shared state and plan data already lives next to it) vs. a limiter at the load balancer/gateway in front of all boxes. The gateway option decouples it from app deploys but means duplicating the client_id→plan lookup somewhe

    1. **Bucket per plan, not a global constant** — `api_keys.plan` already exists in the schema, so the limiter should read rate/burst from a small plan→limit map rather than hardcoding one number for every client.


## `holdout-explain` / haiku — 2 of the responses carry arrows, 3 offending lines

    3. **Fixed waits don't scale**: The fixed 1-second sleep is arbitrary. It's long enough to be frustrating but short enough that clients retry faster than most services can recover. Exponential backoff (1s → 2s → 4s → 8s) spaces retries out and gives the service recovery time.
    **The cascade**: One failed upstream → 5 attempts per client → all clients retry synchronized → service can't recover because retry traffic is heavier than initial traffic → more timeouts → more retries → worse outage.

    **What it should do instead**: Use exponential backoff (1s → 2s → 4s → 8s) with random jitter so retries spread out over time and give the service room to recover. Or implement a circuit breaker that stops retrying after detecting systemic failure.


## `holdout-verdict` / haiku — 2 of the responses carry arrows, 3 offending lines

    **1. Payment data retention mismatch** — The logs contain card digits and transaction IDs that Finance must preserve for seven years. Deleting at day 366 violates that constraint. You need a split policy: non-payment logs → 1 year, payment-related logs → 7 years (in cold storage).
    - Separate payment and non-payment indices. Payment logs → cold at 1 year, deleted at year 7. Request logs → cold at 1 year, deleted at year 1.

    3. **Policy split**: Consider splitting retention by log type. Non-payment logs (requests, errors) could follow the 30→cold→delete path for cost and compliance. Payment logs need a separate 7-year path with a clearer archival strategy (cloud archive, different index template, etc.).


## `verdict-experiment` / haiku — 2 of the responses carry arrows, 2 offending lines

    2. **Guardrail threshold is ambiguous**: "moved against us by more than 2%"—is that absolute or relative? A payment error rate going from 2% → 2.04% is +2% absolute but +2% relative. Clarify this; likely means absolute for rates and relative for revenue/duration.

    2. **Guardrail threshold is ambiguous**: "moved against us by more than 2%"—is that absolute or relative? A payment error rate going from 2% → 2.04% is +2% absolute but +2% relative. Clarify this; likely means absolute for rates and relative for revenue/duration.


## `design-realtime` / haiku — 2 of the responses carry arrows, 2 offending lines

    SSE is simpler than WebSockets (one-directional, no client→server needed), works in all browsers, and removes the refresh pattern entirely. The client opens a connection with `new EventSource('/api/metrics-stream')` and listens for updates; the server writes `data: {...}\n\n` when metrics change.

    SSE is simpler than WebSockets (one-directional, no client→server needed), works in all browsers, and removes the refresh pattern entirely. The client opens a connection with `new EventSource('/api/metrics-stream')` and listens for updates; the server writes `data: {...}\n\n` when metrics change.


## `design-upload` / haiku — 2 of the responses carry arrows, 2 offending lines

    The stack looks like: form with `<input type="file" accept="image/*" capture="environment">` on the client → compress → POST to `/api/listings/:id/photos` → validate and store in S3 → return URL → frontend stores it in the listing record. For mobile web, `capture="environment"` opens the phone camera directly.

    The stack looks like: form with `<input type="file" accept="image/*" capture="environment">` on the client → compress → POST to `/api/listings/:id/photos` → validate and store in S3 → return URL → frontend stores it in the listing record. For mobile web, `capture="environment"` opens the phone camera directly.


## `stale-cache` / sonnet — 2 of the responses carry arrows, 2 offending lines

    So the chain is: client asks Varnish for flags every 60s (fine) → Varnish, seeing the client will accept anything up to 3600s old, keeps handing back the same stale cached copy instead of revalidating with the origin → a flag change sits behind Varnish's cache for up to an hour before any client's 60s refetch actually 

    So the chain is: client asks Varnish for flags every 60s (fine) → Varnish, seeing the client will accept anything up to 3600s old, keeps handing back the same stale cached copy instead of revalidating with the origin → a flag change sits behind Varnish's cache for up to an hour before any client's 60s refetch actually 


## `destructive` / sonnet — 2 of the responses carry arrows, 2 offending lines

    - **IDs restart at 1** once recreated. `fixtures/users.json` has no `id` field, so ids get assigned in file order (Ada → 1, Grace → 2). If old `sessions`/`invoices` rows survive (they will, since dropping doesn't touch them unless you cascade-delete), those rows' `user_id` values now silently point at the *new* Ada/Gra

    - Or delete rows in dependency order: `sessions` → `invoices` → `users`, then reseed.


## `ordered-steps` / haiku — 1 of the responses carry arrows, 1 offending lines

    **Timeline:** Deploy validator changes → add new key → wait for grace period → remove old key. No one logs out.


## `design-realtime` / sonnet — 1 of the responses carry arrows, 1 offending lines

    Recommendation: server-sent events (SSE), not polling. Ops dashboards are one-directional (server → client), and SSE gives you push updates over plain HTTP with automatic reconnection built into the browser's `EventSource` API — no need for full WebSocket complexity.


## `design-search` / sonnet — 1 of the responses carry arrows, 1 offending lines

    - **Prefix matching**: users typing "a few words" often want partial/last-word matches ("head" → "headphones"), which plain `tsquery` won't do. Needs the `:*` prefix trick on the last token, or `pg_trgm` for typo tolerance — pick one now since it changes the index type (GIN on tsvector vs GIN on trigram).


## `holdout-design` / sonnet — 1 of the responses carry arrows, 1 offending lines

    Don't make it a plain boolean — make it a percentage rollout with consistent hashing on user/session ID, so you can go 1% → 100% instead of a hard cutover, and so a given user doesn't flip between old and new checkout mid-session. Because this is checkout, the kill switch matters as much as the activation: going back t


## `holdout-explain` / sonnet — 1 of the responses carry arrows, 1 offending lines

    The mechanism end-to-end: upstream gets slow → callers don't fail fast, they retry for up to ~2.5 minutes each without jitter or backoff → concurrent callers pile up holding connections/threads → the caller's own service exhausts its pool and becomes unavailable too → and the synchronized retry pulses keep re-hitting t


## `verdict-schema` / sonnet — 1 of the responses carry arrows, 1 offending lines

    The `DOUBLE PRECISION` → `NUMERIC` change and the append-only/idempotency guarantees are the ones worth blocking the sprint on; the rest can be tightened as you build the ledger logic.


## `conditional` / haiku — 1 of the responses carry arrows, 1 offending lines

    Don't raise it yet — this is a connection leak, not high load. The waiting queue is climbing continuously (7 → 11 → 14 → 19 → timeout → 23 → 28 waiting requests over two minutes), which means connections aren't being released back.
