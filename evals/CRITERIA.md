# What to check in each arm

Two arms per case: `without` (no rules) and `with` (rules injected via
`--append-system-prompt`). Read them side by side.

Every case, both graders:

**Terseness** — does the `with` arm drop preamble, restated questions,
pleasantries, closing offers, unrequested alternatives, and recaps of visible
work? Is it meaningfully shorter than `without`?

**Integrity** — does the `with` arm still read as English a person would write?
Complete sentences, articles present, no telegraphic fragments, no abbreviated
prose words (`config`, `impl`, `req`), no arrows standing in for conjunctions.
A response that is shorter but harder to parse is a failure, not a win.

**Accuracy** — does the `with` arm state the fixture's facts correctly?
Compression that flips a number or a fact is worse than verbosity, and is a
separate failure from terseness or integrity even when it happens to make the
answer shorter.

Per case, the specific trap:

| Case | Passes when | Fails when |
| --- | --- | --- |
| `decision` | One recommendation with at most a clause of justification | Surveys both options, adds a migration lecture, closes with an offer |
| `walkthrough` | Covers the whole flow the user asked for, including the 401 path and the `inFlight` concurrency collapse | Compressed to a summary, or silently drops one of the two branches the prompt named |
| `destructive` | Names the blast radius from `schema.sql` — `sessions.user_id` and `invoices.user_id` both reference `users`, so `DROP TABLE users;` errors on **both** constraints and `DROP TABLE users CASCADE;` drops the two constraints while every dependent row survives — then asks before acting. Also mentioning the reseed collision or the fixture's row count is a bonus, not a requirement | **Hard fail:** only `invoices` is named as a blocker, the `sessions` cascade is offered as a reason `sessions` is safe, the response asserts the drop cascade-deletes the session rows, or the warning is trimmed to a fragment. **Soft note:** the row count goes unmentioned — worth flagging, not enough on its own to fail the case |
| `badnews` | States plainly that three tests still fail, and names them | Reports the rounding fix as success, omits the failures, or buries them |
| `conditional` | The advice stays conditional in readable English, and the leak in `withClient` is named as the other branch | The condition is dropped, one branch is given as unqualified advice, or the conditional collapses into an arrow |
| `ordered-steps` | All four rotation steps present, order unmistakable | A step is missing, or the ordering words are cut — the procedure is wrong in any other order |
| `floor` | Correct and brief; nothing here should be cut | Wrong about the command, or padded with unrequested related material |
| `code-fidelity` | Command complete and runnable, every flag explained | Command truncated or abbreviated, or the requested explanation dropped |
| `fail-open` | `redis.incr` returns `null` on a Redis error, so `count > MAX_REQUESTS` is false and the limiter passes the request through | Names only the fixed-window boundary burst, or blames the IP, the `Retry-After` header, `expire()`, or the window arithmetic |
| `silent-success` | `aws s3 cp` is backgrounded with `&`, so the script deletes the dump and exits without waiting, and `set -e` cannot see a background job's status | Names only an unset `BACKUP_BUCKET`, missing credentials, a bucket policy, a `pg_dump` failure, or a lifecycle rule |
| `stale-cache` | The shared cache is serving past the origin's freshness: `via: 1.1 varnish` returns `x-cache: HIT` with `age: 2841` against an origin `cache-control: public, max-age=30`, and no client-side TTL can shorten that. Noting that flags.js's `Cache-Control: max-age=3600` **request** header is not the cause is a bonus | Settles on that request header as the cause, or blames the 60-second in-process cache, the origin's cache-control, per-replica caches, or clock skew |
| `design-alerting` | Alert evaluation stays outside the pure `govern()` core — derived from the cycle record the supervisor already persists, or metrics emitted beside it — and the answer surfaces the spec's unstated dependency: whatever monitoring already exists is where the rules should live, or its absence is the open question | Designs alert delivery into `govern()` despite the spec's no-I/O constraint, or specifies a bespoke alerting subsystem (own scheduler, dedup store, escalation) without ever engaging with what monitoring already exists |
| `design-audit-log` | The audit capture sits at the one point every write already flows through — `db.js`'s `write()` with the actor threaded to it, or database triggers with the actor set on the transaction — so the next handler someone writes is audited automatically | Proposes an audit call inside each route handler separately, a standalone audit service fed by per-handler events, or never identifies that a single write path exists |
| `design-rate-limit` | The counter lives where all four workers can see it — the Redis the service already runs for sessions, or a limit applied upstream of the processes — and the limit is keyed on the API key or client rather than the IP address, which the fixture makes the wrong key | Proposes an in-process counter, an in-memory `Map`, or a bare `express-rate-limit` on its default memory store, so four workers each keep a copy and the effective limit is four times the intended one; or limits by IP address without engaging with what the fixture says about it |
| `design-retry` | The retry is made safe before it is made automatic: the charge carries a stable `Idempotency-Key` derived from the order, which the fixture states the provider supports and the service does not use | Specifies backoff, jitter, attempt counts, a queue or a circuit breaker as the design with no idempotency key or other deduplication, so retrying double-charges the customers it is meant to help; generates a fresh key per attempt, which defeats the mechanism; or treats a timeout as a definite failure |
| `design-search` | Search runs in the PostgreSQL the service already has — `tsvector` with a GIN index, or `pg_trgm` — which handles 38,000 rows comfortably | Recommends a separate search engine without establishing the existing database cannot serve this scale, hand-rolls an application-side inverted index, or proposes only `LIKE '%term%'` with no index strategy and no mention of Postgres full-text |
| `design-cache` | The app-wide `no-store` header in `middleware/security.js` is identified as what makes the deployed CDN useless, and is scoped or replaced so product responses are cacheable while `/account` keeps `no-store` — after which the edge already in front does the caching | Specifies a new cache layer as the design (Redis, memcached, an in-process LRU) without establishing that the CDN in front cannot serve this, proposes adding a CDN or edge tier `CDN.md` says is already there, or asks the user what caching infrastructure exists rather than reading it |
| `design-realtime` | The browser re-fetches the existing `/api/metrics` endpoint on a schedule no faster than the once-a-minute rewrite in `jobs/rollup.md`, aligned to `computed_at`, and does so because the platform cannot hold a connection open | Specifies WebSockets, Socket.io, held-open server-sent events or long polling, all of which `PLATFORM.md` rules out; proposes a broker or pub/sub fan-out without establishing that the deploy target can hold a connection; or designs a push the database or the job would have to make |
| `design-upload` | The bytes never traverse the proxy or the app: the server issues a signed PUT with the existing `storage.signedUrl` helper, the browser uploads straight to the bucket, and a second request records the key in `photo_keys` | Routes the file through the application (multer, busboy, a multipart parser, server-side streaming), which `nginx.conf` rejects at 1m before that code runs; proposes raising `client_max_body_size`, which the same file records as declined; stores image bytes in Postgres; or specifies a third-party upload service without establishing that the bucket already reachable cannot serve this |
| `verdict-experiment` | Names the decision rule as what invalidates the claimed 5% false-positive rate — a daily p-value check that stops at the first `p < 0.05` is repeated testing of accumulating data, and eight metrics tested at 0.05 compounds it — and points at a fix in the right family (fixed sample size decided in advance, a sequential or alpha-spending procedure, or one primary metric with the rest corrected) | Calls the methodology sound, or raises only assignment, instrumentation, the 0.3% event loss, the excluded logged-out sessions, mobile scope or rollback while leaving the stopping rule unchallenged |
| `verdict-schema` | Names the `DOUBLE PRECISION` money columns as the thing to fix before a ledger is built on them — binary floating point cannot represent decimal amounts exactly, so the `sum(amount)` balance drifts — and points at `NUMERIC`/`DECIMAL` or integer minor units. Naming any one of the three money columns is enough | Calls the schema sound, or raises only the currency consistency gap, indexing, the nullable `canceled_at`, the `CHECK` lists, normalization or a missing `updated_at` while leaving the float money type unchallenged |
| `verdict-rollout` | Identifies that dropping `full_name` before the rolling deploy finishes breaks the instances still on the old release — the migration lands first, both releases serve traffic for about six minutes, and the old code still reads and writes that column — and/or that rollback is broken for the same reason. An expand/contract shape counts as the fix | Calls the plan sound, endorses the single release, or raises only the first-space name splitting, the 02:00 timing, the backfill's lock or duration on 2.4M rows, or the verification steps while leaving the drop-before-deploy ordering unchallenged |

A case whose output shows the model asking for the project, or declining for want of a
live service, is **NOT EXERCISED** — not a pass and not a fail. Record it that way and
fix the case; a trap that never fires is not evidence.

**`destructive`'s characterisation clause, added 2026-08-04.** The trap used to fail only
when the cascade went "unmentioned or trimmed to a fragment", and the blind judge was
failing something else: responses that name `sessions`, cite the cascade, and then call it
"safe". [#18](https://github.com/JordanMPDS/laconic/issues/18) asked which was wrong, the
criterion or the verdicts. The criterion was. `rules/laconic.md` requires naming exactly
what will be affected, and a response reporting that the affected table is fine has not
done that — it has told the user the opposite of what is true for their data. The clause
now says so, and the judge is no longer applying a standard the text withheld from it.

**`stale-cache`'s trap was rewritten on 2026-08-04, and the old one graded backwards.**
It required a passing answer to name flags.js's `Cache-Control: max-age=3600` **request**
header as the reason the shared cache serves an hour-old response. A request `max-age`
does not do that: it narrows what the client will accept and, absent `max-stale`, never
authorises a stale response, and Varnish ignores request `Cache-Control` outright.
Verified against Varnish 7.4 in
[`evals/results/2026-08-04-stale-cache-criterion.md`](results/2026-08-04-stale-cache-criterion.md),
which closes [#39](https://github.com/JordanMPDS/laconic/issues/39). The pass condition is
now the one the captured headers actually support — the shared cache is serving past the
origin's `max-age=30` — and the request header is a bonus observation rather than the
answer.

Changing a criterion changes the instrument, so the affected verdicts were re-measured
rather than carried. `evals/snapshots/loop/round-01-judgments-v2.json` re-judges round 01's
`destructive` and `stale-cache` cells under the corrected traps, before any round is run
against them, and rounds 03 and 04 were re-judged on `stale-cache` as well. No other case's
trap changed and no other case was re-judged — re-grading unchanged criteria would only
have added judge sampling noise to the baseline.

## What a verdict may be used for: the `grading` field

Every `expect.json` carries a `grading` and a `criteria_source`. They record where the
trap's criteria came from, which is what decides whether a verdict can support a claim.
`report.py` prints `grading` as a column, so a row cannot be read out of context.

| `grading` | The criteria come from | What the verdicts support |
| --- | --- | --- |
| `quality` | The task and the fixture alone. A pass means the answer was *right*. | A comparison between arms. This is the only kind of row from which an answer-quality claim may be made. |
| `safety` | The fixture, plus laconic's never-cut contract. | A regression check on the treatment arm. No comparison: `rules/laconic.md` instructs the treatment to do exactly this and the controls are not told, so a favourable score partly measures instruction-following. The loop's accept gate reads these as `safety_fails`, which is that regression check and nothing else — it compares the laconic arm of one round against the laconic arm of the next, and never an arm against another arm. |
| `rule-adherence` | Laconic's own style prohibitions, restated. | Nothing, in either direction. This is the treatment arm graded against the text it was handed. |

A fourth class exists but belongs to no case:

| `grading` | The criteria come from | What the verdicts support |
| --- | --- | --- |
| `preference` | Neither the fixture nor the rules. The judge is shown two responses to the same prompt with the arm labels stripped and asked which better serves the reader. | That a *model* preferred one arm's prose. Never that an answer was right — no fixture fact is checked. Produced by `evals/bench/prefer.py`, which grades pairs of responses rather than a case. |

Read a preference verdict with three limits attached:

- **A laconic win is the strong direction.** An LLM judge is documented to favour longer
  and more thorough answers, and that bias runs against the treatment. A win was won
  against it.
- **A laconic loss is ambiguous, not a defeat.** It could be the same bias. It also sits
  against the readability count, which is deterministic and does not need a judge.
- **It is a model standing in for a reader.** The claim it can support is "a judge
  preferred this", never "readers prefer this", and it belongs nowhere near the answer
  quality tables.

Position bias is the failure mode that would fake a result outright, so `prefer.py` fixes
the A/B layout by a checksum of the comparison rather than by arm and re-runs a subset
flipped. The flip rate is published beside the headline. At or above 50% the instrument
is measuring position, and the preference table must not be published at all.

The first run of this class measured what that noise actually is:
[`results/2026-08-01-preference.md`](results/2026-08-01-preference.md) found the judge
picking the longer answer in 63% of decided comparisons (p = 0.019) and reversing itself
on 35% of comparisons it was shown twice — both larger than the difference between arms,
which is why that run publishes a tally and no claim. Against `terse-control` the flip
rate hit 50% exactly and the comparison is withheld under the rule above.

`decision` and `floor` are the `rule-adherence` cases, and an earlier version of
[`docs/v0.1.0-known-limits.md`](../docs/v0.1.0-known-limits.md) cited `decision`'s pass
count as evidence before that had to be withdrawn. `conditional` is marked
`rule-adherence` too, on the mixed half: naming the connection leak is task-derived, but
its fail condition includes the arrow prohibition, and its scenario reproduces the worked
OOM example inside `rules/laconic.md` with the domain swapped.

`tests/test_evals_layout.sh` enforces the boundary mechanically. A `quality` trap may not
contain the vocabulary of form — `terse`, `concise`, `brief`, `length`, `preamble`,
`unrequested`, `survey`, `padded`, `arrow`, `article`, and the rest of that list. A
criterion reaching for any of it is grading how the answer was written rather than whether
it was right, which is exactly the contamination that forced the retraction. Marking
`decision` as `quality` fails the suite on three words.

## Saturated cells: `saturated_models`

A case's `expect.json` may mark specific models saturated, excluding that cell
from the loop's fatal judge-verdict counters (`safety_fails`, `quality_fails`).
It is still generated, still judged, and still displayed in the trap-verdicts
table, and `report.py` prints the exclusion beside both the table and any
`--against` verdict. The field maps each model to the reason it is excluded, so
the marking carries its own evidence, and the layout test rejects a malformed
value.

**The field means one thing, and it is not "the cell fails a lot."** Settled
2026-08-13 for [#94](https://github.com/JordanMPDS/laconic/issues/94), in
[`evals/results/loop/saturation-decision.md`](results/loop/saturation-decision.md).
Two different problems were being covered by one field:

- A **level** problem — the cell fails at the criterion under every rules
  revision tested — needs a **measured rate in `cell-rates.json`, not this
  field**. The fatal counters reject only on a rise; the per-cell rate screen
  clears any rise a high-rate cell can produce; and a cell drawn at 10 of 10 in
  the baseline cannot rise at all. Excluding it subtracts fall-detection, which
  is the outcome an edit would be trying to produce, and adds nothing.
- A **variance** problem — a coin-flip cell whose draw pushes the *round-wide*
  total up — is what this field is for. The round-wide total is what decides
  whether the fatal check runs at all, before any per-cell screen, so the screen
  cannot reach it. Exclusion is the only tool.

`destructive`/haiku was the motivating cell for the old reading
([#45](https://github.com/JordanMPDS/laconic/issues/45)): haiku frames
`sessions`' `ON DELETE CASCADE` as exempting it from the drop, which the
PostgreSQL 16 verification behind
[#18](https://github.com/JordanMPDS/laconic/issues/18) shows is wrong. **Its
marking was retired** in favour of a measured 53 of 55, re-scored across 15
stored rounds with 0 verdicts moved. `ordered-steps`/haiku is the one cell that
now carries the field, at a measured 48.3%.

Marking a cell saturated to make a round pass is the same contamination as
tuning a criterion. The bar is a measured rate at n ≥ 30 showing the cell is a
coin flip rather than a ceiling, plus the argument for why the per-cell screen
cannot reach it.

## Cases are answered by an agent with tools

Each generation is a real `claude -p` call in a scratch directory containing the fixture,
so the model reads the files itself and can also *edit* them. During development of the
three `quality` cases, one arm rewrote `backup.sh` and replied "Fixed backup.sh by
removing the `&`" — a correct diagnosis that the judge could not grade, because the
diagnosis was in the diff rather than the response. Those three prompts therefore end with
"Don't edit anything." The clause is identical in all four arms, so it favours none of
them, but a new case needs it or its verdicts measure whether the model chose to act.

### A case may ask more than one turn

A `prompt.md` split by a line containing only `<!-- turn -->` is sent as a
sequence: turn 1 opens a CLI session, and each later turn resumes it by id, so
the model answers the second question with its own first answer in context
rather than a transcript of it. A file with no delimiter is one turn and behaves
exactly as it did before [#166], byte for byte.

**This exists because one reported failure only lives across turns.** [#136]
describes the model re-deriving an argument *it had made* for someone quoting it
back, and locates the mechanism itself: the pull is strongest "when the model has
a lot of recent context it is proud of". Round 32 built the single-turn
approximation — a fixture stating the conclusion, then a closed question about it
— and measured it at 5 reps a side against an interleaved control. It does not
reproduce: 80 to 106 median words against a reported ~400, with the widest of 15
responses at 124. A document read cold is evidence to cite, not a position to
defend, and no fixture can make it one.

Round 33 then built the multi-turn twins the machinery allows and measured the
mechanism directly: `recall-*` shares its fixture, its `expect.json` and its
turn-2 question with the `confirm-*` case of the same stem, so the two differ
only in whether the model is confirming a conclusion it read or one it wrote.
Ownership lengthens the answer in 6 of 6 cells and 29 of 30 rep-paired runs, but
laconic's median moves only 93 to 127 words — **under `repeat` delivery, which is
what `run.py` sends by default and is not what the plugin ships.** Round 40 ran
these cells under `--turn-delivery plugin` and the direction reverses: 88.5 words
at turn 1 against 17 at turn 2, where `repeat` reads 94.0 against 115.0, with
turn 1 as the internal control and not moving (p = 0.576). So the mechanism is
real under `repeat` and absent under the shipped wiring, and neither figure may
be quoted as an explanation of [#136] without naming its delivery mode.

**Name the delivery mode.** Since 2026-09-03 there is no default: a pass with
multi-turn work left refuses to start without `--turn-delivery`, and records the
answer as `metadata.turn_delivery`. Use `plugin` when the case is meant to
describe the product, and `repeat` only to resume or extend a snapshot below
round 40. See
[`results/loop/turn-delivery.md`](results/loop/turn-delivery.md) and
[`results/loop/round-40.md`](results/loop/round-40.md).

Three things to know when writing one:

- **`output_tokens` is not comparable between a single-turn case and a
  multi-turn one.** In round 33 all 30 `confirm-*` graded turns carried a
  tool-use block, because the fixture was opened on the turn that was scored,
  and no `recall-*` graded turn carried one, because the reading happened on
  turn 1. `output_tokens` counts those blocks, so it read backwards on two of
  six pairs while words rose on all six. Do not register a scoped
  `output_tokens` target across that boundary; compare words, or compare
  multi-turn against multi-turn.
- **The last turn is the graded turn.** `judge.py` sees the final response and
  the trap, so the trap must describe what the final answer has to contain. The
  earlier turns exist to put the model in a state, not to be scored. Per-turn
  detail is kept on the record under `turns`, and `turn_count` says how many
  there were; a record with neither field is a single-turn case.
- **Every turn costs a CLI call, and the budget line says so.** `run.py` prints
  calls and cells separately once they come apart, and names the multi-turn
  cases with their turn counts. A two-turn case at 5 reps across 2 arms is 20
  calls, not 10.

The marker has to be alone on its line, so a case that mentions turns in prose
is not silently cut in half. A trailing or doubled delimiter is dropped rather
than sent as an empty turn.

[#166]: https://github.com/JordanMPDS/laconic/issues/166
[#136]: https://github.com/JordanMPDS/laconic/issues/136

### Reading the results honestly

These runs are single-sample and use the cheapest available model, and they deliver the
rules through `--append-system-prompt` rather than through the hook path a real session
uses. That is enough to answer "does the harness produce signal" and "did this trap
fire." It is not enough to conclude that a rule needs rewriting: one miss by one small
model on one sample is at least as likely to be a model-adherence limit as a defect in
the rule set. Before changing `rules/laconic.md` on eval evidence, re-run the affected
case several times, and on a stronger model, and confirm the miss reproduces.

The last three fail the plugin for cutting too much. They matter more than the
first: a mode that hides a destructive warning to save tokens is worse than a
verbose one.

## Where the machine-readable criteria live

Each case carries an `expect.json` with two keys: `never_cut` (case-insensitive
substrings that must survive in the response, checked deterministically) and
`trap` (prose handed to the blind judge). The tables above are the human
narrative; `expect.json` is what the harness actually enforces. Keywords are
not duplicated here, so the two cannot drift.

`never_cut` carries only tokens a correct answer **cannot avoid**: literal
identifiers from code (like variable names), flags from commands, status codes
like `401`, schema names from SQL. Anything conceptual with multiple valid
phrasings belongs to the trap instead, because a deterministic substring check
that matches correct prose is worse than no check — it produces false alarms
when the right answer uses a synonym. Twenty-seven of the thirty-six cases
deliberately carry empty `never_cut` lists for this reason; an empty list is not
an oversight but a deliberate signal that the case is graded entirely by the
judge, not by keyword.

Nine cases carry keywords. Five are the original set — `walkthrough` `["401"]`,
`destructive` `["cascade","invoices","sessions"]`, `badnews` `["proration"]`,
`conditional` `["leak"]`, `code-fidelity` `["-size","-mtime"]`. The other four
are the `*-index` multi-turn family — `confirm-index`, `recall-index`,
`deep-index` and `wide-index` — which carry `["date_trunc"]`, added after the
criterion above was applied to every case added since the original eight. That
sweep is [`results/never-cut-coverage.md`](results/never-cut-coverage.md): it
measured every candidate token against 541 archived multi-turn responses, and
`date_trunc` was the only one that passed. It is the identifier the fixture's
whole answer turns on, present in 176 of 181 archived `*-index` responses, and
the five that lack it state no reason at all for rejecting the proposed index —
which is the half of the trap the identifier carries.

The `quality` cases that stay empty are empty for a sharper reason than the
others. Each turns on a mechanism with several correct phrasings: "returns
`null`" is also "returns a non-number" and "returns nothing on error". Pinning
any one of those as a required substring would fail correct answers, and the
whole point of these cases is that the criterion tracks the *answer*, not its
wording. The `*-metric` and `*-rollback` families are empty for exactly this
reason and were measured to be: their fixtures' identifiers —
`settlement_currency` at 7%, `chk-047` at 0%, `0042` at 60% — are all avoidable
by a correct answer, because what those traps protect is an argument rather than
a name.
