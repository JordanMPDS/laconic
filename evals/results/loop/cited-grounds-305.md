# Were the grounds asked for? [#305] item 1 is dead, and the residual is not

**Registration. Nothing below the results line has been computed.** This file,
the three `cited-*` cases, their scorer and the layout test that holds the
triples together are committed in one commit before any generation, following
[round 38](round-38.md), [`true-premise-136.md`](true-premise-136.md) and
[`closing-recap-305.md`](closing-recap-305.md).

**This is not a round.** It proposes no rule edit, takes no row in
[`LEDGER.md`](LEDGER.md), and spends no [`candidate-due.sh`](../../../tools/candidate-due.sh)
allowance — that script reads `round-NN.md` and this is not one. Round 71
carried a candidate, so round 72 is still unregistered and may go either way.
What this buys is the answer to the question round 72 would otherwise have to
guess at.

Reproduce every number below with:

```sh
python3 evals/pilot/score_cited.py evals/snapshots/loop/cited-grounds-*.json
```

## Part 1: [#305] item 1 is dead on the instrument built for it

[#305] reports an eleven-word narrowing follow-up answered in 309 words, and
its item 1 proposes a rule against **closing a response with a recap of its own
opening**: the answer is stated once, and if restating the lead feels
necessary, the middle is what should shrink.

Three routes to test that have now closed.

1. **A lexical recap detector.** [`closing-recap-305.md`](closing-recap-305.md)
   built one and it inverted on the contrast-versus-recap pair, at 12%
   precision. Every lexical signal gets both directions backwards, which the
   containment probe demonstrated on exactly that pair.
2. **A judged redundancy verdict.** [#155]'s consensus pass lifted the oracle
   ceiling from 78.3% to 89.7% precision with six labellers, and failed its
   registered mechanism bar: the consensus set agrees with the two committed
   hand-label sets no better than those two agree with each other. Its
   registration committed in advance to redirecting rather than opening a
   fourth attempt.
3. **A fixture that makes the correct closing knowable.** Named in advance by
   `closing-recap-305.md` as the route left:

   > an answer where the right last paragraph is empty, so a closing paragraph
   > of any kind is the defect and no semantic judgement is needed to say so.

   [`true-premise-136.md`](true-premise-136.md) built it, and
   [round 71](round-71.md) ran on it.

**Route 3 is closed by round 71's own committed data, at no cost.** 300 haiku
responses on the three `settled-*` cells — 150 at master rules before the
round, 150 on the edit it accepted — sentence-classified by role:

| | control | round-71 edit |
|---|--:|--:|
| responses | 150 | 150 |
| median prose words | 97 | **79** |
| **median paragraphs** | 2 | **1** |
| closing paragraph restates the decision's status | 44.7% | **24.7%** |
| share of words: the first sentence, which is the verdict | 2.3% | 2.6% |
| share of words: **citing grounds out of the record the user read** | 72.1% | **76.7%** |
| share of words: restating the decision's status | 7.1% | 7.7% |
| share of words: everything else | 18.5% | 13.0% |

```sh
python3 evals/pilot/score_cited.py \
  --residual-control evals/snapshots/loop/round-71-{control,repl-control}-{1,2}.json \
  --residual-edit    evals/snapshots/loop/round-71-{edit,repl-edit}-{1,2}.json
```

Round 71's specimen cut the closing recap nearly in half as a side effect it
never claimed: the median response is now a **single paragraph**, so on half of
them there is no closing to remove. What is left that a recap clause could
reach is 7.7% of the words at a 24.7% fire rate. A clause that worked perfectly
would move the registered endpoint — the per-cell median — by approximately
zero, because the median response no longer has the shape the clause describes.

So item 1 is not waiting on a candidate round scoped to haiku, which is what
[#305]'s last comment said it was waiting on. It is waiting on nothing. The
instrument that was built to make it testable measured it and found the
behaviour it targets is not where the words are.

**Items 2 and 3 are untouched by this.** Item 2 — naming the narrowing
follow-up — is cross-turn and still shares [#298]'s instrument problem. Item 3
is the `length scales to the request` question and [#270] measured six clauses
at zero.

## Part 2: what the residual is, and the question that decides whether it is harm

Three quarters of the surviving words are the model reading the decision record,
confirming, and reciting the record's reasoning back to a user who has just
read it. A median edit-side response, at 79 words:

> Yes, exactly. The ADR explicitly states that tax rounds at the line level in
> `tax.py:line_tax`, and the invoice total is the sum of those rounded line
> taxes with no second rounding. The one-cent difference between that sum and
> what you'd get by computing tax on the summed subtotal is a documented,
> expected consequence — not a bug. On a 40-line invoice it happens about a
> third of the time. Reconciliation treats it as matched, and support macro 212
> covers the customer question.

Whether that is harm is genuinely open, and the endpoint cannot settle it:

- **It is surplus by construction.** The fixture's complete answer is one word.
  The user states the conclusion in the question, so the grounds are
  re-derived, not supplied. That is [#136]'s reported harm exactly.
- **It may be the check.** The user asked a model to verify a claim against a
  file. Citing what the file says is the evidence the check happened, and a
  rule that suppressed it would be buying an unchecked "Yes."

Round 71's own disclosures point at the second reading. Its round-wide
`quality_fails` rose +9 with the rise concentrated in the stratum the specimen
is an instance of, and the reserved design question came out worse at
p = 0.3034. Round 71 said in its own words that the next round to touch the
never-cut block should look here first.

**A candidate round that targets grounds citation without settling this is a
round that might be optimizing against the model doing its job.** That is what
this document buys the answer to.

## The design

Three new pilot cases, `cited-{retention,failover,rounding}`. Each is its
`settled-*` twin's prompt with **one sentence added** — *"Quote the part of the
record that settles it."* — over the same fixture by symlink, stating the same
true premise, ending in the same `Don't edit anything.` form.
`tests/test_evals_layout.sh` holds each triple to that contract, so a later
edit to one member fails the suite rather than silently turning the contrast
into a comparison of two different questions. Nothing joins the scored suite,
`cases_cksum` does not move, and no fatal counter gains an unseeded cell.

The contrast is **within one arm**: `laconic` at the rules on `master`, which
include round 71's specimen, generated in a single `run.py` invocation so both
families interleave and share the era, the CLI release and the batch. There is
no arm comparison here and therefore no control worktree.

```sh
python3 evals/bench/run.py --arms laconic --reps 25 --concurrency 1 \
  --cases-dir evals/pilot \
  --cells 'settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,cited-retention:haiku,cited-failover:haiku,cited-rounding:haiku,settled-retention:sonnet,settled-failover:sonnet,settled-rounding:sonnet,cited-retention:sonnet,cited-failover:sonnet,cited-rounding:sonnet' \
  --snapshot evals/snapshots/loop/cited-grounds-main.json
```

300 generations, no judge call, no label. About $13.65 at the rates in the loop
skill — haiku $2.40 and sonnet $11.25.

### The endpoint

Prose words by `metrics.score`, one median per (stem, model) cell, exactly the
endpoint round 71 was scored on. The test is the **stratified one-sided
permutation** round 71 registered, imported from `score_settled` rather than
rewritten: the statistic is the mean over cells of (settled median − cited
median), the family label is permuted within each cell so cell composition is
held fixed, and no single fixture can carry the result by being long. Seed 305,
200,000 resamples.

Three conditions, all registered, and a model is **responsive** only if it
meets all three:

1. The permutation clears **p < 0.05**, one-sided in the direction of
   responsiveness.
2. The mean shift beats a **measured floor** — the median per-cell stdev of the
   settled side, the same estimator the scoped token floor and [#49]'s turn
   floor are built from, taken from this batch and never a published constant.
   Without it a permutation on cells with little within-cell spread calls a
   one-word difference significant, and a one-word shift is not a model
   responding to a request.
3. Every voting cell moves the same way.

[#131] stratification and [#209] mixture apply unchanged, through
`score_settled.votes`: a cell whose reading rate differs between the two
families does not vote, and a cell holding mutating runs does not vote. Both
are reported whether or not they are zero.

### Sonnet is the fixture-validity control, not a second target

Haiku alone cannot separate *"haiku emits the grounds regardless"* from *"the
added sentence does not ask clearly."* Sonnet answers `settled-*` at 0 of 45
above 80 prose words with an upper bound of 7.9%, so it has headroom in the
direction the added sentence points. If sonnet lengthens and haiku does not,
the sentence asks and haiku is not listening.

### The verdict, registered in advance

- **Responsive** — haiku meets all three conditions. A `settled-*` answer's
  grounds are at least partly a response to the question, and **no rule edit is
  proposed against grounds citation on this instrument.** [#136]'s residual
  stops being obviously surplus and the cluster needs a different endpoint
  before it spends another round.
- **Unresponsive** — haiku does not, **and sonnet does.** The added sentence
  demonstrably asks for grounds and haiku emits them either way, so the
  `settled-*` residual is unrequested by measurement rather than by argument.
  A candidate round may target it, and this document is what it cites.
- **Uninformative** — neither model meets the conditions. The prompt
  manipulation is not shown to ask for anything, nothing is concluded about
  haiku, and the next unit is a sharper ask rather than a rule edit.

`score_cited.py` holds all three branches with a selftest over the floor, the
permutation's direction, both refusal paths and the verdict, and
`tests/test_bench.py` already runs every pilot scorer's selftest in CI.

### A secondary, free

The confirmation rate on both families, off `score_premise.verdict`. A `cited-*`
case that stops being answered as a confirmation is a different question rather
than the same one asked differently, and the table prints the Wilson interval
whether or not it moves.

### Pre-mortem

Registered before the numbers, per step 5 of the loop skill and [#26]. The way
I expect this to fail is **uninformative**: a model that already recites the
record has nothing left to add when asked to recite the record, so both
families land at the same length for the uninteresting reason that the ceiling
is the fixture rather than the request. If that happens the discriminator is
the ask, not the model, and the fix is a sharper one — asking for a verbatim
quotation with line numbers, which has a form the response either carries or
does not. The second most likely failure is the reading-rate refusal: an added
sentence naming *the record* could raise the read rate on `cited-*` above
`settled-*`, which crosses [#131]'s stratum and refuses the cell, and three
refused cells is no test at all.

## Where the design came from

`bash tools/consult.sh` was run against the draft before any of this was
written. One of three targets answered — `kimi`, via the Kimi Code CLI —
and two of its points are in the design:

- **It agreed route 3 is dead and said why in the same terms the data does:**
  the 97-to-79 win came from collapsing multi-paragraph structure, not from
  suppressing a closing recap, and conditioning on multi-paragraph responses to
  rescue the clause is post-hoc conditioning on the symptom. That is the
  argument Part 1 makes for spending no generations on item 1.
- **The whole of Part 2's design is its answer to question 2.** Asked whether
  any deterministic endpoint separates "cited the grounds because it checked"
  from "recited the grounds the user already had", it said no endpoint reads it
  off the text — three judged attempts confirm that — and that *"the only clean
  separation is a fixture property: prompt for a bare confirmation in one
  condition and for explicit citation in another, and measure whether the model
  follows the requested form."* The `cited-*` twin is that, and the reason it
  exists.

Its third point was not adopted here. It proposed targeting the reported
failure directly with a rule about narrowing follow-ups. That is [#305]'s item
2, it is cross-turn, and it shares [#298]'s instrument problem — the same wall
this cluster has hit four times. It is recorded because the reading is right
about where the user-visible harm is, and wrong only about what can currently
be measured.

`codex` and `deepseek` were asked and did not answer inside the timeout;
`deepseek`'s failure names a model-catalog mismatch rather than a timeout, and
is worth a look before the next consultation.

---

## Results

Generated 2026-09-21 in one `run.py` invocation: **300 runs, 0 failed**, all on
`claude` **2.1.278**, so no release boundary crosses this file. $7.47 —
haiku $2.04, sonnet $5.44.

## Verdict: **unresponsive**

Haiku fails all three conditions and sonnet meets all three, which is the
second of the three branches registered above. The added sentence demonstrably
asks for grounds; haiku emits them either way.

### Haiku does not move

| stem | n settled | n cited | settled median | cited median | difference | votes |
|---|--:|--:|--:|--:|--:|---|
| retention | 25 | 25 | 67.0 | 54.0 | **-13.0** | yes |
| failover | 25 | 25 | 94.0 | 98.0 | +4.0 | yes |
| rounding | 25 | 25 | 91.0 | 101.0 | +10.0 | yes |

Mean settled minus cited **-0.33 words**, one-sided p = 0.47630, 3 of 3 cells
voting. Measured floor **18.7 words**.

All three conditions fail, and independently. The permutation is nowhere near
alpha. The shift is 0.33 words against a floor of 18.7, which is to say it is
indistinguishable from nothing by an estimator built from this batch's own
spread. And the cells do not agree on a direction: retention falls 13 words
while the other two rise.

### Sonnet does

| stem | n settled | n cited | settled median | cited median | difference | votes |
|---|--:|--:|--:|--:|--:|---|
| retention | 25 | 25 | 1.0 | 26.0 | +25.0 | yes |
| failover | 25 | 25 | 32.0 | 58.0 | +26.0 | yes |
| rounding | 25 | 25 | 19.0 | 55.0 | +36.0 | yes |

Mean settled minus cited **-29.00 words**, one-sided p < 0.00001, 3 of 3 cells
voting, 3 of 3 rising. Measured floor **13.7 words**, cleared twice over.

The sentence asks, it asks clearly enough that a model with headroom answers
it, and it asks for about 29 words' worth. The fixture-validity control does
what it was put there to do.

### The pair that carries it

Sonnet, `settled-retention`, the median of 25:

> Correct.

Sonnet, `cited-retention`, the median of 25:

> Correct. Line 11: "The quarterly report reads `events_daily`. It does not
> read `events_raw`, and a re-run of a past quarter cannot be reconstructed
> from `events_raw`, because the rows are gone."

Haiku, `settled-rounding`, the median of 25, at 91 words:

> Yes, that's correct. Per ADR 021, tax rounds half-up at the line level in
> `tax.py:line_tax`, and the invoice total is the sum of those already-rounded
> line taxes with no second rounding. The document explicitly states that the
> one-cent difference between the summed line taxes and the tax computed on the
> invoice subtotal is expected output, not a defect—it occurs about a third of
> the time on a 40-line invoice and is accepted as the cost of meeting filing
> guidance that requires each line to show the exact tax charged for that line.

Haiku, `cited-rounding`, the median of 25, at 101 words: the same recitation
with a block quotation added in front of it, not in place of it.

Haiku is not withholding the grounds until asked and then supplying them. It
supplies them unasked, and when asked it supplies them twice.

## The refusals, both at zero

Registered to be reported whether or not they moved, and neither moved.

- **[#131] stratification.** Reading rate is 25 of 25 in all twelve cells, both
  families, both models. No cell crosses a stratum, so none is refused on that
  ground. The pre-mortem named this as the second most likely failure — an
  added sentence naming *the record* pulling the `cited-*` read rate above
  `settled-*` — and it did not happen, because the rate was already at ceiling
  on both sides.
- **[#209] mixture.** Zero mutating runs in all twelve cells. The
  `Don't edit anything.` form held across the manipulation.

## The secondary, unmoved

Confirmation rate is 25 of 25 in every cell, Wilson [86.7, 100.0] throughout.
Adding the sentence did not turn a closed confirmation into a different
question. The contrast is the same question asked two ways, which is what it
had to be for the primary to mean anything.

## What the reading rate settles, which the endpoint could not

Part 2 above left one question genuinely open: whether the grounds in a
`settled-*` answer are surplus or are *the evidence that the model checked*.
The endpoint was registered as unable to settle it. The refusal check settles
it anyway, as a side effect of being reported at all.

Sonnet opened the fixture in **25 of 25** `settled-retention` runs and answered
**"Correct."** — one word, no grounds. The check happened and left no trace in
the prose. So reciting the record is not what makes the check; the tool call
is, and the tool call is observable without it.

The limit on that: `grounded()` records that a tool was called, not that the
right content was verified — it is the same definition every round's reading
strata use, and it is evidence rather than proof. But the `cited-retention`
specimen quotes line 11 accurately, so on this fixture the two travel together.

## What this buys, and what it does not

**Bought.** The `settled-*` residual is unrequested **by measurement**. A
candidate round targeting grounds citation on these cases is no longer
optimizing against a model doing its job on the strength of an argument that
could go either way — the argument has a number now, and it is the one this
document was registered to go and get. A round that proposes such an edit
cites this file.

**Not bought.** This says nothing about whether suppressing the grounds is
*safe*. Round 71's disclosure stands unchanged: its round-wide `quality_fails`
rose +9 with the rise concentrated in this stratum, and its reserved design
question came out worse at p = 0.3034. A candidate round here inherits that and
has to carry a quality bound, not just a length target. "Unrequested" and
"harmless to remove" are different claims and only the first has been measured.

**Unchanged.** [#305] item 1 is dead, per Part 1, on data that already existed.
Items 2 and 3 are untouched. [#298]'s cross-turn instrument problem is still
the wall in front of item 2.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#270]: https://github.com/JordanMPDS/laconic/issues/270
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
