# Round 122: a design answer renders volunteered scope it should only name (#46)

**Registration. Nothing below the results line has been computed**, except the
figures quoted from the prechecks and earlier rounds, which are merged. This
file and the edit (with regenerated `rules/dist/*.md`) are committed before any
confirming generation. No harness, scorer or case changes.

`bash tools/candidate-due.sh` exited 1 at registration: round 121 measured
(its precheck did not fire and the edit was withdrawn unrun), so round 122 owes
a candidate and carries one, under **The edit** below. `bash tools/release-due.sh`
exited 0: v0.3.10 is tagged and current.

Decided on **sonnet**. #46 is a sonnet-shaped finding — the one-turn and length
inflation it documents were measured on sonnet, and the current CLI reads the
fixtures reliably on every model, so sonnet is where the live residual sits
(prechecks below).

## Why this round exists

[#46] reported a bare "how would that be built?" answered in ~1,400 words across
eight H2 sections — a schema, a 9-row routing table, dedup rules, an end-of-day
digest, a testing note — of which four sections were scope the user never asked
for. Two halves of that report have diverged on the current instrument:

- **The reading half is saturated.** On CLI 2.1.310, master rules, the laconic
  arm on sonnet opens the fixtures every time: one-turn **0/36** on the three
  quality-graded cases (`design-cache`, `design-realtime`, `design-upload`) and
  **0/50** on the five older design cases (`design-alerting`, `design-audit-log`,
  `design-search`, `design-rate-limit`, `design-retry`). Judge-graded quality on
  the three is 0%, 0%, 15% fail — the one-turn ungrounded failure the rounds 07
  to 21 family chased no longer reproduces. The edit a round would once have
  proposed for the reading half has no headroom.
- **The length half is alive.** Those same grounded answers are still
  treatises. Median output on sonnet, master rules:

  | case | median output_tokens |
  |---|--:|
  | `design-audit-log` | 2494 |
  | `design-cache` | 2160 |
  | `design-alerting` | 1928 |
  | `design-upload` | 1841 |
  | `design-retry` | 1775 |
  | `design-rate-limit` | 1598 |
  | `design-search` | 1529 |
  | `design-realtime` | 1352 |

  The model reads, gives the right recommendation, then volunteers the schema,
  the routing table, the dedup rules and the rollout plan #46 named. The
  design-question bullet already says the approach is "the recommendation, the
  one or two decisions that genuinely fork it, and a name for the depth you left
  out," and its Wrong example already lists those very artifacts — and it is not
  followed on length.

Because reading is saturated (one-turn 0 on both sides), every design cell
reads in both arms, so all eight seat the `output_tokens` sign test with no
reading-stratum crossing to drop a cell ([#131]).

## Hypothesis

Editing the design-question "earned by reading" sub-bullet to key the cut on
**provenance** — kept material is whatever the user asked for or read in the
files, everything else is named not rendered — should move `output_tokens`
**down** on `design-alerting`, `design-audit-log`, `design-search`,
`design-rate-limit`, `design-retry`, `design-cache`, `design-realtime`,
`design-upload` / sonnet, with judge-graded quality not regressing.

- **Primary target:** `output_tokens`, `--target-cases` the eight design cases,
  `--target-models sonnet`, grounded stratum. Sign test across the eight cells
  plus a median shift larger than the committed floor.
- **Fatal guard:** `quality_fails` round-wide over the generated cells must not
  rise; `turns` must not rise (the edit cuts rendered output, not reading, so
  `num_turns` should hold). A quality regression rejects whatever the length did.
- **Disclosed secondary, not a gate:** rendered-artifact count per answer
  (fenced code blocks and Markdown tables, by regex), control against edit, to
  show whether the cut landed on the rendered artifacts rather than on prose.
- **Looks:** one. The round opens at 15 reps a side on the eight cases and is
  scored once; `report.py --looks 1`. A decision to extend would be a new round,
  not a second look at this one.

## Why provenance, and its origin

The design and both forks below come from Kimi, via `tools/consult.sh` (Codex
and DeepSeek timed out on both consults). The first instinct was to sharpen the
reading requirement in the same slot; the precheck killed it. The second was to
cut by length ("named, not rendered"); Kimi's objection is the keystone of this
round:

> "named, not rendered" alone is same-slot noise … The reason the current
> bullet gets ignored is that it describes what the answer *is* but gives the
> model no procedure at the moment it's deciding whether to open a code fence. A
> provenance test is that procedure, applied per artifact: *did the user ask for
> this, or did I read it in the files?* … And it's why this cut is safe where
> the holdout regression wasn't: last time you cut by form, this time by origin.

That is the answer to the standing worry about [#46] length edits. Rounds 07 to
15 cut design answers by form and round 15's edit regressed on the holdout
because cutting length cut grounding. Cutting by **origin** cannot: read
material is kept by definition, so the only thing left to drop is the
volunteered artifact. The protected-code clarification closes the loophole #46
named — the model treating an invented schema as Never-cut code.

## Pre-mortem

The most likely failure is the point estimate moving **with** the registered
direction and not separating — a `noise-floor` reject. The bullet already names
these artifacts in a Wrong example and is ignored on length, so the provenance
rewrite may be one more thing in a slot the model does not consult at the moment
it opens a code fence. Kimi flags a second route to the same null: the
enumerated Wrong list may be *priming* the artifacts it bans, keeping a schema
and a routing table salient for an alerting question. A third, less likely
failure is a `quality_fails` rise if the provenance frame makes the model drop a
constraint it actually read — the guard exists for exactly this, and the origin
keying is the reason to expect it not to fire.

**Pre-registered backstop, not co-shipped:** if this round nulls, round 123 does
*not* reword the same slot. It pulls the artifact enumeration out of the Wrong
example and adds a structural cap (at most one rendered artifact, and only one
that passes the provenance test) — a frame change, not a wording tweak. Naming
it here keeps a null interpretable: it sends the next round to structure.

## The edit

One sub-bullet of the `level: full` design-question bullet, replaced:

```diff
-  - **This licence is earned by reading, not by being brief.** It covers an
-    approach derived from the files the question is about. An approach recalled
-    from general practice has not earned it and stays subject to everything
-    above. Read what the question is about, then be brief about it.
+  - **This licence is earned by reading, not by being brief.** Kept material is
+    whatever the user asked for or you found in the files, including rephrased;
+    everything else is volunteered scope and gets a name, not a body. A schema,
+    a routing table, a dedup rule or a rollout order is mentioned in a clause,
+    not delivered — and the Never-cut list protects code you were shown, not an
+    artifact you invented. An approach that engages nothing from the files has
+    not earned the licence and stays subject to everything above.
```

The Wrong/Right examples are left unchanged: this round pulls one lever, the
sub-bullet text. The enumeration's priming is Kimi's Fork 2 and is held for the
backstop so a result is attributable to the provenance rewrite alone.

## Results

_Pending generation._
