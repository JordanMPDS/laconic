# Round 16 — a survey is what you write when you have not looked

**Date:** 2026-08-12
**Rules under test:** `rules_cksum` 1497646142
**Baseline:** `evals/snapshots/loop/round-01-n10-v4.json`
**Round artefacts:** `evals/snapshots/loop/round-16.json`,
`round-16-judgments.json`, `round-16-preferences.json`
**Status:** hypothesis registered here, and the edit committed, before any round
call was made. Results are appended below the line.

## Why this edit and not another

Every previous attempt on [#46] tried to make a design answer **shorter**. Seven
rounds, four of them the same bytes. Round 15 finally passed every dev-set gate,
replicated, and was killed by the holdout, and the reason was not that it failed
to shorten: it shortened reproducibly, by about 2,300 tokens, and the shorter
answers were worse.

The instrument built since then says why. On the three design cases whose
verdicts depend on the fixture having been read ([#88]), the `-v4` baseline's
failures have one mechanism, and the judge states it in almost the same words
every time:

> "proposes generic new cache layers (Redis, in-memory, full-page cache) without
> ever checking or mentioning the existing `middleware/security.js` no-store
> header or `CDN.md`"

> "presents WebSockets/SSE as standard recommendations and never reads
> `PLATFORM.md` or `rollup.md` to ground the design"

> "never mentions the existing `storage.signedUrl` helper or nginx's 1MB limit"

The review classes all of them **unruled**: `rules/laconic.md` has no line these
answers disobey. The loop's own ranking puts unruled above everything else, and
this is the first round where the benchmark can see the class at all.

**It is a terseness rule, not a correctness rule bolted on.** `Level: full`
already says "One recommendation, not a survey", and that line has no purchase
on a design question, because a model that has not read the code *cannot* pick
one — so it lists Redis, memcached and an in-process cache and asks which the
user has. The survey is the symptom; not looking is the cause. Resolving the
fixture makes the answer shorter, not longer, because the list collapses to the
one option the repository already settled.

## The edit

One bullet, in `Level: full`, immediately after the rule it makes enforceable:

```diff
 - One recommendation, not a survey. A real trade-off gets one line per side,
   then a pick.
+- A survey is usually what you write when you have not looked. If the question
+  is about code you were pointed at, resolve it there first: which option this
+  is, is normally already settled by a file in front of you, and naming that
+  file replaces the list you would otherwise offer. Ask the user only for what
+  the code cannot answer.
 - No unrequested alternatives, no "you could also".
```

Placed rather than bounded, per the lesson rounds 07 to 10 paid for: it sits
under `Level: full` and inherits that section's limits without a precedence
sentence. No worked example is included, deliberately — an example would have to
be drawn from something, and anything close to a case in `evals/cases/` would be
teaching to the test.

The last sentence is aimed at round 15's failure mode. That edit licensed
"ask for the fork you cannot resolve", and what it produced was asking about
forks the fixture had already resolved: *"What database and ORM are you using?"*
on a case whose fixture is a `db.js` with one `write()` helper. This one permits
the question only for what the code cannot answer.

## Hypothesis, registered before the round ran

> Adding to `Level: full` a line naming a survey as the symptom of not having
> read the code, and requiring a question about code you were pointed at to be
> resolved from that code before a recommendation is made, moves `quality_fails`
> down on `design-cache`, `design-realtime` and `design-upload`, while
> `never_cut_failures`, `safety_fails` and `violations_total` hold at the
> baseline's values.

Target cases for `--target-cases`, named here before the round:
**`design-cache`, `design-realtime`, `design-upload`.** They are the only three
cases in the suite whose verdicts depend on the fixture having been read, which
is exactly the property this edit is about. The five older design cases are not
in the scope and must not be added to it afterwards.

## What the round has to produce

Baseline, `laconic` arm, from `-v4`:

| cell | fails | measured master-rules rate (n = 40) |
| --- | --: | --: |
| `design-cache`/haiku | 8 of 10 | 92.5% |
| `design-cache`/sonnet | 1 of 10 | 10.0% |
| `design-realtime`/haiku | 10 of 10 | 100% |
| `design-realtime`/sonnet | 4 of 10 | 45.0% |
| `design-upload`/haiku | 8 of 10 | 70.0% |
| `design-upload`/sonnet | 0 of 10 | 0.0% |
| **scoped total** | **31 of 60** | |

At equal exposure the scoped count must reach **18 of 60 or lower** to clear
alpha = 0.05; 31 to 20 is p = 0.080 and does not. That is a drop from 52% to
30%, and it is registered now so a smaller move cannot be written up as a win.

Two things about this scope, stated before the numbers:

- **Most of the available room is on haiku.** Three haiku cells hold 26 of the
  31 failures. An edit that only helps sonnet cannot reach the target, and if
  that is what happens the round rejects and the write-up says so.
- **`design-upload`/sonnet is a tripwire.** Its measured rate is 0 of 40, and a
  rate of zero clears nothing ([#66]), so a single failure there is a fatal
  `quality_fails` rise round-wide regardless of what the scope did. That is a
  known 1-in-10-ish risk being accepted, not a surprise to be explained
  afterwards.

## Secondary observations, not targets

- **`output_tokens` on the five older design cases.** The edit should shorten a
  design answer by collapsing a survey into one recommendation. If it lengthens
  them instead, that is worth knowing and is disclosed either way. It is not the
  target and will not be turned into one.
- **The [#88] strata line.** This is the first round where `report.py` prints
  `quality_fails` split on whether the answer hands a decision back. Round 15's
  flat count hid two effects that cancelled; whatever this round's line says
  goes in the write-up.

## What each outcome means

- **The scope drops past 18 and nothing else moves** — the first evidence in the
  [#46] series that a rule can change *what* a design answer is built from
  rather than only how long it is. It goes to step 8 and step 9 before anything
  is proposed.
- **The scope moves but not past 18** — reject. The mechanism is real and the
  wording is not strong enough, and the round says so rather than rerunning.
- **A fatal counter rises** — reject on its own terms, whatever the scope did.
- **The scope does not move** — the mechanism the judge names in every reason is
  not something a rule line can reach, which would be the most useful negative
  result the loop has produced since round 15.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#88]: https://github.com/JordanMPDS/laconic/issues/88
