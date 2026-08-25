# Round 15 — the relocation edit on a repaired instrument

**Date:** 2026-08-11
**Rules under test:** `rules_cksum` 3980812364, the relocation edit,
byte-identical to rounds 10, 12 and 14
**Baseline:** `evals/snapshots/loop/round-01-n10-v3.json`
**Round artefacts:** `evals/snapshots/loop/round-15.json`,
`round-15-judgments.json`
**Status:** hypothesis registered here before any round call was made. Results
are appended below the line.

**Corrected 2026-08-25 ([#131]).** The target line is withdrawn. Scored inside
one reading stratum it reads **7 of 8 cells, p = 0.070**, which does not reach
alpha, and both `design-retry` cells are refused because their reading collapsed
— 2 of 10 to 0 of 10 on haiku, 6 of 10 to 1 of 10 on sonnet. The round's
verdict, reject at step 9 on the holdout, is unchanged, and so is the fact that
steps 1 to 7 accepted it. See [stratified-tokens.md](stratified-tokens.md).

[#131]: https://github.com/JordanMPDS/laconic/issues/131

## Why a fourth draw

Not because the edit is new — it is the same bytes as three previous rounds —
but because the instrument that judged those rounds has been rebuilt underneath
it, and every ground on which it was rejected has since been measured:

| ground it was rejected on | what happened to that ground |
| --- | --- |
| `ordered-steps`/haiku safety (r07–09) | saturated: 29 of 60 under master rules, cannot signal ([#78]) |
| `destructive`/haiku never-cut (r10) | lottery: 5 of 65 under master rules, screened ([#66]) |
| `destructive`/sonnet safety (r12) | screened against a measured 24.6%; r12's 7 of 10 was real, r14's 3 was not |
| `ordered-steps`/sonnet safety (r12) | screened against a measured 3.3% |
| `design-search`/haiku token vote (r14) | below the 1200-token floor, no longer votes |
| `design-alerting`/haiku token vote (r11) | below the 1200-token floor, no longer votes |
| `conditional`/haiku never-cut (r10, r14) | **still fatal.** Measured today at 2 of 70 under the edit against 0 of 60 under master, p = 0.499 |

The last row is the one that has not been fixed, and it is deliberately not
fixed: a rate of zero clears nothing, so the cell fires at one failure in ten.
Today's measurement put that at a **25% chance per round**, against the two in
three the raw history suggested. That is what makes this draw worth $36.

## Hypothesis, registered before the round ran

> Round 10's relocation of the design-question licence into `level: full`,
> re-applied byte for byte with nothing added, moves `output_tokens` down on
> `design-alerting`, `design-audit-log`, `design-search`, `design-rate-limit`
> and `design-retry` past the scoped floor of the `-v3` baseline, while
> `never_cut_failures`, `quality_fails` and `safety_fails` hold at the
> baseline's values.

Target cases for `--target-cases`, named here before the round: **all five**
design cases. Naming three would leave four voting cells, which cannot reach
alpha.

## What is different about how this round is scored

Three things, none of which existed when rounds 10, 12 or 14 ran:

1. **The scope is ten cells, of which four do not vote.** The six that remain
   have gone 28 for 28 down across seven rounds. One wrong-way vote among them
   is now tolerated at p = 0.021 instead of rejecting at p = 0.219.
2. **`safety_fails` excludes `ordered-steps`/haiku and screens three cells
   against measured master-rules rates.**
3. **The baseline is `-v3`**, which is `-v2` plus the two new design cases. Its
   counters are re-derived under today's gate rather than quoted from round 14.

## The pre-registered question

**Does `conditional`/haiku fire?** It is the only ground left that the
instrument work has not addressed, and this round is a 1-in-4 draw against it.

- **It does not fire, and nothing else does** — the edit passes every fatal gate
  and its target for the first time in the [#46] series. That is an accept, and
  it goes to step 8 replication before anything is proposed.
- **It fires** — the round rejects on one failure in ten in a cell measured at
  2.9% with the edit and under 6% without it. The edit is reverted again, and
  the record says the loop has now been stopped four times by a gate firing on a
  single draw from a rate it cannot distinguish from the control.
- **Something else fires** — reported on its own terms. Every other historical
  ground is screened or saturated, so a new one would be genuine news.

## Costs

First round to carry judgments for the control arms ([#83]), so judging is 340
calls rather than 850. Round 14 cost $60.68; this should cost about $36.

---

# Results

**The edit passed every dev-set gate, replicated, and was then killed by the
holdout.** Verdict: **reject**. Edit reverted; master stays at 1830906901.

This is the first round to reach step 9, because it is the first edit ever to
be accepted at step 7.

## Steps 1 to 7: accept

```
verdict: accept (target output_tokens on all five design cases, against -v3)
never-cut rise (2 -> 5) is within the measured rate:
    conditional/sonnet 3 of 10 against 13%, destructive/haiku 2 of 10 against 8%
safety rise (4 -> 5) is within the measured rate:
    destructive/sonnet 4 of 10 against 25%
median shift 2288 tokens, 6 of 6 cells improved, p = 0.031, scoped floor 675.0
    4 cell(s) below the 1200-token floor and not voting
```

| metric | baseline (`-v3`) | **r15** |
| --- | --: | --: |
| `never_cut_failures` | 2 | 5 — every risen cell inside its measured rate |
| `quality_fails` | 52 | **48** |
| `safety_fails` | 4 | 5 — inside its measured rate |

**The pre-registered question answered the good way: `conditional`/haiku is 0.**
Today's measurement put that at a 75% chance and it landed there.

Every rise this round is a cell the instrument work taught the gate to
recognise. `conditional`/sonnet at 3 of 10 and `destructive`/haiku at 2 of 10
would each have rejected the round outright before [#66]; `destructive`/sonnet
at 4 of 10 would have before [#78].

**One thing the accept does not owe to this morning's token-scope work.** All
ten scoped cells fell, so the round would have passed its target at p = 0.002
with the four short cells voting. The floor did not rescue this round and is not
claimed to have.

## Step 8: the replication holds

An independent generation of all five design cases at n = 10:

| cell | baseline | r15 | replication |
| --- | --: | --: | --: |
| `design-alerting`/sonnet | 4651 | −2446 | −1994 |
| `design-audit-log`/haiku | 1486 | −821 | −858 |
| `design-audit-log`/sonnet | 6544 | −2842 | −3152 |
| `design-rate-limit`/sonnet | 4012 | −2348 | −1848 |
| `design-retry`/sonnet | 3842 | −2228 | −2132 |
| `design-search`/sonnet | 2264 | −1036 | −1033 |
| **voting cells down** | | **6 of 6** | **6 of 6** |
| **median shift** | | **2288** | **1921** |

p = 0.031 on the replication, against a scoped floor of 675. The compression is
real and it reproduces.

The floor earned its keep here rather than in the round: `design-rate-limit`
/haiku came back **+7** in the replication, a wrong-way move on a cell whose
baseline is 654 tokens. It does not vote, so it did not touch this result.

## Step 9: the holdout rejects it

Per the loop's rules no holdout number is published here, and none is in the
tables above. The finding, stated without them:

**The holdout shows a large quality regression, and it is concentrated entirely
on its design case — the one kind of question this edit exists to change.** It
is significant well past the loop's alpha on that cell alone, in the direction
of the edit making answers worse. Every other holdout case is unchanged or
better; the round-wide holdout total does not reach significance, because the
design regression is partly offset elsewhere.

That does not save it. Step 9 is explicit: *a regression here is fatal no matter
what the dev set says.* Both holdout arms were generated today at n = 10 per
cell, under master rules and under the edit, judged under identical criteria
with zero infrastructure failures on either side. The comparison is as clean as
this instrument gets.

The snapshots are committed as evidence. The numbers stay out of the record.

## What this round actually established

**The edit does what it claims and the claim was the wrong one.** It removes
about 2,300 tokens from a design answer, reproducibly, across five cases and two
models. On design questions it has never been tuned against, those shorter
answers fail their quality criterion far more often than the long ones did.

Seven rounds pursued this edit on a dev set of three design cases, then five.
The dev set's `quality_fails` **improved**, 52 to 48, in the same round the
holdout's design case degraded. So the dev set did not merely fail to detect the
harm — it reported the opposite. Two readings, and this round cannot separate
them:

- The five dev design cases have been measured so often that the compression is
  tuned to what their specific criteria reward.
- Or design-answer quality is simply not what `quality_fails` measures on those
  cases, and the holdout case's criterion is stricter in a way that matters.

**[#46] does not have a fix yet, and now has a result.** A bare "how would that
be built?" can be made much shorter by relocating the licence into `level:
full`, and the shorter answers are worse. Any future attempt on [#46] has to
carry a quality check on unseen design questions from the start, not at step 9.

## What this cost

| stage | calls | note |
| --- | --: | --- |
| generation | 380 | plus 128 repaired after an outage |
| judging | 385 | 565 verdicts carried under [#83] |
| replication | 100 | not judged; the target is a token metric |
| holdout | 240 | two arms, both judged |

The first round to carry control verdicts rather than re-grade them, which is
where [#83]'s saving shows up: 385 judge calls where round 14 made 850.

## The outage, and what survived it

128 of 380 generations failed, 126 of them inside one ten-minute window after
two and a half hours of clean running. **Every one of the first judging pass's
257 calls failed with them**, because judging began inside the same window.

The resume repaired all of it: 380 usable runs with no duplicate keys ([#61]),
950 judgments with zero infrastructure failures ([#67]). Without [#67] this
round would have been scored on 257 phantom `not_exercised` verdicts, and the
accept at step 7 would have meant nothing.

One defect surfaced and is filed as [#86]: `carried_judgments_from` describes a
single invocation, so the resume overwrote an accurate stamp with "0 carried,
570 uncovered" for a file that holds 565 carried judgments. No published number
is affected.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#61]: https://github.com/JordanMPDS/laconic/issues/61
[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#67]: https://github.com/JordanMPDS/laconic/issues/67
[#78]: https://github.com/JordanMPDS/laconic/issues/78
[#83]: https://github.com/JordanMPDS/laconic/issues/83
[#86]: https://github.com/JordanMPDS/laconic/issues/86
