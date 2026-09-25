# Benchmark

2,775 generations: 37 cases x 5 reps x 3 models (Haiku 4.5, Sonnet 5, Opus 5.5)
x 5 arms — baseline, a terse-only control, a synthetic word-compression foil,
Claude Code's built-in `Concise` output style, and laconic. All five arms and all
three models were generated in one interleaved batch on 2026-09-24 and
2026-09-25, at the `full` rules that ship in v0.3.3 (`rules_cksum` 288018845).
Scored offline on compression, readability, closing offers, latency and cost,
with a deterministic never-cut check, and every response graded blind by a
three-model judge panel (sonnet, opus and kimi, by majority).

Snapshot: `evals/snapshots/loop/benchmark-2026-09-24.json`, merged from eight
shards and judged into `evals/snapshots/loop/benchmark-2026-09-24-judgments.json`.
The previous publication, round 21 of 2026-08-22, is summarised under
[History](#round-21-the-previous-publication).

| vs baseline | tokens (haiku) | tokens (sonnet) | tokens (opus) | latency (sonnet) | latency (opus) | readability violations | closing offers | quality pass rate | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| **laconic** | -11% | **-60%** | **-44%** | **-46%** | **-46%** | **45** | **2** | 80.2% | 1 / 135 |
| concise-style | -14% | -47% | -28% | -41% | -18% | 180 | 43 | 77.5% | 2 / 135 |
| terse-control | **-17%** | -46% | -32% | -34% | -41% | 118 | 63 | 78.6% | 0 / 135 |
| word-compression | -14% | -26% | -28% | -34% | -32% | 536 | 60 | 78.4% | 2 / 135 |
| baseline | 0% | 0% | 0% | 0% | 0% | 196 | 61 | **81.2%** | 1 / 135 |

Tokens and latency are medians of per-case medians. Readability violations,
closing offers and never-cut failures are counts over each arm's 555 responses,
all three models pooled; the quality pass rate is over the 29 quality-graded
cases. Per-model breakdowns are in the sections below.

**Laconic is the shortest and fastest arm on Sonnet and Opus, and the cleanest
on every model.** It cuts Sonnet output 60% and Opus output 44%, against 47%
and 28% for Claude Code's own `Concise` style. It is the cheapest arm per call on
both. It carries 45 readability violations against baseline's 196, and makes 2
closing offers in 555 responses against baseline's 61.

**It does not improve answers, and on Sonnet it may cost some.** Pooled over
three models the quality pass rate is level with baseline, 80.2% against 81.2%.
On Sonnet alone it trails, 80.6% against 90.3% at z = -2.34, uncorrected for
the three models; see [Answer quality](#answer-quality).

**On Haiku it is not a compression plugin.** An 11% saving is smaller than what
"Answer concisely." buys, and laconic is longer than baseline on 11 of 37 cases.

## Provenance and confounds

**Every arm was generated in the same batch.** Round 21 carried its three
control arms from a run eleven days and eleven CLI patch releases older than
its laconic arm; this benchmark carries nothing. The five arms were interleaved
cell by cell, four `run.py` processes each owning one rep of every case (the
fifth rep split across the same four by case), declared as
`--concurrency 4` and recorded as such in the snapshot metadata.

**The batch spans one CLI release, and the arms are balanced across it.**
Generations ran on Claude Code 2.1.281 and 2.1.282; each run is stamped with its
version, and `python3 evals/bench/release.py` reports between 6.5% and 7.0% of
every arm on the older build, with no arm imbalanced across the boundary.

**The batch paused three times at the operator's usage limit** and resumed where it
stopped. A failed call is never recorded as a result, so the snapshot holds
2,775 successful generations and no excluded runs.

**Multi-turn cases were delivered as the plugin delivers them.** Ten of the 37
cases are conversations, and `--turn-delivery plugin` sends the laconic slice
once on turn 1 and the one-line reminder afterwards — the shipped hook wiring,
not a re-appended rule file.

**Every figure in this document describes the moment it was generated.** That is
not a formality. On 2026-09-01 a matched batch re-measured a *syntactic* metric —
preamble openings on `walkthrough`, no judge involved — against archive runs
carrying a byte-identical `rules_cksum` and the same level, and read **46.7%
across late August against 10.0% that day**, Fisher p = 1.0e-05, over five CLI
patch releases. Nothing about the plugin changed; the model did. See
[`round-37.md`](../evals/results/loop/round-37.md). Round 21's Sonnet baseline
had a median of 2,832 output tokens; this one has 1,270 on a newer Sonnet. A
figure quoted from this page needs its date read with it.

## Compression

Median output tokens, as the median of the 37 per-case medians, n = 5 per cell.

| arm | haiku | sonnet | opus |
|---|--:|--:|--:|
| baseline | 702 | 1270 | 2309 |
| terse-control | 580 | 682 | 1562 |
| word-compression | 607 | 944 | 1653 |
| concise-style | 605 | 673 | 1670 |
| **laconic** | 625 | **511** | **1294** |

The comparison that isolates the rule set from merely asking for brevity is
laconic against `terse-control`: 25% shorter on Sonnet and 17% on Opus, and 8%
*longer* on Haiku. The comparison that decides whether this plugin still has a
reason to exist is laconic against `concise-style`, and on the two larger models
laconic now wins it: shorter on 31 of 37 Sonnet cases and 35 of 37 Opus cases.
Round 21 found the reverse on Sonnet, 19 of 22 cases to `concise-style`.

Saving against baseline per case, laconic then `concise-style`; negative means
longer.

| case | grading | laconic haiku | laconic sonnet | laconic opus | concise-style haiku | concise-style sonnet | concise-style opus |
|---|---|--:|--:|--:|--:|--:|--:|
| `badnews` | safety | 1% | **33%** | **52%** | 4% | 24% | 35% |
| `code-fidelity` | safety | 2% | **64%** | 12% | 19% | 61% | 5% |
| `cold-service` | quality | **43%** | **47%** | **48%** | 29% | 54% | 27% |
| `conditional` | rule-adherence | 8% | **39%** | **49%** | 0% | 12% | 35% |
| `confirm-index` | quality | 7% | **53%** | **67%** | 12% | 27% | 3% |
| `confirm-metric` | quality | 20% | **47%** | **30%** | 20% | 27% | 21% |
| `confirm-rollback` | quality | -13% | **47%** | **33%** | 8% | 36% | 26% |
| `decision` | rule-adherence | 6% | **62%** | **67%** | 10% | 53% | 61% |
| `deep-index` | quality | **40%** | **43%** | **66%** | 14% | 35% | 12% |
| `deep-metric` | quality | **36%** | **69%** | **78%** | 33% | 39% | 33% |
| `deep-rollback` | quality | 24% | **46%** | **74%** | 10% | 25% | 11% |
| `design-alerting` | quality | 25% | **62%** | **67%** | 6% | 43% | 26% |
| `design-audit-log` | quality | **58%** | **59%** | **65%** | 43% | 30% | 25% |
| `design-cache` | quality | 3% | **31%** | **66%** | -5% | 72% | 45% |
| `design-rate-limit` | quality | 0% | **44%** | **77%** | 16% | 24% | 15% |
| `design-realtime` | quality | -17% | **72%** | **66%** | -8% | 81% | 37% |
| `design-retry` | quality | 29% | **58%** | **65%** | 38% | 65% | 32% |
| `design-search` | quality | -26% | **63%** | **64%** | 0% | 54% | 26% |
| `design-upload` | quality | 13% | **51%** | **54%** | 9% | 42% | 43% |
| `destructive` | safety | -7% | -27% | -20% | 6% | -32% | 29% |
| `drift-service` | quality | 19% | **82%** | **65%** | 8% | 39% | 24% |
| `fail-open` | quality | -19% | **57%** | **49%** | 1% | 54% | 39% |
| `floor` | rule-adherence | 17% | **74%** | **66%** | 34% | 67% | 62% |
| `ordered-steps` | safety | -2% | **74%** | **39%** | 11% | 59% | 17% |
| `quota-merge` | quality | -38% | **46%** | 27% | 0% | 48% | 21% |
| `recall-index` | quality | 13% | **89%** | **55%** | 18% | 45% | 21% |
| `recall-metric` | quality | 29% | **88%** | **61%** | -7% | 20% | 33% |
| `recall-rollback` | quality | 3% | **92%** | **69%** | 6% | 51% | 42% |
| `silent-success` | quality | 10% | **44%** | **48%** | 14% | 35% | 33% |
| `stale-cache` | quality | -3% | 23% | **44%** | -18% | 40% | 28% |
| `verdict-experiment` | quality | -13% | **73%** | **40%** | -5% | 69% | 40% |
| `verdict-rollout` | quality | -24% | **64%** | **50%** | -11% | 60% | 19% |
| `verdict-schema` | quality | 1% | **68%** | **57%** | 10% | 24% | 10% |
| `walkthrough` | safety | 4% | **63%** | **55%** | 18% | 58% | 19% |
| `wide-index` | quality | 20% | **89%** | **48%** | 3% | 56% | 17% |
| `wide-metric` | quality | 29% | **77%** | **60%** | 17% | 54% | 4% |
| `wide-rollback` | quality | 27% | **74%** | **55%** | 3% | 29% | 11% |

**Haiku is not a compression result.** The median saving is 11%, `terse-control`
saves more, and laconic is longer than baseline on 11 of 37 cases —
`quota-merge` worst at -38%.

**`destructive` is the one case laconic lengthens on every model**, by 7%, 27%
and 20%. It is a safety case: the response has to name both dependent tables
and the constraint behavior before anyone runs the drop, and the never-cut list
exists to protect exactly that content. Under the judge the extra length buys
nothing: every arm passes 5 of 5 on Opus and 0 of 5 on Haiku, and on Sonnet
laconic passes 2 against baseline's 3.

**These are marginal medians, over every answer whether or not it opened a
file.** Part of any gap between two arms can be one arm reading less rather than
writing less. Here the reading rates are too close to carry most of the
gap: counting responses that called no tool at all, laconic sits at 85 of 185
on Sonnet against baseline's 76 and `concise-style`'s 95, and at 64 of 185 on
Opus against 65 and 65. The rules loop's own token gate compares answers inside
one reading stratum instead
([stratified-tokens.md](../evals/results/loop/stratified-tokens.md)).

## Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | haiku | sonnet | opus | total | responses affected (of 555) |
|---|--:|--:|--:|--:|--:|
| baseline | 70 | 104 | 22 | 196 | 87 |
| terse-control | 24 | 79 | 15 | 118 | 64 |
| word-compression | 155 | 108 | 273 | 536 | 165 |
| concise-style | 64 | 104 | 12 | 180 | 76 |
| **laconic** | **21** | **22** | **2** | **45** | **26** |

Laconic is the cleanest arm on every model, and it is not clean: 26 of its 555
responses carry a violation, and `report.py` still exits 1 on this snapshot
because the gate allows none. On Opus it is 2 violations in 185 responses.
`word-compression` is the foil it was built to be, and on Opus it is worse than
any arm on any model.

### What readability does not say

The row above counts degraded grammar. It can show laconic making prose worse
and can never show it making prose better, so "shorter with grammar intact" is
where the deterministic evidence stops. The one run that asked a judge which of
two answers better serves the reader — 130 comparisons on 2026-08-01, against a
long-superseded arm — did not prefer laconic, and its own length and position
biases were larger than the gap between arms, so it supports no preference claim
in either direction:
[`evals/results/2026-08-01-preference.md`](../evals/results/2026-08-01-preference.md).

## Closing offers

`lite` prohibits closing offers and offers to do more work, and `full` inherits
the rule. Unlike compression this is **binary**: whether the answer offered to
go and do something is not a judgement two readers can disagree about, which is
the property [#113] asked for when it reported the rule breaking on one turn and
holding on the next.

Counted with `metrics.closing_offers()`:

| arm | haiku | sonnet | opus | total (of 555) | rate |
|---|--:|--:|--:|--:|--:|
| terse-control | 13 | 39 | 11 | 63 | 11.4% |
| baseline | 11 | 38 | 12 | 61 | 11.0% |
| word-compression | 7 | 42 | 11 | 60 | 10.8% |
| concise-style | 5 | 31 | 7 | 43 | 7.7% |
| **laconic** | **2** | **0** | **0** | **2** | **0.4%** |

**Being told to be brief does not suppress the shape; the rule does.** Two arms
instructed to compress sit at baseline's rate, and `concise-style` — which
installs a near-clause-for-clause restatement of laconic's own never-cut list —
removes about a third of it. Laconic removes all but two, both on Haiku. This
ordering has now held in every batch that measured it: round 21, the matched
batch of 2026-08-23, rounds 36 and 37, and this one.

### What this measurement does and does not support

**Precision was measured before the rate was used.** 30 hits drawn at random
from the archive and hand-read: 30 of 30 are genuine offers to do more work.
That is the bar the restatement metric of [#155] could not clear at 55.3%, and
the reason is that a closing offer is syntactically formulaic where a restated
claim is semantic.

The first version of the detector had **zero** precision. Keyed on `i can`,
`should i` and `if you want` it fired 13 times across 210 responses and every
one was a stated limitation ("the document gives no order counts, so I can't
quantify the impact") or a request for what was needed to answer at all. Both
are never-cut content. The rules also carve out confirmation explicitly, so
"DROP TABLE users CASCADE orphans every dependent row — should I proceed?" is
not a closing offer. All three shapes are regression tests in
`tests/test_metrics.py`.

**Recall was estimated from 40 hand-read negatives**, after widening the
pattern to three shapes it had missed. The rates are floors.

[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#155]: https://github.com/JordanMPDS/laconic/issues/155

## Answer quality

Every case declares in a `grading` field where its criteria came from, and that
field decides what the row supports. Only `quality` rows compare arms: their
criteria come from the fixture rather than from `rules/laconic.md`, so no arm
was instructed toward them. Verdicts are the panel's majority. A three-way split
is recorded as `not_exercised` and left out of the rate. So are the 14
judgments the panel could not finish: sonnet and opus disagreed on them, and
the third member's usage quota ran out before it could break the tie.

**Quality-graded cases (29 of 37).**

| arm | haiku | sonnet | opus | pooled |
|---|--:|--:|--:|--:|
| baseline | 101 / 138 | **130 / 144** | 115 / 144 | **81.2%** |
| **laconic** | **106 / 136** | 116 / 144 | **118 / 144** | 80.2% |
| terse-control | 97 / 138 | 123 / 143 | 114 / 144 | 78.6% |
| word-compression | 97 / 137 | 123 / 145 | 114 / 144 | 78.4% |
| concise-style | 93 / 138 | 122 / 145 | 116 / 144 | 77.5% |

**Pooled, no arm separates from any other.** Laconic against baseline is
z = -0.38, against `terse-control` +0.58 and against `concise-style` +0.95.
Round 21's strongest negative result — laconic 12 points behind a one-sentence
"Answer concisely.", z = -2.14 — did not reproduce.

**On Sonnet, laconic trails baseline: 80.6% against 90.3%, z = -2.34.** That is
one of three per-model comparisons and it is not corrected for the other two;
corrected it sits near p = 0.06. It is concentrated in four cases, `recall-index`
(0 fails against 4), `design-alerting` (2 against 5), `design-realtime` (1 against
4) and `quota-merge` (0 against 3). On Haiku and Opus laconic is level with or
ahead of baseline. This is the result on this page most worth a matched follow-up.

**Safety cases (5 of 37)** sit between 85.3% and 90.7% in every arm, all inside
noise. `destructive` separates the models rather than the arms: every arm passes
5 of 5 on Opus and 0 of 5 on Haiku.

**Rule-adherence cases (3 of 37)** grade laconic's own style prohibitions, so the
treatment arm is scored on what it was told to do and the controls were not.
Laconic passes 42.2% against baseline's 37.2%. The row hides one pattern worth
naming: on Opus laconic fails `conditional` 5 of 5 where baseline passes 5 of 5.
Each laconic response reads `db.js`, finds that `withClient` leaks on a throw, and
answers "No" to raising the pool outright; the case requires the advice to stay
conditional on whether the load is genuinely concurrent. Whether a condition the
code has already settled still needs stating is a question about the case as
much as about the rules.

## Cost, reported net

Median USD per call. The injected rules cost input tokens of their own, which
is why the Haiku column is flat: the output saving there is about what the rules
cost to send.

| median USD per call | haiku | sonnet | opus |
|---|--:|--:|--:|
| baseline | 0.0171 | 0.0668 | 0.1636 |
| terse-control | 0.0159 | 0.0494 | 0.1041 |
| word-compression | 0.0156 | 0.0542 | 0.1235 |
| concise-style | 0.0163 | 0.0490 | 0.1396 |
| **laconic** | 0.0159 | **0.0451** | **0.0993** |

Laconic is the cheapest arm per call on Sonnet and Opus. On Opus it costs 39%
less than baseline. Each single-turn generation is one call with a cold cache,
so this **overstates** what a real session pays once the first turn's cache
write becomes a cache read. The whole batch cost $415.80 to generate at API
prices, drawn from a Claude Code subscription.

## Multi-turn: what a session costs as it deepens

Most figures above are a question answered cold, and the ten conversation
cases in the benchmark mix depths rather than isolating them. A real session is
a sequence, and the rules reach a later turn differently: the plugin sends the full
text once at `SessionStart` and a one-line reminder afterwards. A separate batch
measured that directly, using two case families that share a fixture, a final
question and a trap byte for byte, and differ only in whether the question is
asked at turn 1 or turn 5.

Sonnet, 20 runs per arm per family, generated in one interleaved batch under the
shipped hook wiring:

| | median words | USD per call | seconds per run |
|---|--:|--:|--:|
| **turn 1** — baseline | 139.0 | 0.0415 | 8.1 |
| **turn 1** — laconic | 98.0 | 0.0439 | 7.0 |
| **turn 5** — baseline | 210.5 | 0.0427 | 121.3 |
| **turn 5** — laconic | **30.5** | **0.0241** | **20.0** |

**The arms move in opposite directions.** An unruled answer runs 51% longer at
turn 5 than at turn 1; laconic's runs 69% shorter. Every one of the six cells
agrees, two-sided exact sign test p = 0.0312, and the gap between the arms widens
from a median 39.5 words to 181 (p = 5e-06 on a permutation over the paired
cells).

**The rules cost you on the first turn and pay back at depth.** At turn 1 laconic
is marginally the more expensive arm per call, because the injected text is input
tokens — the same effect the Haiku column shows above. By turn 5 it is 44%
cheaper per call, and the whole five-turn conversation finishes in 20 seconds
against 121.

**The extra words buy nothing the judge can see.** Both arms were graded on the
identical final question at both depths and both read **120 of 120**. That
comparison sits at a ceiling: it rules out a laconic deficit of six failures in
thirty and cannot see a smaller one.

Read with the same limits as everything else here: sonnet only, one vendor, n=20
a side, and scored on words rather than `output_tokens`, because a single-turn
graded answer carries a tool-use block that a multi-turn one does not and the
token counts are not comparable across that boundary. Full write-ups in
[`round-42.md`](../evals/results/loop/round-42.md) and
[`round-43.md`](../evals/results/loop/round-43.md).

## Never-cut check

Checked on the 135 responses per arm, across all three models, that carry a
keyword list by design.

| arm | failures | what was dropped |
|---|--:|---|
| terse-control | 0 / 135 | — |
| baseline | 1 / 135 | `destructive`/haiku rep2 dropped `sessions` |
| **laconic** | **1 / 135** | `conditional`/haiku rep1 dropped `leak` |
| concise-style | 2 / 135 | `conditional`/sonnet rep0 dropped `leak`; `destructive`/haiku rep4 dropped `sessions` |
| word-compression | 2 / 135 | `conditional`/sonnet rep1 dropped `leak`; `deep-index`/sonnet rep0 dropped `date_trunc` |

**No arm separates from any other on this check.** One or two failures in 135
is noise at this sample size. The failures were read rather than counted, and
they are not all the same kind. Laconic's is genuine: the Haiku response calls
the `withClient` wrapper "correct" and never finds the leak. The two Sonnet
`conditional` failures fixed the leak in the file and answered "Fixed." without
saying what was fixed, so the content is in the diff rather than the answer.
The `deep-index` one names the wrapped predicate without the function it
wraps.

**Read the never-cut column as a floor.** The check is a deterministic substring
test: it confirms that the protected content is present and cannot see it
mischaracterised. On `destructive` a response can name the `sessions` table and
then tell the user it is safe, which passes this check and fails the judge. The
judge column in [Answer quality](#answer-quality) is the one that sees that.

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
plugin has. In round 21 it won on compression, -55% on Sonnet against laconic's
-32%. In this benchmark it loses on Sonnet and Opus, -47% against -60% and -28%
against -44%, and it is level on quality. On [closing offers](#closing-offers)
it sits at 43 in 555 against laconic's 2, despite installing a
near-clause-for-clause restatement of laconic's own never-cut list.

### What the style installs, and what it actually does

From the 2.1.240 bundle the style's own first line reads "Keep your responses
short and direct **while doing the work just as thoroughly**", and its rules 5
and 6 restate laconic's "length scales to the request" and its never-cut list
nearly clause for clause. The instruction not to trade thoroughness for brevity
is present and explicit.

**It did not hold, when last measured.** A matched interleaved batch on 2026-08-23 — all five arms
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

- **The compression, readability, closing-offer, latency and cost figures are
  the load-bearing ones.** They come from deterministic offline scoring of raw
  response text and depend on no judge.
- **29 of 37 cases can be compared between arms on quality.** Five grade the
  never-cut contract, which the treatment arm was instructed to follow and the
  controls were not; three grade adherence to laconic's own style prohibitions.
  Neither kind supports an arm comparison.
- **The judge is a panel of language models grading language-model output,**
  blind to arm with the rules text withheld. Two of its three members are Claude
  models grading Claude outputs. It is not an independent evaluator, and the
  quality claims are the ones that rest on it.
- **Never-cut coverage is 135 of 555 responses per arm.** Cases with an empty
  keyword list are not checked, and the check cannot see mischaracterisation.
- **n = 5 per cell, three models, one vendor.** Differences smaller than a cell's
  spread across reps are treated as noise, and the results speak only to Claude
  models.
- **27 of the 37 cases are a single question asked cold.** Ten are
  conversations of two to five turns, delivered as the plugin delivers them. The
  separate depth batch in [Multi-turn](#multi-turn-what-a-session-costs-as-it-deepens)
  is the one that isolates what depth does.
- **Every figure is a `full`-level figure.** The three levels were measured
  against each other separately and the ladder the level text implies is not
  there: [`evals/results/2026-07-31-levels.md`](../evals/results/2026-07-31-levels.md).
- **No reader-preference claim is made anywhere.**

## History

The sections below describe **superseded tables**. They are kept because each
records a correction made against the plugin, and the reasoning still applies to
how this benchmark is read. The figures in them are not the figures above.

### Round 21, the previous publication

`evals/snapshots/loop/round-21.json`, judged into
`evals/snapshots/loop/round-21-judgments.json`: 1,100 calls, 22 cases x 5 reps x
2 models (Haiku and Sonnet) x 5 arms, at `rules_cksum` 1830906901, six
accepted rule edits before what ships now. The three control arms were carried
from 2026-08-11 on CLI 2.1.227, `concise-style` was generated 2026-08-21 on
2.1.238 and laconic 2026-08-22 on 2.1.239.

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | quality pass rate | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| laconic | -32% | -9% | -32% | 66 | 59.7% | 0 / 50 |
| concise-style | -55% | -12% | -52% | 113 | 58.4% | 3 / 50 |
| terse-control | -3% | -2% | 0% | 107 | 71.9% | 1 / 50 |
| word-compression | +7% | +5% | +6% | 176 | 70.3% | 1 / 50 |
| baseline | 0% | 0% | 0% | 134 | 68.1% | 0 / 50 |

What it found, and what this benchmark did to each finding:

- **`concise-style` compressed harder than laconic on Sonnet, -55% against
  -32%.** Reversed: -47% against -60% here. A
  matched batch on 2026-08-23 had already found that roughly three fifths of
  `concise-style`'s round-21 advantage was not opening files rather than
  tighter prose; see [The concise-style arm](#the-concise-style-arm).
- **Laconic trailed a one-sentence "Answer concisely." on quality, 59.7%
  against 71.9%, z = -2.14.** Did not
  reproduce: pooled here it is 80.2% against 78.6%, z = +0.58.
- **Laconic was the cleanest arm on readability and on closing offers.** Held,
  with a wider margin on both.
- **Laconic's clean never-cut sheet on `destructive` sat beside 2 of 10 judge
  passes,** because the substring check confirms `sessions` is named and cannot
  see a response that then calls the table safe. The same limit applies to the
  never-cut column above.
- **Its three `concise-style` never-cut failures did not survive replication.**
  Re-measured on 2026-08-24 at n = 20 a side on Haiku, `concise-style` and
  laconic were level at 4 of 40 each, and laconic's 0 in round 21 had been a
  five-rep draw (`evals/snapshots/loop/never-cut-concise.json`).

### The 2026-08-04 regeneration

The laconic arm in that superseded table was generated on 2026-08-03 under
`rules_cksum` 1830906901 — the same revision as round 21's table. Before it, the
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

**This is a `full`-level result.** The three-level snapshots checksum to
`lite` 1146585023, `full` 1830906901 and `ultra` 823082683. None of the three
is what ships any more; the shipped `full` slice is 288018845. The design-question licence and the asking-permission edit
landed in the `Level: full` section, which the `lite` slice does not carry;
round 55's pre-action check landed in the shared opening checks, which all
three carry, which is why `lite` moved too. Across it,
laconic's arrow violations are 25 at `lite`, 23 at `full` and 16 at `ultra` —
no level is clean, and the gap between levels is smaller than the earlier
"12 at `lite` against 0 at `full`" suggested. See
[`evals/results/2026-07-31-levels.md`](../evals/results/2026-07-31-levels.md).

Reproduce:

```bash
python3 evals/bench/run.py \
  --arms baseline,terse-control,word-compression,concise-style,laconic \
  --turn-delivery plugin      # 2,775 cells over today's 37 cases and three models
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```

This page's benchmark ran as four shards of that command, one rep of every case
each (`--reps 1 --rep-offset K --concurrency 4`), merged with
`python3 evals/bench/merge.py` and judged with `judge.py --judge-all`. Read the
cost line `run.py` prints before it makes a call.

The three-level run, and its offline report:

```bash
for L in lite full ultra; do
  python3 evals/bench/run.py --level "$L" --arms laconic \
    --snapshot "evals/snapshots/levels-$L.json"
done
python3 evals/bench/levels.py   # ladder verdicts, never-cut and readability per level
```

`levels.py` exits non-zero when the cross-level run is incomplete - a level with
no usable snapshot, or a model with no usable run at one of them - and zero
otherwise. The length ladder verdict (`monotonic`, `flat`, `broken`) never
decides the exit code: it reports what a generation run measured, and on the
committed snapshots it reads `broken` for both models. What is gated instead is
decision monotonicity, which is a property of the code rather than of a run:
`metrics.decisions(text, level)` returns the findings in force at one level, and
`tests/test_metrics.py` and `tests/test_bench.py` assert that those sets nest
across `lite`, `full` and `ultra`.
