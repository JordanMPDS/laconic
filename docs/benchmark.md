# Benchmark

440 API calls: 11 cases × 5 reps × 2 models × 4 arms — baseline, a terse-only
control, a synthetic word-compression foil, and laconic. Scored offline on
compression, readability, answer quality, and a deterministic never-cut safety
check. Full method, every honesty note, and every table:
[`evals/results/2026-07-31-benchmark.md`](../evals/results/2026-07-31-benchmark.md).

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | answers correct | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| **laconic** | **-33%** | +1% | **-29%** | **35** | 27 / 30 | 2 / 50 |
| terse-control | -11% | +3% | -13% | 50 | 27 / 30 | 1 / 50 |
| word-compression | +3% | +4% | -13% | 60 | 27 / 30 | 0 / 50 |
| baseline | 0% | 0% | 0% | 60 | 28 / 30 | 0 / 50 |

Every column is reported as measured, on both models and all four arms. The
per-case tables and the method notes behind each number follow.

**The readability column was corrected on 2026-08-03** and reads 0 / 9 / 11 / 1
in anything published before that date. See
[Readability](#readability--the-whole-point) for what the detector was missing
and why the correction went the way it did.

**The three levels were then measured against each other**, 330 more calls at
`lite`, `full` and `ultra`. The ladder the rule text implies is not there: `full`
is not shorter than `lite` (11 of 22 case/model cells shorter, sign test
p = 1.00) and `ultra` shortens the model's tool turns more than its answer. The
never-cut contract holds at every level. Published in full, including what it
costs this table's readability claim:
[`evals/results/2026-07-31-levels.md`](../evals/results/2026-07-31-levels.md).

## Compression

Median output tokens per case, n=5 per cell. The comparison that matters is
laconic against `terse-control` — a plain "be terse, no preamble, no closing
offers" instruction — because that isolates the rule set from merely asking for
brevity.

**Sonnet 4.5**

| case | baseline | terse-control | laconic | saved |
|---|--:|--:|--:|--:|
| `floor` | 201 | 220 | 82 | **59%** |
| `walkthrough` | 3701 | 3682 | 1628 | **56%** |
| `silent-success` | 1105 | 947 | 511 | **54%** |
| `ordered-steps` | 1329 | 1630 | 801 | **40%** |
| `decision` | 839 | 786 | 513 | **39%** |
| `fail-open` | 1265 | 1234 | 877 | **31%** |
| `code-fidelity` | 307 | 315 | 214 | **30%** |
| `conditional` | 908 | 981 | 740 | 19% |
| `badnews` | 435 | 414 | 372 | 14% |
| `stale-cache` | 1660 | 2245 | 1640 | 1% |
| `destructive` | 2336 | 2775 | 2462 | **-5%** |
| **median** | **1105** | **981** | **740** | **33%** |

`destructive` is the one Sonnet case that gets longer, which is the design
working: naming exactly what a `DROP TABLE` affects is never-cut content, so
laconic has nothing to trim there. `stale-cache` sits at 1% for the same reason
— it is the case that needs a mechanism explained, and a requested explanation
is not something laconic cuts.

<details>
<summary><strong>Haiku 4.5</strong></summary>

| case | baseline | terse-control | laconic | saved |
|---|--:|--:|--:|--:|
| `floor` | 266 | 236 | 225 | 15% |
| `silent-success` | 775 | 732 | 711 | 8% |
| `badnews` | 469 | 432 | 443 | 6% |
| `conditional` | 956 | 1017 | 911 | 5% |
| `walkthrough` | 1228 | 1008 | 1185 | 4% |
| `code-fidelity` | 425 | 421 | 418 | 2% |
| `decision` | 522 | 506 | 515 | 1% |
| `fail-open` | 922 | 843 | 960 | -4% |
| `ordered-steps` | 653 | 636 | 715 | -9% |
| `stale-cache` | 1246 | 1355 | 1404 | -13% |
| `destructive` | 711 | 791 | 837 | -18% |
| **median** | **711** | **732** | **715** | **-1%** |

Haiku's result depends on the aggregation convention, so no compression claim is
made for it in either direction. The table above is a median of per-case
medians (-1%); a flat median over the 55 raw runs gives 731 against 715, a 2%
cut. Sonnet compresses on both estimators — 33% and 37% — and the Sonnet figures
are the ones quoted above.

</details>

On Sonnet, laconic's stdev (175) is the lowest of the four arms and its max
(865) sits below baseline's median, so the gap is not one or two short outliers.
Dispersion per arm and model is in the results doc.

## Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | violations | responses affected (of 110) |
|---|--:|--:|
| baseline | 60 | 16 |
| terse-control | 50 | 12 |
| word-compression | 60 | 22 |
| **laconic** | **35** | **7** |

### The 2026-08-03 correction

This table read baseline 1, terse-control 9, word-compression 11 and laconic
**0** until the detector was corrected. `_symbol_hits` skipped every
`STRUCTURAL` line — bullets, numbered steps, headings, blockquotes and table
rows — on the reasoning that the rule forbids arrows "in running prose" and a
bullet is markdown structure rather than prose.

That reasoning was wrong, and wrong in the direction that flattered the result.
`rules/laconic.md` bans arrows "after a bold label", "in a 'quick runbook'
line" and "inside a quoted flow": three structural positions, and between them
the most common places the forbidden arrow actually appears. The detector was
blind to the rule's own worked example, `**Request A**: calls
`currentToken()` → token expired → calls `refresh()``, whenever it arrived as a
list item. Across every committed snapshot, 510 arrows sat in structural lines
and went uncounted.

What survives the correction: laconic is still the cleanest arm, on both total
violations and the share of responses carrying one (7 of 110, against
baseline's 16). What does not: the headline **0**. Laconic breaks its own
no-arrows rule in 7 responses of 110, and the earlier claim that a rule
revision had driven arrow violations to zero was an artifact of where the
detector was looking.

The correction was found by the rules loop, which scored an edit at 7 → 0 on
this metric while the model went on writing the same chains one list marker to
the left: [`evals/results/loop/round-01.md`](../evals/results/loop/round-01.md).

A numeric progression like `7 -> 11 -> 14` is still exempt. It quotes a series
rather than standing in for a conjunction.

**This is a `full`-level result.** Re-measured across the three-level run,
laconic's arrow violations are 25 at `lite`, 23 at `full` and 16 at `ultra` —
no level is clean, and the gap between levels is smaller than the earlier
"12 at `lite` against 0 at `full`" suggested. See
[`evals/results/2026-07-31-levels.md`](../evals/results/2026-07-31-levels.md).

### What readability does not say

The row above counts degraded grammar. It can show laconic making prose worse
and can never show it making prose better, so "shorter with grammar intact" is
where the deterministic evidence stops.

A blind judge was then asked the other question — which of two answers better
serves the reader — over 130 comparisons of responses this snapshot already
held. **It did not prefer laconic.** Against baseline: laconic 37, baseline 52,
21 ties, p = 0.137. The same judge picked the longer answer 63% of the time
(p = 0.019) and reversed its verdict on 35% of comparisons it saw twice, both
effects larger than the gap between arms, so the run supports no preference
claim in either direction. Reported in full, including the comparison withheld
for a 50% flip rate:
[`evals/results/2026-08-01-preference.md`](../evals/results/2026-08-01-preference.md).

## Answer quality

The three `quality` cases each present a fixture with a buried mechanism and a
plausible decoy, and ask a diagnostic question. The criterion is whether the
response names the mechanism, and every word of it comes from the fixture rather
than from `rules/laconic.md` — which is what makes these the only cases in the
suite from which a comparison between arms is legitimate.

| arm | answers correct (of 30) |
|---|--:|
| baseline | 28 |
| terse-control | 27 |
| word-compression | 27 |
| **laconic** | **27** |

**Laconic's answers were as often correct as baseline's** while being 31%
shorter on Sonnet across those same three cases. A one-response difference,
Fisher's exact two-sided p = 1.00.

This is a coarse instrument and the results doc publishes its power curve: at
n=30 per arm it would have caught a drop to about 64% and would have missed
anything smaller. Two of the three cases are at ceiling — every arm passes — so
the only separation comes from `stale-cache` on Haiku, where all four arms sit
within one response of each other. Read it as ruling out a large regression, not
as a fine-grained quality measurement.

## Cost, reported net

The injected rules cost tokens of their own, so the net per-call cost sits
slightly above baseline on both models even where output tokens drop.

| median USD per call | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0165 | 0.0716 |
| laconic | 0.0190 | 0.0767 |

Each generation is one `--append-system-prompt` call with a single question, not
a multi-turn session, so this **overstates** what a real session pays once the
first turn's cache write becomes a cache read on every turn after it.

## Never-cut check

`report.py` gates on the never-cut contract and exits 1 against the committed
snapshot: 2 failures out of the 50 responses per arm that carry a keyword list
to verify by design. Both were read and confirmed. One `destructive` response
pointed at foreign keys generally rather than naming the two tables in the
fixture, and one `conditional` response stopped short of diagnosing the leak.

The difference from the previous run's 0 is not statistically distinguishable
(Fisher p = 0.50), and `terse-control` scores 1 on the same snapshot. The
threshold is unchanged from the run that passed it. Adding the three quality
cases did not change either failure — they carry no keyword list — but it did
drop the checked fraction from 63% of responses to 45%.

The `destructive` one turned out to be a rule defect: that response never opened
the schema it was pointed at, and the rule said "including exactly what will be
affected" without saying *from the material in front of you*. The bullet now
demands the read, and a re-run at n=5 on both models is clean at 10 of 10 —
[`evals/results/2026-07-31-destructive-recheck.md`](../evals/results/2026-07-31-destructive-recheck.md).
The committed snapshot above predates that change and was not regenerated, so
`report.py` still exits 1: `conditional` was left alone for want of a textual
argument.

## Scope

What the numbers cover:

- **The compression, readability, latency and cost figures are the load-bearing
  ones.** They come from deterministic offline scoring of the raw responses.
- **Only 3 of the 11 cases can be compared between arms.** Every case declares
  where its criteria came from in a `grading` field. Five grade the never-cut
  contract, which the treatment arm was instructed to follow and the controls
  were not; three grade adherence to laconic's own style prohibitions. Neither
  kind supports a comparison, and the trap table publishes the field as a column
  so a row cannot be read out of context.
- **The quality result rules out a large regression and nothing finer.** Power
  at n=30 per arm reaches 0.78 only by a drop to 65%. Two of the three cases are
  at ceiling.
- **The headline compression figure moved from 28% to 33% on Sonnet** when the
  case set grew from 8 to 11. Both are published; the added cases give 31% on
  their own.
- **Never-cut coverage is 50 of 110 responses per arm.** Six cases carry an
  empty keyword list and are not checked — three were emptied once an earlier
  `"if"` keyword turned out to match "different", "specify" and "identify", and
  the three quality cases turn on mechanisms with several correct phrasings, so
  any required substring would fail correct answers.
- **The snapshot is mixed for the original 8 cases.** Their laconic arm was
  regenerated on 2026-07-31 after the arrow fix while their controls were
  carried over from 2026-07-30, so treatment and control were not sampled at
  the same time. The 3 quality cases have all four arms generated together and
  do not inherit this.
- **n=5 per cell, two models, one vendor.** Differences smaller than the
  published stdev are treated as noise, and the results speak only to Claude
  models.
- **The judge is a Claude model grading Claude outputs,** blind to arm with the
  rules text withheld. It is not an independent evaluator, and the answer-quality
  claim is the one result that rests on it.
- **Every figure above is a `full`-level figure.** The three levels were
  measured against each other separately, one arm and 330 more calls, and the
  ladder the level text implies is not there. That run also found arrows at
  `lite` on Sonnet, which is why the readability row above carries a level
  qualifier.
- **No reader-preference claim is made anywhere.** The one run that asked a
  judge which answer served the reader better did not favour laconic and was
  not interpretable in either direction, because the judge's length bias and
  position bias both exceeded the difference between arms. Every claim above is
  a length, readability, latency or cost claim.
- **Compression is counted in output tokens, which include the model's tool
  turns.** Recomputing the same committed snapshot in words of the answer gives
  45% on Sonnet rather than 33%, and leaves the Haiku non-result's sign
  unchanged. The token figure is the conservative one and stays the headline.

Reproduce:

```bash
python3 evals/bench/run.py      # generate (~440 calls, 2-3 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```

The three-level run, and its offline report:

```bash
for L in lite full ultra; do
  python3 evals/bench/run.py --level "$L" --arms laconic \
    --snapshot "evals/snapshots/levels-$L.json"
done
python3 evals/bench/levels.py   # ladder verdicts, never-cut and readability per level
```
