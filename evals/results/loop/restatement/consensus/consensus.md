# Can `restates` be labelled at all? Six labellers, one sitting

**Registration. Nothing below the results line has been computed**, with the
exception of part A, which reads only files committed before today and is
printed in full here because it is the reason the bars are shaped the way they
are. The scripts, the bars and this document are committed in one commit before
any labelling pass runs.

This is not a benchmark round. It buys no generations, proposes no rule edit,
and writes no round document — `tools/candidate-due.sh` is untouched by it. It
is [#155]'s remaining half, taken as its own unit of work because
[round 70](../../round-70.md) said that is what [#150] is owed next:

> [#155]'s detector is parked at 55.3% precision and may not be promoted inside
> a round, so closing this needs that detector's precision raised first, as its
> own unit of work.

## What is already known, and what is left

[#155] asked to "sharpen the criterion, **or rethink the construct**". Three
things have been tried and all three are closed:

| attempt | result |
|---|---|
| lexical containment probe | fails in the **wrong direction** — a known-redundant closing recap scores 0.21, a known-dense contrast scores 0.40 |
| direction B, deletability | all four registered predictions failed; 51.2% against v1's 55.3% |
| direction A, sharpen the criterion | stopped at the labels: the criterion moves 14 of 60, the labeller alone moves 12 of 60 |

What direction A produced instead of a precision figure was a **ceiling**: a
detector is scored against one label set, so a second set drawn the same way is
the best any detector could read, and that is 78.3% precision. The 72% this
issue had been chasing was the label-noise floor all along.

Two routes remained. [#155]'s own words:

> - Two labellers with adjudication. Never tried here; the agreement between two
>   people at one sitting is a different quantity from one labeller twice,
>   months apart.
> - A positive condition that is a named fact rather than a judgement.

**This unit runs the first.** The second is addressed at the bottom, because
both consult targets independently called it dead and one of them supplied the
argument this repository had not written down.

## Part A, computed before the bars were set

```
  batch 2, criterion v1 twice: agreement 48/60 = 80.0%, kappa 0.584
  bootstrap 95%, by item:  [0.358, 0.781]   (too narrow: items cluster)
  bootstrap 95%, by case:  [0.184, 1.000]   (four clusters, so wide)
  oracle ceiling against the committed labels:
    precision 78.3% (n=23, Wilson 95% [58%, 90%])
    recall    72.0% (n=25, Wilson 95% [52%, 86%])
```

**The headline this issue has been reasoning from does not resolve.** `restates`
at 0.584 against `unread_asks` at 0.902 reads as a settled gap, and at four
source cases the interval around 0.584 runs to 1.000. The item-level interval
is the one a reader would compute by default and it is too narrow, because the
60 responses come from four prompts: 24 `walkthrough`, 17 `verdict-rollout`,
13 `verdict-experiment`, 6 `verdict-schema`.

That is what shapes everything below. **A design whose primary reading is a
kappa comparison at n=60 cannot fire**, so this one does not make that
comparison its bar.

## The design

Six independent labelling passes over batch 2's 60 responses. Every pass is a
fresh context, blind to every other pass, blind to both committed label sets and
to every detector artefact, under `criterion.md` **v1 unchanged**, all on the
same day and the same model. Each pass reads its own re-ordered copy of
`blind.md` from `shuffle.py`; pass 1 keeps file order so that one pass stays
directly comparable to the committed labels, which were written in id order.

**Six, and not two, because of what six buys that two cannot.** A pair is a 2x2
table and part A is what a 2x2 table resolves here. Six passes give each
response a vote count in 0 to 6, and the quantity the decision needs falls out
of that profile without a second experiment:

> Two disjoint triples, each adjudicated by majority, disagree on a response
> **if and only if** that response's six votes split 2, 3 or 4 true.

A response at 0, 1, 5 or 6 votes agrees across every way of splitting six
labellers into two triples, because a triple holding at most one minority vote
still reaches the same majority. So the adjudicated ceiling is set entirely by
the contested band, and that band is read off 360 votes rather than estimated
from one table. All ten disjoint splits are scored and averaged, not one
arbitrary split.

**Re-ordering is the only decorrelation applied, deliberately.** Varying the
model would measure a committee rather than the labeller whose drift
`labeller_drift.py` reports, and the comparison to 0.584 would not survive it.
Both consult targets said the same thing about order — free, and it breaks
anchoring on the first items and drift down a long file — and deepseek said
explicitly that a different model is a confound rather than a fix. The
correlation that re-ordering does **not** touch is the one that matters, and it
is handled by measurement rather than by design; see the next section.

## The bars

Both must clear.

1. **Level.** Mean adjudicated kappa over the ten disjoint splits **>= 0.80**.
   `unread_asks` ruled its labeller out at 0.902, and 0.80 is the conventional
   boundary below it.
2. **Mechanism.** The split-proof share — responses whose label is invariant to
   which three of the six adjudicate them — **>= 85%**, with a Wilson lower
   bound **>= 75%**.

**Both are point estimates with a Wilson bound, and not cluster intervals, and
part A is the whole reason.** At four clusters the interval spans [0.18, 1.00]
on a reading of 0.584. Gating on an interval that wide would be a decision rule
that can only ever return "inconclusive", which is the failure this unit exists
to avoid rather than repeat. The cluster interval is computed and printed beside
every figure as the honest width, and the adjudication gain is **disclosed
rather than gated** for the same reason.

The split-proof share is the bar that carries the resolution. It is a proportion
over 60 items rather than a difference of two kappas, so its Wilson interval
separates 60% from 90% where the kappa comparison separates nothing.

## What each outcome means, written before the passes run

- **Both bars clear.** Adjudication raises the ceiling. A consensus label set is
  the route for [#150], [#298] and [#305], at a stated cost of six passes per
  batch, and [#155]'s detector work resumes against consensus labels rather than
  single ones.
- **Either bar fails.** Adjudication does not deliver a label set a detector
  could be scored against. The judged-verdict route then needs a **different
  construct**, not a better protocol, and [#150], [#298] and [#305] are told so
  rather than left waiting on a fourth attempt at this one.

There is no third reading in which the number is encouraging and more labelling
is bought. Four attempts have now been made on this construct and each one
ended by naming the next; this one ends by deciding.

## The correlation problem, and the one signature that separates it

All six labellers are the same model under the same criterion, so their errors
need not be independent, and a majority over correlated errors buys less than
the arithmetic suggests. **Two triples could agree at 95% for the wrong reason.**

The obvious test does not work, and the reason is worth recording. Under
independent errors the 3-0 unanimity rate is predictable from the pairwise
agreement rate, so unanimity above that prediction looks like correlation — but
item difficulty is not uniform, and shared difficulty inflates unanimity exactly
the same way. deepseek made this point and the existing by-case drift table
already falsifies uniform difficulty: 0 of 13 and 0 of 6 in two cases against
5 of 17 and 7 of 24 in the other two.

What does separate them is the shape of the contested band, and it costs no
extra passes:

> A response the six split exactly 3-3, **where that 3-3 is itself a clean split
> into two internally unanimous triples**, is two systematic readings meeting.
> A response at 3-3 that splits every which way is one genuinely ambiguous item.

Both are counted. A clean-split share far above what exchangeable votes predict
indicts correlation, and the verdict is reported with that reading attached
rather than as a bare ceiling.

## Route 2 is closed here, on argument rather than on a pilot

Both consult targets were asked whether any deterministic positive condition for
redundancy escapes the inversion the lexical probe hit, and both said no.
deepseek's form of it is the one this repository had not written down:

> The contrast and the recap are the two hard directions and every signal gets
> both backwards. The contrast shares most words but asserts a new claim; the
> recap shares few words but asserts an old one.

That is not a threshold problem, and [PR #308] had already measured the same
shape from the other end: a closing-recap overlap detector built on exactly the
"named fact" that route 2 would reach for scored **12% precision**, and its
no-new-referents gate *inverted*, selecting for the largest false-positive class
instead of against it. Two independent probes on two constructs, both inverting
on the contrast/recap pair, is enough to close the route on argument. A third
pilot would buy the same finding a third time.

So if the bars below fail, what is left is not a better rule for this construct.
It is a different construct with a lexical signature — `closing_offers` reads
laconic 3.5% against baseline 13.1% at p = 8.6e-18 and needs no labeller at all
— and [#150], [#298] and [#305] should be pointed at that.

## Consulted

`bash tools/consult.sh` was run on this design before it was committed. codex did
not answer within the timeout. Adopted from **deepseek**: that the unanimity test
is unsound because it assumes uniform item difficulty; the internally-unanimous
versus internally-split localisation that replaces it; that a different model is
a confound rather than a decorrelation; that the intervals must be cluster
bootstraps at the case level and will be wider than the naive ones; and the
route 2 closing argument quoted above. Adopted from **kimi**: that response order
should be shuffled, and that any stopping rule has to be stated against an
interval rather than a point difference — which is what sent the bars onto the
split-proof share, the one quantity here that an interval can separate. Both
targets recommended opposite headline actions — deepseek said do not spend the
six passes because the comparison cannot fire, kimi said run it coarse — and the
design resolves that by moving the bar off the quantity deepseek showed cannot
fire and onto one that can.

## Reproduce

```sh
python3 evals/results/loop/restatement/consensus/shuffle.py --out /tmp/restates-consensus
python3 evals/results/loop/restatement/consensus/consensus.py
```

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
[PR #308]: https://github.com/JordanMPDS/laconic/pull/308
