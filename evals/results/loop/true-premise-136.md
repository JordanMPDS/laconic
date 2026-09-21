# The closed question whose premise is true: the instrument [#136] and [#305] both asked for

**Registration. Nothing below the results line has been computed.** This file,
the six pilot cases it describes, their scorer and the layout test that holds
the pairs together are committed in one commit before any generation, following
[round 38](round-38.md), [`register-inheritance-136.md`](register-inheritance-136.md)
and [`closing-recap-305.md`](closing-recap-305.md).

**This is not a round.** It proposes no rule edit, takes no row in
[`LEDGER.md`](LEDGER.md), and spends no [`candidate-due.sh`](../../../tools/candidate-due.sh)
allowance: round 70 carried a candidate, so round 71 is still unregistered and
may go either way. What this buys is an instrument, and the reason to buy it
before the next candidate round rather than after is that two open issues now
name the same missing case and neither can be tested without it.

Reproduce every number below with:

```sh
python3 evals/pilot/score_premise.py evals/snapshots/loop/true-premise-*.json
```

> **Amendment, 2026-09-21 ([#319]).** `verdict()` has been widened by four
> alternations, registered and measured in
> [`verdict-widening-319.md`](verdict-widening-319.md). **Every claim this
> document makes survives unchanged**, because the widening touches
> `DENY_ANYWHERE` alone and `AFFIRM` is consulted first, so no confirm count can
> move: 180 of 180 settled responses confirming the premise, and the lowest
> settled-case agreement of 100.0%, both stand exactly.
>
> Five `unsettled-*` rows of Bar 2 gain denials out of the `unclear` column —
> `unsettled-retention`/sonnet baseline 15/20 to **19/20**,
> `unsettled-failover`/haiku baseline 14/15 to **15/15**,
> `unsettled-rounding`/haiku laconic 14/15 to **15/15**,
> `unsettled-rounding`/sonnet baseline 17/20 to **20/20**, and
> `unsettled-rounding`/sonnet laconic 19/20 to **20/20**. The figures below were
> computed at **`b3e2d92`** and reproduce from it. One sentence below is now
> wrong: the selftest asserts twenty shapes, not eleven.

> **Amendment, 2026-09-21 ([#321]).** `verdict()` has been widened a second
> time, by five alternations registered and measured in
> [`verdict-residual-321.md`](verdict-residual-321.md). **No row of this
> document moves**, in either direction: none of that widening's six recovered
> runs is in a `true-premise-*` snapshot, and this document's own two
> still-`unclear` runs are in the one shape a phrase list cannot reach. Every
> Bar 2 figure stands as [#319] left it. The sentence about the selftest moves
> again: it now also asserts [#321]'s six shapes, the contrast shape it
> deliberately refuses, and the confirmation that shape becomes when "Yes" is
> put in front of it.

## What both issues ask for, in the same words

[#136]'s last comment, closing out the third of three proposals:

> **What would open it is one case** — a closed question whose premise is
> **true**, where a bare confirmation is the complete answer, so that any
> surplus is unrequested by construction and the fixture decides completeness
> before a response exists. No labeller, no redundancy judgement.

[`closing-recap-305.md`](closing-recap-305.md) arrives at the same thing from
the other side, having killed [#305]'s item 1 before round 71 could be built on
it:

> **What would make item 1 testable.** Not a better regex. Either the judged
> verdict above, or a case whose fixture makes the correct closing *knowable* —
> an answer where the right last paragraph is empty, so a closing paragraph of
> any kind is the defect and no semantic judgement is needed to say so.

The judged route is the one that just failed. [#155]'s consensus pass lifted the
oracle ceiling to 89.7% precision and failed its registered mechanism bar, and
its registration committed in advance to redirecting rather than opening a
fourth attempt. So the route left is the fixture, and it is the same fixture for
both issues.

## Why the suite cannot already do this

All thirteen closed questions in the scored suite carry a false or partial
premise. [`closed-question-136.md`](closed-question-136.md) measured what that
costs, over 1,953 de-duplicated responses:

> **The false positives are one shape, and it is the suite rather than the
> cutoff.** All thirteen closed questions here carry a false or partial premise,
> so a complete answer is a denial plus the qualification the trap requires — 80
> to 145 words of content with nothing deletable in it.

A detector on those cells reads 30.0% precision strict, or 63.3% if every
redundant restatement counts, and the distance between those two numbers is a
redundancy judgement — exactly the judgement [#155] is parked on. A false
premise is a forcing function: it makes the answer long *correctly*, and no
count endpoint can see past it.

## The instrument: three decision records, two premises each

Six single-turn cases under `evals/pilot/`, so nothing joins the scored suite,
`cases_cksum` does not move for any future round, and no fatal counter gains an
unseeded cell.

| case | premise | a complete answer is |
|---|---|---|
| `settled-retention` | true | a confirmation |
| `settled-failover` | true | a confirmation |
| `settled-rounding` | true | a confirmation |
| `unsettled-retention` | false | a denial and the record's version |
| `unsettled-failover` | false | a denial and the record's version |
| `unsettled-rounding` | false | a denial and the record's version |

Each `unsettled-*` case shares its twin's fixture **by symlink**, opens by
reading the same file, and ends in the same `correct? Don't edit anything.`
form. The only thing that varies is whether the premise the user states matches
the record. `tests/test_evals_layout.sh` holds the three pairs to that contract,
so a later edit to one half fails the suite rather than silently turning the
contrast into a comparison of two different questions.

Each fixture is a decision record that states three things: the conclusion, the
reasoning that produced it, and that the decision was accepted, closed, and its
argument recorded in full. The third part is load-bearing and it is not an
instruction to the reader — it is a recorded fact about the decision, so an
answer that proposes a remedy contradicts the record rather than disobeying it.
That distinction is what keeps this a quality trap rather than a test of
whether the model follows orders in a fixture.

**Why a decision record and not a configuration value.** A flat fact — the port
is 8080, correct? — has no reasoning for an unruled arm to re-derive, so both
arms answer in four words and the case measures nothing. The surplus this is
built to see is re-derivation, which is the [#136] harm as reported: a
confirmation answered by rebuilding the argument the user already has. A record
with a three-clause rationale is the smallest fixture that offers that
re-derivation and still admits a one-word correct answer.

## Endpoints, all deterministic

`evals/pilot/score_premise.py`, on prose words by `metrics.score` and on a
first-sentence verdict detector. No judge call is bought and no label is
written, which is the point of the case: the fixture decides completeness
before a response exists.

The detector reads the response's **first sentence** and returns `confirm`,
`deny` or `unclear`. `python3 evals/pilot/score_premise.py --selftest` asserts
its decisions on eleven shapes, including the one that would break a
whole-response scan — a denial that goes on to quote the user's own wording
back.

### Bar 1, the arm contrast

> Over the six settled cells (3 records x 2 models), `laconic` answers the
> true-premise closed question in fewer prose words than `baseline`.

Per-cell two-sided permutation of the arm label over per-run medians at 200,000
resamples, seed 136, combined across cells by `metrics.sign_test`. Six cells is
the minimum a two-sided exact sign test can reach alpha on, at 6 of 6,
p = 0.031.

**A family that does not separate the arms cannot host a rule candidate**, and
that is what this bar decides. It is not a claim about the rules: `laconic` is
the short arm by construction on every case in the archive, and a failure here
says the case is at a floor, not that the plugin stopped working.

### Bar 2, premise validity

> On every settled cell, at least **90%** of responses confirm the premise, in
> both arms.

This is the bar that can kill the fixture. A premise the model argues with is
not a true premise however carefully it was written, and a case where the
correct answer is contested cannot say that surplus is unrequested. Below 90% on
any settled cell the case is **rejected rather than patched**: a fixture edited
until the model agrees with it is a fixture tuned on its own measurement.

The twin's mirror — the share of `unsettled-*` responses that deny — is reported
beside it and is a disclosure rather than a bar. A twin that fails to provoke a
denial is a broken control, and this document will say so.

### Headroom, reported whichever way it lands

The share of settled `laconic` responses above **40** and above **80** prose
words, pooled and per cell, with a 95% Wilson interval. Forty is the rule's own
standard restated as a count — *"A yes/no question gets a word or a line"* —
and eighty is [`closed-question-136.md`](closed-question-136.md)'s cutoff, so
the two numbers are comparable to the only other measurement of this shape.

**This is the deliverable and it has no bar.** A high rate makes the case an
instrument a later candidate round can be powered from. A rate near zero is the
finding that the reported harm does not reproduce on a benchmark question whose
premise is true — which would be the first evidence in the cluster that [#136]'s
failure needs the session, not the question.

### The premise contrast

Within `laconic`, settled against unsettled on the same record and model, six
cells, same test. This is what licenses the claim that premise truth is what the
family manipulates. The archive's false-premise figures — laconic median 62
prose words against baseline 160.5 — are not used for this, because they were
recorded in another CLI era and [round 37](round-37.md) measured a syntactic
behaviour moving 4.7x in five days at byte-identical rules.

## The buy, staged, and the looks declared before the first one

1. **A shape look.** 5 reps, sonnet only, both arms, all six cases, into
   `true-premise-shape.json`. Every response is hand-read and tagged by shape;
   **no p-value is computed from it and none may be quoted.** If it shows the
   fixture is argued with, or that the verdict detector mis-reads a shape the
   cases actually produce, the fix lands before the main pass is bought and
   these runs are discarded with the case text that produced them.
2. **The main pass.** 15 reps a cell, both models, both arms, all six cases,
   `--rep-offset 5` so it shares no generation key with the shape look. 360
   generations, four shards, `--concurrency 4` declared on each.

**One look, on the main pass.** The shape look decides nothing the bars decide,
so no alpha is spent on it, and its runs are excluded from every test above.
That is the whole reason it is offset rather than extended: reusing the runs a
fixture decision was made on would let the inspection into the sample.

## Pre-mortem, registered

The way I expect this to fail is **bar 2 on `settled-rounding`**. It is the
record whose conclusion is a consequence rather than a decision — the one-cent
difference *follows* from per-line rounding — and a model that sees a
consequence stated as a premise has an easy hedge available: "yes, though the
difference is a symptom of the rounding rule rather than the rule itself." That
opens `unclear` rather than `confirm`, and three or four of those in a
fifteen-run cell put it under the bar. If it happens, the honest reading is that
two of three records carry the instrument and the third does not, and the
family ships as two pairs or not at all — not that the bar was too strict.

The second way is headroom: both arms answer "yes" in four words, the rate above
40 is near zero in both, and the case is real but has nothing in it for a rule
edit to move. That is a publishable answer to [#136] and a dead end for [#305]'s
item 1, and it is the outcome that would most change what the cluster does next.

## Where the design came from

Sharpened by `tools/consult.sh`; two of three targets answered, and both changed
what was built. Codex was asked and did not answer inside the timeout.

- **DeepSeek** corrected the premise of the question I asked. I had framed
  headroom as a trade against how arguable the fact is; it pointed out that
  headroom comes from the **reasoning chain in the fixture**, because that is
  what an unruled arm re-derives, and that the word endpoint convicts an
  unforced clause whether or not a reader would have called it helpful. It
  supplied the sentence the records now carry — settled **and its reasoning
  complete as written** — on the ground that `settled` alone closes the remedy
  and not the re-derivation, which is the larger surplus and the literal [#136]
  harm. It also named the failure mode this design had not priced: a true
  premise removes the forcing function to read, so bar 2 can pass vacuously on
  a model that simply affirms. The reading rate is reported per cell for exactly
  that reason. It argued the twin costs nothing — 15+15 and 30+0 are the same
  360 generations — and that is why the twin is balanced rather than
  diagnostic.
- **Kimi** proposed the decision-record shape the three fixtures use, with the
  rationale, the alternatives considered and the accepted cost written out, and
  warned that a flat configuration value collapses both arms. It asked for the
  quotation diagnostic, which is in the scorer: the share of responses carrying
  a verbatim ten-word run from the fixture, so a word count inflated by
  quotation is visible rather than silent. Its imperative version of the
  settled sentence — *"Do not revisit or propose an alternative"* — was **not
  adopted**: an instruction in a fixture makes the absence of a remedy a
  measurement of instruction-following, which is the contamination
  `tests/test_evals_layout.sh` rejects traps for. The records state the decision
  is closed as a recorded fact instead.
- Both independently said to hand-read a small sample before committing the
  full buy. That is the shape look, and it is the project's own standing method:
  every detector document in this cluster did the hand-read before the buy, and
  it caught the shape that broke the measurement each time.

---

## Results

*Nothing above this line was computed. Everything below it was.*

### The shape look, 2026-09-20: the instrument behaves, and the detector did not

60 runs, sonnet, both arms, all six cases, 5 reps, in
`evals/snapshots/loop/true-premise-shape.json`. **No p-value is computed from
it and none is quoted.** Its runs are reps 0 to 4 and the main pass starts at
rep 5, so nothing here enters a registered test.

| | settled | unsettled |
|---|---|---|
| agreed with the premise as stated | **30 of 30** | 0 of 30 |
| denied it | 0 of 30 | **30 of 30** |
| opened the fixture | 30 of 30 | 30 of 30 |
| mutating runs | 0 | 0 |

Median prose words, sonnet, settled cells: `baseline` 166, 111 and 77 against
`laconic` 51, 26 and 28. The unsettled twin runs 149, 111 and 103 against 80,
39 and 66.

**What the hand-read found, which is what this look is for.** Every settled
`laconic` response is a confirmation followed by the record's own reasoning
quoted back — *"Correct. `events_raw` is gone after 14 days
(`prune_events_raw`); the quarterly report reads `events_daily`, retained 13
months, because its three measures ... are all derivable from the rollup."* Not
one response proposed a remedy, argued with the record, or treated the closed
decision as open. So the surplus this family carries is **re-derivation**, which
is [#136]'s reported harm in its plainest form, and it is now countable without
a labeller: everything after the first word.

Two things the pre-mortem got wrong, recorded because a pre-mortem that is only
consulted when it was right measures nothing. `settled-rounding` was named as
the likeliest bar-2 failure and read 5 of 5 confirmations on sonnet. DeepSeek's
non-reading failure mode — a model that affirms a true premise without opening
the file, passing bar 2 vacuously — did not occur at all: 60 of 60 runs read.

**The detector did fail, and it was fixed here rather than after the buy.**
Seven of the 30 unsettled responses opened *"Not correct."* or *"I read it —
your understanding is backwards."*, which the first draft returned `unclear` on.
Both shapes are now in `verdict()` and in its selftest, and the phrase search
that catches the second runs after the affirm test so a confirmation that says
*"it would not be correct to ..."* is unaffected. Re-scored, the shape look
reads 60 of 60 correctly. This touched no case text, so the shape look's runs
remain valid evidence about the cases the main pass generates.

### The main pass, 2026-09-20: 360 runs, one CLI release, nothing failed

15 reps a cell from rep 5, both models, both arms, all six cases, four shards at
`--concurrency 4`, in `evals/snapshots/loop/true-premise-main-{1,2,3,4}.json`.
360 of 360 generations succeeded, **360 of 360 opened the fixture**, and no run
mutated anything, so no cell is refused under [#131] or [#209]. Every run is on
CLI **2.1.278** and `evals/bench/release.py` reports no unreadable span and no
arm imbalanced across a release, which is the first round document in this
cluster that needs no era caveat at all.

### Bar 1: passed, 6 of 6 cells

| settled cell | `baseline` median | `laconic` median | permutation p |
|---|--:|--:|--:|
| `settled-retention`/haiku | 90.0 | 88.0 | 0.774 |
| `settled-retention`/sonnet | 108.0 | 24.0 | 0.00021 |
| `settled-failover`/haiku | 135.0 | 108.0 | 0.0049 |
| `settled-failover`/sonnet | 159.0 | 48.0 | 0.00001 |
| `settled-rounding`/haiku | 138.0 | 110.0 | 0.0162 |
| `settled-rounding`/sonnet | 80.0 | 32.0 | 0.00006 |

**6 of 6 lower, two-sided sign test p = 0.03125.** Pooled median 122.5 to 62.5,
disclosure only. The family separates the arms, so it can host a rule candidate.

### Bar 2: passed, and by more than the bar asks

**180 of 180 settled responses confirm the premise** — every cell, both arms,
both models, no `unclear` and no `deny`. The bar was 90% and the lowest cell is
100%.

A first-sentence detector can be fooled by a response that opens *"Yes"* and
corrects in the next clause, so the confirmations were swept for a correction
marker in their opening 400 characters — *backwards, the opposite, however, one
correction, caveat, clarification, to be precise, though*. **0 of 180 flagged.**
The premises are not being agreed with under protest; they are simply true, and
every arm reads them that way.

**The twin works and its detector is the weaker half.** Of 180 unsettled
responses, 162 deny, 14 read `unclear` and 4 read `confirm`. Hand-read, the 14
are denials the pattern does not cover — *"That's backwards."*, *"That's the
opposite of what the doc says."*, one bare correction with no marker at all, and
one *"Got it."* that answers nothing. All four `confirm` calls are on
`unsettled-retention`/haiku and all four open *"Yes, that's correct"* and then
contradict the premise in the following clause: *"Yes, with one clarification:
the quarterly report reads `events_daily`, **not** `events_raw`."* Those are
detector false positives rather than model errors, they are 4 of 180 = 2.2%, and
they can only arise where the premise is false. Nothing the bars rest on is
affected.

### Headroom: the finding, and it is entirely a model split

| settled cells | above 40 words | above 80 words | median |
|---|--:|--:|--:|
| haiku `baseline` | 45/45 = 100.0% | 42/45 = **93.3%** | 128.0 |
| haiku `laconic` | 45/45 = 100.0% | 34/45 = **75.6%** [61.3, 85.8] | 98.0 |
| sonnet `baseline` | 45/45 = 100.0% | 34/45 = 75.6% | 116.0 |
| sonnet `laconic` | 14/45 = 31.1% | **0/45 = 0.0%** [0.0, 7.9] | 32.0 |

Eighty words is [`closed-question-136.md`](closed-question-136.md)'s cutoff, so
these rates are directly comparable to the only other measurement of this shape.
On a question whose complete answer is one word:

- **sonnet under the rules never once exceeds it.** 0 of 45, upper bound 7.9%,
  against its own simultaneous control at 34 of 45.
- **haiku under the rules exceeds it three times in four.** 75.6% against a
  control at 93.3% — the rules move it 17.7 points and leave it answering a
  yes/no question at a median of 98 prose words.

This is [#136]'s report reproduced in the benchmark for the first time, on a
question where no redundancy judgement is needed to call the surplus surplus.
A specimen, `settled-retention`/haiku/`laconic`, 98 words, in full:

> Yes, that's correct. The quarterly report reads `events_daily` because
> `events_raw` is deleted 14 days after ingest by the `prune_events_raw` job,
> so past-quarter data is no longer available in the raw table.
>
> The document also notes this works because the three report measures — active
> accounts, billable events, and p95 latency — are all computable from the daily
> rollup, which keeps the necessary per-account counts, billable counts, and
> t-digests. So the quarterly numbers are identical whether they come from raw
> or rolled-up data. The 14-day retention on raw was chosen because that's what
> incident review needs (longest investigation reached back 9 days) while
> balancing storage costs.

Every word after *"Yes, that's correct"* is the record's own rationale returned
to a user who has just said they read it. Nothing in it is wrong, nothing is a
remedy, and nothing was asked for. That is the whole construct: **surplus by
construction rather than by judgement.**

### The premise contrast: does not separate as registered

| `laconic`, same record and model | unsettled median | settled median | permutation p |
|---|--:|--:|--:|
| retention/haiku | 80.0 | 88.0 | 0.463 |
| retention/sonnet | 37.0 | 24.0 | 0.0035 |
| failover/haiku | 145.0 | 108.0 | 0.00024 |
| failover/sonnet | 81.0 | 48.0 | 0.00025 |
| rounding/haiku | 112.0 | 110.0 | 0.848 |
| rounding/sonnet | 66.0 | 32.0 | 0.00004 |

**5 of 6 lower, sign test p = 0.21875.** The registered test does not separate,
and at six cells only a clean sweep could have: this is the power the scope
was known to have, not a surprise.

**The stratified reading below is post-hoc and is disclosure, not a result.**
The model split is what the cells were built to carry, but the claim that the
two models differ *from each other* was not registered and is not tested here.

| `laconic`, settled against unsettled, pooled within model | unsettled | settled | permutation p |
|---|--:|--:|--:|
| sonnet | 61.0 | 32.0 | < 0.00001 |
| haiku | 113.0 | 98.0 | 0.061 |

Sonnet spends about half as many words when the premise is true as when it is
false. Haiku spends about the same either way. Read with the headroom table,
that is one coherent picture and it is the useful one: **the surplus on haiku is
not responsive to what the question needs**, which is why a false-premise case
could never have exposed it — on those cases the words are required, and haiku
producing them looks like correctness.

## What this buys the two issues that asked for it

**An instrument, with a measured fire rate, on the cells where the harm is.**
A candidate round on [#136] or [#305]'s item 1 now has a target that needs no
labeller: the share of settled `laconic` responses above 80 prose words, 75.6%
[61.3, 85.8] on haiku, against a simultaneous control. [#155]'s redundancy
verdict is not on the path to it.

**And a scope that is decided rather than guessed.** Such a round is a haiku
round. On sonnet the rate is 0 of 45 with an upper bound of 7.9%, so there is
nothing there for an edit to move, and a round scoped to both models would spend
half its generations on a cell at the floor. That inverts the loop's usual
sonnet-first habit, and the reason is specific to this endpoint rather than
general.

**What is not claimed.** Nothing here says a rule edit can move the haiku rate,
and nothing here is a rule edit. The one previous attempt on this paragraph
family — round 64's worked closed question — moved one cell of three and
reverted.

## The cases stay in `evals/pilot/` for now

Promotion into `evals/cases/` changes `cases_cksum` for every future round and
adds six cells that the round-21 baseline has no runs for, which every fatal
counter would read as a rise rather than as unchanged. That is a separate
decision with a seeding cost attached, and this pilot does not take it. Any
round can reach these cases today with `--cases-dir evals/pilot`, which is how
both passes above were generated.



[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#305]: https://github.com/JordanMPDS/laconic/issues/305

[#319]: https://github.com/JordanMPDS/laconic/issues/319
[#321]: https://github.com/JordanMPDS/laconic/issues/321
