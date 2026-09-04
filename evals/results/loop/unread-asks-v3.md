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

---

# Batch 3: the bar fails, and v2 fails with it

**The registered bar was fresh precision above 73.7% and fresh recall no worse
than 87.5%. v3 reads 70.0% and 58.3%. It is not promoted.**

80 responses drawn with seed 153 from the same eight snapshots and the same
`laconic`/`sonnet`/`design-*` population as both earlier batches, disjoint from
all 140 already labelled, out of a pool of 1,220. Labelled blind from `blind.md`
under batch 2's rule verbatim, **before either detector was run on it**.

| batch | detector | precision | recall | F1 |
|---|---|--:|--:|--:|
| 2 (published) | v2 | 73.7% | 87.5% | 80.0% |
| **3 (fresh)** | **v2** | **66.7%** | **50.0%** | **57.1%** |
| **3 (fresh)** | **v3** | **70.0%** | **58.3%** | **63.6%** |

**v3 beats v2 on this batch on every measure** — one more true positive, one
fewer false negative, the same three false positives — and both are far below
what batch 2 said either was worth.

## The result that matters is not v3's

**v2's published out-of-sample figure does not replicate.** 73.7%/87.5% on batch
2 against 66.7%/**50.0%** on batch 3, on the same population by the same drawing
method. Recall nearly halves.

[#153] treats 73.7% as v2's honest number, earned by freeze-then-draw, and it
was — for that draw. A second fresh batch says the quantity itself moves a great
deal between samples, which is a different and worse problem than v3 failing a
bar.

## The leading alternative explanation, and it is not detector quality

**These are my labels, not the original labeller's**, and the two may not draw
the same line. Three things point that way and one points against:

- **The base rates differ**: 12 of 80 here against 16 of 80 on batch 2, 15%
  against 20%.
- **The case mix differs.** Batch 3 drew 11 `design-alerting` and 13
  `design-audit-log`; batch 2 had none of the first and 4 of the second. Those
  cases end in impersonal "Left out:" notes rather than direct questions.
- **The rule's own `_note` names this seam** — *"the borderline class in both is
  the 'fork posed then resolved for both branches' shape"* — and labelling batch
  3 needed two conventions to settle it, recorded in `labels.json`.
- **Against:** v3's five misses are shapes no version was built to catch, not
  borderline calls. *"I'd want to know if Cardstream offers webhooks before
  picking"*, *"I don't have that answer from what's here"*, *"the fork you'll
  need to resolve"*, *"worth checking that first"*, and *"What's the payment
  processor here — that determines…"* (which v3's wh-clause misses only because
  it requires the word "you" in the line). Those are hand-backs on any reading.

## What would separate them, and it is free

**Re-label batch 2 under the two conventions recorded here, and compare against
its stored labels.** If the labels agree, the drop is real and the instrument is
weaker than [#153] believes. If they disagree, the drop is a labeller effect and
both fresh figures are measuring the labeller as much as the detector.

### The check, run: the labeller explanation is refuted

**61 of batch 2's 80 responses re-labelled under batch 3's conventions**, without
consulting the stored labels. Nineteen were excluded as contaminated — this
session had already seen their labels while diagnosing v2's errors, and knowing
an answer is not a blind re-label.

| | mine | theirs |
|---|--:|--:|
| labelled `asks` | 13 / 61 (21.3%) | 13 / 61 (21.3%) |

**Agreement 59 of 61, 96.7%. Cohen's kappa 0.902.** The base rates are identical
to the response.

The two disagreements are both on the seam the rule's own `_note` names:

| id | theirs | mine | the sentence |
|---|---|---|---|
| F25 | ask | not | *"The two decisions that actually fork the design: token bucket … vs. fixed/sliding window … — token bucket is usually right"* — I read the last clause as resolving it |
| F58 | not | ask | *"worth knowing what's currently in front of `/v1` before picking that"* — inside a Left-out list, so their carve-out applies; I applied clause (c), instructing the reader to go determine something |

**So batch 3's drop is not a labelling artefact.** Two labellers applying the
same written rule to the same population agree at kappa 0.90 and disagree only
where the rule says it is ambiguous.

**One caveat on the check itself.** The 19 excluded items are not a random
nineteen — they are precisely the ones where v2 erred, which is where labelling
is hardest. Agreement was therefore measured on a slightly easier subset than the
full batch, and 96.7% should be read as an upper bound on inter-labeller
agreement rather than a point estimate.

### What that settles

**v2's published figure does not replicate, and the reason is the detector.**
73.7%/87.5% on batch 2 against 66.7%/50.0% on batch 3, drawn the same way from
the same population and labelled to a standard now shown to be reproducible.

[#153] records 73.7% as v2's honest out-of-sample number. It was honest, and it
was one draw. **Neither 73.7% nor 66.7% is v2's precision**; the two together say
the quantity moves by 7 points of precision and 37 of recall between samples, and
that is the number a decision about `unread_asks` has to be made against.

## What this does not change

Round 28 was scored through v2 and says so; nothing here re-scores it. But the
case for ever making `unread_asks` fatal is weaker than it was this morning, not
stronger — the counter's precision is now known to move by 7 points and its
recall by 37 between two fresh samples drawn the same way.

`detector_v3.py` stays in the tree, unpromoted, with its in-sample and fresh
figures both recorded. `report.py` is untouched and still calls v2.

[#153]: https://github.com/JordanMPDS/laconic/issues/153
