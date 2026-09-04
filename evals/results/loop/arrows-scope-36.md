# #36's target re-measured: one case, not two

> **Consolidated 2026-09-04 into [`arrows.md`](arrows.md),** which indexes all
> six arrow rounds and the four issues they answered. This document is the
> instrument measurement that narrowed the target to one case; that one is the
> line of work's summary, including round 38's finding that the rule's own
> `Wrong:` line is not the carrier.

**Date:** 2026-08-28
**Status:** an instrument measurement, not a round. No rule changed, no round is
accepted or rejected by it. 40 generations, 0 judge calls, 0 failures.
**Snapshot:** `evals/snapshots/loop/arrows-scope-36.json`, `rules_cksum`
136269960, CLI 2.1.250, sequential.

## Why buy anything before proposing an edit

[#36] says the arrow work belongs to `walkthrough` and `ordered-steps`. It was
written on 2026-08-04 against `rules_cksum` 1830906901, and the shipped rules
have changed four times since. Every round from 25 onward has been scoped to
sonnet design cases, so at today's rules `walkthrough` and `ordered-steps` had
**ten stored responses each** — not enough to say whether the concentration
survived.

Round 29 registered its bar from a snapshot eight days and one rule revision
old, and its own post-mortem calls that the round's most useful finding. Forty
generations is the cheapest possible way not to repeat it. `symbol_connectors`
is computed offline from the response text, so this stage costs generations
only.

The case prompts are unchanged since before 2026-08-10 — the one commit touching
either case directory since, `a8555f7`, adds `saturated_models` to
`ordered-steps/expect.json` and nothing else — and the detector reads text
alone. Every comparison below is one instrument across two rule revisions.

## The rate fell, and the concentration narrowed to one case

Responses carrying at least one arrow, `laconic` arm, pooled over every stored
snapshot at each revision:

| cell | `1830906901` | today, `136269960` | Fisher |
|---|--:|--:|--:|
| `walkthrough`/haiku | 72/120 (2.3 arrows per response) | 3/20 (0.6) | 0.000 |
| `walkthrough`/sonnet | 51/120 (1.4) | 6/20 (0.8) | 0.335 |
| `ordered-steps`/haiku | 9/140 (0.2) | 1/10 (0.3) | 0.510 |
| `ordered-steps`/sonnet | 44/140 (0.8) | 1/10 (0.1) | 0.283 |
| **`walkthrough` pooled** | **123/240 (51%)** | **9/40 (22%)** | **0.001** |
| **`ordered-steps` pooled** | 53/280 (19%) | 2/20 (10%) | 0.548 |

**`ordered-steps` is no longer a target.** It sits at 2 of 20 responses and 0.1
to 0.3 arrows per response. Scoping a count target to it would add the kind of
cell `instrument-notes.md` already complains about: one that has never moved
outside its own noise and votes anyway.

**`walkthrough` is still a target, and still the worst case in the set.** At
today's rules, excluding the holdout:

| scope | responses carrying an arrow |
|---|--:|
| `walkthrough` | 9/40 (22%) |
| `design-*` sonnet | 46/848 (5%) |
| everything else | 5/80 (6%) |

Fisher p = 0.00042 for `walkthrough` against the design cases. On chains
specifically the gap is wider: 37.5 per 100 responses against 2.6.

## The shipped edits cut every form proportionally, and closed none

Two decompositions the repo already tracks, on matched scopes so the case mix
cannot explain the movement:

| scope and revision | n | chains per 100 | mappings per 100 |
|---|--:|--:|--:|
| `design-*` sonnet, `1830906901` | 1080 | 22.0 | 24.5 |
| `design-*` sonnet, `3694954268` | 1723 | 2.0 | 3.4 |
| `design-*` sonnet, `136269960` | 848 | 2.6 | 4.7 |
| `walkthrough`, `1830906901` | 240 | 125.4 | 61.7 |
| `walkthrough`, `136269960` | 40 | 37.5 | 35.0 |

And by position, over every response at each revision:

| revision | arrows | in a list item or table row | in a running paragraph |
|---|--:|--:|--:|
| `1830906901` | 1462 | 954 (65%) | 508 (35%) |
| `136269960` | 122 | 75 (61%) | 47 (39%) |

**Neither composition moved.** The rate fell by roughly two thirds and the
chain-to-mapping and list-to-paragraph splits are where they were. Whatever the
shipped arrow section does, it does it evenly across forms rather than closing
one — so there is no form-shaped hole left to aim a scoped edit at, which is the
first thing an edit proposal would have reached for.

The list-versus-prose reading in particular is a dead end and was already
settled: `docs/benchmark.md` records that `_symbol_hits` once skipped structural
lines on exactly that reasoning, that the reasoning was wrong, and that 510
arrows had gone uncounted because of it. The rule text already names three
structural positions.

## What the surviving violations look like

All eight arrow-carrying responses in this batch, by form:

- **Condition-to-consequence bullet labels**, the largest group:
  `` - `res.status === 401` → the refresh token itself was rejected ``,
  `- any other non-ok status → throws`, `- success → writes the new access token`.
- **Sequential chains**, the shape the rule spends most of its paragraph on:
  ``Request 1 calls `currentToken()` → token invalid → calls `refresh()` → sets `inFlight` ``.
- **One mapping**: `` `kid` → public key ``.

The second group reproduces the rule's own worked example almost word for word.
`rules/laconic.md:56` reads:

```
- Wrong: **Request A**: calls `currentToken()` → token expired → calls `refresh()`
```

The case material does not supply that vocabulary — `walkthrough/prompt.md` says
"when two requests refresh at once" and the fixture never says "Request A". The
likeliest reading is the reverse of copying: the example was written *from* this
case's failures, and the case still produces the construction the example names.
That is [#34]'s question with a fresh data point, not a new finding.

## Recommendation

**Narrow [#36] to `walkthrough` and do not buy a fifth enumeration edit.**

Rounds 01, 03 and 04 each aimed at these cases by adding to the enumeration.
Round 01 scored 7 to 0 while the model wrote the same chains one list marker to
the left; round 03 moved its named cases 21 arrows to 5 and rejected on the
round-wide sum; round 04 added a read-aloud substitution test and drove
`walkthrough`/haiku from 9 arrows to 17. The shipped section that followed cut
the rate two thirds and closed no form. A fifth attempt of the same kind is the
attempt the ledger's own accounting argues against.

What the data supports instead, in order of cost:

1. **Close the two-case framing.** `ordered-steps` is done at any scope this
   instrument can measure. Whatever [#36] becomes, it is about `walkthrough`.
2. **A scoped round is now affordable if one is wanted.** `violations_total`
   on `walkthrough`, both models, is 2 cells and 29 arrows in 40 responses — the
   count test round 03 already used at this scope reached p = 0.001. Detecting a
   halving wants about 25 reps a side, so 100 generations and no judge calls,
   both sides interleaved in one batch.
3. **The residual belongs to [#34].** Four revisions have each lowered the rate
   without closing it, and the composition has not shifted once. That is
   evidence about whether an enumerated prohibition can close, which is the
   question [#34] exists to ask, and it is worth more than another enumeration.

[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#36]: https://github.com/JordanMPDS/laconic/issues/36
