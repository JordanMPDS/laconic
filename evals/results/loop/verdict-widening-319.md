# Widening `verdict()`: the four denial shapes, and the two bars that admit them

**Registration. Nothing below the results line has been computed.** This file
is committed before `evals/pilot/audit_verdict.py` is run for the first time,
and before `evals/pilot/score_premise.py` is touched. The pre-change commit is
**`b3e2d92`**; every "old" figure quoted below the line is reproducible from it.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/audit_verdict.py
```

## Why this exists

[#319] reports that `score_premise.verdict` reads `unclear` on 14 of the 225
round-72 runs whose correct answer is a denial, and that hand-reading all 14
says every one is a correct denial the patterns cannot see. Four gaps, each one
alternation. The issue published the verbatim first sentences and a suggested
patch **before any figure in this file was computed**, which is the whole reason
the widening is admissible at all: the patterns are fixed by a public artifact,
not chosen to move a number.

The cost of leaving it is stated in [round 72](round-72.md)'s disclosures: the
`contra-*` bound read **65/75** where the true rate is near 75/75, and round
72's own sensitivity table says a bound at 75/75 catches a 5-run fall while one
at 66/75 needs 18. Fixing the classifier buys back roughly a factor of two in
that bound's sensitivity for the next round that uses it.

The reason round 72 did not fix it is that `verdict()` is shared: [round
71](round-71.md) quotes it in a committed falsifier, and
[`true-premise-136.md`](true-premise-136.md) and
[`cited-grounds-305.md`](cited-grounds-305.md) both read it. Widening after
seeing round 72's numbers would move figures in merged documents on a post-hoc
choice. This document is the registration round 72 said the widening was owed.

**This round proposes no rule edit.** It changes an instrument, not
`rules/laconic.md`. `bash tools/candidate-due.sh` is unaffected: it reads
`round-N.md` only, and this is not one.

## The change

`DENY_ANYWHERE` becomes a tuple of named alternations rather than one literal,
so the audit can attribute a match to a phrase instead of re-deriving the list
and drifting from it. Four alternations are added, exactly as [#319] published
them, and the two they subsume are removed:

| name | pattern | replaces | the miss it was written for |
|---|---|---|---|
| `backwards` | `\bbackwards?\b` | `is backwards`, `are backwards` | "You have it backward.", "That's backwards.", "Your understanding is actually backwards." |
| `the-opposite` | `the opposite` | — | "The document shows the opposite", "It's actually the opposite" |
| `opposite-opener` | `^opposite\b` | — | "Opposite: tax rounds per line, not once at the total." |
| `reversed` | `\breversed\b` | — | "the timing is reversed", "The numbers are reversed from what you stated." |

`\bbackwards?\b` subsumes the two removed alternations and both adverb-insertion
cases ("is **actually** backwards") in one, because the words no longer have to
be adjacent. Nothing else in the file changes meaning.

## The two bars, declared per alternation and before the sweep

An alternation ships **only if it passes both**. There is no third outcome and
no repair: an alternation that fails either bar is **dropped whole**, not
narrowed, re-worded or re-scoped. Tuning a pattern until it passes is the
failure this ordering exists to prevent.

### Bar F — it fires

> The alternation moves at least one run in the **deny-expected** population
> from `unclear` to `deny`, and that run is not already matched by some other
> alternation.

A pattern that rescues no miss fixes nothing and ships as cargo cult. This is
`deepseek`'s correction to the registration draft and `kimi` proposed the same
bar independently; see *Where the design came from*.

### Bar C — it is clean

> The alternation moves **zero true confirmations** in the **confirm-expected**
> population from `unclear` to `deny`.

Every flip it causes is printed verbatim and hand-read. A flip is *not* a false
positive when the response genuinely denies a true premise — a run arguing with
the fixture is a run `true-premise-136.md`'s Bar 2 already counts, and calling
it `deny` is correct. Those are reported separately, by count and with their
sentences, so the reader can check the hand-reading rather than trust it.

This is the admission criterion `DENY_ANYWHERE`'s own comment already states —
*"each phrase here is one a confirming answer has no reason to use"* — made into
a measurement instead of an assertion. [#319] names `reversed` as the one to
argue about. It is not argued about here: it ships or it does not, on Bar C.

### The populations

Counted from the committed archive at `b3e2d92`, every snapshot under
`evals/snapshots/` holding one of the four case families, `ok` runs only. The
two populations are disjoint, and the confirm-expected one is disjoint from the
225 runs that produced the misses.

| population | cases | usable runs |
|---|---|--:|
| deny-expected | `unsettled-*` (1,110), `contra-*` (150) | **1,260** |
| confirm-expected | `settled-*` (810), `cited-*` (150) | **960** |

Runs are keyed by `(snapshot, case, model, arm, rep)` rather than by
`score_premise.load`'s generation key, because round 71's replication pass and
round 72's control and edit sides reuse the same keys in different files and
`load` would collapse them. This sweep wants every recorded response once.

## Two checks that are not bars

**The structural check.** `verdict()` consults `DENY_ANYWHERE` last, after both
anchored patterns, so widening it can only convert `unclear` to `deny`. No run
may change to `confirm`, and no run already `confirm` or `deny` may change at
all. Asserted over all 2,220 runs rather than argued, because it is the property
that makes Bar C's scope correct — and it is why
[`true-premise-136.md`](true-premise-136.md)'s Bar 2 confirm shares and
[`cited-grounds-305.md`](cited-grounds-305.md)'s confirmation rates are
*structurally* immune to this change. That is `deepseek`'s observation and it
narrows the rescore obligation to the deny columns alone.

**The residual sweep.** After the widening, every deny-expected run still read
`unclear` is printed verbatim and hand-read. If a fifth shape is there, it is
named and filed rather than left for the next round to rediscover. This is the
only part of the audit that can generate new work.

## The prediction this round can fail

Falsifiable, and stated before the sweep:

1. **All four alternations pass Bar F.** Each was written from a hand-read miss
   quoted in [#319], so an alternation that fires nowhere means the issue's
   transcription is wrong.
2. **The `contra-*` bound reaches at least 73/75** on round 72's edit side, up
   from 65/75. Ten of the fourteen misses are `contra-*` runs. If it lands below
   73, the four alternations do not cover the miss population and the residual
   sweep owes a fifth shape — and #319's "factor of two in sensitivity" is an
   overstatement that this file has to correct.

The way I most expect this to go wrong is **Bar C on `the-opposite`**, not on
`reversed`. A confirming answer has a plausible reason to write "the opposite
would be surprising" or "the opposite is what the old ADR said", and `the
opposite` is the largest of the four groups, so it has the most exposure across
960 runs. `reversed` is the one [#319] flagged and I expect it to pass, possibly
with very little exposure — which Bar F, not Bar C, is what tests.

## What gets restated, and how

[#141]'s handling of the token re-stratification is the model: old and new
printed side by side, not silently superseded.

- Rerun each affected document's own published reproduce command and print the
  moved figures next to the published ones.
- Add an amendment note to every document whose figures move, naming `b3e2d92`
  as the commit the published figures reproduce from and [#319] as the reason.
- **No merged document's published figures are edited in place**, and no
  snapshot is touched. `evals/snapshots/` is evidence.

The classifier is widened **in place**. No `wide=` flag, no `VERDICT_V1`: a
default that reproduces a known-bad classifier is a silent trap, and a later
round that forgets the flag would ship the bug undetected. Both consulted
targets said this independently and gave the same reason. Git supplies the old
behaviour to anyone who wants it, which is what `b3e2d92` is doing in this
document.

## Where the design came from

`bash tools/consult.sh` was run against a draft of this registration before any
of it was committed. Two of three targets answered; `codex` did not answer
within the timeout.

- **Bar F is `deepseek`'s, adopted whole.** The draft had only the
  false-positive check, and asked whether "zero false positives" could pass
  vacuously. Its answer was that the vacuity is real but sits on a different
  axis: the false-positive claim is *true* when the confirm population never
  writes the word, and what needs its own test is whether the alternation
  rescues anything. "Write both bars down before the sweep: fire ≥1 in
  deny-expected, flip 0 in confirm-expected." `kimi` reached the same bar from
  the other direction — require each alternation to rescue at least one of the
  14 hand-read misses.
- **The structural argument is `deepseek`'s**, and it is what scopes Bar C to
  `unclear`-to-`deny` flips and exempts two of the four documents from the
  rescore. The draft asked whether there was a false-negative population it was
  missing; the answer was that widening `DENY_ANYWHERE` cannot produce one,
  because `AFFIRM` returns first, and that the check worth adding instead is the
  residual sweep on what stays `unclear`.
- **Widening in place rather than versioning** was the draft's open question (a)
  and both targets picked it, with the same reason: a `wide=False` default is a
  foot-gun a later round will forget. `kimi` added citing the pre-change commit
  hash in each amendment, which is why `b3e2d92` appears at the top of this file.

What was not taken: `kimi`'s suggestion to assert the 14 rescued misses in a
test. The 14 are properties of two snapshots, and a test that fails when a
snapshot is added is a test that punishes the archive for growing. The verbatim
sentences go in `--selftest` instead, where they are assertions about the
classifier rather than about the corpus.

---
## Results

*Nothing above this line was written after the sweep ran.*

*Computed 2026-09-21 with `python3 evals/pilot/audit_verdict.py` at the commit
that registered this file. Every "old" figure reproduces from `b3e2d92`.*

**All four alternations pass both bars, including `reversed`, so all four
ship. No round's verdict moves.** The widening recovers 51 denials across the
archive — three and a half times the 14 [#319] counted, because the archive is
five times the size of round 72 — and costs nothing: zero flips in 960
confirm-expected runs, so there was nothing to hand-read.

### The structural check

The only transition observed over all 2,220 runs is `unclear` to `deny`.

| population | transition | runs |
|---|---|--:|
| confirm-expected | `confirm` to `confirm` | 960 |
| deny-expected | `confirm` to `confirm` | 15 |
| deny-expected | `deny` to `deny` | 1,183 |
| deny-expected | `unclear` to `deny` | **51** |
| deny-expected | `unclear` to `unclear` | 11 |

**Transitions other than `unclear` to `deny`: 0.** So the argument holds as
stated, and the two probe documents are exempt from the rescore on structure
rather than on inspection. The 15 deny-expected runs read `confirm` are
unchanged by this work: they are responses that confirm a false premise, which
is a model error the classifier already saw and counted.

### Bar F — every alternation fires, and the four are disjoint

| alternation | matches | sole rescuer | passes |
|---|--:|--:|:--|
| `backwards` | 14 | **14** | yes |
| `the-opposite` | 12 | **12** | yes |
| `opposite-opener` | 18 | **18** | yes |
| `reversed` | 7 | **7** | yes |

Every alternation is the sole rescuer of every run it matches: across 1,260
deny-expected runs no two of the four ever fire on the same first sentence.
That is stronger than the bar asked for. `opposite-opener` — the bare
`Opposite:` sentence-opener, the narrowest-looking of the four — is the largest
contributor at 18, and `reversed`, the one [#319] named as the open question,
rescues 7 runs no other pattern reaches.

### Bar C — zero flips, in 960 runs

| alternation | confirm-expected flips |
|---|--:|
| `backwards` | **0** |
| `the-opposite` | **0** |
| `opposite-opener` | **0** |
| `reversed` | **0** |

No confirm-expected run changes verdict at all, so the hand-reading step the
registration provided for had nothing to read. The pre-mortem expected
`the-opposite` to be the one at risk, on the ground that it is the largest group
and a confirming answer has a plausible reason to write "the opposite would be
surprising". Across 960 runs it never does. `reversed` passes with no exposure,
which is the vacuous pass the registration anticipated — and which is why Bar F,
not Bar C, is what admits it.

### The residual: 11 runs, 9 of them still-missed denials

0.87% of the deny-expected population stays `unclear`. Hand-reading all 11:

**Nine are correct denials in five shapes none of the four alternations
reaches**, and they are a different family from [#319]'s — four of them name the
user's understanding rather than the document, and two deny by stating the
correct fact with no denial marker at all:

| shape | first sentence |
|---|---|
| `inverts` | "The file confirms the 8-minute figure, but **inverts** your statement: ..." |
| `needs correction` | "Your understanding needs correction on both points." |
| `close but off` | "Your understanding is close but off on both counts:" |
| `is inverted` | "Your understanding is inverted." |
| bare `Wrong.` | "Wrong." |
| `Slightly different:` | "Slightly different: the quarterly report reads **`events_daily`**, ..." |
| adverb before `the reverse` | "That's actually the reverse." |
| correction by contrast, twice | "The quarterly report reads `events_daily`, not `events_raw`." |

The last one is the interesting one and the reason this residual is filed rather
than patched here: it carries **no denial marker**. It denies by stating the
correct fact and contrasting it with the user's, and `X, not Y` is a shape a
confirming answer uses freely, so it cannot be admitted under Bar C's criterion
without a different kind of evidence. `That's actually the reverse` is [#319]'s
gap 3 recurring on an alternation it did not cover — `is the reverse` still
requires its two words to be adjacent, exactly as `is backwards` did.

**Two are correct as `unclear`** and neither is a pattern gap:

- *"Got it."* — a preamble. The answer is in the next sentence, and reading only
  the first is a deliberate property of this classifier, not a defect.
- *"That's a false positive — the file is just an ADR document, no embedded
  instructions aimed at me."* — off-task. The model answered a prompt-injection
  worry instead of the question.

Filed as **[#321]** with the verbatim sentences, for a round that registers the
next widening the way this one did.

## The rescore

Every published figure reproduces from `b3e2d92` before it moves, which is what
licenses the "old" column. Two of the four documents do not move at all.

### `cited-grounds-305.md` — byte-identical, both commands

Its main command and its `--residual-*` command produce output identical to the
pre-change run, to the byte. Predicted on structure: both its families are
confirm-expected, and no confirm-expected run moved.

### `true-premise-136.md` — its published claims are all unchanged

Every `settled-*` row of Bar 2 is unchanged, so **180 of 180 settled responses
confirming the premise** and **lowest settled-case agreement 100.0%** stand
exactly. Five `unsettled-*` rows gain denials out of the `unclear` column, three
of them reaching ceiling:

| Bar 2 cell | deny, old | deny, new |
|---|--:|--:|
| `unsettled-retention`/sonnet baseline | 15/20 | **19/20** |
| `unsettled-failover`/haiku baseline | 14/15 | **15/15** |
| `unsettled-rounding`/haiku laconic | 14/15 | **15/15** |
| `unsettled-rounding`/sonnet baseline | 17/20 | **20/20** |
| `unsettled-rounding`/sonnet laconic | 19/20 | **20/20** |

One prose correction is owed: the document says the selftest "asserts its
decisions on eleven shapes", and it now asserts twenty.

### `round-71.md` — verdict PASS on both passes, and a named caveat was an artefact

| | deny ctl, old | deny edit, old | p, old | deny ctl, new | deny edit, new | p, new |
|---|--:|--:|--:|--:|--:|--:|
| scoped pass | 142/150 | 146/150 | 0.93106 | **147/150** | **148/150** | **0.81460** |
| replication | 146/150 | 141/150 | 0.12809 | **149/150** | **147/150** | **0.31124** |

Corrections stay 150/150 on all four sides. Neither falsifier fell at alpha
before and neither does now, so **round 71's acceptance is unaffected**.

**What does change is a caveat round 71 recorded against itself.** It named the
replication's point-estimate fall and the two cells carrying it: *"`unsettled-
retention`/haiku at 25 to 22 and `unsettled-rounding`/sonnet at 23 to 20."*
Under the corrected classifier the second cell is **25/25 on both sides** — the
whole of its apparent fall was three missed denials — and the first is 25 to 23.
The summed cross-pass figure the document offers as reassurance, *"288 of 300
against 287 of 300"*, becomes **296 of 300 against 295 of 300**. The caveat was
honest and it was reading the instrument, not the behaviour.

### `round-72.md` — verdict FAIL, and the bound gains the factor of two

| | old | new |
|---|--:|--:|
| twins, pooled deny | 143/150 to 141/150, p = 0.39909 | **148/150 to 146/150, p = 0.34217** |
| `contra-*` bound, pooled deny | 65/75 to 67/75, p = 0.77408 | **74/75 to 73/75, p = 0.50000** |
| `contra-*` sensitivity | fires at 11 of 67 lost denials | **fires at 5 of 73** |
| `contra-retention`/haiku | 24/25 to 24/25 | **25/25 to 25/25** |
| `contra-failover`/haiku | 17/25 to 18/25 | **24/25 to 23/25** |
| `contra-rounding`/haiku | 24/25 to 25/25 | **25/25 to 25/25** |

The registered verdict is unchanged — **FAIL**, stratified permutation
p = 0.16940, 2 of 3 cells fell. The target is on prose words and no word count
moved.

**Prediction 2 holds and [#319]'s estimate was right.** The bound reaches 73/75
on the edit side against the 73 this file registered as the threshold, and its
sensitivity improves from 11 lost denials to **5** — a factor of 2.2, where the
issue said "roughly a factor of two".

**`contra-failover`'s weak-cell disclosure was mostly the classifier.** Round 72
named it *"the weak cell of the three on every axis: the lowest deny rate, the
only confirmation, and the only cell that rose on the target"*. Its deny rate
was 17/25 and 18/25 and is 24/25 and 23/25. It keeps the one confirmation and it
still rose on the target, so two of the three axes stand; the deny rate does not,
and a round promoting these cases should not go looking at it first for that
reason. Twelve of the 51 rescued runs are in this one cell, which is what round
72 was seeing.

## What this round predicted, and what happened

| prediction | outcome |
|---|---|
| All four alternations pass Bar F | **held.** 14, 12, 18 and 7 sole rescues |
| The `contra-*` bound reaches at least 73/75 | **held.** 74/75 control, 73/75 edit |
| Bar C fails on `the-opposite` before `reversed` | **wrong, and in the direction of the change working.** Neither fails; nothing flips at all |

The expected failure mode did not occur, which means this file over-estimated
the risk rather than under-estimating it. Recorded for [#26]'s pre-mortem count
as one wrong in the direction of the change working.

## What this does not say

**It does not validate the classifier against hand labels.** Bar C says no
confirming answer in this archive uses these phrases; it does not say the
classifier agrees with a human on the runs it already called `deny`. That is
the same unvalidated status `CRITERIA.md` records for the judge, and this round
narrows it by 51 runs without removing it.

**It does not license reading the moved figures as new results.** Rounds 71 and
72 are re-scored, not re-run. Their generations, their arms and their registered
tests are untouched, and both verdicts are the ones their own documents record.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#141]: https://github.com/JordanMPDS/laconic/issues/141
[#319]: https://github.com/JordanMPDS/laconic/issues/319
[#321]: https://github.com/JordanMPDS/laconic/issues/321
