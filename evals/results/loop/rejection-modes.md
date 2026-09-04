# Why rounds get rejected, and what that says about [#26]

Every rule edit this loop has proposed, classified by **what actually rejected
it**. [#26] defers multi-agent candidate generation with an explicit revisit
condition, and this is the evidence that decides it.

## The classification

A round rejects for one of two reasons, and they mean opposite things:

- **Gate failure** — a fatal counter rose somewhere the hypothesis never named.
  The idea may have been fine; something else broke.
- **Hypothesis failure** — the target itself did not move, or moved the wrong
  way. The idea was wrong.

| verdict | rounds | n |
|---|---|--:|
| **accept** | 24, 26, 28 | 3 |
| gate failure | 01, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 14, 20, 25, 30 | 15 |
| **hypothesis failure** | 16, 17, 22, 23, 27, 29, 31, 38, 40 | 9 |
| holdout failure | 15 | 1 |

Rounds 32 to 37 and 41 to 43 proposed no rule edit and are not counted; they are
instrument rounds.

## [#26]'s revisit condition is met

> **Revisit when** the ledger shows several consecutive rounds rejected at step 7
> for a failed hypothesis rather than a failed gate. That is the signal that idea
> quality has become the constraint.

**The last three rule-edit rounds are all hypothesis failures**, and each moved
in the wrong direction rather than landing inside the noise floor:

| round | the target | what it did |
|---|---|---|
| 31 | arrows on `walkthrough`/sonnet | **31 → 33**, and round-wide rose 60 → 63 |
| 38 | arrows with the rendered specimens replaced by prose | control 36 against edit **62** |
| 40 | [#60]'s third pre-send check | five of seven cells moved **up**, p = 0.4531 |

Before those, round 30 was a gate failure — its target passed decisively at
p = 0.016 and a never-cut loss on `destructive`/haiku rejected the round anyway.

**Wrong-sign is the strongest form of the signal [#26] describes.** An effect too
small to detect is a noise-floor problem; an effect with the wrong sign is a
wrong idea.

## And the loop's own indexes now say the same thing in prose

Two documents written this week end by admitting they do not know what to try
next, which is idea exhaustion stated directly:

- [`arrows.md`](arrows.md): five edits, no accepts, and *"there is no
  form-shaped hole to aim at"* — four revisions cut the rate by two thirds while
  moving neither the chain/mapping nor the list/prose composition. What a
  seventh attempt should be is left as three options, none obviously right.
- [`over-length-cluster.md`](over-length-cluster.md): four wording attempts
  rejected, one relocation accepted, one structural attempt rejected. *"The next
  edit here does not have an obvious form, and buying one before the measurement
  is in would be a fifth guess."*

## The honest counter-argument

**Two of the three consecutive failures are the same exhausted target.** Rounds
31 and 38 are both arrow edits, and [`arrows-scope-36.md`](arrows-scope-36.md)
established there is no form-shaped hole left in that prohibition. More proposers
reading the same inventory would not have found one.

Round 40 is the round that carries the argument: [#60]'s structural check is a
genuinely new idea, deliberately not another sentence bounding a licence, and it
moved the wrong way too.

**And [#26]'s cost argument still holds in calls.** A confirmation round is ~900
calls and candidate generation is nearly free, so parallel proposers do not
relieve the expensive constraint. What has changed is that the loop now has two
documented dead ends and no queue of untried ideas — the constraint moved without
the cost structure moving.

## What this issue should do

**Reopen it as actionable, not build it on this evidence alone.** Three
consecutive wrong-sign rejections and two indexes ending in "no obvious next
edit" satisfy the letter of the condition and most of its spirit. What they do
not establish is that *more* proposers would produce a better idea rather than
more of the same ones.

The cheapest test of that is not the workflow: it is to take one of the two dead
ends and ask for candidates through the four lenses [#26] names — never-cut,
compression, readability, answer quality — and see whether any lens produces an
edit the single-reader loop did not already try. That costs no generation calls
and it is the pilot the full approach deserves before 900 are spent confirming
whatever it produces.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#60]: https://github.com/JordanMPDS/laconic/issues/60
