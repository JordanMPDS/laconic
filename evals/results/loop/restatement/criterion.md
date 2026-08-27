# The labelling rule for `restates`

**Written and committed before batch 1 was labelled.** The order matters: a rule
adjusted to what the sample turned out to contain is a description of the
sample, not a criterion. `unread_asks` learned this the expensive way — its v2
detector was designed on batch 1's errors and read 93.1% precision in sample
against 73.7% fresh.

## The question each response is labelled on

> Does this response assert a claim it has already asserted?

`restates = true` when some passage of the response makes a claim the response
has already made, and the passage adds nothing that was not already there.

This is the **redundancy** half of the distinction [#150] draws, and only that
half:

- **Scope** — which claims belong in the answer. Set by the request. A requested
  report legitimately needs many, and a response with many claims is not
  labelled `true` for that reason.
- **Redundancy** — whether a claim is already made. Never licensed by the
  request. This is what is labelled.

Length is not the criterion. A 3,000-token response that says each thing once is
`false`. A 400-token response whose last sentence repeats its first is `true`.

## Counts as a restatement

- A closing recap that lists conclusions the response already gave.
- A sentence asserting a relationship between two earlier points where that
  relationship was already stated when the second point was made.
- A paragraph re-explaining what a table, list or code block directly above it
  already showed.
- A "so what this means is" sentence whose content is the preceding sentence.

## Does not count as a restatement

- **A contrast that distinguishes two cases.** "A 401 from the refresh endpoint"
  followed by "a 401 from some other API call" is a distinction being drawn, not
  a claim being repeated, even though the two share most of their words.
- **A cross-reference that names an earlier point without re-arguing it.**
  "as in #1 above", "the same problem as the migration", "this is why the
  rollback is broken" — naming is not restating.
- **A heading, label or lead-in** that announces what follows.
- **Repeating a term, identifier, file path or number** while making a new
  claim about it. Technical vocabulary recurs; that is not redundancy.
- **A recommendation that follows from earlier analysis but was not itself
  stated earlier.** "Use NUMERIC" is a new claim even when the reasoning for it
  was given above. It becomes a restatement only if the recommendation itself
  was already given.
- **A summary the user asked for.** None of these four cases asks for one, so
  this exclusion should never fire here; it is written down so that it cannot be
  invented later.

## Borderline convention

When a passage is arguably either a restatement or a new claim, label `false`.
The metric is meant to detect a harm, and a detector tuned to catch ambiguous
cases will report harm that a reader would not recognise. This convention is
recorded so that it is applied consistently rather than per response.

## What is deliberately not decided here

**How much restatement.** This label is binary: does the response restate
anything. Whether the metric that eventually ships is this binary, a count of
restated passages, or a share of the response, is a decision that should be made
from the measured base rate rather than guessed before it. If nearly every long
response restates something, a binary saturates and cannot move, and the count
form is the one worth building.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
