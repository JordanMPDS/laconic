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

---

# Results

Six passes, 2026-09-20, opus, one sitting, run in parallel so that no pass could
see another's output. Every pass returned all 60 ids as JSON booleans. Full
output from `consensus.py`; nothing below was computed before the passes ran.

## The verdict, as registered

| bar | reading | |
|---|---|---|
| 1, level: adjudicated kappa >= 0.80 | **0.807** | PASS |
| 2, mechanism: split-proof >= 85%, Wilson lower bound >= 75% | **83.3%**, lower bound **72.0%** | **FAIL** |

**A bar fails, so the registered reading stands: this protocol does not hand
[#150], [#298] and [#305] a label set today.** Those three are redirected rather
than left waiting, which is what the registration committed to.

Both bars landed within a point or two of their thresholds, and that is worth
stating plainly rather than rounding away. The level bar cleared at 0.807
against 0.80, with a cluster interval of [0.708, 0.948] straddling it.

## The vote profile

| votes for `restates` | responses | |
|---:|---:|---|
| 0 of 6 | 18 (30.0%) | unanimous false |
| 1 of 6 | 7 (11.7%) | split-proof |
| 2 of 6 | 6 (10.0%) | **contested** |
| 3 of 6 | 3 (5.0%) | **contested** |
| 4 of 6 | 1 (1.7%) | **contested** |
| 5 of 6 | 6 (10.0%) | split-proof |
| 6 of 6 | 19 (31.7%) | unanimous true |

61.7% of the sample is unanimous and 83.3% is split-proof. The construct has a
large decidable core; what it does not have is a decidable rim.

## Adjudication works, and the size of it is not in doubt

| | agreement | kappa |
|---|--:|--:|
| one pass against one pass, 15 pairs | 83.6% | **0.675** (range 0.367 to 0.832) |
| majority-of-three against the disjoint other three, 10 splits | 90.3% | **0.807** (range 0.707 to 0.899) |

**Gain +0.132 kappa, cluster bootstrap 95% [+0.080, +0.180].** That interval
excludes zero at four clusters, which is more than any other comparison in this
issue's history has managed. And the directly comparable ceiling moves a long
way:

| oracle ceiling — the best any detector could read | precision | recall |
|---|--:|--:|
| against a single label set (part A) | 78.3% | 72.0% |
| against a consensus-of-three label set | **89.7%** | **91.1%** |

## Two things the registration got wrong, recorded rather than quietly fixed

**Bar 2 was a conservative proxy for bar 1, not an independent requirement.**
The split-proof share is a *lower bound* on adjudicated agreement — contested
responses still agree on most splits, which is why 83.3% split-proof produces
90.3% agreement. Registering both is one quantity gated twice, with the proxy
set at a level that implies a stricter requirement than the kappa bar it stands
in for. The bar is honoured because it was registered; the sentence attached to
it in the registration — *"adjudication does not deliver a label set a detector
could be scored against"* — does **not** survive the 89.7% ceiling beside it,
and it should not be quoted as a finding.

**The registered correlation signature is vacuous.** It proposed counting
responses split 3-3 whose votes fall into two internally unanimous triples.
Every 3-3 response is one: the three who voted true *are* a triple, and the
three who voted false are its complement. All 3 of the 3-3 responses "passed"
the test, and the test cannot return anything else. It is printed as a null
result rather than deleted, and replaced below.

## What the disagreement actually is, and this is the useful finding

Per-pass `true` counts: **24, 24, 27, 29, 34, 38** of 60 — a spread from 40.0%
to 63.3%.

Permuting labels *within* each response across the six passes holds every vote
count fixed and makes the passes exchangeable by construction. Under that null
the observed spread of 14 has **p = 0.0002** over 20,000 shuffles.

**The six labellers differ by threshold, not only by which hard responses they
called.** That is a different diagnosis from "the construct is ambiguous", and
it is one the criterion is supposed to prevent: `criterion.md`'s borderline
convention — *"when a passage is arguably either a restatement or a new claim,
label `false`"* — exists precisely to pin the threshold, and six readers of it
landed 23 percentage points apart. Majority voting cancels part of a threshold
spread, which is where the +0.132 comes from.

## The caveat that keeps this from being a green light

| | agreement | kappa |
|---|--:|--:|
| the two committed hand label sets, against each other | 80.0% | 0.584 |
| consensus-of-six against the committed labels | 75.0% | **0.489** |
| consensus-of-six against the v1 re-label | 81.7% | 0.622 |

The committee agrees with itself at 0.675 pairwise and with the earlier hand
sets at 0.489 and 0.622 — around the 0.584 those two manage between themselves.
So the consensus set is a plausible draw from the same construct rather than a
second instrument, but **nothing here demonstrates that it measures what batches
1 and 2 measured**, and a detector scored against it would inherit that.

Two further limits belong on the number rather than in a footnote. The ten
disjoint splits reuse the same six passes, so they are not ten independent
comparisons and the cluster bootstrap does not price that reuse. And these six
passes ran as subagents with the criterion inlined in the prompt, while the
committed labels were written by a main session reading `criterion.md` from
disk — a different labelling condition, which is a second explanation for
0.675-at-one-sitting against 0.584-months-apart alongside session drift.

`labels-consensus.json` is committed with both warnings in its own header.

## Where the contest sits

| case | contested | |
|---|--:|--:|
| `verdict-experiment` | 0 of 13 | 0.0% |
| `verdict-rollout` | 2 of 17 | 11.8% |
| `verdict-schema` | 2 of 6 | 33.3% |
| `walkthrough` | 6 of 24 | 25.0% |

Nothing separates, at Fisher p = 0.2594 for the worst case against the rest.
`verdict-experiment` being unanimous on all 13 is the same shape the earlier
drift table showed, and with four clusters it stays a description.

## What this decides

**For [#150], [#298] and [#305]:** the judged-verdict route does not deliver
today, and they are pointed at a construct with a lexical signature instead.
`closing_offers` is the working template — laconic 3.5% against baseline 13.1%
at p = 8.6e-18, no labeller anywhere in it. [PR #308] reached the same place
from the other end for [#305]'s item 1, and route 2 is closed above on argument
from two independent inversions.

**For [#155]:** it stays open, and for the first time with a route that has a
measured effect size rather than a projection. Adjudication lifts the oracle
ceiling from 78.3% to 89.7% precision, and the residual is a threshold spread
rather than irreducible ambiguity — so the thing to fix is the borderline
convention, which is one paragraph of `criterion.md` doing a job that six
readings show it does not do. That is a pre-registrable unit: pin the threshold
with worked examples, then replicate on a **fresh batch** with the bar set
directly on the consensus ceiling, which is the quantity that matters and the
one this registration should have gated on.

**What the loop does not do is buy it on the strength of this.** The reading
above is post-hoc: the bar it would be set on is the one this round disclosed
rather than gated, and the registration said there is no third reading in which
an encouraging number buys more labelling. It is written down so the next
attempt starts from a measured ceiling instead of a fourth guess, not so that
the next round is obliged to run it.

## Cost

Six labelling passes, no benchmark generations, no judge calls, no `claude`
CLI sessions from `run.py` or `judge.py`. Nothing was spent from a usage window
that a round would have wanted.
