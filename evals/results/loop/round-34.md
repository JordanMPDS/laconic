# Round 34: subject size is not the missing factor

**This round proposes no rule edit.** It tests the variable round 33 pointed at
and reports a null, with the bound that null carries.

## Where round 33 left it

Round 33 isolated ownership — the model confirming a conclusion it wrote rather
than one it read — and measured it decisively: longer in 6 of 6 cells
(p = 0.031) and 29 of 30 rep-paired runs (p < 0.0001). It was also small.
Laconic's median moved 93 to 127 words against the ~400 [#136] reports, so
about a third of the gap was accounted for and roughly three times that was
not.

Round 33 named the next candidate, taking it from round 32's own framing of the
cluster: *a short question about a large subject, where the subject's size sets
the answer's size.* These fixtures are one page. [#136]'s subject was an
argument developed across a session.

## The instrument

`wide-metric`, `wide-index` and `wide-rollback` **share their `prompt.md` byte
for byte** with the `recall-*` case of the same stem — same fixture filename,
same open turn 1, same closed turn 2 — and their traps are byte-identical, so
quality is graded by the same criterion. The only difference is the fixture:

| Stem | `recall-*` | `wide-*` | Ratio |
|---|--:|--:|--:|
| metric | 483 w | 1,817 w | 3.8× |
| index | 557 w | 1,298 w | 2.3× |
| rollback | 607 w | 1,394 w | 2.3× |

Everything added is real supporting material a careful answer *could* draw on —
a power table and segment breakdowns, `BUFFERS` output and measured build times,
an impact table and the release job's order of operations — and none of it is
**required** by the closed question, whose correct answer is unchanged. If a
correct answer grows anyway, that is the failure the cluster reports.

`recall-*` was regenerated in the same interleaved batch rather than carried
from round 33's snapshot an hour earlier. It is cheap, and it removes the only
methodological objection.

## The registered question

> Holding ownership constant at the `recall-*` shape and scaling the fixture
> 2.3–3.8×, the closed question's correct answer is unchanged, so median words
> on the graded turn should be flat. Falsifier: a laconic median at or above
> ~250 words, or a tail reaching [#136]'s ~400.

## Result

Median words on the graded turn, 5 reps a cell:

| Case | baseline | laconic |
|---|--:|--:|
| `recall-metric` | 174 | 118 |
| `recall-index` | 173 | 136 |
| `recall-rollback` | 166 | 98 |
| `wide-metric` | 177 | 157 |
| `wide-index` | 189 | 129 |
| `wide-rollback` | 174 | 92 |

| | baseline | laconic |
|---|--:|--:|
| `recall-*` | 173 | 126 |
| `wide-*` | 177 | 132 |
| **shift** | **+2.3%** | **+4.8%** |

**A null.** Wide is longer than its control in 4 of 6 cells (two-sided exact
sign test, p = 0.6875) and in 16 of 29 rep-paired runs (p = 0.7111). The
falsifier did not occur: laconic's widest response across 30 runs is 193 words.

Set against round 33 run on the same instrument a week's worth of rounds apart
in method but an hour apart in time, the contrast is the finding:

| Variable | cells | rep-paired | laconic median |
|---|--:|--:|--:|
| ownership (round 33) | 6 of 6, p = 0.031 | 29 of 30, p < 0.0001 | 93 → 127 |
| subject size (round 34) | 4 of 6, p = 0.688 | 16 of 29, p = 0.711 | 126 → 132 |

## What the null does and does not say

**The manipulation is smaller than the fixture ratios suggest.** Turn-1 context
is 73,710 tokens on `recall-*` and 76,042 on `wide-*`. Tripling the fixture
moved it from roughly 2% of what the model sees to roughly 5%.

So the honest statement is: **a fixture worth +3% of context does not move
answer length**, not "subject size does not matter". A manipulation that made
the subject the *bulk* of context would be a different experiment, and this
round does not speak to it.

That bound was written down before the numbers were read, from the interim
token counts, rather than constructed afterwards to soften a null.

## Replication, and what this instrument can resolve

`recall-*` ran in both rounds, one hour and two independent batches apart:

| | round 33 | round 34 |
|---|--:|--:|
| `recall-*` baseline, pooled | 175 | 173 |
| `recall-*` laconic, pooled | 127 | 126 |

Pooled across three cases the family replicates within 1%. Individual cells do
not: `recall-metric`/baseline read 154 then 174, and `recall-index`/baseline 201
then 173, both about 14%.

That is worth recording as a property of the instrument. **At 5 reps a cell the
pooled family median is stable and a single cell median is not**, so a
hypothesis scored on one cell at this depth is scoring sampling noise. It also
means round 33's headline numbers are corroborated by an independent batch,
which no round in this loop has previously been able to say.

## Grading

Traps grade **60 of 60**, both arms, both families, on criteria byte-identical
to `recall-*`'s. The larger fixture did not make the question harder, and the
extra words in `wide-*` were not buying correctness.

**All 60 runs opened their fixture**; every cell 5/5, so no [#131] stratum
crossing.

## What this leaves

Two of [#136]'s candidate mechanisms are now measured. Ownership is real and
worth about a third more words. Subject size, at +3% of context, is worth
nothing. Roughly three times the measured effect remains unexplained.

The next candidate is the one the issue's own wording points at most directly —
*"when the model has a lot of recent context it is proud of"*. That is a claim
about the **volume of the model's own prior output**, not about the size of the
document it read. `recall-*` gives it exactly one prior answer. A family that
asks four or five open questions before the closed one would give it several,
and [#166] means `run.py` can express that without further machinery.

120 generations across 60 runs, 60 judgments, 0 failed, $4.92.

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#166]: https://github.com/JordanMPDS/laconic/issues/166
