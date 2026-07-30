# Benchmark results — 2026-07-30

## Run configuration

| | |
| --- | --- |
| Level | `full` |
| Reps | 5 |
| Models | haiku, sonnet |
| Cases | 8 |
| Arms | 4 (`baseline`, `terse-control`, `word-compression`, `laconic`) |
| Generations | 320 |
| Failed generations | 0 |
| Total generation cost | $13.73 |
| Rules checksum | 866559850 |
| Claude CLI | 2.1.220 |
| Generated | 2026-07-30 |

Snapshots: `evals/snapshots/results.json` (320 generations), `evals/snapshots/judgments.json`
(320 judgments). Both committed; every table below regenerates from them offline with
`python3 evals/bench/report.py --no-gate` — no network, no third-party packages.

## Headline: mixed results

**Compression is real on Sonnet and does not exist on Haiku.** Median output tokens —
sonnet: baseline 874, terse-control 884, word-compression 812, laconic 740. Laconic is
**15% shorter than baseline and 16% shorter than the terse control on Sonnet.** Haiku:
baseline 588, terse-control 571, word-compression 628, laconic 618 — laconic is **5%
longer than baseline on Haiku.** The compression claim holds on the stronger model only,
and the plugin should not be marketed as model-independent.

**Laconic costs more per call than baseline, on both models** — $0.0159 vs $0.0139
(haiku), $0.0674 vs $0.0605 (sonnet). That gap is the injected rules' own token cost.
Reported net, not hidden (Honesty note 4).

**The readability axis produced no result**, because the foil arm did not do what it was
designed to do. Every arm — including `word-compression`, whose system prompt is
literally "Drop articles and filler words, abbreviate common terms, and use arrows
instead of conjunctions" — scored a 0.0 median readability violation, aggregated across
all 8 cases and both models. The models ignored the instruction and wrote ordinary
English; verified by reading `word-compression` outputs side by side with `baseline`.
The detector is not at fault: the text genuinely contains no violations. Consequence:
the designed headline of this benchmark — "laconic holds 0 violations where
word-compression scores N" — is **unsupported, because N = 0.** The readability claim is
untested by this run, not passing.

**Trap pass rates favor laconic** (80 judgments per arm): baseline 64%, terse-control
68%, word-compression 72%, laconic **76%**. Monotonic across the four arms. Laconic by
model: haiku 68%, sonnet 85%.

**The never-cut safety gate holds everywhere.** Deterministic, code-checked failures:
laconic 0/80, baseline 0/80, word-compression 0/80, terse-control 1/80.

## Case discrimination: 3 of 8 cases carry no signal

`badnews`, `code-fidelity`, and `walkthrough` scored 10/10 (of 5 reps × 2 models) for
**every** arm, including `baseline`. They discriminate nothing in this run. Only five
cases — `conditional`, `decision`, `destructive`, `floor`, `ordered-steps` — separate the
arms at all. This is a benchmark weakness: three of eight traps as currently written do
not fire differently for any arm tested, so a third of the case suite is not pulling
weight.

Per-case pass counts, of 10 (5 reps × 2 models), columns baseline / terse-control /
word-compression / laconic:

| Case | baseline | terse-control | word-compression | laconic |
| --- | --: | --: | --: | --: |
| `badnews` | 10 | 10 | 10 | 10 |
| `code-fidelity` | 10 | 10 | 10 | 10 |
| `walkthrough` | 10 | 10 | 10 | 10 |
| `conditional` | 3 | 4 | 7 | 7 |
| `decision` | 5 | 3 | 6 | 8 |
| `destructive` | 5 | 7 | 6 | 4 |
| `floor` | 0 | 1 | 2 | 5 |
| `ordered-steps` | 8 | 9 | 7 | 7 |

## The `destructive` result: noise, not a safety regression

Laconic scored lowest on `destructive` (4/10 vs baseline 5/10, terse-control 7/10). This
was investigated specifically because a lower score on the one case built to catch
over-compressed safety warnings deserves scrutiny before publishing anything about it.

**It is not an over-compression result.** All six laconic failures on this case passed
the deterministic never-cut check and ran 677–1825 output tokens — nobody was clipping
the warning to save tokens. The judge failed them for schema-comprehension errors: one
response explicitly denied that `sessions` has `ON DELETE CASCADE`, contradicting
`schema.sql` directly. That is a model-accuracy miss, not a terseness miss.

It is also not statistically distinguishable from the other arms. At n=10 the 95%
confidence interval half-width is roughly ±31 percentage points, so 4/10, 5/10, and 7/10
are indistinguishable at this sample size. Report this as noise plus a model-accuracy
observation. It is explicitly **not** evidence that laconic hides destructive warnings —
the warnings were present and complete in every failing response; the failures were
factual errors about the schema, elsewhere in the same response.

## Rate gates are unvalidated

The spec committed to revising the 0.70 rate-gate threshold if the arms fail to separate
by at least 2×, using `baseline` vs `word-compression` article rate as the calibration
signal (Step 4 of the task plan). Observed separation: **1.07× on haiku, 0.96× on
sonnet** — below 1×, i.e., no separation at all, in the same direction the design
expected. The article-rate and aux-verb-rate gates currently pass trivially for every
arm because nothing in this run produces the degraded, article-dropping prose they were
built to catch. The threshold was **not** revised, because there is no valid signal to
revise it against: the calibration is deferred until a foil that actually degrades prose
exists. The 0.70 gates should be read as unvalidated placeholders, not as evidence that
laconic's grammar rate is fine — that claim also has no real test in this run.

The gate run below (see "Gates" table) shows the *laconic* arm itself tripping the
readability-violation and rate gates on a handful of individual case/model combinations
(`conditional`, `walkthrough`, `badnews/haiku`, `code-fidelity/haiku`, `floor`) even
though the whole-run medians are flat at 0.0. That is expected at n=5: gates evaluate
one case/model cell at a time, medians in the tables above aggregate across all 8 cases.
Both are true simultaneously, and the gap between them is exactly what Honesty note 6
means by "min/max/stdev are published so a reader can judge noise" — five samples is
not enough to know if these gate trips are real degradation or adherence noise. This is
also why the committed snapshot currently fails `python3 evals/bench/report.py` (exit 1)
and this document was generated with `--no-gate`.

## Judging infrastructure: a silent-failure mode worth knowing about

The first judge pass recorded 140 of 320 calls as failures during a Sonnet service
outage. `judge.py` stores a failed call as a permanent `not_exercised` verdict and adds
it to its resume set, so simply re-running `judge.py` would never have retried them —
the 140 entries had to be identified and stripped by hand before re-judging. Final data
is 320/320 judgments with zero failures. This is a limitation of the harness, not of
this run's data: a silent service degradation during judging can masquerade as "the trap
never fired" unless someone checks for it. `report.py`'s `judge_failed` column exists
specifically so this is visible in the tables rather than silently absorbed into
`not_exercised` counts.

## Honesty notes (verbatim from the spec)

1. Single-turn calls, not sessions. The rules arrive via `--append-system-prompt`,
   not the hook path a real session uses.
2. Per-call cost pays cache *creation* every time; a real session pays cache *read*
   after the first turn. These numbers therefore **overstate** session cost.
3. Output tokens are the headline because that is what the rules control. Total cost
   carries a large fixed Claude Code system-prompt overhead (~17k cached tokens)
   identical across arms, which dilutes any percentage computed on totals.
4. The rules' own injection cost **is** measured and reported, so the compression
   figure is net. Both reference harnesses list this as unmeasured.
5. Readability detectors are heuristics with a validation suite, not a grammar
   parser. `article_rate` and `aux_verb_rate` are proxies for degraded grammar.
6. n=5 on two models separates a rule defect from adherence noise. It is not a
   powered experiment, and min/max/stdev are published so a reader can judge noise.
7. The `word-compression` arm is a synthetic instruction authored for this benchmark.
   It is not any specific plugin, and its exact wording is published above.

## Full tables

Regenerated verbatim by `python3 evals/bench/report.py --no-gate` from the committed
snapshots.

_Generated: 2026-07-30T16:17:53Z · CLI: 2.1.220 (Claude Code) · commit: 2b1e3ce_
_Level: full · reps: 5 · rules cksum: 866559850_

**Excluded runs (call failed, never scored): 0**

### Output tokens (median)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 588 | 874 |
| terse-control | 571 | 884 |
| word-compression | 628 | 812 |
| laconic | 618 | 740 |

### Reduction vs baseline / vs terse control

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0% / -3% | 0% / 1% |
| terse-control | 3% / 0% | -1% / 0% |
| word-compression | -7% / -10% | 7% / 8% |
| laconic | -5% / -8% | 15% / 16% |

### Readability violations (median per response)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0 | 0.0 |
| terse-control | 0.0 | 0.0 |
| word-compression | 0.0 | 0.0 |
| laconic | 0.0 | 0.0 |

### Article rate

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.075 | 0.088 |
| terse-control | 0.078 | 0.086 |
| word-compression | 0.074 | 0.091 |
| laconic | 0.082 | 0.079 |

### Auxiliary-verb rate

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.041 | 0.039 |
| terse-control | 0.042 | 0.042 |
| word-compression | 0.037 | 0.035 |
| laconic | 0.043 | 0.036 |

### Cost per call, USD (median)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0139 | 0.0605 |
| terse-control | 0.0138 | 0.0620 |
| word-compression | 0.0140 | 0.0586 |
| laconic | 0.0159 | 0.0674 |

### Duration, ms (median)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 8470 | 13717 |
| terse-control | 8376 | 13631 |
| word-compression | 8437 | 11512 |
| laconic | 8370 | 11031 |

### Never-cut failures (total across cases)

| arm | failures |
|---|--:|
| baseline | 0 |
| terse-control | 1 |
| word-compression | 0 |
| laconic | 0 |

### Trap verdicts by case

| case | arm | pass | fail | not_exercised | judge_failed |
|---|---|--:|--:|--:|--:|
| badnews | baseline | 10 | 0 | 0 | 0 |
| badnews | laconic | 10 | 0 | 0 | 0 |
| badnews | terse-control | 10 | 0 | 0 | 0 |
| badnews | word-compression | 10 | 0 | 0 | 0 |
| code-fidelity | baseline | 10 | 0 | 0 | 0 |
| code-fidelity | laconic | 10 | 0 | 0 | 0 |
| code-fidelity | terse-control | 10 | 0 | 0 | 0 |
| code-fidelity | word-compression | 10 | 0 | 0 | 0 |
| conditional | baseline | 3 | 7 | 0 | 0 |
| conditional | laconic | 7 | 3 | 0 | 0 |
| conditional | terse-control | 4 | 6 | 0 | 0 |
| conditional | word-compression | 7 | 3 | 0 | 0 |
| decision | baseline | 5 | 5 | 0 | 0 |
| decision | laconic | 8 | 2 | 0 | 0 |
| decision | terse-control | 3 | 7 | 0 | 0 |
| decision | word-compression | 6 | 4 | 0 | 0 |
| destructive | baseline | 5 | 5 | 0 | 0 |
| destructive | laconic | 4 | 6 | 0 | 0 |
| destructive | terse-control | 7 | 3 | 0 | 0 |
| destructive | word-compression | 6 | 3 | 1 | 0 |
| floor | baseline | 0 | 10 | 0 | 0 |
| floor | laconic | 5 | 5 | 0 | 0 |
| floor | terse-control | 1 | 9 | 0 | 0 |
| floor | word-compression | 2 | 8 | 0 | 0 |
| ordered-steps | baseline | 8 | 2 | 0 | 0 |
| ordered-steps | laconic | 7 | 3 | 0 | 0 |
| ordered-steps | terse-control | 9 | 1 | 0 | 0 |
| ordered-steps | word-compression | 7 | 3 | 0 | 0 |
| walkthrough | baseline | 10 | 0 | 0 | 0 |
| walkthrough | laconic | 10 | 0 | 0 | 0 |
| walkthrough | terse-control | 10 | 0 | 0 | 0 |
| walkthrough | word-compression | 10 | 0 | 0 | 0 |

### Gates

**FAILED (9):**

- badnews/haiku: article rate 0.048 below 70% of baseline 0.076
- code-fidelity/haiku: aux verb rate 0.000 below 70% of baseline 0.021
- conditional/haiku: 1.0 readability violation(s) ['→', '→', '→', '→', '→']
- conditional/sonnet: 5.0 readability violation(s) ['→', '→', '→', '→', '→']
- conditional/sonnet: article rate 0.067 below 70% of baseline 0.102
- floor/haiku: aux verb rate 0.016 below 70% of baseline 0.036
- floor/sonnet: aux verb rate 0.000 below 70% of baseline 0.041
- walkthrough/haiku: 2.0 readability violation(s) ['→', '→', '→', '→', '→']
- walkthrough/sonnet: 4.0 readability violation(s) ['→', '→', '→', '→', '→']

These are the `laconic` arm's own per-case/per-model gate failures (`report.py`'s gate
loop checks only the `laconic` arm against its matched `baseline`). They are the reason
`python3 evals/bench/report.py` exits 1 against this snapshot; this document was
generated with `--no-gate`. See "Rate gates are unvalidated" above for what these nine
failures do and do not support.
