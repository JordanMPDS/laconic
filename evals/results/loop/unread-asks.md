# `unread_asks`: the archive re-score

Working notes for [#146]. Establishes what the counter reads across every
stored round **before** it is allowed to gate anything, which is the sequence
[#49] followed for `turns`.

## What it counts

An answer that handed the decision back **and** never opened a file: the
intersection of `report.asks_back()` and `num_turns == 1`. Both facts are already on
every stored run, so the whole re-score below is offline and cost no
generations.

It is a **subset of `one_turn`**, and carries `one_turn`'s fixture-only filter
for that reason: a case with no `fixture/` directory is one-turn by
construction, so every question it asked would count here spuriously.

**Its exposure is `one_turn` itself, not the run count, which makes the target
a conditional rate** — of the answers that never opened a file, how many handed
the decision back. It was a joint count until the round 20 analysis below
showed that form confounds two factors; see there for why.

**The detector is `_quality_strata`'s, and both counters read the same one.**
Two counters reading one behaviour through two expressions would drift, and
re-tuning a detector after seeing what it found is how a disclosure becomes a
story.

**That detector is no longer v1.** Everything from here to the fresh validation
was computed with `^[^\n]*\?\s*$`, which is what shipped while it had no
measurement. It has one now, and `report.py` reads `asks_back()` — v2 — since
[the promotion](#the-promotion-and-what-the-archive-reads-under-it). Each
section below carries what it reads under the detector that actually ships.

## Why not just use `one_turn`

`one_turn` counts every answer that opened no file, whether or not it then
handed the decision back. Round 26 measured the difference directly:

| round 26, licence arm | v1 | shipped detector |
|---|--:|--:|
| hands back, read the repository | **0/6 (0%)** | **0/18 (0%)** |
| hands back, did not read | **12/22 (55%)** | **19/32 (59%)** |

Round 27 rejected an edit on the proxy at p = 0.151 while the effect it was
aiming at moved at p = 0.044 on this intersection — p = 0.084 under the
detector that shipped, which is the one number the promotion cost. **The split
this counter exists for is sharper under it, not softer**: not one of the 18
hands-back answers that read the repository failed.

## Independence rules, applied before any statistic

- `round-01-n10`, `-v2` and `-v3` are prefixes of `-v4`. Only `-v4` is counted.
- `round-21` (n=5) and `round-22` (n=5) are subsets of their own `-n10` files.
  Only the `-n10` files are counted.
- **Arbitration snapshots are excluded.** An arbitration regenerates only the
  cells that rose, so it is a biased subset by construction and cannot serve as
  a random redraw. `round-25-arbitration` and `round-10-replication` are out.

## Between-round dispersion at identical rules text

Comparing only rounds that share a `rules_cksum` **and** a case-scope size:

Scored as the conditional rate the metric now is:

| rules text | scope | rounds | pooled | chi2 | df | phi |
|---|--:|--:|--:|--:|--:|--:|
| 1497646142 | 8 | 2 | 2/17 | 2.55 | 1 | 2.55 |
| 1823644123 | 3 | 2 | 3/9 | 0.00 | 1 | 0.00 |
| 1830906901 | 3 | 2 | 6/48 | 0.25 | 1 | 0.25 |
| 1830906901 | 8 | 4 | 13/172 | 15.52 | 3 | **5.17** |
| 3694954268 | 8 | 6 | 75/290 | 3.02 | 5 | **0.60** |
| 3980812364 | 3 | 3 | 8/26 | 3.11 | 2 | 1.56 |
| 3980812364 | 5 | 2 | 11/39 | 1.16 | 1 | 1.16 |
| **pooled** | | **19** | | **25.62** | **14** | **1.83** |

**phi = 1.83**, against `ONE_TURN_PHI` = 3.39 for the counter it conditions on.
Chi-square 25.62 on 14 df is **p = 0.029, so unlike the joint count this form
is significantly overdispersed** and the inflation is not optional.

**Under the detector that shipped it reads 15.29 on 14 df, phi = 1.09 at
p = 0.359, and no inflation is applied.** Most of the dispersion below was v1
missing a class of hand-back at different rates in different rounds. See
[the promotion](#1-the-between-round-dispersion-halves-and-the-inflation-is-dropped).

**That is the price of conditioning and it should be stated plainly.** The same
data as a joint count reads phi = 1.47 at p = 0.113. Conditioning shrinks the
denominator roughly fourfold — 15, 26, 65 and 66 in the pre-licence group where
the joint form had 80, 80, 200 and 200 — so the rate is inherently noisier. The
metric is better targeted and less precise at the same number of runs.

The best-populated group is still the reassuring one: six independent rounds of
the current master text, 290 unread answers, **phi = 0.60**. Most of the pooled
dispersion is the 1830906901 group at 5.17, which is also the group spanning
the widest era.

## The false-accept rate matches nominal alpha

A target must *improve* to clear, so the failure mode is a gate that passes on
noise. Every ordered pair of rounds at identical rules text and identical
scope, scored one-sided at alpha 0.05:

**3 of 56 pairs reach alpha (5.4%), against a nominal 5%** — the same three
pairs, and the same rate, as the joint count gave. **Under the shipped detector
it is 1 of 56 (1.8%)**, and none of these three survive.

All three involve `round-26-control` reading **0/200**, and that zero is real
rather than an artifact: every one of its 200 runs carries text, 66 of them are
one-turn, and the pre-licence rules simply produced 6 questions in 200 with
none in a one-turn answer.

**The honest caveat is era, not sampling.** The 1830906901 group spans
2026-07-31 to 2026-08-24 — the same window in which `terse-control`'s one-turn
rate moved 4/40 to 11/40 with nothing changed but the calendar and the CLI. All
three false accepts are cross-era pairs, so 5.4% is if anything an
over-estimate of the sampling component.

## It separates the rules texts the loop has already judged

Eight-case design scope, sonnet:

| rules text | | conditional rate |
|---|--:|--:|
| round 10's licence, via round 20 (3980812364) | 15/45 | **33.3%** |
| the licence, current master (3694954268) | 75/290 | **25.9%** |
| round 27's edit (136269960) | 9/76 | **11.8%** |
| pre-licence (1830906901) | 13/172 | **7.6%** |

- pre-licence to licence: **p = 3.0e-06**. This is round 26's disclosed
  composition effect, read directly instead of inferred from a stratum split.
- licence to round 27's edit: **p = 0.012**, on 290 unread answers against 76
  rather than round 27's own 76 against 76.

Under the shipped detector the same four texts read 60.0%, 45.2%, 27.6% and
7.0%, in the same order, at p = 2.5e-15 and p = 0.019. **The separation the
counter was built for is stronger, not weaker, under the better detector.**

## CORRECTION: the first validation's recall figure was biased

**The 80% recall published above and in [#146] is wrong. The true figure is
about 48%.**

The first sample was stratified 30 detector-positive against 30
detector-negative, drawn from a pool of 82 positives and 400 negatives.
Precision is a ratio computed *within* the positive stratum, so 1:1 sampling
leaves it unbiased. **Recall is not**: it takes TP from the positive stratum
and FN from the negative stratum, and sampling those 1:1 against a true ratio
of roughly 1:5 undercounts FN by that factor.

Reweighting the first batch to the population it was drawn from:

| | precision | recall |
|---|--:|--:|
| batch 1, as published | 80.0% | **80.0%** |
| batch 1, reweighted | 80.0% | **45.1%** |
| batch 2, fresh and unstratified | 100.0% | **50.0%** |

**The corrected first estimate and the independent fresh estimate agree.** v1
misses about half of all hand-backs, not a fifth.

That does not change the conclusions the first validation reached — both error
classes are still systematic, the construct still holds at 90%, and a better
detector still weakens round 27 — but it makes v1 a substantially worse
instrument than reported, and the correction is the reason the fresh sample was
worth drawing.

## The fresh out-of-sample validation

80 one-turn design responses, **unstratified simple random draw** so the
estimate is unbiased for both detectors at once, disjoint from the first 60,
seed and pool recorded in `unread-asks-v2/resample.py`. `detector_v2.py` was
committed in `111723b` **before this sample was drawn**, so its figure is a
genuine out-of-sample measurement. Labelled blind under an explicit rule
recorded in `unread-asks-v2/labels.json`. 16 of 80 (20%) are true hand-backs.

| | precision | recall | F1 |
|---|--:|--:|--:|
| v1, in-sample (as published) | 80.0% | 80.0% | 80.0% |
| v1, batch 1 reweighted | 80.0% | 45.1% | 57.7% |
| **v1, fresh** | **100.0%** | **50.0%** | **66.7%** |
| v2, in-sample | 93.1% | 90.0% | 91.5% |
| **v2, fresh** | **73.7%** | **87.5%** | **80.0%** |

**v2's in-sample figure overstated its precision by 19 points** — 93.1% against
a fresh 73.7% — which is exactly what designing a detector on the errors of the
sample you then score it on produces. Its recall held, 90.0% against 87.5%.

**v2 is the better instrument on the fresh sample** (F1 80.0% against 66.7%),
and it buys that by trading precision for recall: it catches 14 of 16
hand-backs where v1 catches 8, at the cost of 5 false positives where v1 has 0.

Pooled across both batches, v1's precision is 32 of 38 = **84.2%**.

### The remaining error classes

v2's five false positives are all the same shape: a fork **posed as a question
and then resolved for both branches in the same breath**. F27 asks "do you need
that pixel data, or just a listing-quality image?" and immediately answers it.
The reader is not blocked, so nothing was handed back.

v2's two false negatives are hand-backs carrying **no question mark at all**.
F78 says "The fork I can't resolve without knowing your setup:" and then
branches; F06 ends "What's the current stack and rough catalog size — that'd
pin down which option actually applies." with a period.

A v3 would need to drop self-resolved forks and catch question-less
declarations of ignorance. Both are harder than what separates v1 from v2, and
neither should be attempted against these 140 labelled responses — a third
sample would be needed to score it.

## The promotion, and what the archive reads under it

`report.py` reads the behaviour through `asks_back()` now, and that function is
`v2`. Both counters call it — `_quality_strata`'s disclosure and `unread_asks` —
so the two still cannot drift apart, which is the property v1 was kept
unmodified to protect. The frozen copy the fresh sample scored is untouched at
[`unread-asks/detector_v2.py`](unread-asks/detector_v2.py), and
`tests/test_bench.py` compares the shipped detector against it over every stored
response of a real round rather than over examples, because the two differ only
on real text.

Every table below is regenerated by
[`unread-asks/archive_rescore.py`](unread-asks/archive_rescore.py), which reads
stored snapshots only and prints both detectors side by side.

**No stored verdict moves.** The detector has exactly two readers: a
disclosure line, and a target that is not fatal. Round 26 re-scored under it
still returns `accept`, with the same opposite-direction signature in its strata
line. What moves is what the archive *says*, and four of the statements above
change.

### 1. The between-round dispersion halves, and the inflation is dropped

The same table, the same 21 rounds in seven groups at identical rules text and
identical case-scope size:

| rules text | scope | rounds | pooled | chi2 | df |
|---|--:|--:|--:|--:|--:|
| 1497646142 | 8 | 2 | 2/17 | 0.01 | 1 |
| 1823644123 | 3 | 2 | 9/9 | — | 1 |
| 1830906901 | 3 | 2 | 6/48 | 0.25 | 1 |
| 1830906901 | 8 | 4 | 12/172 | 0.99 | 3 |
| 3694954268 | 8 | 6 | 131/290 | 9.79 | 5 |
| 3980812364 | 3 | 3 | 16/26 | 3.40 | 2 |
| 3980812364 | 5 | 2 | 26/39 | 0.85 | 1 |
| **pooled** | | **21** | | **15.29** | **14** |

| detector | chi2 | df | p | phi |
|---|--:|--:|--:|--:|
| v1 | 25.61 | 14 | **0.029** | **1.83** |
| v2 | 15.29 | 14 | **0.359** | **1.09** |

**Most of what looked like between-round drift was the detector.** The group
that carried the v1 dispersion — 1830906901 at scope 8, chi-square 15.52 on 3 df
— falls to 0.99. Its spread was `round-26-control` reading 0 of 66 against
siblings at 4 of 15, 4 of 26 and 5 of 65; v2 reads the same four rounds as 1 of
15, 3 of 26, 4 of 65 and 4 of 66. The 1823644123 group contributes nothing
either way: v2 fires on all 9 of its unread answers, and a group at a rate of 1
has no dispersion left to measure.

**The inflation this measurement was going to buy is not applied, and the
reason is the direction it would move.** `_inflated_count_p` is a normal
approximation on a difference of proportions, and it *replaces* the exact
conditional binomial `_count_p` computes rather than adjusting it. On round 27's
counts — 32 of 76 against 21 of 76 — the exact test reads **0.084** and the same
test inflated by phi = 1.09 reads **0.037**. An inflation that turns a
non-significant fall into a significant one is not an inflation. `ONE_TURN_PHI`
is 3.39 and swamps that effect; 1.09 does not, so `unread_asks` keeps the exact
test and the measured phi is published here instead of applied there.

### 2. The false-accept rate falls, and stops being one cell's story

| detector | pairs reaching alpha | |
|---|--:|---|
| v1 | **3 of 56 (5.4%)** | all three against `round-26-control` reading 0 of 200 |
| v2 | **1 of 56 (1.8%)** | `round-24-replication-2` (20 of 30) against `round-24` (2 of 11), p = 0.042 |

Both are consistent with a nominal 5% on 56 non-independent pairs. What changed
is the shape: under v1 every false accept was the same zero, which is the
signature of a detector missing a class of hand-back rather than of sampling.

### 3. Round 20 does not stay silent, and the earlier reading of it does not survive

| | one_turn | ask given unread, v1 | ask given unread, v2 |
|---|--:|--:|--:|
| rounds 18+19, neighbours | 24/160 (15%) | 4/24 (17%) | **1/24 (4%)** |
| round 20, round 10's licence | 45/80 (56%) | 15/45 (33%) | **27/45 (60%)** |
| | **p = 6.2e-08** | p = 0.155 | **p = 0.0001** |

**This costs the reading published above.** Under v1 the conditional rate was
correctly silent on round 20: a reading collapse that `one_turn` already gates
far harder. Under v2 round 20's text did *both* — it collapsed reading and it
raised the rate at which the answers that read nothing hand the decision back.

The decomposition still separates the two rounds, which was the point of making
the metric conditional: round 20 moves on both factors and round 27's edit moves
on only the second. What does not survive is the stronger claim that the
conditional rate reports nothing about round 20.

**v2 is the more plausible reading of that contrast, not just the newer one.**
Round 10's licence is a text that explicitly permits asking a design question,
and the neighbours' 4 of 24 under v1 are the closing-offer class the fresh
validation measured at 0 false positives for v2. A detector that finds a licence
to ask produced more asking is more credible than one that does not.

### 4. Round 27's disclosure moves further below alpha

| round 27, sonnet, eight cases | v1 | v2 |
|---|--:|--:|
| share handing back | 23/200 to 12/200, **p = 0.045** | 44/200 to 32/200, **p = 0.103** |
| conditional, given unread | 19/76 to 9/76, **p = 0.044** | 32/76 to 21/76, **p = 0.084** |

This was already disclosed above and it is unchanged by promotion: [#138]'s edit
moved the right way under both detectors and reaches alpha under neither once
the detector is the validated one.

### And rounds 25 and 26 read the same signature, larger

| | hands-back fails | resolves fails | share handing back |
|---|--:|--:|--:|
| round 25 control | 1/11 | 38/189 | 11/200 |
| round 25 licence | **15/43** | 26/156 | **43/200** |
| round 25 replication (`round-25-arbitration`) | 8/44 | 32/156 | 44/200 |
| round 26 control | 1/12 | 45/188 | 12/200 |
| round 26 licence | **19/50** | 24/150 | **50/200** |

Round 26's cancelling pair is unchanged in shape and larger in both halves: the
hands-back stratum fails 19 of 50 against the control's 1 of 12 while the
resolving stratum improves, 45 of 188 to 24 of 150. The share moves 12/200 to
50/200, **p = 6.1e-07**, against v1's 6/200 to 28/200 at p = 9.8e-05.

**Round 25's withdrawal needs splitting in two.** It withdrew a failure-rate
spike, and that withdrawal stands: pooled over the round and its replication the
hands-back stratum fails 23 of 87 against the control's 1 of 11, p = 0.23, which
establishes nothing on a control stratum of eleven. But round 25 also reported
its *share* shift as not significant — 16/200 to 44/400, p = 0.17 — and under
v2 the same comparison is **11/200 to 87/400, p = 4.0e-07**. The share shift
round 26 was credited with replicating was already there in round 25, under a
detector that could not see half of it.

## The first validation, as originally written

## The detector validation, and it is bad news

60 one-turn design responses, drawn with a seeded sample across eight
snapshots and three rules texts, 30 detector-positive and 30 detector-negative.
**Labelled blind**: `blind.md` carries the response text and the case name, no
detector verdict and no stratum marker, and the label definition was written
before reading any of them.

Everything needed to re-check it is committed under
[`unread-asks/`](unread-asks/): `labels.json` holds the labels and the
definition they were assigned under, `key.json` the unblinding key, and
`resample.py` regenerates the blinded file from the committed snapshots — its
output is byte-identical to the file that was actually labelled.

| | label: asks | label: no ask |
|---|--:|--:|
| **detector fires** | 24 | 6 |
| **detector silent** | 6 | 24 |

**Precision 80.0%, recall 80.0%, F1 80.0%.**

**Both error classes are systematic, not random.**

*All six false positives are closing offers* — "Want me to sketch the actual
schema?", "or is this enough to take to the team?". The answer resolved the
question and then offered more work. That is the opposite of the harm being
counted.

*All six false negatives are line-position artifacts.* The hand-back is
phrased without a terminal question mark ("What's the current stack and rough
catalog size — that'd pin down which option actually applies.") or carries the
question mark mid-line, so `^[^\n]*\?\s*$` never matches. `design-realtime`
R06 hands back a fork `PLATFORM.md` answers outright, and the detector is
silent.

**The errors cancelled in this sample — 30 counted against 30 true — and that
is luck, not a property.** The two classes are independent and nothing makes
them offset in another draw.

### The metric's premise holds even though its detector does not

Among the 30 true asks, would reading the fixture have settled the question?

| | | |
|---|--:|--:|
| yes | 27 | **90%** |
| partial | 2 | 7% |
| no | 1 | 3% |

**An unread hands-back is almost always a question the repository answers.**
One of thirty was a genuine product fork. That is the construct this counter
was built on, and it survives.

### A better detector makes round 27's result weaker, not stronger

A candidate `v2` — a question anywhere in the closing two paragraphs, minus
first-person offers to do more work — scores **precision 93.1%, recall 90.0%**
on the same 60 labels. Re-running round 27 under both:

| detector | control | edit | one-sided fall |
|---|--:|--:|--:|
| v1, shipped | 19/200 | 9/200 | **0.0436** |
| v2, candidate | 32/200 | 21/200 | **0.0845** |

**Round 27's nominally significant disclosure does not reach alpha under the
better detector.** Both agree on direction, and neither is close to reversing
it, but the p = 0.045 that made round 27's disclosure quotable was carried in
part by a detector that misses a fifth of real hand-backs and counts closing
offers as if they were forks.

**Two honest limits on `v2` itself.** It was designed after seeing v1's error
classes on these 60 responses and then scored on the same 60, so 93.1/90.0 is
an in-sample figure and its true performance is lower. And promoting it would
change `_quality_strata`, which means re-scoring the disclosure figures
published in rounds 25, 26 and 27 — the repository has done that before
([#66], [#78], [#94]) but it is a deliberate act, not a detail.

### What this changes

The case for gating on this counter is weaker than round 27's numbers
suggested, and the honest order is now:

1. A **fresh** validation sample for any candidate detector, labelled blind,
   disjoint from these 60. An in-sample 93% is not an estimate.
2. Only then a detector change, with the rounds-25-to-27 re-score published
   alongside it.
3. Only then a gate.

Nothing here justifies re-running [#138]'s edit yet. It moved the right way
under both detectors and reached alpha under neither once the detector is
improved.

## What round 20's edit was, and why it changes the metric

The re-score put `rules_cksum` 3980812364 highest of all eight texts at 18.8%.
It is **not a novel edit**: it is round 10's design-question licence, the
version placed in `level: full`, re-applied byte for byte by rounds 10, 12, 14,
15 and 20. Round 20 ran it a fifth time, not to test it, but to ask whether the
dev set could detect the harm the round 15 holdout had found.

**The loop condemned that text twice, independently of this counter.** Round
15's incarnation was killed by the holdout. Round 20 was rejected on quality:
`quality_fails` 87 → 104, of which +13 fell on the three [#88] cases. So the
counter ranking it top of eight is an external check it passes, on a text it
was not built from.

### The comparison that made it look highest was invalid

18.8% against master's 9.4% spans 2026-08-14 to 08-25 — nine days and eight CLI
releases — which is the era confound in the false-accept section above, not a
rules effect.

**Round 20's own control arms cannot fix it.** All three of rounds 18, 19 and
20 carry `carried_arms_from: round-01-n10-v4.json`, so their `baseline`,
`terse-control` and `word-compression` numbers are byte-identical to each other
and belong to a different era than the treatment. This is exactly the defect
the loop skill records under "Carrying the controls was wrong".

**The valid comparison is the freshly generated laconic arms of its
neighbours**, rounds 18 and 19, run on 2026-08-13 against round 20's 08-14,
same eight-case scope, different rules texts:

| | one_turn | ask given unread | unread_asks |
|---|--:|--:|--:|
| rounds 18+19, neighbours | 24/160 (15%) | 4/24 (17%) | 4/160 (**2.5%**) |
| round 20, round 10's licence | 45/80 (56%) | 15/45 (33%) | 15/80 (**18.8%**) |

`unread_asks` rises at **p = 6.1e-05**. The effect is real and it is not era.

### The decomposition is the finding, and it corrects this issue's premise

Splitting the counter into its two factors — how often an answer failed to
read, and how often an answer that failed to read then handed the decision back
— separates round 20 from round 27 completely:

| | one_turn rate | ask given unread | unread_asks |
|---|--:|--:|--:|
| rounds 18+19 | 15% | 17% | 2.5% |
| round 20 | **56%** | 33% | 18.8% |
| round 27 control (master) | 38% | **25%** | 9.5% |
| round 27 edit ([#138]) | 38% | **12%** | 4.5% |

| | one_turn | ask given unread |
|---|--:|--:|
| round 20 vs neighbours | **p = 6.2e-08** | p = 0.155 |
| round 27 edit vs control | p = 0.532 | **p = 0.044** |

**These are two different failure modes and only one of them needs this
counter.** Round 20's text collapsed reading — 15% to 56% one-turn — and the
conditional ask-rate did not move significantly. `one_turn` already gates that,
and gates it far more powerfully. Round 27's edit is the mirror image: reading
is exactly flat and what changed is what unread answers *do*, which `one_turn`
cannot see by construction.

**So the framing this issue was opened on is wrong.** [#146] says `one_turn` is
"a diluted proxy" for the same harm. The truer statement is that the two
measure different factors, and **the raw joint count confounds them**: round 20
scores highest on `unread_asks` almost entirely through a reading collapse that
needed no new metric.

**The metric that isolates [#138]'s behaviour is the conditional rate — asks
given unread — not the joint count.** A gate on the joint count can be cleared
by improving reading while asking gets worse, or tripped by a reading collapse
that `one_turn` already reports.

### The counter was switched to the conditional rate, and it discriminates

`_exposure` now returns `one_turn` for this target rather than the run count.
The check that matters is whether the change separates the two failure modes it
was made for:

| | | | |
|---|--:|--:|---|
| round 20 vs same-week neighbours | 15/45 vs 4/24 | rise **p = 0.155** | correctly silent — this was a reading collapse, and `one_turn` reports it at p = 6.2e-08. **Not silent under the shipped detector: 27/45 against 1/24, p = 0.0001. See [the promotion](#3-round-20-does-not-stay-silent-and-the-earlier-reading-of-it-does-not-survive).** |
| round 27's edit vs control | 9/76 vs 19/76 | fall **p = 0.044** | still fires — `one_turn` is flat at p = 0.532 and cannot see it |

Under the joint count round 20 was the highest-scoring text in the archive.
Under the conditional rate it is not significant against its own neighbours,
which is the correct reading: nothing about its asking behaviour was
established, only that it stopped reading.

Separation across rules texts survives the change — pre-licence 7.6% to master
25.9% at p = 3.0e-06 — so conditioning did not cost the signal that motivated
the counter.

Two caveats. On round 27 the joint count and the conditional rate give
identical p-values, because `one_turn` happened to tie at exactly 76/200 on
both sides; that tie is coincidental, and the per-case distributions differ
substantially (`design-cache` 17 against 10, `design-retry` 13 against 19). And
the detector caveat is unchanged: under `v2` the conditional rate reads 42% to
28%, p = 0.0845.

## Open questions before this gates anything

1. **The detector is measured and promoted, and its remaining errors are
   named.** v2 reads 73.7% precision and 87.5% recall out of sample, against
   v1's 100% and 50%. Its false positives are forks posed as a question and
   resolved in the same breath; its false negatives are hand-backs carrying no
   question mark at all. **A v3 addressing either needs a third labelled sample
   — not the 140 responses these two were scored on.** No detector yet separates
   "which monitoring stack do you run?", a fork reading cannot settle, from "is
   there a logged-in state on these pages?", which the fixture answers, and that
   distinction is the entire point of the metric. The construct survives it: 27
   of 30 true hand-backs in batch 1 were questions the repository answers.
2. **Target-only, and it stays that way for now.** The archive null above is
   about false *accepts*. Making it fatal asks a different question — the false
   *rejection* rate — and that has not been measured.
3. **Whether the era confound needs its own correction.** Three of three false
   accepts are cross-era. A within-era estimate needs rounds close in time at
   fixed rules text, which the archive has few of.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#146]: https://github.com/JordanMPDS/laconic/issues/146
