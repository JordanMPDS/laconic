# Round 16 — a survey is what you write when you have not looked

**Date:** 2026-08-12
**Rules under test:** `rules_cksum` 1497646142
**Baseline:** `evals/snapshots/loop/round-01-n10-v4.json`
**Round artefacts:** `evals/snapshots/loop/round-16.json`,
`round-16-judgments.json`. No preferences file: see "What did not happen".
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

---

# Results

**Reject.** The scoped target moved 31 to 28 against a registered threshold of
18. Edit reverted; master stays at 1830906901.

```
verdict: reject (target quality_fails on design-cache, design-realtime,
                 design-upload, against round-01-n10-v4.json)
  REJECT: quality_fails 31 -> 28 on design-cache, design-realtime,
          design-upload, p = 0.397 (round-wide 83 -> 74)
```

No fatal counter rose. Every round-wide number moved the right way or held:

| metric | `-v4` | **r16** | |
| --- | --: | --: | --- |
| `never_cut_failures` | 2 | 2 | held |
| `quality_fails` | 83 | 74 | improved, p = 0.262, not the target |
| `safety_fails` | 4 | 4 | held |
| `violations_total` | 158 | **125** | improved, p = 0.029 |

## The registered prediction was right, and it is why the round failed

Written before the round: *"Most of the available room is on haiku. Three haiku
cells hold 26 of the 31 failures. An edit that only helps sonnet cannot reach
the target, and if that is what happens the round rejects and the write-up says
so."*

That is exactly what happened.

| cell | `-v4` | r16 | |
| --- | --: | --: | --- |
| `design-cache`/sonnet | 1 | **0** | |
| `design-realtime`/sonnet | 4 | **1** | |
| `design-upload`/sonnet | 0 | 1 | the tripwire, below |
| **sonnet subtotal** | **5** | **2** | |
| `design-cache`/haiku | 8 | 9 | |
| `design-realtime`/haiku | 10 | 10 | |
| `design-upload`/haiku | 8 | 7 | |
| **haiku subtotal** | **26** | **26** | **no movement at all** |

The entire scoped improvement is sonnet, and it is a real one:
`design-realtime`/sonnet went 4 to 1 against a measured master-rules rate of
45%, and `design-cache`/sonnet to zero. Haiku did not move by a single net
verdict.

## Why haiku did not move

Not wording. The judge's reasons under the edit are the same sentences as
before it:

> "The response recommends WebSockets/SSE and never checks PLATFORM.md or
> rollup.md constraints"

> "designs a new in-process/Redis cache layer without ever checking whether a
> CDN or middleware/security.js no-store header already exists"

> "proposes a new Redis/Memcached cache layer as the design and asks the user
> about their stack instead of reading the codebase"

**A rule that says "read the code first" does not make a model read the code.**
On these fixtures haiku answers design questions from convention regardless of
what the system prompt asks of it, and the three cells hold at 9 of 10, 10 of 10
and 7 of 10. `design-realtime`/haiku has now failed 50 of 50 across the rate
measurement and this round.

That is a capability boundary rather than a rules defect, and it is the useful
thing this round establishes. It also means the scope as registered was
unreachable: with haiku immovable, the best attainable scoped count was 26, and
18 was never available. **The threshold was registered honestly and it was
registered wrong**, which is worth more in the record than a target chosen to be
clearable.

## The tripwire fired, and did not reject

`design-upload`/sonnet went 0 to 1, exactly the 1-in-10 risk registered in
advance against its measured 0 of 40. It did not cause a fatal rejection,
because the fatal loop only enters when the round-wide counter **rises**, and
round-wide `quality_fails` fell 83 to 74. The screen was never consulted.

Worth stating plainly, because it is a property of the gate rather than of this
round: **a zero-rate tripwire only bites in a round whose round-wide total is
already going the wrong way.** In a round that improves overall it is silent.

## The [#88] strata disclosure, first live use

```
quality strata (disclosure, not a gate): answers that hand a decision back
22 of 47 -> 28 of 44, answers that resolve it 61 of 233 -> 46 of 236; the two
strata moved in OPPOSITE directions, which a flat quality count hides - the
hands-back stratum got worse
```

| stratum | `-v4` | r16 |
| --- | --: | --: |
| answers that hand a decision back | 22 fail of 47 (47%) | 28 fail of 44 (**64%**) |
| answers that resolve it | 61 fail of 233 (26%) | 46 fail of 236 (**19%**) |

**This is round 15's shape again, and this time it was visible in the same
round rather than found afterwards.** The edit made resolving answers better and
asking answers worse, and round-wide `quality_fails` improved because most
answers resolve.

The edit's closing sentence — *"Ask the user only for what the code cannot
answer"* — was written to suppress exactly this. It did reduce how often answers
ask, 47 to 44 of 280, but among the answers that still asked the failure rate
went up sharply. The reading this round supports: the models that ask are
overwhelmingly the ones that did not read, so the instruction to ask less does
not help them; it removes the question without adding the reading.

[#88] part B paid for itself on its first round.

## What did not happen

**The edit did not shorten design answers.** The registered secondary
observation expected a survey collapsing into one recommendation to be shorter.
Over the ten older design cells the median token shift is **−152 with 6 of 10
cells down, sign test p = 0.754** — indistinguishable from no change, and far
inside any noise floor. It is disclosed here because it was registered, not
because it means anything.

**Preference was not run.** The round rejects on a deterministic gate, and
preference may neither reject an edit that passed every deterministic gate nor
rescue one that failed. 440 comparisons would have bought no decision, so they
were not bought. No preference number is claimed anywhere in this round.

**No replication and no holdout.** Both are step 8 and step 9, and step 7
rejected.

## What this round establishes

1. **Design-answer grounding is model-dependent in a way no rule text reaches.**
   Sonnet responds to the instruction; haiku does not. Any future [#46] work
   that scopes a quality target across both models is scoping a target that
   cannot be hit, and the scope should say which model it expects to move.
2. **The strata disclosure works.** It caught in one round the pattern that cost
   round 15 a replication and a holdout to discover.
3. **The mechanism is real and the rule is partially right.** Sonnet's three
   scoped cells went 5 to 2 while nothing else regressed and readability
   improved by 33 violations. That is not enough to accept, and it is a
   different result from "the edit did nothing".

The edit is reverted. What it would take to try again is a scope naming sonnet
cells only, registered as such in advance, and that decision belongs to a
separate round rather than to a re-score of this one.

## The outage, and what it cost

Third service outage in two days. The first generation pass returned **166
failures in 440 runs**; the shards were resumed and returned **440 usable, 0
failed, 0 duplicate keys** ([#61]). Judging then ran with **0 infrastructure
failures** and carried 660 control verdicts ([#83]), so it made 440 calls rather
than 1100.

Generation ran one case per process at 5-way concurrency, which is a change from
previous rounds and is recorded in the snapshot's `metadata.sharded`. Each
process owns its own file, so nothing races on a write, and the shards were
merged into `round-16.json` afterwards.

[#61]: https://github.com/JordanMPDS/laconic/issues/61
[#83]: https://github.com/JordanMPDS/laconic/issues/83
