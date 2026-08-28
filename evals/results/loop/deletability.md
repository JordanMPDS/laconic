# `deletable`: piloting a different construct for #150

**Status: B does not advance. All four registered predictions failed, and the
construct scores worse than the detector it was meant to improve on.** The
registration, the criterion and the shape assignment were committed at `5ee563d`
before any verdict was read.

## Why a different construct rather than a better detector

[#150] reports a model citing the length-scaling paragraph to justify 1,335
words of which about 230 restated claims the document had already made. Round 29
([`round-29.md`](round-29.md)) rejected the rules edit and established the harder
constraint: `output_tokens` cannot answer [#150] at any n, because the scoped
noise floor is 17.7% against a 17.2% harm and the floor is a per-cell standard
deviation rather than a standard error.

So [#150] needs a metric. [`restatement.md`](restatement.md) built one and parked
it at 55.3% precision out of sample. The reason it parked is specific and is what
this pilot responds to: **the dominant error class is a boundary the criterion
does not draw.** Fourteen of detector v1's 26 false positives are a closing
sentence whose first clause names a point already made and whose second attaches
a priority, a reason or a scope judgement that was not — *"Just fix the data type
before you go further."* `criterion.md` says a restatement is a passage that
"adds nothing that was not already there" and is silent on a sentence that is
half each. That is also the one seam where the human labelling is internally
inconsistent.

[#155] recorded two ways out. **A** sharpens the criterion, which invalidates all
120 labels and needs a full re-label to reach a projected ceiling near 72%.
**B** replaces the question with one that has less to arbitrate, and can be
piloted against the labels that already exist. [#155] recommends B first, and
this is B.

## The construct

> Is there a passage that could be deleted with no claim lost?

Two definitions carry it, and both exist to remove an arbitration:

- **A passage is one complete sentence or more.** Not a clause. A sentence that
  would have to be rewritten rather than removed is not a deletable passage.
- **A claim is anything a reader could act on or disagree with** — an assertion,
  a recommendation, a priority, a scope bound, a reason, a risk, a number.

The mixed closing that `restates` cannot score becomes determinate: deleting
*"Just fix the data type before you go further."* loses the priority, so it is
not deletable. Full rule in
[`deletability/criterion.md`](deletability/criterion.md).

Every `true` also records **why** the passage is free to delete —
`redundant`, meaning every claim in it is made elsewhere in the response, or
`claimless`, meaning it makes no claim at all. They are recorded apart because
they are not the same finding: `redundant` is [#150]'s harm, and `claimless` is
ceremony, which the rules already govern at `lite`.

## What this pilot can and cannot say

**It cannot publish a validated precision.** `criterion.md` for `deletable` was
written after reading the classification of all 26 of v1's false positives across
both batches, so every figure here is in-sample in the design sense. This is the
same constraint [`restatement.md`](restatement.md) records for a hypothetical
`restates` v2, and it does not go away by changing the question.

**The labels are `restates` labels.** They answer a different question, so
agreement with them is a yardstick, not a ground truth. Two consequences were
registered in advance:

- A `deletable=true` on a claimless passage scores as a false positive against
  these labels however correct it is. That is why `kind` exists and why the
  pilot is scored on the `redundant` subset as well as pooled.
- A response whose only restatement is half a sentence is a hand-label `true`
  that this construct is designed to call `false`. Recall must fall somewhat for
  the construct to be working.

**What it can do** is decide whether B earns a third labelled batch — a fresh
draw, labelled blind under this criterion, after this detector is frozen. That
is the only thing that could validate it.

## The four predictions, registered at `5ee563d`

| # | prediction | bar |
|---|---|--:|
| 1 | mixed-closing false positives that go clean | ≥ 10 of 14 |
| 2 | precision on the `redundant` subset, batch 2 | > 55.3% |
| 3 | responses whose only `true` is `claimless` | ≤ 15% |
| 4 | recall on the `redundant` subset | ≥ 70% |

**Decision rule, fixed in advance.** All four hold: B earns a third labelled
batch. Any one fails: B does not advance on this evidence, and the
recommendation reverts to [#155]'s direction A or to leaving the metric parked.

## Results

120 calls, $11.83, no failures. Scored against the same hand labels, the same
two batch directories, and the same scorer that reads v1 at 74.2% and 55.3%.

### Every prediction failed

| # | prediction | bar | read | |
|---|---|--:|--:|---|
| 1 | mixed-closing false positives cleared | ≥ 10 of 14 | **8 of 14** | fails |
| 2 | precision, `redundant` subset, batch 2 | > 55.3% | **40.9%** | fails |
| 3 | responses whose only `true` is `claimless` | ≤ 15% | **35.0%** | fails |
| 4 | recall, `redundant` subset, batch 2 | ≥ 70% | **36.0%** | fails |

The decision rule registered in advance was that all four had to hold. **B does
not advance on this evidence.**

### It is worse than v1 on the same labels, scored the most generous way

Counting *either* kind as a positive — which forgives the construct for finding
ceremony where the labels are about redundancy:

| | precision | recall | F1 |
|---|--:|--:|--:|
| `restates` v1, batch 2 | 55.3% | 84.0% | 66.7% |
| **`deletable`, batch 2** | **51.2%** | 84.0% | 63.6% |
| `restates` v1, pooled | 63.8% | 86.3% | 73.3% |
| **`deletable`, pooled** | **50.0%** | 80.4% | 61.7% |

Counting only `redundant` — the [#150] harm — it carries no signal at all:
pooled precision **40.5%** against a base rate of 42.5%, and detector-positive
against detector-negative is Fisher **p = 0.74**. A detector that flipped a coin
would do as well.

**And it is close to saturation.** `deletable` fires on **84 of 120** responses,
70.0%, against a hand-label rate of 42.5%. `restatement.md` registered the
saturation test before any of this existed: a label that fires on nearly every
long response cannot move, and 70% is most of the way there.

### Why: the question admits ceremony, and the seam it was written for holds

**42 of 120 responses have a `claimless` passage as their only deletable one,
and 33 of those 42 are `walkthrough`.** The quote is almost always a one-line
lead-in:

```
Here's the flow:
Here's the flow as written:
Here's the complete token refresh flow in auth.js:
```

Deleting that sentence loses no claim, so `deletable` is correct under its own
criterion. But `restates` excludes exactly this — *"a heading, label or lead-in
that announces what follows"* — so every one of them is scored as a false
positive here, and would be a false positive against [#150]'s harm too. [#150]
is about a document making a claim twice, not about a lead-in.

The damage is concentrated where the lead-ins are. Excluding `walkthrough`,
pooled precision is **31.0%**; on `walkthrough` alone it is 66.7%, and only
because 28 of its 43 responses are hand-labelled `true` anyway.

**The model split gets worse, not better.** `deletable` fires on 68.8% of sonnet
responses against a 25.0% hand rate, for **31.8% precision**; haiku reads 67.5%.
v1's stratum-dependent bias was already the hazard `restatement.md` flagged, and
this construct widens it.

**And the seam B was written to resolve only half-resolved.** 8 of the 14
mixed-closing false positives went clean, which is the whole-sentence unit doing
what it was designed to do: deleting *"Just fix the data type before you go
further."* loses the priority, so it is not deletable. The other 6 came back as
`redundant` — the model judged the second clause not to be a claim. Sharpening
the *unit* did not remove the arbitration; it moved it from "does this add
anything" to "is that clause a claim".

### One confound, named, and why it does not rescue the result

The reply shape asks for **one** passage and **one** kind. A response containing
both a lead-in and a real restatement is reported as `claimless`, so the
`redundant` subset loses it: 24 of the 42 claimless-only responses are
hand-labelled `true`. Predictions 2 and 4 are therefore lower bounds on the
construct rather than measurements of it.

It does not rescue anything. The pooled scoring above ignores `kind` entirely,
which forgives that confound completely, and `deletable` still reads 51.2%
against v1's 55.3% out of sample and 50.0% against 63.8% pooled.

## What this says for [#150] and [#155]

**Direction B is closed on this evidence.** Replacing "does this restate?" with
"could this be deleted?" broadens the construct instead of sharpening it: it
admits ceremony, which is a different harm the rules already govern at `lite`,
and it leaves the mixed-closing arbitration in place under a new name.

**One piece is worth keeping, and it belongs to direction A.** The whole-sentence
unit cleared 8 of 14 mixed closings on its own. If [#155]'s direction A is ever
run — sharpen `criterion.md`, re-label all 120, freeze a v2, draw a third batch —
the sharpening it should carry is *the deletion unit is one complete sentence or
more*, stated in the criterion rather than left to the labeller. That is the part
of B that worked, and it costs nothing to import.

**A byproduct worth its own issue, not a metric yet.** 33 of 43 `walkthrough`
responses open with a lead-in that announces what follows, and `lite` bans
preamble in as many words: *"Do not restate the question, announce what is about
to happen"*. Unlike restatement, that shape has a surface form a regex could
reach, which is what made `asks_back` free to re-score across 27,291 stored runs.
Nothing here measures it — no one hand-labelled ceremony, and these 42 verdicts
are detector output — so it is an observation, and it would need the same
criterion-first, label-blind, freeze-then-draw sequence as everything else.

## Reproducing

```sh
python3 evals/results/loop/restatement/score_detector.py --verdicts verdicts-deletable.json
python3 evals/results/loop/restatement/score_detector.py --verdicts verdicts-deletable.json --kinds redundant
python3 evals/results/loop/deletability/compare.py            # predictions 1 and 3
```

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
