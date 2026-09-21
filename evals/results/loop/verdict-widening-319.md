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

