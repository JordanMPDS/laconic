# Benchmark

440 API calls: 11 cases × 5 reps × 2 models × 4 arms — baseline, a terse-only
control, a synthetic word-compression foil, and laconic. Scored offline on
compression, readability, answer quality, and a deterministic never-cut safety
check. Full method, every honesty note, and every table:
[`evals/results/2026-07-31-benchmark.md`](../evals/results/2026-07-31-benchmark.md),
which describes the archived snapshot the controls still come from.

The laconic arm is `rules_cksum` 1830906901, generated 2026-08-03; the three
control arms are carried unchanged from the 2026-07-30 generation, because no
control carries rules in its system prompt and none of them can have moved.

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | answers correct | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| **laconic** | **-38%** | -1% | **-28%** | **26** | 23 / 30 | 1 / 50 |
| terse-control | -11% | +3% | -13% | 50 | 24 / 30 | 1 / 50 |
| word-compression | +3% | +4% | -13% | 60 | 21 / 30 | 1 / 50 |
| baseline | 0% | 0% | 0% | 60 | 21 / 30 | 0 / 50 |

Every column is reported as measured, on both models and all four arms. The
per-case tables and the method notes behind each number follow.

> **Two columns were corrected on 2026-08-04, both against the plugin.** The
> answer-quality column read 28 / 27 / 28 / **30** and the never-cut column read
> 0 / 1 / 0 / 0, because two case criteria asserted things their technologies do
> not do. `destructive` said `ON DELETE CASCADE` governs table drops
> ([#18](https://github.com/JordanMPDS/laconic/issues/18)) and `stale-cache`
> said a request `Cache-Control: max-age=3600` tells a shared cache to serve
> hour-old responses ([#39](https://github.com/JordanMPDS/laconic/issues/39)).
> Both were verified against the real software — PostgreSQL 16 and Varnish 7.4 —
> and rewritten. Laconic no longer leads the quality column and no longer holds
> a clean never-cut sheet. Full accounts:
> [`destructive`](../evals/results/2026-08-04-destructive-criterion.md),
> [`stale-cache`](../evals/results/2026-08-04-stale-cache-criterion.md).

**The laconic arm was regenerated on 2026-08-03** under the current rules. Every
laconic figure on this page moved, and each one moved in laconic's favour. Read
[The 2026-08-04 regeneration](#the-2026-08-04-regeneration) before quoting any of
them — one of the four columns is attributable to a rule change and three are
not, and the same regeneration cost laconic its largest per-case compression
result.

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
| `floor` | 201 | 220 | 71 | **65%** |
| `silent-success` | 1105 | 947 | 580 | **48%** |
| `code-fidelity` | 307 | 315 | 191 | **38%** |
| `decision` | 839 | 786 | 534 | **36%** |
| `conditional` | 908 | 981 | 688 | **24%** |
| `ordered-steps` | 1329 | 1630 | 1059 | **20%** |
| `fail-open` | 1265 | 1234 | 1081 | **15%** |
| `stale-cache` | 1660 | 2245 | 1593 | 4% |
| `walkthrough` | 3701 | 3682 | 3666 | 1% |
| `badnews` | 435 | 414 | 439 | -1% |
| `destructive` | 2336 | 2775 | 2542 | **-9%** |
| **median** | **1105** | **981** | **688** | **38%** |

`destructive` is the one Sonnet case that gets meaningfully longer, which is the
design working: naming exactly what a `DROP TABLE` affects is never-cut content,
so laconic has nothing to trim there. `stale-cache` sits at 4% for the same
reason — it is the case that needs a mechanism explained, and a requested
explanation is not something laconic cuts.

`walkthrough` is the case that changed. It saved 56% in the archived snapshot
and saves 1% here, on the same prompt, and it is the case the arrow-prohibition
revisions were aimed at. Writing "the request calls `currentToken()`, finds the
token expired, and calls `refresh()`" instead of chaining the same three states
with arrows costs tokens, and `walkthrough` is nine steps of exactly that. The
median improved and the suite's largest single compression result disappeared,
in the same regeneration.

<details>
<summary><strong>Haiku 4.5</strong></summary>

| case | baseline | terse-control | laconic | saved |
|---|--:|--:|--:|--:|
| `badnews` | 469 | 432 | 442 | 6% |
| `floor` | 266 | 236 | 251 | 6% |
| `walkthrough` | 1228 | 1008 | 1163 | 5% |
| `fail-open` | 922 | 843 | 891 | 3% |
| `silent-success` | 775 | 732 | 753 | 3% |
| `stale-cache` | 1246 | 1355 | 1203 | 3% |
| `conditional` | 956 | 1017 | 951 | 1% |
| `destructive` | 711 | 791 | 704 | 1% |
| `ordered-steps` | 653 | 636 | 653 | 0% |
| `decision` | 522 | 506 | 549 | -5% |
| `code-fidelity` | 425 | 421 | 530 | -25% |
| **median** | **711** | **732** | **704** | **1%** |

Haiku's result depends on the aggregation convention, so no compression claim is
made for it in either direction. The table above is a median of per-case medians
(1%); a flat median over the 55 raw runs gives 731 against 714, a 2% cut. The
sign flipped from the archived snapshot's -1%, which is the point: this is a
number that moves with the estimator and the sample, and nothing should be built
on it. Sonnet is where the compression claim lives.

</details>

On Sonnet, laconic's max (968) sits below baseline's median (1105), so the gap is
not one or two short outliers. Its stdev is 209, second-lowest of the four behind
`word-compression`'s 195 — in the archived snapshot it was 175 and the tightest
of the four. `report.py`'s noise floor tracks this number and moved with it, which makes
the loop's accept gate stricter than it was.

## Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | violations | responses affected (of 110) |
|---|--:|--:|
| baseline | 60 | 16 |
| terse-control | 50 | 12 |
| word-compression | 60 | 22 |
| **laconic** | **26** | **9** |

Laconic is the cleanest arm on violations and is not clean. Nine responses of
110 break its own no-arrows rule, and `report.py` exits 1 on six case/model
cells because the gate allows none: `walkthrough` carries 17 of the 26 arrows,
`silent-success`/haiku 3, `ordered-steps` 4, `destructive`/sonnet 2.

### The 2026-08-04 regeneration

The laconic arm above is the one generated on 2026-08-03 under `rules_cksum`
1830906901, which is the rules this repository ships today. Before it, the
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

The three `quality` cases each present a fixture with a buried mechanism and a
plausible decoy, and ask a diagnostic question. The criterion is whether the
response names the mechanism, and every word of it comes from the fixture rather
than from `rules/laconic.md` — which is what makes these the only cases in the
suite from which a comparison between arms is legitimate.

| arm | answers correct (of 30) |
|---|--:|
| baseline | 21 |
| terse-control | 24 |
| word-compression | 21 |
| **laconic** | **23** |

> **Corrected 2026-08-04.** This table read 28 / 27 / 28 / **30** until
> `stale-cache`'s criterion was rewritten. The old trap required a passing
> answer to name the client's `Cache-Control: max-age=3600` **request** header
> as the reason the shared cache serves an hour-old response, which is not what
> a request `max-age` does — verified against Varnish 7.4 in
> [`evals/results/2026-08-04-stale-cache-criterion.md`](../evals/results/2026-08-04-stale-cache-criterion.md),
> closing [#39](https://github.com/JordanMPDS/laconic/issues/39). Every arm was
> being graded on the wrong answer, so every arm's figure falls, and laconic no
> longer leads the column.

**Laconic's answers were as often correct as baseline's**, 23 against 21, while
being 15% shorter on Sonnet across those same three cases. Fisher's exact
two-sided p = 0.77 — read it as no detectable difference, not as a win. The arm
that scores highest is `terse-control` at 24, by one response over laconic, and
that gap is noise by the same test.

This is a coarse instrument. Two of the three cases are at ceiling — every arm
passes `fail-open` and `silent-success` 10 of 10 — so the entire column is
`stale-cache`, where every arm is near the floor: 1, 4, 1 and 3 of 10. A single
hard case carrying a whole quality column is a limit of the case set, not a
result. Read the column as ruling out a large regression and nothing finer.

That `stale-cache` is hard for every arm is itself measured rather than
inferred: the same cell regenerated 20 times under unchanged rules passes 7
times, and four separate draws of it — at three different rule revisions — do
not differ from one another at any conventional level.

## Cost, reported net

The injected rules cost tokens of their own, so the net per-call cost sits
slightly above baseline on both models even where output tokens drop.

| median USD per call | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0165 | 0.0716 |
| laconic | 0.0196 | 0.0781 |

Each generation is one `--append-system-prompt` call with a single question, not
a multi-turn session, so this **overstates** what a real session pays once the
first turn's cache write becomes a cache read on every turn after it.

## Never-cut check

The never-cut contract is checked on the 50 responses per arm that carry a
keyword list by design. Laconic fails **1** of them on the current snapshot, as
do `terse-control` and `word-compression`. `baseline` fails 0.

> **Corrected 2026-08-04.** This section read "laconic fails 0" until
> `destructive`'s keyword list gained `sessions`. Dropping `users` is blocked by
> the `sessions` foreign key exactly as it is by the `invoices` one, so a
> response naming only `invoices` has left out half the blast radius, and the
> old two-keyword list could not see that. The new miss is
> `destructive`/haiku rep 3. Full account:
> [`evals/results/2026-08-04-destructive-criterion.md`](../evals/results/2026-08-04-destructive-criterion.md).

The archived snapshot had 2 laconic failures, and both were read and confirmed at
the time: one `destructive` response pointed at foreign keys generally rather
than naming the two tables in the fixture, and one `conditional` response stopped
short of diagnosing the leak. The `destructive` one was a rule defect — that
response never opened the schema it was pointed at, and the rule said "including
exactly what will be affected" without saying *from the material in front of
you*. The bullet was changed to demand the read.

That fix was reported as confirmed by a re-run coming back "clean at 10 of 10"
([`evals/results/2026-07-31-destructive-recheck.md`](../evals/results/2026-07-31-destructive-recheck.md)).
**That number does not survive the corrected criterion: the same ten responses
grade 4 of 10, with all five haiku responses failing.** The #3 edit fixed the
response that never opened the schema. It did not fix haiku on this case, and
the recheck could not tell, because the criterion it used asserted a cascade
`DROP TABLE` does not perform. The `conditional` failure was left alone for want
of a textual argument.

So one of the two failures had a fix landed against it and the other did not,
and the regenerated arm shows 1 rather than 2. That is consistent with the fix
working and equally consistent with 2-in-50 being rare enough to miss: 2/50
against 1/50 is Fisher p = 1.0. The rules loop has since failed
`conditional`/sonnet on never-cut in two separate rounds
([`round-03.md`](../evals/results/loop/round-03.md)), which is the better
evidence that the case remains close to the line.

`report.py` still exits 1 against the committed snapshot, now on readability
alone: six case/model cells carry arrows and the gate allows none.

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
- **The headline compression figure has been 28%, 33% and now 38% on Sonnet.**
  28% to 33% came from growing the case set from 8 to 11; 33% to 38% came from
  regenerating the arm under current rules, one sample against another. None of
  the three is a measurement of an improvement over the one before it.
- **Never-cut coverage is 50 of 110 responses per arm.** Six cases carry an
  empty keyword list and are not checked — three were emptied once an earlier
  `"if"` keyword turned out to match "different", "specify" and "identify", and
  the three quality cases turn on mechanisms with several correct phrasings, so
  any required substring would fail correct answers.
- **The snapshot is mixed, now for every case.** The laconic arm was generated
  on 2026-08-03 and all three control arms are carried from 2026-07-30, so
  treatment and control are never sampled at the same time. This is deliberate —
  no control carries rules in its system prompt, so a rule change cannot move
  one — but it does mean any drift in the models themselves lands entirely on
  the treatment arm.
- **The laconic arm is a snapshot the rules loop generated for another purpose.**
  It is round 01's baseline, generated as the control half of a loop round before
  this regeneration was contemplated, which is why it was not selected for its
  numbers. It is the only sample that exists under the current rules, and
  re-drawing one would buy a different draw of the same distribution, not an
  independent instrument.
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
  28% on Sonnet against the token figure's 38%. That ordering reversed with the
  regeneration — on the archived snapshot the same two estimators read 45% and
  33% — because the current rules trade arrows for conjunctions and put prose
  words back into the answer. The token figure stays the headline; it is no
  longer the conservative one, and both are published for that reason.

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
