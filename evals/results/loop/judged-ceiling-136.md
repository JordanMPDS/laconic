# The draw that was not bought: a floor-derived cutoff corrects the threshold and buys no precision

**This is not a round.** It proposes no rule edit, buys no generation, spends no
`claude` call, and takes no row in [`LEDGER.md`](LEDGER.md). Round 71 is still
unregistered and [`candidate-due.sh`](../../../tools/candidate-due.sh)'s
allowance is unspent. It is the same class of work as
[`judged-floor-136.md`](judged-floor-136.md),
[`closed-question-136.md`](closed-question-136.md) and
[`closing-recap-305.md`](closing-recap-305.md).

Reproduce every number below with:

```sh
python3 evals/results/loop/judged-ceiling/ceiling.py
python3 evals/results/loop/judged-ceiling/ceiling.py --demo
```

## What this was going to be

[`judged-floor-136.md`](judged-floor-136.md) established that every trap in this
repository is a floor, computed the shortest response each of the 37 traps has
ever passed, hand-read all 37, and used the result to falsify the dominant
false-positive class in [#136]'s detector sample: all 11 hits excused as *"the
correction is the length, nothing is deletable"* sit 39 to 129 words above a
response that passed the identical trap.

It then named the one thing left, and the cluster's own next-step table carried
the same request:

> A detector firing at, say, twice its case's judged floor is one hand-labelled
> draw away from being measurable, and this document does not claim the draw.

So the plan was: freeze a `2 x floor` detector, draw 30 fresh hits, label them
under the committed criterion, and compare *30.0% strict at a global 80* against
*X% strict at twice the per-case floor*. **The draw was not bought.** Everything
below is why, and all of it is computed from files already committed.

## The consult changed the design before any of it was written

`bash tools/consult.sh` was given the issue, the design above and the four
things it was least sure of. DeepSeek and Kimi answered; Codex did not answer
inside the timeout. Three of the ideas below are theirs and are credited in
place, because a conclusion whose origin is not stated cannot be audited later.

**DeepSeek supplied the shape argument** (result 1), **the reason the draw is
unbuyable** (the closing section), and **the correction to the promotion bar**:
a one-sided 95% Clopper-Pearson lower bound clears 73.7% at **27 of 30**, not
the 29 of 30 the design had written down. It also proposed the session-local
check that result 4 tests and closes.

**Kimi supplied the population rule** — that excluding the no-headroom cases
*after* seeing their ratios is post-hoc however principled it sounds, so the
report stratifies rather than scopes — and the distinction the last section
rests on, that a labeller who has read the floors produces an auditor's
assessment rather than a held-out precision estimate.

## Result 1: `K x floor` is not one detector, it is thirteen

A multiple of the floor sets the surplus a response may carry to `(K-1) x
floor`, which at `K = 2` is the floor itself. The floors on these thirteen cases
span **12 to 64 words for the same trap**, because a cold answer has to
establish the fact it just read and a later one can point at it — the effect
[`judged-floor-136.md`](judged-floor-136.md) measures across the four families.

So the same surplus is convicted on one case and acquitted on another. Sixty
surplus words on `recall-index` (floor 12) is 72 words against a cutoff of 24
and fires; sixty on `confirm-rollback` (floor 64) is 124 against a cutoff of 128
and does not. That is not one detector with heterogeneous rates, it is a
per-case constant nobody chose.

| case | floor | allowance at 2x | fires @2x | fires @+40 |
|---|--:|--:|--:|--:|
| `confirm-index` | 41 | 41 | 15/150 | 17/150 |
| `confirm-metric` | 39 | 39 | 51/150 | 49/150 |
| `confirm-rollback` | 64 | 64 | **7/370** | **35/370** |
| `deep-index` | 45 | 45 | 24/242 | 29/242 |
| `deep-metric` | 39 | 39 | 25/245 | 24/245 |
| `deep-rollback` | 27 | 27 | 29/206 | 24/206 |
| `quota-merge` | 62 | 62 | 25/65 | 46/65 |
| `recall-index` | 12 | 12 | **40/59** | **33/59** |
| `recall-metric` | 18 | 18 | 39/65 | 33/65 |
| `recall-rollback` | 20 | 20 | 31/56 | 27/56 |
| `wide-index` | 16 | 16 | 19/25 | 13/25 |
| `wide-metric` | 31 | 31 | 13/25 | 12/25 |
| `wide-rollback` | 14 | 14 | 15/25 | 8/25 |

The two columns are not a rescaling of each other. `confirm-rollback` fires on 7
responses under the ratio and on 35 under a fixed allowance; `wide-rollback`
goes the other way, 15 to 8. **A future attempt should state the cutoff as an
absolute surplus allowance**, because the harm [#136] reports is denominated in
words the reader did not need and the rule the issue cites states an absolute
allowance — *"a yes/no question gets a word or a line"*.

## Result 2: no shape moves precision on the thirty labels that exist

The 30 committed labels were read under a criterion with three values, and
[`closed-question-136.md`](closed-question-136.md) reports the pair rather than
one number because the gap between them is where the redundancy judgement sits.
Re-scoring those same labels under every floor-derived cutoff:

| cutoff | kept | viol | bord | not | strict | generous |
|---|--:|--:|--:|--:|--:|--:|
| 80 words (as drawn) | 30 | 9 | 10 | 11 | **30.0%** | **63.3%** |
| 1.5x floor | 27 | 9 | 7 | 11 | 33.3% | 59.3% |
| 2.0x floor | 20 | 6 | 5 | 9 | 30.0% | 55.0% |
| 2.5x floor | 16 | 4 | 5 | 7 | 25.0% | 56.2% |
| 3.0x floor | 13 | 4 | 4 | 5 | 30.8% | 61.5% |
| floor +20 | 30 | 9 | 10 | 11 | 30.0% | 63.3% |
| floor +40 | 23 | 8 | 5 | 10 | 34.8% | 56.5% |
| floor +60 | 17 | 6 | 5 | 6 | 35.3% | 64.7% |
| floor +80 | 11 | 4 | 2 | 5 | 36.4% | 54.5% |

**Strict precision moves between 25.0% and 36.4% and lands nowhere.** The drawn
figure is 9 of 30, 95% CI [14.7%, 49.4%]; the best any shape reaches is 4 of 11,
95% CI [10.9%, 69.2%]. These are nested subsets of one sample rather than nine
draws, so the spread is not even nine noisy estimates — it is one estimate read
at nine cut points, and the promotion bar of 27 of 30 is not in view from any of
them.

**What the floor removed was a reason, not a false positive.** The 11 hits
labelled `not` are still 11 under every shape that keeps them: the floor
falsifies the justification recorded beside those labels, and re-labelling them
against a criterion without that escape is work this document does not do and
the next section says should not be bought.

## Result 3: what a floor-derived cutoff adds is shorter and unlabelled

Every shape above admits hits the global 80 excluded, because the cutoff sits
below 80 words on **9 of the 13 cases**: `confirm-metric`, `deep-metric`,
`deep-rollback`, all three `recall-*` and all three `wide-*`.

| cutoff | hits | at or under 80 words | median of the new hits | median of all hits |
|---|--:|--:|--:|--:|
| 1.5x floor | 687 | 336 | 66 | 81 |
| 2.0x floor | 333 | 87 | 61 | 96 |
| 2.5x floor | 228 | 58 | 61 | 106 |
| 3.0x floor | 188 | 50 | 63 | 104 |
| floor +20 | 701 | 283 | 69 | 88 |
| floor +40 | 350 | 48 | 72 | 106 |
| floor +60 | 196 | 6 | 78 | 120 |
| floor +80 | 119 | 0 | - | 128 |

At `2 x floor`, 87 of 333 laconic hits are responses of 61 median words that
nobody has read. **So the 30.0% in result 2 is the optimistic read of the new
cutoff, not a neutral one.** [#136]'s harm is 400 words of re-derivation; a
61-word answer to a closed question is a weaker candidate for it than the 96-word
median the labels were drawn from, and the shapes that avoid admitting anything
new (`floor +80`) are the ones that have stopped being floor-derived at all —
that column keeps 119 hits, all above 80 words, which is the cutoff it was meant
to replace.

## Result 4: the harm is not verbatim reuse across turns either

DeepSeek's sharpest suggestion was that the check belongs against the transcript
rather than the trap, because [#136]'s harm is literally an argument the model
had already made **earlier in the same session**. That turns out to be
measurable with no labeller at all: `run.py`'s `merge_turns` stores every turn's
full record under `turns`, so the model's own earlier answers are in the archive
on nine of the thirteen closed cases — `confirm-*` is cold by construction and
`quota-merge` is one turn.

Measuring the share of the graded turn's prose that sits inside a six-word run
it had already used, over 1,112 de-duplicated multi-turn responses:

| arm | n | median | mean | p90 | max |
|---|--:|--:|--:|--:|--:|
| baseline | 165 | 0.032 | 0.038 | 0.095 | 0.207 |
| laconic | 947 | 0.000 | 0.031 | 0.115 | 0.682 |

**There is nothing there, and what little there is points the wrong way.** The
median laconic response shares no six-word run at all with its own earlier
turns, the means are 3.1% against 3.8%, and the one extreme value in the archive
is on the laconic arm. Per case the medians are 0.000 on eight of nine laconic
cells and 0.090 on the ninth.

Bag-of-words overlap is not the missing refinement, it is the failure mode:
every turn in these cases is about one fixture, so shared vocabulary is
guaranteed and measures the case rather than the response. A six-word run is not
guaranteed, and it is absent. **The model re-derives in fresh words.** That is
[`closing-recap-305.md`](closing-recap-305.md)'s conclusion — redundancy is not
a lexical property — reached from the cross-turn direction instead of the
intra-response one, and it closes the cheapest remaining route to [#298] and
[#305] item 2 as well as this one.

## Why the draw is not bought

The comparison the draw exists to make is broken asymmetrically, and this is
DeepSeek's argument rather than a scheduling decision:

**The 30.0% was labelled by someone who had not seen the floors. Any new figure
comes from someone who has.** All 37 floor responses were read in full to produce
[`judged-floor-136.md`](judged-floor-136.md), several of them on these very
cases, and that reading is exactly a model of how short a correct answer to
these questions can be — which is the judgement the label turns on. There is one
labeller. Hiding the word count does not restore the state before that reading,
and no seed or freeze reaches it.

A second labeller does not rescue it either, unless they also re-label the
80-word sample, because otherwise the delta between the two figures is the
labeller and not the threshold. That is a 60-label protocol to arbitrate a
threshold which results 2 and 3 already say is not where the problem is.

**And the one claim the draw was going to add is already committed.** "Nothing
is deletable" is false for all 11 hits that said it, established mechanically by
[`judged-floor-136.md`](judged-floor-136.md) from blind verdicts, with no
labeller in it at all. The draw would have added a precision figure whose
expected value results 2 and 3 predict at or below 30.0%, measured by a
contaminated labeller, against a bar of 27 of 30.

So the threshold correction is the deliverable and the precision at the corrected
threshold is honestly unmeasurable here. Kimi's alternative — buy the draw,
disclose the contamination, and drop the hard bar — was considered and refused:
a precision figure that may not be gated on is a number that will be quoted
anyway, and this cluster has already had to correct four round documents for
reading a figure as something it was not.

## What this leaves [#136]

**All three of its proposals are now answered, and the third is closed rather
than parked.** Proposal 1 was rejected by [round 64](round-64.md); proposal 2
was priced at −0.16 of the demonstration block's gap by
[round 60](round-60.md); proposal 3 reached 30.0% precision strict at its own
80-word cutoff, had its dominant false-positive class falsified by the judged
floor, and does not improve at any floor-derived cutoff.

What is not closed is the construct. The floor says a shorter answer passed the
same trap; it does not say the surplus is re-derivation rather than a second
correct remedy, and that judgement is the one [#155] parks at 55.3% precision.
[#136] joins [#150], [#298] and [#305] on the [#146] judged-verdict route, and
result 4 removes the last cheap alternative to it for all four.

**What a future attempt should not repeat.** Not the ratio shape (result 1), not
a fresh 30-label draw by this labeller against the existing 30 (the section
above), and not a lexical cross-turn measure (result 4).

## What goes into `evals/CRITERIA.md`

One bullet, under the ceiling rule that
[`judged-floor-136.md`](judged-floor-136.md) already put there:

> **State the cutoff as a surplus allowance, not as a multiple of the floor.**
> `K x floor` tolerates `(K-1) x floor` words of surplus, and the floors on the
> thirteen closed questions span 12 to 64 words for the same trap, so a single
> `K` convicts sixty surplus words on one case and acquits them on another.

## What this cannot establish

- **That a floor-derived cutoff is worse than 80.** Results 2 and 3 say it is
  not measurably better on the labels that exist and that its extra hits are
  shorter. Neither is a measurement of the new cutoff's own precision, which is
  what the draw was for and what is not buyable here.
- **That cross-turn redundancy is absent.** Result 4 measures verbatim reuse and
  finds it absent. A re-derivation in fresh words is invisible to it by
  construction, and that is the reading: the harm is real and not lexical.
- **Anything about the four cases with no transcript.** `confirm-*` asks its
  question cold and `quota-merge` is a single turn, so result 4 covers nine of
  the thirteen and says nothing about the other four.
- **Anything about a rule.** No rule text is proposed, tested or changed here.

## Cost

No generations, no judge calls, no `claude` CLI sessions, nothing spent from a
usage window. One `tools/consult.sh` call to three delegate targets, two of
which answered.

[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#146]: https://github.com/JordanMPDS/laconic/issues/146
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
