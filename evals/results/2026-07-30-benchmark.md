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

## This revision corrects the previous publication

A review of the first published version of this document found two of its headline
claims wrong and one gate result undisclosed. Nothing about the underlying snapshots
changed — same `results.json`, same `judgments.json` — only how they were read and
scored. What changed and where:

1. **The trap-pass-rate claim ("laconic 76%, monotonic across arms") is retracted
   entirely.** It was confounded two different ways: contamination (the treatment arm's
   own system prompt contains material that overlaps two of the five discriminating
   cases) and circularity (two of those five cases grade adherence to laconic's own rule
   text, verbatim). See "Trap-based claims: retracted" below. No trap-based claim is
   made anywhere in this document.
2. **The readability claim ("every arm scored 0.0, the foil never degraded, the
   detector is not at fault") was wrong in both directions.** The 0.0 was a median
   artifact, not an absence of violations, and the raw counts behind it were 96% false
   positives from a detector bug. The detector has since been fixed. See "Readability"
   below.
3. **New disclosure: laconic fails its own gate.** With the corrected detector and a
   sum-based gate, `report.py` now exits 1 against this exact snapshot, with 4 failures,
   one of them a confirmed real defect. This was not disclosed in the previous version.
   See "Laconic fails its own gate" below.
4. **The compression headline's aggregation convention is now named.** "Median output
   tokens" is a median of per-case medians; a flat median over the 40 raw runs per
   arm/model gives a different number and, on Haiku, a different sign. See "Compression"
   below.
5. **min/max/stdev are now actually computed and published.** The previous version's
   Honesty note 6 claimed dispersion was published "so a reader can judge noise" when
   nothing in the report computed it. That was false when written; it is true now.
6. **The never-cut denominator is corrected.** "0 failures across 80 checked responses"
   overstated the denominator by 60% — only 50 of 80 responses per arm carry a
   `never_cut` keyword list to check at all. See "Never-cut" below.
7. **An asymmetric statistical treatment is removed.** The previous version computed a
   ±31 percentage-point confidence interval to explain away one unfavorable trap result,
   while presenting every favorable result with no uncertainty at all. Since no
   trap-based claim survives this revision, the interval is simply dropped rather than
   applied selectively.

A benchmark that quietly revises its own numbers is worth less than one that shows its
corrections. This section stays in future revisions of this document as long as any of
the corrected claims are still being cited elsewhere.

## Headline

**No trap-based claim is made in this document.** The cases that discriminate at all are
contaminated by material from laconic's own rule text reaching the treatment arm, and two
of those cases grade adherence to that same rule text verbatim. Full reasoning: "Trap-based
claims: retracted," below.

**Compression is real on Sonnet and does not exist on Haiku.** Median output tokens (median
of per-case medians — see "Compression" for the aggregation note) — sonnet: baseline 874,
terse-control 884, word-compression 812, laconic 740. Laconic is **15% shorter than
baseline and 16% shorter than the terse control on Sonnet.** Haiku: baseline 588,
terse-control 571, word-compression 628, laconic 618 — laconic is **5% longer than baseline
on Haiku.** The compression claim holds on the stronger model only, and the plugin should
not be marketed as model-independent.

**Laconic costs more per call than baseline, on both models** — $0.0159 vs $0.0139
(haiku), $0.0674 vs $0.0605 (sonnet). That gap is the injected rules' own token cost.
Reported net, not hidden (Honesty note 4).

**Readability shows no contrast across arms, for a different and better-understood reason
than previously published.** With a corrected arrow detector, 17 violations total across
all 320 responses; no arm — including the word-compression foil, which wrote ordinary
English despite being instructed to drop articles and use arrows — degrades grammar
meaningfully. Laconic does not "win" this axis. See "Readability," below.

**Laconic fails its own gate.** `report.py` (sum-based gate, corrected detector) exits 1
against this snapshot: 4 failures, one of them a confirmed real arrow-chain violation in
running prose. See "Laconic fails its own gate," below.

**The never-cut safety gate holds on every response it checks.** Deterministic,
code-checked failures, out of 50 checked responses per arm (30 of the 80 responses per
arm carry no keywords to check by design): laconic 0, baseline 0, word-compression 0,
terse-control 1.

## Compression: the one clean result

Median output tokens —

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 588 | 874 |
| terse-control | 571 | 884 |
| word-compression | 628 | 812 |
| laconic | 618 | 740 |

Laconic is 15% shorter than baseline on Sonnet (740 vs 874) and 5% longer than baseline on
Haiku (618 vs 588). It costs more per call than baseline on both models — $0.0159 vs
$0.0139 (haiku), $0.0674 vs $0.0605 (sonnet) — the injected rules' own token cost, net.

**Aggregation convention, disclosed:** the number above is a median of per-case medians —
`report.py` first takes the median output-token count within each (case, arm, model)
bucket (5 reps), then medians those 8 per-case values into the single number shown per
arm/model. A flat median over the 40 raw per-arm-per-model runs (8 cases × 5 reps, no
intermediate per-case step) gives **sonnet 13.7% shorter** (not 15%) and **haiku roughly
break-even at +0.9%** (not +5% longer) — same direction on Sonnet, a **different sign on
Haiku**. A reader recomputing this figure directly from `evals/snapshots/results.json`
without matching this convention will get a different number, and on Haiku, a different
conclusion. This convention is named here because nothing enforces it implicitly.

Dispersion across reps (median across cases), from the same snapshot:

min:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 526 | 712 |
| terse-control | 452 | 664 |
| word-compression | 490 | 638 |
| laconic | 480 | 620 |

max:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 713 | 1229 |
| terse-control | 678 | 1054 |
| word-compression | 731 | 1019 |
| laconic | 690 | 884 |

stdev:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 56.5 | 191.8 |
| terse-control | 54.3 | 169.1 |
| word-compression | 87.1 | 159.0 |
| laconic | 66.1 | 103.7 |

These three tables did not exist in the previous version of this document, despite Honesty
note 6 there claiming they did. They are real now — see "This revision corrects the
previous publication," item 5.

These are single-turn `--append-system-prompt` calls, not multi-turn sessions, so the
per-call cost above **overstates** what a real session pays once the first turn's cache
write becomes a cache read (Honesty note 2).

## Readability: no contrast, for a corrected reason

The previous version of this document stated: "every arm scored 0.0 violations, the foil
never degraded its prose, the detector is not at fault." **That was wrong in both
directions.**

The 0.0 was a median artifact — violations concentrate in a minority of responses per
cell, and a median across 5 reps reads as 0.0 even when individual responses have several.
And the raw counts behind that median were themselves wrong: **96% of the symbol hits
were false positives.** The arrow detector was firing on two things it should never have
counted: markdown bullets (`- step one → step two`, which is structural, not prose) and
numeric progressions quoted out of a log fixture (`7 → 11 → 14`, which is data, not a
conjunction). The rule the detector enforces — `rules/laconic.md`'s "No arrows standing in
for conjunctions in running prose" — forbids arrows in running prose *specifically*; it
does not forbid them in a bulleted procedure or a quoted number sequence.

The detector has since been corrected: structural lines (bullets, headings, table rows)
and numeric progressions are now excluded before counting. That correction dropped real
symbol hits from 269 to 12 project-wide. Recomputed from the **same, unmodified**
snapshots — no re-generation, no re-judging — violations across 80 responses per arm:

| arm | haiku | sonnet | total |
|---|--:|--:|--:|
| baseline | 0 | 2 | 2 |
| terse-control | 1 | 3 | 4 |
| word-compression | 0 | 5 | 5 |
| laconic | 0 | 6 | 6 |

17 violations across all 320 responses. The honest conclusion: **no arm degrades grammar
meaningfully, including the word-compression foil** — which wrote ordinary English despite
being instructed to "Drop articles and filler words, abbreviate common terms, and use
arrows instead of conjunctions." The readability axis still yields no contrast between
arms, but for a different and better-understood reason than previously published, and
laconic does not "win" it: 6 of the 17 violations across the entire run belong to laconic,
the largest count of any arm, not the smallest.

**Rate gates are unvalidated for the same underlying reason.** The spec committed to
revising the 0.70 article/aux-verb-rate threshold if `baseline` and `word-compression`
separated by at least 2×, calibrated on the article rate. Observed separation (median of
per-case medians): 1.01× on haiku, 0.96× on sonnet — nowhere near 2×, and inverted on
Sonnet. The threshold was not revised, because there is no valid signal to revise it
against: nothing in this run produces the degraded, article-dropping prose the gates were
built to catch, on any arm, including the foil designed to produce exactly that. Read the
0.70 thresholds as unvalidated placeholders, not as evidence that laconic's grammar rate
is fine — see "Laconic fails its own gate" for two cells where the threshold does fire.

## Trap-based claims: retracted

The previous version of this document headlined: "trap rates rise monotonically —
baseline 64%, terse-control 68%, word-compression 72%, laconic 76%." **That claim is
retracted. The owner's decision is that no trap-based claim is made from this run.**

It is confounded two separate ways.

**Contamination.** `rules/laconic.md:36-37` ships inside laconic's own system prompt and
contains a worked example: *"Check the trend first. If memory sits at a steady ceiling,
raise the limit; if it is climbing, you have a leak and a bigger limit only delays the
next kill."* The `conditional` case is a connection-pool domain-swap of exactly that
scenario — the treatment arm receives, inside its own instructions, worked reasoning for
the specific trap it is then scored on. Separately, `rules/laconic.md:92` contains the
literal string `"Use a UUID."` while the `decision` case asks whether a sharded primary
key should be a UUID or an auto-incrementing integer. The treatment arm received answer
material no control arm did, on two of the five cases that discriminate at all in this
run.

**Circularity.** The `decision` and `floor` traps grade adherence to laconic's own rule
text. "Surveys both options," "ends with an offer to do more work," and "padded out with
unrequested material" are lifted directly from `rules/laconic.md`'s own prohibitions. A
benchmark cannot validly score a treatment on criteria drawn from that treatment's own
instructions — the control arms were never given a chance to fail by that standard,
because the standard did not exist for them.

**Excluding just those two cases (`decision`, `floor`), the ordering inverts.** Out of 60
(6 remaining cases × 10 reps-and-models each):

| arm | pass | rate |
|---|--:|--:|
| terse-control | 50/60 | 83% |
| word-compression | 50/60 | 83% |
| laconic | 48/60 | 80% |
| baseline | 46/60 | 77% |

**Laconic goes from first to third of four.** This is not offered as a corrected trap
claim either — six cases at n=10 is still too little to support one, and three of those
six carry no signal at all (below). It is offered as proof that the retracted claim was
an artifact of which cases were included, not a robust result that merely needs a caveat.

**Three of eight cases discriminate nothing.** `badnews`, `code-fidelity`, and
`walkthrough` scored 10/10 (of 5 reps × 2 models) for every arm, including `baseline`, in
this run. A third of the case suite is not pulling weight.

Fixing this requires two things, neither of which has happened yet: cases designed
independently of `rules/laconic.md`'s text (so the treatment cannot receive answer
material the control never gets, and so pass criteria are not drawn from the rule under
test), and a re-run against those cases. Until then, this benchmark has no valid
trap-avoidance signal to publish, favorable or unfavorable.

**On `destructive` specifically:** laconic's response text was read directly for every
failure on this case (the one case designed to catch a hidden or truncated safety
warning). In every laconic failure on `destructive`, the schema warning itself — the
`invoices` foreign key and the `sessions` cascade — was present and complete; every
observed failure was the judge marking a factual claim about the schema wrong elsewhere in
the same response, not a missing or shortened warning. This is a reading of the raw
transcripts, not a trap-count comparison, and it is the only claim about `destructive` made
in this document.

For raw data only — **not evidence for any claim in this document** — pass counts of 10
(5 reps × 2 models), columns baseline / terse-control / word-compression / laconic:

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

## Laconic fails its own gate

With the corrected detector and the sum-based gate (`violations_total`, not the
per-response median — a median cannot see a regression concentrated in a minority of
responses), `python3 evals/bench/report.py --judgments evals/snapshots/judgments.json`
exits 1 against this exact, unmodified snapshot, with 4 failures:

- `badnews/haiku` — article rate 0.048 vs 70% of baseline 0.076 (baseline had ~5.0 article
  words)
- `conditional/sonnet` — article rate 0.067 vs 70% of baseline 0.102 (baseline had ~10.0
  article words)
- `ordered-steps/sonnet` — 5 readability violations across 5 responses (median displays as
  0.0 — see below)
- `walkthrough/sonnet` — 1 readability violation across 5 responses

**The `ordered-steps/sonnet` failure is genuine, verified by reading the response.** All 5
violations in that cell come from a single response (rep 2 of laconic/sonnet/ordered-steps),
which wrote:

> Rough runbook: generate new key pair → add to JWKS/key store as non-primary → let it
> propagate to all verifiers (respect any cache TTL) → cut over signing to the new key →
> wait out the old token TTL → remove the old key.

Five arrows standing in for conjunctions, in running prose, in one sentence — exactly what
`rules/laconic.md` forbids ("No arrows standing in for conjunctions in running prose"). The
other 4 responses in that cell have zero violations; the per-response median for the cell
is 0.0, which is why this is reported as "5 violations across 5 responses (median 0.0)"
rather than as a median. This is a real finding about the plugin, not a detector artifact:
laconic's own rule text is what this response broke.

**Three further rate-gate readings were suppressed as artifacts, not as passes**, because
the baseline cell had fewer than 5 article/auxiliary words to begin with:

- `code-fidelity/haiku` — baseline had ~1.0 auxiliary word (of ~49 total words)
- `floor/haiku` — baseline had ~2.0 auxiliary words
- `floor/sonnet` — baseline had ~4.0 auxiliary words

`report.py` enforces an absolute floor (`ABS_COUNT_FLOOR = 5`) alongside the rate
threshold specifically because a ratio of small integers is not evidence: one short,
correct answer with zero auxiliary verbs in it is terse English, not a degraded ratio.
Below the floor, the gate does not fire regardless of what the rate says. This is disclosed
here so "4 failures" is not misread as "these 3 other candidate readings passed on their
merits" — they did not pass; they were excluded as not meaningful.

This gate result is reported here, in the body of this document, rather than only
discoverable by running the command: laconic — the arm under test — currently fails the
readability/rate gate this benchmark itself defines, on 4 of the case/model cells checked,
one of which is a confirmed defect in the plugin's own adherence to its own rule.

## Never-cut: denominator corrected

| arm | checked | unchecked | failures |
|---|--:|--:|--:|
| baseline | 50 | 30 | 0 |
| terse-control | 50 | 30 | 1 |
| word-compression | 50 | 30 | 0 |
| laconic | 50 | 30 | 0 |

Three of eight cases (`decision`, `floor`, `ordered-steps`) carry an empty `never_cut`
keyword list by design — they are graded entirely by the judge, not by a deterministic
keyword check (`evals/CRITERIA.md`). That means 30 of the 80 responses per arm are not
checked by this gate at all. The previous version of this document reported "0 failures
across 80 checked responses," which overstated the denominator by 60% — only 50 of those
80 were actually checked. 0 failures out of 50 checked is still 0 failures, and still holds
for `baseline`, `word-compression`, and `laconic`; `terse-control` has 1.

## Judging infrastructure: limitations worth knowing about

**Judging blindness was not enforced at generation time.** The committed judgments were
produced by a judge process that ran with its working directory set to the repo root,
where `evals/snapshots/results.json` labels every response by arm and `rules/laconic.md`
is the treatment's own prompt — both readable from that working directory even though the
judge is not supposed to look at them. `judge.py` has since been fixed to run from a
scratch directory instead, but the committed judgments in this snapshot predate that fix.
This is a separate and compounding reason no trap-based claim is made from this run: even
setting aside contamination and circularity in the case design, the grading process itself
was not guaranteed blind when these judgments were produced.

**The first judging pass lost 140 of 320 calls to a service outage.** `judge.py` records a
failed call as a permanent `not_exercised` verdict and adds it to its resume set, so simply
re-running `judge.py` at the time would never have retried them — the 140 affected entries
had to be identified and stripped by hand before re-judging. `judge.py` now retries a
failed call once before recording it as failed. Final data in this snapshot is 320/320
judgments with zero unresolved failures, but the retry behavior that would have caught this
automatically did not exist when this snapshot was produced.

## Honesty notes (from the original spec, corrected where wrong)

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
   parser. `article_rate` and `aux_verb_rate` are proxies for degraded grammar. The
   symbol-connector detector was corrected during this revision (see "Readability").
6. n=5 on two models separates a rule defect from adherence noise. **Corrected:** the
   previous version of this document claimed min/max/stdev were published here; they
   were not. They are now — see "Compression."
7. The `word-compression` arm is a synthetic instruction authored for this benchmark.
   It is not any specific plugin, and its exact wording is published above.
8. "Median output tokens" is a median of per-case medians, not a flat median over the
   40 raw per-arm-per-model runs. Naming this here because a reader recomputing the
   headline number directly from the snapshot without matching the convention gets a
   different number, and on Haiku, a different sign — see "Compression."

## Full tables

Regenerated verbatim by `python3 evals/bench/report.py --no-gate --judgments evals/snapshots/judgments.json`
from the committed snapshots.

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

### Output tokens dispersion across reps (median across cases)

min:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 526 | 712 |
| terse-control | 452 | 664 |
| word-compression | 490 | 638 |
| laconic | 480 | 620 |

max:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 713 | 1229 |
| terse-control | 678 | 1054 |
| word-compression | 731 | 1019 |
| laconic | 690 | 884 |

stdev:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 56.5 | 191.8 |
| terse-control | 54.3 | 169.1 |
| word-compression | 87.1 | 159.0 |
| laconic | 66.1 | 103.7 |

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

### Readability violations (total across responses; this is what gates)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0 | 2 |
| terse-control | 1 | 3 |
| word-compression | 0 | 5 |
| laconic | 0 | 6 |

### Responses with >=1 readability violation

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0 | 2 |
| terse-control | 1 | 2 |
| word-compression | 0 | 3 |
| laconic | 0 | 2 |

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

### Never-cut failures (checked vs unchecked responses)

| arm | checked | unchecked | failures |
|---|--:|--:|--:|
| baseline | 50 | 30 | 0 |
| terse-control | 50 | 30 | 1 |
| word-compression | 50 | 30 | 0 |
| laconic | 50 | 30 | 0 |

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
| destructive | word-compression | 6 | 3 | 0 | 1 |
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

**FAILED (4):**

- badnews/haiku: article rate 0.048 below 70% of baseline 0.076 (baseline had ~5.0 article words)
- conditional/sonnet: article rate 0.067 below 70% of baseline 0.102 (baseline had ~10.0 article words)
- ordered-steps/sonnet: 5 readability violation(s) across 5 response(s) (median 0.0) sample: ['→', '→', '→', '→', '→']
- walkthrough/sonnet: 1 readability violation(s) across 5 response(s) (median 0.0) sample: ['auth.js is self-contained — 40 lines, no']

This is why `python3 evals/bench/report.py --judgments evals/snapshots/judgments.json`
(no `--no-gate`) exits 1 against this snapshot, and why this document was generated with
`--no-gate`. See "Laconic fails its own gate," above, for what these four failures do and
do not mean.
