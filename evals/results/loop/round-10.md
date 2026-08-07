# Round 10 — relocating the design-question licence instead of rewording it

**Date:** 2026-08-07
**Baseline:** `evals/snapshots/loop/round-01-n10.json`
**Status:** hypothesis registered; snapshot not yet generated

## Hypothesis (registered before generation)

> Moving the design-question licence out of the "Never cut" list and into the
> `level: full` section — where it is subordinate to every never-cut
> protection by placement rather than by assertion — moves `output_tokens`
> down on `design-alerting`, `design-audit-log`, `design-search` across all
> six cells past the matched all-cells scoped floor, while `safety_fails` and
> `never_cut_failures` hold at the baseline's 6 and 2.

`--target-cases design-alerting,design-audit-log,design-search`, the same
three cases rounds 07, 08 and 09 named, so this round is directly comparable
against 18 of 18 scoped cells already down.

## Why relocation rather than a third rewording

Rounds 07, 08 and 09 all put the licence inside the never-cut list and all
rejected on `ordered-steps`/haiku. Round 07 wrote a bound; rounds 08 and 09
added mutual exclusion in both directions, including an explicit "this bullet
outranks the approach license above". The cell read 6, 3 and 5 against a
baseline of 2. Prose asserting precedence between two never-cut bullets has
been tried twice and has not moved it.

The never-cut section is exempt from level rules by its own header — "every
level, including ultra" — and the document says so again at the top: laconic
"governs volunteered content; it never truncates requested content." A licence
living in `level: full` therefore cannot reach never-cut material at all,
without any sentence claiming it cannot. That is the mechanism under test:
placement instead of assertion.

## The edit

Never-cut is byte-identical to master. The whole diff is an addition to
`level: full`:

```
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
```

The one clause about the never-cut bullet — "explaining something that
already exists is a different request" — distinguishes two kinds of question
rather than ranking two bullets. A design question is about a thing that does
not exist; an explanation is about a thing that does. That is a property of
the question, where rounds 08 and 09 asked the model to predict a property of
its own answer (would someone follow this as steps?).

## Two consequences, both accepted before the numbers

1. **The licence no longer applies at `lite`.** Level sections slice, so a
   rule in `level: full` is absent from `laconic-lite.md`. This is the right
   place for it: lite "keeps full reasoning, context, and trade-offs" and cuts
   only ceremony, so a licence to withhold substance does not belong there.
   The benchmark runs at `full`, so no measurement changes.
2. **The licence may simply not fire.** The never-cut list protects "how", and
   a design question says "how". If the model resolves that in never-cut's
   favour every time, tokens will not move and this round fails on its target
   rather than on a safety cell. That is a real outcome and will be recorded
   as one.
