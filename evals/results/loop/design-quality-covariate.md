# Why the dev set reported the opposite of the holdout in round 15

**Date:** 2026-08-12
**Cost:** zero model calls. Everything here is computed from snapshots already
committed: `round-01-n10-v3.json`, `round-15.json`, and round 15's two holdout
arms.
**Status:** an instrument measurement. It changes no gate, and the covariate it
identifies may not be used to score a stored round.

## The question this answers

[`round-15.md`](round-15.md) closed on two readings it could not separate. The
edit halved design-answer length, the dev set's `quality_fails` **improved** 52
to 48, and the holdout's design case regressed hard in the same round:

> - The five dev design cases have been measured so often that the compression is
>   tuned to what their specific criteria reward.
> - Or design-answer quality is simply not what `quality_fails` measures on those
>   cases, and the holdout case's criterion is stricter in a way that matters.

**Neither.** The dev set detected the harm. The round-wide counter summed it
away.

## The dev set saw it, split one way

Scoped to the five design cases, laconic arm, master rules against the
relocation edit — 100 responses each side:

| | quality pass |
| --- | --: |
| master rules (`-v3` baseline) | 61 of 100 |
| the relocation edit | 61 of 100 |

Fisher p = 1.000. That is the number the gate read, and it is genuinely flat.

Now split those same 200 responses on one covariate — **does the answer hand a
decision back to the user rather than resolve it?** Operationally: the response
contains a line that is a question.

| | master rules | the edit | Fisher |
| --- | --: | --: | --: |
| answers that ask | 16 pass of 27 | **10 pass of 33** | **p = 0.036** |
| answers that do not ask | 45 pass of 73 | 51 pass of 67 | p = 0.071 |

Two real effects in opposite directions, of similar size, which cancel in the
total. The edit makes an answer that resolves the design decision *better*, and
an answer that hands it back *worse*, and it shifts more answers into the second
group.

That is not a subtle statistical artefact. It is the edit's own clause working
as written:

> Ask for the fork you cannot resolve.

Sampling the questions the edit-arm answers actually ask on the dev design
cases:

- "What database and ORM are you using?" — `design-audit-log`, whose fixture is
  a `db.js` with one `write()` helper.
- "What's your current tech stack and how many products are we talking about?" —
  `design-search`, whose fixture is a `schema.sql` stating PostgreSQL and 38,000
  rows.
- "Which stack are you running?" — `design-rate-limit`, whose fixture runs Redis
  for sessions.

Every one of those forks is resolvable, and resolvable from a file in the case
directory. The clause was meant to license asking when the answer genuinely is
not available; what it produced was asking instead of reading.

## Why the five dev cases dilute it

Because on all five, the answer a model gives without resolving anything is
already the fixture's answer. Rate-limiting reaches for Redis, payment retries
reach for an idempotency key, search over a Postgres table reaches for full-text
search. The conventional answer and the correct answer coincide.

The evidence is in the baseline snapshot, before any edit. Marker: does the
response name the mechanism its trap requires?

| arm | names the required mechanism | quality fails | mean tokens |
| --- | --: | --: | --: |
| `baseline` (no system prompt) | 44 of 50 | 19 of 50 | 2627 |
| `laconic` | 88 of 100 | 36 of 100 | 2565 |
| `terse-control` ("Answer concisely.") | 45 of 50 | 17 of 50 | 2527 |
| `word-compression` (the degenerate arm) | 47 of 50 | 18 of 50 | 2580 |

**All four arms are the same, including the one instructed to drop articles and
use arrows.** The five dev design cases have never demonstrated that they can
separate a compression effect from no compression at all. They were built to be
gradeable from the fixture alone, and they are; what they were never checked for
is whether the fixture is *load-bearing* in the answer.

The holdout's design case is the one where it is. Its question is a feature
flag, and the conventional answer — an environment variable, or a third-party
flag service — is exactly what its trap fails. The fixture's answer, another row
in the `settings` table read the way `maintenance_mode` already is, is only
reachable by reading the code. Per the loop's rules no holdout count appears
here, but the direction is unambiguous: under the edit, nearly every answer
offered the generic options and asked which one the user had, and the judge's
stated reason was that the answer never engaged the mechanism the app already
has.

So the holdout case is not stricter. It is the only design case in the whole
suite whose criterion can tell reading from guessing.

## The same check on the three `verdict-*` cases, which is worse

`verdict-experiment`, `verdict-rollout` and `verdict-schema` were added to
instrument [#60], the evaluative-question sibling of [#46]. Running the same
check on them:

| | quality fails |
| --- | --: |
| `-v3` baseline, all four arms, three cases | **0 of 150** |
| round 15, all four arms, three cases | **0 of 150** |

Zero failures in 300 gradings, across every arm and both rules revisions, with
no `not_exercised` verdicts hiding in the denominator. These cases are not
weakly discriminating; they are saturated at pass and cannot signal at all. It
is the mirror of `destructive`/haiku, which `expect.json` already documents as
stuck at fail, and of `ordered-steps`/haiku, stuck at a coin flip.

So the instrument for [#60] is presently three cases that always pass, and the
instrument for [#46] is five cases that score a degenerate arm like an untreated
one. Neither was checked for discrimination before it was adopted.

## What this licenses, and what it does not

**It does not license re-scoring round 15.** The covariate was found after the
round, by looking at responses whose verdicts were already known. Used as a
gate it would be exactly the mistake the loop's pre-registration discipline
exists to prevent.

**It does not license a second attempt at the same edit.** Nothing here says the
edit is harmless; it says the harm is real, present in the dev data, and hidden
by aggregation.

What it does establish, and what a future attempt on [#46] has to carry:

1. **A design case is only an instrument for compression if its fixture is
   load-bearing.** Five of the six in the suite are not. A case whose right
   answer a model would give without opening a file measures nothing about
   whether the answer was derived or recalled.
2. **The round-wide `quality_fails` count can be flat over two opposite
   effects.** It was here, at p = 1.000, in a round where one stratum moved at
   p = 0.036.

## What to do about it

Two candidates, and the first is much cheaper.

**A. Add design cases whose conventional answer is wrong.** The property to
build for is not difficulty; it is that the fixture contradicts what the model
would otherwise say. `holdout-design` has it by accident. Three or four dev
cases with it would put the signal on the dev set, where a round can act on it
at step 7 instead of discovering it at step 9. Building them is fixture work and
no model calls until a round runs.

**B. Report `quality_fails` split by stratum on design cases.** Cheap, and it
makes a cancelling pair visible in `report.py`'s output rather than requiring
this analysis to find it. The covariate would have to be pre-registered before
it could reject anything.

A does the real work. B is a disclosure that stops the same cancellation from
being invisible next time.

**Both done 2026-08-12.** A is [`design-discrimination.md`](design-discrimination.md)
and the [`-v4` baseline](baseline-v4.md). B is in `report.py`: `round_summary`
carries a `quality_strata` block, `accept_verdict` prints a disclosure line
whichever way the verdict went, and `render` prints the split for a single
snapshot. Re-scoring round 15 with it active leaves the verdict exactly as it
was — the line may never reject — and adds this to the step 7 output:

```
quality strata (disclosure, not a gate): answers that hand a decision back
10 of 31 -> 20 of 40, answers that resolve it 42 of 189 -> 28 of 180; the two
strata moved in OPPOSITE directions, which a flat quality count hides - the
hands-back stratum got worse
```

That is the warning the round did not have, printed beside the `quality_fails`
improvement of 52 to 48 that it did have.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
