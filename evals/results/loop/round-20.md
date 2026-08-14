# Round 20: can the dev set see what the holdout saw?

**Date:** 2026-08-14
**Rules under test:** `rules_cksum` 3980812364 — round 10's design-question
licence, re-applied byte for byte for the fifth time
**Baseline:** `round-01-n10-v4.json`, judged under
`round-01-n10-v4-judgments-traps2.json`
**Status:** hypothesis registered before the round ran. Results are appended
below the line.

## Hypothesis, registered before the round ran

> Round 10's design-question licence, re-applied byte for byte, moves
> `output_tokens` down on `design-alerting`, `design-audit-log`, `design-search`,
> `design-rate-limit` and `design-retry`, as it did in rounds 10, 12, 14 and 15.

> Pre-registered question: does `quality_fails` rise on `design-cache`,
> `design-realtime` and `design-upload`? Those three cases were admitted in [#88]
> because their criteria can tell a derived answer from a recalled one, and they
> did not exist when the holdout killed this edit at step 9 of round 15.
> Registered outcomes, before any data: (a) `quality_fails` rises on those cells
> — the dev set now sees what the holdout saw, and the instrument is repaired;
> (b) `quality_fails` holds while `output_tokens` moves — the dev set still
> cannot see the harm, the edit would pass step 7 a second time, and step 9
> remains the only gate that can kill it. **Outcome (b) is a negative result
> about the instrument and is NOT a licence to ship this edit.**

Target cases for `--target-cases`, named here before the round: **all five**
design cases. Naming three would leave four voting cells, which cannot reach
alpha.

## Why run an edit that has already been rejected

This round is not asking whether the edit is good. Round 15 answered that at
step 9: the holdout showed a large quality regression concentrated entirely on
its design case, in the direction of the edit making answers worse, and no
holdout number is published.

It is asking whether the **dev set** can now detect that harm. When round 15 ran,
the five older design cases could not tell a derived answer from a recalled one
— on all five, the answer a model gives without opening a file is already the
fixture's answer, which is why `baseline`, `laconic`, `terse-control` and
`word-compression` all scored alike
([`design-discrimination.md`](design-discrimination.md), [#88]). The dev set's
`quality_fails` moved the *other way* in round 15, so it did not merely miss the
harm, it reported the opposite.

`design-cache`, `design-realtime` and `design-upload` were built precisely to
close that gap, and on them no response that failed to resolve the fixture has
ever passed. They have never been exposed to this edit. That is the measurement.

## The edit

The "Never cut" section is byte-identical to master. The entire diff is one
bullet added to `Level: full`, immediately before the "Typical shape" paragraph.
Verified byte-for-byte against the copy preserved in
[`round-10.md`](round-10.md), and the resulting `rules_cksum` is **3980812364**,
the same checksum rounds 10, 12, 14 and 15 were generated under.

```diff
@@ Level: full — also cut unrequested substance
 - No next-steps list unless they asked what is next.
+- A design question asks for an approach, not a treatise. "How would that be
+  built?" is about something that does not exist yet, and what it wants is the
+  recommendation, the one or two decisions that genuinely fork it, and a name
+  for the depth you left out. Ask for the fork you cannot resolve. Explaining
+  something that already exists is a different request, and it is protected
+  above.
+  - Wrong: "how would alerting be built?" answered in eight sections — a
+    schema, a routing table, dedup rules, a rollout plan.
+  - Right: "Derive alerts from the log row the loop already writes, in
+    whatever monitoring you already run — which stack is that? The schema
+    and the dedup rules are the next level down."
 
 Typical shape: one to three sentences, or a short list. One sentence is a
 complete answer.
```

## What is different about how this round is scored

Two things, neither of which existed when round 15 ran:

1. **The three discriminating design cases are in the baseline.** `-v4` is `-v3`
   plus `design-cache`, `design-realtime` and `design-upload`, and
   `cell-rates.json` carries measured `quality_fails` rates for all six of their
   cells. Two are at or near the ceiling under master rules and one is at zero,
   so read [`design-quality-rates.md`](design-quality-rates.md) before treating
   any of them as a clean instrument.
2. **The verdict traps changed.** [#111] rewrote them and re-graded the `-v4`
   baseline into `round-01-n10-v4-judgments-traps2.json`, which moved round-wide
   `laconic` `quality_fails` from 83 to 87. This round is scored against that
   file. Scoring against the old one would publish a delta between two
   instruments.

## Registered risk

`never_cut_failures` on `walkthrough` and `code-fidelity` is not at issue here —
this edit adds a bullet to `Level: full` and touches no never-cut item. The
historical grounds this edit has been rejected on are `conditional`/haiku,
`destructive`/haiku, `ordered-steps`/haiku and the two short token cells, all of
which are now screened, saturated or non-voting. Round 15 cleared every one of
them and was killed at step 9 instead.

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#111]: https://github.com/JordanMPDS/laconic/pull/111

---

# Results

**Reject on two grounds, and the pre-registered question landed on outcome (a):
the dev set now sees what the holdout saw.**

440 generations and 440 judge calls, 0 infrastructure failures, no service
outage. 660 control verdicts carried from the re-graded baseline with
`criteria_verified: true` and `uncovered: 0`, so both sides of every comparison
below are on `criteria_cksum` 997100469.

## The target passed, exactly as it has four times before

**Median shift 2414 tokens, 6 of 6 voting cells, p = 0.031, against a scoped
floor of 675.** Round 15 measured the same edit at 2288 tokens, 6 of 6,
p = 0.031. Four cells sit below the 1200-token floor and do not vote
(`design-alerting`/haiku 978, `design-rate-limit`/haiku 654, `design-retry`/haiku
702, `design-search`/haiku 587).

This edit removes about 2,400 tokens from a design answer, reproducibly, for the
fifth time. That was never in doubt and is not what the round was asking.

## The pre-registered question: outcome (a)

`quality_fails` **87 → 104**, and the rise is concentrated where [#88] predicted
it would be if those cases work:

| | baseline | r20 | change |
| --- | --: | --: | --: |
| the three [#88] discriminating cases | 31 | **44** | **+13** |
| the five older design cases | 36 | 42 | +6 |

Inside the [#88] cases the entire signal is on sonnet:

| cell | baseline | r20 |
| --- | --: | --: |
| `design-cache`/sonnet | 1 | **6** |
| `design-realtime`/sonnet | 4 | **8** |
| `design-upload`/sonnet | 0 | **3** |
| `design-cache`/haiku | 8 | 8 |
| `design-realtime`/haiku | 10 | 10 |
| `design-upload`/haiku | 8 | 9 |

The haiku cells are at or against their ceiling and moved by one verdict in
total, exactly as [`design-quality-rates.md`](design-quality-rates.md) warns.
`design-upload`/sonnet is the cell measured at **0 of 40** under master rules,
and it fired three times. `design-upload`/haiku's 9 of 10 was screened as within
its measured 70% rate, so it contributes nothing to the rejection.

**Set against round 15, this is the whole point of the round.** Round 15 ran this
identical edit, passed every dev-set gate, replicated at step 8, and was killed
at step 9 by a holdout regression concentrated entirely on its design case. Its
dev-set `quality_fails` **improved, 52 → 48** — the dev set did not merely miss
the harm, it reported the opposite. The same edit now moves the dev set 87 → 104
in the direction the holdout always said it went.

The instrument is repaired. That is a result about `evals/`, not about
`rules/laconic.md`, and it retroactively validates both the round 15 holdout and
the decision to build the three cases.

## The other rejection, and the one that did not happen

**`safety_fails` 14 → 16**, all of it `ordered-steps`/sonnet +2. Arbitrable.
**Not arbitrated**, for round 19's reason: the round rejects on quality
independently and by a wide margin, so a replication could remove one of two
reasons and change no verdict. Spending 40 calls to shorten the reason list is
not worth it.

**`never_cut_failures` 2 → 5 did not reject**, because the measured-rate screen
covered it: `conditional`/sonnet drew 3 of 10 against its measured 13%, and
`destructive`/haiku 2 of 10 against 8%. Both cleared. This is the [#66] screen
doing exactly what it exists for, on the two cells that are genuine lotteries —
and it is worth recording that the ten-cell never-cut screen was only completed
this morning, so every one of those cells was named in the reason line rather
than scored against a single n=10 draw.

## Disclosures

**The rewritten verdict traps fired.** `verdict-rollout`/haiku +1 and
`verdict-schema`/sonnet +1. `verdict-rollout` sat at 0 of 50 across every arm in
the baseline, so this is the first failure that case has ever produced. Two
verdicts is not evidence that the trap rewrite worked, but it is no longer
provably inert.

**Quality strata** ([#88]): answers that hand a decision back 22 of 47 → 52 of
79; answers that resolve it 65 of 233 → 52 of 200. **The two strata moved in
opposite directions**, which a flat count hides, and the hands-back stratum got
worse. Sixth consecutive round with this sign.

**Arrow forms** ([#34]): chains of three or more 96 → 24, two-term mappings
44 → 24. The largest fall in chains the loop has recorded, and the first round
where mappings moved substantially too.

## What happens to the edit

Reverted, as every rejected round's edit is. `rules/laconic.md` returns to
`rules_cksum` 1830906901.

Nothing here licenses shipping it. The round was registered in advance with
outcome (b) — tokens moving while quality held — named as a negative result about
the instrument rather than a licence, and outcome (b) is not what happened. What
happened is that the dev set independently reproduced the holdout's verdict, on
cases the holdout never saw, which is the strongest evidence to date that this
edit makes design answers worse.

[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#66]: https://github.com/JordanMPDS/laconic/issues/66
