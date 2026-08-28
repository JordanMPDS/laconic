# `deletable`: piloting [#155]'s direction B

**Outcome: all four predictions below failed and B does not advance.** The
report is [`../deletability.md`](../deletability.md). Nothing in this file was
edited after the verdicts were read — a registration that moves is not one.

**Registration. Committed before a single verdict was read.** Everything below —
the predictions, the bar, and what the pilot is not allowed to claim — is fixed
in advance, because the criterion it tests was written after reading both
batches' errors and a number chosen afterwards would score whatever moved.

## Why this exists

[#155] parked `restates` at 55.3% precision out of sample and recorded two
directions. **A** sharpens `criterion.md`, which invalidates all 120 hand labels
and needs a full re-label to reach a projected ceiling near 72% — parity with
`unread_asks`, which
[`round-28.md`](../round-28.md) already registers as *"not obviously good enough
to gate on"*. **B** replaces the question. [#155] recommends trying B first,
because it can be piloted against labels that already exist.

This is that pilot. The construct is in
[`criterion.md`](criterion.md): *is there a passage that could be deleted with no
claim lost?*, with a passage defined as one complete sentence or more, so the
mixed closing clause that dominates v1's false positives has a determinate
answer instead of an arbitration.

## What is being measured, and against what

The same 120 responses, the same two batch directories, the same hand labels —
[`restatement/`](../restatement) and [`restatement-b2/`](../restatement-b2). No
new draw and no new labelling. The detector is new; nothing else is.

**The labels are `restates` labels.** They were written under a different
question, so agreement with them is a yardstick and not a ground truth for
`deletable`. Two consequences, registered here rather than discovered in the
results:

- A `deletable=true` on a **claimless** passage is scored as a false positive
  against these labels by construction, however correct it is. That is why
  `kind` is recorded and why the pilot is scored both pooled and on the
  `redundant` subset alone.
- A response whose only restatement is *half a sentence* is a hand-label `true`
  that `deletable` is designed to call `false`. Recall must fall somewhat for
  the construct to be doing its job. The question is how far.

## The bar this pilot has to clear

**These figures are in-sample in the design sense.** `criterion.md` was written
after reading the classification of all 26 of v1's false positives across both
batches, so a precision measured here is not a validated precision and this pilot
may not publish one as if it were. What it can do is decide whether B earns a
third labelled batch — which is the only thing that could validate it, and which
costs a fresh draw plus a fresh blind labelling pass.

Four predictions, and the decision rule that reads them:

| # | prediction | why it is the right test |
|---|---|---|
| 1 | **At least 10 of the 14 mixed-closing false positives go clean.** | This is the seam B exists to resolve. Deleting one of those sentences loses its priority clause, so the criterion answers `false` without arbitration. Fewer than 10 means the sharpened unit is not reaching the shape it was written for. |
| 2 | **Precision on the `redundant` subset, batch 2, beats 55.3%.** | v1's out-of-sample figure is the thing being improved on. Beating it in-sample is necessary and nowhere near sufficient. |
| 3 | **`claimless`-only `true` fires on no more than 15% of responses.** | Above that, B is largely measuring ceremony rather than [#150]'s harm, the label comparison stops meaning much, and the construct needs re-scoping before anything else. |
| 4 | **Recall on the `redundant` subset is at least 70%.** | v1 reads 84.0%. Some fall is the design working. A large fall means the whole-sentence unit misses most real restatement, and precision bought that way is not progress. |

**Decision rule, fixed in advance.** All four hold: B earns a third labelled
batch, drawn after this detector is frozen, and that batch is what a published
figure would come from. Any one fails: B does not advance on this evidence, and
the recommendation reverts to [#155]'s direction A or to leaving the metric
parked. The failure is reported either way — a pilot that only reports the
outcome it hoped for is not evidence.

## What this pilot is not

Not a gate, not a target, not a round. Nothing here scores a rules edit, and
nothing here changes `rules/laconic.md`. [#150] stays open on its own terms.

## Running it

```sh
python3 evals/results/loop/deletability/detector.py \
  --key evals/results/loop/restatement/key.json \
  --out evals/results/loop/restatement/verdicts-deletable.json

python3 evals/results/loop/deletability/detector.py \
  --key evals/results/loop/restatement-b2/key.json \
  --out evals/results/loop/restatement-b2/verdicts-deletable.json

python3 evals/results/loop/restatement/score_detector.py \
  --verdicts verdicts-deletable.json
```

120 calls at roughly $0.065 each. The verdicts land beside the key and labels
they are scored against, because that is where `score_detector.py` looks and a
third copy of the frame is a third thing to keep in sync.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
