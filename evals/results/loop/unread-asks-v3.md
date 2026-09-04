# `unread_asks` detector v3: frozen, with its validation sample registered and not yet drawn

**Status: v3 is committed and every figure below is in-sample.** The third
sample is specified here and has not been drawn. That order is the whole point:
v2 read 93.1% precision in-sample against **73.7%** on a fresh batch, a 19-point
overstatement, and the only reason anyone knows that is that its freeze happened
first.

Answers step 1 of [#153].

## What v2 leaves

[#153] names two systematic error classes, and reproducing them exactly on the
80-response batch 2 confirms both:

- **All 5 false positives are a self-resolved fork.** F15 asks *"do you have (or
  can you add) an idempotency key on the charge call?"* and continues *"If yes,
  this is a straightforward reconcile-then-retry job. If the processor…"* The
  reader is not blocked, so nothing was handed back.
- **Both false negatives are hand-backs with no question mark.** F78 opens *"The
  fork I can't resolve without knowing your setup:"*; F06 ends *"Which database
  are you on, and roughly how many products — that decides which of the two to
  actually spec out."* with a period.

## What v3 adds, and nothing else

**(a) A question the answer resolves itself is not a hand-back.** Only the text
*after* the last `?` in the paragraph counts — a recommendation stated before the
question does not resolve it.

**(b) Two shapes of question-less hand-back.** An explicit unresolved dependency
(*"can't resolve … without"*, *"without knowing your …"*), and a wh-question
addressed to the reader that ends in a period or dash.

## Two constraints the design had to discover

Both were found by measuring rather than reasoning, and both are in the file's
comments so a v4 does not rediscover them.

**The wh-word must open the line.** A first draft allowed it anywhere, which
fired on any closing line containing "what" and "you" — *"Left out: … and what
'processing' looks like in the UI — those are the next layer down once you pick
sync vs async."* — and cost **11 false positives on batch 2 alone**.

**And it must not be followed by a colon.** A wh-phrase with a colon is a label:
*"**What you cache**: raw query rows vs. the fully-assembled page-data object."*
and *"What I'm leaving out: …"* both open a line with a wh-word and both report
rather than ask. Forbidding the colon removed the last two false positives
without losing either target.

## In-sample figures, which are not estimates

| batch | detector | precision | recall | F1 |
|---|---|--:|--:|--:|
| 1 (n=60) | v2 | 93.1% | 90.0% | 91.5% |
| 1 (n=60) | **v3** | **96.4%** | 90.0% | **93.1%** |
| 2 (n=80) | v2 | 73.7% | 87.5% | 80.0% |
| 2 (n=80) | **v3** | **78.9%** | **93.8%** | **85.7%** |

v3 dominates v2 on both batches and **adds no false positive to either**. On
batch 2 it removes F15 and catches both F06 and F78 — the three responses [#153]
names.

**Read these as designed-on, not measured.** v3 was written against batch 2's
errors and refined three times against both batches. v2's own history says what
that is worth: 93.1% in-sample became 73.7% fresh. The honest expectation for v3
is that its fresh precision lands below 78.9%, and the question the third sample
answers is by how much.

## The third sample, registered

> **Protocol.** `detector_v3.py` is committed in this PR, before any of the
> below. Then: draw a sample **disjoint from both existing batches** by the same
> unstratified simple random method `resample.py` implements, label it blind
> under the rule in `unread-asks-v2/labels.json` `_rule` — unchanged, so v2 and
> v3 are scored against the same definition — and only then score both detectors
> on it.

**Registered bar:** v3 is promoted only if its fresh precision exceeds v2's
73.7% *and* its fresh recall is no worse than v2's 87.5%. A trade in either
direction goes back to a v4 rather than shipping, because `unread_asks` is a
disclosure counter today and the case for making it fatal rests on precision.

**What promotion costs, unchanged from [#153]:** the published disclosure
re-scored across rounds 25 to 28; a new frozen copy with `tests/test_bench.py`'s
equivalence pin updated to it; and the overdispersion table recomputed, since
phi was 1.83 under v1 and 1.09 under v2 and most of that was v1's line-position
artifact moving between rounds.

## What is not claimed

Nothing about round 28, which was scored through v2 and says so. Nothing about
whether `unread_asks` should be fatal — 78.9% in-sample is not the number that
decides that, and the fresh figure is what this registration exists to buy.

[#153]: https://github.com/JordanMPDS/laconic/issues/153
