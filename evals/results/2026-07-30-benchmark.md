# Benchmark results — 2026-07-30

> **Superseded by [2026-07-31](2026-07-31-benchmark.md).** This document's central
> readability finding — that laconic violated its own no-arrows rule more than any other
> arm, 16 of the run's 25 violations — was correct, and it was a real defect in the
> shipped rules. That defect is fixed; the re-measured count is 0. This document is kept
> as the record of finding it.
>
> **Its numbers no longer regenerate from `evals/snapshots/results.json` at HEAD.** The
> `laconic` arm in that snapshot was regenerated under the corrected rules. To reproduce
> the tables below, check out the snapshot as of commit `ee36d2c~1`:
>
> ```bash
> git show ee36d2c~1:evals/snapshots/results.json > /tmp/old-results.json
> git show ee36d2c~1:evals/snapshots/judgments.json > /tmp/old-judgments.json
> python3 evals/bench/report.py --no-gate \
>   --results /tmp/old-results.json --judgments /tmp/old-judgments.json
> ```
>
> The gate section below also reflects the pre-correction rate gates, which fired on two
> article-rate cells that were later shown to be false positives. See "What changed in the
> harness" in the 2026-07-31 document.

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
3. **The gate-failure disclosure is corrected, not introduced.** The claim that laconic
   failing its own gate "was not disclosed in the previous version" was itself false, and
   is retracted here: the version before this one disclosed it twice — in prose ("Rate
   gates are unvalidated," which named the failing case/model cells directly) and in a
   `**FAILED (9):**` block in its own full-tables section. What is actually new in this
   revision is threefold: the gate now sums violations per cell (`violations_total`)
   rather than reporting a per-cell median, which is why the failure count differs from
   nine; the `ordered-steps/sonnet` failure has been verified by reading the actual
   response text, not just counted; and the finding has been promoted out of a buried
   table into its own body section, "Laconic fails its own gate," below.
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
8. **A second detector bug, still favoring laconic, is now fixed.** The arrow detector
   corrected in item 2 above matched a markdown bullet marker (`-`, `*`, `+`, `#`) with no
   requirement for a following space, so a bolded prose paragraph opening with `**Request
   A**: ...` was misread as a bullet and skipped whole — arrows inside it never reached
   the count. laconic's responses use exactly that "**Bolded label**: step → step → step"
   construction more than any other arm does, so this bug suppressed violations
   disproportionately in the arm under test, not evenly. A second, related fix corrected a
   fenced-code-removal bug that manufactured false lowercase-sentence-start violations
   (roughly evenly distributed across arms, unlike the arrow bug). Recomputing with both
   fixes raises the run's total from 17 to 25 violations and laconic's own count from 6 to
   16 — the largest of any arm by a wide margin, not a near-tie — and adds a fifth gate
   failure, at `walkthrough/haiku`. See "Readability" and "Laconic fails its own gate,"
   below.

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

**Laconic has the most readability violations of any arm, and a further detector fix is
why this is now visible.** A second arrow-detector bug (see "This revision corrects the
previous publication," item 8) was hiding arrows specifically in laconic's own
`**Bolded label**: step → step → step` paragraphs — a construction that arm's responses
use more than any other's. With both fixes applied, the run totals 25 violations, up from
17: baseline 0, terse-control 5, word-compression 4, laconic 16. Laconic alone accounts
for 64% of the violations in a 320-response run, against a 25%-of-runs share, and two of
its responses are confirmed genuine arrow-chains in running prose, not detector noise. The
word-compression foil, explicitly instructed to "use arrows instead of conjunctions,"
still wrote fewer violations than laconic did unprompted. See "Readability," below.

**Laconic fails its own gate.** `report.py` (sum-based gate, corrected detector) exits 1
against this snapshot: 5 failures, two of them confirmed real arrow-chain violations in
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
intermediate per-case step) gives **sonnet 13.7% shorter** (not 15%) — same direction, a
smaller figure. On Haiku it gives a **different sign**: laconic 598.5 vs baseline 604.0,
laconic **0.9% shorter** (not the per-case-median convention's 5% *longer*). A reader
recomputing this figure directly from `evals/snapshots/results.json` without matching this
convention will get a different number, and on Haiku, the opposite conclusion. This
convention is named here because nothing enforces it implicitly.

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

## Readability: laconic has the most violations, once the detector stops hiding them

The previous version of this document stated: "every arm scored 0.0 violations, the foil
never degraded its prose, the detector is not at fault." **That was wrong in both
directions,** and the version after it — while it corrected the median artifact and one
class of false positive — was still wrong in laconic's favor specifically. Both errors are
recounted here because both shaped a published conclusion this document once made and no
longer makes.

**First correction (previous revision).** The 0.0 was a median artifact — violations
concentrate in a minority of responses per cell, and a median across 5 reps reads as 0.0
even when individual responses have several. And the raw counts behind that median were
themselves wrong: 96% of the symbol hits were false positives, from an arrow detector
firing on markdown bullets (`- step one → step two`, structural, not prose) and numeric
progressions quoted out of a log fixture (`7 → 11 → 14`, data, not a conjunction). That
correction dropped real symbol hits from 269 to 12 project-wide.

**Second correction (this revision).** The bullet check itself was wrong: it matched `-`,
`*`, `+`, and `#` with no requirement for a following space, so a bolded prose paragraph
opening with `**Request A**: ...` was misread as a bullet marker and the entire line —
arrows included — was skipped rather than counted. laconic's responses use exactly that
`**Bolded label**: step → step → step` construction more than any other arm's do, so this
bug suppressed violations disproportionately in the arm under test, not evenly across arms.
A second, unrelated bug in the same detector run — a fenced-code-block removal that left a
lone whitespace-only line behind, which a paragraph-boundary check then read as a sentence
break — manufactured 5 false "lowercase sentence start" violations, split 3-and-2 between
`destructive` (a fence-adjacent continuation, e.g. "...safer sequence: ```sql...``` or if
you do want to actually drop/recreate: ...") and `walkthrough` (a bare filename, `auth.js`,
opening a sentence). Both are now fixed; see `evals/bench/metrics.py` and
`tests/test_metrics.py` for the fixture-level proof for each.

Recomputed from the **same, unmodified** snapshots — no re-generation, no re-judging —
violations across 80 responses per arm:

| arm | haiku | sonnet | total |
|---|--:|--:|--:|
| baseline | 0 | 0 | 0 |
| terse-control | 2 | 3 | 5 |
| word-compression | 0 | 4 | 4 |
| laconic | 8 | 8 | 16 |

25 violations across all 320 responses, up from 17. **This does not read as "no contrast"
anymore.** Laconic accounts for 16 of the 25 (64%) on a quarter of the runs, and two of its
responses are confirmed, not merely detector output:

- `ordered-steps/sonnet` rep 2 wrote a five-arrow runbook in running prose (quoted in full
  in "Laconic fails its own gate," below).
- `walkthrough/haiku` rep 2 wrote two bolded-label paragraphs, each chaining four arrows in
  place of "and then": *"**Request A**: Calls `currentToken()` → token is expired → calls
  `refresh()` → `inFlight` is null → starts the fetch..."* and a matching **Request B**
  paragraph — eight arrows total, exactly the construction the previous bullet-check bug
  was hiding.

A third laconic response (`walkthrough/sonnet` rep 3) contributes 3 more from the same
bolded-label pattern, applied to a quoted hypothetical ("If your mental model was 'make
request → get 401 → refresh → retry'...") rather than a direct instruction — arguably
milder, still counted, still the same construction. The word-compression foil, explicitly
instructed to "use arrows instead of conjunctions," produced 4 violations doing so on
purpose; laconic produced 16 without being asked to. **Laconic does not "win" this axis —
it has the worst count of any arm in this run, driven by a stylistic habit (bolded-label
paragraphs chaining arrows) that the earlier, buggier detector was specifically blind to.**

**Two known detector gaps remain, neither triggered in this run.** `_is_numeric_progression`
decides an arrow is data, not a conjunction, by checking for a digit on both sides — it
cannot distinguish *"the queue climbed 7 → 11 → 14"* (a quoted measurement, correctly
excluded) from *"scale replicas 2 → 4 to fix it"* (an arrow standing in for "to," which the
digit-adjacency check would also excuse). Both read identically to the detector; only the
first is actually data. Separately, `SYMBOLS` matches `->`, `=>`, and `→` but not `⇒`,
`~>`, or `>>`, so any response using one of those instead would score zero for that arrow
regardless of context. Neither gap fired in this snapshot — every response was checked
directly, not just re-scored — but a future run should not assume they can't.

**Rate gates are unvalidated for a related reason, and not just in laconic's favor.** The
spec committed to revising the 0.70 article/aux-verb-rate threshold if `baseline` and
`word-compression` separated by at least 2×, calibrated on the article rate. Observed
separation (median of per-case medians): 1.01× on haiku, 0.96× on sonnet — nowhere near 2×,
and inverted on Sonnet. The threshold was not revised, because there is no valid signal to
revise it against: nothing in this run produces the degraded, article-dropping prose the
gates were built to catch, on any arm, including the foil designed to produce exactly that.
Read the 0.70 thresholds as unvalidated placeholders, not as evidence that laconic's
grammar rate is fine — see "Laconic fails its own gate" for two cells where the threshold
does fire, and where the same skepticism this section applies to the *suppressed* readings
(below the absolute-count floor) is owed to the two readings that *do* fire: `badnews/haiku`
clears the floor at exactly 5.0 (per-rep baseline article counts 4, 3, 6, 5, 5 — a coin-flip
away from being suppressed too) and expects 4.7 articles (0.076 baseline rate × 62 median
laconic words) against 3.0 observed; `conditional/sonnet` expects 8.4 (0.102 × 82) against
5.0 observed, from a baseline ranging 3 to 15 article words per rep. Neither is a stronger
signal than the readings this document declines to gate on; both are reported anyway
because the gate fires on them and suppressing a firing reading with the same reasoning
used to suppress a non-firing one would be the selective skepticism this document exists to
correct.

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
(6 remaining cases × 10 reps-and-models each) — except `word-compression`, which has one
`judge_failed` cell (`destructive/word-compression`, an infrastructure failure, not a
verdict) and so is out of 59, not 60:

| arm | pass | rate |
|---|--:|--:|
| word-compression | 50/59 | 85% |
| terse-control | 50/60 | 83% |
| laconic | 48/60 | 80% |
| baseline | 46/60 | 77% |

Correcting the denominator moves `word-compression` fractionally above `terse-control` (85%
vs 83%, previously misreported as a tie at 83%/83%) — a small reordering within the two
control arms. It does not change the point this table exists to make: **laconic goes from
first to third of four**, and baseline stays last, both unaffected by the correction. This
is not offered as a corrected trap claim either — six cases at n=10 is still too little to
support one, and three of those six carry no signal at all (below). It is offered as proof
that the retracted claim was an artifact of which cases were included, not a robust result
that merely needs a caveat.

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
exits 1 against this exact, unmodified snapshot, with 5 failures:

- `badnews/haiku` — article rate 0.048 vs 70% of baseline 0.076 (baseline had ~5.0 article
  words)
- `conditional/sonnet` — article rate 0.067 vs 70% of baseline 0.102 (baseline had ~10.0
  article words)
- `ordered-steps/sonnet` — 5 readability violations across 5 responses (median displays as
  0.0 — see below)
- `walkthrough/haiku` — 8 readability violations across 5 responses (median displays as 0.0)
- `walkthrough/sonnet` — 3 readability violations across 5 responses (median displays as 0.0)

**The `ordered-steps/sonnet` and `walkthrough/haiku` failures are both genuine, verified by
reading the response.**

All 5 violations in the `ordered-steps/sonnet` cell come from a single response (rep 2 of
laconic/sonnet/ordered-steps), which wrote:

> Rough runbook: generate new key pair → add to JWKS/key store as non-primary → let it
> propagate to all verifiers (respect any cache TTL) → cut over signing to the new key →
> wait out the old token TTL → remove the old key.

Five arrows standing in for conjunctions, in running prose, in one sentence — exactly what
`rules/laconic.md` forbids ("No arrows standing in for conjunctions in running prose").

All 8 violations in the `walkthrough/haiku` cell come from a single response (rep 2 of
laconic/haiku/walkthrough), which wrote:

> **Request A**: Calls `currentToken()` → token is expired → calls `refresh()` →
> `inFlight` is null → starts the fetch, stores Promise in `inFlight`
>
> **Request B** (microseconds later): Calls `currentToken()` → token is still expired →
> calls `refresh()` → `inFlight` is not null → **returns the same Promise** that Request A
> is already waiting on

Two bolded-label paragraphs, four arrows each, none of them bulleted or fenced — running
prose by the same rule. This is the exact construction that the previous revision's
bullet-check bug hid (see "Readability," above): a bolded label followed by a colon, read
as a markdown bullet, dropped from the count entirely. It is real laconic output, in the
committed, unmodified snapshot, and it was invisible to every version of this document
before this one.

The `walkthrough/sonnet` cell's 3 violations come from a third response (rep 3), applying
the same bolded-label-and-arrow pattern to a quoted hypothetical rather than a direct
instruction — see "Readability," above, for the text. In all three cases, the other 4
responses in the cell have zero violations; the per-response median is 0.0, which is why
each is reported as "N violations across 5 responses (median 0.0)" rather than as a median.
These are real findings about the plugin, not a detector artifact: laconic's own rule text
is what these responses broke.

**Three further rate-gate readings were suppressed as artifacts, not as passes**, because
the baseline cell had fewer than 5 article/auxiliary words to begin with:

- `code-fidelity/haiku` — baseline had ~1.0 auxiliary word (of ~49 total words)
- `floor/haiku` — baseline had ~2.0 auxiliary words
- `floor/sonnet` — baseline had ~4.0 auxiliary words

`report.py` enforces an absolute floor (`ABS_COUNT_FLOOR = 5`) alongside the rate
threshold specifically because a ratio of small integers is not evidence: one short,
correct answer with zero auxiliary verbs in it is terse English, not a degraded ratio.
Below the floor, the gate does not fire regardless of what the rate says. This is disclosed
here so "5 failures" is not misread as "these 3 other candidate readings passed on their
merits" — they did not pass; they were excluded as not meaningful. The two rate-gate
readings that *do* fire (`badnews/haiku`, `conditional/sonnet`) are themselves close to that
same floor and are not stronger evidence than the suppressed three — see "Readability,"
above, for why they are reported anyway rather than quietly suppressed too.

This gate result is reported here, in the body of this document, rather than only
discoverable by running the command: laconic — the arm under test — currently fails the
readability/rate gate this benchmark itself defines, on 5 of the case/model cells checked,
two of which are confirmed defects in the plugin's own adherence to its own rule.

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
   symbol-connector and lowercase-sentence-start detectors have now been corrected
   twice, across two revisions of this document — see "Readability" — and two narrow
   gaps remain disclosed there (a numeric-progression check that cannot tell a quoted
   measurement from a digit-adjacent conjunction, and arrow variants `⇒`/`~>`/`>>` the
   regex does not match).
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
| baseline | 0 | 0 |
| terse-control | 2 | 3 |
| word-compression | 0 | 4 |
| laconic | 8 | 8 |

### Responses with >=1 readability violation

| arm | haiku | sonnet |
|---|--:|--:|
| baseline | 0 | 0 |
| terse-control | 1 | 2 |
| word-compression | 0 | 3 |
| laconic | 1 | 2 |

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

**FAILED (5):**

- badnews/haiku: article rate 0.048 below 70% of baseline 0.076 (baseline had ~5.0 article words)
- conditional/sonnet: article rate 0.067 below 70% of baseline 0.102 (baseline had ~10.0 article words)
- ordered-steps/sonnet: 5 readability violation(s) across 5 response(s) (median 0.0) sample: ['→', '→', '→', '→', '→']
- walkthrough/haiku: 8 readability violation(s) across 5 response(s) (median 0.0) sample: ['→', '→', '→', '→', '→']
- walkthrough/sonnet: 3 readability violation(s) across 5 response(s) (median 0.0) sample: ['→', '→', '→']

This is why `python3 evals/bench/report.py --judgments evals/snapshots/judgments.json`
(no `--no-gate`) exits 1 against this snapshot, and why this document was generated with
`--no-gate`. See "Laconic fails its own gate," above, for what these five failures do and
do not mean.
