# `tools`: what 5,557 recorded tool lists say, and the one case that answers [#116]

**The registration below was committed in `b1ea65b`, before its batch ran.** The
result section is the only thing added afterwards.

[#142] made `run.py` invoke the CLI with `--output-format stream-json`, so every
run since round 27 carries a `tools` list: the tool names that response actually
invoked, in order. The loop skill has been saying this since:

> **Nothing scores that list yet, and a round you run does not gate on it.** The
> field is absent on every round below 27, so a read-versus-write metric built
> from it today could not be re-scored against a single stored round... The list
> accumulates until enough rounds carry it to say what a normal tool mix looks
> like.

Forty-one snapshots and **5,557 runs** now carry it. This is that survey.

## What the corpus holds

| arm | runs | | model | runs |
|---|--:|---|---|--:|
| laconic | 4,602 | | sonnet | 3,977 |
| baseline | 955 | | haiku | 1,140 |
| | | | opus | 440 |

**Four tool names appear. That is the whole vocabulary.**

| tool | calls | runs using it | share of runs |
|---|--:|--:|--:|
| `Read` | 6,978 | 3,240 | 58.30% |
| `Bash` | 5,315 | 3,196 | 57.51% |
| `Edit` | 81 | 81 | **1.46%** |
| `Agent` | 8 | 8 | 0.14% |

No `Write`, no `Glob`, no `Grep`, no `WebFetch`. `Bash` is a read in substance
almost everywhere — round 33 already recorded a run reading its fixture through
`cat`.

**A read-versus-write metric cannot be built on this suite.** The write side is
81 calls, and all 81 are on one case. That is the answer to the loop skill's
open question, and it is a negative one: waiting for more rounds will not help,
because the suite does not ask the model to write.

## Two instrument results, free

**1. `one_turn` is a 99.95% accurate proxy for "called no tool", and its
exception has a name.** The counter is computed from `num_turns == 1`, and
nothing had checked that against the tool list:

| | runs |
|---|--:|
| empty tool list | 1,716 |
| `num_turns == 1` | 1,719 |
| both | 1,716 |
| empty list but `num_turns > 1` | **0** |
| `num_turns == 1` but a non-empty list | **3** |

The three exceptions are all the same thing: a run that called `Agent`. Work
done inside a subagent does not raise the parent's `num_turns`, so one of them
reports `num_turns == 1` while its own tool list holds **21 entries**, five of
them `Read`. `one_turn` scores that run as never having opened a file.

**All eight `Agent` calls are haiku, and all eight are laconic.** `one_turn` is
already restricted to sonnet by its own rule 2 — *"the proxy leaks on haiku"* —
so the gate as written cannot see this. What is new is a second, previously
unnamed form of that leak: not a short answer quoting fixture content, but a
delegated one whose reading is invisible to the counter. The scoping rule that
was justified on other grounds turns out to cover it.

**2. Nothing in the archive contradicts `turns`.** Its grounded-stratum
definition reads action volume, and with `Edit` at 1.46% the volume it measures
is overwhelmingly reading.

## The case that answers [#116]

[#116] reports a question answered correctly and then substantiated with
unrequested work:

> The correct response is roughly one line: yes, plus one caveat. Instead the
> model replied "Yes, that's exactly right. Let me put real numbers on it." and
> started running analysis over the project's data.
>
> The prose was terse. The behavior was not. Laconic caught neither, because it
> was never pointed at this.

All 81 `Edit` calls in the archive are on **`conditional`**, whose prompt is:

> Our Postgres connection pool keeps hitting max — pool.log has the last hour and
> db.js is where it's configured. **Should I raise the pool size?**

That is an interrogative. The deliverable is a recommendation. On 21.3% of runs
the model edits `db.js` instead, and one baseline response opens:

> **Fixed.** Now `client.release()` always runs, even when `fn` throws.

**This is [#116]'s behaviour, in the suite, unscored since round 27.** Unlike the
`Don't edit anything.` cases, `conditional` does not forbid editing — so the
model is not disobeying an instruction, it is answering a question with a work
product, which is exactly the distinction [#116] draws.

`Edit` is **sonnet-only**: 81 of 3,977 sonnet runs, 0 of 1,140 haiku, 0 of 440
opus.

### The matched comparison, and why the pooled one is worse evidence

`conditional`/sonnet holds 380 runs, but they span three dates, and only one date
has both arms. The pooled figure is baseline 8/10 against laconic 73/170,
p = 0.0445 — and it is the carried-arm error this loop already documents, a
single-day baseline against a laconic arm pooled over three eras.

**The matched pair, one interleaved batch on 2026-09-02 at `rules_cksum`
136269960:**

| arm | edits | rate |
|---|--:|--:|
| baseline | **8 / 10** | 80.0% |
| laconic | **2 / 10** | 20.0% |

Two-sided Fisher **p = 0.0230**.

Laconic's rate across the three dates, at byte-identical rules, is 50.0%
(08-28, n=80), 38.8% (08-31, n=80) and 20.0% (09-02, n=10). The widest pair is
p = 0.0975, so unlike round 37's preamble case there is **no demonstrated drift
here** — but the 09-02 endpoint is ten runs and cannot rule one out either.

**Ten a side cannot settle this**, which is the lesson
[`preamble.md`](preamble.md) recorded and round 37 acted on. What makes this one
cheap is that `conditional` is single-turn and the metric is syntactic: does the
tool list contain `Edit`.

## The matched batch, registered here

> **Hypothesis:** on `conditional`/sonnet, generated as one interleaved batch,
> the laconic arm's `Edit` rate is lower than the baseline arm's.

**Falsifier, registered before the batch:** the two arms not separating at
p < 0.05 on a two-sided Fisher exact test. That would make the archive's
p = 0.0230 a ten-run draw and leave [#116] with no measured evidence in either
direction.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 40 \
  --cases conditional --concurrency 1 \
  --snapshot evals/snapshots/loop/volunteered-work-conditional.json
```

80 generations, no judging, because the metric is a substring of a recorded
field. **`conditional` is a `rule-adherence` case, so this may not be optimized
against** — no rule edit may be proposed from it. It is measured for disclosure,
which is what the skill reserves those cases for.

Registered secondary, so it is not chosen afterwards: **the same batch re-reads
the archive's era question.** Its laconic cell lands beside 08-28's 50.0% and
08-31's 38.8% at the same `rules_cksum`, so it says whether the 20.0% reading
was drift or a draw.

## The matched batch: result

**The falsifier did not fire. The arms separate.**

| arm | edits | rate |
|---|--:|--:|
| baseline | **25 / 40** | 62.5% |
| laconic | **14 / 40** | 35.0% |

Two-sided Fisher **p = 0.0247**, one interleaved batch, 40 a side, sonnet,
`rules_cksum` 136269960. Baseline's 62.5% is consistent with the archive's 8/10
(p = 0.4606), so the ten-run cell was not misleading about its own arm.

**This is the first measured evidence bearing on [#116], and it points for the
plugin**: laconic nearly halves the rate at which a question gets answered by
editing the user's file.

### The registered secondary: it was a draw, not drift

> **Corrected 2026-09-05 in [`conditional-homology-116.md`](conditional-homology-116.md).**
> Every row of the table as first published was miscounted, and the caption said
> "byte-identical rules" of two cells that were not. The 08-28 and 08-31 rows each
> summed a round's control snapshot with that round's **rules-edit treatment**
> snapshot, which carries a different `rules_cksum` (`3191525351` and `2407259766`);
> the 09-02 row counted the same five runs twice, because
> `opus-model-set-sonnet-a` is a shard that was merged into `opus-model-set`. The
> corrected table is below. **The conclusion is unchanged** — no drift is
> demonstrated — but see the correction for what the corrected series says once
> 09-05 is added to it.

Laconic's rate at byte-identical rules, one row per snapshot at `rules_cksum`
136269960, sonnet, `laconic`, `conditional`:

| date | rate | source |
|---|--:|---|
| 2026-08-28 | 19/40, 47.5% | `round-30-nevercut-control` |
| 2026-08-31 | 16/40, 40.0% | `round-31-control` |
| 2026-09-02 | 1/5, 20.0% | `opus-model-set` |
| **2026-09-03** | **14/40, 35.0%** | this batch |

Today lands between the two large cells — p = 0.8176 against 08-31 and p = 0.3638
against 08-28. **No drift is demonstrated over six days**, and the 09-02 reading
of 20.0% was a five-run draw. Worth recording against round 37, where the same
kind of check found a syntactic rate moving 4.7x in five days: drift is a hazard
to test for, not a background assumption.

## The unregistered finding, which matters more than the registered one

**A run that edits says almost nothing. The work product replaces the prose.**

| | n | median words |
|---|--:|--:|
| edited `db.js` | 39 | **45.0** |
| did not edit | 41 | **144.0** |

A 99-word gap at permutation **p = 5e-06**. One baseline response in full is
*"Fixed. Now `client.release()` always runs, even when `fn` throws."* plus two
sentences.

**So every prose-length metric this loop has rewards the behaviour [#116]
reports.** An answer that edits the user's file instead of answering scores as
excellent compression. That is not a subtlety — it is the metric pointing the
wrong way on the exact case that exhibits the failure.

### And it produces a clean Simpson's reversal on the arm contrast

| | edited | did not edit | whole case |
|---|--:|--:|--:|
| baseline | 51.0 | 232.0 | **77.0** |
| laconic | 25.0 | 115.5 | **95.5** |

**Laconic is lower in both strata and higher overall**, because it edits less and
editing runs are short. A scoped `output_tokens` target on `conditional` would
read laconic as the *worse* arm, from data in which it is better on every
comparison that holds behaviour fixed.

This is [#131]'s problem on a second axis. That issue gave `output_tokens` a
reading stratum, because a cell whose reading rate moved had nothing comparable
to compare. Editing does the same thing and nothing accounts for it. Filed as [#209];
`conditional` is the only case in the suite that admits an edit, so the exposure
today is one non-scoring case, and the fix is not urgent — but it stops being one
as soon as a case lets the model act, which is what [#116] needs in order to be
testable at all.

## Disclosure

- **Never-cut.** `conditional` requires the word `leak`. Baseline 38/40, laconic
  36/40, p = 0.6752. Not a separation, and disclosed because never-cut is fatal
  in a scored round and this is not one.
- **Reading.** Both arms 0/40 on `one_turn`; every run opened the fixture, so no
  [#131] stratum crossing on the reading axis.
- **Tool vocabulary in this batch:** `Read` 154 calls, `Bash` 80, `Edit` 39.
  Nothing else, consistent with the archive-wide survey above.
- **No rule edit is proposed.** `conditional` grades `rule-adherence`, and the
  skill forbids optimizing against those cases. This is measured for disclosure.

## Operational: killed twice, and the resume path is why it cost nothing

The batch was killed twice by something outside `run.py` — no OOM (4.5 GB free),
no traceback, no output — at 9 runs and then at 19. Round 35 recorded the same
thing twice and reached the same conclusion. `run.py` records nothing for a run
it did not finish, so re-running the identical command redoes exactly what is
missing: the second launch printed `71 call(s) to make, of 80 cell(s) in this
pass (9 already in the snapshot)`.

What finished it was running the same command in the foreground in two chunks
under a `timeout 560`, which is worth knowing: **the kill did not reach a
foreground process.** The measurement is unaffected either way — resume is by
key, and every completed run is byte-identical whichever process produced it.

## Follow-up, registered before it runs: does the work product come with the answer?

**No number in the result section below has been computed.** This is the
prerequisite for authoring the case [#116] needs, and it is a question about
[`CRITERIA.md`](../../CRITERIA.md)'s own rule:

> Those three prompts therefore end with "Don't edit anything." The clause is
> identical in all four arms, so it favours none of them, but **a new case needs
> it or its verdicts measure whether the model chose to act.**

That clause is why no scorable case admits an edit, and it is the reason [#116]
cannot be optimized against. A case for [#116] has to drop it, which means
knowing what dropping it costs: **if an editing response still carries the
diagnosis, the quality verdict survives and the case is buildable. If it does
not, `CRITERIA.md` is right and a `quality` trap cannot coexist with an edit.**

The deterministic check is ambiguous, which is what makes the verdict worth
buying. `conditional` requires the word `leak`:

| | n | names `leak` |
|---|--:|--:|
| edited `db.js` | 39 | 34 (87.2%) |
| did not edit | 41 | 40 (97.6%) |

Fisher **p = 0.1044** — the right direction for `CRITERIA.md`'s worry and not
significant.

> **Hypothesis:** on `volunteered-work-conditional.json`, runs that edited
> `db.js` pass the trap at a lower rate than runs that did not.
>
> **Falsifier, registered before the pass:** the two strata not separating at
> p < 0.05 on a two-sided Fisher exact test, which would say an editing response
> still carries its answer and a `quality` case may drop the clause.

```sh
python3 evals/bench/judge.py   --results evals/snapshots/loop/volunteered-work-conditional.json   --judge-all --jobs 6   --out evals/snapshots/loop/volunteered-work-conditional-judgments.json
```

**Read with the grading caveat.** `conditional` is `rule-adherence`, so its
verdicts support nothing as an arm comparison. This is not one: it is a
within-corpus correlation between a behaviour and the trap, and the trap's
load-bearing half — the conditional advice and naming the leak — is
fixture-derived. Its one form clause, the arrow prohibition, is the contaminated
part and is disclosed with the result.

## Follow-up: the falsifier fired, and the clause can go

| stratum | trap passes | rate |
|---|--:|--:|
| edited `db.js` | 24 / 39 | 61.5% |
| did not edit | 22 / 41 | 53.7% |

Two-sided Fisher **p = 0.5055**. The registered falsifier fired: the strata do
not separate, and the point estimate runs the *other* way from the worry.

**An editing response carries its answer as often as a non-editing one.** The
diagnosis does not migrate into the diff — the model edits *and* explains, or
fails to explain whether or not it edited. So the premise behind
[`CRITERIA.md`](../../CRITERIA.md)'s clause does not hold on this case, and **a
`quality`-graded case for [#116] may drop "Don't edit anything."**

That is the prerequisite cleared. What such a case still needs, and what this
result does not supply, is its own fixture and trap: the behaviour is then read
from the tool list as a syntactic counter, the way closing offers and `one_turn`
are, while the judge grades only fixture-derived content. Keeping those two
apart is what stops the trap from grading laconic against a rule laconic
proposed.

### Disclosure: the clause that makes this case `rule-adherence` never fires

`conditional` is marked `rule-adherence` because its trap's fail condition
includes the arrow prohibition — *"when the conditional is collapsed into a
symbol such as `waiting climbing -> raise max`"*. Across **34 failures, not one**
judge reason cites it. Every failure is on the fixture-derived half: the advice
was given unqualified rather than conditional, or the `withClient` leak was never
named.

That is worth recording and is not acted on here. Re-grading a case changes what
its stored verdicts support, and a case's classification should not be revised
inside the measurement that noticed it — the same reason [#172] was filed rather
than fixed in round 35.

> **Tested and refused, 2026-09-04.**
> [`conditional-retrap.md`](conditional-retrap.md) re-judged these 80 runs under
> a trap with the clause removed. The clause is indeed inert — 0 of 18 flips turn
> on it, matching the 0 of 34 here. But a same-trap control moved **10 verdicts
> of 80**, so this criterion self-disagrees at 12.5% and the null is
> uninformative. `conditional` stays `rule-adherence`: promoting a criterion
> that flips 1 verdict in 8 into `quality_fails`, a fatal counter, would put a
> coin flip behind a fatal gate.

### Disclosure: an arm gap that may not be read as one

| arm | trap passes |
|---|--:|
| baseline | 31 / 40 |
| laconic | 15 / 40 |

**No claim is made from this and none may be.** `conditional` grades
`rule-adherence`, which per `CRITERIA.md` supports nothing in either direction:
it is the treatment arm graded against text it was handed. The trap requires two
things at once — state the conditional *and* name the leak — which is exactly the
kind of two-part completeness a terse arm sheds, so scoring laconic against it is
the circularity the rule exists to prevent.

It is disclosed rather than omitted because omitting an unfavourable number is
how a ledger lies, and because it is the sharpest argument for building the
`quality`-graded successor: on a case whose trap is fixture-derived and whose
grading permits a comparison, this number would mean something. Here it cannot.

### Cost

80 judgments, 0 failed, 3 `not_exercised`. No generation.

## Cost

80 generations, 0 failed, **$3.91**. No judging, because the metric is a
substring of a recorded field.

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#172]: https://github.com/JordanMPDS/laconic/issues/172
[#209]: https://github.com/JordanMPDS/laconic/issues/209

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#142]: https://github.com/JordanMPDS/laconic/issues/142
