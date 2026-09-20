# The closed question: [#136]'s last untried proposal, and the label it cannot get

**This is not a round.** It proposes no rule edit, buys no generation, spends no
call, and takes no row in [`LEDGER.md`](LEDGER.md). It is a detector measured
before a round was registered, the way
[`closing-recap-305.md`](closing-recap-305.md) was measured the same week.
Round 71 is still unregistered and the
[`candidate-due.sh`](../../../tools/candidate-due.sh) allowance is unspent.

Reproduce every number below with:

```sh
python3 evals/results/loop/closed-question/sweep.py
```

## What [#136] asks for

[#136] reports an eight-word closed confirmation question — *"you mentioned Lift
is the wrong metric correct?"* — answered in about 400 words across three `##`
sections, re-deriving an argument the model had made earlier in the same
session. Its diagnosis is what makes it the strongest lead in the cluster: two
rules already cover the case in plain terms, *"A yes/no question gets a word or a
line"* and *"No teaching a concept the question already shows the user knows"*,
so this is an explicit rule failing to fire rather than a gap in the rules.

It proposes three fixes. Round 64 bought the first as a rule edit and the
registered falsifier fired — 2 of 3 target cells against a bar of 3 of 3, one hit
at p = 0.013 which is what three tests produce, reverted in full. The second is a
telling sentence, which [round 60](round-60.md) prices at −0.16 of the
demonstration block's gap. The third has never been attempted:

> **A detector, cheap and binary.** Flag any response over ~80 words to a prompt
> under ~15 words that ends in `correct?`, `right?`, `is that right?`, or
> `yes or no`. That is narrow enough not to fire on real responses and would have
> caught this turn.

That proposal is also what the loop's own standing redirect asks for. The judged
redundancy route closed this week: [#155]'s detector parks at 55.3% precision,
and six independent labellers at one sitting lifted the oracle ceiling to 89.7%
while failing the registered mechanism bar, so
[`restatement/consensus/consensus.md`](restatement/consensus/consensus.md)
refused a fourth attempt and sent the cluster to constructs with a *lexical*
signature instead. A closed question is a lexical signature. This is the attempt.

## The detector

[`closed-question/detector.py`](closed-question/detector.py), using
`metrics.score`'s own word count so that fenced blocks, inline code and URLs are
excluded — these answers carry SQL, and charging a response for a
`CREATE INDEX` statement would charge it for content the rule file protects
verbatim.

The prompt half is binary and needs no interpretation: the graded turn ends in
one of the four markers [#136] names, plus `true?`, which is the same shape. Two
settings, because the issue's literal form and the form this suite can carry are
not the same predicate:

- **`literal`** — the marker ends the question and the prompt is at most 15
  words, both as [#136] specifies.
- **`widened`** — the word cap is replaced by the condition it proxies for, that
  the prompt asks for no explanation (`why`, `explain`, `walk me through`,
  `how`), since an explanation request is never-cut content outright.

**The literal predicate fires on nothing at all until a harness artifact is
removed.** Every prompt in `evals/cases/` ends with the appended instruction
`Don't edit anything.`, which `evals/CRITERIA.md` requires so that a diagnosis
lands in the response rather than in a diff. So the marker is never the last
thing in the file, and `correct?` is never at the end of anything. The detector
strips that instruction and says so rather than reporting a zero. It is worth
naming twice, because the first version of the strip used a literal space and
`confirm-rollback`'s prompt wraps as `Don't edit\nanything.` — one case and 370
of the archive's runs dropped out of the population silently. `detector.demo()`
holds both forms.

## The population, discovered rather than listed

| | cases | note |
|---|--:|---|
| closed under `widened` | **13** | `confirm-*`, `recall-*`, `deep-*` and `wide-*` — four families of three sharing three fixtures — plus `quota-merge` |
| closed under `literal` | 12 | `quota-merge`'s graded turn is 35 words and fails the cap; it is as closed as the other twelve |

## The rate, and why the arm contrast is not the finding

1,953 de-duplicated responses, every one already stored. No generation.

| arm | n | median prose words | p90 | max | fires at 80 |
|---|--:|--:|--:|--:|--:|
| `laconic` | 1,683 | 62.0 | 107 | 254 | 449 (**26.7%**) |
| `baseline` | 270 | 160.5 | 227 | 291 | 268 (**99.3%**) |

The arms separate enormously, and that is not evidence of anything this loop did
not already have. The whole curve says why:

| cutoff, prose words | `laconic` | `baseline` |
|--:|--:|--:|
| 20 | 92.8% | 100.0% |
| 30 | 83.7% | 100.0% |
| 40 | 74.2% | 100.0% |
| 60 | 51.9% | 100.0% |
| **80** ([#136]'s) | **26.7%** | **99.3%** |
| 100 | 13.1% | 93.0% |
| 120 | 5.9% | 86.3% |
| 160 | 1.5% | 50.0% |
| 200 | 0.2% | 18.5% |

**The unruled arm is at the ceiling for every cutoff the rule text could
justify.** A rule that licenses "a word or a line" cannot be operationalised
above 120 words without licensing six lines, and below 120 the baseline reads
86% to 100%. So the contrast is the same fact `output_tokens` already reports as
a median of 62 against 160.5, re-expressed as a rate — which is what DeepSeek
said when the design was put to it, and it is right. A binary endpoint is worth
buying anyway, but only for the thing a median cannot do: **convict one
response**. That is what precision decides.

For contrast, the one detector in this family that was promoted:
`metrics.closing_offers` reads laconic 3.5% against baseline 13.1% at
p = 8.6e-18, with every control arm at or above baseline
([`closing-offers.md`](closing-offers.md)). There the ruled arm is low and the
unruled one high. Here both arms are high and the ruled one is lower.

## Per-case, where the spread lives

| case | n | median | fires |
|---|--:|--:|--:|
| `confirm-index` | 150 | 60.0 | 14.0% |
| `confirm-metric` | 150 | 73.0 | 28.7% |
| `confirm-rollback` | 370 | 78.0 | 44.6% |
| `deep-index` | 242 | 49.0 | 13.6% |
| `deep-metric` | 245 | 45.0 | 9.4% |
| `deep-rollback` | 206 | 30.0 | 11.2% |
| `quota-merge` | 65 | 115.0 | **84.6%** |
| `recall-index` | 59 | 63.0 | 44.1% |
| `recall-metric` | 65 | 60.0 | 35.4% |
| `recall-rollback` | 56 | 51.0 | 30.4% |
| `wide-index` | 25 | 59.0 | 28.0% |
| `wide-metric` | 25 | 67.0 | 40.0% |
| `wide-rollback` | 25 | 47.0 | 12.0% |

The five-turn `deep-*` family is the lowest in the table at 9.4% to 13.6%, which
is [round 42](round-42.md)'s finding in a second form: under the shipped
`--turn-delivery plugin` wiring the rule binds hardest at depth, exactly where
[#136] observed it failing.

## Precision, and the number that will not settle

Thirty hits drawn at seed 136 from the laconic arm at [#136]'s own cutoff, hand
read in full. That is the [#155] convention — the standard set `closing_offers`
cleared at 30 of 30, the restatement detector failed at 55.3%, and the closing
recap at 12%. The labels and the criterion are in
[`closed-question/labels.json`](closed-question/labels.json); redraw them with
`python3 evals/results/loop/closed-question/draw.py`.

> A hit is a **violation** when the response either re-derives the argument for a
> claim it has already stated or introduces a subject the question did not raise,
> which is the harm [#136] reports. It is **not** a violation when every clause is
> the yes-or-no, the correction the case's own `trap` requires, or content the
> rule file protects — code and commands verbatim, bad news, a request for
> information the answer needs. A hit whose only surplus is one redundant
> restatement is **borderline**, and reported separately rather than resolved.

| label | n | precision |
|---|--:|--:|
| violation | 9 | **30.0%** |
| borderline | 10 | |
| not a violation | 11 | |
| violation + borderline | 19 | **63.3%** |

**The gap between 30.0% and 63.3% is the [#155] judgement, and that is the
result.** Every borderline hit has exactly one redundant unit: the fixture's own
conclusion quoted after the response has already paraphrased it, or a closing
sentence re-asserting the answer. Calling those either way is deciding whether a
restatement is surplus — which is the call [#155] parked at 55.3% and
[`closing-recap-305.md`](closing-recap-305.md) reached 12% on. A detector cannot be promoted on a
precision whose value is set by the judgement it was built to avoid needing.

## The false positives are one shape, and it is structural

| shape | n | why it fires |
|---|--:|---|
| **the correction is the length** | 11 | The premise is false, so the answer is a denial plus the qualification the trap requires, at 80 to 145 words of necessary content. *"No — a plain index on `created_at` can't serve this query, since the predicate wraps it in `date_trunc`…"* Nothing is deletable. |
| **the fixture quote** | 8 | Correction, then the document's own conclusion quoted verbatim underneath it. One redundant unit; the [#155] call. |
| **the closing restatement** | 2 | A final sentence re-asserting the answer — [#305] item 1's construct, already dead at 12% precision. |
| **re-derivation** | 3 | The reported harm: the case for a claim already stated, rebuilt. |
| **unsupported speculation** | 3 | All three on `quota-merge`: hypotheses about what the fixture states outright, and the trap's required claim missing. |
| **double restatement** | 3 | The quote *and* a closing restatement. |

**All thirteen closed questions in this suite carry a false or partial premise.**
`*-index` asks whether the proposed index is the fix and the trap requires
denying it; `*-metric` asks whether lift is the wrong metric, and the trap requires
denying that switching estimators fixes the readout; `*-rollback` and
`quota-merge` ask a half-true question and the trap requires the confirmation
plus a qualification the response has to go and find. The responses agree:

| arm | n | accepts the premise | denies it | neither |
|---|--:|--:|--:|--:|
| `laconic` | 1,683 | 40 (**2.4%**) | 1,444 (85.8%) | 199 (11.8%) |
| `baseline` | 270 | 0 (0.0%) | 256 (94.8%) | 14 (5.2%) |

So **the suite has no case on which a bare yes is a complete answer**, and
[#136]'s report is the opposite case: the premise was true, the model had made
the claim itself, and the correct answer was *"yes, and the second metric is not
a safe substitute either."* A cutoff that catches 400 words of re-derivation on
that question convicts 80 words of required correction on all thirteen of these.
That is not a threshold in the wrong place; it is a population that cannot carry
the construct.

## The structural alternative, refuted before it was labelled

Kimi's answer to `tools/consult.sh` argued the response side should be binary
rather than a threshold: a markdown heading, a list, more than one paragraph, or
an explicit explanatory clause, on the reasoning that *"a single line cannot
contain a `##` heading"*. The sharpest of those is measurable for free and it has
no hits:

| signature | `laconic` | `baseline` |
|---|--:|--:|
| markdown heading | **0.00%** | **0.00%** |
| list | 13.2% | 73.3% |
| more than one paragraph | 37.5% | 99.3% |

**Zero of 1,953.** The one signature that is genuinely incompatible with "a word
or a line" never fires in this archive, so it can neither be validated nor used;
the two that do fire are the word count again, with the baseline at 73% and 99%.
The heading is also the signature [#136]'s own report names — three `##` sections
— which places the gap between the report and every instrument the loop has,
where [round 32](round-32.md) and
[`register-inheritance-136.md`](register-inheritance-136.md) already put it.

## The one place the shape does appear

Every laconic hit that opens by accepting the premise, all 17 of them, read in
full under the same criterion:

| label | n | precision |
|---|--:|--:|
| violation | 12 | **70.6%** |
| borderline | 4 | |
| not a violation | 1 | |
| violation + borderline | 16 | **94.1%** |

They are the reported shape almost verbatim — *"Yes, that's correct"*, and then
the four-purchase swing, the coin-flip quote, the substitute analysis and a
recommendation, in 101 to 158 words.

**This is a lead and not a measurement, and the reasons are disqualifying on
their own.** The stratum was chosen *after* the seed-136 sample was labelled,
which is the post-hoc subgroup selection [round 56](round-56.md) named and
[round 57](round-57.md) refused to take. It is 2.4% of the laconic arm, so no
round this loop buys could move it. 16 of the 17 are haiku. And `baseline` has
**zero** runs in it, so there is no control arm at all: the one stratum where the
detector is precise is the one stratum where nothing can be compared.

## What this closes, and what would open it

**[#136] proposal 3 is not buildable on this benchmark, and the reason is the
cases rather than the cutoff.** Precision is 30.0% strict, 63.3% if every
redundant restatement counts, and the detector may not be promoted at either
figure — the first is below the 55.3% that parked [#155] and the second is
decided by the judgement that parked it. Nothing in
[`closed-question/`](closed-question/) is imported by `evals/bench/metrics.py`
and nothing there has a `POLICY_RANK` entry, because a detector this imprecise
may not name a rule.

That leaves [#136] with all three proposals answered: proposal 1 rejected by
round 64, proposal 2 priced at −0.16 of the demonstration gap by round 60, and
proposal 3 unmeasurable here.

**What would open it is one case, and it is the cheapest thing this cluster has
ever asked for.** A closed question whose premise is **true** and whose complete
answer is the confirmation plus at most one clause — the shape [#136] actually
reported. On such a case any material beyond the confirmation is unrequested *by
construction*, so the detector needs no redundancy judgement and no labeller: the
fixture decides what a complete answer is before any response exists. That is
the same move [`closing-recap-305.md`](closing-recap-305.md) arrived at from the
other side — *"a case whose fixture makes the correct closing knowable"* — and it
is now asked for by two of the cluster's eight issues.

Two constraints on building it, both learned here:

- **It belongs in `evals/pilot/`, not `evals/cases/`.** A case added to the suite
  moves `cases_cksum` and gives every future round-wide pass an unseeded cell.
  `register-*` is the precedent: fixtures by symlink, held to its contract by
  `tests/test_evals_layout.sh`, and no fatal counter gains a cell.
- **It has to state the qualification in the fixture, not withhold it.** The
  reason all thirteen existing cases carry a false premise is that a trap needs
  something to grade. A true-premise case grades the *absence* of surplus, so its
  trap is a ceiling rather than a floor, and that is a criterion this repository
  has never written. `evals/CRITERIA.md` would gain its first one.

## Where the design came from

The design was put to `tools/consult.sh` before anything was built, and two of
the three targets answered. Both attacked the same thing, from opposite
directions, and both changed what was built.

- **DeepSeek: the 80 is the symptom, not the disease — a continuous quantity
  registered as a binary finding.** It argued the cutoff must be frozen from the
  rule text before any arm is read, that the whole curve must be published rather
  than the chosen point, and that this belongs in `MEASUREMENTS` rather than
  `POLICY_RANK` because the rule file has no line stating an "over N words"
  prohibition to anchor. All three are in this document: the curve is the table
  above, the cutoff is [#136]'s own and was never moved, and nothing is
  registered anywhere. Its prediction — *"if the null shows both arms mostly
  under the cutoff you have a re-binned `output_tokens`"* — came out the other
  way round, with both arms mostly *over* it, and the conclusion is the one it
  named.
- **Kimi: make the response side structural and genuinely binary.** Headings,
  lists, paragraph counts. Measured above: the heading rate is 0.00% on both
  arms, which refutes the sharpest form outright and cost nothing to establish
  because the archive was already in hand. Its second point — that a hand label
  asking "should this have been a line?" is not salvageable — is the reason the
  criterion in `labels.json` asks about re-derivation and unraised subjects
  instead, and the reason `borderline` exists as a separate column rather than
  being resolved by the author's own preference.

Codex was asked and did not answer inside the timeout.

[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#305]: https://github.com/JordanMPDS/laconic/issues/305
