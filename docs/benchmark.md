# Benchmark

1100 API calls: 22 cases x 5 reps x 2 models x 5 arms — baseline, a terse-only
control, a synthetic word-compression foil, Claude Code's built-in `Concise`
output style, and laconic. Scored offline on compression, readability, latency
and cost, with a deterministic never-cut check and a blind judge for the trap
criteria.

Snapshot: `evals/snapshots/loop/round-21.json`, judged into
`evals/snapshots/loop/round-21-judgments.json`. The laconic arm is `rules_cksum`
1830906901, the rules this repository ships.

**This table covers all 22 cases.** Earlier publications of this page measured
only the eleven original ones and said they would refresh at the next full
benchmark publish. This is that publish.

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | quality pass rate | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| **laconic** | -32% | -9% | -32% | **66** | 59.7% | 0 / 50 † |
| concise-style | **-55%** | **-12%** | **-52%** | 113 | 58.4% | 3 / 50 † |
| terse-control | -3% | -2% | 0% | 107 | **71.9%** | 1 / 50 |
| word-compression | +7% | +5% | +6% | 176 | 70.3% | 1 / 50 |
| baseline | 0% | 0% | 0% | 134 | 68.1% | 0 / 50 |

Every column is reported as measured, on both models and all five arms. Three
readings of it are load-bearing, and two of them are against the plugin.

† **Do not read the never-cut column as a gap between laconic and
`concise-style`.** Both figures are five-rep draws, and re-measuring the only
two cells they differ on at n = 20 a side puts the two arms level at 4 of 40
each — see [Compression](#compression) below.

**Laconic is the cleanest arm on prose and the cheapest on Sonnet.** 66
readability violations against baseline's 134, 31 of 220 responses carrying one
against baseline's 49, and $0.0636 per call against baseline's $0.1099 — while
not being the shortest arm. It also leads rule-adherence at 63.3% against
baseline's 43.3%.

**Laconic does not win answer quality.** 59.7% against baseline's 68.1% is
z = -1.45, short of significance: not a demonstrated regression, and not a win.
Against `terse-control`'s 71.9% the 12.2-point gap is z = -2.14 and does clear
it. A plain "Answer concisely." instruction produced better answers on the
quality-graded cases than the whole rule file did, and that is the single
strongest negative result this benchmark has produced.

**Claude Code now ships a competitor that compresses harder, and most of that
compression is not writing.** The built-in `Concise` output style cuts Sonnet
output 55% against laconic's 32% at half the latency, and is indistinguishable
from laconic on quality here (58.4% against 59.7%, z = +0.22). A matched
interleaved batch run on 2026-08-23 decomposed that advantage and it does not
mean what this table implies: roughly **three fifths of `concise-style`'s
compression comes from not opening files**, not from tighter prose. See
[The concise-style arm](#the-concise-style-arm), which now carries the matched
measurement, and read it before quoting the -55% figure.

## Provenance and confounds

The three control arms are carried unchanged from `round-20.json`, generated
2026-08-11 on CLI 2.1.227. `concise-style` was generated 2026-08-21 on 2.1.238
and `laconic` on 2026-08-22 on 2.1.239. All five ran against identical case
material (`cases_cksum` 2389944869).

That makes two comparisons of unequal strength, and they should not be quoted
interchangeably:

- **laconic against `concise-style` is the stronger of the two.** Same cases,
  same rules checksum, one patch release apart, one day apart. It is still not
  a matched comparison; the matched one is linked below and disagrees on what
  the compression gap consists of.
- **Anything against baseline carries eleven days and eleven patch releases**
  of possible model and harness drift, landing entirely on the treatment arms.

**The argument that used to justify carrying controls has been retired.** It
read: no control takes rules in its system prompt, so a rule change cannot move
one. The premise is true and the conclusion does not follow. Regenerated on
2026-08-22 alongside its treatment, `terse-control`'s one-turn rate went **4 of
40 to 11 of 40** with nothing changed but the calendar and the CLI. A control
arm cannot move *because of an edit*, but it moves a great deal on its own, and
conflating those two claims is what produced every arm comparison in this table
being against runs from another era. See
[`interleaved-batch.md`](../evals/results/loop/interleaved-batch.md).

The control verdicts were likewise carried rather than re-judged, at a verified
matching criteria checksum (997100469). Only `concise-style` and `laconic` were
graded in this round's 440 judge calls.

## Compression

Median output tokens per case, n=5 per cell, medians of per-case medians in the
final row. The comparison that isolates the rule set from merely asking for
brevity is laconic against `terse-control`; the comparison that matters for
whether this plugin still has a reason to exist is laconic against
`concise-style`.

**Sonnet 4.5**

| case | baseline | terse-control | concise-style | laconic | laconic saved |
|---|--:|--:|--:|--:|--:|
| `decision` | 839 | 786 | 185 | 236 | **72%** |
| `floor` | 201 | 220 | 69 | 69 | **66%** |
| `destructive` | 2336 | 2775 | 1488 | 810 | **65%** |
| `silent-success` | 1105 | 947 | 467 | 475 | **57%** |
| `design-cache` | 5395 | 4990 | 1167 | 2423 | **55%** |
| `design-realtime` | 3327 | 3279 | 1134 | 1716 | **48%** |
| `walkthrough` | 3701 | 3682 | 1471 | 2376 | **36%** |
| `code-fidelity` | 307 | 315 | 128 | 198 | **36%** |
| `ordered-steps` | 1329 | 1630 | 555 | 882 | **34%** |
| `fail-open` | 1265 | 1234 | 588 | 888 | **30%** |
| `conditional` | 908 | 981 | 671 | 644 | **29%** |
| `verdict-rollout` | 3478 | 2950 | 1532 | 2470 | **29%** |
| `design-upload` | 4943 | 3838 | 1469 | 3609 | **27%** |
| `design-alerting` | 5444 | 5425 | 3366 | 4364 | **20%** |
| `design-audit-log` | 6255 | 5950 | 3837 | 5167 | **17%** |
| `design-rate-limit` | 4155 | 4394 | 2767 | 3440 | **17%** |
| `verdict-schema` | 3419 | 2938 | 1752 | 2834 | **17%** |
| `design-search` | 2255 | 1929 | 1377 | 2013 | 11% |
| `design-retry` | 4559 | 4438 | 1652 | 4421 | 3% |
| `verdict-experiment` | 3856 | 2718 | 2001 | 3887 | -1% |
| `badnews` | 435 | 414 | 369 | 461 | -6% |
| `stale-cache` | 1660 | 2245 | 1129 | 1842 | -11% |
| **median** | **2832** | **2746** | **1272** | **1928** | **32%** |

**Haiku 4.5**

| case | baseline | terse-control | concise-style | laconic | laconic saved |
|---|--:|--:|--:|--:|--:|
| `design-realtime` | 635 | 544 | 546 | 502 | **21%** |
| `design-retry` | 805 | 747 | 556 | 655 | **19%** |
| `code-fidelity` | 425 | 421 | 383 | 358 | **16%** |
| `verdict-rollout` | 1671 | 1573 | 1280 | 1426 | 15% |
| `conditional` | 956 | 1017 | 925 | 838 | 12% |
| `badnews` | 469 | 432 | 398 | 413 | 12% |
| `silent-success` | 775 | 732 | 620 | 684 | 12% |
| `ordered-steps` | 653 | 636 | 640 | 578 | 11% |
| `design-search` | 596 | 687 | 544 | 528 | 11% |
| `destructive` | 711 | 791 | 644 | 659 | 7% |
| `design-cache` | 730 | 652 | 790 | 697 | 5% |
| `floor` | 266 | 236 | 242 | 255 | 4% |
| `walkthrough` | 1228 | 1008 | 1067 | 1201 | 2% |
| `fail-open` | 922 | 843 | 782 | 931 | -1% |
| `design-rate-limit` | 657 | 673 | 604 | 683 | -4% |
| `decision` | 522 | 506 | 469 | 547 | -5% |
| `verdict-experiment` | 1473 | 1504 | 1545 | 1591 | -8% |
| `design-alerting` | 941 | 888 | 1013 | 1070 | -14% |
| `verdict-schema` | 1290 | 1263 | 1055 | 1543 | -20% |
| `design-upload` | 556 | 571 | 684 | 691 | -24% |
| `stale-cache` | 1246 | 1355 | 1326 | 1587 | -27% |
| `design-audit-log` | 787 | 1105 | 810 | 1463 | -86% |
| **median** | **752** | **740** | **664** | **688** | **9%** |

Sonnet is where the compression claim lives, and the case spread is wide: seven
cases save 30% or more, and three come out longer than baseline. On Haiku the
median saving is 9% and eight of the 22 cases are negative, `design-audit-log`
worst at -86%. A 9% median with that spread is not a compression result worth
quoting on its own.

`concise-style` is shorter than laconic on 19 of 22 Sonnet cases and 16 of 22
on Haiku, several by large margins — `design-retry` at 1652 tokens against
laconic's 4421, `design-upload` at 1469 against 3609. Laconic is shorter on
exactly two Sonnet cases: `destructive` (810 against 1488) and `conditional`
(644 against 671), the two cases that carry never-cut keyword lists.

**That was published as laconic spending its tokens on the protected content,
and the reading does not survive measurement.** Round 21's three
`concise-style` never-cut failures were all on Haiku and all in two cells:
`conditional` 1 of 5, and `destructive` 2 of 5. Those two cells were
re-measured on 2026-08-24 in one matched interleaved batch — `baseline`,
`concise-style` and `laconic`, Haiku, n = 20 a side, 120 generations, one CLI
build (2.1.240), no carried arms — in
`evals/snapshots/loop/never-cut-concise.json`:

| arm | never-cut failures | `conditional` | `destructive` | judge pass, `conditional` | judge pass, `destructive` |
|---|--:|--:|--:|--:|--:|
| `baseline` | 0 / 40 | 0 / 20 | 0 / 20 | 14 / 20 | 0 / 20 |
| `concise-style` | 4 / 40 | 2 / 20 | 2 / 20 | 11 / 20 | 0 / 20 |
| **`laconic`** | 4 / 40 | 0 / 20 | 4 / 20 | 9 / 20 | 0 / 20 |

**The two compression arms are level on the substring check**, 4 of 40 each,
Fisher p = 1.0. On `destructive` laconic fails more often, 4 of 20 against
2 of 20 at p = 0.66, and 4 in 20 is what laconic's own measured rate for that
cell — 5 in 65 — predicts. Laconic's 0 in round 21 was a five-rep draw rather
than a clean sheet.

Both failure sets were read rather than counted. All six `destructive` failures
name `invoices` as the only obstacle and never mention `sessions`, which is that
case's documented fail condition, so they are real failures. The two
`conditional` failures are substring artifacts: both responses diagnose the leak
correctly, `try`/`finally` fix included, and simply never use the word.

**Under the blind judge, `destructive` on Haiku separates nothing at all** —
every arm fails 20 of 20. Whatever that cell measures on Sonnet, at this sample
size on Haiku it has no opinion, which is worth knowing before a round is scoped
on it. `conditional` grades adherence to laconic's own rules and so supports no
arm comparison in either direction; its column is here for completeness, and
laconic is the lowest arm in it.

The one contrast the batch did produce is not between the compression arms:
`baseline` failed 0 of 40 where the two of them together failed 8 of 80,
p = 0.0508. Any compression instruction may cost never-cut fidelity. That is
suggestive, it is not established, and the batch was not scoped to test it.

On Sonnet laconic's stdev is 480.5 against baseline's 447.8 and
`concise-style`'s 246.9. The native style is both shorter and more consistent.

## Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | violations (haiku) | violations (sonnet) | total | responses affected (of 220) |
|---|--:|--:|--:|--:|
| baseline | 61 | 73 | 134 | 49 |
| terse-control | 36 | 71 | 107 | 42 |
| word-compression | 103 | 73 | 176 | 64 |
| concise-style | 48 | 65 | 113 | 49 |
| **laconic** | **25** | **41** | **66** | **31** |

Laconic is the cleanest arm on both totals and the share of responses carrying a
violation, and it is not clean. **`report.py` exits 1 on this snapshot: 18
case/model gates fail, because the gate allows no violations at all.** The
samples are dominated by arrows, and they concentrate in the design cases the
suite gained after the rules were last revised:

| cell | violations |
|---|--:|
| `design-retry`/sonnet | 13 |
| `design-upload`/haiku | 6 |
| `design-upload`/sonnet | 6 |
| `ordered-steps`/sonnet | 6 |
| `design-rate-limit`/haiku | 4 |
| `walkthrough`/haiku | 4 |
| `design-realtime`/sonnet | 4 |

The arm that ships the no-arrows rule is breaking it on the cases where an
answer has stages to describe. `design-retry`/sonnet runs a median of 3
violations per response.

### What readability does not say

The row above counts degraded grammar. It can show laconic making prose worse
and can never show it making prose better, so "shorter with grammar intact" is
where the deterministic evidence stops.

A blind judge was then asked the other question — which of two answers better
serves the reader — over 130 comparisons of responses the archived snapshot
held, and it has not been re-run against the regenerated arm. **It did not
prefer laconic.** Against baseline: laconic 37, baseline 52,
21 ties, p = 0.137. The same judge picked the longer answer 63% of the time
(p = 0.019) and reversed its verdict on 35% of comparisons it saw twice, both
effects larger than the gap between arms, so the run supports no preference
claim in either direction. Reported in full, including the comparison withheld
for a 50% flip rate:
[`evals/results/2026-08-01-preference.md`](../evals/results/2026-08-01-preference.md).

## Answer quality

Every case declares in a `grading` field where its criteria came from, and that
field decides what the row supports. Only `quality` rows compare arms: their
criteria come from the fixture rather than from `rules/laconic.md`, so no arm
was instructed toward them.

**Quality-graded cases (14 of 22).**

| arm | pass | fail | pass rate |
|---|--:|--:|--:|
| terse-control | 100 | 39 | **71.9%** |
| word-compression | 97 | 41 | 70.3% |
| baseline | 92 | 43 | 68.1% |
| **laconic** | **83** | **56** | **59.7%** |
| concise-style | 80 | 57 | 58.4% |

Two-proportion tests against laconic: baseline z = -1.45 (not significant),
`terse-control` z = -2.14 (significant at p < 0.05), `concise-style` z = +0.22
(noise). The honest summary is that laconic sits at the bottom of this column
with the native output style, that the gap to baseline is not established, and
that the gap to a one-sentence terseness instruction is.

**Rule-adherence cases (3 of 22)** grade laconic's own style prohibitions, so
the treatment arm is being scored on what it was told to do and the controls
were not. The row is reported because it is what the rules move, not as an
arm comparison:

| arm | pass rate |
|---|--:|
| **laconic** | **63.3%** |
| concise-style | 60.0% |
| terse-control | 53.3% |
| word-compression | 53.3% |
| baseline | 43.3% |

**Safety cases (5 of 22)** are flat across every arm — 84% to 88%, all inside
noise. The one row worth reading individually is `destructive`, below.

## Cost, reported net

Median USD per call. The injected rules cost input tokens of their own, so on
Haiku laconic is the most expensive arm despite emitting fewer output tokens.
On Sonnet the output saving more than pays for them.

| median USD per call | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0145 | 0.1099 |
| terse-control | 0.0158 | 0.1022 |
| word-compression | 0.0168 | 0.1099 |
| concise-style | 0.0174 | 0.0744 |
| **laconic** | 0.0197 | **0.0636** |

Laconic is the cheapest arm per call on Sonnet, below `concise-style`, despite
emitting 52% more output tokens than it. Each generation is one call with a
single question rather than a multi-turn session, so this **overstates** what a
real session pays once the first turn's cache write becomes a cache read.

## Never-cut check

Checked on the 50 responses per arm that carry a keyword list by design.

| arm | failures | what was dropped |
|---|--:|---|
| **laconic** | **0 / 50** | — |
| baseline | 0 / 50 | — |
| terse-control | 1 / 50 | `conditional`/sonnet rep3 dropped `leak` |
| word-compression | 1 / 50 | `destructive`/haiku rep1 dropped `sessions` |
| concise-style | 3 / 50 | `conditional`/haiku rep0 dropped `leak`; `destructive`/haiku reps 0 and 3 dropped `sessions` |

**Every cell in this table is a five-rep draw, and the laconic-versus-
`concise-style` gap in it did not survive replication.** Both of
`concise-style`'s cells were re-run at n = 20 a side against laconic and
baseline in one matched batch, and the two compression arms came out level at
4 of 40 each while laconic went from 0 to 4 of 20 on `destructive`. The table
and the reading are in [Compression](#compression).

**This column contradicts the judge, and the judge is the one to believe.** On
`destructive`, laconic has a clean never-cut sheet and passes **2 of 10** under
the blind judge, against baseline's 4 and `concise-style`'s 4. Both numbers are
correct and the gap between them is the finding.

The never-cut check is a deterministic substring test. It confirms that the
response contains `sessions`, which laconic always does. The judge additionally
applies the criterion added in
[#18](https://github.com/JordanMPDS/laconic/issues/18), which fails a response
that names the affected table and then characterises it as safe — because
`rules/laconic.md` requires naming exactly what will be affected, and a response
reporting that an affected table is fine has told the user the opposite of what
is true for their data. Laconic is producing that shape.

Read the never-cut column as a floor: it rules out the content being absent. It
does not establish that the safety contract holds, and on the one case where
both instruments have an opinion, they disagree.

## The concise-style arm

`concise-style` measures the `Concise` output style built into Claude Code
2.1.x, and it is delivered differently from every other arm. An output style
**replaces** part of the default system prompt rather than appending to it, so
`--append-system-prompt` cannot reproduce one and a hand-transcribed copy of the
style text would be a different treatment wearing the same label. The arm
therefore carries no system prompt and is passed to the CLI through
`--settings '{"outputStyle":"Concise"}'`, so what is measured is what Claude
Code actually ships.

An unrecognised style name is silently ignored: the CLI exits 0 and runs with
the default system prompt, which would make this arm a second copy of baseline
wearing a different name. `run.py` guards against that with a live preflight
probe before any generation call, and refuses to start the round if the style is
not reaching the model.

This arm exists because it is the closest thing to a native competitor this
plugin has, and the result is that on compression it wins.

### What the style installs, and what it actually does

From the 2.1.240 bundle the style's own first line reads "Keep your responses
short and direct **while doing the work just as thoroughly**", and its rules 5
and 6 restate laconic's "length scales to the request" and its never-cut list
nearly clause for clause. The instruction not to trade thoroughness for brevity
is present and explicit.

**It does not hold.** A matched interleaved batch on 2026-08-23 — all five arms
generated in one alternating pass on one CLI, `design-cache`, `design-realtime`
and `design-upload`, sonnet, n=10, 30 matched cells an arm — measured how often
each arm opened a file at all:

| arm | read the repository | median tokens |
|---|--:|--:|
| `baseline` | 26/30 | 3834 |
| `terse-control` | 22/30 | 2912 |
| `word-compression` | 20/30 | 2879 |
| `laconic` | 18/30 | 3415 |
| `concise-style` | **7/30** | 1542 |

`concise-style` against `baseline` is Fisher **p = 1.3e-06**; laconic against
`baseline` is **p = 0.0391**. Both arms suppress investigation; the native style
suppresses far more.

Holding every arm at `baseline`'s 87% reading rate decomposes the compression:

| arm | actual | at baseline's reading rate | share that is mix-shift |
|---|--:|--:|--:|
| `terse-control` | -24% | -19% | 19% |
| `word-compression` | -25% | -18% | 27% |
| `concise-style` | **-60%** | **-32%** | **46%** |
| `laconic` | -11% | **+2%** | **116%** |

Two readings, and both are uncomfortable. **`concise-style`'s headline
advantage is roughly three fifths a reading effect.** And **laconic does not
compress grounded design answers at all** — held at baseline's reading rate it
is 2% *longer* than baseline, so its entire measured token effect on these
cases is the same mix-shift, in a smaller dose.

The style writes well when it reads. Counting inline code spans as a grounding
proxy, `concise-style` answers that read the repository cite a median 19.5
identifiers against `baseline`'s 19 while writing 22% shorter. Its unread
answers cite 2. The defect is in how often it looks, not in what it produces
once it has looked.

**Why that matters for the quality column.** In the same batch, pooled over all
five arms' 150 verdicts, answers that read the repository failed quality **4 of
93**; answers that did not failed **55 of 57**. Fisher **p = 1.5e-33**.
Conditional on reading, laconic failed 0 of 18 and `concise-style` 0 of 7 — the
compression style has no measurable effect on quality at all, and the arms'
quality ranking is their reading-rate ranking inverted. On design questions the
only axis that separates these arms is how often they open a file.

Full working: [`round-23.md`](../evals/results/loop/round-23.md).

## Scope

What the numbers cover:

- **The compression, readability, latency and cost figures are the
  load-bearing ones.** They come from deterministic offline scoring of raw
  response text and depend on no judge.
- **14 of 22 cases can be compared between arms.** Five grade the never-cut
  contract, which the treatment arm was instructed to follow and the controls
  were not; three grade adherence to laconic's own style prohibitions. Neither
  kind supports an arm comparison, and the trap table publishes `grading` as a
  column so a row cannot be read out of context.
- **The quality column now says something it did not before.** At 14 cases it
  is no longer a single hard case carrying the whole column, and what it shows
  is laconic at the bottom rather than the top.
- **The headline Sonnet compression figure has been 28%, 33%, 38% and now
  32%.** The movements track changes in the case set and in which snapshot was
  drawn, not measured improvements over one another. This one covers twice as
  many cases as the 38% did.
- **Never-cut coverage is 50 of 220 responses per arm.** Cases with an empty
  keyword list are not checked, and the check cannot see mischaracterisation —
  see the contradiction documented above.
- **The snapshot is mixed.** Controls carried from 2026-08-11, `concise-style`
  from 2026-08-21, `laconic` from 2026-08-22, on three CLI versions. See
  [Provenance and confounds](#provenance-and-confounds).
- **n=5 per cell, two models, one vendor.** Differences smaller than the
  published stdev are treated as noise, and the results speak only to Claude
  models.
- **The judge is a Claude model grading Claude outputs,** blind to arm with the
  rules text withheld. It is not an independent evaluator, and the quality and
  trap claims are the ones that rest on it.
- **Every figure above is a `full`-level figure.** The three levels were
  measured against each other separately and the ladder the level text implies
  is not there:
  [`evals/results/2026-07-31-levels.md`](../evals/results/2026-07-31-levels.md).
- **No reader-preference claim is made anywhere.** The one run that asked a
  judge which answer served the reader better did not favour laconic and was not
  interpretable in either direction.

## History

The sections below describe **superseded tables** — the eleven-case, four-arm
publication that this page replaced. They are kept because each records a
correction made against the plugin, and the reasoning still applies to how this
benchmark is read. The figures in them are not the figures above.

### The 2026-08-04 regeneration

The laconic arm in that superseded table was generated on 2026-08-03 under
`rules_cksum` 1830906901, still the rules this repository ships. Before it, the
published table scored text generated on 2026-07-30, under rules two revisions
old — so the readability gate was judging prose that no rule change could reach.
Regenerating fixed that and nothing else about the gate: it still exits 1, on the
same six cells, for the same reason.

Every laconic column moved, and every one moved in laconic's favour. That warrants
stating plainly which movements mean anything:

| column | archived | current | attributable? |
|---|--:|--:|---|
| readability violations | 35 | 26 | partly — the arrow revisions target exactly this |
| tokens (sonnet) | -33% | -38% | no — one sample against another, n=5 per cell |
| answers correct | 27 / 30 | *not comparable* | the criteria changed between them — see below |
| never-cut failures | 4 / 50 | 1 / 50 | no — 4 in 50 against 1 in 50, Fisher p = 0.36 |

The answer-quality row can no longer be compared at all, and that is a stronger
statement than the hedge it replaces. The archived arm was graded under
`stale-cache`'s old criterion; the current arm is graded under the corrected
one. Putting 27 next to 23 would be two different instruments in one row. The
archived snapshot was not re-judged — 40 judge calls to restate a comparison
whose conclusion ("read none of this as an improvement") the correction only
strengthens.

The never-cut row **was** recounted on both snapshots, because that check is a
deterministic substring test rather than a judge call, so applying
`destructive`'s corrected keyword list to the archive costs nothing. It read
2 / 50 against 0 / 50 before; with `sessions` in the list it reads 4 / 50
against 1 / 50. The gap widens in laconic's favour and stays inside sampling at
p = 0.36, which is the same conclusion the smaller numbers supported.

That conclusion held on its own evidence before the correction, and still does.
The controls' responses are byte-identical between the two snapshots — they were
carried, not regenerated — yet re-judging moved word-compression by a response
on that same unchanged text. A column where the control drifts on identical
input cannot support a one-arm claim.

What the regeneration does establish is narrower and worth more than the table:
the gate now measures the rules in the repository. It failed before and it fails
now.

### The 2026-08-03 correction

This section describes the archived snapshot,
`evals/snapshots/results-2026-07-31.json`, and the figures in it are that
snapshot's.

The readability row read baseline 1, terse-control 9, word-compression 11 and
laconic **0** until the detector was corrected. Recounted from the archived
snapshot it reads 60 / 50 / 60 / 35. `_symbol_hits` skipped every
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
violations and the share of responses carrying one — 7 of 110 in the archived
snapshot against baseline's 16, and 9 of 110 in the current one. What does not:
the headline **0**. Laconic breaks its own no-arrows rule in both snapshots, and
the earlier claim that a rule revision had driven arrow violations to zero was an
artifact of where the detector was looking.

The correction was found by the rules loop, which scored an edit at 7 → 0 on
this metric while the model went on writing the same chains one list marker to
the left: [`evals/results/loop/round-01.md`](../evals/results/loop/round-01.md).

A numeric progression like `7 -> 11 -> 14` is still exempt. It quotes a series
rather than standing in for a conjunction.

**This is a `full`-level result.** The three-level snapshots checksum to the
rules this repository ships today (`lite` 1146585023, `full` 1830906901, `ultra`
823082683), so that run did not go stale with this regeneration. Across it,
laconic's arrow violations are 25 at `lite`, 23 at `full` and 16 at `ultra` —
no level is clean, and the gap between levels is smaller than the earlier
"12 at `lite` against 0 at `full`" suggested. See
[`evals/results/2026-07-31-levels.md`](../evals/results/2026-07-31-levels.md).

Reproduce:

```bash
python3 evals/bench/run.py      # generate (~1100 calls)
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
