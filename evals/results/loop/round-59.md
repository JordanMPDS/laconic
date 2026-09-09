# Round 59 — which of the 750 words carries the compression?

**Registered 2026-09-09, before any run. No rule edit.** An arm round for
[#275]: three arms in one interleaved batch, the shipped `full` slice against
two ablations of it.

## Why the round exists

[Round 58](round-58.md) tested [#270]'s dilution hypothesis and inverted it. Two
minimal slices carrying every instruction with a measured effect, in 295 and 317
words against the shipped slice's 1,041, produced answers **1.66x and 2.09x
longer** — on every cell, in both reading strata, on both case families, at
permutation p ≤ 0.00002. So the compression lives substantially in the ~750
words those slices dropped, and round 58 deliberately does not say which of
them.

[#275] names the candidate: the minimal slices removed every *rendered
instance* while keeping every *instruction*. Out went the worked OOM question
and its three-row level table, the four arrow `Wrong:`/`Right:` pairs, the
design licence's own `Wrong:`/`Right:` pair, the section headings, and a
quantity of ordinary prose. A rule that says "be brief" and a rule that shows a
20-word answer beside a 60-word one are not the same treatment.

## The arms

Each arm is the shipped slice **minus one named block and nothing else** — not a
rewrite and not an extract, so a difference against the control attributes to
that block. `tests/test_bench.py` enforces it: every line of an arm has to be a
line of the shipped slice, in order, and the removed word count has to be
exactly the figure below.

| arm | words | block removed | words removed |
|---|--:|---|--:|
| `laconic` | 1,041 | — (control, `hooks/laconic.sh start` at level `full`) | — |
| `laconic-abl-shown` | 832 | every rendered short answer: the worked OOM question, its three-row level table and its coda, and the design licence's `Wrong:`/`Right:` pair | 209 |
| `laconic-abl-arrow` | 876 | the arrow rule entire: the prohibition, its enumeration of forbidden uses, the four `Wrong:`/`Right:` lines, the fenced-code exemption | 165 |

**The pairing is the design, and it is what makes a null readable.**
`abl-shown` removes the file's only rendered instances of a brief answer.
`abl-arrow` removes a comparable bulk of on-topic instruction — carrying its own
rendered `Wrong:`/`Right:` demonstrations — that says nothing about length
anywhere in it. `abl-shown` moving while `abl-arrow` does not separates "showing
a short answer is the carrier" from "any 200 words are". Both moving together
says the variable is bulk. Every instruction each block illustrates stays in the
arm that drops it.

All three arms are delivered by `--append-system-prompt`, the same path the
`laconic` arm uses, so the comparison is treatment against treatment.

## Three registered deviations from [#275]'s proposed ladder

[#275] proposed four arms at the ladder's own reps. All three changes below were
made before generating and each has a reason.

1. **[#275]'s fourth arm cannot be built.** It names "the six clauses rounds 44
   to 49 measured at zero", but every one of those rounds' edits was **rejected
   and reverted** — see their rows in [`LEDGER.md`](LEDGER.md). Those clauses
   are not in the shipped slice, so there is nothing to ablate. The arm is
   dropped rather than approximated.
2. **[#275]'s arrow arm is widened from the four `Wrong:`/`Right:` lines (70
   words) to the whole arrow rule (165 words).** At 70 words the arm is not
   word-matched against a 209-word demonstration arm, so a null on it would be
   a null about size rather than about content. Widening also makes the arm the
   thing the design needs: a block with demonstrations *and* prose in it, none
   of it about length.
3. **Three arms at 40 reps rather than four at 30.** Same 720 generations. The
   power arithmetic below is why.

*Origin: deviations 2 and 3, and the estimand in the next section, came from
the `codex` delegate target on `bash tools/consult.sh`, which argued that a
word-mismatched control smuggles in its own treatment and that a six-cell sign
test cannot be the primary of a multi-arm round. `deepseek` and `kimi` did not
answer.*

## Scope and depth

Sonnet only, 40 reps per arm, six cases, **720 generations**, three shards
declaring `--concurrency 3`, no judging in step 1.

**Every shard runs every case.** The three processes split the rep range
(`run.py --rep-offset`, 0-13, 14-26, 27-39) rather than splitting the cases the
way round 58 did. A run is keyed on (case, arm, model, rep), so a rep split
gives each process a disjoint key space while every process still covers all
six cases and all twelve blocks. Splitting by case instead makes case
inseparable from shard, and therefore from wall-clock time and from any CLI
release that lands mid-round: round 58's per-shard spread of 1.23x to 1.43x on
one arm cannot be read as case heterogeneity or as process artefact, because
there each shard *was* a pair of cases. Under the rep split, the per-shard
contrast below is a genuine robustness check.

- `design-cache`, `design-realtime`, `design-upload` — the sanctioned `one_turn`
  scope, the three cells that can tell a fixture-derived answer from a recalled
  one ([#88]).
- `destructive`, `code-fidelity`, `badnews` — the three cells whose `expect.json`
  carries never-cut keywords, so the contract check is a free substring test.

**All six are in the prose-words scope, registered in advance.** Round 58 scored
words on the three `design-*` cells and reported the contract cells as
exploratory, where they showed the *largest* ratios — `badnews` 9.5 words
against 36 and 60. Widening the registered scope is the correction that finding
asks for, and it doubles the blocks the primary test runs over.

## Endpoints, registered before generation

**Primary, free, six cells, two contrasts against `laconic` at Bonferroni
α = 0.025:**

**Mean log prose words, blocked on the case**, permutation on arm labels within
block at seed 58, reported as a geometric-mean ratio. Each block contributes the
difference of its two arm means and every block weighs the same, so no one wide
cell carries the contrast, and a cell with 30 grounded runs cannot outvote one
with 5.

**The reading stratum is a secondary here, not part of the primary, and that is
a change from round 58.** `grounded()` is `num_turns > 1` — what the run did
under its own treatment. An arm can change whether a response opens a file at
all, so blocking on it conditions on a post-treatment variable, which the
assignment does not identify. The quantity this round needs is the total effect
of shipping the slice: length as it actually comes out, reading included. [#131]'s
concern is answered by the reading-rate guardrail below, which is the endpoint
built for it, rather than conditioned away in the primary. Both blocks are
computed and both are reported; only the case block is the primary. Dropping the
stratum costs almost nothing: measured on round 58's 540 runs the within-cell
standard deviation of log words rises from 0.280 to 0.290, moving the minimum
detectable ratio from 1.082x to 1.085x.

Round 58's per-cell-median test stays, as a robustness display and not as the
primary. It cannot be the primary here: with six cells the exact two-sided sign
test bottoms out at p = 0.03125, which does not clear α = 0.025 for two
contrasts, so a sign test on this scope is unable to reject whatever the data
say.

**The primary is also reported per shard, as a diagnostic and not an endpoint.**
Three processes, each with all twelve blocks. A contrast carried by one process
is a warning that something wall-clock or release-shaped is in the number, and
the pooled figure alone cannot show that. Substantial arm-by-shard spread is
reported and weakens the reading; it does not by itself reject.

**Guardrail 1, free: reading rate** on the three `design-*` cells, share with
`num_turns > 1`, non-inferiority against `laconic` at the 15-point margin round
58 registered. This is [#264]'s failure mode and the round must not repeat it:
an arm that bought its compression by not opening a file has not won.

**Guardrail 2, free: never-cut keyword failures** pooled over the three contract
cells, 120 runs per arm. **A smoke alarm, not an equivalence test** — the rule
of three bounds each arm near 2.5% and the archive's rate on these cells is near
zero. Fatal only on the catastrophic loss defined in advance: more than 5
failing runs of 120 where `laconic` fails 1 or fewer.

**Manipulation check, not an endpoint: responses carrying an arrow.**
`abl-arrow` deletes the arrow prohibition, so its arrow rate must rise; if it
does not, the arm did not receive its treatment and its null says nothing. The
check has a measured prior — rescoring round 58 through the same counter reads
`laconic` **5 of 90** against the minimal slices' 37 and 41 of 90, both at
Fisher p < 0.0001, on slices that dropped the same rule.

## Power, and what a null would mean

The pooled within-cell standard deviation of log prose words, measured over
round 58's own 540 runs, is **0.290** within (case, arm) and 0.280 within
(case, arm, stratum). At 240 runs per arm over six blocks the first gives a
standard error near 0.027 and a **minimum detectable ratio of about 1.085x** at
α = 0.025 with 80% power. The stratified secondary reads 1.082x, so the choice
of block costs three thousandths of a ratio.

If the effect were linear in words removed, round 58's 746 words at 1.66x
predicts **1.15x** for a 209-word ablation and **1.12x** for a 165-word one.
Both sit comfortably above the detection threshold, which is the point of buying
40 reps rather than 30. So a null here is not the uninterpretable kind: it bounds
the block's effect below roughly 1.09x and thereby rules out proportionality,
which is a result about the shape of the dose-response rather than an absence of
one.

## The registered reading

**This round tests two blocks, not two mechanisms, and no result of it licenses
a mechanism claim.** The 209 words `abl-shown` deletes are three things at once:
the file's only rendered instance of a short answer, its only side-by-side
calibration of the three levels, and a worked application of the rule to a
specific question. A positive result identifies *that block*, and all three
readings survive it. Separating them needs a later factorial round — the table
replaced by a prose description of the same answer, the worked framing kept
without the three-row calibration, a short answer shown without the level
ladder — and four arms inside 720 generations would only localise one of the
three while costing every arm its power. So the reading below is written in
terms of blocks, and the discussion of what carries the effect is named as
speculation where it appears.

Fixed before the numbers:

- **`abl-shown` lengthens, `abl-arrow` does not.** The deleted demonstration
  block carries a measurable part of the compression and a word-matched block of
  on-topic instruction does not. This is [#275]'s hypothesis at the resolution
  this design actually has. It does *not* establish that showing rather than
  describing is the mechanism; it establishes that the block is load-bearing and
  makes the factorial round worth buying.
- **Both lengthen, and by a similar ratio.** Bulk is the variable: ~200 words of
  anything costs roughly this much, and the next question is about total length
  rather than about content.
- **Neither lengthens.** The effect is not proportional to words removed. Two
  blocks of 200 words are worth less than 2/7 of round 58's gap each, so
  whatever carries it is either in the material neither arm touches or does not
  decompose block by block at this granularity.
- **`abl-arrow` lengthens and `abl-shown` does not.** Not predicted by anything,
  and the round would report it as such rather than explain it.

Anything reported outside these endpoints is exploratory and says so where it is
written.

## Four further changes, all made before generating

Registered after a second `bash tools/consult.sh` pass put the design in front
of the delegate targets with its three weakest joints named. `codex` and `kimi`
answered; `deepseek` was asked and did not.

1. **The primary blocks on the case alone, and the reading stratum becomes a
   secondary.** `codex`: blocking on whether a run opened a file conditions on
   post-treatment behaviour, and it is separately one of the round's own
   guardrails. Both were right and both blocks are reported; the arithmetic cost
   is in the power section.
2. **Every shard runs every case, through a new `run.py --rep-offset`.** `kimi`
   named the shard split as the design's weakest joint and the fix as making
   each of the three processes cover all six cases. Round 58's case-per-shard
   split left case, process and wall-clock inseparable.
3. **The registered reading is a block-deletion claim, not a mechanism claim.**
   Both targets independently said the `abl-shown` block is three treatments
   welded together and that no three-arm design can separate them. Neither
   offered a cheap fix, and the honest move was the one they both named: fix the
   claim to the resolution the design has, and name the factorial follow-up.
4. **The primary is reported per shard as a diagnostic.** Asked for by both,
   and only interpretable because of change 2.

`codex` also suggested a max-|T| permutation adjustment in place of Bonferroni
for a small free power gain. Not adopted: Bonferroni is registered, it is
already implemented, and the round has power to spare against both predicted
effects.

## Bound, fatal to the round

A single `rules_cksum` across every snapshot, and any pass that crosses a CLI
release is reported through `python3 evals/bench/release.py` before a contrast
is read out of it ([#272]).

---

# Result

**720 generations, 0 failed, one `rules_cksum` (594915793), one CLI release
(2.1.266).** `release.py` reports no unreadable span and no arm imbalanced
across a release; `concurrency.py` reads the declared 3 on all nine arm-days.
Scored with

```sh
python3 evals/pilot/score_dilution.py \
  --words-cases 'design-cache,design-realtime,design-upload,destructive,code-fidelity,badnews' \
  evals/snapshots/loop/round-59-{a,b,c}.json
```

## The registered reading's first branch obtains

**`abl-shown` lengthens and `abl-arrow` does not**, on the primary, on the
secondary, and in every shard.

| arm | words removed | primary ratio | p | Bonferroni α = 0.025 |
|---|--:|--:|--:|---|
| `laconic-abl-shown` | 209 | **1.119x** | **0.0008** | clears |
| `laconic-abl-arrow` | 165 | 0.967x | 0.3054 | null, and the point estimate is the other way |

Blocked on case, six blocks, 240 runs per arm, permutation seed 58. The
secondary that additionally blocks on the reading stratum agrees and is larger:
`abl-shown` **1.184x, p < 0.0001**, `abl-arrow` 1.024x, p = 0.4393.

**The per-shard diagnostic does not weaken it.** Each of the three processes ran
all six cases, and `abl-shown` is above 1 in all three — 1.080 (p = 0.1893),
1.104 (p = 0.1032), 1.180 (p = 0.0054) — while `abl-arrow` is at or below 1 in
all three: 0.986, 0.922, 0.992. No contrast here is carried by one process.

**The manipulation check fired, which is what makes `abl-arrow`'s null worth
anything.** Responses carrying an arrow: `laconic` **8 of 240**, `abl-arrow`
**25 of 240**, Fisher **p = 0.0033**. The arm received its treatment — deleting
the prohibition roughly tripled the behaviour it prohibits — and still produced
answers no longer than the control's. `abl-shown` reads 17 of 240 (p = 0.0986),
which is not part of any endpoint and is noted because it is not zero.

## What the round establishes, stated at the resolution it has

**Removing 209 words of worked demonstration lengthens answers by about 12%.
Removing 165 words of on-topic prohibition does nothing.** The variable is not
bulk. That is the finding, and it is the one [#275] bought the round for.

Against round 58 on the same estimator, the two minimal slices removed ~735
words for a geometric-mean **1.606x** (+0.4739 log). Proportionally:

| block | share of the 735 words | share of round 58's gap it delivers |
|---|--:|--:|
| `abl-shown` | 28% | **24%** |
| `abl-arrow` | 22% | **−7%** |

So one block pays slightly under its weight and the other pays nothing, which is
the shape a null on *proportionality* takes when the effect is real but
content-specific. Three quarters of round 58's gap is still unaccounted for, in
material neither arm touches.

**This is a claim about a block and not about a mechanism**, as registered
before the numbers. The 209 words are the only rendered short answer, the only
side-by-side calibration of the three levels, and the only worked application of
the rule to a specific question, and a positive result on the block cannot tell
those apart. The replacement round that would is filed as [#277].

## Exploratory: the effect is confined to the case family the block is about

Not an endpoint, and reported as exploratory. Per-case geometric-mean ratios
against `laconic`, medians beside them:

| case | `abl-shown` | `abl-arrow` | `laconic` median |
|---|--:|--:|--:|
| `design-cache` | **1.260x** (240.0) | 1.019x (177.5) | 172.0 |
| `design-realtime` | **1.224x** (184.5) | 1.068x (165.0) | 151.5 |
| `design-upload` | **1.373x** (240.5) | 1.087x (188.0) | 172.0 |
| `destructive` | 1.027x (133.0) | 0.964x (123.5) | 120.5 |
| `code-fidelity` | 0.962x (26.5) | 0.832x (20.5) | 28.0 |
| `badnews` | 0.940x (11.5) | 0.860x (12.5) | 22.5 |

`abl-shown`'s whole effect is on the three design questions and it is absent on
the three contract cells. The deleted block is *about* advice-shaped questions —
a worked "should I bump the memory limit?" and the design licence's own
`Wrong:`/`Right:` pair — so the material and the cells where it matters line up.
That is a hypothesis for the factorial round, not a result of this one: six
cells cannot separate "the block governs design answers" from "design answers
are simply where this file has room to move".

## Guardrail 1 failed, on both arms

**Neither ablation can be certified non-inferior on reading rate**, and the
registered margin is what it is:

| arm | reads | rate | difference | lower bound | margin | verdict |
|---|--:|--:|--:|--:|--:|---|
| `laconic` | 45/120 | 37.5% | — | — | — | — |
| `laconic-abl-shown` | 32/120 | 26.7% | −10.8 pts | −20.5 | −15.0 | **INFERIOR** |
| `laconic-abl-arrow` | 33/120 | 27.5% | −10.0 pts | −19.7 | −15.0 | **INFERIOR** |

Reported as a failure of the registered test rather than reinterpreted. What the
round actually has is an inability to certify: neither fall reaches significance
(Fisher p = 0.0967 and 0.1293), and at n = 120 a 15-point margin cannot be
cleared by a 10-point observed fall whichever way the truth lies. Round 58's
`laconic-min-a` failed the same guardrail the same way at n = 90. Three rounds
have now run this test and none of them could certify anything with it; that is
filed as [#278], because a guardrail that cannot pass is not protecting
anything.

**It does not rescue `abl-arrow` or explain `abl-shown`.** Reading less makes
answers shorter, so a reading fall biases *against* the lengthening the primary
found — `abl-shown` lengthened anyway, and by more inside the stratum (1.184x)
than across it. And `abl-arrow`'s null survives the same conditioning at 1.024x,
p = 0.4393, so its flat result is not a reading fall cancelling a real effect.

Guardrail 2, the never-cut contract: **0 failures of 120 on all three arms.**
Certifies nothing by design — the rule of three bounds each arm at 2.5% — but
rules out the one way a length result could have been trivial.

The per-cell median display, kept from round 58 as robustness: 1 of 5 cells
shorter for each arm, sign test p = 0.3750 both. Uninformative, exactly as the
registration said a six-cell sign test would be, and it is the reason it is not
the primary.

## No rule edit

None was registered under any outcome and none follows. The finding argues for
*keeping* 209 words the file already ships, which needs no change, and the
mechanism question it opens is a round rather than an edit.

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#270]: https://github.com/JordanMPDS/laconic/issues/270
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#275]: https://github.com/JordanMPDS/laconic/issues/275
[#277]: https://github.com/JordanMPDS/laconic/issues/277
[#278]: https://github.com/JordanMPDS/laconic/issues/278
