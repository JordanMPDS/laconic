# `unread_asks`: the archive re-score

Working notes for [#146]. Establishes what the counter reads across every
stored round **before** it is allowed to gate anything, which is the sequence
[#49] followed for `turns`.

## What it counts

An answer that handed the decision back **and** never opened a file: the
intersection of `ASKS_BACK` and `num_turns == 1`. Both facts are already on
every stored run, so the whole re-score below is offline and cost no
generations.

It is a **subset of `one_turn`**, and carries `one_turn`'s fixture-only filter
for that reason: a case with no `fixture/` directory is one-turn by
construction, so every question it asked would count here spuriously.

**Its exposure is `one_turn` itself, not the run count, which makes the target
a conditional rate** — of the answers that never opened a file, how many handed
the decision back. It was a joint count until the round 20 analysis below
showed that form confounds two factors; see there for why.

**The detector is `_quality_strata`'s, unmodified.** Two counters reading one
behaviour through two regexes would drift, and re-tuning a detector after
seeing what it found is how a disclosure becomes a story. Its known limits are
in the open questions below.

## Why not just use `one_turn`

`one_turn` counts every answer that opened no file, whether or not it then
handed the decision back. Round 26 measured the difference directly:

| round 26, licence arm | failed |
|---|--:|
| hands back, read the repository | **0/6 (0%)** |
| hands back, did not read | **12/22 (55%)** |

Round 27 rejected an edit on the proxy at p = 0.151 while the effect it was
aiming at moved at p = 0.044 on this intersection.

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
pairs, and the same rate, as the joint count gave.

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
| round 20 vs same-week neighbours | 15/45 vs 4/24 | rise **p = 0.155** | correctly silent — this was a reading collapse, and `one_turn` reports it at p = 6.2e-08 |
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

1. **The detector is crude, now measured: 80% precision, 80% recall.** `ASKS_BACK` is
   `^[^\n]*\?\s*$` — any line that is a whole question. It cannot separate
   "which monitoring stack do you run?", a fork reading cannot settle, from
   "is there a logged-in state on these pages?", which the fixture answers.
   That distinction is the entire point of the metric. Validating it needs
   hand-labelled responses, and the labels must be assigned blind to the
   detector's verdict and never against round outcomes.
2. **Target-only, and it stays that way for now.** The archive null above is
   about false *accepts*. Making it fatal asks a different question — the false
   *rejection* rate — and that has not been measured.
3. **Whether the era confound needs its own correction.** Three of three false
   accepts are cross-era. A within-era estimate needs rounds close in time at
   fixed rules text, which the archive has few of.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#146]: https://github.com/JordanMPDS/laconic/issues/146
