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

**Mean log prose words, blocked on (case, reading stratum)**, permutation on
arm labels within block at seed 58, reported as a geometric-mean ratio. Each
block contributes the difference of its two arm means and every block weighs
the same, so no one wide cell carries the contrast. Blocking on the reading
stratum is [#131]; blocking on the case is what stops a cell with 30 grounded
runs outvoting one with 5.

Round 58's per-cell-median test stays, as a robustness display and not as the
primary. It cannot be the primary here: with six cells the exact two-sided sign
test bottoms out at p = 0.03125, which does not clear α = 0.025 for two
contrasts, so a sign test on this scope is unable to reject whatever the data
say.

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
round 58's own 540 runs, is **0.264**. At 240 runs per arm over twelve blocks
that gives a standard error near 0.024 and a **minimum detectable ratio of about
1.077x** at α = 0.025 with 80% power.

If the effect were linear in words removed, round 58's 746 words at 1.66x
predicts **1.15x** for a 209-word ablation and **1.12x** for a 165-word one.
Both sit comfortably above the detection threshold, which is the point of buying
40 reps rather than 30. So a null here is not the uninterpretable kind: it bounds
the block's effect below roughly 1.08x and thereby rules out proportionality,
which is a result about the shape of the dose-response rather than an absence of
one.

## The registered reading

Fixed before the numbers:

- **`abl-shown` lengthens, `abl-arrow` does not.** The rendered short answer is
  the carrier. This is [#275]'s hypothesis and the one the round was bought to
  test.
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

## Bound, fatal to the round

A single `rules_cksum` across every snapshot, and any pass that crosses a CLI
release is reported through `python3 evals/bench/release.py` before a contrast
is read out of it ([#272]).

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#270]: https://github.com/JordanMPDS/laconic/issues/270
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#275]: https://github.com/JordanMPDS/laconic/issues/275
