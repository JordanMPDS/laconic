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

*(appended after the round; nothing above this line was written with knowledge
of the numbers)*
