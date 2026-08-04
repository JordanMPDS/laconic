# Loop round 04 — in progress

Point 3 of [#36](https://github.com/JordanMPDS/laconic/issues/36), and the first
round scored by the `--target-cases` instrument that point 1 of the same issue
built. It is also the first attempt at the question [#34](https://github.com/JordanMPDS/laconic/issues/34)
poses: whether a rule stated as a test the model can apply generalizes where an
enumeration of positions has twice failed to.

## Hypothesis

Written before the round was generated:

> Adding a read-it-aloud substitution test to the arrow prohibition in
> `rules/laconic.md` — "before you keep an arrow, read it aloud; it always says a
> word, and that word is the one to write" — should move `violations_total` on
> `walkthrough` and `ordered-steps` downward from round 01's baseline, without
> raising round-wide `never_cut_failures` (0) or `quality_fails` (0).

## Root cause it addresses

Both previous arrow edits changed which positions the rule enumerates, and both
failed the same way. Round 01 added the colon-introduced chain and the model
wrote the same chains inside bullets. Round 03 extended the list to cover
bullets, numbered steps and the colon, and `stale-cache` — clean in round 01 —
produced ten arrows in the colon-introduced form the list already named.

The pattern across both is that naming the position does not stop the
construction. In round 01's baseline the model writes constructions the current
list already covers:

- `walkthrough`/sonnet rep1: `- Any other non-OK status → throws.` The list
  covers this twice over, under chaining states and under one thing becoming
  another.
- `ordered-steps`/haiku rep1: `a list/map of key ID → key material`, which is
  the mapping form named in the same sentence.

An enumeration asks the model to check membership: is what I am writing one of
the listed positions? That question is answerable "no" about a construction the
list does cover, and the two rounds are the evidence. A read-aloud test asks a
different question, about the arrow rather than its surroundings, and it is
answerable the same way in any position — including positions no list names.

This edit does **not** remove the enumeration. A general phrasing was already
tried once, before the levels run: "no arrows standing in for conjunctions in
running prose" left two openings the benchmark caught immediately, which is why
the enumeration exists and why `tests/test_rules.sh` asserts it is still there.
The test is added on top of the list, not in place of it.

## Round configuration

| | |
| --- | --- |
| Baseline | `evals/snapshots/loop/round-01.json`, `rules_cksum` 1830906901 |
| Treatment | `evals/snapshots/loop/round-04.json` |
| Arms | `laconic` regenerated, three controls carried |
| Target | `violations_total` on `walkthrough`, `ordered-steps` |

The baseline is round 01 rather than a fresh generation: its rules are exactly
master before this edit, and both rounds are scored by the current detector,
which counts arrows in bullets and numbered steps.

Results follow once the round is generated.
