# The labelling rule for `restates`, v2

**Written and committed before any label was written under it**, and before
batch 3 was drawn. The order matters for the same reason it did for v1: a rule
adjusted to what the sample turned out to contain is a description of the
sample, not a criterion.

**This supersedes [`criterion.md`](criterion.md) at one seam and nowhere else.**
Every section below is v1's text verbatim except "The unit is a whole
sentence", which is new, and the borderline convention, which now defers to it.
[`criterion.md`](criterion.md) stays in the repository because the 120 labels in
`labels.json` were written under it and are evidence about that construct rather
than this one.

## Why there is a v2

v1 reads **55.3% precision out of sample** ([#155]). Classifying its 26 false
positives by the passage it quoted puts 14 of them in one class: a closing
sentence whose first clause names a point already made and whose second attaches
a priority, a reason or a scope judgement that was not.

> *"Just fix the data type before you go further."*
> *"Fix the multiple-comparisons issue first — it's the clearest threat to
> validity."*

v1 does not decide those. It says a passage restates when it "adds nothing that
was not already there", and is silent on a **sentence that is half each**. That
silence is also the one seam where v1's own human labelling is internally
inconsistent: batch 2 labels every mixed closing `false` under the borderline
convention and batch 1 does not.

So the seam is decided here explicitly, in the direction the deletability pilot
measured. That pilot failed as a construct — 51.2% precision against v1's 55.3%,
see [`deletability.md`](../deletability.md) — but one piece of it was worth
keeping: **defining the deletion unit as one complete sentence or more cleared 8
of the 14 mixed-closing false positives on its own.**

**A mechanical version of this rule was tried first and does not work.** Applying
"the quoted passage must begin and end at a sentence boundary" to v1's stored
quotes costs precision on both batches — 74.2% to 66.7% on batch 1 and 55.3% to
44.4% on batch 2 — because it mostly rejects true positives whose quote is a
fragment or a paraphrase. What it measures is v1's quoting habit, not the
passage. The rule has to be in the criterion, where the labeller and the
detector both apply it to the response, rather than in a filter on the quote
string.

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

## The unit is a whole sentence

**New in v2, and the only thing v2 changes.**

A passage counts only if **one or more complete sentences could be deleted with
no claim lost**. Judge each sentence whole: a sentence is a restatement when
everything it asserts was already asserted, and it is not one when any part of
it asserts something new.

So a sentence whose first clause repeats a point already made and whose second
clause attaches a priority, a reason, a scope, a severity or a recommendation
that was not already made is **not** a restatement. Deleting it would lose the
second clause.

- Not a restatement: *"Fix the multiple-comparisons issue first — it's the
  clearest threat to validity."* The ordering and the severity are new even when
  the issue is not.
- Not a restatement: *"Just fix the data type before you go further."* "Before
  you go further" is a new claim about sequencing.
- A restatement: *"So the plan as written will cause errors during rollout."*
  when that is already the response's stated conclusion and the sentence carries
  nothing else.

Applied to a closing paragraph, this is per sentence rather than per paragraph:
a four-sentence close of which one sentence is wholly redundant is `true`, and
one whose every sentence carries something new is `false`, however familiar the
paragraph reads.

**This rule is about the unit, not about the threshold.** It does not make the
label harder to earn in general; it makes it earned by a whole sentence rather
than by a clause. A wholly redundant clause inside an otherwise new sentence is
real redundancy and this criterion does not count it, deliberately: a metric
that fires on half-sentences cannot be acted on by a rule, because the repair
for a half-sentence is a rewrite rather than a deletion.

## Counts as a restatement

- A closing recap that lists conclusions the response already gave.
- A sentence asserting a relationship between two earlier points where that
  relationship was already stated when the second point was made.
- A paragraph re-explaining what a table, list or code block directly above it
  already showed.
- A "so what this means is" sentence whose content is the preceding sentence.

## Does not count as a restatement

- **A sentence that repeats in one clause and adds in another.** See "The unit
  is a whole sentence" above; this is the seam v2 exists to decide.
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
cases will report harm that a reader would not recognise.

**The whole-sentence rule is applied before this convention, not by it.** A
mixed sentence is not a borderline case under v2; it is decided, and it is
`false`. The convention is left for what it was always for — a passage whose
status is genuinely unclear after the rule has been applied.

## What is deliberately not decided here

**How much restatement.** This label is binary: does the response restate
anything. Whether the metric that eventually ships is this binary, a count of
restated passages, or a share of the response, is a decision that should be made
from the measured base rate rather than guessed before it.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
