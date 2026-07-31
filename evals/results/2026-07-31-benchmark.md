# Benchmark results — 2026-07-31

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
| Generation cost | $3.61 (laconic arm, regenerated) + $10.12 (controls, carried over) |
| Rules checksum | 3401310310 |
| Claude CLI | 2.1.220 |
| Laconic arm generated | 2026-07-31 |
| Control arms generated | 2026-07-30 |

Snapshots: `evals/snapshots/results.json` (320 generations), `evals/snapshots/judgments.json`
(320 judgments). Both committed; every table below regenerates from them offline with
`python3 evals/bench/report.py --no-gate` — no network, no third-party packages.

## This run supersedes 2026-07-30, which found a real defect

The [2026-07-30 run](2026-07-30-benchmark.md) reported that laconic had the most
readability violations of any arm — 16 of the run's 25, on a quarter of the responses,
more than a foil that had been explicitly instructed to use arrows. That finding was
correct. It was a genuine defect in the shipped rules, and this run is the measurement
taken after fixing it.

**What was wrong with the plugin.** `rules/laconic.md` said: *"No arrows standing in for
conjunctions in running prose."* That sentence has two openings, and every single one of
the 16 observed violations went through one of them:

- *"standing in for **conjunctions**"* — none of the violations substituted an arrow for
  "and" or "but". They chained sequences: `generate new key pair → add to JWKS → let it
  propagate → cut over signing`. A sequence arrow is not a conjunction, so the rule read
  as not applying.
- *"in **running prose**"* — 11 of the 16 sat inside a bolded-label paragraph
  (`**Request A**: calls currentToken() → token is expired → ...`) or a `Rough runbook:`
  line. Those read as structured constructs rather than running prose.

A contributing cause sat in the rule text itself. The rules file is injected verbatim
into the prompt, and its word-shortening gloss was written ``(`configuration` →
`config`, `implementation` → `impl`)`` — arrows used approvingly, in the same sentence
that prohibits arrows.

**The fix.** The prohibition now bans arrows anywhere in a sentence, names the
constructions the model actually reaches for, and carries a wrong/right pair for each,
matching how every other never-do item in the file is written. The gloss no longer uses
arrows to illustrate itself. `tests/test_rules.sh` now fails if an arrow reappears in the
rules text outside a line marked `Wrong`, and if the rule stops naming the bold-label and
runbook forms.

**The result: 16 violations → 0.** Laconic is now tied with baseline as the cleanest arm
in the run. The two control arms, whose text did not change, still carry 5 and 4.

This took two iterations. The first rewrite banned arrows for chaining "steps, stages,
states, or causes" and took the count from 16 to 1; the survivor used an arrow for a
*mapping* (``mapping `kid` → public key``), which that enumeration did not cover. The
enumeration was closed rather than left with a gap, and the arm regenerated again.

**What changed in the harness, and why it is not scorekeeping.** The 2026-07-30 gate also
fired on two article-rate cells (`badnews/haiku`, `conditional/sonnet`). Those were false
positives, and the evidence is not statistical hand-waving:

1. All four flagged responses were read. They are ordinary correct English. One is 38
   words with zero articles and nothing wrong with it: *"Any query callback that throws
   was leaking its client — with waiting requests piling up 4-5 per 30s, that's likely
   one recurring failing query."* Its noun phrases take possessives, quantifiers and
   demonstratives, which is what short English does.
2. The gate fired on `word-compression` at exactly the same rate (2 of 16 cells) — an arm
   whose responses also keep their articles.
3. Splitting `baseline`'s own five reps and running the gate against itself fires in 11
   of 160 splits (~7%). At 16 cells, a clean arm is *expected* to produce one or two
   failures.

The metric itself is sound — mechanically strip the articles out of laconic's responses
and it fires on every case — so it was kept, not deleted. What changed is that the two
rate gates now require the drop to reproduce on **every model tested**. That costs no
sensitivity: on article-stripped text the corroborated gate still fires on 7 of 8 cases
and reports the 8th as ungated rather than passing it. A rules regression is a property of
the rules and shows on both models; sampling noise does not correlate across them.

Directly observed defects — an arrow in prose, a dropped never-cut keyword — are not
proxies and still fail on a single occurrence. That distinction is the whole rule: gate
observations on any occurrence, gate statistical proxies on corroboration.

**Disclosure: this snapshot is mixed.** The `laconic` arm was regenerated on 2026-07-31
under the new rules. The `baseline`, `terse-control` and `word-compression` arms are
carried over unchanged from 2026-07-30 — none of their prompts depend on
`rules/laconic.md`. Holding the controls fixed isolates the rule change instead of adding
fresh sampling noise to both sides of the comparison, but it does mean the control numbers
were not sampled at the same time as the treatment numbers. `results.json` records both
dates and both commits.

## Headline

**Laconic no longer violates its own no-arrows rule.** 0 violations across 80 responses,
down from 16. Baseline 0, terse-control 5, word-compression 4, laconic 0. The arms that
still violate are the two whose instructions did not change.

**Compression is real on Sonnet and absent on Haiku.** Median output tokens (median of
per-case medians) — sonnet: baseline 874, terse-control 884, word-compression 812,
laconic 626. That is **28% shorter than baseline** and 29% shorter than the terse control.
Haiku: baseline 588, laconic 615 — **5% longer than baseline.** The aggregation convention
matters and the two estimators disagree on Haiku: a flat median over the 40 raw runs gives
sonnet 884 → 708 (−20%) and haiku 604 → 552 (−9%). Sonnet compresses on both estimators;
Haiku's sign depends on which one you pick, so no Haiku compression claim is made.

**Laconic still costs more per call than baseline, on both models** — $0.0164 vs $0.0139
(haiku), $0.0653 vs $0.0605 (sonnet). That gap is the injected rules' own token cost, and
the rules got longer with this fix. Reported net, not hidden.

**No trap-based claim is made.** Unchanged from 2026-07-30 and unaffected by this fix: the
cases that discriminate at all are contaminated by material from laconic's own rule text
reaching the treatment arm, and two of them grade adherence to that same rule text
verbatim. See "Trap-based claims: still retracted," below.

**Laconic still fails its own gate, for a different and smaller reason.** `report.py`
exits 1 against this snapshot with 2 never-cut failures. Both were read and both are
genuine — this is the safety check working, and it has not been touched. See "The gate,"
below.

## Compression

The comparison that matters is laconic against `terse-control`, not against baseline.
The terse control receives a plain "be terse, no preamble, no closing offers" instruction
with none of laconic's structure; it isolates how much of the effect is the rule set
rather than merely asking for brevity.

On Sonnet, laconic is 29% shorter than the terse control — the effect is the rule set,
not the request for brevity. On Haiku, laconic is 8% *longer* than the terse control.

Dispersion is published in the full tables (min, max, stdev per arm/model) so a reader
can judge how much of any gap is noise at n=5. On Sonnet, laconic's stdev (119) is the
lowest of the four arms and its max (832) is below baseline's min-to-max band — the
compression there is not one or two short outliers dragging a median.

## Readability

The detector counts three things on code-stripped prose: arrows standing in a sentence,
telegraphic abbreviations (`impl`, `req`, `w/`), and sentences starting lowercase. It is a
proxy for degraded grammar, not a parser, and it has been wrong before — the 2026-07-30
document records two corrections to it, both of which had been hiding violations in
laconic's favour.

It has not been touched in this revision. That is deliberate: the detector was corrected
twice while it was reporting results unfavourable to the plugin, and touching it again now
that the plugin passes would be indistinguishable from tuning it to a desired answer. The
fix went into the rules, and the unchanged detector scored the result.

| arm | violations | responses affected (of 80) |
|---|--:|--:|
| baseline | 0 | 0 |
| terse-control | 5 | 3 |
| word-compression | 4 | 3 |
| laconic | **0** | **0** |

## Trap-based claims: still retracted

Nothing in this revision changes the contamination or the circularity, and the retraction
from 2026-07-30 stands in full. Briefly:

- **Contamination.** `rules/laconic.md` is injected verbatim into the treatment arm's
  prompt, and it contains a worked example about an OOM kill and a memory limit whose
  structure the `conditional` case reproduces with the domain swapped, plus the literal
  string `"Use a UUID."`, which the `decision` case's expected answer matches.
- **Circularity.** `decision` and `floor` grade whether the response follows laconic's own
  rule text. The treatment arm is handed that text and the control arms are not, so a
  favourable result measures instruction-following, not response quality.

The trap-verdict table is still published below, because suppressing it would hide the
five cases where the arms genuinely differ. It is not evidence for the plugin.

## The gate

`report.py` exits 1 against this snapshot:

```
FAILED (2):
- conditional/sonnet: 1 never-cut failure(s)
- destructive/haiku: 1 never-cut failure(s)
```

Both were read rather than counted, and both are real:

- **`destructive/haiku` rep2** was shown a schema where `sessions` cascade-deletes from
  `users` and `invoices` holds a foreign key to it, and asked about dropping `users`. It
  answered *"Look for any other tables with `FOREIGN KEY ... REFERENCES users`"* — telling
  the user to go find out instead of naming what was in the fixture in front of it.
  `rules/laconic.md` requires naming "exactly what will be affected" before a destructive
  action. It also closed with *"Want me to check the schema and fixtures for you?"*, which
  `lite` forbids outright; this sample ignored several rules at once.
- **`conditional/sonnet` rep3** answered *"That's the actual fix — no need to raise pool
  size"* — a reply that reads as a mid-conversation continuation and never diagnoses the
  connection leak the case is about.

**Is this a regression from the arrow fix?** The honest answer is that it is not
distinguishable from sampling noise, and there is no evidence it is caused by the fix:

- Pre-fix laconic scored 0 of 50 checked responses; post-fix it scores 2 of 50. Fisher's
  exact two-sided p = 0.50.
- `terse-control`, whose text did not change, scores 1 of 50 on the same snapshot. A low
  ambient rate of these misses is what these models do on these cases.
- The concern that a longer rules file might make responses terser and cut safety content
  was tested directly and does not hold. The overall median token change is not
  significant (two-sided permutation test, p = 0.67; 11 of 16 case/model cells shorter,
  5 longer). More to the point, the `destructive` case — the safety-critical one — got
  **longer**, by 17% on Haiku and 35% on Sonnet.

Two failures out of 50 is not zero and is not being reported as zero. The gate is red, and
it stays red until a run produces responses that pass it. It was not loosened to
produce a green result.

## Never-cut

The never-cut check is deterministic: for the five cases that carry a keyword list, it
asserts the response contains tokens a correct answer cannot avoid (`cascade` and
`invoices` for `destructive`, `leak` for `conditional`, `401` for `walkthrough`,
`proration` for `badnews`, `-size`/`-mtime` for `code-fidelity`).

Three of the eight cases — `decision`, `floor`, `ordered-steps` — carry an empty list and
are **not checked at all**. Their keyword lists were emptied deliberately during
development, after an earlier version used `"if"` for `conditional` and discovered it
matched "different", "specify" and "identify", making the assertion vacuous. Only tokens a
correct answer cannot avoid survived. The denominator is therefore 50 of 80 responses per
arm, not 80, and a "0 failures" reading must not be mistaken for "all 80 checked and
clean".

## Honesty notes

1. **These are single-turn calls.** Every generation is one `--append-system-prompt`
   invocation, not a multi-turn session. The per-call cost figures therefore **overstate**
   what a real session pays, because the first turn's cache write becomes a cache read on
   every subsequent turn.
2. **n=5 per cell.** Dispersion is published so the reader can judge noise. Differences
   smaller than the stdev shown are not claims.
3. **Two models, one vendor.** Nothing here says anything about how these rules behave on
   a non-Claude model.
4. **Cost is reported net of the injected rules**, which is why laconic costs more per
   call while producing fewer output tokens on Sonnet.
5. **The judge is a Claude model grading Claude outputs**, blind to arm, with the rules
   text withheld. It is still not an independent evaluator, and no claim rests on it.
6. **The snapshot is mixed** — treatment regenerated 2026-07-31, controls carried over
   from 2026-07-30. See the disclosure above.
7. **The compression aggregation convention changes the Haiku result's sign.** Both
   estimators are published rather than the flattering one.
8. **The gate is red.** See "The gate," above.

## Full tables

Everything below is generated by `python3 evals/bench/report.py --no-gate` from the
committed snapshots.

_Generated: 2026-07-31T00:00:00Z · CLI: 2.1.220 (Claude Code) · commit: ee36d2c_
_Level: full · reps: 5 · rules cksum: 3401310310_

**Excluded runs (call failed, never scored): 0**

### Output tokens (median)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 588 | 874 |
| terse-control | 571 | 884 |
| word-compression | 628 | 812 |
| laconic | 615 | 626 |

### Output tokens dispersion across reps (median across cases)

min:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 526 | 712 |
| terse-control | 452 | 664 |
| word-compression | 490 | 638 |
| laconic | 516 | 502 |

max:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 713 | 1229 |
| terse-control | 678 | 1054 |
| word-compression | 731 | 1019 |
| laconic | 658 | 832 |

stdev:

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 56.5 | 191.8 |
| terse-control | 54.3 | 169.1 |
| word-compression | 87.1 | 159.0 |
| laconic | 81.4 | 119.4 |

### Reduction vs baseline / vs terse control

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0% / -3% | 0% / 1% |
| terse-control | 3% / 0% | -1% / 0% |
| word-compression | -7% / -10% | 7% / 8% |
| laconic | -5% / -8% | 28% / 29% |

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
| baseline | 0 | 0 |
| terse-control | 2 | 3 |
| word-compression | 0 | 4 |
| laconic | 0 | 0 |

### Responses with >=1 readability violation

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0 | 0 |
| terse-control | 1 | 2 |
| word-compression | 0 | 3 |
| laconic | 0 | 0 |

### Article rate

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.075 | 0.088 |
| terse-control | 0.078 | 0.086 |
| word-compression | 0.074 | 0.091 |
| laconic | 0.081 | 0.096 |

### Auxiliary-verb rate

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.041 | 0.039 |
| terse-control | 0.042 | 0.042 |
| word-compression | 0.037 | 0.035 |
| laconic | 0.040 | 0.034 |

### Cost per call, USD (median)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0139 | 0.0605 |
| terse-control | 0.0138 | 0.0620 |
| word-compression | 0.0140 | 0.0586 |
| laconic | 0.0164 | 0.0653 |

### Duration, ms (median)

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 8470 | 13717 |
| terse-control | 8376 | 13631 |
| word-compression | 8437 | 11512 |
| laconic | 8480 | 10242 |

### Never-cut failures (checked vs unchecked responses)

| arm | checked | unchecked | failures |
|---|--:|--:|--:|
| baseline | 50 | 30 | 0 |
| terse-control | 50 | 30 | 1 |
| word-compression | 50 | 30 | 0 |
| laconic | 50 | 30 | 2 |

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
| destructive | laconic | 5 | 5 | 0 | 0 |
| destructive | terse-control | 7 | 3 | 0 | 0 |
| destructive | word-compression | 6 | 4 | 0 | 0 |
| floor | baseline | 0 | 10 | 0 | 0 |
| floor | laconic | 6 | 4 | 0 | 0 |
| floor | terse-control | 1 | 9 | 0 | 0 |
| floor | word-compression | 2 | 8 | 0 | 0 |
| ordered-steps | baseline | 8 | 2 | 0 | 0 |
| ordered-steps | laconic | 9 | 1 | 0 | 0 |
| ordered-steps | terse-control | 9 | 1 | 0 | 0 |
| ordered-steps | word-compression | 7 | 3 | 0 | 0 |
| walkthrough | baseline | 10 | 0 | 0 | 0 |
| walkthrough | laconic | 10 | 0 | 0 | 0 |
| walkthrough | terse-control | 10 | 0 | 0 | 0 |
| walkthrough | word-compression | 10 | 0 | 0 | 0 |

### Gates

**FAILED (2):**

- conditional/sonnet: 1 never-cut failure(s)
- destructive/haiku: 1 never-cut failure(s)

**Not gated (2)** - reported so an unevaluated check is not read as a passing one:

- code-fidelity: article rate not gated - only sonnet had a comparable baseline, so a drop cannot be corroborated
- ordered-steps: aux verb rate not gated - only sonnet had a comparable baseline, so a drop cannot be corroborated

