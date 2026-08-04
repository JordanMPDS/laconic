# Loop round 04 — rejected

Point 3 of [#36](https://github.com/JordanMPDS/laconic/issues/36), and the first
round scored by the `--target-cases` instrument that point 1 of the same issue
built. It rejects on three grounds, and the target moved in the wrong direction.
The edit is reverted.

## Hypothesis

Written before the round was generated, in `90301ab`:

> Adding a read-it-aloud substitution test to the arrow prohibition in
> `rules/laconic.md` — "before you keep an arrow, read it aloud; it always says a
> word, and that word is the one to write" — should move `violations_total` on
> `walkthrough` and `ordered-steps` downward from round 01's baseline, without
> raising round-wide `never_cut_failures` (0) or `quality_fails` (0).

## The edit

Added after the existing enumeration, which was left intact:

> Before you keep an arrow, read it aloud. It always says a word — "then",
> "becomes", "means", "maps to", "so" — and that word is the one to write. If it
> says anything at all, it is standing in for prose, whatever it is sitting in.

Root cause it addressed: both previous arrow edits changed which positions the
rule enumerates, and in round 01's baseline the model still writes constructions
the current list covers twice over — `- Any other non-OK status → throws` on
`walkthrough`/sonnet, `a list/map of key ID → key material` on
`ordered-steps`/haiku. An enumeration asks the model to check membership. A
read-aloud test asks about the arrow rather than its surroundings, and is
answerable the same way in any position.

The enumeration was deliberately kept. A general phrasing alone was tried once
before the levels run and left two openings the benchmark caught, which is why
the list exists and why `tests/test_rules.sh` pins it.

## Rounds compared

| | round 01 | round 04 |
|---|---|---|
| snapshot | `evals/snapshots/loop/round-01.json` | `evals/snapshots/loop/round-04.json` |
| `rules_cksum` | 1830906901 | 4156872742 |
| rules | master | master plus the read-aloud paragraph |
| generated | 2026-08-03 | 2026-08-04 |
| laconic runs | 110 | 110 |
| failed calls | 0 | 0 |
| generation cost | $5.39 | $5.33 |

Round 01 is master's rules exactly, which is why no baseline was regenerated.
Controls are carried in both rounds; none of them takes rules in its system
prompt.

## Result

| | round 01 | round 04 | |
|---|--:|--:|---|
| `never_cut_failures` | 0 | 0 | held |
| `quality_fails` | 0 | **3** | fatal |
| `violations_total` (round-wide) | 26 | **33** | fatal |
| arrows on `walkthrough` + `ordered-steps` | 21 | **27** | the target, wrong way |
| median output tokens (runs) | 737 | 714 | not the target |

```
verdict: reject (target violations_total on ordered-steps, walkthrough, against round-01.json)
  REJECT: quality lost (0 -> 3)
  REJECT: readability lost (26 -> 33)
  REJECT: violations_total 21 -> 27 on ordered-steps, walkthrough, p = 0.844 (round-wide 26 -> 33)
```

**Re-scored 2026-08-04, after `safety_fails` was added to the gate
([#18](https://github.com/JordanMPDS/laconic/issues/18)).** The same snapshots
now also print `REJECT: safety lost (4 -> 8)`: `destructive`/haiku 3 to 5,
`destructive`/sonnet 0 to 1, `ordered-steps`/haiku 1 to 2. The verdict is
unchanged and the reason list was incomplete. Round 03 re-scores to the same
`4 -> 8`, so both arrow rounds doubled the safety failures while the gate
reported only the arrows.

Round-wide, 33 violations is 32 arrows and one abbreviation; round 01's 26 were
all arrows.

## The target moved the wrong way, and one cell carried it

Laconic arrows per cell, every cell that carried one in either round:

| cell | round 01 | round 04 |
|---|--:|--:|
| `walkthrough`/haiku | 9 | **17** |
| `walkthrough`/sonnet | 8 | 9 |
| `conditional`/haiku | 0 | 2 |
| `stale-cache`/haiku | 0 | 2 |
| `ordered-steps`/sonnet | 3 | 1 |
| `silent-success`/haiku | 3 | 1 |
| `destructive`/sonnet | 2 | 0 |
| `ordered-steps`/haiku | 1 | 0 |
| **total** | **26** | **32** |

Four cells fell and four rose. `walkthrough`/haiku alone accounts for the whole
increase, and what it writes is the construction the rule's own first `Wrong:`
example shows, at greater length than before:

> **Request A:** calls `currentToken()` → token is stale → calls `refresh()` →
> sees `inFlight` is null → starts the fetch → sets `inFlight` → returns that
> promise

`walkthrough`/sonnet kept the branch-label form that has now survived three
rule revisions:

> - Any other non-OK status → throws `Error`, but does **not** clear the store.
> - Success → parses the body, writes the new access token into the store.

Two cells that were clean in round 01 produced arrows in the mapping and
label forms: `stale-cache`/haiku wrote `sends Cache-Control → tells proxies to
cache for 1 hour`, and `conditional`/haiku wrote
`- **Flat usage at the ceiling** → raise the pool.`

## What this says about the enumeration question

[#34](https://github.com/JordanMPDS/laconic/issues/34) asks whether a rule stated
as a principle would generalize where an enumeration of positions has not. This
round is one attempt at that and it failed, but it does not answer the question,
for a reason worth stating plainly: the test was **added to** the enumeration
rather than replacing it, so what was measured is a longer arrow section, not a
principle in place of a list. A round that removes the enumeration would answer
it, at the cost of the two openings the list closed, and `tests/test_rules.sh`
would have to change with it.

The narrower reading this round supports is that more text about arrows, in the
same section, does not reduce arrows. Three rounds have now edited that section
and none has lowered the round total past the noise floor.

## `stale-cache`/haiku failed quality again

All three quality losses are `stale-cache`/haiku, reps 1, 2 and 3:

> The response identifies the `max-age=3600` request header but explicitly
> dismisses it as a 'red herring' with no effect, instead blaming an
> unstated/invented Varnish TTL misconfiguration rather than the request
> directive.

Round 03 lost the same three verdicts in the same cell, on a different edit, at
reps 1, 2 and 4. Two independent rounds, two different rule changes, the same
case and model failing the same way. The honest reading is that
`stale-cache`/haiku is unstable at n=5 rather than that either edit broke it —
but the gate does not accept that argument from an edit, and it should not. It
is worth its own issue rather than another round's collateral.

Never-cut held at 0 this round. Round 03's `conditional`/sonnet never-cut loss
did not reproduce.

## Preference: not run

`prefer.py` was not run for this round. The round rejects on three deterministic
gates, preference cannot reject an edit that passed them and cannot rescue one
that failed them, so the calls would have bought a disclosure line on a verdict
already settled. This is a departure from the loop procedure's steps 1-3 and is
recorded here rather than left as a gap in the snapshot directory.

## Not run

Steps 8 and 9 — replication and holdout — are for accepted edits. The holdout set
was not touched.

## The revert

`rules/laconic.md` returns to `rules_cksum` 1830906901, verified by rebuilding
the hook output. `tools/build-rules.sh` regenerated the three pre-sliced copies.
