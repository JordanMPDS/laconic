# Building design cases that can tell a derived answer from a recalled one

**Date:** 2026-08-12
**For:** [#88]
**Cost:** 160 generations and 160 judge calls, 0 failed on either side.
**Artefacts:** `evals/snapshots/loop/design-discrimination.json` and
`design-discrimination-judgments.json`.
**Result:** three of four candidates admitted — `design-cache`,
`design-realtime`, `design-upload`. `design-pagination` was built, measured and
discarded.

## Why

[`design-quality-covariate.md`](design-quality-covariate.md) established that
the five design cases in the scope cannot separate the treatment arm from the
arm instructed to drop grammar and use arrows: all four arms name the mechanism
their traps require and fail quality at the same rate. On those five, the answer
a model gives without opening a file is already the fixture's answer, so no
verdict depends on the fixture having been read. That is why the round 15 edit
passed every dev-set gate and was killed by a holdout case that happens, by
accident, to have the missing property.

These four candidates were built with that property on purpose: **the fixture
contradicts what the model would otherwise say.**

| case | what a model says without reading | what the fixture forces |
| --- | --- | --- |
| `design-cache` | add Redis, memcached, an in-process cache | a CDN is already in front at a 0% hit rate, defeated by an app-wide `no-store` added for the account pages |
| `design-realtime` | WebSockets, Socket.io, a held-open stream | the platform returns 501 on upgrade and freezes instances between invocations; the data is rewritten once a minute |
| `design-upload` | `multer` streaming the file through the app | the shared proxy caps bodies at 1 MB and raising it was declined for PCI; `storage.js` already signs PUT |
| `design-pagination` | `LIMIT`/`OFFSET` with page numbers | 52M rows, one index on `(account_id, created_at desc, id desc)`, and a published opaque-cursor contract |

## The acceptance test, and its correction

[#88] registered one: generate on `baseline` and on `word-compression`, keep the
case if the degenerate arm fails more. **That test was corrected before any of
this data existed**, in a comment on the issue timestamped before judging began,
because it cannot measure what it was meant to measure.

`word-compression` does not compress a design answer. Measured on these four
candidates:

| case | `baseline` mean tokens | `word-compression` mean tokens |
| --- | --: | --: |
| `design-cache` | 2847 | 2813 |
| `design-pagination` | 2359 | 2634 |
| `design-realtime` | 1622 | 1844 |
| `design-upload` | 2883 | 2279 |

It is *longer* on two of the four. An arm contrast therefore tests whether a
degenerate style instruction moves the verdict, which is not what happened in
round 15 — there the rule edit compressed the answers, and no arm did.

The corrected test needs no new arm and comes off the same snapshot:

- **Headroom** — the share of responses that resolve the fixture's
  contradiction. A case where nearly every response resolves it cannot detect a
  rule that stops them, whatever its criterion looks like. This is what
  disqualifies the five existing cases, at about 90% on every arm.
- **Bite** — the pass rate among responses that resolve it against those that
  do not, with a two-sided Fisher exact.

## Results

The registered arm contrast, reported because it was registered:

| case | `baseline` fails | `word-compression` fails | Fisher |
| --- | --: | --: | --: |
| `design-cache` | 8 of 20 | 10 of 20 | 0.751 |
| `design-pagination` | 2 of 20 | 4 of 20 | 0.661 |
| `design-realtime` | 15 of 20 | 10 of 20 | 0.191 |
| `design-upload` | 7 of 20 | 7 of 20 | 1.000 |

Nothing separates. Under the test as first registered, all four candidates would
have been rejected, including the three that work.

The corrected test, both arms pooled at n = 40:

| case | resolves the fixture | pass, resolved | pass, not resolved | Fisher | |
| --- | --: | --: | --: | --: | --- |
| `design-cache` | 30 of 40 | 19 of 30 | **0 of 10** | 0.0005 | admitted |
| `design-realtime` | 19 of 40 | 14 of 19 | **0 of 21** | <0.0001 | admitted |
| `design-upload` | 31 of 40 | 24 of 31 | **0 of 9** | <0.0001 | admitted |
| `design-pagination` | 40 of 40 | 33 of 40 | — | — | discarded |

**On all three admitted cases, not one response that failed to resolve the
fixture passed.** That is the property the five existing cases do not have, and
it is what makes these three able to see a rule change that stops the model
resolving the fixture.

`design-realtime` has the most headroom: a majority of responses reach for
WebSockets or a held-open stream without engaging `PLATFORM.md`, and every one
of them fails.

## Why `design-pagination` was discarded

Every response resolved the fixture under the registered marker, so the split
cannot be computed and the case cannot demonstrate headroom.

The diagnosis is worth recording, because it is the same defect the four cases
were built to avoid, one level down. **Keyset pagination is the conventional
answer to a paging question.** A model that never opens a file gets the main
recommendation right, so the trap ends up hinging on a narrower detail — whether
the answer matches the opaque `next_cursor` contract `API.md` already publishes.
The seven failures are all that detail:

> "The response invents its own cursor parameter and encoding (`after=xyz123`,
> base64(created_at, id)) rather than reading and matching the existing opaque
> next_cursor contract that API.md already publishes."

That is a real criterion and the case does grade fixture-reading. But its
headroom is unmeasurable, and admitting a case that cannot demonstrate the
property is how the scope came to hold five cases that measure nothing. It was
removed rather than kept and excluded, so nothing has to remember why it is
there.

The 40 runs stay in the snapshot as the evidence for this paragraph.

## What this does not do

**No gate changes and no round is re-scored.** Adding a case changes what a
future round can measure; it does not change any published number. The three new
cases are `quality`-graded with an empty `never_cut` list, exactly like the
five that preceded them, so the round-wide counters see them the same way.

**It does not fix [#46].** It removes the reason [#46] could not be attempted
honestly. The next attempt can put design-answer quality on the dev set at step
7 instead of discovering it at step 9, which is what round 15 cost.

**The five existing design cases stay.** They carry the scoped `output_tokens`
target, which is a length measurement and does not depend on the property they
lack. What they may no longer be read as is evidence about design-answer
quality.

## What is still open

The three new cases have never been generated on the `laconic` arm. Their
verdicts here come from `baseline` and `word-compression` only, which is what
the discrimination check needs and is not a baseline for a round. A round that
wants to score them needs them in the `-v3` baseline first, or a `-v4`.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#88]: https://github.com/JordanMPDS/laconic/issues/88
