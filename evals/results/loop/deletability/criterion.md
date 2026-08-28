# The labelling rule for `deletable`

**Written and committed before a single verdict was read**, the same order
[`../restatement/criterion.md`](../restatement/criterion.md) was committed in and
for the same reason: a rule adjusted to what the sample turned out to contain is
a description of the sample.

This is [#155]'s direction **B** — rethinking the construct rather than
sharpening `restates`. The question `restates` asks is *"does this response
assert a claim it has already asserted?"*, and 14 of its 26 out-of-sample false
positives sit on one seam it does not resolve: a closing sentence whose first
clause names a point already made and whose second attaches a priority, a reason
or a scope judgement that was not. `criterion.md` says "some passage ... adds
nothing that was not already there" and is silent on a sentence that is half
each.

## The question each response is labelled on

> Is there a passage that could be deleted with no claim lost?

`deletable = true` when the response contains at least one **passage** whose
removal would leave every claim the response makes still made.

Two definitions carry the whole construct, and both exist to remove the
arbitration `restates` needs:

**A passage is one complete sentence or more.** Not a clause, not a phrase.
Delete whole sentences, list items, paragraphs, or a heading together with its
body. A sentence that must be rewritten rather than removed is not a deletable
passage, and the response is not `true` on account of it.

**A claim is anything a reader could act on or disagree with.** An assertion
about the code, a recommendation, a priority ("fix this first"), a scope bound
("only on the write path"), a reason, a risk, a number. Ceremony is not a claim:
"Here's what I found", "Let me know if you want more", "Great question".

So the mixed closing sentence that `restates` cannot score is determinate here.
*"Just fix the data type before you go further."* names a point already made and
adds a priority. Deleting the sentence loses the priority, so it is **not**
deletable, and a response carrying only that is `false`.

## The kind field, and why it is separate from the verdict

Every `true` also records **why** the passage costs nothing to delete:

- `redundant` — every claim in the passage is made elsewhere in the response.
  This is the [#150] harm, and it is what `restates` was trying to measure.
- `claimless` — the passage makes no claim at all: a preamble, a closing offer,
  a sentence that announces what the next section will say.

Both are deletable, and they are recorded apart because they are not the same
finding. `claimless` is ceremony, which the rules already govern at `lite`;
`redundant` is the thing [#150] reported. The pilot is scored both ways, and the
split is what says whether this construct is measuring [#150]'s harm or a
broader one — see [`README.md`](README.md), where that prediction is registered
before any verdict was read.

## Does not count

- **A contrast that distinguishes two cases.** "A 401 from the refresh endpoint"
  against "a 401 from some other API call" is a distinction, and deleting either
  sentence loses it.
- **A cross-reference that names an earlier point without re-arguing it**, where
  the naming does work in its new position: "this is why the rollback is broken"
  asserts a link that was not asserted before.
- **A recommendation that follows from earlier analysis but was not itself
  stated earlier.** "Use NUMERIC" is a claim; deleting it loses it.
- **A summary the user asked for.** None of the four cases in this frame asks
  for one. Written down so it cannot be invented later.
- **Words that fix the order of steps** — "before", "after", "first". The rules
  protect them, and a step whose order is lost is a claim lost.

## Borderline convention

When it is arguable whether deleting the passage would lose a claim, label
`false`. Same direction as `restates`, and for the same reason: a metric tuned
to catch ambiguous cases reports harm a reader would not recognise.

The point of this construct is that the convention should fire *less often* than
it does under `restates`. If it fires just as often, B has bought nothing and
[#155]'s direction A is the only route left.

## What is deliberately not decided here

**How much is deletable.** The label is binary, matching `restates` so the two
can be scored against the same 120 hand labels. Whether a count of deletable
passages or a share of the response discriminates better is open, and these
labels cannot answer it.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
