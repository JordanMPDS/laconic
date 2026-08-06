# Loop round 06 — pending

Designed by an eleven-agent brainstorm (five proposal lanes, a ranking judge,
four adversarial skeptics, one synthesis) over the round-05 evidence. The
winning path pairs an instrument change, committed and tested before this
hypothesis could be scored by it (`c1ef792`), with one edit to the three
never-cut bullets whose cases carry the compression gap.

## Hypothesis

Written before the round was generated:

> Editing the requested-explanation, ordered-instructions, and bad-news
> bullets of the never-cut section (rules/laconic.md:25-30) so each bullet
> grants its protection and names its stop in the same sentence should move
> `output_tokens` on `badnews`, `ordered-steps`, and `walkthrough` downward in
> all six case/model cells.

Pre-registered arithmetic, so a rejection is informative: acceptance needs a
6-of-6 sweep (two-sided sign_test(6, 6) = 0.031 clears alpha; 5 of 6 = 0.219
fails) AND the scoped median of cell medians falling from 856 by more than the
scoped floor of 138.5 tokens — a new scoped median at or below 717 — which
requires `ordered-steps`/sonnet (1059) or `walkthrough`/haiku (1163) to land
at or below roughly 850, a 20–30% cut of backfill mass, not just a trailing
sentence. Replaying round 05's deltas through this gate scores 3 of 6 with a
−18.5 shift: that is the prior this edit must beat, and a 186-token shift is a
predicted rejection, not a surprise.

Target: `output_tokens --target-cases badnews,ordered-steps,walkthrough`
(6 cells). Fatal conditions stay round-wide: `never_cut_failures`,
`quality_fails`, `safety_fails`, `violations_total` each reject alone.

## The instrument, first

report.py refused every scoped `output_tokens` target on 4-cell arithmetic
(sign_test(4, 4) = 0.125 can never reach alpha). That reasoning is correct and
now has its true boundary: a scope is refused under 6 cells — with the
arithmetic printed — and offered from 6 up, running the same two-estimator
gate (two-sided sign test plus a median-shift floor) over the scoped cells,
with the round-wide cell count and p disclosed beside the scoped line. The
scoped noise floor is built by the identical estimator behind `NOISE`'s 209 —
the median per-cell stdev over the scoped **sonnet** cells of the baseline
snapshot (verified: 209 is round-01's median sonnet per-cell stdev, 208.7) —
which for `badnews`, `ordered-steps`, `walkthrough` is **138.5** (sonnet cell
stdevs 75.8, 138.5, 1519.1). Not the all-cells median of 119: mixing haiku
cells into the estimator changes the construction the 209 uses and lowers the
floor, which is alpha-shopping baked into the gate; a skeptic killed that
figure and the kill is built in. A scope with no sonnet cell refuses. Tests
pin the sweep-accept, the 5-of-6 rejection at p = 0.219, the inside-floor
rejection, the under-6 refusal, the no-sonnet refusal, and that a round-wide
fatal counter still rejects a passing scoped target.

Goodhart defence: the boundary and floor construction were committed in
`c1ef792` before this hypothesis existed to be scored; the case list is named
above, before generation; the fatal gates stay round-wide; the ledger records
the attempt either way.

## Root cause the edit addresses

On round 01's baseline, laconic's compression collapses exactly where the
never-cut section protects content in kind: `walkthrough` at 0.95/0.99 of
baseline's median tokens (haiku/sonnet), `ordered-steps` 1.00/0.80, `badnews`
0.94/1.01 — against 0.35–0.65 on `floor`, `silent-success`, and `decision`,
where nothing is protected. Round 05 established two things about this gap.
First, the padding is deletable when the exact behaviour is named: its
paragraph after the bullet list cut `walkthrough`/sonnet 3666 to 1719 with
every protected claim intact. Second, a stop stated two screens from the
license does not reach the other cells: `badnews` and `ordered-steps` sat at
−11/+21/+21/+21 while their transcripts kept the padding by changing form —
round 05's `badnews`/haiku reps end "What would you like to do?" where round
01 had "Want me to look at the billing code?", and `ordered-steps` replaced
its banned trailing offers with "Key benefits" recaps, Auth0/Okta name-drops,
and trade-off elaboration — and the paragraph's "no tour of code the question
did not ask about" pressed `stale-cache`/sonnet's diagnosis onto the wrong
cause, quality 2 to 5. This round moves the stop inside the bullet that grants
each protection, in that content kind's own vocabulary, so a model composing a
bad-news reply finds "name every failure, then stop" in the same sentence as
the license instead of a bare bullet it reads as licensing the whole response.
It closes the question-form loophole by naming the class ("What would you like
to do?" is the same offer in question form), bars the ordered-steps backfill
rather than the already-dead trailer ("after it, nothing the question did not
ask"), and draws the line round-05.md said was missing by anchoring the tour
ban to answer-relevance and licensing diagnosis outright: reading the evidence
that decides between causes is part of the answer, never a tour — so
`stale-cache`'s response-headers.txt is licensed by construction, not by the
model's early guess at the answer.

## The edit

The three consecutive bullets at rules/laconic.md:25-30 became:

> - Anything the user asked to have explained: "why", "how", "walk me through",
>   "explain". Protection covers the explanation's claims, not the prose around
>   them: cover every branch the question names, then end — no recap of what was
>   just explained, no tour of code the answer does not rest on. Reading the
>   evidence that decides between causes is part of the answer, never a tour.
> - Ordered instructions: every step, and the words that fix their order
>   ("before", "after", "first"). Give the steps once and end on the last one:
>   after it, nothing the question did not ask — no recap of the sequence, no
>   benefits or trade-offs of the procedure just given, no follow-up question.
>   A confirmation before a destructive action is never a follow-up question.
> - Bad news: a failure, a broken test, a limit hit, a thing not done. Omitting
>   it is not terseness. Name every failure, then stop: the failures are the
>   answer, and a closing offer softens nothing — "What would you like to do?"
>   is the same offer in question form.

Grafts from losing proposals, per the synthesis: the question-form closure and
the destructive carve-out come from the ceremony-only lane; the instrument
specification comes from the instrument-first lane, corrected to the
sonnet-consistent floor after its own skeptic killed the 119 figure.

Known risks, stated before the round: the round-wide fatal lotteries
(`conditional`/sonnet dropping "leak", `destructive`/haiku dropping
"sessions", `stale-cache`/haiku's 7-of-20 instability, `walkthrough`/haiku's
arrow swings) can reject any round regardless of the edit; `badnews`/haiku is
the weakest sweep cell — its median rep ends in diagnosis, not an offer, so
"the failures are the answer" has to deprotect the cause-guessing wrap-up to
give that cell room.

## Rounds compared

| | round 01 | round 06 |
|---|---|---|
| snapshot | `evals/snapshots/loop/round-01.json` | `evals/snapshots/loop/round-06.json` |
| `rules_cksum` | 1830906901 | 2779121711 |
| rules | master | master plus the per-bullet stops |
| judgments | `round-01-judgments-v2.json` (current criteria) | `round-06-judgments.json` |

Round 01 is master's rules exactly, which is why no baseline was regenerated.
Controls are carried in both rounds; none of them takes rules in its system
prompt.

## Result

Pending.
