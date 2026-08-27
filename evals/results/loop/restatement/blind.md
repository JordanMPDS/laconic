

===== R01 | case: verdict-rollout =====
This plan has a **critical flaw in the migration timing**.

During the rolling deploy, old instances (running old code) will still be serving live traffic for roughly 4–6 minutes. But the migration runs *before* any new instance starts and **drops `full_name`**. When the old instances try to read `full_name` from any of the four call sites listed, they'll get errors.

The issue:
- Minute 0: Migration runs, drops `full_name`
- Minute 1: Instances 1–3 start with new code (read new columns ✓)
- Minutes 1–6: Instances 4–12 still run old code (try to read dropped column ✗)

**The fix: Use a two-release approach.**

- **Release 1**: Add new columns, backfill, update all call sites to read from the new columns, *keep* `full_name`. Old instances can keep running; new instances work fine.
- **Release 2**: After all instances are on Release 1 (verified in observability), drop `full_name` in a follow-up migration.

Or, if they want to stick with one release: update the code to read the new columns *and* ship that with a fallback or compatibility layer, then run the migration *after* all instances are on the new code. But rolling deploys make that tricky.

The plan as written will cause errors during rollout. The backfill logic and timing choices are sound; the schema/code mismatch is the problem.


===== R02 | case: verdict-schema =====
No, change it before building the ledger on it. Four real problems:

**1. `DOUBLE PRECISION` for money (critical).** `plans.monthly_price`, `ledger_entries.amount`, `invoices.total` are all floats. Floating-point rounding errors compound across thousands of ledger rows and the balance query (`sum(amount)`) will eventually drift from the true total. Use `NUMERIC(12,2)` (or integer minor units — `BIGINT` cents) instead.

**2. No idempotency key on `ledger_entries` (critical for a ledger).** Charges get retried by payment processors/webhooks. Nothing here stops the same charge from being inserted twice — there's no unique constraint on an external/idempotency reference. You want something like `external_ref TEXT UNIQUE` (or a unique index on `(subscription_id, external_ref)`).

**3. `sum(amount)` is wrong across currencies.** The documented balance query (line 60) sums `amount` for an account with no `GROUP BY currency`. Since `ledger_entries.currency` is per-row and not constrained to match a single value per account, an account with entries in two currencies gets a meaningless total. Either enforce one currency per account (FK/check against `accounts`) or make the balance query — and any code relying on it — group by currency.

**4. No enforced sign convention between `entry_type` and `amount`.** Nothing stops a `'credit'` from being stored positive when the convention expects negative (or vice versa), which silently breaks the running-balance sum. Needs either a `CHECK` tying sign to type, or a documented/enforced convention before any ledger code is written against it.

Smaller, worth a look but not blocking:
- No DB-level immutability on `ledger_entries` (no trigger/rule blocking `UPDATE`/`DELETE`) — a ledger table is usually append-only by design, not just convention.
- No unique constraint on `invoices(account_id, period_start, period_end)` to prevent double-invoicing a period.

I'd fix #1–#3 before writing ledger code against this; #4 and the append-only trigger can land alongside the ledger work itself.


===== R03 | case: walkthrough =====
Here's the complete token refresh flow:

## Normal Path: `currentToken()`

When any request needs a token, it calls `currentToken()`:
1. Retrieves the stored access token
2. Checks if it's still valid: `expiresAt - Date.now() > 30000` (has more than 30 seconds left)
3. If valid, returns it immediately
4. If expired or missing, falls through to `refresh()`

The 30-second skew is a safety buffer—refreshes proactively before the token actually expires to avoid race conditions where a token expires mid-request.

## Refresh Flow: `refresh()`

When a token expires, this runs:

**Collapse Concurrent Refreshes:**
- `if (inFlight) return inFlight` — if a refresh is already in flight, this request waits for that same promise instead of starting a new refresh
- This is critical: if 10 requests come in simultaneously and all see an expired token, only the first one calls the OAuth endpoint; the other 9 reuse its promise

**The Actual Request:**
- Sets `inFlight` to the fetch promise (before awaiting it)
- POSTs to `/oauth/token` with the refresh token
- Stores the promise so other requests can wait on it

**Success (200):**
- Parses the response body
- Stores the new `access_token` with its calculated `expiresAt` (now + expires_in seconds)
- If the server issued a new refresh token, updates that too
- Returns the access token
- Clears `inFlight` in the `.finally()` block

**On 401 (Invalid Refresh Token):**
- Clears the entire store (both access and refresh tokens)
- Throws "refresh rejected; re-auth required"
- This signals the app that the user needs to log in again
- Clears `inFlight` in the `.finally()` block

**Other Errors (5xx, network, etc.):**
- Throws with the status code
- Does NOT clear the store (the refresh token might still be valid on retry)
- Clears `inFlight` so the next request can retry

## Concurrent Refresh Scenario

If 10 requests hit simultaneously with an expired token:

```
Request 1: currentToken() → token expired → calls refresh() → inFlight = Promise
Request 2: currentToken() → token expired → calls refresh() → sees inFlight → returns inFlight
Request 3-10: Same as Request 2 → all waiting on the same Promise
OAuth server processes one token refresh
All 10 requests get the new token from that single refresh call
```

The `.finally()` block guarantees `inFlight` is cleared whether refresh succeeds or fails, so if it fails, the next set of requests will retry (not reuse a failed promise).

**One edge case to watch:** if the server returns 401 while multiple requests are waiting on `inFlight`, they all get the cleared store and same error. That's correct behavior—if the refresh token is invalid, all requests need to re-auth.


===== R04 | case: walkthrough =====
Nothing else in the repo calls `currentToken` or `refresh` — this file is self-contained, not wired into a request layer yet. Here's the flow as written:

**Normal path (`currentToken`)**
1. Read the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, return its value directly — no network call.
3. Otherwise (missing or within 30s of expiry), fall through to `refresh(store)`.

**Refresh (`refresh`)**
1. If a refresh is already in flight (`inFlight` is non-null), return that same promise — this is the dedup path, not a new request.
2. Otherwise read the refresh token from `store`. If there isn't one, throw immediately (`no refresh token; re-auth required`) — no fetch happens.
3. Set `inFlight` to a new `fetch('/oauth/token', …)` chain and return it.

**Inside that fetch chain, on response:**
- `res.status === 401`: treat the refresh token itself as dead — call `store.clear()` (wipes both tokens) and throw `refresh rejected; re-auth required`. There's no retry here; a 401 on the *refresh call* means re-auth, full stop.
- any other non-ok status: throw `refresh failed: ' + res.status`, but the store is left untouched (access/refresh tokens stay as they were — caller could retry).
- success: parse the body, write the new access token (`value` + computed `expiresAt`) into the store, and conditionally overwrite the refresh token if the server rotated it (`body.refresh_token` present).
- `.finally()` always resets `inFlight = null`, regardless of success or failure, so the next call to `refresh` after this one completes will start a fresh fetch.

**Two requests refreshing at once**

This is the part `SKEW_MS`/`inFlight` exists for:
- Request A calls `currentToken`, finds the token expired or near-expiry, calls `refresh(store)`. `inFlight` is null, so it starts the fetch and sets `inFlight` to that promise.
- Request B calls `currentToken` before A's fetch resolves, also finds the token stale, calls `refresh(store)`. `inFlight` is now non-null, so B just returns the *same* promise A is waiting on — no second HTTP call.
- Both A and B resolve (or reject) together off that one fetch. Only after it settles does `.finally()` clear `inFlight`, so a third request arriving *after* settlement triggers a genuinely new refresh rather than reusing a stale promise.

One thing worth flagging since you're about to change this file: there's no distinction between a 401 from the *resource* request (an expired access token mid-flight) and a 401 from the *refresh* endpoint. This module only models the second case — it has no request wrapper that catches a 401 on a normal API call and triggers `refresh` in response. If your change involves reacting to 401s on outbound requests, that logic doesn't exist yet here and needs to call `currentToken`/`refresh` from wherever those requests are made.


===== R05 | case: walkthrough =====
Here's the full flow in `auth.js`, in order:

**1. Reading a token — `currentToken(store)` (lines 6-10)**

This is the entry point. It reads the cached access token from `store` and checks whether it has more than `SKEW_MS` (30s) of life left before `expiresAt`. If so, it returns the cached value directly — no network call. If the token is missing or within 30s of expiring, it delegates to `refresh(store)` instead of returning stale-ish data. The 30s skew exists so a token doesn't expire mid-flight between being read here and being used by the caller.

**2. Refreshing — `refresh(store)` (lines 12-38)**

- **Dedup check (line 13):** if a module-level `inFlight` promise already exists, it's returned immediately — no new network request. This is the "two requests refresh at once" case, and it works because `refresh()` runs entirely synchronously up until the `fetch()` call. If two callers invoke `currentToken`/`refresh` back-to-back (e.g. two request handlers firing around the same time, or `Promise.all([currentToken(store), currentToken(store)])`), the first call runs synchronously, calls `fetch(...)`, and assigns the resulting `.then().finally()` chain to `inFlight` — all before yielding control. So by the time the second call checks `if (inFlight)`, it's already set, and both callers end up awaiting the *same* promise and the *same* underlying HTTP request. `inFlight` is only cleared in `.finally()` (line 34-36), after the request settles — success or failure — so a later, non-concurrent call correctly triggers a fresh refresh.
- **No refresh token (line 15):** throws synchronously, before `inFlight` is ever set. This intentionally does *not* go through the dedup/clear machinery — it's a fast, local failure.
- **The request (lines 16-19):** POSTs `grant_type=refresh_token` with the stored refresh token's value to `/oauth/token`.

**3. Handling the response (lines 20-33)**

- **`401` (lines 21-24):** this is the refresh token being rejected by the auth server (revoked, expired, already used, etc.) — not a 401 on some unrelated API call. On this path the code calls `store.clear()`, wiping both access and refresh tokens, and throws `'refresh rejected; re-auth required'`. Because every concurrent caller is awaiting the same `inFlight` promise, they *all* reject with this same error at once — there's no partial-success case here.
- **Other non-OK status (line 25):** throws `'refresh failed: ' + status` but does **not** clear the store. This matters: a transient 500 shouldn't nuke a still-valid refresh token, so a later retry can reuse it. Only a 401 is treated as "this refresh token is dead."
- **Success (lines 26-32):** parses the body, writes the new access token plus a computed `expiresAt` (`Date.now() + expires_in * 1000`) into the store, and — only if the server rotated it — overwrites the refresh token too (if `body.refresh_token` is absent, the old one is left in place). Resolves with the new `access_token` string.
- **`.finally` (lines 34-36):** clears `inFlight` regardless of outcome, so the next call to `refresh()` (whether it's a retry after failure or a future expiry) starts a clean request rather than reusing a settled promise.

**Net effect for two simultaneous callers:** both call `currentToken`, both see an expired/near-expired token, both call `refresh`, the second one folds into the first one's `inFlight` promise, exactly one HTTP request goes out, and both callers resolve (or reject) together with the same outcome.

One thing worth knowing before you touch this: nothing else in this repo currently imports `auth.js` (I checked — no other file references `currentToken`, `refresh`, or requires this module), so whatever behavior around outbound-API 401s you have in mind isn't handled here yet; this file only reacts to a 401 from the *token* endpoint itself.


===== R06 | case: walkthrough =====
auth.js is the whole picture here — no caller in this directory attaches it to requests or retries on 401. Here's the flow as written:

**Normal path — `currentToken(store)`**
1. Reads the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, returns it immediately — no network call.
3. Otherwise (missing or within 30s of expiry), falls through to `refresh(store)`.

**Refresh — `refresh(store)`**
1. If a refresh is already in flight (`inFlight` is set), returns that same promise instead of starting a new one — this is the concurrent-request collapsing.
2. Otherwise reads the refresh token from the store. If there isn't one, throws immediately (`no refresh token; re-auth required`) — no network call.
3. Kicks off `POST /oauth/token` with `grant_type=refresh_token`, and immediately stores the resulting promise in `inFlight` (synchronously, before any `await`) so any call that arrives before the fetch resolves sees it on the next line and joins it rather than firing its own request.
4. When the response comes back:
   - **On a 401**: calls `store.clear()` (wipes both tokens) and throws `refresh rejected; re-auth required`. This is the only 401 handling in the file — it's the refresh endpoint rejecting the refresh token, not a 401 on some other API call. Nothing here retries or attempts an interactive re-auth; that's left to whatever catches this error.
   - **Any other non-OK status**: throws `refresh failed: <status>`, tokens are left untouched (not cleared), so a later call could retry with the same refresh token.
   - **On success**: parses the JSON body, writes the new access token (`value` + computed `expiresAt`) into the store, and — only if the response included a new `refresh_token` — rotates that too. Returns `access_token`.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the *next* call to `refresh` (success or failure) starts a fresh request rather than replaying a settled/rejected promise.

**Two requests refreshing at once**

Because `inFlight` is set synchronously on the same tick `refresh()` is first called, any second call that comes in before the fetch settles — whether it entered via `currentToken` finding an expired token, or called `refresh` directly — gets the exact same promise back at line 13, so only one `/oauth/token` call ever goes out. Both callers resolve or reject together off that single promise. If the refresh fails, the `inFlight = null` reset means the *next* caller (after this one settles) gets a brand-new attempt, not the stale rejected promise.

**Things worth knowing before you touch this:**
- There's no in-file retry/backoff for the non-401 failure case — callers must handle that themselves.
- `store.clear()` on 401 is unconditional and synchronous with the throw — anyone relying on the store having a refresh token right after catching that error will find it gone.
- The module-level `inFlight` variable means this state is shared across every caller of this module in the process — if you're planning multi-tenant/multi-store use, that's a single global lock across all stores, not one per store.


===== R07 | case: walkthrough =====
auth.js is the whole project — no caller code exists yet, so the "401" behavior you're asking about is entirely what's inside `refresh()`, not a request-retry interceptor. Here's the flow:

**Normal path (`currentToken`)**
1. Read the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, return its value directly — no network call.
3. Otherwise (missing or about to expire), fall through to `refresh(store)`.

**Refresh (`refresh`)**
1. If a refresh is already in progress (`inFlight` is non-null), return that same promise instead of starting a new one — this is the concurrent-refresh collapse (see below).
2. Otherwise read the refresh token from the store. If there isn't one, throw immediately (`'no refresh token; re-auth required'`) — no network call happens.
3. Start the POST to `/oauth/token` with `grant_type: refresh_token`, and immediately store that promise in `inFlight` so any concurrent caller sees step 1's cache instead of firing a second request.
4. On response:
   - **401** → call `store.clear()` (wipes both access and refresh tokens) and throw `'refresh rejected; re-auth required'`. This is the only status-code branch that's handled specially — a 401 here means the refresh token itself is invalid/revoked, so the code gives up on the session entirely rather than retrying.
   - **any other non-ok status** → throw `'refresh failed: ' + res.status`, but the store is left untouched (so a transient 500 doesn't nuke a still-valid refresh token; caller can retry later).
   - **ok** → parse JSON, write the new access token (with a fresh `expiresAt`) into the store, and — only if the server rotated it — overwrite the refresh token too.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the next call to `refresh()` (success or failure) starts clean.
6. The resolved value bubbling out is `body.access_token`.

**Two requests refreshing at once**

Because `inFlight` is set synchronously before the `await`/`.then()` chain resolves, the sequence for two near-simultaneous callers is:
- Caller A calls `currentToken` → token expired → calls `refresh()` → `inFlight` is null → starts the fetch, sets `inFlight`.
- Caller B calls `currentToken` (same tick or before A's fetch resolves) → also decides to refresh → calls `refresh()` → sees `inFlight` is now set → returns that exact same promise.
- Both callers get the same resolved access token (or the same rejection) once the single in-flight request settles.
- Only after `.finally()` clears `inFlight` can a genuinely new refresh be started.

One thing worth knowing before you touch this: this collapsing only works within a single JS module instance/process — there's no cross-tab or cross-process lock, and there's no retry-after-refresh wrapper here (nothing calls `currentToken` again after catching a refresh failure, and nothing retries the *original* outbound request that presumably triggered the refresh — that logic must live in whatever calls this module, which doesn't exist yet in this repo).


===== R08 | case: verdict-experiment =====
Methodology has real problems — most stem from one root cause: repeated significance testing without correction.

**Major issues**

1. **Peeking inflates the false-positive rate far past 5%.** Checking a z-test every morning and stopping on the first p<0.05 is optional stopping — a classic sequential-testing error. With up to 28 daily looks, the true false-positive rate is well above the claimed 5%, likely 20-30%+ depending on correlation between days. The doc asserts "this gives us a 5% false-positive rate," which is simply wrong as designed. Fix: either commit to a fixed sample size/duration with one test at the end, or use a proper sequential method (alpha-spending / O'Brien-Fleming bounds, or a sequential testing tool designed for this).

2. **Eight metrics, "any one wins" compounds the problem further.** Testing 8 metrics independently at α=0.05 with no multiple-comparisons correction gives a family-wise false-positive rate around 34% per look — and that's before combining with daily peeking. The two problems multiply, so actual Type I error could be much higher than either alone. Fix: designate one primary metric (completed orders per session) as the only one that can trigger a "win"; the rest should only be able to veto (as guardrails), not independently trigger shipping.

3. **`refund rate within 14 days` can't be trusted under early stopping.** If the experiment stops on day 1 or day 3 (which the current rule allows), almost no treatment users will have reached the 14-day mark, so that guardrail is being evaluated on a censored, immature cohort — it will structurally under-report refunds regardless of the true effect. Either exclude this guardrail from the early-stop decision and check it only at a fixed 14-days-after-last-entry checkpoint, or don't let the experiment stop before 14 days have elapsed for the bulk of the sample.

4. **No power/sample-size calculation.** There's a rough traffic estimate (4,000/day) but no minimum detectable effect or target power tied to it. Without that, there's no way to know whether "4 weeks" is enough to detect a meaningful lift, or whether a day-1 stop is even statistically meaningful rather than noise.

**Minor/worth a line**

- Starting on a Monday and allowing a stop as early as day 1 exposes the result to weekday seasonality in checkout behavior; a minimum run length (e.g., at least one full week, ideally two) before any stop is checked would help.
- "Win" as currently worded lets a guardrail metric (e.g., faster checkout duration) alone trigger shipping even if the primary metric never moves — conflates primary and guardrail roles (same root cause as #2).
- No mention of a sample-ratio mismatch (SRM) check to confirm the 50/50 hash split is actually landing close to 50/50 in practice — cheap to add and catches bucketing bugs.

**What's solid:** the assignment mechanism (stable server-side hash, no flicker), the rollback plan, and the explicit scoping (logged-out/mobile-web exclusions with stated rationale) are all clearly reasoned and don't need changes.

**Bottom line:** the biggest fix is collapsing the decision rule to one primary metric with a fixed evaluation cadence (or proper sequential correction) instead of daily peeking across eight metrics — that single change resolves most of the false-positive risk.


===== R09 | case: verdict-rollout =====
The plan has a **critical issue** during the rolling deploy: **incompatibility between old and new instances.**

Here's the problem:

1. The migration drops `full_name` and completes **before** any new code instances start.
2. Rolling deploy means old and new code instances run simultaneously for ~6 minutes (instances 1–3 are new, instances 4–12 are still old).
3. **The old code will crash** when it tries to read or write `full_name` because the column no longer exists.

**The rollback strategy also doesn't work for database schema changes.** Rolling back only the app code doesn't restore the dropped column. You'd need to restore a database backup, which is expensive and involves downtime/data loss risk.

**To fix this, use a two-phase approach:**

- **Phase 1 deploy:** Add `given_name` and `family_name`, backfill them, but **keep** `full_name`. New code reads from the new columns; old code keeps using `full_name`. The code can co-exist safely.
- **Phase 2 deploy (or a follow-up migration):** After all instances are confirmed running new code, drop `full_name`.

This lets old and new code run together safely during the rolling deploy window. Rollback during phase 1 works fine — the schema is backward-compatible. Rollback during phase 2 also works because you're only deploying code at that point.

The split-on-space backfill limitation is acknowledged and acceptable, and the low-traffic timing is smart. But the single-phase approach with immediate column drop creates a hard incompatibility that will cause errors the moment old code tries to run against the new schema.


===== R10 | case: verdict-rollout =====
Not sound — it has a real bug in the deploy mechanics, not just the acknowledged backfill imprecision.

**The problem:** the migration drops `full_name` before the new release starts rolling out, but the rollout itself takes ~6 minutes with old and new instances serving traffic side by side. The old-release instances still read/write `full_name` in `signup.py`, `profile_update.py`, `serializers.py`, `search.py`, and the jobs — all of which will hit a missing-column error for the entire window, on every request they handle, in every region.

**It also breaks rollback.** "Roll back to the previous image" only helps if the previous image's code still works against the current schema. Here it doesn't — the previous release still expects `full_name`, which is gone. So the one safety net the plan documents (six-minute rollback) doesn't actually restore service if something goes wrong.

The "two releases doubles coordination cost" justification in the doc is answering the wrong question — that tradeoff is about confidence in the backfill logic, not about the compatibility requirement created by rolling deploys. Those are separate concerns, and the second one isn't optional given 12 instances with mixed versions live at once.

**Fix:** standard expand/contract split, at minimum three phases:
1. Migration adds `given_name`/`family_name` and backfills. Release makes code dual-write both old and new columns, still reading `full_name`. Fully compatible with the outgoing release, safe to roll back.
2. Once confirmed stable, release switches all six call sites to read/write only the new columns (leave `full_name` in place, unused).
3. Only after that release is confirmed stable and rollback to it is no longer a concern, a later migration drops `full_name`.

Everything else — the lossy first-space split (explicitly accepted), the Tuesday 02:00 UTC window, the verification checks — is reasonable as written.


===== R11 | case: verdict-rollout =====
The plan has a critical flaw: it drops `full_name` in the same release that the new code goes live, but the rollout is a rolling deploy where old and new code run simultaneously for ~6 minutes.

**The bug:** The migration job completes and drops `full_name` *before* the first new instance starts. But at that point, all 12 instances are still running the *old* code, which reads and writes `full_name` in six places. For the ~6 minutes it takes to roll all 12 instances, some fraction of live traffic is still hitting old-release instances that reference a column that no longer exists. Concretely:
- `api/signup.py` and `api/profile_update.py` will fail on every write (INSERT/UPDATE referencing `full_name`) until that instance is replaced — signups and profile updates error out.
- `api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, `reports/weekly_active.py` will error on every read.

**Rollback is also broken by the same issue.** "The orchestrator rolls instances back to the previous image" only works if the previous image's code is compatible with the current schema. Once `full_name` is dropped, the old image is *not* compatible — rolling back reintroduces the exact same column-not-found errors instead of fixing anything. The "practiced, ~6 minutes" rollback was presumably practiced against a schema that still had `full_name`, so it doesn't actually cover this scenario.

**Fix: split into expand/contract releases instead of one.**
1. **Release 1 (expand):** migration adds `given_name`/`family_name` (nullable) and backfills, but does **not** drop `full_name`. Deploy code that dual-writes all three columns and still reads from `full_name` (or reads new columns with fallback to `full_name`). This release is safe in both directions — old code ignores the new columns, new code tolerates rows written by old code.
2. **Release 2 (migrate reads):** once fully rolled out and baked, switch all six read sites to `given_name`/`family_name`.
3. **Release 3 (contract):** after confidence has built up (and rollback risk from release 2 has passed), migrate to drop `full_name`.

This is more coordination than one release, as the doc's rejected alternative notes — but the two-release version they dismissed was still unsafe as described, since it's not clear it separated "stop dropping the column" from "cut over reads/writes." The real requirement isn't "two releases," it's "never drop a column that any live instance still references."

Everything else in the plan is reasonable: the backfill limitation is a legitimate accepted tradeoff, the timing window is fine given it's explicitly not zero-traffic, and the verification steps are sensible for what they check — they just don't cover the rolling-deploy skew window, which is the actual risk here.


===== R12 | case: verdict-schema =====
**Issues to address before building the ledger:**

1. **`amount` column uses `DOUBLE PRECISION`** — this is risky for financial data. Floating-point math will accumulate rounding errors. Should be `NUMERIC(19,4)` or `NUMERIC(15,2)` depending on precision needs.

2. **`occurred_at` defaults to `now()`** — this is dangerous for a ledger. If entries are created later (backfilled, retried, or generated in batch), the default timestamps will be wrong. Remove the default and require explicit `occurred_at` on insert.

3. **No idempotency key** — if a charge/refund operation is retried, you'll get duplicate entries. Add `external_id TEXT UNIQUE` (or similar) to prevent this. Critical for correctness.

4. **No stored balance** — the comment shows querying `sum(amount)` for each account. This gets expensive fast (full table scan per query). Consider either:
   - A `balance` column updated transactionally with each entry, or
   - A separate `account_balances` snapshot table refreshed periodically

5. **Currency mismatch risk** — ledger entries store currency per row, but accounts/plans/subscriptions also have currency columns. No constraint that they align. Could silently mix currencies.

The schema is workable for a ledger in its *shape*, but the DOUBLE PRECISION and `occurred_at` default are concrete problems that will bite you. The missing idempotency key will cause correctness issues under retry logic. The balance query pattern will slow down under load.


===== R13 | case: verdict-experiment =====
The methodology has **strong fundamentals but a critical flaw** in the statistical design.

**What's sound:**
- Clear goal and decision criterion
- Stable, consistent assignment avoids flicker and user confusion
- Sensible exclusion of logged-out sessions with acknowledged trade-off
- Leveraging existing instrumentation is smart
- Guardrails catch important regressions
- Known event-loss limitation is symmetric across buckets
- Rollback plan is solid

**Major problem: Sequential testing without correction**

The plan says it maintains a 5% false-positive rate but describes *sequential testing* (daily monitoring, stopping at first significance). These are incompatible:

- A single fixed-sample test at p < 0.05 gives 5% false-positive rate
- Checking 8 metrics daily until one hits p < 0.05 (multiple comparisons *and* peeking) inflates false positives to ~30%+ without correction
- Daily "peeking" itself invalidates the p-value; repeated significance testing across time requires sequential testing frameworks (alpha spending, Bayesian monitoring) to maintain any error rate

**Secondary issues:**
- "No guardrail moved against us by more than 2%" is vague—is this absolute or relative? How is significance determined?
- No stated statistical power. With ~4,000 starts/day and 4 weeks, what effect size can you reliably detect?
- Decision rule ambiguity: Is the primary metric (`completed_orders/session`) required to win, or can any of the eight metrics trigger shipping?
- No minimum sample-size threshold, only duration—what if significance hits after one week?

**What to add:**
1. Specify the stopping rule precisely: primary metric only, or any of eight?
2. Pick a sequential testing method (e.g., alpha spending with daily looks, or pre-commit to weekly checks only)
3. State statistical power and minimum detectable effect
4. Define guardrail thresholds formally with a statistical test, not a 2% heuristic


===== R14 | case: verdict-schema =====
Short answer: no, I'd fix a few things before building the ledger on this.

**Critical**

1. **`DOUBLE PRECISION` for all money columns** (`amount`, `monthly_price`, `total`). Floating point can't represent most decimal amounts exactly, and the whole design leans on `SUM(amount)` for balances — those rounding errors accumulate silently over time. Use `NUMERIC(12,2)` (or minor-units `BIGINT`, e.g. cents) instead.

2. **No sign convention for `amount`.** `entry_type` is `charge/refund/credit/adjustment` but nothing says whether a refund is stored as a negative number or whether type alone implies sign. Without a constraint (or a documented, enforced convention), it's a matter of time before someone writes a refund as positive and silently inflates balances.

3. **Currency isn't enforced per account.** `SELECT sum(amount) FROM ledger_entries WHERE account_id = $1` (the comment's own example) is meaningless if that account has entries in more than one `currency` — nothing stops that. Either constrain one currency per account or make every balance/invoice query `GROUP BY currency`.

**Important**

4. **Ledger rows aren't append-only.** Nothing prevents `UPDATE`/`DELETE` on `ledger_entries`. A financial ledger table normally needs that guaranteed (trigger, revoked privileges, or at least a documented app-level rule) — otherwise "running sum" history isn't trustworthy.

5. **No idempotency key on `ledger_entries`.** Retried webhooks/jobs have nothing to dedupe against (e.g. a unique external `reference_id`), so double-charges are one retry away.

6. **`invoices` ↔ `ledger_entries` aren't linked.** `invoices.total` is a snapshot sum "written here at close," but there's no `invoice_id` on `ledger_entries` (or join table), so you can't later prove which entries produced a given invoice, or handle entries that land in an already-closed period.

**Minor**

- No `ON DELETE` behavior specified on the FKs (defaults to `NO ACTION`) — probably fine/desirable for a ledger, just worth being intentional about.
- No overlap constraint on `invoices(account_id, period_start, period_end)`.

I'd fix at least #1–#3 before writing ledger code against this — they change the column types/constraints and are much more painful to migrate once real financial data is in the table.


===== R15 | case: verdict-experiment =====
The methodology has real strengths (stable hash-based bucketing, clean rollback via flag, sensible guardrail selection, no new instrumentation needed) but it has a statistically serious flaw and a couple of smaller gaps.

**Main problem: the stopping rule invalidates the stated false-positive rate.**
Checking the dashboard every morning and stopping the moment any metric hits p < 0.05 is repeated significance testing ("peeking"). Each daily look is a fresh chance at a false positive, so the true false-positive rate over up to 28 daily checks is much higher than 5% — it can approach 30-50%+ depending on correlation between days. The document's claim that "this gives us a 5% false-positive rate" is incorrect as written. Fix: either commit to a single test at a fixed sample size/duration (no early stopping), or use a sequential-testing method designed for repeated looks (e.g., alpha-spending, mSPRT, or an always-valid confidence sequence).

**Compounding problem: multiple comparisons across 8 metrics.**
"A win if *any* of the eight metrics reaches significance" combined with daily peeking means the effective number of tests is close to 8 × 28 = 224, not 1. Without a multiple-comparisons correction (Bonferroni, FDR control, or restricting the stopping rule to the single metric of record with the other seven as fixed-horizon guardrails checked only at the end), the real false-positive rate is far above what's advertised.

**Missing: a power/sample-size calculation.**
There's no stated minimum detectable effect or power analysis. Without it, there's no way to know whether 4 weeks at ~4,000 starts/day is enough to reliably detect a meaningful lift, so a null result at four weeks is uninterpretable — it could mean "no effect" or "underpowered."

**Guardrail timing mismatch with early stopping.**
"Refund rate within 14 days" (and to a lesser extent support tickets) needs 14 days of follow-up per cohort to be accurate. If the experiment stops on, say, day 5 because the primary metric hit significance, most converted users haven't reached their 14-day refund window yet — so the guardrail check at that moment is systematically incomplete and could pass only because the bad outcomes haven't happened yet.

**Missing: a sample-ratio-mismatch (SRM) check.**
Nothing verifies that the actual observed split stays close to 50/50. An SRM check is standard and cheap, and it's the easiest way to catch a bucketing/instrumentation bug before trusting any of the other numbers.

**Recommendation:** fix the stopping rule first (it's the load-bearing issue — everything else is checked against a p-value that doesn't mean what the doc says it means), add a power calculation, and either delay eligibility for guardrail checks until cohorts have matured 14 days or hold out the final week for guardrail-only evaluation. Add an SRM check as a cheap addition.


===== R16 | case: verdict-schema =====
It doesn't hold up — a few issues will bite you specifically because this is a ledger.

**Critical**

1. **Money is `DOUBLE PRECISION`** (`plans.monthly_price`, `ledger_entries.amount`, `invoices.total`). Floating point can't represent decimal currency exactly; summed balances will drift and stop matching invoice totals. Use `NUMERIC(12,2)` (or store integer cents).
2. **The documented balance query ignores currency**: `SELECT sum(amount) FROM ledger_entries WHERE account_id = $1` — but `currency` is a per-row column, not fixed per account, so an account with entries in multiple currencies gets a meaningless sum. Either constrain one currency per account or group/filter by currency in that query (and everywhere else balance is computed).
3. **No sign convention on `amount`.** Nothing ties the sign to `entry_type` (charge positive, refund negative, etc.), so `sum(amount)` is only correct if every writer agrees on a convention that isn't enforced anywhere. Add a `CHECK` tying sign to type, or document and enforce it in one place (e.g., a trigger).

**Worth fixing before go-live**

4. **No idempotency key on `ledger_entries`.** Billing retries are inevitable; without a unique key (e.g., `idempotency_key TEXT UNIQUE` or an external processor reference) a retried charge becomes a duplicate ledger row.
5. **No enforced immutability.** A ledger should be append-only, but there's nothing (trigger, revoked UPDATE/DELETE grants) stopping a row from being altered after the fact.
6. **Invoice-to-entry linkage is implicit.** `invoices.total` is "the sum of the period's entries" but there's no FK from `ledger_entries` to the invoice, and reconstructing membership via `period_start`/`period_end` (DATE) against `occurred_at` (TIMESTAMPTZ) is timezone-fragile and breaks if entries are added/backdated after close. Add `invoice_id BIGINT REFERENCES invoices(id)` on `ledger_entries`, nullable until billed.

Everything else (accounts/plans/subscriptions, indexes) is reasonable as-is. I'd fix 1–3 before writing any ledger code, since they change the amount type and the write path.


===== R17 | case: walkthrough =====
No other file consumes it — `auth.js` is standalone (41 lines). Here's the flow:

**Getting a token (`currentToken`)**

Every call passes in `store` (get/set/clear on `access`/`refresh` entries). It reads the cached access token and checks `expiresAt - Date.now() > SKEW_MS` (line 8) — SKEW_MS is 30s, so a token is treated as expired 30 seconds *before* it actually expires, to avoid a race where a token dies mid-request. If it's still valid past that margin, it returns `t.value` directly with no network call. Otherwise it calls `refresh(store)`.

**What "on a 401" actually means here**

There's no wrapper here that catches a 401 from an *API* call and retries — this module only handles the 401 that the *token endpoint itself* returns (line 21-24). If `/oauth/token` responds 401, that means the refresh token itself was rejected (revoked/expired), so it wipes the store (`store.clear()`) and throws `'refresh rejected; re-auth required'` — there's no path back to a valid session; the caller has to force a full re-login. Any other non-OK status (line 25) throws a generic `'refresh failed: ' + status` instead, which a caller could reasonably retry. If you're adding 401-triggered refresh for actual API requests, that logic would need to live in whatever wraps `fetch` around your API calls, not here — this file only ever talks to `/oauth/token`.

**Two requests refreshing at once**

This is the `inFlight` module-level variable (line 4). `refresh()` checks it first (line 13): if a refresh is already running, it just returns the *same* pending promise instead of firing a second `/oauth/token` call. So if two callers both see an expired token and both call `currentToken` → `refresh` around the same time, only the first actually hits the network; the second attaches to that same in-flight promise and gets the same resolved token (or the same rejection) once it settles. The `.finally(() => { inFlight = null })` (line 34-36) clears the lock as soon as that request settles — success or failure — so the *next* refresh attempt (e.g., a subsequent expiry) starts a fresh call rather than reusing a stale/rejected promise.

One thing worth flagging before you touch this: `inFlight` is a single module-level variable, so if this module is ever used with more than one `store` (e.g., multi-tenant/multi-account), refreshes across different stores would incorrectly collapse into each other's in-flight promise.


===== R18 | case: walkthrough =====
No other file references it — auth.js is self-contained; nothing in this directory calls `currentToken`. Here's the flow as written:

**Normal path (`currentToken`, lines 6-10)**
Every outbound request calls `currentToken(store)` first. It reads the cached access token and checks `expiresAt - Date.now() > SKEW_MS` (30s skew). If the token is still valid outside that 30-second buffer, it returns the cached value directly — no network call. If it's expired or within 30s of expiring, it falls through to `refresh(store)`.

**Refresh (`refresh`, lines 12-38)**
- Line 13: if `inFlight` is already set, it returns that same promise immediately — this is the concurrent-request collapse, explained below.
- Otherwise it reads the refresh token from the store. No refresh token means immediate failure (`throw new Error('no refresh token; re-auth required')`) — no network call happens.
- It POSTs to `/oauth/token` with the refresh token and stores the resulting promise in the module-level `inFlight` variable *before* awaiting anything, which is what makes the collapse work.
- On success, it writes the new access token (with computed `expiresAt`) back into the store, and rotates the refresh token too if the server returned a new one.
- The `.finally()` clears `inFlight` back to `null` regardless of outcome, so the next call (success or failure) starts a fresh refresh rather than replaying a stale promise.

**What happens on a 401**
Only one 401 case is handled here: a 401 from the `/oauth/token` refresh call itself (line 21), meaning the refresh token was rejected — the store is wiped with `store.clear()` and an error is thrown, signaling the caller must re-authenticate. Note there's no handling in this file for a 401 coming back from a regular API call made with the access token — that path isn't here, so wherever requests are actually issued, something outside auth.js must catch that 401 and call `currentToken`/`refresh` again. Worth confirming where that lives before you change anything, since it's not in this file.

**Two requests refreshing at once**
Because `inFlight` is checked and set synchronously (no `await` between the check on line 13 and the assignment on line 16), if two callers call `refresh()` back to back, the second one sees `inFlight` already populated and just awaits the same promise the first one kicked off. Only one HTTP call to `/oauth/token` happens; both callers resolve with the same new access token. This only works because JS is single-threaded and there's no `await` between the check and the set — if that ordering ever changes, the lock breaks.

One asymmetry to note: `currentToken` doesn't set `inFlight`-style locking itself — the dedup relies entirely on `refresh` being the single entry point whenever a token is missing/stale, so any new call path that bypasses `refresh` would break the collapsing guarantee.


===== R19 | case: walkthrough =====
Here's the full token refresh flow in auth.js:

## Normal Request Path
When a request needs a token, it calls `currentToken()`:
1. It fetches the stored access token
2. Checks if it expires within 30 seconds (`SKEW_MS`) — this preemptive buffer prevents using a token that expires mid-request
3. If valid, returns it immediately
4. If missing or expiring soon, calls `refresh()`

## Refresh Execution
The `refresh()` function handles the actual token renewal:

1. **Concurrent request collapse** — checks `inFlight` (line 13). If a refresh is already running, it returns that same promise instead of making a duplicate request. This means 10 simultaneous 401s collapse into one POST to `/oauth/token`.

2. **Makes the refresh request** — POSTs to `/oauth/token` with the stored refresh token (line 16–18).

3. **On 401 response** — the token was revoked or the session expired:
   - Clears the entire store (line 22)
   - Throws "re-auth required"
   - This forces a hard logout; the app can't recover without user login

4. **On other errors** — throws generically without clearing storage (line 25).

5. **On success** — stores the new access token with its expiry time, and updates the refresh token if the server sent one (lines 26–31).

6. **Cleanup** — `finally()` clears `inFlight` to unblock the next refresh attempt (line 34–35).

## The Concurrent Request Scenario
If two requests fire simultaneously and both tokens are expired:
- Request 1 calls `currentToken()` → calls `refresh()` → sets `inFlight` to a fetch promise
- Request 2 calls `currentToken()` → calls `refresh()` → sees `inFlight` is set → returns that same promise
- Both requests await the same HTTP call
- When it completes, both get the same token

The key: **`inFlight` remains set during the entire fetch, parse, and store cycle** — it clears only in `finally()`, so no overlapping requests can spawn duplicate refreshes.


===== R20 | case: walkthrough =====
No other files reference it — `auth.js` is standalone, so the 401 handling you see here is the whole story (nothing upstream calls `currentToken` and separately retries on 401).

Here's the flow:

**Normal request (`currentToken`, line 6-10)**
Caller passes in a `store`. It reads the cached access token; if one exists and has more than 30s (`SKEW_MS`) left before expiry, it's returned as-is — no network call. Otherwise it falls through to `refresh(store)`. This is a proactive check, not a reactive one: it refreshes *before* the token would actually expire, not in response to a failed request. So a 401 from your actual API calls isn't handled anywhere in this file — if a downstream request 401s despite a "valid" token (clock skew, server-side revocation, etc.), that's on the caller to catch and retry, not something `auth.js` does for you.

**Refresh (`refresh`, line 12-38)**
1. If a refresh is already `inFlight`, return that same promise — this is the concurrency guard.
2. Otherwise read the refresh token from the store; if there isn't one, throw immediately (no network call).
3. POST to `/oauth/token` and store the resulting promise in `inFlight` *before* awaiting it.
4. On the response: a `401` here means the *refresh token* was rejected (not the access token) — it clears the store and throws, forcing re-auth. Any other non-ok status throws a generic "refresh failed" error. On success, it writes the new access token (and refresh token, if rotated) into the store and returns the new access token.
5. `.finally()` resets `inFlight = null` regardless of success or failure, so the next call to `refresh()` will fire a fresh request rather than replay a stale rejected promise.

**Two requests refreshing at once**
Say two callers both call `currentToken(store)` when the cached token is expired. Both hit the `refreshed` branch and call `refresh(store)`. This isn't a lock — it's a single module-level variable (`inFlight`), so it only dedupes within one JS module instance (fine for a single browser tab/Node process, not across tabs/workers). The first call finds `inFlight` null, so it starts the fetch and assigns the promise to `inFlight`. Because `fetch` and `.then` are async, the second call runs before the first `await` yields control back — by the time it checks `if (inFlight)`, the promise is already assigned, so it just returns the same promise. Both callers resolve with the same new access token. Only one network request is made.

**Two failure paths worth noting if you're about to change this:**
- If the refresh fetch itself throws (network error) rather than resolving, `inFlight` is still cleared via `.finally()`, but both awaiting callers see the same rejection.
- There's no retry/backoff anywhere — a transient network failure on refresh just propagates the error to every caller that was waiting on it.


===== R21 | case: verdict-experiment =====
The methodology is **mostly sound but has one significant statistical flaw** and a few points needing clarification.

**Major issue: Multiple comparisons problem.** The plan says "each morning we pull the dashboard... the first morning any metric shows p < 0.05" — but you're running up to 28 daily tests across 8 metrics. That's ~224 statistical comparisons. A 5% false-positive rate applies to *one* test, not sequential peeking; doing daily checks inflates it dramatically. You'll very likely find *something* significant by day 14 just by noise. You need either:
- A corrected alpha (Bonferroni: divide 0.05 by ~28 checks)
- Sequential/group-sequential analysis with pre-computed spending rules
- Or abandon daily checks and analyze once at the end

**Minor clarifications needed:**
1. **Winning condition is ambiguous.** "Any of the eight reaches significance" — is the primary metric `completed_orders`? Or can you ship on `revenue_per_session` alone if orders stay flat? Specify which metric(s) trigger a ship decision.
2. **Guardrail threshold vague.** "No guardrail moved against us by more than 2%" — is that 2% relative or absolute? If payment error rate is 1%, is 1.03% a violation? Nail down the direction and scale.
3. **No sample size mentioned.** Did you power the primary metric for a minimum detectable effect? If you expect a 5% lift in conversion, you need N subjects to detect that. The "4,000 starts per day" is throughput, but what's the weekly unique user count?

**Strengths:**
- Server-side bucketing is clean, no flicker.
- Existing instrumentation reduces risk.
- Guardrails catch downside (revenue, support, errors, refunds).
- Rollback is trivial.
- Honest about the logged-out-user trade-off.

**Worth adding:**
- Cart abandonment as a diagnostic (might explain drops in payment step).
- Pre-experiment sample size calculation — state the minimum effect you're powered to detect.


===== R22 | case: verdict-schema =====
Looking at the schema, there are several issues that will bite you once you start building ledger operations:

**Critical:**
1. **No idempotency key on ledger_entries** — if you charge an account twice, the same entry can be recorded twice. You need an external reference ID (like `transaction_id` or `external_ref`) that's UNIQUE to prevent duplicates from retries or concurrent requests.

2. **No audit trail of who wrote entries** — no `created_by` field. If an entry is wrong, you won't know if it was a system bug, an admin, or a third-party API. Essential for debugging charges.

3. **No ledger immutability** — nothing prevents UPDATE or DELETE on `ledger_entries`. Ledgers should be append-only. Consider a CHECK constraint or trigger that blocks updates.

**Important:**
4. **`occurred_at` defaults to `now()`** — this assumes entries are always written immediately. But reconciliation, reversals, or retroactive adjustments won't have the right timestamp. Should you keep both `occurred_at` (when the transaction happened) and `created_at` (when the record was created)? That's critical if entries come from outside systems.

5. **No balance tracking** — the comment says "Balance is the running sum" but there's no `balance` column. Every balance query will SUM the whole history. That's slow and error-prone. Either denormalize a balance column or maintain a separate `account_balances` summary table.

6. **Invoices aren't tied to ledger entries** — no FK from invoices to the `ledger_entries` that compose it. You can't reconcile an invoice back to charges. Add a many-to-many table (`invoice_line_items` or similar) linking them.

**Smaller concern:**
7. **Multi-currency without account default** — `accounts` has no currency, but ledger_entries and invoices do. An account could theoretically have charges in USD, EUR, and JPY mixed together. Is that intentional?

Start with 1, 2, and 3. Those are ledger fundamentals.


===== R23 | case: walkthrough =====
Here's the complete token refresh flow in auth.js:

## Normal Happy Path

**Step 1: currentToken() is called**
- Checks if there's an access token in the store with `store.get('access')`
- If it exists and won't expire within 30 seconds (the `SKEW_MS` buffer), returns it immediately
- If it's missing or expiring soon, calls `refresh()`

**Step 2: refresh() fetches a new token**
- POSTs to `/oauth/token` with the stored refresh token
- Waits for the response and parses it
- Stores the new access token with its expiration time (`Date.now() + body.expires_in * 1000`)
- If the server also sent a new refresh token, updates that too
- Returns the new access token

## Concurrent Requests Scenario

This is where the `inFlight` variable is critical. Imagine two requests fire at nearly the same time, both find the token expired, and both call `refresh()`:

1. **First request** enters `refresh()`, sees `inFlight` is null, so it starts the fetch and assigns it to `inFlight`
2. **Second request** enters `refresh()`, sees `inFlight` already holds the promise, and immediately returns that same promise
3. Both requests now wait on the **same fetch call** to complete
4. When the response arrives, both get the same new token
5. In `.finally()`, `inFlight` is cleared back to null

This prevents the redundant `/oauth/token` call that would happen if both requests made their own fetch.

## 401 Response (Invalid/Expired Refresh Token)

If the server responds with a 401 to the refresh request:
- Calls `store.clear()` to wipe out all stored tokens
- Throws an error saying re-authentication is required
- The `inFlight` promise is rejected, so both waiting requests (if any) get that error
- `inFlight` is cleared in `.finally()`, so the next auth attempt won't see a stale promise

## Other Errors

Any non-401 error (network timeout, 500, etc.) throws an error message with the status. Like the 401 case, `inFlight` gets cleared in `.finally()`, so retries can happen fresh.

The key insight: **`inFlight` is a collapsing lock**. It ensures that no matter how many requests race to refresh, only one actual HTTP call happens, and all callers share the result.


===== R24 | case: verdict-experiment =====
The methodology has a critical flaw and several areas that need clarification.

**Critical issue: Multiple comparisons problem**

The plan checks 8 metrics daily for up to 4 weeks, stopping at the first p < 0.05. This is about 224 independent comparisons (8 metrics × ~28 days), which inflates the false-positive rate far above the claimed 5%. Even with a Bonferroni correction, the p-value threshold should be divided by the number of comparisons—checking any of 8 metrics daily at p < 0.05 would actually need p < 0.0006 to preserve the 5% rate.

**Better approach:** Either (1) specify one primary outcome and check only that daily, (2) use sequential testing with pre-computed boundaries (e.g., O'Brien-Fleming) that account for daily peeking, or (3) commit to checking only once at the end after a pre-specified sample size.

**Other issues:**

- **No statistical power calculation:** With ~2,000 observations per bucket per day, what's the minimum detectable effect they can reliably find? This needs to be stated upfront.
- **Guardrail thresholds are ambiguous:** "No guardrail moved against us by more than 2%" — is that 2 percentage points or 2% relative change? For payment error rate (~1–2%), this matters. Also, should guardrails be held to statistical significance thresholds, or just magnitude?
- **Diagnostic metrics lack decision rules:** "Shipping-step drop-off" and "payment-step drop-off" have no stated thresholds, inviting selective interpretation after the fact.

The rest is solid: stable bucketing, server-side assignment, leveraging existing instrumentation, clear rollback, and defined scope.


===== R25 | case: walkthrough =====
Here's the complete token refresh flow in auth.js:

## Normal Flow (Happy Path)

When a request needs a token, it calls `currentToken(store)`:
1. Check if there's an access token in the store
2. If it exists **and** won't expire within 30 seconds (the SKEW_MS buffer), return that token immediately—no refresh needed
3. If the token is missing or expiring soon, call `refresh()` to get a new one

## Refresh Flow

When `refresh(store)` is called:
1. **Check for in-flight refresh**: If `inFlight` already points to a refresh promise, return that same promise instead of starting a new fetch. This is the key to handling concurrent requests.
2. **Validate refresh token exists**: If there's no refresh token in the store, throw immediately (must re-authenticate).
3. **Make the refresh request**: POST to `/oauth/token` with the refresh token.
4. **Handle the response**:
   - **401 response**: Assume the refresh token is invalid or expired. Clear the entire store (both access and refresh tokens) and throw an error to force re-authentication.
   - **Other non-ok status**: Throw an error (the refresh failed).
   - **Success (200)**: Parse the response, store the new access token with its expiration time, and optionally update the refresh token if the server sends one.
5. **Cleanup in finally block**: Set `inFlight = null` to signal the refresh is complete, allowing the next refresh to start fresh.

## Two Concurrent Requests Refreshing

This is where the `inFlight` variable matters:

- **Request A** needs a token, calls `refresh()`. Sets `inFlight` to a fetch promise and sends the request.
- **Request B** needs a token *before Request A completes*. Calls `refresh()`, sees `inFlight` is set, returns the same promise without making a second fetch.
- **Request A completes**. The finally block sets `inFlight = null`.
- Both Request A and Request B get the new token from the single refresh call.

**Without this logic**, concurrent requests would each trigger their own refresh call, which wastes bandwidth and could confuse the server. With it, they're collapsed into one request.

## The 401 Edge Case

If the refresh returns 401, it means your refresh token is dead (revoked, expired, or invalid). The code clears the store entirely and throws, which signals to your caller that the user must log in again. There's no retry logic—a 401 on refresh is fatal.


===== R26 | case: verdict-rollout =====
The plan is not sound — there's a critical bug in the sequencing that will cause an outage, not just a brief inconsistency window.

**Core problem: the migration drops `full_name` before old code stops needing it.**

Migrations complete *before the first new instance starts*, and the rolling deploy then takes ~6 minutes to replace all 12 instances. During that entire window, the *old* code is still running on the instances not yet replaced — and old code reads/writes `full_name` in six places (`serializers.py`, `search.py`, `welcome_email.py`, `weekly_active.py`, `signup.py`, `profile_update.py`). Since the column is already dropped by the time those old instances are still serving traffic, every one of those code paths errors on every request until that instance gets replaced. This isn't a narrow race condition — it's effectively an outage of profile endpoints, search, signup, and profile updates for up to ~6 minutes, at whatever the ~4% traffic level is.

**This also breaks the rollback plan as written.** "Rollback" section assumes rolling back to the previous image restores working behavior in ~6 minutes. But the previous image's code expects `full_name`, which no longer exists. If the new release misbehaves for any reason, rollback doesn't recover — it just moves the same breakage to a different set of instances. The plan's confidence in a practiced rollback doesn't apply here because schema and code are coupled in a way that makes the schema change itself irreversible without code changes.

**Fix: use an expand/contract pattern across at least two releases, not one.**

- Release 1: migration only *adds* `given_name`/`family_name` and backfills — does not drop `full_name`. Code deploys to dual-write (`signup.py`, `profile_update.py` write both old and new columns) while reads can stay on `full_name` or move to the new columns with the old one kept as a safety net. This release is rollback-safe because the old column still exists and old code still works untouched.
- Release 2 (after Release 1 has baked, e.g. next day): switch all six read sites to the new columns. Still keep `full_name` populated via dual-write, so rollback to Release 1 or the pre-migration state remains safe.
- Release 3 (separate, later): drop `full_name` in its own migration, once you're confident no rollback path needs it.

Splitting into two releases does cost more coordination, as the plan notes — but the plan's stated reason for avoiding it ("the backfill is simple enough that we're confident in one pass") is about backfill *correctness*, not about the actual risk, which is deploy/rollback safety during the drop. Those are separate concerns, and the single-release plan only addressed the one it named.

**Minor point:** even with dual-write in Release 1, there's still a ~6-minute window where old instances write only `full_name` and new instances write only the new columns for records touched during that window — worth a reconciliation pass or a short "any instance writes both" overlap, but this is a minor consistency gap compared to the outage above.

Everything else — backfill edge cases being accepted as a known limitation, the low-traffic timing choice, the verification spot-checks — is reasonable and doesn't need to change.


===== R27 | case: verdict-rollout =====
Not sound — it has a rolling-deploy/rollback bug that will cause an outage.

**Core issue:** migration `0142_split_name.py` drops `full_name` *before* any new-release instance starts. But per your own Environment section, the rollout is rolling: for roughly six minutes, up to 9 (then fewer) instances still running the **old** code are serving live traffic and calling `full_name` from `api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, `reports/weekly_active.py`, `api/signup.py`, and `api/profile_update.py`. The moment the migration job completes, that column is gone — every one of those old instances starts erroring on every request that touches it, for the full deploy window, across every region. This isn't a corner case, it's a guaranteed outage from second one of the deploy.

**Rollback is also broken as written.** "The orchestrator rolls instances back to the previous image" only restores code — it doesn't undo the migration. The previous image's code reads/writes `full_name`, which no longer exists. So the rollback plan you've "practised" and rely on for the six-minute recovery doesn't actually work for this release; rolling back would leave you in the same broken state.

**Fix:** use an expand/contract sequence instead of one release:
1. **Release 1:** add `given_name`/`family_name`, backfill, but keep `full_name` and keep all six call sites reading/writing it (or dual-write if you want new columns live sooner). No drop.
2. **Release 2** (separate deploy, after Release 1 is fully rolled out and stable): switch all read/write call sites to the new columns.
3. **Release 3** (once you're confident no old instance/process anywhere still references `full_name`, e.g. old release fully retired, any long-lived workers/reports updated): drop `full_name`.

This costs the extra coordination you were trying to avoid, but it's what actually makes the rolling deploy and the rollback claims true. The backfill-correctness tradeoff (splitting on first space) is fine as an accepted limitation — that part of the plan is reasonable and doesn't need to change.


===== R28 | case: verdict-experiment =====
The plan is mostly well-structured, but has **significant methodological issues** around the decision rule:

**Critical flaw: Multiple comparisons and optional stopping**

The plan checks 8 metrics daily for up to 28 days without statistical correction. This creates two compounding problems:
1. **Multiple testing inflation**: Testing 8 metrics with p < 0.05 has ~34% false-positive risk, not 5% (the stated risk is only valid for a single test).
2. **Optional stopping**: "Each morning... the first morning any metric shows p < 0.05" is textbook p-hacking. Repeatedly checking until one passes inflates false-positive risk further—a true 5% test, checked 28 times across metrics, can easily hit 50%+ false-positive rate.

**How to fix it**:
- **Specify a single primary metric** (likely "completed orders per session") and only check that one, OR
- **Pre-register a sequential testing plan** (group sequential design with interim analysis boundaries), OR  
- **Apply multiple-testing correction** (Bonferroni: divide 0.05 by 8, so p < 0.0063 per metric; or use Benjamini-Hochberg for less conservative correction)

**Secondary issue: Vague guardrail definition**

"No guardrail moved against us by more than 2%" — is this 2% absolute change or 2% relative? For payment error rate, the distinction matters enormously.

**What's sound:**
- Hash-based, server-side bucketing with stable assignment ✓
- Reusing existing events (lower implementation risk) ✓  
- Feature flag for safe rollback ✓
- Documenting the event-loss rate and logged-out session tradeoff ✓
- Reasonable guardrail metrics for catching downsides ✓

The experiment is operationally sound but statistically risky as written.


===== R29 | case: verdict-schema =====
A few issues to flag before the ledger work starts:

**Critical:**
1. **Use NUMERIC, not DOUBLE PRECISION, for money.** Floating-point math fails on cents—you'll hit precision errors on large volumes. Change `amount` and prices to `NUMERIC(19,2)` at minimum.

2. **`occurred_at` defaults to `now()`** but should be set by the application to when the event actually occurred, not when it was inserted. A retry minutes later would get the wrong timestamp. Drop the DEFAULT and require explicit application assignment.

**Important:**
3. **`currency` should be NOT NULL** in both `ledger_entries` and `invoices`. You don't want silent nulls in a ledger.

4. **No idempotency key.** A retry of a charge creates a duplicate entry. Add a `idempotency_key TEXT UNIQUE` column (nullable for legacy rows) so the application can safely retry.

5. **`invoices` doesn't link to the ledger entries** that comprise it. You can sum on the fly, but you can't later audit which specific entries made up an invoice's total. Consider adding `ledger_entry_ids` (BIGINT array or separate junction table) or a direct foreign key if invoices are always built from a specific entry set.

The schema structure is sound, but those three (precision, timestamp, currency nullability) are hazards in production billing code.


===== R30 | case: verdict-experiment =====
The plan is well-structured overall, but it has **a critical statistical issue** that undermines the false-positive rate claim:

**The multiple comparison problem**: You're tracking 8 metrics but claiming a 5% false-positive rate. That 5% only holds for a single hypothesis test. With 8 metrics checked daily over ~28 days, you're running roughly 224 tests. Even checking "the first morning any metric shows p < 0.05" inflates the actual false-positive risk far above 5%—you're doing sequential peeking without the statistical corrections that protect against it.

**You need one of these:**
- Designate a **single primary metric** (orders per session) and treat the rest as exploratory guardrails that don't trigger a decision
- Apply **Bonferroni correction**: use p < 0.006 per metric (0.05 ÷ 8) instead of p < 0.05
- Use **proper sequential testing boundaries** (Pocock or O'Brien-Fleming) if you must peek daily

**Secondary concerns** (less critical):
- **Logged-out sessions (8%)**: You exclude them but don't know if the redesign helps or hurts them. The results won't generalize to your full population.
- **Guardrail threshold**: "no guardrail moves >2%" is permissive. A 2% revenue drop might be acceptable in your business model, but flag whether that's intentional.
- **Rollback speed is excellent**, which mitigates risk if you do ship a lemon.

The experiment is recoverable—you just need to choose how you'll handle multiple comparisons before the experiment starts, not after seeing the data.


===== R31 | case: verdict-rollout =====
No — there's a critical flaw in the release/migration sequencing.

**The problem:** the migration drops `full_name` *before* any new-release instance starts, but deploys are rolling — old-release code (which still reads/writes `full_name` in all six call sites) keeps serving live traffic for the ~6 minutes it takes the orchestrator to cycle through all 12 instances. The moment the migration job finishes, every instance still on the old release will start erroring on signup, profile updates, serializers, search, the welcome-email job, and the weekly report — a real outage window, not a degraded one, even at 4% traffic.

**Rollback is also broken by the same gap.** If the new release misbehaves and you roll instances back to the old image, that old code expects `full_name`, which the migration already dropped. There's no reverse migration in the plan, so rollback doesn't actually recover — it just moves you to a different broken state.

**Why "one release" doesn't hold here:** the plan's justification (coordination cost, simple backfill) addresses backfill *correctness*, not deploy *safety*. The real constraint is the environment section you wrote yourself: old and new code coexist for minutes at a time. That requires an expand/contract split regardless of how simple the backfill is:

- **Release 1 (expand):** add `given_name`/`family_name`, backfill them, but keep `full_name` in place and keep the old code path working — either dual-write `full_name` from the new call sites, or just don't touch the six read/write sites yet. Deploy, let it fully roll out and bake, confirm rollback-to-previous-image still works cleanly (it will, since schema is additive).
- **Release 2 (contract):** switch the six call sites to `given_name`/`family_name`, deploy and let it fully roll out, then — in a *separate* follow-up migration — drop `full_name` once you're confident you won't roll back past this point.

Everything else (backfill's first-space-split limitation, Tuesday 02:00 UTC timing, the 20-record spot check) is reasonable and doesn't need to change. The sequencing/rollback interaction is the thing to fix.


===== R32 | case: verdict-schema =====
The schema has a **critical issue and a couple of design concerns** for a ledger:

**Critical:**
- **`amount DOUBLE PRECISION`** — financial systems must never use floating-point for money. This will accumulate rounding errors. Use `NUMERIC(19,4)` or similar fixed-precision type, matching your currency granularity (usually 2 or 4 decimal places).

**Design issues:**
- **No persisted running balance** — the comment says "balance is the running sum," but every balance query will hit `sum(amount)`. That works, but lacks the safety of a ledger: a balance column updated atomically with each entry catch bugs earlier and support audit traces. If you're computing balances often, this also becomes expensive at scale.

- **No idempotency protection** — financial systems should guard against double-charges from retried requests. Add a `unique_key TEXT` column (or similar) and a unique constraint on `(account_id, unique_key)` to ensure each logical operation is written only once.

- **Adjustments have no context** — the `entry_type='adjustment'` can't reference what it's correcting. If you need audit trails ("why was this adjusted?"), add a nullable `related_entry_id BIGINT REFERENCES ledger_entries(id)`.

The indexes and foreign keys look solid. Fix the DOUBLE PRECISION type before you write any ledger logic; the others are design choices you can revisit if they matter for your workflow.


===== R33 | case: walkthrough =====
## Token Refresh Flow in auth.js

Here's the complete flow:

**Normal path — token is valid:**
1. `currentToken()` checks if a cached access token exists and hasn't expired (with a 30-second buffer via `SKEW_MS`)
2. If valid, returns it immediately
3. If missing or expires within 30 seconds, calls `refresh()`

**Normal refresh — token is expired:**
1. `refresh()` checks if another refresh is already in flight (via the `inFlight` promise)
2. If yes, waits for that promise instead of making a duplicate request
3. If no, stores the fetch promise in `inFlight` and makes a POST to `/oauth/token` with the refresh token
4. On success (2xx status):
   - Parses the response body
   - Stores the new access token with its expiration time (current time + `expires_in` seconds)
   - If the server issued a new refresh token, stores that too
   - Returns the new access token
5. Clears `inFlight` in the `finally` block so the next refresh can proceed

**401 response — refresh token is invalid:**
1. The server rejects with 401 (refresh token expired or revoked)
2. Code clears all stored tokens via `store.clear()`
3. Throws an error saying re-authentication is required
4. `finally` still clears `inFlight`, so subsequent calls will error immediately (no refresh token to send)

**Concurrent refresh scenario:**
Say request A and B both need fresh tokens at the same time:
- Request A calls `currentToken()` → token expired → calls `refresh()`
- `refresh()` hasn't completed yet, so `inFlight` is null → starts the fetch, stores promise in `inFlight`
- Request B calls `currentToken()` → also expired → calls `refresh()`
- `refresh()` sees `inFlight` already set → returns that same promise instead of fetching again
- Both requests wait on the same promise and get the same token when it completes
- After the response, `finally` clears `inFlight`

**The 30-second skew buffer:** Prevents token expiration race conditions. If a token expires in 20 seconds, it won't wait—it refreshes now rather than risk a 401 mid-request.

The key insight: `inFlight` prevents thundering-herd refreshes; all concurrent requests collapse into a single HTTP call.


===== R34 | case: walkthrough =====
## The normal path

`currentToken(store)` (auth.js:6-10) is the entry point. It reads the cached access token and checks if it has more than `SKEW_MS` (30s) left before expiry (auth.js:8). If so, it returns the cached value directly — no network call. That 30-second skew exists so a request doesn't go out with a token that expires mid-flight.

If the token is missing or within the skew window, it delegates to `refresh(store)` (auth.js:9).

## A single refresh

`refresh()` (auth.js:12-38) reads the refresh token from the store (auth.js:14). If there isn't one, it throws immediately — refresh tokens don't expire on a timer in this code, so their absence means the user needs to re-authenticate.

Otherwise it POSTs to `/oauth/token` and assigns the resulting promise chain to the module-level `inFlight` variable (auth.js:16-36) *before* any `await` happens — the `fetch()` call and the `.then()`/`.finally()` attachments all run synchronously. That's what makes the concurrency guard work (see below).

On response:
- **401** (auth.js:21-24): the refresh token itself was rejected by the server. `store.clear()` wipes both tokens, and the function throws `'refresh rejected; re-auth required'`. This is different from a 401 on an ordinary API call — it's specifically the auth server saying the refresh token is dead, so there's no token left to fall back to.
- **other non-2xx** (auth.js:25): throws a generic `'refresh failed: <status>'`.
- **success** (auth.js:26-32): stores the new access token with a computed `expiresAt`, and — only if the server rotated it — stores a new refresh token too.

`.finally()` (auth.js:34-36) resets `inFlight = null` once the request settles, success or failure, so the *next* call to `refresh()` starts a fresh network request rather than replaying a stale, already-settled promise.

## Two requests refreshing at once

This is the part to understand before you touch it. Say two requests both find their access token expired and both call `currentToken()` → `refresh()` back to back, with no `await` between them (e.g. fired in the same synchronous loop or `Promise.all`).

1. First call: `inFlight` is `null`, so it proceeds, kicks off `fetch()`, and synchronously assigns the resulting promise to `inFlight` before returning it (auth.js:13, 16, 37).
2. Second call happens in that same tick: `inFlight` is now non-null, so line 13 short-circuits and returns the *same* promise — no second HTTP request is made.
3. Both callers now await the identical promise. When it resolves, both get the same new access token; when it rejects (e.g. the 401 case above), both see the same rejection.
4. Only after that promise settles does `.finally` clear `inFlight`, so a later, unrelated refresh cycle starts its own new request.

The important subtlety: **the "no refresh token" check on auth.js:14-15 is not inside the guarded region.** It runs before `inFlight` is ever set, so if two concurrent calls both hit that branch, they don't share one thrown error — each independently reads the store and throws its own error. It's harmless here since it's synchronous and cheap, but it means the collapsing guarantee only covers the actual network request, not this early bailout.

One more thing worth knowing if you're changing this: `refresh` is exported directly alongside `currentToken` (auth.js:40), so other code can call it outside the expiry check in `currentToken` — e.g. a fetch wrapper that sees a 401 on a *regular* API call (not the refresh endpoint) and wants to force a refresh-and-retry. That path isn't implemented in this file; whatever calls `currentToken()` for outbound requests would need its own 401-retry logic that calls `refresh()` on demand.


===== R35 | case: verdict-experiment =====
The methodology has **sound structure** but contains **critical flaws** in the statistical testing approach:

**Problems:**

1. **Multiple testing without correction** — Testing eight metrics and stopping at the first p < 0.05 inflates the false-positive rate far above 5%. With 8 independent tests at α=0.05 each, family-wise error rate is roughly 34%, not 5%. The team's claim is not justified.

2. **Sequential testing / daily peeking** — Checking the dashboard each morning and stopping at the first significance compounds the problem. This is "optional stopping," which inflates type I error even with a single metric. Daily peeks with α=0.05 per peek across four weeks can easily hit a false positive on noise alone.

3. **Unclear decision rule** — The plan says "any of the eight reaches significance in treatment's favour" counts as a win. This treats all eight metrics equally, but only `completed orders per session` is the goal; the others are guardrails. A revenue drop + order lift is not a win, but the current wording could read that way.

**What to add or change:**

- **Declare one primary metric** (`completed orders per session`). Stop the experiment only if it reaches significance, then verify guardrails have not moved against treatment by more than 2%.
- **Commit to a fixed duration** (four weeks is reasonable), *or* use a proper sequential testing design (e.g., spending α across planned interim analyses, not peeking every day).
- **Pre-specify sample size / power calculation** based on the minimum order-lift you'd consider shipping. 4,000 checkout starts/day for 28 days gives ~112k sessions total; whether that's enough depends on baseline conversion and effect size.
- **Acknowledge the trade-off on logged-out users** — results apply only to logged-in checkout, not the full funnel.

The design is otherwise solid: stable bucketing, server-side assignment, existing instrumentation, simple rollback.


===== R36 | case: verdict-rollout =====
Not sound — there's a critical flaw in the deploy/migration sequencing that will cause an outage, not just a rollback risk.

**The core problem:** the migration drops `full_name` in the same job that runs *before* any new-release instance starts. At the moment migration completes, all 12 instances are still running the *old* code, which reads/writes `full_name` in six places (serializers, search, welcome email, weekly report, signup, profile_update). That column no longer exists. Every one of those code paths starts erroring immediately — not during some edge-case rollback, but on the happy path, for the full ~6 minutes it takes the rolling deploy to cycle all 12 instances. At 4% of peak traffic that's real users hitting 500s on signup, profile reads, and profile updates.

**It also breaks rollback**, which the plan treats as a safety net: "if the new release misbehaves, roll back to the previous image." The previous image still reads/writes `full_name`. Rolling back the code doesn't reverse the migration, so post-rollback you'd have old code pointed at a schema that no longer has the column it needs — the outage continues, not resolves.

**Fix:** split this into an expand/contract sequence instead of one release:

1. **Release 1 (expand):** migration adds `given_name`/`family_name` and backfills them, but does *not* drop `full_name`. Deploy code that writes all three columns (dual-write) and reads from the new columns. Old code, if rolled back, still finds `full_name` intact and keeps working.
2. **Release 2 (contract), after the rollback window has safely passed:** a separate migration drops `full_name`, and code stops dual-writing it.

This costs an extra release, which the plan explicitly wanted to avoid ("doubles the coordination cost") — but the single-release version isn't actually cheaper, it's just broken during the rollout window and unsafe on rollback.

Two smaller notes, not blockers:
- The backfill splitting on first space is called out as an accepted limitation — fine as a product decision, just make sure Support is actually briefed before Tuesday, since they're the stated mitigation.
- Verification checks error rates and spot-checks 20 records but doesn't mention watching error rates specifically *during* the rollout window (the 6 minutes where the outage above would show up) — worth calling out explicitly once the sequencing is fixed.


===== R37 | case: walkthrough =====
Here's the complete flow:

## Normal Path (Happy Case)

1. **`currentToken()` is called** with the store
   - Retrieves the stored access token
   - Checks two things: does it exist AND does it have more than 30 seconds left (the SKEW_MS buffer)?
   - If yes to both, returns it immediately — no refresh needed
   - If no, calls `refresh()`

2. **`refresh()` makes the token request**
   - Fetches POST to `/oauth/token` with the refresh token
   - Server responds with new `access_token` and `expires_in`
   - Stores the new token with calculated expiry time: `Date.now() + expires_in * 1000`
   - May also store a new refresh token if the server sent one
   - Returns the fresh access token

## Concurrent Requests (Two+ calls at once)

This is where `inFlight` does the heavy lifting:

- **Request A** calls `currentToken()`, sees the token is stale, and calls `refresh()`
- `refresh()` starts the fetch and stores the Promise in the **`inFlight`** variable
- **Request B** calls `currentToken()` a few milliseconds later, also needs a refresh
- `refresh()` is called again, **but immediately sees `inFlight` is already set** (line 13)
- Instead of making a second fetch, Request B just returns the same Promise from Request A
- Both requests wait on the same network call and get the same new token
- When the fetch completes, `finally()` clears `inFlight` so the next batch of refreshes (after token expires again) can make a new network call

This prevents the thundering herd problem where 10 concurrent requests would each try to refresh independently.

## On 401 (Unauthorized)

- Server rejects the refresh token (it's expired, revoked, or invalid)
- `refresh()` **nukes the entire store** (`store.clear()`)
- Throws an error forcing the caller to re-authenticate
- The assumption: if refresh fails with 401, the user's session is dead and they need to log in again

## Timeline Example

```
t=0ms   Request A: currentToken() → token expired → refresh() starts fetch
        inFlight = Promise(...)
t=5ms   Request B: currentToken() → token expired → refresh() called
        → sees inFlight, returns Promise(...) [same one]
t=50ms  Fetch completes: new token stored, inFlight cleared
        → Both A and B get the new token
t=200ms Request C: currentToken() → token still valid (50 seconds left)
        → returns immediately, no network call
```

The critical invariant: **only one token refresh network call is ever in flight at a time**, but all waiting requests share the result.


===== R38 | case: verdict-experiment =====
The plan is well-structured but has a **critical statistical flaw** with multiple comparisons and optional stopping.

**Main issue:** The team is checking eight metrics daily and stopping at the first p < 0.05 (peeking each morning over ~28 days). This violates the assumptions behind the 5% false-positive rate claim in two ways:

1. **Multiple comparisons**: Eight metrics × daily checks = many opportunities to see p < 0.05 by chance. A Bonferroni correction would lower the significance threshold to p < 0.05/8 ≈ 0.006, or they need a different multiple-testing framework.

2. **Optional stopping bias**: Peeking daily and stopping at the first p < 0.05 inflates Type I error far above 5%. Sequential testing requires either a stopping rule (like Pocock's test) or a pre-commitment to e.g. two intermediate analyses with adjusted alpha levels.

**Secondary issues:**

- **Guardrail thresholds**: "moved against us by more than 2%" — is that relative or absolute? How is it tested? If also at p < 0.05, that's another multiple comparison.
- **Power**: No mention of expected effect size or statistical power. What lift do they need to detect, and can 2,000 sessions per bucket (per day × 28 days) detect it?
- **Session vs. user**: Assignment is per account, but the metric is per session. A user might have multiple sessions, adding variance.
- **Support tickets metric**: Manual coding introduces measurement error; weaker than automated events.

**Recommendation:** Add a **pre-registered stopping rule** (e.g., Pocock boundaries or fixed two looks with Bonferroni correction) and specify the minimum detectable effect size. Otherwise, the 5% false-positive rate claim is overstated.


===== R39 | case: verdict-rollout =====
No — there's a critical flaw: **the plan drops `full_name` in the same release that migrates the code, but deploys are rolling with a ~6-minute overlap window.**

The migration runs and drops `full_name` *before the first new instance starts*. For the following ~6 minutes, 9 of the 12 instances are still running the old release — the four read sites and two write sites that reference `full_name` — against a schema where that column no longer exists. Every signup, profile update, profile-fetch, support lookup, welcome email, and weekly report hitting an old instance during the rollout will error. "Lowest-traffic hour" and "not zero, every region" (line 57-58) means this is real user-facing breakage, not a theoretical edge case.

This also breaks the rollback plan (lines 60-63): rollback reverts the *code* image, but the migration already destructively dropped the column. Rolling back doesn't restore `full_name`, so if the new release misbehaves, rollback doesn't actually recover — the old code still has nothing to read or write.

**Fix: split into an expand/contract sequence instead of one release.**

1. **Release 1** — additive only: migration adds `given_name`/`family_name` and backfills them; `full_name` stays. Code changes to dual-write both old and new columns on signup/profile_update, and can read from `given_name`/`family_name`. Old code paths are unaffected since `full_name` still exists and is kept populated.
2. **Release 2** — after Release 1 has fully rolled out and baked: code stops referencing `full_name` anywhere (all four reads and two writes now only touch the new columns).
3. **Release 3** — migration drops `full_name`. Safe now, since no running instance (old or new) references it anymore.

Each step is independently rollback-safe, because no release ever depends on a schema element the previous release destroyed.

Secondary note: the backfill (2.4M rows) is bundled into the same migration as the `DROP COLUMN`, run synchronously before the first new instance starts. Worth confirming that update won't run long enough to blow past your deploy window or cause replication lag — batching the backfill is safer than a single full-table `UPDATE`.

The backfill-correctness tradeoff (splitting on first space) is fine as written — that's an explicit, reasoned decision, not a gap.


===== R40 | case: verdict-experiment =====
The methodology has one serious flaw and a couple of smaller gaps.

**Serious: the stopping rule invalidates the stated 5% false-positive rate.** Checking daily and stopping the instant any metric hits p < 0.05 is repeated significance testing — each daily look is a fresh chance to cross the threshold on noise. Over ~20 daily looks the actual false-positive rate is well above 5%, commonly 20-30%+. This compounds with checking 8 metrics each day (any one crossing counts as a win), so it's really ~160 implicit tests over the run, not one. Fix: either commit to a single fixed-horizon test (no peeking until the 4-week mark) or use a sequential method designed for repeated looks (alpha-spending / O'Brien-Fleming bounds, or "always-valid" p-values) so the interim checks don't inflate the error rate.

**Missing: no power analysis.** The doc gives expected volume (4,000 starts/day) but never states the minimum effect size the design can reliably detect in 4 weeks, or the sample size that requires. Without that, "4 weeks and no significance → keep control" could just mean the test was underpowered, not that the redesign doesn't work.

**Ambiguous: guardrail rule.** "Moved against us by more than 2%" isn't specified as a point-estimate threshold or a statistical test. On the small samples typical of an early stop (e.g., if the primary metric already hit significance by day 3), guardrail estimates will be noisy — worth defining whether this is a CI-based check or a raw threshold.

**Minor, worth a note but not necessarily a fix:** randomization is by account id but the metric is per-session, so a user with multiple checkout attempts contributes multiple correlated observations to one bucket — the z-test assumes independence. If repeat sessions per user are common this understates variance slightly.

Everything else — bucket stability, server-side assignment avoiding flicker, shared event-loss rate, rollback plan, logged-out/mobile-web exclusions being disclosed — is sound and clearly stated.


===== R41 | case: verdict-rollout =====
Not sound. The rolling deploy makes this migration unsafe in two ways:

**Rollback is broken, contradicting the doc's own claim.** The migration drops `full_name` before the new release starts (ROLLOUT.md:19-20, 37-39). If the new release misbehaves and the orchestrator rolls back to the previous image (ROLLOUT.md:60-63), that old code still reads/writes `full_name` in six places (`api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, `reports/weekly_active.py`, `api/signup.py`, `api/profile_update.py`) — a column that no longer exists. Every request touching users would start erroring immediately. "We have practised this and it takes about six minutes" is only true if the schema is compatible with the old code, which it won't be.

**The rolling window itself is exposed.** Deploys take ~6 minutes with old and new instances serving traffic simultaneously (ROLLOUT.md:13-17), but the migration runs before *any* new instance starts. So for up to 6 minutes, the still-running old-release instances hit `full_name`, which is already dropped. That's guaranteed breakage on every deploy of this change, not just a rollback contingency — worsened by, not mitigated by, doing it at low-traffic o'clock.

The stated reason for rejecting two releases — "doubles the coordination cost" — doesn't hold up against this: it's not a coordination nicety, it's what makes the change reversible and rollout-safe at all.

**Fix: standard expand/contract, two releases.**
- Release 1: add `given_name`/`family_name`, backfill, update the two write sites to dual-write both old and new columns, keep all four read sites on `full_name` (or switch reads to new columns with `full_name` still present as a safety net). Deploy fully. This release is safely rollback-able either way, since `full_name` still exists throughout.
- Release 2 (separate deploy, after Release 1 is fully soaked): switch remaining reads/writes fully to the new columns, then drop `full_name` in a later migration once you're confident you won't need to roll back past it.

The backfill-correctness tradeoff (split-on-first-space, corrected later) is fine as documented — that's a legitimate accepted limitation, not a soundness problem.


===== R42 | case: walkthrough =====
Nothing else in the repo calls this module — `auth.js` is self-contained, so the whole flow lives in these 41 lines. Here's how it works.

**Normal path — `currentToken(store)`**
1. Read the cached access token from `store`.
2. If it exists and has more than 30s (`SKEW_MS`) left before expiry, return its value directly — no network call.
3. Otherwise (missing or within 30s of expiring), call `refresh(store)`.

The 30s skew is a buffer so a token doesn't expire mid-flight between the check and its use.

**Refresh path — `refresh(store)`**
1. If a refresh is already in progress (`inFlight` is set), return that same promise instead of starting a new one — this is the concurrent-request collapsing.
2. Otherwise read the refresh token from `store`. If there isn't one, throw immediately (`no refresh token; re-auth required`) — no network call.
3. POST to `/oauth/token` with `grant_type: refresh_token`, and store the resulting promise in `inFlight` right away (before awaiting), so any refresh call that arrives while this is pending also sees `inFlight` set.
4. On response:
   - **401**: this means the *refresh token itself* was rejected (not the access token — this module never calls a resource API, only the token endpoint). It wipes `store` via `store.clear()` and throws `refresh rejected; re-auth required`. There's no automatic retry here — the caller must send the user back through login.
   - Any other non-ok status: throws `refresh failed: <status>`.
   - Success: parses the JSON body, writes the new access token (with a fresh `expiresAt`) into `store`, and — only if the server rotated it — writes a new refresh token too (rotation is optional, so the old refresh token is kept if the server doesn't send a new one).
5. `.finally()` resets `inFlight = null` regardless of outcome, so the *next* call to `refresh` (success or failure) starts a clean attempt rather than being stuck returning a rejected promise forever.

**Two requests refreshing at once**

Say request A and request B both call `currentToken` and both see an expired token.
- A calls `refresh`, `inFlight` is `null`, so A creates the fetch and assigns it to `inFlight`, then returns that promise.
- B calls `refresh` a moment later (still synchronous-ish, before the fetch resolves), sees `inFlight` already set, and just returns the *same* promise — B does not fire a second `/oauth/token` request.
- Both A and B resolve when the one real fetch completes, get the same `access_token` back, and `inFlight` clears via `.finally`.

This only works because `inFlight` is assigned synchronously before any `await` — there's no gap where a second caller could slip in and start a duplicate request. One subtlety worth knowing before you touch this: `inFlight` is a single module-level variable, so if this module is ever used with more than one `store` (e.g. multi-account), refreshes across different stores would incorrectly collapse into one.


===== R43 | case: verdict-experiment =====
The methodology has real problems — mostly around the stopping rule and multiplicity. Here's what I'd fix, most serious first.

**1. Optional stopping without correction inflates the false-positive rate far above 5%.** Checking a p-value every morning and stopping the first time it crosses 0.05 is repeated significance testing. With daily peeking over up to 28 days, the true Type I error rate for a single metric is well above 5% — the "5% false-positive rate" claim in the doc is only true for a single fixed-time look, not for a monitored sequence. Either commit to a single look at a pre-set sample size, or use a sequential method with proper alpha-spending (e.g., O'Brien-Fleming/group-sequential boundaries) that accounts for repeated looks.

**2. Multiplicity across the eight metrics compounds the problem.** "Win if any of the eight reaches significance" tests eight hypotheses per day, uncorrected. Combined with #1, you're effectively running dozens of tests and taking the best result. Apply a multiple-comparisons correction (Bonferroni/Benjamini-Hochberg) across the metric set, or designate one primary metric for the ship decision and treat the rest as strictly monitoring/guardrails that can only veto, not trigger, a ship.

**3. The stopping rule is asymmetric in a way that biases results.** You stop early on a win but require the full four weeks to declare a loss. That's optional stopping in one direction only, which both inflates false positives further and biases the estimated effect size upward (winner's curse) for whichever result ships. A sound design stops on the same rule regardless of direction, or pre-commits to a fixed duration either way.

**4. The metrics table and the decision rule contradict each other.** The table labels only "completed orders per session" as the metric of record, with drop-off metrics marked "diagnostic" — implying they're not decision-grade. But the decision rule says a win is triggered by *any* of the eight, diagnostics included. Pick one: diagnostics inform interpretation, they don't trigger shipping.

**5. Refund rate within 14 days can't be validly read on an early stop.** If the experiment stops on day 5 or 10, most orders placed near the end of the window haven't had 14 days to generate a refund yet — the metric is right-censored and will read artificially low. Either exclude this metric from any early-stop check and only evaluate it at a fixed date, or measure it on a cohort cutoff (only orders placed more than 14 days before the analysis date).

**6. No power analysis or minimum detectable effect.** ~4,000 starts/day, minus 8% logged-out, split 50/50 gives a rough per-bucket sample size, but nothing here says what effect size that can actually detect, especially for low-base-rate metrics like refund rate or checkout-tagged support tickets. Without this, "four weeks with no signal" doesn't tell you whether the redesign has no effect or whether the test was simply underpowered to see it.

**7. Same test (z-test) applied to metrics it doesn't fit.** A two-sample z-test is appropriate for the completion-rate metric of record, but "median checkout duration" isn't validly tested with a z-test on means (duration data is typically skewed; a median needs a different method, e.g. bootstrap or a rank test), and rare-event metrics (refund rate, tagged support tickets) may have counts too small early on for the normal approximation a z-test relies on.

**8. Instrumentation assumption isn't verified for the new design.** The plan assumes `shipping_completed` and `payment_completed` retain their meaning once the two steps are collapsed onto one page. Worth confirming these still fire as distinct, meaningfully-ordered events in the v2 flow rather than near-simultaneously — otherwise the two drop-off diagnostics become uninformative or misleading.

**9. No sample-ratio mismatch (SRM) check.** There's no mention of verifying the actual observed split stays ~50/50. An SRM check is a standard, cheap sanity test for broken randomization or differential logging, and its absence should be flagged.

Smaller point: excluding logged-out sessions (~8%) is a defensible scope call, not a methodology flaw, but should be stated as a limitation on generalizability of the result, not just a technical exclusion.

Nothing here needs to be *removed* — the guardrail set and rollback plan are reasonable — but I wouldn't ship a decision off this plan without fixing the stopping rule (1–3) at minimum.


===== R44 | case: verdict-schema =====
**Critical issue: use NUMERIC/DECIMAL for money, not DOUBLE PRECISION.**

Your ledger sums `DOUBLE PRECISION` amounts to compute balances (line 60). Floating-point accumulation will drift—you'll get 0.01 or 0.99 cent errors that compound and become audit nightmares. Every ledger system that uses float for money regrets it. Switch `amount` in `ledger_entries`, `monthly_price` in `plans`, and `total` in `invoices` to `NUMERIC(19,2)` (or whatever precision your currency needs).

**Secondary: be explicit about foreign key deletes.** If you delete an account, what happens to its subscriptions and ledger entries? Add `ON DELETE CASCADE` or `ON DELETE RESTRICT` to each foreign key so the behavior is clear and documented.

**Tertiary: invoices and ledger_entries aren't linked.** You write an invoice total at close (line 61), but there's no way to audit which ledger entries made up that total. Consider adding a ledger entry ID range, a line-items table, or a checksum so you can reconcile. This matters when disputes come up.

Everything else (status enum, subscription indexes, account/plan structure) looks solid. But fix the DOUBLE PRECISION before you start writing ledger code—changing it later means a migration that touches every financial record.


===== R45 | case: verdict-experiment =====
Not sound as written — the stopping rule is the critical flaw, plus a few smaller gaps.

**1. Daily peeking + first-significant-metric-wins invalidates the "5% false-positive rate" claim.** The plan checks a dashboard every morning for up to 4 weeks (~28 looks) across 8 metrics, and stops the moment *any* metric shows p<0.05. Each look and each extra metric is another chance for noise to cross the threshold, and repeated significance testing without a correction inflates the true false-positive rate to well above 5% — likely 50%+ depending on metric correlation. To actually get a 5% false-positive rate you need either a fixed single look at a pre-committed sample size, or a proper sequential design (alpha-spending / O'Brien-Fleming boundaries) plus a multiple-comparisons correction across the 8 metrics (e.g., Bonferroni, treating the metric of record separately from the guardrails).

**2. No sample-ratio-mismatch (SRM) check.** Nothing verifies the 50/50 split is actually holding in live data. A subtle bucketing bug (e.g., in `checkout/bucket.py`) can silently bias results, and this is the standard first guardrail in most experimentation frameworks — worth adding.

**3. The guardrail threshold ("moved against by more than 2%") isn't defined as statistical or raw.** Combined with daily peeking, an un-tested 2% swing is likely to trip on noise alone in the first few days when sample size per bucket is small. This should be a significance test too, not a bare percentage.

**4. The 14-day refund guardrail conflicts with early stopping.** If the experiment stops on day 3 because another metric hit p<0.05, the most recent cohorts haven't had 14 days to generate refunds — that guardrail will look artificially clean at exactly the moment you're relying on it most.

**5. Minor: uniform z-test across all 8 metrics is questionable.** Revenue per session is typically right-skewed (a two-sample z-test assumes a roughly normal sampling distribution of the mean, which needs either large samples or a transform), and "median checkout duration" isn't naturally tested with a z-test on means — that calls for a rank-based test or a test built for medians.

Everything else — hash-based stable bucketing, excluding logged-out sessions with the loss disclosed, the flag-based instant rollback, mobile-web out of scope — is clearly reasoned and fine as is.


===== R46 | case: verdict-rollout =====
The plan has a critical timing issue during the rolling deploy.

The migration drops `full_name` *before* the new release starts rolling out. But a rolling deploy means old instances keep serving traffic for ~6 minutes while new instances spin up. **Old code will crash trying to read/write `full_name` which no longer exists.** You'll see immediate errors during the deploy window, not the flat error rates you're expecting.

To fix this, either:

1. **Two-release approach** (safest, proven pattern): Release 1 adds the new columns, backfills, and updates code to read/write both (preferring the new columns). Keep `full_name`. Release 2 drops `full_name` after you've verified everything works. This doubles coordination but eliminates the deploy-window crash risk.

2. **Keep the old column during deploy**: Add new columns, backfill, update code to read/write new columns only—but don't drop `full_name` until after the rolling deploy finishes and old instances are gone. Then drop it in a follow-up migration. Simpler than option 1, still safe.

3. **Database view for backwards compatibility**: Create a view that synthesizes `full_name` from `given_name` and `family_name` so old code doesn't crash if somehow still running. Less common but technically possible.

Also note: if you roll back *after* the migration runs, your old instances will still crash looking for `full_name`. That's a gap in your rollback story.

The single-release simplicity isn't worth the deploy risk here. I'd go with option 2 as the minimum safe change: keep `full_name` until after the rolling deploy window closes.


===== R47 | case: verdict-rollout =====
Not sound as written. The critical problem: it's a single migration/release that both adds the new columns *and drops `full_name`*, but the rollout itself isn't atomic.

**The rolling deploy breaks it.** Deploys take ~6 minutes, and during that window old-release instances (still reading/writing `full_name` in `signup.py`, `profile_update.py`, and the four read sites) are serving live traffic alongside new-release instances. The migration drops `full_name` *before the first new instance starts*, which means for the full ~6 minutes, every old-release instance still in the pool is hitting a column that no longer exists. That's an outage window, not a low-risk deploy — happening at 4% traffic doesn't make it safe, it just makes it smaller.

**Rollback is also broken by the same fact.** "Roll back to the previous image" only works if the previous image's code still matches the schema. Once `full_name` is dropped, rollback puts old code in front of a schema it can't read — the rollback plan as described (roll instances back, ~6 minutes) doesn't actually recover a working state.

**Backfill timing gap.** Even setting aside the drop: the backfill runs once, at migration time, before any new-release code exists. Any signup or profile update handled by an old-release instance during the rollout window writes `full_name` only — those rows won't get `given_name`/`family_name` populated, since the code that would dual-write doesn't exist yet at that point.

**Fix: split into two releases (expand/contract), not one.**
- Release 1: migration adds `given_name`/`family_name` and backfills, but *keeps* `full_name`. New code dual-writes all three columns on signup/update; reads can switch to the new columns immediately since they're now populated. Old-release instances during rollout keep working unmodified — they still see `full_name`.
- Release 2 (separate deploy, after Release 1 is fully rolled out and verified): stop writing `full_name`, then drop it in its own migration.

Everything else in the plan is fine — the backfill's first-space-split limitation is a reasonable accepted tradeoff, and the timing/verification sections are sensible. It's specifically the single-release expand+contract that needs to change.


===== R48 | case: verdict-schema =====
No — the money columns will bite you. `amount`, `monthly_price`, and `total` are all `DOUBLE PRECISION`. The comment at the bottom explicitly defines balance as `SELECT sum(amount)` — a running sum of binary floats will drift from the true decimal total as entries accumulate, and that's the one property a ledger can't compromise on. Switch these to `NUMERIC(19,4)` (or similar fixed-precision type) before anything else.

Three more worth fixing while you're in there:

1. **No idempotency key on `ledger_entries`.** If entries get created from webhook/retry-prone code paths (payment processor callbacks, retried jobs), nothing stops a duplicate charge from landing twice. Add a unique constraint on something like `(source, external_id)` or an `idempotency_key` column.
2. **The balance sum is currency-blind.** `sum(amount) WHERE account_id = $1` mixes currencies if an account ever has entries in more than one. Either constrain one currency per account, or make the documented balance query `GROUP BY currency`.
3. **Nothing enforces ledger immutability.** It's an audit trail in spirit ("every charge, refund and credit lands here") but the table permits ordinary `UPDATE`/`DELETE`. Worth a `REVOKE UPDATE, DELETE` for the app role, or a trigger, so corrections have to go through new offsetting entries instead of edits.

Everything else — indexes, FKs, the `status`/`entry_type` CHECK constraints — looks reasonable for this stage.


===== R49 | case: verdict-experiment =====
Not sound as written — the decision rule has a statistical flaw that undermines the whole experiment.

**Core problem: uncorrected peeking + multiple comparisons stack multiplicatively.**
- Checking a p-value every morning and stopping the first time it crosses 0.05 is optional stopping. With repeated looks, the true false-positive rate is much higher than 5% — the more days you check, the more chances random noise gets to cross the line even with no real effect.
- On top of that, the rule triggers on *any of eight* metrics, not one. Even with a single look, testing 8 metrics independently gives roughly a 1-(0.95)^8 ≈ 34% chance of a false positive somewhere, not 5%.
- Combined (8 metrics × up to 28 daily looks), the real false-positive rate is far north of the "5%" the doc claims, likely irrelevant of what the true effect is. The stated 5% is the nominal per-test rate, not the operating characteristic of this procedure.

**Secondary issues:**
- No power calculation or pre-registered minimum sample size/duration. At ~4,000 starts/day split 50/50, there's no stated minimum detectable effect, so there's no way to know if 4 weeks is even enough to detect a real lift, or conversely whether an early "win" is trustworthy.
- Stopping on a diagnostic metric alone (e.g. shipping-step drop-off improving) without requiring the metric of record (order_placed/checkout_started) to also move is risky — you could ship on a funnel-shape change that isn't actually more completed orders.
- No day-of-week guard: daily stopping means the experiment could end mid-week and never see a weekend, if checkout behavior differs by day.
- No sample-ratio mismatch (SRM) check mentioned — worth verifying the assignment hash actually lands ~50/50 in practice, since a bug there silently invalidates everything else.

**Fix, in one line:** pick a fixed sample size/duration up front (via a power calc on the primary metric), only evaluate significance once at that endpoint (or use a proper sequential-testing correction like alpha-spending if you want early stopping), and apply a multiple-comparisons correction across the 8 metrics.

Everything else — the bucketing/hashing approach, instrumentation reuse, guardrail list, rollback plan, mobile-web exclusion — is reasonable.


===== R50 | case: verdict-rollout =====
The plan has a **critical race condition** during the migration window.

Here's the problem: migrations run before the new code starts rolling out, but the old code instances keep serving traffic **during** the migration. So the sequence is:

1. Migration drops `full_name`
2. First instance of new code starts
3. Old instances are still running, still trying to write to `full_name`
4. Those writes hit a "column not found" error, causing silent failures or exceptions

Even worse: writes that succeed before the migration completes get lost when the column is dropped.

**The fix:** You need a **two-release approach** to avoid downtime, or a **brief traffic drain** before the migration:

**Option A (two releases, recommended):**
- **Release 1:** Deploy code that reads both columns and writes to *both* `full_name` and the new columns. Let it roll fully and stabilize.
- **Run the migration** to drop `full_name`
- **Release 2:** Deploy code that only touches the new columns

**Option B (one release, requires downtime):**
- Stop traffic (or drain connections) on all instances
- Run the migration
- Deploy the new code and start instances

The plan as written will either error or lose data during the migration window. The current verification step (spot-checking 20 records after deploy) won't catch writes that failed during the migration on old instances.


===== R51 | case: verdict-rollout =====
The plan has a **critical rollback gap** and several data-safety concerns worth addressing.

**The main problem:** If something goes wrong and you roll back the code, the database schema change (dropping `full_name`) remains. Old code hitting a missing column will fail with 500 errors anyway. The rollback procedure as written doesn't actually work for a schema change.

**Other risks:**

1. **Concurrent writes during backfill:** The migration runs before new code deploys, but writes to `full_name` can still happen during the backfill itself (sign-ups, profile updates from old instances). Those writes either fail silently or overwrite the backfilled data. There's no mention of how to handle this window.

2. **Insufficient verification for 2.4M rows:** Spot-checking 20 records catches obvious corruption but misses systematic issues (encoding problems, regional patterns, specific name formats). For this scale, you'd want:
   - Pre-migration validation of the backfill logic on the production data snapshot
   - A broader sample check (hundreds, not 20)
   - Automated checks for the known-bad cases (mononyms, particles)

3. **No staged migration strategy:** There's no mention of testing the backfill on a production-scale copy first. A data migration this size benefits from running it offline on a replica to catch issues before the actual deployment.

4. **Missing database rollback:** If code rolls back, you'll need a restore from backup, not just an orchestrator revert. The plan should document this explicitly.

**What I'd change:**

- Add a **read-only backfill validation step** on a staging database before Tuesday
- **Quiesce writes** during the actual backfill (even at 4% traffic, coordinating this is safer than racing writes)
- Document the **actual rollback** (database restore from backup, not just code revert)
- Expand verification to **hundreds of records** and include automated checks for known edge cases

The single-release approach is reasonable given the simplicity, but the execution needs tighter guards around data safety during the migration window itself.


===== R52 | case: verdict-schema =====
Three issues jump out before you build the ledger on this:

1. **DOUBLE PRECISION for money is a bug waiting to happen.** `monthly_price` (line 16), `amount` (line 38), and `total` (line 51) should all be `NUMERIC(19, 4)` or similar, not `DOUBLE PRECISION`. Financial calculations with floats accumulate rounding errors—you'll get balance mismatches over time. This gets worse the more entries you have.

2. **Missing idempotency key on ledger_entries.** Add something like `external_id TEXT UNIQUE` so you can safely retry charge requests without creating duplicates. Critical for a billing system.

3. **No constraint on invoice period_end.** Add `CHECK (period_end >= period_start)` to catch bad data at the database level rather than in application code.

Minor: The nullable `subscription_id` on ledger_entries is fine for adjustments, but be explicit in docs about when it's null vs. required.

The schema is otherwise solid for a ledger—good indexing on (account_id, occurred_at) and status, proper foreign keys, immutable timestamps. Fix those three and you're ready.


===== R53 | case: verdict-schema =====
Three issues before ledger work starts:

**Critical: DOUBLE PRECISION for money.** Lines 16, 38, 51 use floating-point types. This fails for billing — rounding errors accumulate. Switch to `NUMERIC(19,2)` (or `NUMERIC(12,2)` if you don't need 10-digit integers).

**Missing running balance in ledger.** Line 60 shows the query pattern, but computing `sum(amount)` every time is wasteful. Add a `balance NUMERIC(19,2)` column to `ledger_entries` and maintain it on insert. Makes historical balance queries O(1) instead of O(n).

**No immutability on ledger entries.** A ledger record should never change once written. Add a trigger to prevent UPDATE/DELETE on `ledger_entries`, or document this as a hard rule enforced at the application layer. If corrections are needed, append an offsetting entry (negative charge or credit).

**Weak:** No link from invoices back to ledger entries. If you need to answer "which ledger entries are in this invoice?", add `ledger_entry_ids` (array or junction table) to invoices, or add an `invoice_id` foreign key to ledger.

**Nice to have:** ENUMs for status/entry_type instead of string checks; reference tables for `country` and `currency` to validate them.

The structure holds up, but the money columns need fixing before you start recording real charges.


===== R54 | case: walkthrough =====
Here's the token refresh flow:

## Normal path (token valid)

When `currentToken()` is called, it checks the stored access token. If it exists and expires more than 30 seconds from now (the 30-second skew), it returns that token immediately—no refresh needed. This is the fast path for most requests.

## Expired or missing token

If the token doesn't exist, has expired, or is within 30 seconds of expiring, `currentToken()` calls `refresh()`.

## The refresh call

`refresh()` makes a POST to `/oauth/token` with the refresh token. Two things happen in parallel during this:

**If there's already a refresh in flight:** The `inFlight` variable stores a promise. When a second request comes in and sees `inFlight` is not null, it returns that same promise instead of starting a new fetch. Both requests wait on the one network call and receive the same new access token. This collapses concurrent refresh attempts into a single request to the server.

**If no refresh is in flight:** It starts a new fetch and stores the promise in `inFlight` so any concurrent requests can find it.

## After the response

The `.then()` handler processes the response:

- **401 response:** The store is cleared entirely (both access and refresh tokens), and an error is thrown. This signals the user needs to re-authenticate because the refresh token itself was rejected.
- **Non-200 response:** An error is thrown with the HTTP status, but the store is *not* cleared. This is a transient server error, not an auth failure.
- **200 response:** The new access token and expiry are stored. If the server sent a new refresh token (rotating refresh tokens), that's stored too. The new access token value is returned.

## Finally block

Once the promise settles (success or error), `inFlight` is set back to null. The next `refresh()` call can start a new refresh cycle.

The key insight: **`inFlight` is the concurrency control.** If requests 1, 2, and 3 all hit the refresh path within milliseconds, only request 1 hits the network; requests 2 and 3 wait on request 1's promise.


===== R55 | case: walkthrough =====
Here's the flow, all in this one file (nothing else in the repo calls it yet):

**Normal path — `currentToken(store)`** (line 6-10)
Reads the cached access token. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, it's returned as-is. Otherwise it calls `refresh(store)` and returns whatever that resolves to. The 30s skew means refresh happens *before* actual expiry, not after.

**`refresh(store)`** (line 12-38)
1. If a refresh is already in flight (module-level `inFlight` variable), return that same promise instead of starting a new one — this is the dedup for concurrent callers (more below).
2. Otherwise, read the refresh token from the store. No refresh token means an immediate throw: `'no refresh token; re-auth required'`.
3. POST to `/oauth/token` with the refresh token, and store the resulting promise in `inFlight` *before* awaiting it — that's what lets concurrent callers see it.
4. `.finally()` clears `inFlight` back to `null` once the request settles, success or failure.

**On a 401** — this only applies to the `/oauth/token` refresh call itself, not to a general API request:
- `store.clear()` wipes both tokens, then throws `'refresh rejected; re-auth required'`. Any other non-ok status throws a generic `'refresh failed: ' + status` *without* clearing the store — so a 500 leaves tokens in place for a retry, but a 401 assumes the refresh token itself is dead and nukes everything.
- Note: there's no wrapper here for "make an API request, get a 401 back, call refresh and retry the request." `auth.js` only ever supplies a token; whatever calls it externally would need to own that retry loop itself. Worth confirming whether that logic exists elsewhere before you touch this.

**Two requests refreshing at once**
Say two callers both call `currentToken` when the token's expired. Both see no valid token, both call `refresh`. The first sets `inFlight` to the fetch promise. If the second call happens before that promise settles, `if (inFlight) return inFlight` hands it the exact same promise — so only one network call to `/oauth/token` ever goes out, and both callers resolve/reject together off the same result. The `.finally` reset means the *next* refresh cycle (after this one completes) starts clean.

One thing to watch if you're changing this: the dedup is keyed on a single module-level `inFlight`, not per-store — if this module is ever used with multiple stores/sessions in the same process, refreshes across different users would collapse into each other.


===== R56 | case: walkthrough =====
No other file calls into `auth.js` — it's self-contained, not yet wired into a request pipeline. Here's the flow as written:

**Normal path — `currentToken(store)`**
1. Reads the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, returns it directly — no network call.
3. Otherwise (missing or within 30s of expiry), calls `refresh(store)` and returns whatever that resolves to.

**`refresh(store)`**
1. If a refresh is already in flight (`inFlight` is set), returns that same promise instead of starting a new one — this is the concurrency collapse.
2. Otherwise reads the refresh token from `store`; if there isn't one, throws immediately (`no refresh token; re-auth required`).
3. Kicks off `POST /oauth/token` with `grant_type: refresh_token`, and immediately stores the resulting promise in `inFlight` (synchronously, before any `await`) so any call that arrives before the fetch settles sees it and joins in.
4. On response:
   - `401` → clears the whole store (wipes both access and refresh tokens) and throws `refresh rejected; re-auth required`. This is the only 401 handling in the file — it's the refresh endpoint rejecting the refresh token, not a 401 from a regular API call.
   - any other non-OK status → throws `refresh failed: <status>`.
   - success → writes the new access token (`value` + computed `expiresAt`) into the store, and conditionally rotates the refresh token if the server sent a new one.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the next call after this settles will start a fresh refresh.
6. Returns the new `access_token` string.

**Two requests refreshing at once**

Both call `currentToken`, both see the token as expired/near-expiry, both call `refresh`. The first call finds `inFlight` null, starts the fetch, and synchronously assigns the promise to `inFlight` before returning. Because `refresh` is `async`, the `if (inFlight)` check and the assignment both happen in the same synchronous tick relative to any other call that hasn't yet reached that line — so as long as the second call's `refresh()` invocation happens after the first has assigned `inFlight` (which it will, since JS is single-threaded and the assignment happens synchronously before the `fetch` promise's `.then` chain does anything), the second call sees the already-set `inFlight` and just returns that same promise. Both callers end up awaiting the identical in-flight request, so only one network call happens and both resolve to the same new token.

**A gap worth knowing before you touch this**: there's no retry-after-refresh loop anywhere — nothing here catches a 401 from an actual API call and retries it with a fresh token. This module only refreshes proactively (based on `expiresAt`) or reactively when the *refresh call itself* gets a 401. If some other request wrapper is meant to call `currentToken`, get a 401 anyway (e.g., clock skew, server-side revocation), and retry once — that logic doesn't exist yet, at least not in this file.


===== R57 | case: verdict-experiment =====
The plan is mostly sound but has **three statistical issues** that inflate the false-positive risk well above the claimed 5%:

1. **Multiple comparisons**: Testing eight metrics means the true false-positive rate is roughly 1-(0.95^8) ≈ 34%, not 5%. The 5% only applies if testing a single metric. Options to fix:
   - Apply Bonferroni correction (use p < 0.006 instead of 0.05)
   - Designate *one* primary metric (`completed orders per session`) and only stop on that; use the eight others as guards against harm
   - Pre-specify false-discovery rate control

2. **Daily peeking**: Checking every morning and stopping at first p < 0.05 is optional stopping, which compounds the multiple-comparisons problem. Sequential testing needs either pre-computed stopping boundaries (Pocock/O'Brien-Fleming) or a fixed check schedule (e.g., only at 2 weeks and 4 weeks).

3. **Missing power justification**: No mention of minimum detectable effect size or sample-size math. Do 4,000 daily starts over four weeks give enough power for the effect size you expect?

**Minor clarity issues:**
- "Guardrail has moved against us by more than 2%" needs precise direction and units (absolute vs relative change?)
- `shipping-step drop-off` should probably be a guardrail, not diagnostic—a significant increase would indicate the redesign made things worse

**What's good:** stable assignment, server-side bucketing, existing instrumentation, easy rollback, clear duration, and real-world metrics.


===== R58 | case: verdict-rollout =====
The plan has a **critical timing issue**. During the rolling deploy, old instances (still running the previous code) and new instances (running the new code) both serve traffic simultaneously. The migration runs before the first new instance starts, which means `full_name` is already dropped when the old instances are still live and trying to read it.

Old code hitting a missing column will fail hard—500 errors on every profile endpoint and user lookup for those requests routed to old instances. This defeats the rollback safety net, since by the time you notice the errors, you're already running with mixed generations.

**Fix: two-phase migration**

Phase 1 (release N): Migration adds `given_name` and `family_name`, backfills from `full_name`, but keeps `full_name` intact. Code updates all six call sites to read the new columns (or both, for safety). Old code can stay as-is since the old column still exists.

Phase 2 (release N+1, or later): Drop `full_name` after you're confident the old code is fully retired.

This decouples the schema change from the code rollout, so old and new instances can coexist safely. The one-release coordination you're trying to avoid is necessary here—the alternative is errors during deploy.

Alternatively, if you want to keep one release: migrate in the **last step of the deploy** (after all old instances are drained), not before. But that requires you to trust the orchestrator's health checks and have no lingering instances, which is riskier than the two-phase approach.


===== R59 | case: verdict-schema =====
No — the money type and the missing invoice-to-ledger link will bite you.

**Fix before building on it:**

1. **`DOUBLE PRECISION` for all money columns** (`plans.monthly_price`, `ledger_entries.amount`, `invoices.total`) — floating point can't represent currency exactly. `sum(amount)` for a balance will drift and stop matching what was charged. Use `NUMERIC(12,2)` (or integer cents).

2. **No link from `ledger_entries` to `invoices`.** The comment says invoice totals are "the sum of the period's entries," but that's only inferred from `account_id` + `occurred_at` between `period_start`/`period_end` — there's no `invoice_id` on `ledger_entries`. A refund posted after close, or any late-arriving entry, silently changes what a recompute would give vs. what's stored in `invoices.total`, with no way to tell which entries were actually invoiced. Add `invoice_id BIGINT REFERENCES invoices(id)` (nullable until invoiced) so entries get locked to an invoice.

3. **No idempotency key on `ledger_entries`.** A retried charge (webhook replay, network retry) has nothing to prevent a duplicate row. Ledgers need a unique external reference (e.g. `UNIQUE(idempotency_key)` or `UNIQUE(account_id, source_event_id)`).

4. **No currency consistency guarantee.** `ledger_entries.currency` is per-row and independent of the account; `accounts` itself has no currency. `SELECT sum(amount) FROM ledger_entries WHERE account_id = $1` (the documented balance query) is wrong the moment one account has entries in two currencies — nothing stops that.

5. **No constraint tying `entry_type` to the sign of `amount`.** Whether a refund is a negative `charge`-style amount or a positive amount that's subtracted elsewhere isn't encoded anywhere, so a bad insert (right type, wrong sign) corrupts the balance with no error.

6. **No append-only enforcement.** For a ledger, `UPDATE`/`DELETE` on `ledger_entries` should be impossible (or at least logged), otherwise "balance is the running sum" isn't trustworthy. Worth a trigger or revoked privileges, not just a comment.

Smaller, non-blocking: `invoices` has no `UNIQUE(account_id, period_start, period_end)` to prevent double-invoicing a period, and no check that `period_end > period_start`.

Of these, #1, #2, and #3 are the ones I'd fix before writing ledger code against this — the rest can be patched later without a data migration headache, those three can't.


===== R60 | case: walkthrough =====
Here's the complete flow:

## Normal path (token still valid)

`currentToken()` checks if the stored access token exists and won't expire in the next 30 seconds (the `SKEW_MS` buffer). If it's good, return it immediately.

## Token expired or missing

If expired or missing, call `refresh()`. This is where the concurrency handling kicks in.

## Concurrent refresh collapse (the clever part)

The `inFlight` variable is a module-level Promise. When `refresh()` is called:

1. **First request**: `inFlight` is null, so we make the network call and assign the Promise to `inFlight`
2. **Second request (arrives before first completes)**: `inFlight` is already set, so we return that same Promise instead of making another call
3. Both requests wait for the single network response

This means if RequestA and RequestB both need a token simultaneously, they share one `/oauth/token` call instead of making two.

## On 401 (refresh token invalid)

The server rejects the refresh attempt (token revoked, etc.). The code:
1. Clears the entire store (nukes both access and refresh tokens)
2. Throws an error signaling re-authentication is required
3. Still clears `inFlight` in the finally block so the next `currentToken()` call can attempt a fresh re-auth flow

## On other errors (5xx, network failure)

Throws the error. `inFlight` is still cleared in finally, so the next call will retry.

## On success

Stores the new access token with its expiry time (calculated as now + expires_in seconds). If the server sent a new refresh token, stores that too. Returns the token value. The finally block clears `inFlight`, allowing subsequent refreshes to proceed normally.

The 30-second skew buffer is intentional—it prevents you from using a token that's about to expire mid-request.
