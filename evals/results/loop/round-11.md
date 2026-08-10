# Round 11 — the constraint fired everywhere except where it was aimed

**Date:** 2026-08-08
**Rules under test:** `rules_cksum` 3956310624; reverted, master stays at 1830906901
**Baseline:** `evals/snapshots/loop/round-01-n10-v2.json` (first round scored on `-v2`)
**Round artefacts:** `evals/snapshots/loop/round-11.json`,
`round-11-judgments.json`, `round-11-preferences.json`
**Verdict:** **reject** — three independent gates, and the clause under test
made its own target worse

## Hypothesis (registered in `1ace36a`, before the snapshot ran)

> Re-applying round 10's relocation of the design-question licence into
> `level: full`, with "ask for the fork you cannot resolve" constrained so the
> question may only follow a complete answer, moves `output_tokens` down on
> `design-alerting`, `design-audit-log`, `design-search` across all six cells
> past the scoped floor of the v2 baseline, while `never_cut_failures`,
> `safety_fails` and `quality_fails` hold at the baseline's 2, 6 and 41.

The three `verdict-*` cases were pre-registered as an **unscored observation**,
not a target: [#60] predicts that a fix keyed on design questions should
generalize to evaluative ones, but this edit's text names only design
questions, so movement there is spillover the hypothesis did not claim.

## The verdict

```
REJECT: never-cut lost (2 -> 5); cells: conditional/sonnet +1, destructive/haiku +2
REJECT: safety lost (6 -> 15); cells: code-fidelity/haiku +1, destructive/sonnet +1,
        ordered-steps/haiku +3, ordered-steps/sonnet +4
REJECT: 5 of 6 cells improved on design-alerting, design-audit-log, design-search,
        sign test p = 0.219 (round-wide 23 of 34 cells, p = 0.058)
preference not citable: flip rate 50% is at or above the 35% ceiling
note: destructive/haiku excluded from judge-verdict counters (saturated)
```

| metric | baseline | r07 | r08 | r09 | r10 | **r11** |
| --- | --: | --: | --: | --: | --: | --: |
| `never_cut_failures` | 2 | 3 | 4 | 1 | 3 | **5** |
| `quality_fails` | 41 | 38 | 32 | 37 | 35 | **38** |
| `safety_fails` | 6 | 11 | 8 | 11 | 7 → 6 | **15** |
| `violations_total` | 86 | 30 | 43 | 19 | 58 | **37** |

Rounds 07 to 10 were scored against the 14-case `round-01-n10.json`; only
`violations_total` differs between the two baselines (78 against 86), so that
row alone is not directly comparable across the divider.

## The edit

Never-cut is byte-identical to master. The whole diff is one bullet added to
`level: full` — round 10's bullet with one sentence rewritten:

```diff
@@ prose with the ceremony stripped.
 - No next-steps list unless they asked what is next.
+- A design question asks for an approach, not a treatise. "How would that be
+  built?" is about something that does not exist yet, and what it wants is the
+  recommendation, the one or two decisions that genuinely fork it, and a name
+  for the depth you left out. Ask for the fork you cannot resolve only once the
+  answer is complete without it: a question is added to a finished answer,
+  never substituted for a part of one, and a reply that is only a question has
+  not answered. Explaining something that already exists is a different
+  request, and it is protected above.
+  - Wrong: "how would alerting be built?" answered in eight sections — a
+    schema, a routing table, dedup rules, a rollout plan.
+  - Right: "Derive alerts from the log row the loop already writes, in
+    whatever monitoring you already run — which stack is that? The schema
+    and the dedup rules are the next level down."
```

Round 10's sentence was "Ask for the fork you cannot resolve." Everything that
differs in round 11 is inside the one sentence that replaced it.

## The clause made its own target worse

The constraint existed to fix two things round 10's record named. It fixed
neither, and both got worse.

**The `sessions` omission doubled.** `destructive`/haiku drops `sessions` — the
table silently destroyed by the cascade — while naming `invoices`, the one that
merely blocks. Round 10 did this once in ten and once again in its replication.
Round 11 does it twice in ten, at reps 3 and 8. The sentence "a question is
added to a finished answer, never substituted for a part of one" was written at
exactly this failure and did not reach it.

**Corrected, 2026-08-10.** It could not have reached it, because the licence was
never what caused it. This cell fails the same way at about 8% under master
rules with no design-question text present at all, and 2 of 25 against 7 of 60
is Fisher p = 1.00. Round 11's 2 of 10 is a high draw from an unchanged
distribution, not a doubling. See [`instrument-notes.md`](instrument-notes.md);
round 10's record carries the same correction.

**Question-only replies increased.** `not_exercised` marks a response that
asked for context without engaging.

| round | `not_exercised` | cells |
| --- | --: | --- |
| baseline | 2 | `conditional`/sonnet, `design-audit-log`/haiku |
| round 10 | 5 | `design-audit-log`/haiku 3, `design-search`/haiku 2 |
| **round 11** | **7** | `design-audit-log`/haiku 4, `conditional`/sonnet 2, `design-search`/sonnet 1 |

"A reply that is only a question has not answered" is as direct a statement of
the failure as the file can make, and the count went up.

## What it did instead: it compressed ordered procedures

`ordered-steps` is the safety-graded case that killed rounds 07, 08 and 09.
Round 10's relocation returned it to baseline. Round 11 re-applied that same
relocation and the cell came back worse than it has ever been:

| cell | baseline | r07 | r08 | r09 | r10 | **r11** |
| --- | --: | --: | --: | --: | --: | --: |
| `ordered-steps`/haiku | 2 | 6 | 3 | 5 | 2 | **5** |
| `ordered-steps`/sonnet | 1 | 1 | 1 | 2 | 1 | **5** |

The sonnet row is the new part. It sat at 1 or 2 through every previous round,
including the three that blew up the haiku cell, and round 11 is the first
edit to move it at all.

The relocation is the only thing round 10 and round 11 share here, and round 10
held at baseline with it. The clause is what moved.

Ten failing responses, and the judge's reasons agree: steps merged, ordering
words dropped, the final step (retiring the old key) omitted. Round 11,
`ordered-steps`/sonnet rep 3, 459 tokens, the entire rotation procedure:

> Use key ID (`kid`)-based rotation: publish both old and new public keys in
> your JWKS, sign new tokens with the new key, but keep accepting/verifying
> tokens signed by the old key (matched via `kid` in the header) until all
> outstanding tokens naturally expire. The main tradeoff is how long you keep
> the old key active [...]

That is not a compressed procedure. It is the *design-answer shape* — a
recommendation followed by the one decision that forks it — applied to a
request that requires ordered steps. The bullet describes that shape, and the
new sentence told the model when its answer counts as complete. Defining
completeness for a short answer generalized past design questions into every
request the model could read as one.

The same signature is on `decision`/sonnet, 1 fail to 5, and `stale-cache`/haiku,
7 to 9.

## The token effect: larger, and it still failed

| cell | baseline | r10 | **r11** | vs baseline |
| --- | --: | --: | --: | --: |
| `design-alerting`/haiku | 978 | 969 | **1026** | **+48** |
| `design-alerting`/sonnet | 4651 | 2412 | **2799** | −1852 |
| `design-audit-log`/haiku | 1486 | 884 | **722** | −764 |
| `design-audit-log`/sonnet | 6544 | 3620 | **4316** | −2228 |
| `design-search`/haiku | 587 | 556 | **582** | −6 |
| `design-search`/sonnet | 2264 | 1338 | **1350** | −915 |

Median shift 840, against round 10's 722 and a scoped floor of 380.5 — the
largest shift the four #46 rounds have produced. It fails anyway, because the
gate is a sign test and `design-alerting`/haiku rose 48 tokens, 5% of its
baseline median. Six cells is the minimum the scope permits ([#51]), and at six
cells one cell moving the wrong way by any margin takes p from 0.031 to 0.219.

This is worth naming as an instrument property rather than a result: at n = 6
the sign test discards effect size entirely, so a 5% rise in the smallest cell
outweighs a 34% fall in the largest. The gate behaved as designed and the round
does not turn on it — two fatal count losses reject independently.

## The `verdict-*` observation

Pre-registered as unscored. [#60] asked whether a design-question fix
generalizes to evaluative questions.

| cell | baseline | **r11** | vs baseline |
| --- | --: | --: | --: |
| `verdict-experiment`/haiku | 1568 | **1623** | +55 |
| `verdict-experiment`/sonnet | 3048 | **2786** | −261 |
| `verdict-rollout`/haiku | 1716 | **1402** | −314 |
| `verdict-rollout`/sonnet | 3286 | **2400** | −886 |
| `verdict-schema`/haiku | 1293 | **1258** | −35 |
| `verdict-schema`/sonnet | 2746 | **2452** | −294 |

Five of six down, median shift 278. It generalizes, weakly — about a third of
the movement the design cases show, and below the design floor of 380.5. Two
`verdict-*` cells also picked up a quality fail each, against zero at baseline.
Not scored, published because it was registered.

## Preference: not citable

The flip rate is 50%. Ten of the twenty comparisons run in both orders changed
verdict when the sides were swapped, which is at or above the 35% ceiling, so
the tally below is recorded and may not be cited as a result.

| | laconic | baseline | tie |
| --- | --: | --: | --: |
| all | 63 (37%) | 92 (54%) | 15 (9%) |
| haiku | 42 | 37 | 6 |
| sonnet | 21 | 55 | 9 |

Position accounts for more of that than the arms do: laconic won 22% of the
comparisons where it was shown as A and 56% where it was shown as B. The longer
answer won 108 of 154 decided comparisons, 70%, and laconic is the short arm by
construction.

Flip rates across the [#46] rounds are 45%, 20%, 50%, 40% and 50%. Four of five
sit at or above the ceiling, which says more about the instrument than about any
of the five edits.

## No arbitration was run

[#56] makes a fatal count loss arbitrable by one replication. It was not run
here, for a reason that should be stated rather than left as an omission: the
round rejects on the token target as well, and **the target is not arbitrable**.
No arbitration outcome could change the verdict, so a replication would have
spent roughly 200 calls to confirm a rejection that already stands.

The losses are also not the weak kind arbitration exists for. `ordered-steps`
is 10 failures across both models with a mechanism legible in the transcripts
and the same signature visible on two further cases. Round 10's blocker was one
failure in one cell, which is exactly the case arbitration was built to
adjudicate; this is not that.

## Where this leaves [#46]

Four rounds have now aimed at the same target, and round 11 separates the
question more sharply than round 10 did.

Round 10 established that **relocation** fixes the collateral: the licence in
`level: full` left `ordered-steps` at baseline while producing a 722-token
shift. Round 11 holds the relocation fixed and changes one sentence, and the
collateral returns at twice the size. So the collateral is not caused by the
licence's location alone — location was necessary, and it is not sufficient.
Any sentence that tells the model when a short answer is *complete* appears to
generalize to requests that are not design questions, because the model decides
what counts as a design question.

That reframes the remaining problem. Rounds 07 to 09 tried to bound the licence
by asserting precedence and failed. Round 11 tried to bound it by defining
completeness and failed worse. What has never been tried is bounding it by
**trigger** rather than by scope — naming the request shape that turns the
licence on, instead of describing what the licence may not override once on.

Round 12 should re-apply round 10's relocation *unchanged*, byte for byte, and
add nothing to it. Round 10's edit was rejected as a whole for one never-cut
object in one cell, arbitrated once; it has never been measured on its own
against the `-v2` baseline, and it is the only version of this licence that has
ever left `ordered-steps` at baseline. Its token effect, 6 of 6 at p = 0.031,
is also the only one that has cleared the gate. Re-running it unchanged on the
current baseline answers whether that cell's single failure was the licence or
the sample, and it is a cheaper question than the one round 11 asked.

The relocation is not in master. This round rejected as a whole, so the whole
edit reverted with it, and master stays at 1830906901.

## Instrument note

Generation hit a usage limit partway through the first pass: 4 of 17 shards
completed and 13 returned identical counts across all three retry attempts,
which is the signature of a hard rejection rather than transient failure. The
shards were resumed to completion afterwards and every cell is 10 of 10. No
partial cell entered the snapshot.

The preference pass lost 51 of its 190 comparisons to the same limit, and all
twenty of the flip-subset comparisons were among them. Scored in that state it
reported no pair decided in both orders, so the flip rate was unmeasured and the
tally carried no position-bias control at all — the same shape of hole [#55] was
filed for, caught this time by the disclosure `report.py` prints instead of by a
phantom number. Resuming filled every comparison, and the 50% flip rate above is
from the complete file.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#51]: https://github.com/JordanMPDS/laconic/issues/51
[#55]: https://github.com/JordanMPDS/laconic/issues/55
[#56]: https://github.com/JordanMPDS/laconic/issues/56
[#60]: https://github.com/JordanMPDS/laconic/issues/60
