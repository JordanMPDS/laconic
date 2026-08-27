

===== S01 | case: verdict-experiment =====
The methodology has solid bones but has **two significant statistical issues** that inflate the false-positive rate beyond the stated 5%:

**Critical issues:**

1. **Multiple comparisons problem**: Eight metrics + daily peeking without correction means the actual Type I error rate is much higher than 5%. Even under the null hypothesis, the probability of at least one false positive across 8 independent tests at α=0.05 is ~34%. The plan either needs Bonferroni correction (divide α by 8) or a proper sequential testing design; as written, the "5% false-positive rate" claim doesn't hold.

2. **Optional stopping without adjustment**: Daily checks naturally inflate Type I error. If they're serious about 5%, they need either a pre-specified group sequential design (with spending function) or to acknowledge the actual error rate and adjust α accordingly.

**Secondary issues:**

3. **Guardrail threshold ambiguous**: "No guardrail has moved against us by more than 2%" — is that 2 percentage points or 2% relative? And does a guardrail violation automatically disqualify a win, or just trigger manual review?

4. **No power analysis**: They mention ~2,000 sessions per bucket per day, but what effect size is this powered to detect? What's the baseline conversion? This should be explicit.

5. **Potential confounds**: Event loss is noted as symmetric, but what if the redesign changes how frequently events fire (JS errors, async issues)? Logged-out sessions are excluded, but no discussion of other segment-specific impacts.

**Should add:**
- Multiple comparisons correction (Bonferroni minimum, or sequential testing methodology)
- Explicit power calculation and minimum detectable effect
- Clear definition of guardrail thresholds and their relationship to the decision rule

**Should remove or clarify:**
- The "5% false-positive rate" claim as currently stated

Otherwise the plan is well-structured: clear goal, stable assignment, good guardrail metrics, tested rollback, and reasonable scope boundaries.


===== S02 | case: verdict-experiment =====
No — the stopping rule is the core problem, and it undermines the stated false-positive rate.

**Add / fix:**

1. **Peeking inflates the false-positive rate far past 5%.** Checking a two-sample z-test every morning and stopping the instant p<0.05 is repeated significance testing — each daily look is a fresh chance to false-positive. Over 4 weeks that's ~28 looks; the true false-positive rate is well above the claimed 5% (could be 20-30%+ depending on correlation between days). Either use a sequential method with proper alpha-spending (e.g., O'Brien-Fleming, or a Bayesian/mSPRT approach designed for continuous monitoring), or commit to a fixed sample size / fixed horizon and only look once.

2. **Multiple comparisons across 8 metrics compound #1.** "Win if any of the eight metrics hits p<0.05" tested daily is roughly 8 × 28 = 224 implicit tests, not one. No correction (Bonferroni, Benjamini-Hochberg, etc.) is applied. Combined with the peeking issue, the actual chance of a spurious "win" over 4 weeks is very high.

3. **Guardrail/diagnostic metrics shouldn't be alternative win triggers.** The metric of record is completed orders per session; the other seven (revenue, duration, error rate, drop-off, tickets, refunds) are described as guardrails/diagnostics — but the decision rule lets *any* of them independently trigger shipping. That conflates "don't ship if this got worse" with "ship if this got better," which isn't what a guardrail is for. Only the metric of record should trigger a win; the guardrails should only be able to veto.

4. **No power analysis / minimum detectable effect.** ~2,000 checkout starts/bucket/day, up to 56,000/bucket over 4 weeks — there's no stated MDE or power calculation to say whether that's enough to detect the lift you actually care about. Without it you can't tell if a null result after 4 weeks means "no effect" or "underpowered."

5. **No sample-ratio-mismatch (SRM) check.** Nothing here verifies the realized split stays ~50/50; a bucketing bug (e.g., differential exclusion by bucket) would silently bias results and this design wouldn't catch it.

6. **Day-1 evaluation risks novelty/day-of-week confounds.** Allowing a stop on the very first morning means a single good day (weekend pattern, promo, etc.) can end the experiment. Common practice is a minimum runtime (e.g., at least one full week, ideally in multiples of 7 days) before any stopping decision is evaluated.

**Sound as-is:** instrumentation reuse (no new events, symmetric 0.3% loss), the rollback/flag plan, and the disclosed logged-out exclusion are all fine.


===== S03 | case: walkthrough =====
auth.js is the entire project — it's a standalone module, not wired into any caller yet. Here's the flow as written:

**Normal path (`currentToken`)**
- `currentToken(store)` reads the cached access token from `store.get('access')`.
- If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, it's returned as-is — no network call.
- Otherwise (missing or within 30s of expiry) it falls through to `refresh(store)`. Note the 30s skew means refresh happens *before* actual expiry, not after — this module never reacts to a live 401 from a real API call, since there's no wrapper here that catches one and retries. Whatever calls `currentToken` is expected to check expiry proactively.

**Refresh (`refresh`)**
- Reads the refresh token from the store. If there isn't one, throws immediately — no network call, caller must re-auth.
- Otherwise POSTs to `/oauth/token` with `grant_type: refresh_token`.
- On the response: a `401` means the refresh token itself was rejected — the store is cleared entirely (both tokens gone) and it throws `'refresh rejected; re-auth required'`. Any other non-ok status throws `'refresh failed: ' + status` but leaves the store untouched (so a transient 5xx doesn't nuke a still-possibly-valid refresh token).
- On success, it stores the new access token with a computed `expiresAt`, and updates the refresh token too, but only `if (body.refresh_token)` is present — so if the server doesn't rotate it, the old refresh token stays valid and in place.

**Two requests refreshing at once**
- This is the `inFlight` module-level variable. `refresh()` checks it first: if a refresh is already in progress, every caller just returns the same pending promise instead of firing a second `/oauth/token` request.
- The `.finally(() => { inFlight = null })` resets it once the request settles (success or failure), so the next call after that starts a fresh refresh.
- Concretely: if two requests call `currentToken` while the token is expired, both call `refresh`. The first sets `inFlight` and starts the fetch. The second sees `inFlight` already set and returns that same promise — so both callers get the same token (or the same rejection) from one network round trip, and the store is only written once.
- One thing worth knowing before you touch this: `inFlight` is a plain module-level variable, not per-store. If this module is ever used with more than one `store` (e.g. multi-account/multi-tenant), concurrent refreshes for *different* stores would collapse into each other incorrectly — the second store's caller would get the first store's token. Right now there's only one call site conceptually assumed, so it's fine, but it's the sharp edge to know about if your change adds multiple stores or instances.


===== S04 | case: walkthrough =====
`auth.js` is a single self-contained module (no other file in the repo imports it) with three moving parts: a module-level `inFlight` promise, `currentToken()`, and `refresh()`.

**Entry point — `currentToken(store)` (auth.js:6-10)**
Reads the cached access token from `store`. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, it returns the value immediately — no network call. Otherwise it delegates to `refresh(store)`. The 30s skew means a token isn't used right up to the wire; anything refreshing within 30s of expiry is treated as already expired.

**Refreshing — `refresh(store)` (auth.js:12-38)**
1. If `inFlight` is already set, it returns that existing promise instead of starting a new request (auth.js:13) — this is the concurrency guard, more below.
2. Otherwise it reads the refresh token from `store`. If there isn't one, it throws immediately (`'no refresh token; re-auth required'`) — no network call happens in this case.
3. It POSTs to `/oauth/token` with the refresh token, and assigns the resulting promise chain to `inFlight` *before* anything is awaited.
4. On response:
   - **401** — treated as "the refresh token itself is dead." `store.clear()` wipes *both* the access and refresh tokens, and it throws `'refresh rejected; re-auth required'`. This is the only 401 handling in this file — it's specific to the token endpoint, not a general "any API call got 401, go refresh" wrapper (there isn't one here).
   - Any other non-OK status throws a generic `'refresh failed: <status>'`.
   - On success, it stores the new access token with a freshly computed `expiresAt`, and updates the refresh token too if the server rotated it (`body.refresh_token` present).
5. `.finally()` resets `inFlight = null` regardless of outcome, so the next call to `refresh()` starts a fresh attempt.

**Two requests refreshing at once**
Because `refresh()` has no `await` before the `inFlight = fetch(...)` assignment, that assignment happens synchronously within the same tick the function is invoked. So:
- Request A calls `currentToken` → sees an expired token → calls `refresh()`. `inFlight` is `null`, so A starts the fetch and sets `inFlight` synchronously.
- Request B calls `currentToken` shortly after (same or next tick) → also sees an expired token → calls `refresh()`. This time `inFlight` is already set, so B just returns that same promise — no second HTTP call is made.
- Both A and B resolve off the single `/oauth/token` round trip. Once it resolves, `.then` writes the new token to `store`, then `.finally` clears `inFlight`. Order matters here: the store is updated *before* `inFlight` is cleared, so there's no window where a third caller could see `inFlight == null` but a stale token in `store`.

**One thing worth flagging before you change it:** `inFlight` is a single module-level variable, not scoped per `store`. If `currentToken`/`refresh` is ever called concurrently with two different `store` instances (e.g. multi-account), the second store's refresh would incorrectly collapse into the first's in-flight promise and get the wrong account's token. Not an issue today since nothing in this repo calls it with more than one store, but it's a sharp edge if that assumption changes.


===== S05 | case: walkthrough =====
Here's the complete flow:

## Normal path (valid token exists)
`currentToken()` checks if the stored access token will still be valid 30 seconds from now (`SKEW_MS`). If yes, returns it immediately. If no, calls `refresh()`.

## Refresh flow (token expired or missing)

**First refresh request:** `inFlight` is null, so it proceeds:
- Grabs the stored refresh token (errors if missing — signals need for re-auth)
- Makes a POST to `/oauth/token` with `grant_type: 'refresh_token'`
- Sets `inFlight` to the fetch promise so other callers can see it

**Concurrent refresh requests while one is in flight:** The `if (inFlight) return inFlight` check collapses all concurrent refresh attempts into a single HTTP request. Every caller gets the same promise and waits for the same result.

## Response handling

- **401 response:** Token was rejected (credentials invalid). Clears all stored tokens and throws "refresh rejected; re-auth required". Any caller waiting on that promise also gets the error.
- **Other non-2xx:** Throws "refresh failed: [status]". Stored tokens are untouched — the error bubbles up.
- **2xx success:** Parses the response, stores the new access token with expiration time calculated as `now + expires_in`. If the response includes a new refresh token, stores that too. Returns the access token value.

## Cleanup
The `finally` block sets `inFlight = null` after the response handling completes, regardless of success or failure. This unblocks the next refresh attempt if another request comes in later.

## Key safety property
The `inFlight` promise ensures that if 10 requests hit `refresh()` simultaneously, only one HTTP request goes out. All 10 callers either all succeed together and get the same token, or all fail together with the same error. There's no race condition where some get a new token and others stale.

What aspect do you need to change?


===== S06 | case: walkthrough =====
Read the whole file — it's short (41 lines), so here's the full flow with line references.

## The proactive path (`currentToken`, auth.js:6-10)

Every outbound request is supposed to call `currentToken(store)` first. It reads the cached access token and checks its expiry against `Date.now() + SKEW_MS` (30s buffer, line 2). If the token is still valid outside that skew window, it returns `t.value` directly — no network call. If the token is missing or within 30s of expiring, it defers to `refresh(store)` (line 9).

Note this is **proactive, not reactive**: the module never inspects a 401 from an actual API request. It only ever avoids sending a stale token by checking expiry ahead of time. If something outside this file calls a resource endpoint and gets a 401 (token revoked server-side, clock drift, etc.), nothing in `auth.js` catches that — the caller would need its own 401 handler that calls `refresh(store)` and retries. That's a gap worth knowing about before you change anything here.

## `refresh` and the 401 it does handle (auth.js:12-38)

This is about the 401 the refresh *endpoint itself* can return, not a 401 from some other API call:

1. Line 13: if `inFlight` is already set, return it immediately — this is the concurrency guard, covered below.
2. Line 14-15: reads the refresh token from the store; if there isn't one, throws synchronously right away, before touching the network or setting `inFlight`.
3. Line 16-19: POSTs to `/oauth/token` and immediately assigns the resulting promise chain to `inFlight` (line 16), synchronously, before any `await` happens.
4. In the `.then` handler (line 20-33):
   - **401** (line 21-24): the refresh token itself was rejected. `store.clear()` wipes stored tokens and it throws `'refresh rejected; re-auth required'` — this is the "your session is dead, log in again" case.
   - **other non-2xx** (line 25): throws `'refresh failed: ' + status` — presumably transient/retryable by the caller.
   - **success**: stores the new access token with a computed `expiresAt` (line 27-30), and rotates the refresh token too if the server sent a new one (line 31) — some OAuth servers rotate refresh tokens on every use.
5. `.finally` (line 34-36): unconditionally resets `inFlight = null` once the promise settles, success or failure.

## Two requests refreshing at once

This is what `inFlight` is for:

- Request A calls `currentToken` → sees the token expired → calls `refresh(store)`. `inFlight` is `null`, so A passes the guard, starts the `fetch`, and assigns it to `inFlight`.
- Request B calls `currentToken` at nearly the same time → also sees the (still-stale, not-yet-updated) token as expired → calls `refresh(store)`. Now `inFlight` is already set, so B hits the line-13 guard and returns that *same* promise without making a second network call.
- Both A and B are awaiting the identical promise, so they get the same resolution (or the same rejection, including the 401 case) once it settles.
- Because `inFlight` is only nulled out in `.finally` after settlement, any number of callers arriving while the request is in flight get folded into the same promise — only the next call *after* settlement triggers a fresh fetch.

This works safely because JS is single-threaded and nothing awaits between the `inFlight` check (line 13) and the assignment (line 16) — so there's no window where two callers could both see `inFlight` as `null` and both start a fetch.

One asymmetry: the "no refresh token" throw (line 15) happens *before* `inFlight` is set, so it isn't deduped the way network calls are — two concurrent callers with no refresh token would each independently hit that synchronous throw. Harmless since no network request is involved either way, but worth knowing if you're about to touch this logic.


===== S07 | case: walkthrough =====
No other file calls into `auth.js` — it's self-contained, so this is the whole flow.

**Normal path.** `currentToken(store)` reads the cached access token. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, it's returned as-is — no network call. That 30s skew exists so a token doesn't expire mid-request.

**Expired/near-expired path.** If there's no token or it's within 30s of expiring, `currentToken` calls `refresh(store)` instead of returning a value.

**What "401" means here — important nuance:** there's no request-level 401 handling in this file. `currentToken` never makes an outbound API call itself and never inspects a 401 from one. The only 401 handled is a 401 from `/oauth/token` when *refreshing*, i.e. the refresh token itself was rejected. In that case (auth.js:21-24): the store is cleared entirely (both access and refresh tokens gone) and it throws `'refresh rejected; re-auth required'`. That error propagates up through `refresh()`'s promise to whoever awaited `currentToken`. So if you're expecting "on a 401 from a protected endpoint, retry with a refreshed token," that logic lives outside this file (in whatever wraps the actual API calls) — it isn't here.

Any other failure mode from `/oauth/token` (non-401, non-ok status) throws `'refresh failed: ' + status` but leaves the store untouched, so a later call will retry the refresh.

**Two requests refreshing at once.** This is the `inFlight` module-level variable. `refresh()` checks it first: if a refresh is already in progress, it just returns that same pending promise (auth.js:13) rather than starting a second `/oauth/token` call. Concretely:

- Request A calls `currentToken`, sees the token is expired, calls `refresh`. `inFlight` is null, so it sets `inFlight` to the new fetch promise and starts the call.
- Request B calls `currentToken` a moment later, also sees the token expired, calls `refresh`. `inFlight` is now non-null, so B just gets handed A's in-progress promise — no second network call.
- When the fetch resolves, `.finally()` resets `inFlight = null` (auth.js:34-36), so the *next* refresh cycle starts fresh. Both A and B resolve to the same `access_token`.
- If that shared refresh fails (401 or otherwise), both A and B reject with the same error, since they're awaiting the same promise.

One thing worth knowing before you touch this: `inFlight` is a plain module-level variable, not scoped per-store. If this module is ever used with more than one `store` (e.g. multi-account/multi-tenant), refreshes across *different* stores would incorrectly collapse into a single in-flight promise. Right now there's only one caller path so it's not a live bug, just a constraint to keep in mind if your change adds a second store.


===== S08 | case: verdict-experiment =====
Read it. The engineering side (assignment, instrumentation, rollback, scope) is solid, but the decision rule has real statistical problems that could ship a change on noise rather than a true effect.

**Critical**

1. **Daily peeking inflates the false-positive rate (§Duration and decision rule).** Stopping the first morning any metric hits p<0.05, checked daily for up to 28 days, is repeated significance testing without correction. The actual false-positive rate is nowhere near the claimed 5% — it climbs with every look. Fix: either fix the sample size/duration in advance and look once, or use a sequential procedure with alpha-spending (e.g., O'Brien-Fleming) that controls the cumulative error rate.

2. **Multiple comparisons across 8 metrics compounds it.** "A win if any of the eight reaches significance" multiplies the false-positive rate further — even independently, that's roughly a 34% chance of a spurious hit, stacked on top of the daily-peeking problem. Fix: pick one primary metric for the stop/ship decision; keep the rest as guardrails that don't trigger stopping, or apply a Bonferroni/Holm correction if several metrics are allowed to trigger it.

3. **Guardrails can be immature at decision time.** Refund rate within 14 days (§Metrics) can't be meaningfully measured for orders placed in the last two weeks — if the team stops on day 2 under the current rule, they'd be shipping on near-zero refund data. Fix: require a minimum run length (e.g., 14+ days, or the full 4 weeks) before evaluating guardrails, even if the primary metric already looks significant.

**Should fix**

4. **Randomization unit vs. analysis unit mismatch.** Bucketing is per account id (§Assignment), but the metric of record is "per session" (§Instrumentation). If one account can start checkout more than once, session-level observations are correlated within account, which violates the z-test's independence assumption and biases the p-values. Fix: aggregate to one observation per account before testing, or use a clustered variance estimator.

**Worth adding**

5. No sample-ratio mismatch (SRM) check — worth confirming the observed split stays near 50/50 each day, to catch assignment or logging bugs before trusting any p-value.
6. "Median checkout duration" tested via a z-test (which compares means) is a mismatch — durations are typically right-skewed. A rank-based test (Mann-Whitney) or bootstrap CI on the median would match the stated metric.
7. Stopping the instant significance is hit tends to overestimate the true lift (winner's curse) — worth noting the effect size at ship time is an upper bound, not the expected long-run lift.
8. The claim that the 0.3% event-loss rate applies equally to both buckets (§Instrumentation) is asserted, not verified — treatment and control render different pages and could fail differently. Worth a one-time balance check.


===== S09 | case: walkthrough =====
No other files reference it — `auth.js` is standalone (43 lines, two exported functions). Here's the flow:

**Normal path — `currentToken(store)`**
1. Reads the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, returns its value directly — no network call.
3. Otherwise (missing or within 30s of expiry), falls through to `refresh(store)`.

The 30-second skew is a buffer so a token doesn't expire mid-flight between the check and the request actually reaching the server.

**Refresh — `refresh(store)`**
1. Reads the refresh token from `store`. If there isn't one, throws `'no refresh token; re-auth required'` — this is the hard stop that pushes the caller back to a login flow.
2. POSTs to `/oauth/token` with the refresh token.
3. On the response:
   - **401** → calls `store.clear()` and throws `'refresh rejected; re-auth required'`. This is the "what happens on a 401" case *for the refresh call itself* — it means the refresh token is dead, so it wipes both tokens and forces re-authentication. Note: this file never makes the actual API calls that token is used for, so it has no handling for a 401 on a *resource* request — that logic lives wherever `currentToken()` is consumed.
   - **other non-ok status** → throws `'refresh failed: ' + status` (no store clearing — treated as transient/retryable, not a credential failure).
   - **success** → parses the body, writes the new access token (`value` + computed `expiresAt`) into the store, and conditionally updates the refresh token only `if (body.refresh_token)` is present (some providers rotate it, some don't).
4. Returns `body.access_token` from the resolved promise.

**Concurrency — the `inFlight` guard**

`inFlight` is module-level state, not per-store. Sequence for two simultaneous callers:
1. Call A finds no `inFlight`, so it starts the fetch chain and assigns it to `inFlight`.
2. Call B (before A settles) checks `if (inFlight) return inFlight;` at line 13 — it never touches `store.get('refresh')` or issues a second fetch. Both callers now await the same promise.
3. When the fetch settles (success or failure), the `.finally()` at line 34 resets `inFlight = null`, regardless of outcome.
4. Both A and B resolve/reject together with the same result — one network round trip serves both.

Things worth knowing before you touch this:
- `inFlight` is a single module-level variable, so if you ever support multiple concurrent users/stores in the same process, this collapsing logic would incorrectly merge unrelated refreshes — it's implicitly scoped to one store today.
- The 401-from-refresh path clears the entire store (access + refresh), but 401 from a downstream resource call using the returned token isn't handled here at all — if you're adding "retry once on 401" logic, that has to live in the HTTP client that calls `currentToken()`, not in this file.
- Errors thrown mid-chain still go through `.finally()`, so `inFlight` is always cleaned up — a failed refresh doesn't wedge future calls.


===== S10 | case: walkthrough =====
auth.js is the entire project — it's a standalone module, not wired into any caller yet. Here's the flow as written:

**Normal path (`currentToken`)**
- `currentToken(store)` reads the cached access token from `store.get('access')`.
- If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, it's returned as-is — no network call.
- Otherwise (missing or within 30s of expiry) it falls through to `refresh(store)`. Note the 30s skew means refresh happens *before* actual expiry, not after — this module never reacts to a live 401 from a real API call, since there's no wrapper here that catches one and retries. Whatever calls `currentToken` is expected to check expiry proactively.

**Refresh (`refresh`)**
- Reads the refresh token from the store. If there isn't one, throws immediately — no network call, caller must re-auth.
- Otherwise POSTs to `/oauth/token` with `grant_type: refresh_token`.
- On the response: a `401` means the refresh token itself was rejected — the store is cleared entirely (both tokens gone) and it throws `'refresh rejected; re-auth required'`. Any other non-ok status throws `'refresh failed: ' + status` but leaves the store untouched (so a transient 5xx doesn't nuke a still-possibly-valid refresh token).
- On success, it stores the new access token with a computed `expiresAt`, and updates the refresh token too, but only `if (body.refresh_token)` is present — so if the server doesn't rotate it, the old refresh token stays valid and in place.

**Two requests refreshing at once**
- This is the `inFlight` module-level variable. `refresh()` checks it first: if a refresh is already in progress, every caller just returns the same pending promise instead of firing a second `/oauth/token` request.
- The `.finally(() => { inFlight = null })` resets it once the request settles (success or failure), so the next call after that starts a fresh refresh.
- Concretely: if two requests call `currentToken` while the token is expired, both call `refresh`. The first sets `inFlight` and starts the fetch. The second sees `inFlight` already set and returns that same promise — so both callers get the same token (or the same rejection) from one network round trip, and the store is only written once.
- One thing worth knowing before you touch this: `inFlight` is a plain module-level variable, not per-store. If this module is ever used with more than one `store` (e.g. multi-account/multi-tenant), concurrent refreshes for *different* stores would collapse into each other incorrectly — the second store's caller would get the first store's token. Right now there's only one call site conceptually assumed, so it's fine, but it's the sharp edge to know about if your change adds multiple stores or instances.


===== S11 | case: verdict-experiment =====
Read it. The engineering side (assignment, instrumentation, rollback, scope) is solid, but the decision rule has real statistical problems that could ship a change on noise rather than a true effect.

**Critical**

1. **Daily peeking inflates the false-positive rate (§Duration and decision rule).** Stopping the first morning any metric hits p<0.05, checked daily for up to 28 days, is repeated significance testing without correction. The actual false-positive rate is nowhere near the claimed 5% — it climbs with every look. Fix: either fix the sample size/duration in advance and look once, or use a sequential procedure with alpha-spending (e.g., O'Brien-Fleming) that controls the cumulative error rate.

2. **Multiple comparisons across 8 metrics compounds it.** "A win if any of the eight reaches significance" multiplies the false-positive rate further — even independently, that's roughly a 34% chance of a spurious hit, stacked on top of the daily-peeking problem. Fix: pick one primary metric for the stop/ship decision; keep the rest as guardrails that don't trigger stopping, or apply a Bonferroni/Holm correction if several metrics are allowed to trigger it.

3. **Guardrails can be immature at decision time.** Refund rate within 14 days (§Metrics) can't be meaningfully measured for orders placed in the last two weeks — if the team stops on day 2 under the current rule, they'd be shipping on near-zero refund data. Fix: require a minimum run length (e.g., 14+ days, or the full 4 weeks) before evaluating guardrails, even if the primary metric already looks significant.

**Should fix**

4. **Randomization unit vs. analysis unit mismatch.** Bucketing is per account id (§Assignment), but the metric of record is "per session" (§Instrumentation). If one account can start checkout more than once, session-level observations are correlated within account, which violates the z-test's independence assumption and biases the p-values. Fix: aggregate to one observation per account before testing, or use a clustered variance estimator.

**Worth adding**

5. No sample-ratio mismatch (SRM) check — worth confirming the observed split stays near 50/50 each day, to catch assignment or logging bugs before trusting any p-value.
6. "Median checkout duration" tested via a z-test (which compares means) is a mismatch — durations are typically right-skewed. A rank-based test (Mann-Whitney) or bootstrap CI on the median would match the stated metric.
7. Stopping the instant significance is hit tends to overestimate the true lift (winner's curse) — worth noting the effect size at ship time is an upper bound, not the expected long-run lift.
8. The claim that the 0.3% event-loss rate applies equally to both buckets (§Instrumentation) is asserted, not verified — treatment and control render different pages and could fail differently. Worth a one-time balance check.


===== S12 | case: verdict-rollout =====
The plan has a **critical flaw**: the deployment model and migration strategy don't align.

During rolling deployment, old code instances run concurrently with new code. But the migration **drops `full_name`** before rolling deployment begins. When old instances try to read or write `full_name`, they'll fail immediately with "column does not exist" errors. This breaks the zero-downtime guarantee and would spike error rates through the entire rolling window, not just health-check failures.

**The rollback strategy also won't work.** If you roll back instances to the previous release, they'll try to access `full_name`, which the migration already dropped from the database. You've rolled back the code but not the schema.

**Better approach:** Split this into two releases:

1. **Release 1** (this week): Add `given_name` and `family_name` columns, backfill them, but leave `full_name` untouched. Update writes to populate both old and new columns. Everything still works.

2. **Release 2** (a week or two later): Update reads to use the new columns only, drop `full_name`. True rollback is now safe—old code can still run against the new schema if needed, since the columns exist.

This adds a week of dual-write overhead but buys you actual safety: no error spike, no coordinated code-and-schema rollback, and time to verify the split is working correctly before committing to dropping data.

If you want to stay with one release, you'd need to defer the `DROP` to a separate scheduled job that runs *after* all 12 instances are confirmed running the new code—but that loses the simplicity advantage.


===== S13 | case: verdict-rollout =====
Not sound — the plan breaks backward compatibility during the rolling deploy, and that same break disables rollback.

**Core problem:** migration `0142_split_name.py` drops `full_name` before the new release starts, but the new release takes ~6 minutes to roll out and old-release instances (still reading/writing `full_name` in `api/signup.py`, `api/profile_update.py`, `api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, `reports/weekly_active.py`) are serving live traffic that whole time. For those 6 minutes at 02:00 UTC, ~3-9 of the 12 instances will hit a missing column and error on every signup, profile update, and profile read.

**Rollback is also broken by the same cause:** the plan says "roll instances back to the previous image" if something goes wrong, but the previous image's code depends on `full_name`, which the migration already dropped. Rollback would need the column restored, not just the old binary.

**Secondary issue:** dropping `full_name` in the same migration that does the lossy first-space split makes the split's imperfections (mononyms, particles, reversed order) unrecoverable — there's no way to re-derive the original value for the "support corrects individual records" plan to work from.

**Fix:** use an expand/contract split across releases instead of one:
1. Release 1 — add `given_name`/`family_name`, backfill, dual-write both columns from `signup.py`/`profile_update.py`, keep reading `full_name` everywhere.
2. Release 2 — switch the four read sites to `given_name`/`family_name`. Old and new instances can coexist safely since both columns exist and are populated throughout.
3. Release 3 — stop dual-writing `full_name`, drop it once you've confirmed nothing reads it and you're comfortable losing the unsplit originals.

This adds coordination overhead, which is the tradeoff the plan explicitly weighed against — but the one-release version isn't a shortcut, it's a guaranteed error window plus a broken rollback, so it's worth the extra releases.


===== S14 | case: walkthrough =====
auth.js is the whole thing — 41 lines, no callers elsewhere in the repo. Here's the flow:

**Normal path — `currentToken(store)`** (lines 6-10)
Every outbound request calls this first. It reads the cached access token and checks `expiresAt - Date.now() > SKEW_MS` (30s skew). If the token's still good beyond that 30-second buffer, it returns `t.value` directly — no network call. Otherwise (missing, expired, or expiring within 30s) it falls through to `refresh(store)`.

**Refresh — `refresh(store)`** (lines 12-38)
1. If `inFlight` is already set, it returns that same promise immediately — this is the concurrent-refresh collapse (more below).
2. Otherwise it reads the refresh token from the store. No refresh token means an immediate throw: `'no refresh token; re-auth required'`.
3. It POSTs to `/oauth/token` and stores the resulting promise in the module-level `inFlight` variable *before* the request resolves — that's what makes step 1 work for anyone who calls in during the window the request is outstanding.
4. On response:
   - **401** (line 21-24): the refresh token itself was rejected. The store is cleared entirely (both access and refresh tokens gone) and it throws `'refresh rejected; re-auth required'`. This is the "your refresh token is dead, go log in again" path — there's no retry.
   - **Other non-ok status** (line 25): throws `'refresh failed: ' + status` but does *not* clear the store — this is treated as transient, so a caller could try again later with the same refresh token.
   - **Success**: parses the body, writes the new access token (`value` + computed `expiresAt`) into the store, and — only if the response included one — rotates the stored refresh token.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the next call after this settles (success or failure) starts a fresh refresh rather than replaying the dead promise.

**Two requests refreshing at once**
This is the `inFlight` singleton pattern. Say request A and request B both call `currentToken` and both see an expired token:
- A calls `refresh()`, finds `inFlight` null, kicks off the `fetch`, and assigns the promise to `inFlight`.
- B calls `refresh()` a moment later (before A's fetch resolves), finds `inFlight` already set, and just returns that same promise — B never issues its own POST to `/oauth/token`.
- Both A and B resolve off the single network call's result. Only after that promise settles does `.finally()` clear `inFlight`, opening the door for the *next* refresh cycle.

One thing worth knowing before you touch this: the collapsing only guards against concurrency *within a single JS instance* — there's no cross-tab/cross-process lock, so if this runs in multiple tabs sharing the same `store`, they can each independently race the refresh endpoint. Also note the two failure paths are asymmetric by design (401 nukes the store, everything else doesn't) — worth preserving if you're changing the retry/error handling.


===== S15 | case: verdict-experiment =====
The methodology has solid fundamentals but misses key statistical safeguards:

**Strengths:**
- Server-side assignment avoids client flicker; stable hashing preserves bucketing across sessions
- Reuses existing instrumentation (low implementation risk)
- Feature flag enables instant rollback with no data migration
- Diagnostic metrics paired with guardrails is good practice
- Time-bound (4 weeks) prevents indefinite peeking

**Critical gaps:**

1. **Multiple comparisons not addressed.** Eight metrics checked daily for ~28 days without adjustment inflates false-positive rate. A single p<0.05 across 8 metrics with daily peeking exceeds the stated 5% false-positive rate. Add Bonferroni correction (divide threshold by 8) or use sequential testing boundaries (Pocock/O'Brien-Fleming).

2. **Guardrail thresholds vague.** "No guardrail moved against us by more than 2%" — is that relative or absolute? If revenue per session is $100, does 2% mean $98 or $102? For rates (error rate, refund rate), 2% could be trivial or severe depending on baseline. Specify baselines and whether thresholds are relative/absolute.

3. **Power and sample size unstated.** ~2,000 sessions per bucket over 4 weeks — is that enough to detect the effect size you care about? What's the baseline conversion rate? Without this, you won't know if negative results mean "no effect" or "underpowered."

4. **Refund rate data lag.** The 14-day window means refunds from the final two weeks of the experiment won't be fully observed. Either extend observation or weight early-experiment data more heavily.

5. **Metric definitions could be tighter.** "Completed orders per session" — are these unique sessions? Unique users? Can one session have multiple orders? Precision prevents misinterpretation when analyzing.

**What to add:** Sequential testing adjustment or Bonferroni correction; power analysis; precise guardrail thresholds with baselines; explicit handling of refund-window lag.


===== S16 | case: verdict-experiment =====
The methodology has a sound foundation but has **two critical statistical issues** that inflate the false-positive risk well beyond the stated 5%:

**1. Multiple Comparisons Problem**
The plan says "a result counts as a win if *any* of the eight metrics reaches p < 0.05". Running eight independent tests at α = 0.05 gives a family-wise error rate around 34%, not 5%. With no correction (Bonferroni, FDR, etc.), the false-positive risk across all metrics is much higher than acknowledged.

**2. Sequential Testing / Optional Stopping**
Checking the dashboard each morning and stopping at the first p < 0.05 is sequential testing with optional stopping. Without alpha-spending corrections (Pocock or O'Brien-Fleming boundaries), daily peeks inflate the effective false-positive rate significantly — likely well above 5% over 28 days. The stated 5% doesn't account for this repeated testing.

**Other issues to consider:**

- **No power analysis**: You list expected volume (4,000 starts/day) but not the minimum effect size you're trying to detect. Is four weeks actually enough power?
- **Guardrail thresholds lack justification**: The 2% threshold on guardrails is stated without reasoning. Why 2%, not 1% or 3%?
- **Revenue guardrail may miss issues**: "Revenue per session" includes failed checkouts in the denominator. If the redesign increases order volume but decreases revenue per order (e.g., users accidentally skip discount fields), this metric could hide the problem.
- **No pre-registration stated**: Were these metrics and the decision rule locked in before you started, or chosen afterward? Post-hoc metric selection multiplies the problem.

**What's solid:** server-side stable assignment, leveraging existing events, feature flag rollback, excluding logged-out sessions with reasoning, and the general structure. The weak point is the statistical testing framework.


===== S17 | case: verdict-rollout =====
The plan has a critical rollback gap. Once the migration drops `full_name`, rolling back to the previous release will fail—the old code tries to read and write a column that no longer exists. You're locked in at the point the migration completes, before the new code even starts running and before verification happens.

**The safer approach:**

Split this into two releases:

**Release 1**: Add `given_name` and `family_name`, backfill, deploy code that *writes to both columns* and *reads from the new ones* (with fallback to old for safety). After this is stable and you can confirm the backfill worked, proceed.

**Release 2**: Deploy code that only uses the new columns, then drop `full_name` in a cleanup migration.

This gives you a rollback window—if something goes wrong in Release 1, you're fine. If Release 2 breaks, you can roll back Release 2 without the old code failing on a missing column.

**Other minor gaps:**

- No mention of how long the backfill takes on 2.4M rows. At low traffic (4% of peak), you should still confirm the migration completes within acceptable bounds before running it.
- Verification happens "after deploy" when instances are already running. Better to verify the migration and new code against a replica *before* the deploy window.
- No explicit pre-flight test of the migration on production-scale data.

The one-release approach trades coordination complexity for rollback safety, and on a 2.4M-row table with a breaking schema change, that's the wrong trade. How much coordination overhead are you trying to save, and would a week delay between releases be acceptable?


===== S18 | case: verdict-schema =====
**Critical issue**: `ledger_entries` and `invoices` use `DOUBLE PRECISION` for monetary amounts (`amount` and `total`). That's unsafe for financial data—floating-point arithmetic causes precision loss. Both should be `NUMERIC(19, 2)` (or whatever scale your currency uses) to store exact decimal values.

**Worth considering before you start**:

1. **Foreign key behavior**: If an account is deleted, do ledger entries stay (audit trail) or cascade? The schema allows both, but make sure the ledger deletion policy is intentional.

2. **Deduplication**: Ledger entries have no idempotency key. If you retry a charge operation, you could insert duplicates. Consider adding a `(account_id, entry_type, amount, currency, occurred_at)` unique constraint or an explicit `idempotency_key` field.

3. **Performance**: Computing balance with `sum(amount) WHERE account_id = $1` works but gets slower as the table grows. A materialized `balance` column on `accounts` or periodic snapshots might be worth planning for.

The schema is sound structurally—the ledger design is solid. Just fix the data type before you go further.


===== S19 | case: walkthrough =====
Nothing else in the repo calls this — it's a standalone module. Here's the flow as written:

**Normal path (`currentToken`)**
1. Read the cached access token from `store`.
2. If it exists and has more than 30s (`SKEW_MS`) left before `expiresAt`, return it directly — no network call.
3. Otherwise (missing or within 30s of expiry), fall through to `refresh(store)`.

**Refresh (`refresh`)**
1. If a refresh is already in progress (`inFlight` is non-null), return that same promise instead of starting a new one — this is the concurrent-request collapse.
2. Otherwise, read the refresh token from the store. If there isn't one, throw immediately (caller must re-authenticate).
3. Kick off `POST /oauth/token` with `grant_type: refresh_token`, and immediately store the resulting promise in `inFlight` (synchronously, before any `await`) so any call that arrives before the fetch resolves sees `inFlight` set and joins it rather than firing a second request.
4. When the response comes back:
   - **401**: treat the refresh token itself as dead — clear the whole store (both tokens) and throw `'refresh rejected; re-auth required'`.
   - Any other non-OK status: throw `'refresh failed: ' + status` but leave the store untouched (so a transient 500 doesn't wipe valid tokens).
   - OK: parse the body, write the new access token (with a fresh `expiresAt`), and rotate the refresh token too if the server sent a new one.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the *next* call to `refresh` (success or failure) starts a clean attempt.
6. The function returns `inFlight` (the promise) both on the fresh-start path and implicitly via step 1 for joiners.

**Two requests refreshing at once**

Concretely: request A calls `currentToken`, sees the token expired, calls `refresh` — `inFlight` is null, so A sets `inFlight` and starts the fetch. Before it resolves, request B also calls `currentToken`, also sees the token expired, calls `refresh` — `inFlight` is now non-null, so B just returns that same promise. Both A and B resolve off the one network call. Neither ever fires its own second fetch. The critical detail: `inFlight` is assigned *before* the `.then` chain runs, so there's no `await` gap between the null-check and the assignment — no window where two calls could both see `inFlight === null`.

**What a 401 means depends on which request it's on**

- A 401 from the *refresh call itself* (line 21) is handled here directly: store is wiped, error thrown.
- A 401 from an *ordinary API request* using the token is **not handled anywhere in this file** — there's no wrapper here that calls `currentToken`, gets a 401 back, and retries with a forced refresh. That logic must live in whatever HTTP client consumes this module (none exists in this repo currently). Worth confirming that's intentional before you change anything, since "what happens on a 401" for a normal request currently means "nothing — this module never sees it."

One sharp edge for your change: if `refresh` throws (bad refresh token, network error, non-OK status), `inFlight` still resets via `.finally`, but the store is only cleared on the 401 case — other failures leave a stale access token in place that will just keep re-triggering `refresh` on every call until it either succeeds or eventually gets a 401.


===== S20 | case: verdict-rollout =====
This plan has a **critical flaw in the deployment window**.

During a rolling deploy, old instances still serve live traffic while new instances are starting. The migration runs before new code deploys and drops `full_name`. But old code running on instances 4–12 will immediately fail when it tries to read or write `full_name` — the column no longer exists.

Specifically:
- `api/signup.py` and `api/profile_update.py` write to `full_name` during sign-up and profile updates (which will happen during the rolling window with live traffic)
- `api/serializers.py`, `api/search.py`, etc. read `full_name`
- All of these will get "column not found" errors

**Fixes to consider:**

1. **Two-phase rollout** (they dismissed this, but it avoids the problem):
   - Release 1: Add new columns, backfill, keep `full_name`. Code reads/writes both.
   - Release 2: Drop `full_name`. Code reads/writes only new columns.

2. **Add a view** for backward compatibility:
   - After migration, create a view that reconstructs `full_name` from `given_name`/`family_name` so old code still reads it.
   - Old code can't write through a view, but you could use a trigger.
   - This buys time to roll out new code.

3. **Reverse the order:**
   - Deploy new code first (that reads/writes both columns, or dual-writes).
   - Once all instances are running new code, run the migration.
   - Requires a "shim" release.

The current plan works only if old code never runs against the new schema, but the rolling deployment guarantees the opposite. I'd recommend either going two-phase or adding a backward-compatibility view.


===== S21 | case: verdict-rollout =====
The plan has a critical flaw in how it handles the rolling deploy window.

**The problem:** The migration drops `full_name` before any new instances start. But during the rolling deploy, old and new instances run concurrently (for ~6 minutes). When requests hit old instances, they'll try to read/write `full_name`, which no longer exists. You'll get immediate errors on every user-related endpoint until the rollout completes.

**Why this matters:** The plan treats the migration as "complete before the deploy" and the deploy as a separate event where code changes take effect. But the code assumes `full_name` exists — it's hard-coded in four read paths and two write paths. Old code can't survive the schema change it doesn't know about.

**The fix:** Keep `full_name` through the rolling deploy, then drop it in a follow-up migration or release once all instances are running new code:

1. **Release 1 (this one):** Migration adds the new columns and backfills them, but leaves `full_name` in place. New code reads and writes both (or just the new ones with a fallback to old). Old code still works unchanged.
2. **Release 2 (next):** Drop `full_name` once you're confident all old instances are gone.

This eliminates the concurrent-code-vs-schema mismatch. The two-release approach they considered actually solves this problem — it's not just about coordination cost, it's about safety.

Alternatively, if you need a single release: migrate and deploy at exactly the same time (not "before"), and coordinate the database change with infrastructure so instances don't start serving until the schema is ready. But that's harder than just keeping the old column for one more release.


===== S22 | case: verdict-rollout =====
Not sound — one real flaw, and it's serious enough to block this as written.

**The problem:** Release 1 both adds the new columns *and* drops `full_name` in the same migration, which runs to completion before any new-release instance starts. But the rolling deploy then takes ~6 minutes to replace all 12 instances, and old-release instances keep serving live traffic during that window. Those old instances still run the pre-migration `api/signup.py`, `api/profile_update.py`, `api/serializers.py`, `api/search.py`, and `jobs/welcome_email.py` — all of which read or write `full_name`, a column that no longer exists once the migration job finishes. Every request hitting those old instances during the rollout window will fail with an undefined-column error: signups, profile updates, profile views, support lookups.

**It also breaks the rollback story.** "If the new release misbehaves, the orchestrator rolls instances back to the previous image" — but the previous image's code depends on `full_name`, which is gone. Rolling back the instances doesn't roll back the schema, so a rollback would just continue erroring rather than fixing anything. The plan describes rollback as a practiced, six-minute operation, but for this migration it isn't actually a working mitigation.

There's a secondary, narrower race too: the backfill is a single pass over existing rows, but old instances are still writing `full_name` for new signups/updates while the migration job runs (traffic is ~4% of peak, not zero). Any row inserted or updated after the backfill's snapshot but before the `DROP COLUMN` step gets its name data silently lost.

**Fix:** use an expand/contract split across separate releases instead of combining them:

1. **Release 1** — add `given_name`/`family_name`, backfill, deploy code that dual-writes both old and new columns but keeps reading `full_name`. Old and new instances are both compatible with this schema; rollback is safe because `full_name` still exists and is still kept current.
2. **Release 2** — switch reads to `given_name`/`family_name` (keep dual-writing, or at least keep `full_name` populated). Still safe to roll back to Release 1.
3. **Release 3**, only after Release 2 has been stable for a while (no rollback scenario left that needs `full_name`) — drop `full_name` in its own migration.

The plan's stated reason for rejecting multiple releases — "the backfill is simple enough" — addresses backfill correctness, not the actual reason multi-release is needed here, which is mixed-version compatibility during a rolling deploy and a working rollback path. The parsing-accuracy tradeoff (splitting on first space) is fine as accepted; that part isn't the issue.


===== S23 | case: walkthrough =====
Here's the complete token refresh flow:

**Normal happy path (`currentToken`):**
Checks if you have a valid access token that won't expire within the next 30 seconds (the `SKEW_MS` buffer). If it's good, returns it immediately. If missing or stale, calls `refresh()`.

**The refresh request:**
POST to `/oauth/token` with the stored refresh token. The response body contains a new `access_token` and `expires_in` (in seconds), and optionally a new `refresh_token`. Both get stored with an absolute expiration timestamp (`Date.now() + body.expires_in * 1000`).

**Handling concurrent requests (the key part):**
There's a module-level `inFlight` variable that holds the promise from the in-progress refresh. When `refresh()` is called, it checks `if (inFlight)` and just returns that promise instead of making a new request. This collapses multiple simultaneous requests into a single HTTP call—all of them wait on the same promise. Once complete, `.finally()` clears `inFlight` so the next refresh starts fresh.

**On a 401 from the refresh endpoint:**
The refresh token itself is invalid or expired. The code clears the entire store (`store.clear()`) and throws "re-auth required". This signals to the caller that the user needs to log in again—there's no valid token path forward.

**On other non-200 responses:**
Throws with the HTTP status. The caller has to decide whether to retry or escalate.

**What happens when two requests fire simultaneously:**
Request A calls `currentToken()`, sees the token is stale, and calls `refresh()`. That starts the fetch and sets `inFlight` to its promise. Request B calls `currentToken()` a millisecond later with the same stale token. It also calls `refresh()`, but this time the check `if (inFlight)` catches it and returns the *same* promise. Both requests wait on one HTTP call. The response updates the store once, both get the new token.


===== S24 | case: verdict-experiment =====
I read it. The overall structure (bucketing, instrumentation, rollback plan) is solid, but the decision rule has real statistical problems.

**What's sound**
- Server-side, stable hash-based bucketing avoids client flicker and bucket-switching.
- Instrumentation reuses existing events instead of adding new ones, and the known 0.3% loss rate is disclosed and applies equally to both buckets.
- Rollback via flag flip is low-risk and pre-tested.
- Excluding logged-out sessions (8%) is a reasonable, disclosed trade-off.

**Problems to fix**

1. **Peeking inflates the false-positive rate far past 5%.** "Stop the first morning any metric hits p < 0.05" is repeated significance testing without correction. Checking daily for up to 28 days doesn't give a 5% false-positive rate — it gives something much higher (each day's look is a fresh chance to cross the threshold by noise). Fix: use a sequential-testing method with proper alpha-spending (group sequential design, SPRT), or commit to a fixed horizon with a single look at the end.

2. **Multiple metrics compound the peeking problem.** "A win if *any* of the eight reaches significance" tests 8 metrics × up to 28 days with no multiple-comparison correction. Combined with #1, the true false-positive rate could be several times the claimed 5%. Fix: correct across metrics (e.g., Bonferroni for the guardrails, or treat `order_placed`/`checkout_started` as the sole hypothesis test and demote the rest to non-inferiority checks rather than significance tests).

3. **The 14-day refund-rate guardrail can be evaluated before the data matures.** If the experiment stops on day 1 or 2 (which the rule permits), most treatment orders won't have had 14 days to generate a refund yet — the guardrail will look artificially clean because of right-censoring, not because refunds are actually fine. Fix: exclude this guardrail from the early-stop condition, or only evaluate it on the cohort of orders old enough to have matured.

4. **A two-sample z-test isn't the right tool for "median checkout duration."** Duration is typically skewed, and z-tests target means/proportions under a normal approximation, not medians. Fix: use a rank-based test or bootstrap CI for that metric.

5. **No minimum sample size / power analysis before stopping is allowed**, and no sample-ratio-mismatch check to confirm the 50/50 split is actually holding. Both are cheap to add and would catch early-look flukes and randomization bugs respectively.

The single biggest issue is #1 combined with #2 — as written, the stopping rule could ship the redesign off a lucky Tuesday with no real effect behind it.


===== S25 | case: verdict-rollout =====
The plan has a **critical rollback vulnerability** and some moderate risky choices.

**Critical issue: Rollback will fail.**

The migration runs before the new release deploys. If the new release misbehaves and the orchestrator rolls back the code to the old instances, those instances will try to read and write `full_name`, which no longer exists in the database. Every request fails. You have practiced rolling back the code, but not the database schema, so this failure scenario is untested and likely unrecoverable without manual intervention.

**The safer pattern:**

1. **Release 1**: Add `given_name` and `family_name`, backfill them, but leave `full_name` in place. Update code to *write* both the old and new columns (dual-write), but continue *reading* from `full_name`. Migration is additive, not destructive.
2. **Release 2** (after a few days): Migrate code to read from the new columns. Drop `full_name`. This decouples schema changes from code changes.

If release 2 breaks, you rollback code only, and the database still has `full_name`, so no cascading failures. If release 1 breaks, the new columns exist but aren't used yet.

**Secondary concerns:**

- **Concurrent writes during migration**: If the application is live while the migration backfills 2.4M rows, writes to `full_name` after the backfill but before the column is dropped will be lost. Clarify whether the app is paused during the migration window.
- **Verification is minimal**: Spot-checking 20 of 2.4M records is noise. You know the backfill breaks mononyms and non-space-separated names — run the actual backfill logic on the pre-migration dump, count how many records will be "wrong," and decide if that's acceptable. If it's thousands, support will be underwater.
- **No index**: If support needs to sort by surname often, add an index on `family_name` in the migration itself.

The one-release approach saves coordination effort, but it trades safety for speed. Given you're operating at 12 instances and have practiced orchestration, the two-release approach is more cautious and lets you abort at any point without manual recovery.


===== S26 | case: verdict-schema =====
## Issues to address before ledger work:

**Critical:**
- **`amount` in ledger_entries and `total` in invoices use `DOUBLE PRECISION`** — this is a well-known trap for financial data. Floating-point arithmetic accumulates rounding errors that compound in billing systems. Use `NUMERIC(19,4)` or similar instead. This will bite you hard.

**Should define:**
- **Foreign key deletion behavior** — no explicit `ON DELETE` clauses. For a ledger, you typically want `ON DELETE RESTRICT` (prevent deletion if ledger entries exist), since deleting accounts/subscriptions with billing history should fail, not cascade.

**Worth considering:**
- **Ledger immutability** — nothing prevents updates/deletes of ledger entries. Consider adding `CHECK (occurred_at <= now())` or an application-level guarantee that entries are write-once.
- **Currency consistency** — plan, ledger entry, and invoice each have separate currency fields, but there's no check that a charge matches the plan's currency. This could cause mismatches.
- **Balance query efficiency** — summing all ledger entries on every balance check works for small scale but won't scale. Might need a cached `account_balances` table or denormalized balance column, depending on your traffic model.

The DOUBLE PRECISION issue is a show-stopper; the others are fixable now or later depending on your timeline.


===== S27 | case: verdict-experiment =====
The methodology has a **critical statistical issue** but is otherwise well-structured.

**What's sound:**
- Clear, measurable goal (orders per session)
- Stable, server-side assignment—no client-side flicker
- Reuses existing instrumentation (no new event pipeline)
- Practical rollback (flag flip, no migration)
- Reasonable guardrails (revenue, duration, errors, refunds)
- Defined scope and timeline

**What needs fixing:**

1. **Multiple comparisons + peeking problem**: They're testing 8 metrics daily over 4 weeks (~224 tests total). Each daily check inflates the false-positive rate beyond the stated 5%. The decision rule compounds this: "ship if **any** metric hits p < 0.05" multiplies the false-positive probability again. At 8 metrics with p < 0.05, the actual risk of at least one false positive is much higher than 5% (roughly 34% if independent). 

   **Fix**: Either use sequential testing (designed for continuous monitoring), apply Bonferroni correction (divide p-threshold by # metrics: p < 0.0063 per metric), or commit to checking only once at the end.

2. **Guardrail threshold is vague**: "moved against us by more than 2%" doesn't specify absolute vs. relative change, or whether guardrails are hard stops (e.g., if refund rate doubles, stop?) vs. soft warnings. **Clarify**: define each guardrail as a hard fail or a soft check.

3. **No early stopping rule for negative trends**: What if a guardrail metric starts degrading significantly? Do they stop early or run through 4 weeks? Add an early-exit rule.

4. **Power not mentioned**: Did they calculate power for their expected effect size? 2,000 users per bucket per day seems reasonable, but this should be documented.

The core design is solid—the issue is the statistical rigor of the stopping rule. The daily peeking with 8 metrics is a common trap in A/B testing and would almost certainly give false positives if left as-is.


===== S28 | case: verdict-rollout =====
Not sound — there's a real bug in Release 1's sequencing, not just a style preference.

**Core flaw: the migration breaks the old release while it's still serving traffic, and breaks rollback entirely.**

The environment section states migrations complete *before* the first new instance starts. So the sequence is: drop `full_name` → then roll out new instances 3 at a time over ~6 minutes. During that window, every instance still running the *previous* release (all 12 at the start, tapering to 0) is executing code in `serializers.py`, `search.py`, `welcome_email.py`, `weekly_active.py`, `signup.py`, and `profile_update.py` that reads/writes a column that no longer exists. That's not a partial degradation — it's every request touching those code paths erroring, for the full rollout window, before any of the new code is even live.

Worse, it invalidates the rollback plan. "If the new release misbehaves, roll back to the previous image" assumes the previous image's code still works against the current schema. It won't — the previous image still references `full_name`, which is gone. The rollback that's been "practiced" only works for code-only regressions, not for anything triggering this migration's incompatibility, which is exactly the scenario most likely to need a rollback.

**Fix: use expand/contract across at least two releases, not one.**

1. **Release 1**: add `given_name`/`family_name`, backfill, but *keep* `full_name` and leave `signup.py`/`profile_update.py` writing it too (dual-write), so both old and new code work against the same schema. No reads move yet.
2. **Release 2**: switch all six call sites to `given_name`/`family_name`. `full_name` stays present (and dual-written) so rollback to Release 1's image still works.
3. **Release 3** (later, once confident): drop `full_name` in its own migration, once no running code references it.

The doc frames "two releases" as a coordination-cost tradeoff, but it's not optional here — it's what rolling deploy + hard schema drop requires for correctness.

**Secondary concern**: the backfill on 2.4M rows plus the `full_name` drop are described as one migration job with no mention of batching. If that's a single UPDATE + ALTER in one transaction, it risks a long table lock during the low-traffic window; worth confirming the migration tooling batches the backfill.


===== S29 | case: walkthrough =====
`auth.js` is a small, self-contained module (41 lines, no other files reference it here) — one entry point, one refresh function, module-level dedup state.

**Steady-state read path — `currentToken(store)` (line 6-10)**
Called before any authenticated request. Reads the cached access token; if it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, returns it directly with no network call. The 30s skew exists so a token doesn't expire mid-flight between being handed out and the request actually reaching the server. If the token is missing or inside that 30s window, it delegates to `refresh(store)`.

**Refresh — `refresh(store)` (line 12-38)**
1. `if (inFlight) return inFlight;` — if a refresh is already in progress, piggyback on it instead of starting a new one.
2. Otherwise read the refresh token from the store; if there isn't one, throw immediately (`inFlight` is never set on this path, so it doesn't poison future calls).
3. Otherwise POST to `/oauth/token`, and store the resulting promise chain in `inFlight` *before* returning it.
4. On response:
   - **401** (line 21-24): this means the refresh token itself was rejected by the server — expired, revoked, or invalid. The store is wiped (`store.clear()`, dropping both access and refresh tokens) and it throws `'refresh rejected; re-auth required'`. There's no retry — this propagates to the caller, who's expected to send the user through login again.
   - other non-2xx (line 25): throws `'refresh failed: <status>'`, store is left untouched (so a transient 500 doesn't nuke valid tokens).
   - success (line 26-32): stores the new access token with a computed `expiresAt`, and if the server rotated the refresh token (`body.refresh_token` present), stores that too.
5. `.finally(() => inFlight = null)` (line 34-36) always runs, clearing the flag so the *next* call to `refresh()` starts a fresh request rather than reusing a settled (resolved or rejected) promise.

**The two-concurrent-requests case**
This works because `refresh` has no `await` anywhere in its body — the `if (inFlight)` check, the `fetch()` call, and the assignment to `inFlight` all happen synchronously in one tick. So if two callers hit `currentToken` around the same time, the first call runs its entire synchronous body (sees no `inFlight`, fires the POST, assigns `inFlight`) to completion before the second call's `refresh()` even starts executing — JS doesn't interleave synchronous function bodies. The second call then sees `inFlight` already set and returns the exact same promise. Result: only one `/oauth/token` POST goes out no matter how many requests raced in, and every caller resolves to the same new access token.

**Important gap for your change**
There are two different "401"s here, and this file only handles one of them:
- A 401 **from `/oauth/token`** (refresh token itself invalid) — handled, clears the store, throws.
- A 401 **from a downstream API call** made with an expired/invalid access token — **not handled anywhere in this file**. `currentToken` only does proactive expiry checking via `expiresAt`/`SKEW_MS`; there's no reactive "request failed with 401, so refresh and retry" logic, and no other file in this directory calls `currentToken` to show what that retry path looks like. If your change involves reacting to a 401 on a real API request, that logic doesn't exist yet — you'd be adding it, not modifying it.


===== S30 | case: verdict-rollout =====
**Not sound — the single-release plan breaks rollback and guarantees errors during every rolling deploy window.**

The critical flaw: migrations run and drop `full_name` *before* the new release starts, but the rolling deploy takes ~6 minutes during which old-release instances (up to 9 of 12, tapering down) are still serving traffic on code that reads/writes `full_name`. That column will already be gone, so every signup, profile update, serializer call, search lookup, and welcome-email job hitting an old instance will error for the full deploy window — not degraded, just broken, on the four read sites and two write sites listed.

Worse, this also destroys the rollback plan: "if the new release misbehaves, roll back to the previous image" assumes the old code still works against the schema. It won't — `full_name` no longer exists, so rolling back reintroduces the same errors instead of fixing them. The plan's practiced 6-minute rollback is not actually available here.

The 4%-traffic timing window reduces volume but doesn't fix this — it's a hard error, not a slow path, and "we serve every region" means it's not zero either.

**Fix:** split into expand/contract releases, which the doc dismisses for coordination cost but is the standard way to avoid exactly this failure mode:
1. **Release 1** — add `given_name`/`family_name`, backfill, but keep `full_name` and have all six call sites dual-write (write both old and new columns; read from whichever is safe/rollback-compatible). Old code during this deploy's rolling window still works fine since `full_name` still exists.
2. **Release 2** (after the first has baked) — switch reads to the new columns, stop writing `full_name`.
3. **Release 3** — drop `full_name` once you're confident and no rollback path needs it.

This costs more coordination, as the doc notes, but the one-release version isn't a shortcut that trades coordination for risk — it's a plan that breaks on its own rollback path, which is the safety net the whole plan leans on.


===== S31 | case: verdict-experiment =====
The methodology has **major statistical flaws** that undermine the false-positive rate claim:

**Critical issues:**

1. **Multiple comparisons problem**: They track 8 metrics and ship if ANY reaches p < 0.05. Without correction, the false-positive rate is ~34%, not the claimed 5%. Each additional independent test inflates the error rate. They should use a multiple comparisons correction (Bonferroni, Benjamini-Hochberg, or adjust the threshold) or specify a *single* primary metric.

2. **Peeking/sequential testing**: Checking the dashboard every morning for up to 28 days with a p < 0.05 stopping rule dramatically inflates Type I error. Each peek resets the false-positive rate calculation. Sequential testing requires either a pre-specified spending function (e.g., Pocock or O'Brien-Fleming boundaries) or a Bayesian approach.

**Significant ambiguities:**

3. **Guardrail thresholds are vague**: "moved against us by more than 2%" doesn't specify if this is absolute or relative. For revenue per session, 2% relative makes sense; for payment error rate (a percentage itself), 2% absolute would be catastrophic. Needs precise definition per metric.

4. **Sample size justified implicitly**: No power calculation shown. They assume 4,000 starts/day is sufficient, but without knowing baseline conversion rate and target lift size, we can't verify this gives adequate power.

5. **Metric definitions in new design unclear**: The redesign collapses steps—can "shipping-step drop-off" and "payment-step drop-off" still be measured the same way? Or do they need redefinition?

**Recommendations to add:**

- Specify a single primary metric (completed orders) or implement proper multiple comparisons correction
- Use a sequential testing procedure with adjusted p-value thresholds 
- Show power calculation: baseline conversion + target effect size → required sample size
- Define guardrail thresholds precisely (absolute vs. relative per metric)
- Clarify how step-drop metrics are tracked post-redesign

The design is otherwise sound—stable assignment, existing instrumentation, clear rollback—but the statistical reasoning needs tightening.


===== S32 | case: verdict-experiment =====
The plan is well-structured for implementation (clear rollback, stable assignment, existing instrumentation), but has significant **statistical flaws** that inflate false-positive risk:

**Critical issues:**

1. **Multiple testing problem**: Checking 8 metrics daily for significance dramatically inflates Type I error. The claimed "5% false-positive rate" assumes one test; with daily checks across 8 metrics over ~28 days, the actual false-positive rate is much higher (closer to 30%+ per day compounding). This needs either a Bonferroni correction, false-discovery-rate adjustment, or a formal sequential testing design.

2. **No interim analysis plan**: Daily peeking at p-values requires boundaries set in advance (e.g., group sequential design). Just checking p < 0.05 each morning doesn't account for multiple looks at the data.

3. **Guardrail threshold is ambiguous**: "No guardrail has moved against us by more than 2%" — is this absolute or relative? (1% error rate + 2% absolute = 3%, vs. 1% + 2% relative = 1.02%?) This needs to be precise.

4. **One-directional stopping**: The rule stops only if treatment wins. If control is clearly winning, should you stop early too? Currently unspecified.

5. **No power analysis**: No documented minimum effect size, target power, or sample-size justification. With daily peeking, required sample size increases; 56k/bucket may not be sufficient depending on your true effect size.

**Minor concerns:**

- Revenue per session doesn't capture the interaction: higher orders + lower basket size could flatten total revenue
- 8% of traffic (logged-out) is excluded; if the redesign affects logged-out users differently, you won't know
- "Any of eight metrics" reaching significance is another way to state the multiple comparisons problem

**Recommendation**: Document a formal sequential testing plan (p-value spending function, group sequential design, or Bayesian updates), specify guardrail thresholds precisely, and add a power analysis. Without these, the experiment risks shipping a change that isn't actually better.


===== S33 | case: walkthrough =====
Here's the flow:

**Normal case (token still valid):**
When you call `currentToken()`, it checks if the stored access token has more than 30 seconds (`SKEW_MS`) until expiry. If yes, it returns it immediately. This avoids unnecessary refreshes for tokens that still have time left.

**Need to refresh:**
If the token is missing, expired, or within the 30-second buffer window, `currentToken()` calls `refresh()` to get a new one.

**Refresh request:**
`refresh()` posts the stored refresh token to `/oauth/token`. If successful, it stores the new access token (with an expiry time calculated from the server's `expires_in` response) and returns it. If the server sends a new refresh token, it stores that too.

**On 401 during refresh:**
The refresh token itself has expired or been revoked. The code clears the entire token store (both access and refresh tokens) and throws an error, forcing re-authentication. The app can't silently recover from this.

**Concurrent requests collapsing (the key part):**
The `inFlight` variable prevents thundering herd when multiple requests arrive simultaneously. 

1. Request A calls `currentToken()`, needs a refresh, calls `refresh()` which sees `inFlight` is null
2. Request A starts the fetch and assigns the Promise to `inFlight` before returning it
3. Request B arrives immediately and calls `currentToken()`, also needs refresh, calls `refresh()` again
4. Request B sees `inFlight` is already set (a Promise), returns it immediately without starting a second fetch
5. Both requests await the same Promise and get the same token
6. Once the fetch settles (success or error), the `.finally()` block clears `inFlight = null` so the next refresh cycle can work

This means two concurrent requests make exactly one API call, not two. If the refresh fails, both requests get the same error.


===== S34 | case: walkthrough =====
Here's the flow in `auth.js`, in order:

**1. Entry point — `currentToken(store)` (`auth.js:6-10`)**
Every caller asks for a token here. It reads the cached access token (`store.get('access')`) and checks `expiresAt - Date.now() > SKEW_MS`, where `SKEW_MS = 30000`. That's a 30-second safety margin: a token is only considered "good" if it has more than 30s of life left, not just any time left. This absorbs request latency and clock drift so you don't send a token that expires mid-flight. If the token is missing or inside that skew window, it falls through to `refresh(store)`.

**2. `refresh(store)` (`auth.js:12-38`) — the actual network call**
- Reads the refresh token from the store; if there isn't one, throws immediately (`'no refresh token; re-auth required'`) — no network call.
- Otherwise POSTs to `/oauth/token` and chains handling onto the fetch promise:
  - `res.status === 401` → the refresh token itself was rejected. It calls `store.clear()` and throws `'refresh rejected; re-auth required'`.
  - any other non-ok status → throws `'refresh failed: ' + status`.
  - success → parses the body, writes the new access token (`value` + computed `expiresAt`) into the store, and — only if the server rotated it — writes a new refresh token. Refresh token rotation is optional here: if `body.refresh_token` is absent, the old refresh token stays in the store and gets reused next time.
  - Resolves with the new access token string.

**3. Two requests refreshing at once — the `inFlight` guard (`auth.js:4, 13, 34-36`)**
`inFlight` is a module-level variable, not per-call. `refresh()` checks it first: if a refresh is already in flight, it just returns that same promise instead of starting a second `fetch`. The assignment `inFlight = fetch(...)` happens synchronously (the `fetch` call returns a pending promise immediately), so there's no gap where a second concurrent call could sneak past the check — JS won't interleave two calls to `refresh()` unless something actually awaits between the check and the assignment, and nothing does. So `Promise.all([currentToken(store), currentToken(store)])` triggers exactly one network request; both callers resolve off the same promise. `.finally(() => inFlight = null)` clears the flag once the request settles (success or failure), so the *next* expiry triggers a fresh refresh rather than being stuck.

**4. What happens on 401 — important nuance for your change**
The only 401 this file handles is from the **token endpoint itself** (`/oauth/token` rejecting the refresh token) — that's `auth.js:21-24`. That failure propagates through the shared `inFlight` promise, so every caller waiting on that refresh gets the same rejection simultaneously and the store is already cleared by the time they see it.

There's no handling here for a 401 coming back from an actual protected API request (i.e., "access token got revoked/invalid, retry with a refreshed one"). This module only exposes `currentToken`/`refresh`; nothing here wraps outbound API calls or reacts to their 401s — I checked, and nothing else in this directory calls into `auth.js` at all, so that layer doesn't exist yet. If your change is meant to add "retry on 401 from a resource request," that's new logic you'd be building on top of `currentToken`, not something already here.

What are you looking to change — add resource-request 401 handling, adjust the skew/concurrency behavior, or something else?


===== S35 | case: walkthrough =====
Here's the flow in `auth.js:1-41`.

## Normal path — `currentToken()`

`currentToken(store)` (auth.js:6-10) is the entry point callers use before each outbound request:
- It reads the cached access token from `store`.
- If it exists and has more than `SKEW_MS` (30s, auth.js:2) left before `expiresAt`, it returns the value directly — no network call.
- Otherwise (missing, or expiring within 30s) it calls `refresh(store)` and returns whatever that resolves to.

So refresh here is **proactive**: triggered by looking ahead at the token's expiry, not by a request actually failing.

## `refresh()` and the 401 case

`refresh(store)` (auth.js:12-38):
1. If `inFlight` is already set, it immediately returns that promise (see concurrency section below).
2. Otherwise it reads the refresh token from `store`. If there isn't one, it throws synchronously — `'no refresh token; re-auth required'`. This throw happens *before* `inFlight` is set, so it's a one-off rejected promise, not shared.
3. It POSTs to `/oauth/token` with `grant_type: refresh_token`, and assigns the resulting promise chain to `inFlight` right away (synchronously, before any `await`) — that's what makes the concurrency collapse work.
4. In the response handler:
   - **`res.status === 401`**: this means the *refresh token itself* was rejected (revoked/invalid). The code calls `store.clear()` — wiping both access and refresh tokens — and throws `'refresh rejected; re-auth required'`. There's no retry; the caller has to send the user through re-authentication.
   - Any other non-ok status throws `'refresh failed: ' + status` (transient/server error, tokens are left untouched).
   - On success, it writes the new access token (`value` + computed `expiresAt`) into the store, and updates the refresh token too if the server rotated it.
5. `.finally()` sets `inFlight = null` once the request settles (success or failure), so the next call starts a fresh request rather than reusing a resolved/rejected promise.

One thing worth flagging since you asked specifically about "what happens on a 401": this file only reacts to a 401 from *its own* `/oauth/token` refresh call. There's no wrapper here that catches a 401 from an arbitrary API request and triggers a refresh-and-retry — that logic (if it exists) must live in whatever code calls `currentToken()`.

## Two requests refreshing at once

The dedupe relies on `inFlight` being set **synchronously**, with no `await` before that assignment:
- Request A's `expiresAt` check fails, it calls `refresh()`. `inFlight` is `null`, so A proceeds, reads the refresh token, and immediately assigns `inFlight = fetch(...)...`. All of this happens synchronously in one tick.
- Request B calls `refresh()` shortly after (or even in the same tick, before A's fetch settles). It sees `inFlight` already set and just returns that same promise — no second network call, no second read of the refresh token.
- Both A and B await the identical promise and get the identical new access token when it resolves; the store is written exactly once.
- If it rejects (e.g. the 401 case above), both A and B see the same rejection.

The fragile part to know before you change this: the guard only works because there's no `await` between the `inFlight` check and the `inFlight = fetch(...)` assignment. If you ever insert an `await` before that assignment (e.g. to look something up first), two concurrent calls could both pass the `if (inFlight)` check before either sets it, and you'd get two real refresh requests racing — likely both succeeding, with the second's refresh-token rotation silently invalidating whatever the first cached.


===== S36 | case: walkthrough =====
Only file in the repo, so `currentToken`/`refresh` aren't called elsewhere yet — this is the whole picture. Here's the flow in `auth.js`:

**Normal request path** (`currentToken`, lines 6-10)
- Reads the cached access token from `store`.
- If it exists and has more than 30s (`SKEW_MS`) left before `expiresAt`, returns its value directly — no network call.
- Otherwise (missing or about to expire), calls `refresh(store)` and returns whatever that resolves to.

**Refresh itself** (`refresh`, lines 12-38)
- Reads the refresh token from the store. If there isn't one, throws immediately — caller must re-authenticate.
- POSTs to `/oauth/token` with `grant_type: refresh_token`.
- On success: stores the new access token with a computed `expiresAt`, and if the server rotated the refresh token (`body.refresh_token` present), overwrites that too.
- Returns the new access token string.

**On a 401 from the refresh endpoint** (lines 21-24)
- This is a 401 from `/oauth/token` itself (the refresh call), not a 401 from some other API request — nothing here reacts to a 401 on an arbitrary request, since there's no request wrapper in this file.
- On that 401, the store is cleared entirely (both access and refresh tokens gone) and it throws `'refresh rejected; re-auth required'`. There's no retry — the caller has to send the user through login again.
- Any other non-ok status throws a generic `'refresh failed: ' + status` but leaves the store untouched, so a caller could retry later.

**Two requests refreshing at once** (the `inFlight` guard, lines 4, 13, 34-36)
- `inFlight` is a module-level variable, `null` when no refresh is in progress.
- First caller to hit `refresh()` finds `inFlight` null, so it starts the `fetch` and assigns the promise to `inFlight`.
- Any other caller that calls `refresh()` (directly, or indirectly via `currentToken()` finding an expired token) while that fetch is still pending sees `inFlight` already set and just returns the *same promise* — no second HTTP request fires.
- Both callers resolve together off that one promise, with the same access token.
- `.finally()` resets `inFlight = null` once the request settles (success or failure), so the next expiry triggers a fresh call rather than reusing a stale promise.
- Note: `inFlight` isn't cleared on `currentToken`'s fast path, only inside `refresh`, so any interleaving is safe as long as everything funnels through `refresh()` — bypassing it (e.g. a second module instance or a caller that hits `/oauth/token` directly) would defeat the dedup.

One thing worth flagging before you touch it: the `inFlight` promise is shared as-is, including its rejection — if the refresh fails, *every* caller that piggybacked on that promise gets the same rejected promise, not independent retries.


===== S37 | case: verdict-experiment =====
The methodology has solid fundamentals but has **two critical statistical issues** that could lead to many more false positives than the claimed 5%:

1. **Multiple comparisons problem**: Testing 8 metrics and shipping whenever *any* hits p < 0.05 inflates the false-positive rate. With independent tests, you're actually looking at ~34% cumulative false-positive rate (1 − 0.95⁸), not 5%. They need either a Bonferroni correction (divide α by 8, so p < 0.006 per metric) or designate a single primary metric and treat the rest as guardrails that must *not* degrade.

2. **Peeking problem**: Checking the dashboard daily and stopping as soon as any metric crosses p < 0.05 (sequential peeking without correction) further inflates false positives. Each additional look without a proper stopping boundary raises the effective false-positive rate. They need either a pre-specified stopping rule like Pocock or O'Brien-Fleming boundaries, or commit to one final analysis at four weeks.

**Other issues:**

- **Guardrail definition unclear**: "moved against us by more than 2%" is ambiguous—relative or absolute? Against baseline or control? Needs precision.
- **Missing power calculation**: No mention of whether 4,000 starts/day for four weeks gives enough power to detect the effect they care about.
- **Sample size justification**: Why four weeks specifically? Should be tied to effect size and power, not calendar.

**Keep:**
- Stable hashing, server-side bucketing, feature-flag rollback, diagnostic metrics, 0.3% event-loss acceptance, and excluding logged-out sessions are all sound.

Recommend they either use a single primary metric with proper sequential testing, or reduce to fewer metrics with Bonferroni correction and pre-commit to the four-week endpoint.


===== S38 | case: verdict-rollout =====
This plan has a critical race condition during the rolling deploy that's not addressed.

**The problem:** The migration drops `full_name` before any new instances are running, but old instances are still live and will attempt writes to that column during the rolling deploy window (roughly six minutes). Those writes will fail, causing errors for support and the API.

Timeline of the issue:
1. Migration completes, `full_name` is dropped
2. Rolling deploy begins; orchestrator shuts down old instance #1, starts new instance #1
3. Old instances #2–12 are still running, still have code that tries to write to `full_name`
4. Database errors for any user-mutation operations during the next ~5 minutes

**The standard fix is a two-release approach:**
- **Release 1:** Add `given_name` and `family_name` columns alongside `full_name`. Deploy code that writes to both (keeping them in sync) and reads from either.
- **Release 2:** After all instances are upgraded, backfill in the background and drop `full_name`. Deploy code that reads/writes only the new columns.

This avoids the race by ensuring old code can still write when it needs to.

**Alternatively**, if they want to stay single-release: the migration should *not* drop `full_name` until after the rolling deploy completes and all old instances are gone. The schema cleanup happens after verification, as a separate database job.

The rollback scenario also doesn't work as written—rolling back the code to the old release doesn't help if `full_name` is already gone from the database. They'd need to restore from a backup.

The plan is sound on everything else (backfill simplicity, timing, verification), but this gap needs fixing before cutover.


===== S39 | case: walkthrough =====
No other files reference it — it's a standalone module, not yet wired into a request pipeline. Here's the flow as written:

**Getting a token (`currentToken`)**
- Reads the cached access token from `store`.
- If it exists and has more than 30s (`SKEW_MS`) left before expiry, returns it directly — no network call.
- Otherwise (missing or about to expire), calls `refresh(store)` and returns its result.

**Refreshing (`refresh`)**
- If a refresh is already in flight (`inFlight` is non-null), returns that same promise instead of starting a new one — this is the dedup for concurrent callers.
- Otherwise reads the refresh token from the store. If there isn't one, throws immediately (`no refresh token; re-auth required`) — no request is made.
- Starts the POST to `/oauth/token` and immediately stores the promise in `inFlight` (synchronously, before any `await`), so any call to `refresh` that arrives before this promise settles sees `inFlight` set and joins it rather than firing a second request.
- On response: a 401 from the token endpoint means the refresh token itself was rejected — it clears the whole store (wipes both access and refresh tokens) and throws `refresh rejected; re-auth required`. Any other non-ok status throws `refresh failed: <status>`.
- On success, writes the new access token (with computed `expiresAt`) into the store, and rotates the refresh token too if the server sent a new one.
- `.finally()` resets `inFlight` to `null` regardless of outcome, so the *next* call to `refresh` (after this one settles, success or failure) starts a fresh request rather than reusing a dead promise.

**Two requests refreshing at once**
Both call `refresh()`. The first sees `inFlight === null`, kicks off the fetch, and sets `inFlight` to that promise before yielding to the event loop (no `await` happens before the assignment). The second call — whether from the same tick or any time before the promise settles — sees `inFlight` already set and just returns it. Both callers end up awaiting the identical promise, so exactly one network request happens, and both either get the same token or the same rejection.

**Important gap for what you're about to change:** the "401" here is *only* the token-refresh-endpoint's 401 (refresh token rejected). There's no code here handling a 401 from a regular API call that would trigger a refresh-and-retry — `currentToken`/`refresh` are purely for keeping the access token itself fresh proactively (via the expiry/skew check). If your change involves reacting to a 401 on an arbitrary outgoing request, that logic doesn't exist yet in this file and you'd be adding it new, not modifying it.


===== S40 | case: walkthrough =====
No callers exist elsewhere — this is the whole picture; there's no wrapper that catches a 401 from a normal API call and retries via `currentToken`.

Here's the flow in `auth.js:1-41`:

**Normal path — `currentToken(store)`**
1. Reads the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, returns it directly — no network call.
3. Otherwise (missing or within 30s of expiry), calls `refresh(store)` and returns whatever that resolves to.

**Refresh — `refresh(store)`**
1. If a refresh is already in flight (`inFlight` is non-null), it returns that same promise instead of starting a new one — this is the concurrent-request collapsing.
2. Otherwise, reads the refresh token from `store`; if there isn't one, throws immediately (`no refresh token; re-auth required`) — no network call happens.
3. Kicks off a `POST /oauth/token` with `grant_type: refresh_token`, and stores the promise in `inFlight` right away (synchronously, before any `await`), so any call to `refresh` that arrives before the fetch resolves sees `inFlight` set and piggybacks on it.
4. `.finally()` clears `inFlight` back to `null` once the request settles (success or failure), so the *next* refresh cycle starts fresh.

**On the response:**
- `401` from `/oauth/token` (the refresh call itself, not a general API call) means the refresh token was rejected: `store.clear()` wipes everything, then throws `refresh rejected; re-auth required`.
- Any other non-ok status throws `refresh failed: <status>`.
- On success, it writes the new access token (`value` + computed `expiresAt`) into the store, and rotates the refresh token too if the server sent a new one.
- Returns `body.access_token`.

**Two requests refreshing at once** — this is the concurrency case handled by module-level `inFlight`, checked and set synchronously at the top of `refresh` before the `await` boundary: whichever caller runs first creates the fetch and stores the promise; a second caller arriving before it settles gets the exact same promise, so only one `POST /oauth/token` ever goes out, and both callers resolve/reject together off that single request.

One thing worth flagging since you're about to change this: there's no request-level 401 handling here at all — nothing in this file intercepts an API response, spots a 401, and asks `currentToken` for a fresh token. The whole refresh trigger is time-based (the 30s skew check), not reactive to a 401 from a downstream call. If your change assumes there's a "on 401, retry with refreshed token" path, that logic lives elsewhere or doesn't exist yet.


===== S41 | case: verdict-rollout =====
Not sound — the plan has a serious flaw in how the migration interacts with the rolling deploy and rollback.

**Core problem:** migration `0142_split_name.py` drops `full_name` *before* the new release starts, but the rolling deploy means old-release instances keep serving traffic for the full ~6-minute rollout. Those old instances still read/write `full_name` in six call sites — that column no longer exists, so every one of those code paths (profile endpoints, signup, profile update, welcome email, weekly report, support search) errors out for however many old instances are still up. At 4% traffic this isn't zero users, and it's not a blip — it's the whole rollout window.

**Worse, it breaks the stated rollback plan.** "Roll instances back to the previous image" only works if the previous image's code still functions against the current schema. Since `full_name` is dropped, rolling back doesn't restore working behavior — every instance (old and new) is now querying a column that doesn't exist. The rollback they've practiced and are relying on is incompatible with this migration.

**Also unaddressed:** are `jobs/welcome_email.py` and `reports/weekly_active.py` deployed as part of the same 12-instance rolling release, or separately? If separately, they could keep running old code against the post-drop schema for an arbitrary period after the migration, not just six minutes.

**Fix:** use expand/migrate/contract across separate releases instead of one:
1. **Expand** — add `given_name`/`family_name`, backfill, but keep `full_name` in place (and keep old code as-is, or have new code dual-write all three columns).
2. **Migrate** — ship the release that switches all six call sites to `given_name`/`family_name`. `full_name` still exists, so both old and new code work simultaneously during the rolling window, and rollback is safe.
3. **Contract** — once that release is fully rolled out and stable (and any independently-deployed jobs are confirmed updated), a separate migration drops `full_name`.

The backfill-correctness tradeoff and Tuesday-02:00 timing are fine as documented. The single-release, drop-in-the-same-migration approach is the part to change.


===== S42 | case: verdict-schema =====
Three things stand out before you build the ledger on this:

**1. DOUBLE PRECISION for money — use NUMERIC instead.** Floating-point math accumulates rounding errors over time, which breaks ledgers. You need fixed-point precision. Switch to `NUMERIC(19, 2)` (or whatever scale fits your currency). This matters for every amount field.

**2. Foreign keys need ON DELETE policy.** If an account gets deleted, do ledger entries cascade (probably yes)? Do subscriptions cascade? Right now there's no enforcement — you could orphan data or hit unexpected constraint violations during cleanup. Decide and add `ON DELETE CASCADE` or `ON DELETE RESTRICT`.

**3. Invoice-ledger mismatch.** Invoices store a denormalized `total`, but there's no link to which ledger entries it represents. On audit, you can't verify an invoice matches its entries. Add a foreign key relationship (either a new `invoice_id` column on ledger_entries, or a junction table), or at minimum document the period matching clearly so queries stay in sync.

**Secondary:** Add a CHECK on invoices that `period_start < period_end` — catches bugs early.

The schema is sound otherwise — nullable subscription_id makes sense for credits that aren't subscription-tied, and the indices are reasonable. But fix those three before you write ledger logic.


===== S43 | case: walkthrough =====
Here's the complete token refresh flow in auth.js:

## Normal Happy Path

When `currentToken(store)` is called (auth.js:6):
1. It retrieves the stored access token
2. Checks if it's still valid: the token's `expiresAt` time minus 30 seconds (SKEW_MS buffer) hasn't passed yet
3. If valid, returns the token immediately
4. If expired or missing, calls `refresh(store)`

## The Refresh Request

When `refresh(store)` is called (auth.js:12):
1. **Concurrent request collapse** (auth.js:13): If `inFlight` is already set (meaning a refresh is in progress), it returns that same promise. Multiple requests don't trigger multiple refresh calls—they all await the one in-flight request.
2. **Fetch the token** (auth.js:16-19): POSTs to `/oauth/token` with the stored refresh token
3. **Success case** (auth.js:20-32): 
   - Parses the response JSON
   - Stores the new access token with a calculated `expiresAt` timestamp
   - If the response includes a new refresh token (rotation), stores that too
   - Returns the new access token
4. **Sets `inFlight = null`** in the `finally` block (auth.js:34-35), so the next refresh call can proceed independently

## What Happens on a 401

If the `/oauth/token` request returns 401 (auth.js:21-23):
- Calls `store.clear()`, removing both the access token and refresh token
- Throws an error saying re-authentication is required
- Sets `inFlight = null` in finally, but downstream code will need to catch the error and redirect to login

The 401 means your refresh token itself is invalid/expired (not just the access token).

## Concurrent Request Scenario

Say two requests come in 100ms apart, both needing a token:

1. **Request A**: `currentToken()` finds token expired → calls `refresh()`
   - `inFlight` is null, so it makes the POST and stores the promise in `inFlight`
   - Returns that promise

2. **Request B** (while POST is in flight): `currentToken()` finds token expired → calls `refresh()`
   - Sees `inFlight` is already set → returns that same promise without making a second POST
   - Awaits the same response as Request A

3. Both requests get the same access token, and the store is only updated once.

The key insight: `inFlight` collapsing prevents duplicate refresh requests during the network round-trip, and the `finally` cleanup ensures the next batch of expiring tokens can trigger a fresh refresh.


===== S44 | case: verdict-experiment =====
The plan has strong fundamentals—clear goal, stable bucketing, low-risk instrumentation—but has two significant methodological issues:

**Critical: Multiple comparisons problem.** The plan checks 8 metrics daily for up to 28 days and stops at the first p < 0.05. This is continuous monitoring without correction, which inflates the false-positive rate far beyond the claimed 5%. With even rough math: 8 metrics × ~28 days of checks, each at p = 0.05, compounds to something closer to 20–30% false-positive risk. You need either a single pre-planned analysis at 4 weeks, or a proper sequential testing framework with a pre-registered spending function that limits cumulative alpha across peeks.

**Significant: Selection bias.** Excluding logged-out sessions (8% of starts) assumes they behave identically to logged-in users. If the redesign's single-page layout affects checkout completion rate differently for anon vs. logged-in users, your results won't generalize. Document whether you expect the treatment to affect them equally, or accept that results apply only to logged-in cohorts.

**Minor clarity gaps:**
- The "2% guardrail threshold" isn't defined precisely—is this absolute, relative, or direction-specific?
- No sample size / power calculation shown. With 4,000 starts/day you should be able to detect small lifts, but the math should be explicit.

**What to fix:** Either move to a single final analysis at week 4 (simplest, safest), or adopt sequential testing rules that control error rate properly. Both are standard in industry; the daily-peek-and-stop approach is tempting but statistically unsound here.


===== S45 | case: verdict-schema =====
Short answer: not yet — the float money columns and a couple of ledger-specific gaps will bite you. In order of severity:

1. **Money is `DOUBLE PRECISION`** (`plans.monthly_price`, `ledger_entries.amount`, `invoices.total`). Binary floats can't represent cents exactly; `sum(amount)` for a running balance will drift over enough rows. Use `NUMERIC(12,2)` (or store integer minor units as `BIGINT`) everywhere money appears.

2. **No idempotency key on `ledger_entries`.** Charges/refunds normally come from retryable events (webhooks, retried jobs). Without a unique `external_ref`/`idempotency_key`, a retry double-inserts and the balance is silently wrong. Add one with a unique constraint.

3. **The documented balance query contradicts the schema.** The comment says balance is `SELECT sum(amount) FROM ledger_entries WHERE account_id = $1`, but `currency` is a per-row column, not fixed per account — an account with entries in two currencies would sum unrelated currencies together. Either constrain one currency per account (FK to a currency on `accounts`, or a check against the account's existing entries) or make the balance query `GROUP BY currency` and fix the comment.

4. **No constraint tying `entry_type` to the sign of `amount`.** Nothing stops a `'refund'` row from being stored positive (or a `'charge'` negative), which breaks the sum-as-balance invariant silently. Add a `CHECK` relating type to sign, or pick one convention (e.g., refunds/credits always negative) and enforce it.

5. **Ledger rows are mutable.** There's nothing (constraint, trigger, or revoked privileges) stopping `UPDATE`/`DELETE` on `ledger_entries`. A financial ledger usually wants to be append-only, with corrections done via new offsetting rows.

6. **`invoices.total` isn't reconciled to anything.** It's written independently at close with no unique constraint on `(account_id, period_start, period_end)` and no way to verify later that `total` still matches the sum of that period's entries — easy for invoice and ledger to quietly diverge.

The rest (FKs, `subscriptions`/`ledger_entries` indexes, status `CHECK`, no cascading deletes) is solid. I'd fix 1–4 before writing ledger code against this — they change the column types and constraints the ledger logic will depend on; 5–6 can follow once the core shape is settled.


===== S46 | case: verdict-rollout =====
Not sound — there's a real bug in the plan, not just a stylistic concern.

**The core problem: migration and code deploy aren't compatible during the rollout window.**

The migration drops `full_name` *before any new-release instance starts*. But the rolling deploy takes ~6 minutes, during which up to 9 of 12 instances are still running the *old* release — code in `api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, `reports/weekly_active.py`, `api/signup.py`, and `api/profile_update.py` that all reference `full_name`. That column is gone the moment the migration job finishes, so every one of those old instances will start erroring on the very requests the plan is trying to protect (signup, profile update, profile reads) — for the whole rollout window, not just an edge case.

**This also breaks the rollback plan.** "Roll back to the previous image" assumes the previous image's code is compatible with the current schema. It isn't — `full_name` no longer exists, so a rollback to old code doesn't recover; it just moves the same crash back onto all 12 instances. The "we've practised rollback, six minutes" reassurance doesn't hold here because rollback was never tested against a schema that already dropped the column being read.

**Fix: split into expand/contract across releases**, which is exactly the two-release option the plan considered and rejected:

1. **Release 1** — migration adds `given_name`/`family_name` (nullable) and backfills, but **keeps `full_name`**. No code changes yet, or code changes that read new columns but fall back / dual-write to `full_name`. Old code is unaffected; rollback is safe.
2. **Release 2** — switch the six call sites to `given_name`/`family_name`. `full_name` still exists as a safety net, so both this release and a rollback of it are schema-compatible.
3. **Release 3** (later, once confident) — migration drops `full_name`.

The "doubles the coordination cost" trade-off they cite against two releases is real, but it's not optional here — a single-release expand-and-contract is only safe if old and new code can both run against the *final* schema simultaneously, and that's not true for this change since `full_name` is being removed outright.

Everything else in the plan — timing, backfill-splitting caveat, verification steps — is reasonable and doesn't need changes.


===== S47 | case: walkthrough =====
Here's the whole flow in `auth.js`:

**Normal request path** (`currentToken`, lines 6-10)
1. Read the cached access token from `store`.
2. If it exists and has more than `SKEW_MS` (30s) left before `expiresAt`, return it immediately — no network call.
3. Otherwise (missing or within 30s of expiring), fall through to `refresh(store)` and return whatever that resolves to.

The 30-second skew exists so a token that's technically still valid but about to expire mid-request doesn't get used — it forces an early refresh instead.

**Refresh path** (`refresh`, lines 12-38)
1. If `inFlight` is already set, return that same promise — don't start a second refresh.
2. Otherwise, read the refresh token from the store. If there isn't one, throw immediately (`no refresh token; re-auth required`) — this is a synchronous throw, not part of the `inFlight` promise chain.
3. Otherwise, POST to `/oauth/token` and store the resulting promise in `inFlight` right away, before `await`ing anything.
4. On response:
   - **401** → call `store.clear()` (wipes both tokens) and throw `refresh rejected; re-auth required`. This is the "refresh token itself is dead" case — the caller has to send the user back through login.
   - **other non-ok** → throw `refresh failed: <status>` and leave the store untouched, since this might be transient (network blip, 500, etc.) rather than a reason to nuke the tokens.
   - **ok** → parse the body, write the new access token (with a fresh `expiresAt`) into the store, and — only if the response included one — rotate the stored refresh token.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the *next* call to `refresh` (success or failure) starts a clean attempt.
6. The function returns `inFlight`, so every caller — whether it triggered the fetch or piggybacked on one already running — awaits the exact same promise and gets the same result or the same rejection.

**Two requests refreshing at once**

Say request A calls `currentToken()`, finds the token expired, and calls `refresh()`. Before that fetch resolves, request B also calls `currentToken()` and also lands in `refresh()`. Because `inFlight` was set synchronously (line 16) before any `await`, B's call at line 13 sees a non-null `inFlight` and returns that same promise — no second HTTP call, no race to write the store. Both A and B resolve (or reject) together off the one in-flight request. This works because JS is single-threaded and `refresh` doesn't `await` anything before setting `inFlight`, so there's no window where two calls can both see it as `null`.

One thing worth flagging before you change anything: a 401 from a *regular API call* (not the refresh endpoint) isn't handled anywhere in this file — there's no wrapped-fetch-that-catches-401-and-retries-with-a-fresh-token. The only 401 handling here is for the `/oauth/token` refresh call itself. If your callers expect `currentToken`/`refresh` to also cover "API call came back 401, refresh and retry," that logic lives outside this file (or doesn't exist yet).


===== S48 | case: walkthrough =====
No callers in this repo — `auth.js` is standalone. Here's the flow as written:

**Normal path (`currentToken`)**
1. Reads the cached access token from `store`.
2. If it exists and has more than 30s (`SKEW_MS`) of life left, returns it directly — no network call.
3. Otherwise (missing or about to expire), calls `refresh(store)` and returns whatever that resolves to.

**Refresh (`refresh`)**
1. If a refresh is already in flight (`inFlight` is non-null), returns that same promise instead of starting a new one — this is the concurrency collapse.
2. Otherwise, reads the refresh token from the store. If there isn't one, throws immediately (`no refresh token; re-auth required`) — no request is made.
3. Kicks off `POST /oauth/token` with `grant_type: refresh_token`, and immediately stores the resulting promise in `inFlight` *before* awaiting it. That's what lets step 1 catch concurrent callers.
4. When the response lands:
   - **401** → calls `store.clear()` and throws `refresh rejected; re-auth required`. This is the only 401 handled here — it's the refresh *endpoint* rejecting the refresh token (e.g., it's revoked or expired), not a 401 from some other API call using the access token. `auth.js` has no involvement in that latter case; whatever code makes the actual API request would need its own logic to catch a 401, call `currentToken`/`refresh`, and retry.
   - Any other non-OK status → throws `refresh failed: <status>` (store is left untouched, so a transient 500 doesn't wipe out valid tokens).
   - Success → parses the body, writes the new access token (with a fresh `expiresAt`) into the store, and conditionally rotates the refresh token if the server issued a new one. Resolves with the new access token.
5. `.finally()` resets `inFlight = null` regardless of outcome, so the *next* call to `refresh` (success or failure) starts a clean attempt rather than replaying a stale rejected promise.

**Two requests refreshing at once**

Both call `currentToken` around the same time, both see the access token expired/near-expiry, both call `refresh`. The first call finds `inFlight` null, so it creates the fetch and assigns `inFlight` synchronously (before any `await`). The second call — even if it arrives on the very next microtask, since JS is single-threaded — sees `inFlight` already set and just returns that same promise. So only one `/oauth/token` request ever goes out; both callers resolve (or reject) together off the same result. There's no lock/queue needed because the assignment happens synchronously ahead of the async `.then` chain.

**Things to be aware of if you're about to change this:**
- Failed refreshes (rejected `inFlight`) are not cached or retried automatically — the caller gets the rejection, and the *next* call to `currentToken`/`refresh` will attempt a fresh network call.
- On a 401 from the refresh endpoint, `store.clear()` wipes both tokens — any concurrent caller riding the shared promise also gets the rejection and sees a cleared store.
- There's no handling here for a 401 on a *resource* request made with the access token (only the refresh call's own 401 is handled) — if that's the behavior you want to add or change, it'll live in whatever wraps outbound API calls, not in this file as it stands.


===== S49 | case: verdict-schema =====
Short answer: no, fix the money representation and a couple of ledger-integrity gaps first.

1. **`DOUBLE PRECISION` for all money columns** (`plans.monthly_price` line 16, `ledger_entries.amount` line 38, `invoices.total` line 51) — floating point can't represent decimal currency exactly, and the balance query the comment documents (`SELECT sum(amount) FROM ledger_entries WHERE account_id = $1`) will accumulate rounding drift as entries pile up. Use `NUMERIC(12,2)` (or integer minor units/cents) instead.

2. **Ledger entries are fully mutable** — there's no trigger, rule, or revoked privilege stopping `UPDATE`/`DELETE` on `ledger_entries`. A financial ledger that can be silently edited isn't an audit trail. Lock it down (revoke `UPDATE`/`DELETE` from the app role, or a trigger) and correct mistakes with reversing entries, not edits.

3. **The documented balance query ignores currency.** `ledger_entries.currency` can vary per row, but `sum(amount) WHERE account_id = $1` mixes currencies together with no grouping. Either constrain one currency per account or fix the query to `GROUP BY currency`.

4. **No idempotency key.** Nothing prevents a retried charge or duplicate webhook delivery from inserting the same ledger entry twice — worth an external reference id with a unique constraint.

5. Minor: no `CHECK` tying `entry_type` to the sign of `amount`, so a `'refund'` with a positive amount or a `'charge'` with a negative one is representable and easy to get backwards in application code.

#1 is the one to fix before anything else builds on this — the rest are worth doing in the same pass since the ledger table is still new.


===== S50 | case: walkthrough =====
Here's the complete token refresh flow:

## The Normal Happy Path

**`currentToken()` is the entry point.** It checks the stored access token: if there's a valid token with more than 30 seconds left (the SKEW buffer), it returns it immediately. Otherwise it calls `refresh()`.

The 30-second skew is a safety margin—even if the token looks valid now, it might expire mid-request. Refreshing early avoids that race.

## The Refresh Call

**`refresh()` starts the refresh request.** The first thing it does is check `inFlight`—a module-level variable that holds the currently-running refresh promise. If a refresh is already in progress, it returns that promise instead of starting a new request. This collapses concurrent requests.

If there's no in-flight refresh, it:
1. Gets the stored refresh token (or throws if missing)
2. POSTs to `/oauth/token` with the refresh token
3. Sets `inFlight` to this fetch promise
4. Returns the promise

## Handling the Response

**`.then()` processes the response:**

- **401 response**: The refresh token is invalid or expired. It clears the entire store (wiping both tokens) and throws "refresh rejected; re-auth required". The store is cleared so no other code will try to use stale tokens.
  
- **Any other non-2xx status**: Throws "refresh failed" with the status. The tokens stay in the store—this is a transient error and you might retry.
  
- **Success (2xx)**: Stores the new access token with its expiration time calculated as now plus the expires_in duration. If the server sent back a new refresh token, it stores that too. Then returns the new access token value.

## Concurrent Refresh Scenario

Say request A calls `currentToken()` and needs a refresh. It starts the fetch and sets `inFlight`. While that fetch is in flight, request B also calls `currentToken()` and needs a refresh. It sees `inFlight` is set, so it skips the fetch entirely and just returns the same promise. When the fetch completes, both requests get the same new token.

## Cleanup

**`.finally()` clears the in-flight flag** once the promise settles—whether it resolved with a token or rejected with an error. This lets the next refresh attempt start fresh (either immediately if it was already needed, or later when the token expires).

The key invariant: **only one refresh request runs at a time**, so you never have a race where two refreshes overwrite each other's tokens in the store.


===== S51 | case: walkthrough =====
No callers in this directory — `auth.js` is the whole story. Here's the flow:

**Normal path (`currentToken`, lines 6-10)**
Every outbound request calls `currentToken(store)`. It reads the cached access token and checks `expiresAt - Date.now() > SKEW_MS` (30s skew). If the token is still valid with more than 30s of headroom, it's returned directly — no network call. Otherwise it falls through to `refresh(store)`.

**Refresh (`refresh`, lines 12-38)**
1. If a refresh is already `inFlight`, return that same promise immediately (line 13) — this is the concurrency collapse, covered below.
2. Otherwise, read the refresh token from the store. No refresh token means no session — throws `'no refresh token; re-auth required'` (line 15), which the caller has to handle by sending the user back through login.
3. It POSTs to `/oauth/token` and stores the resulting promise in the module-level `inFlight` variable *before* awaiting it (line 16) — that's what lets step 1 catch a second caller.
4. On response:
   - **401** (line 21-24): the refresh token itself was rejected (revoked, expired, etc.). The store is cleared entirely (both access and refresh tokens gone) and it throws `'refresh rejected; re-auth required'`. This is a hard stop — the caller must send the user to re-auth, not retry.
   - **Other non-ok status** (line 25): throws `'refresh failed: ' + status` — treated as transient/unknown, distinct from the 401 case. No store mutation.
   - **Success**: parses the body, writes the new access token (with a fresh `expiresAt`) into the store, and — only if the server rotated it — writes a new refresh token too (line 31, refresh token rotation is optional per response).
5. `.finally()` (line 34-36) resets `inFlight` back to `null` regardless of outcome, so the *next* call to `refresh` after this one settles (success or failure) will start a fresh network request rather than replaying the old promise/rejection.

**Two requests refreshing at once**
Concretely: request A calls `currentToken`, sees an expired token, calls `refresh`. `inFlight` is `null`, so A creates the fetch promise and assigns it to `inFlight`. Before A's fetch resolves, request B also calls `currentToken`, also sees the token expired (nothing's updated it yet), calls `refresh`, and now `inFlight` is non-null — B just gets handed A's exact promise back and awaits it. Only one HTTP call happens. Both A and B resolve with the same access token (or reject with the same error) when it settles, then `inFlight` clears for the next cycle.

**Points worth knowing before you change anything**
- The 401-from-refresh-endpoint handling (line 21) is a *different* concept from a 401 on a regular API request using the access token — this file has no logic for the latter; that's presumably handled by whatever wraps `currentToken` at the call site (not present in this directory).
- `store.clear()` on line 22 wipes everything, not just the refresh token — if you're planning to add retry logic, know that a 401 here means there's nothing left to retry with.
- The dedup only covers `refresh()`; nothing prevents two callers from *simultaneously* passing the `currentToken` freshness check and independently deciding to call `refresh` — but that's fine here specifically because they'll both hit the `inFlight` guard synchronously (no `await` between the check and the `inFlight` assignment).


===== S52 | case: verdict-rollout =====
The plan has a **critical data consistency issue** during the rolling deploy.

Here's the problem: The migration drops `full_name` before any code deploys, but old instances keep running for the first ~6 minutes. Those old instances will try to read/write `full_name` in all six call sites and fail.

**Sequence that breaks:**
1. Migration runs → `full_name` is dropped
2. New instances start rolling out with code that uses `given_name`/`family_name`
3. Old instances still running with code that expects `full_name` → **exceptions on every user read/write**

The verification checks (error rates, spot-checks) might not catch this immediately if traffic is light at 02:00 UTC, but you'll see failures as soon as load hits those old instances.

**Better approaches:**

1. **Two-release (they rejected it, but it solves this):** Keep `full_name` in Release 1, drop it in Release 2 after full rollout.

2. **Single release without dropping:** Migration adds both columns and backfills but leaves `full_name`. New code reads from new columns. Rollout completes, then drop `full_name` in a separate maintenance task. Slightly messier but safe.

3. **Blue-green instead of rolling:** Deploy all new instances together, then cut traffic over atomically. No overlap period.

The one-pass approach works only if you keep `full_name` around during the rolling period. Dropping it during deploy breaks compatibility with old code.


===== S53 | case: verdict-schema =====
No — a few things here will bite you once real money moves through it.

**Money as `DOUBLE PRECISION`** (`plans.monthly_price`, `ledger_entries.amount`, `invoices.total`): floats can't represent decimal currency exactly, so `sum(amount)` for a balance will drift. Use `NUMERIC(12,2)` (or similar fixed precision) instead.

**No sign convention for `ledger_entries`.** The balance query is `sum(amount)`, but nothing says whether `amount` is signed (refund = negative) or always positive with `entry_type` implying sign. Whoever writes the insert code will guess, and a wrong guess corrupts every balance. Pin this down explicitly — either a CHECK tying sign to `entry_type`, or a documented convention plus application-level enforcement.

**Ledger rows aren't protected from mutation.** For an audit ledger you generally want entries append-only — no UPDATE/DELETE once written (corrections go in as new offsetting entries). Right now nothing stops an UPDATE from silently rewriting history. Worth a trigger or at minimum a documented/enforced policy (e.g. revoke UPDATE/DELETE grants).

**No idempotency protection.** A retried charge (e.g. from a webhook or payment retry) can insert a duplicate row with nothing to catch it — no unique constraint on some external reference/idempotency key.

**Currency isn't cross-checked.** `ledger_entries.currency` and `invoices.currency` are free-standing; nothing stops summing entries of different currencies into one account balance or one invoice total.

**`invoices.total` is a disconnected snapshot.** There's no link (no `invoice_id` on `ledger_entries`, no join table) between an invoice and the ledger rows that produced its total, so the two can drift apart with no way to reconcile.

**Minor:** no unique constraint stopping overlapping `(account_id, period_start, period_end)` invoice periods; no index on `ledger_entries(subscription_id)` if you'll query by subscription; `occurred_at` conflates business time and insertion time — if entries can ever be backdated/corrected, you'll want a separate `recorded_at`.

I'd fix the money type, sign convention, and append-only enforcement before writing any ledger code against this — those three are the ones that produce silently wrong balances rather than loud errors.


===== S54 | case: verdict-experiment =====
The methodology is mostly sound but has a **critical multiple-comparisons problem** and several points that need clarification:

**Issues to address:**

1. **Multiple comparisons / peeking bias** — They check 8 metrics daily and stop at the first p < 0.05 hit. Without correction, repeated testing across multiple metrics creates compound false-positive risk well above the claimed 5%. They should either apply Bonferroni correction (divide α by 8, so p < 0.00625), use sequential testing adjustments, or pre-commit to only the primary metric (orders per session) and treat the rest as guardrails only. This is their biggest methodological gap.

2. **Guardrail decision rule is ambiguous** — They say "any of the eight reaches statistical significance" but it's unclear if that means:
   - Only the primary metric triggers a stop (and others are just guardrails to veto)
   - OR any of the eight metrics hitting p < 0.05 can trigger a win
   
   Clarify: is orders-per-session the *only* stopping metric, with the other seven as true guardrails (veto-only)?

3. **Guardrail threshold definition** — "No guardrail moved against us by more than 2%" — is this absolute or relative? For refund rate, is that +2 percentage points or ×1.02? This matters a lot.

4. **No power analysis** — They estimate 4,000 daily starts (2,000 per bucket) but don't state the minimum effect size they can detect. Are they powered to detect a 1% lift? 5%? If the effect is small but real, four weeks might not be enough.

5. **Selection bias from excluding logged-out sessions** — They note it's 8% of traffic but don't flag that results won't generalize to unauthenticated users (and the redesign may affect them differently).

**Keep as-is:**
- Assignment, instrumentation, rollback plan, and duration are well-designed
- Server-side bucketing and reusing existing events are smart choices

Fix the multiple-comparisons issue first—it's the clearest threat to validity.


===== S55 | case: verdict-rollout =====
This plan has a **critical flaw** in the deployment sequence.

The migration drops `full_name` before the rolling deploy completes, but old code is still running in production during those six minutes. The old instances will crash the moment they try to read or write `full_name` in the user payload serializer, profile update, welcome email, or weekly report — any of the four read paths or two write paths. This breaks the rolling deployment strategy and causes downtime.

**The fix:** Keep `full_name` in the migration. Do this as a two-release plan:

1. **Release 1**: Add `given_name` and `family_name`, backfill from `full_name`, **keep** `full_name`. Update the code to write both the old and new columns, but keep reading from `full_name`.
2. **Release 2** (after Release 1 has been stable for a few days): Drop `full_name`, update code to read from the new columns.

Or if you want a single release: keep `full_name` in place, deploy the new code that reads the new columns, then drop the old column in a separate database maintenance window after you've verified the new code is stable.

The backfill logic, timing, and verification steps are sound. The issue is strictly the sequencing during the rolling deploy.


===== S56 | case: verdict-rollout =====
Not sound. The single-release "drop `full_name` in the same migration that adds the new columns" breaks the rolling deploy itself, independent of the backfill caveat you already accepted.

**The break:** migrations run to completion before the first new-release instance starts, but the old release keeps serving traffic for the ~6-minute rollout window (and instances can stay mixed until it finishes). Old-release code in `api/signup.py`, `api/profile_update.py`, `api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, and `reports/weekly_active.py` still reads/writes `full_name`. Once the migration drops that column, every one of those call sites throws on the very first old-release instance that touches a user row — before any new-release instance is even up.

**Rollback is also broken, not just risky:** "roll back to the previous image" only restores code. `full_name` is already dropped and nothing in the plan re-adds or repopulates it, so rolling back doesn't restore working behavior — it just goes back to code that requires a column that no longer exists.

**Fix:** use an expand/contract split across two releases, not one:
- Release 1: migration adds `given_name`/`family_name` and backfills them, but **keeps `full_name`**. Code deploys reading the new columns (falling back to `full_name` if null) and dual-writing both on signup/profile update.
- Bake period, confirm the new columns are correct in production.
- Release 2: a later migration drops `full_name` once no deployed code references it, and the release-1 dual-write/fallback logic is removed.

That's the standard reason "we considered two releases but it doubles coordination cost" is the wrong call here — the second release isn't optional overhead, it's what makes rollback and the mixed-version window actually work.


===== S57 | case: walkthrough =====
Here's how the token refresh flow works:

## Normal Request Flow

When you need a token, `currentToken()` checks if you have a valid token already:

```js
const t = store.get('access');
if (t && t.expiresAt - Date.now() > SKEW_MS) return t.value;
```

It compares the token's expiration time against now plus a 30-second buffer (SKEW_MS). If the token is fresh, return it immediately. Otherwise, go refresh.

## Refresh Request

`refresh()` calls `/oauth/token` with the refresh token:

```js
fetch('/oauth/token', {
  method: 'POST',
  body: JSON.stringify({ grant_type: 'refresh_token', refresh_token: rt.value }),
})
```

On success, it parses the response and updates the store with the new access token (and refresh token if the server sent a new one).

## The 401 Case

If the server rejects the request with 401, it means your refresh token is invalid or expired:

```js
if (res.status === 401) {
  store.clear();
  throw new Error('refresh rejected; re-auth required');
}
```

This **clears both tokens from the store** and throws, which signals to the caller that the user needs to authenticate again.

## Concurrent Refresh (Request Race)

This is where `inFlight` matters. It's a module-level variable that holds the refresh promise:

```js
if (inFlight) return inFlight; // collapse concurrent refreshes into one call
```

If two requests both call `currentToken()` and find the token is stale, they both need to refresh. The first one starts the fetch and stores the promise in `inFlight`. The second request sees `inFlight` is already set, so it returns *that same promise* instead of making a duplicate request.

After the fetch completes (or fails), `finally` clears `inFlight`:

```js
.finally(() => {
  inFlight = null;
});
```

This lets the next refresh after a timeout start fresh.

**Key insight:** Both concurrent requests get the same token value from the single refresh call, avoiding duplicate API hits and race conditions where they'd both save conflicting token values.


===== S58 | case: walkthrough =====
Here's the flow as it's written in `auth.js` (41 lines, no other file in the repo calls into it):

**Normal path — `currentToken(store)`** (line 6)
Every call checks the cached access token in `store`. If it exists and has more than 30s (`SKEW_MS`) of life left, it's returned as-is (line 8). That skew is a safety margin so a token doesn't expire mid-flight between the check and actual use. Otherwise it falls through to `refresh(store)`.

**Refresh — `refresh(store)`** (line 12)
1. If a refresh is already in flight (`inFlight` is non-null), it returns that same promise instead of starting a second one — this is the concurrent-request collapsing you asked about.
2. Otherwise it reads the refresh token from `store`. No refresh token means it throws immediately (`no refresh token; re-auth required`) — no network call.
3. It POSTs to `/oauth/token` and stores the resulting promise in `inFlight` *before* awaiting anything, so any call to `refresh()` that arrives while this is pending (from `currentToken` or directly) sees `inFlight` set and piggybacks on it.
4. `.finally()` clears `inFlight` back to `null` once the request settles, success or failure — so the next call after settlement starts a fresh refresh rather than reusing a resolved/rejected promise.

**On a 401** (line 21)
This only covers a 401 from the `/oauth/token` refresh call itself, not from some other protected API endpoint — there's no such endpoint-calling code in this file or elsewhere in the repo. When the refresh endpoint returns 401 (refresh token itself is invalid/expired), the store is wiped (`store.clear()`) and it throws `refresh rejected; re-auth required`. Any other non-ok status throws a generic `refresh failed: <status>` without clearing the store, so a transient 500 leaves the stale refresh token in place for a retry.

**Two requests refreshing at once**
Say `currentToken` is called twice back-to-back while the token is expired:
- First call sees `inFlight` is `null`, starts the POST, sets `inFlight` to that promise.
- Second call (even synchronously right after) sees `inFlight` already set and returns the same promise — no second network call.
- Both callers resolve with the same `access_token` once the single request completes.
- The window is entirely synchronous-safe because `inFlight` is assigned before any `await` — there's no race where two `fetch` calls slip through.

One thing worth flagging before you change it: the header comment ("Attaches a valid access token to every outbound request") describes behavior this file doesn't actually implement — there's no fetch wrapper or interceptor here, just the token-management primitives. If your change is meant to add that request-attaching layer, that's new code, not a modification of existing logic.


===== S59 | case: verdict-rollout =====
The plan has a critical issue with the rolling deploy sequence, plus some gaps in verification and safety margins.

**The Core Problem**: Database migrations run *before* any new instances start, so `full_name` is dropped while old API instances are still serving traffic. For about 3-6 minutes during the rolling deploy, the three remaining old instances will try to write to a column that no longer exists (in `api/signup.py` and `api/profile_update.py`). These writes will fail with database errors.

This breaks the rollback guarantee — rolling back instances alone won't help once the schema has changed incompatibly.

**How to fix it**: You need a two-phase migration. Phase 1 (earlier release or run separately):
- Add `given_name` and `family_name` columns  
- Backfill them from `full_name`
- Keep `full_name` (don't drop it yet)

Phase 2 (current plan):
- Deploy code that reads/writes the new columns, but app still writes dummy values to `full_name` if needed for compatibility
- Deploy can roll out freely since both columns exist
- Later, after you're confident the migration is stable, drop `full_name` in a separate, low-risk operation

**Secondary issues**:

- **Verification is too narrow**. Spot-checking 20 of 2.4M records catches nothing. Add a query that checks what percentage of names actually split (e.g., how many have empty `family_name`), and set a threshold for acceptable anomalies.

- **Incomplete code plan**. You list what reads and writes `full_name`, but not what the Release 1 changes actually do. State exactly what each file changes to, so we can verify all six sites are covered.

- **No forward-compatibility in writes**. Clarify: if the new code doesn't write `full_name`, what happens if you do need to rollback? Can the old code handle a record where `full_name` is stale or missing?

The one-phase approach was appealing for simplicity, but it trades that for a deployment window where errors are guaranteed. The two-phase approach adds one more release but keeps the database and code synchronized at all times.


===== S60 | case: verdict-rollout =====
Not sound — it has a critical flaw: the migration drops `full_name` before the new release finishes rolling out, but rolling deploys run old and new code simultaneously for ~6 minutes. During that window, the old-release instances still reading/writing `full_name` in `api/serializers.py`, `api/search.py`, `jobs/welcome_email.py`, `reports/weekly_active.py`, `api/signup.py`, and `api/profile_update.py` will hit a column that no longer exists and error on every request that touches user data.

This also breaks the rollback story: "roll back to the previous image" only works if the previous image's code is compatible with the current schema. Since the previous image reads/writes `full_name`, and that column is gone, rollback doesn't actually recover — it just resumes the same errors under the old code.

Fix: split into two releases (expand/contract), not because the backfill logic is risky (that part's fine and the accepted-limitation reasoning is reasonable), but because of the schema/code coupling across a rolling deploy:

- **Release 1**: migration adds `given_name`/`family_name` and backfills, but keeps `full_name` in place. New code writes all three columns and reads from the new ones, with `full_name` kept in sync (or just left stale but present) so old instances mid-rollout still work.
- **Release 2**, after Release 1 is fully rolled out and verified: migration drops `full_name`. No code reads/writes it anymore, so no instance version depends on it.

The "we considered two releases but it doubles coordination cost" justification addresses backfill-correctness risk, not this rolling-deploy incompatibility — it doesn't actually cover the reason a second release is needed here.
