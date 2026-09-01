# Round 35: accumulated own output is the second real mechanism

**This round proposes no rule edit.** It tests the last of the three mechanisms
[#136] offers, and finds a second real one.

## The three candidates, and where they stood

[#136] reports ~400 words in answer to an eight-word closed question, and its
own text offers three explanations. Rounds 33 and 34 tested two:

| Round | Variable | Result |
|---|---|--:|
| 33 | **ownership** — confirming a conclusion the model wrote rather than read | real: 6 of 6 cells, 29 of 30 paired, +35% words |
| 34 | **subject size** — the fixture scaled 2.3–3.8×, worth +3% of context | null: 4 of 6 cells, p = 0.688 |
| 35 | **accumulated own output** — this round | — |

The third is the issue's own wording, and it is a claim about neither the
document nor the single prior answer: *"when the model has a lot of recent
context it is proud of."* `recall-*` gives it exactly one prior answer.

## The instrument

`deep-metric`, `deep-index` and `deep-rollback` share their fixture, their final
question and their trap with the `recall-*` case of the same stem. `recall-*`
asks two turns; `deep-*` asks five, so the model reaches the closed question
carrying **four of its own answers instead of one**.

**The three added turns are deliberately kept off what the trap grades.** A
first draft asked `walk me through why the absolute difference is not the fix`,
which states the metric trap's required content outright, and `which of the
working shapes would you pick`, which states the index trap's. Those were
replaced — the added turns now ask about the assignment audit, the derivation of
the 34,000-sessions figure, why the planner ignores the `tenant_id` index, the
customer impact, and what went well — so the closed question stays fresh and
accumulated output is the only variable.

## The registered question

> Raising the model's own accumulated prior output from one answer to four,
> median words on the graded turn should rise if [#136]'s *"a lot of recent
> context it is proud of"* is the operative mechanism. A shift of round 34's
> size — ≤5%, p > 0.5 — falsifies it.

## Result

Median words on the graded turn, 5 reps a cell, one interleaved batch:

| Case | baseline | laconic |
|---|--:|--:|
| `recall-metric` | 153 | 114 |
| `recall-index` | 177 | 138 |
| `recall-rollback` | 167 | 103 |
| `deep-metric` | 242 | 196 |
| `deep-index` | 211 | 173 |
| `deep-rollback` | 196 | 109 |

| | baseline | laconic |
|---|--:|--:|
| `recall-*` | 172 | 114 |
| `deep-*` | 225 | 156 |
| **shift** | **+30.8%** | **+36.8%** |

**Real, and about the same size as ownership.** `deep-*` is longer than its
control in **6 of 6 cells** (two-sided exact sign test, p = 0.031) and in
**26 of 30 rep-paired runs** (p = 0.0001).

## The chain

Each step measured against a control generated in its own batch:

| | prior own answers | turns | laconic median | widest of 15 |
|---|--:|--:|--:|--:|
| `confirm-*` (round 33) | 0 | 1 | 93 | 114 |
| `recall-*` (rounds 33, 35) | 1 | 2 | 127, 114 | 144 |
| `deep-*` (round 35) | 4 | 5 | **156** | **266** |

From `confirm-*` to `deep-*` is **+68%**, and the widest single laconic response
more than doubles, 114 to 266 words.

That is still short of [#136]'s ~400. But unlike subject size, **this mechanism
scales with the thing the report had more of.** Four prior answers is not many;
the session [#136] describes had considerably more. The remaining gap is now
plausibly a matter of degree rather than a missing mechanism, which is a
different and much weaker claim than the one round 33 left open.

## A correction to round 34

Round 34 read `recall-*` in two batches an hour apart, found the pooled family
medians within 1%, and concluded that **at 5 reps a pooled family median is
stable**. A third independent draw does not support that as stated:

| | round 33 | round 34 | round 35 | range |
|---|--:|--:|--:|--:|
| `recall-*` baseline | 175 | 173 | 172 | 1.7% |
| `recall-*` laconic | 127 | 126 | **114** | 10.3% |

The baseline claim holds. The laconic one does not — that family median moved
10% across three batches, which is close to the 14% round 34 attributed to
single cells. **The corrected statement is that the baseline family median is
stable at this depth and the laconic one is not**, and any round comparing
laconic across batches needs its own control rather than a stored one.

This round's verdict does not depend on it: `recall-*` and `deep-*` were
generated in the same batch, so the comparison is internal.

## Grading, and a case that may be miscalibrated

> **Corrected 2026-09-01 by [#172].** The trap was widened and all three
> failures below flip to pass, so **this round grades 60 of 60** under the
> criterion now in `evals/cases/`. The corrected grading is
> `round-35-judgments-v2.json`; `round-35-judgments.json` is the superseded file
> and is kept. Rounds 33 and 34 were re-judged on the same stem in the same pass
> and did not move, so the widening loosened only what it was aimed at. The
> section below is the round as it was scored, and it is what found the defect.

Traps grade **57 of 60** — the first quality failures this family has produced.
Rounds 33 and 34 both graded 60 of 60.

All three failures are on the `metric` stem, and all three are the same answer:

> The response opens with "Not quite" and explicitly denies that lift
> specifically is the wrong metric, reframing the issue as purely a sample-size
> problem rather than confirming lift is wrong (even though it correctly
> explains why the absolute-difference substitute doesn't fix the readout).

Two are `recall-metric`/baseline and one is `deep-metric`/laconic, so it is
spread across both arms and both families and is **not an effect of the
manipulation**. Both arms' word counts are unaffected either way; the metric
this round scores is words.

**The trap is arguably the thing that is wrong.** It requires the answer to
confirm that lift is the wrong metric here. The fixture's own conclusion is
`Neither metric supports a ship decision on this data`, and its recommendation
is to run to the needed sample size or pick a higher-frequency proxy. A response
that says "not quite — this is a sample-size problem, not a metric-choice
problem" is reading the fixture correctly and failing anyway. That is worth
fixing before the `metric` stem is used to score anything, and it was filed as
[#172] rather than fixed here, because editing a case in the round that found it
is how a criterion gets tuned to a result. It was fixed afterwards, as a separate
unit; see the correction at the top of this section.

One confound is named and dismissed: `deep-metric`'s added turn asks how the
34,000-sessions figure is derived, which primes exactly the sample-size framing
that fails. That could explain the `deep-metric` failure. It cannot explain the
two in `recall-metric`, which has no such turn.

**All 60 runs opened their fixture**, every cell 5/5, so no [#131] stratum
crossing.

## Operational note

The five-turn cells run at about 110 seconds against 35 for a two-turn cell, and
the batch was killed twice by something outside `run.py` before it completed on
the third attempt — no OOM, no crash trace, no error output. `run.py` resumes by
key, so each kill cost only the run in flight. The [#69] guard also refused a
resume that narrowed `--cases` from six cases to three, correctly: the stored
`cases_cksum` covers the scope the snapshot was started with, and narrowing it
would have produced one round from two scopes. That was not overridden.

210 generations across 60 runs, 60 judgments, 0 generation failures, $7.96.

## What this leaves

Two of [#136]'s three mechanisms are real and one is not:

- **ownership** — confirming your own conclusion — worth about +35%
- **accumulated own output** — worth about +35% at four prior answers, and it
  scales
- **subject size** — null at +3% of context

The cluster is now the right unit of work rather than this issue. Six issues
([#46], [#60], [#113], [#116], [#136], [#150]) have absorbed five rounds — 29,
32, 33, 34 and this one — and no document says what is collectively known. That
synthesis, and the decisions it enables about which of the six are answered,
outranks a sixth round.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#172]: https://github.com/JordanMPDS/laconic/issues/172
