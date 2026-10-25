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
- **Looks:** one. The round runs 10 reps a side on the eight cases and is
  scored once; `report.py --looks 1`. The `output_tokens` sign test counts
  cells, not reps, and round 26 read 8/8 at 25 reps where 10 would very likely
  have read the same, so 10 is the buy. A decision to extend would be a new
  round, not a second look at this one.

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

### Generation (160 calls)

Both sides from two trees at once — the edit from this branch, the control
from a worktree of `origin/master` at `12f4ebb` — 10 reps a cell, sonnet,
`--concurrency 2` on each:

```bash
CELLS='design-alerting:sonnet,design-audit-log:sonnet,design-cache:sonnet,design-rate-limit:sonnet,design-realtime:sonnet,design-retry:sonnet,design-search:sonnet,design-upload:sonnet'
python3 evals/bench/run.py --arms laconic --reps 10 --cells "$CELLS" --concurrency 2 \
  --snapshot evals/snapshots/loop/round-122-edit.json &
(cd /tmp/laconic-control-122 && python3 evals/bench/run.py --arms laconic --reps 10 \
  --cells "$CELLS" --concurrency 2 \
  --snapshot /home/jordan/projects/laconic/evals/snapshots/loop/round-122-control.json) &
wait
python3 evals/bench/release.py evals/snapshots/loop/round-122-{control,edit}.json
python3 evals/bench/report.py --results evals/snapshots/loop/round-122-edit.json \
  --judgments /dev/null --against evals/snapshots/loop/round-122-control.json \
  --against-judgments /dev/null --target output_tokens \
  --target-cases design-alerting,design-audit-log,design-search,design-rate-limit,design-retry,design-cache,design-realtime,design-upload \
  --target-models sonnet --looks 1
```

The first pass stopped at a usage limit after 31 and 33 runs (02:57 to 03:05)
and was resumed by key at 04:22 under the same cells; 80 runs a side, 0
failed, all on CLI 2.1.310. `release.py`: no unreadable span, no arm imbalanced
across a release. About $3.70 of generation a side.

Judging was not bought. The registration made the token target the primary and
`quality_fails` a guard that can only reject, so once the primary failed no
verdict could change the outcome.

## Result: rejected (`noise-floor`)

**Reject.** The point estimate moved in the registered direction and did not
separate: 6 of 8 cells fell, sign test **p = 0.289** against alpha 0.05 at one
declared look. `rules/laconic.md` and `rules/dist/` are reverted to master in
this PR. The `#49` turn gate held (+0.0 turns over 8 grounded cells, 1 rising).

| case (sonnet) | control tokens | edit tokens | change | control words | edit words | control artifacts | edit artifacts |
|---|--:|--:|--:|--:|--:|--:|--:|
| `design-alerting` | 1695 | 1562 | -7.9% | 283 | 292 | 0.00 | 0.00 |
| `design-audit-log` | 2869 | 2450 | -14.6% | 334 | 315 | 0.00 | 0.00 |
| `design-cache` | 2142 | 1874 | -12.5% | 280 | 274 | 0.20 | 0.00 |
| `design-rate-limit` | 1526 | 1490 | -2.3% | 276 | 270 | 0.00 | 0.00 |
| `design-realtime` | 1257 | 1339 | +6.5% | 229 | 221 | 0.00 | 0.00 |
| `design-retry` | 1661 | 1720 | +3.6% | 320 | 303 | 0.00 | 0.00 |
| `design-search` | 1630 | 1130 | -30.7% | 223 | 199 | 1.20 | 0.00 |
| `design-upload` | 1912 | 1608 | -15.9% | 301 | 289 | 0.00 | 0.00 |

Tokens and words are per-cell medians over 10 runs. "Artifacts" is the
registered disclosed secondary: fenced code blocks plus Markdown tables per
answer, by regex. Every run in both arms opened a fixture (one-turn 0/80 a
side), so all eight cells compared inside the grounded stratum.

### What the round found instead

**The treatise is not in the answer, so the premise the registration quoted
does not hold.** The registration read median `output_tokens` of 1,352 to 2,494
as "those same grounded answers are still treatises." They are not. The
visible answer is a median **283 words** on the control (precheck: 281) and
**278** on the edit; the longest of 160 answers is 433 words and none passes
600. [#46]'s report was ~1,400 words across eight sections. Tool inputs are a
median 315 characters a run, so neither the prose nor the tool calls account
for the ~1,760 median output tokens; the bulk is reasoning the user never sees,
at about 6 tokens per visible word, and words and tokens correlate at only
0.52 to 0.56 across runs.

**And the volunteered artifacts are almost absent at master.** The control
rendered 0.175 artifacts per answer, 14 in 80 answers, 12 of them in
`design-search`. The edit took that to 0/80 — the provenance clause did reach
the rendered artifact — but there was little to remove, and the visible prose
moved 283 to 278 words.

So the round measured a rule about rendered scope against a counter that is
mostly unrendered. The 8.9% fall in pooled median tokens (1,764 to 1,608) may
be real and is not separable at this size; either way it is a change in hidden
reasoning more than in the answer [#46] complained about.

### The pre-registered backstop has no headroom

The registration named round 123's backstop as pulling the artifact enumeration
out of the Wrong example and capping rendered artifacts at one. At master that
cap binds on 14 of 80 answers, all but two on one case, and the answers are
already a fifth of [#46]'s length. **The backstop is withdrawn on this
evidence rather than bought:** it would cut a behaviour that barely occurs, and
scoring it on `output_tokens` would repeat this round's mismatch. A further
[#46] length round would need a visible-length measure (prose words, not
`output_tokens`) and a precheck showing answers that are actually long.

### Pre-mortem against the result

The pre-mortem's most likely failure is what happened: the estimate moved with
the direction and did not separate. Its reason was wrong, though. It expected
the model to ignore the rewritten slot; the edit did reach what it targeted
(artifacts 14 to 0), and the null comes from the target being nearly absent and
the counter measuring something else.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#131]: https://github.com/JordanMPDS/laconic/issues/131
