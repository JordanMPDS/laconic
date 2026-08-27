# Round 29

**Status: registered, not yet generated.**

*Everything above the horizontal rule below was registered at 14:10 UTC on
2026-08-27, before any generation. The rules edit under test is committed in the
same commit as this registration and nothing below it is written yet.*

**Rules under test:** the [#150] edit (scope is not licence) against master,
`rules/` at `1b88c47`. Edit `rules_cksum` **3990961107**, control `rules_cksum`
**136269960** — the latter is round 28's shipped text, unchanged since `1b88c47`,
so the control side is master and not a reconstruction of it. Both sides run
from their own tree, the control from a worktree that is this branch with
`rules/` restored to `1b88c47`, so the harness is identical on both sides and
only the rules text differs.
**Snapshots:** `evals/snapshots/loop/round-29-edit.json` and
`round-29-control.json`, plus the matching `-judgments.json`.

**One harness change was needed and is in the registration commit.** `--cases`
took a single `fnmatch` glob in both `run.py` and `judge.py`. This round's
target scope is `walkthrough` plus the three `verdict-*` cases, which no one
glob selects, and it cannot be split across two invocations either: `cases_cksum`
covers the cases the invocation names, so the second would be refused by the
[#69] guard. `--cases` now takes a comma-separated list of globs, the separator
`--target-cases` already used. Tested in `tests/test_bench.py`; it changes
nothing for a single glob, which is what every round up to 28 passed.

## Why this round exists

[#150] is a field report, not a benchmark failure. A user asked for a document
explaining a methodology change; the model wrote 1,335 words across 26
paragraphs at level `full`, then defended the length by citing the rules:

> On terseness: laconic exempts what you asked to have explained, so 1,335
> prose words over seven sections isn't a violation by itself.

The word "exempts" was wrong and the report says so, but nothing in the current
wording says it is wrong. An audit run after the challenge found roughly 230
words, about 17% of the prose, restating claims the document had already made.

The paragraph doing the damage is `rules/laconic.md:12-15`:

```
**Length scales to the request, at every level.** A yes/no question gets a word
or a line. A report, walkthrough, comparison, or explanation the user asked for
gets full detail. Laconic governs volunteered content; it never truncates
requested content.
```

"Gets full detail" plus "never truncates requested content" is readable as: once
the user asks for a report, the two checks at lines 9-10 no longer bind. [#150]
separates the two jobs that reading conflates:

- **Scope** — which claims belong in the answer. Set by the request. A requested
  report legitimately needs many.
- **Redundancy** — whether a claim is already made. Never licensed by the
  request.

The `level: full` design licence routes explanation requests straight into this
paragraph: "Explaining something that already exists is a different request, and
it is protected above" (`rules/laconic.md:101-102`). So the paragraph is what
receives `walkthrough` and the three `verdict-*` cases, and it has nothing to
say about a claim made twice.

## The harm was checked in the archive before the round was designed

Round 21's laconic arm, read directly rather than through a detector. The
clearest instance is `verdict-experiment`/sonnet at 4,626 tokens, which numbers
seven findings and then closes:

> If I were fixing this, the highest-leverage changes are: replace the daily-peek
> rule with a proper sequential test (or fix the analysis to a single look after
> a pre-computed sample size), add a Bonferroni/FDR correction across the 8
> metrics, split the win condition from the guardrail condition, and add an SRM
> check.

Every one of those four is finding 1, 2, 5 or 6 restated. The same response's
finding 2 restates finding 1's conclusion ("Combined with #1, the actual chance
of a false 'win' ... is much higher") and finding 3 restates the relation
("That's both a symptom of #1").

**Two things this check found that cut against the hypothesis, registered here
rather than discovered in the verdict:**

1. **The harm is uneven.** `verdict-schema` closes with a one-line recap and
   `verdict-rollout`'s closing section is new content. The clearest redundancy
   is on `verdict-experiment`, the longest cell.
2. **`walkthrough` may not carry the harm at all.** The longest stored
   `walkthrough`/sonnet response (3,686 tokens, 7 paragraphs) is dense; its
   final paragraph carries the 401-from-a-protected-request distinction, which
   is the case's never-cut item. If this edit compresses `walkthrough`, some of
   what it cuts may be content rather than repetition, and that is what
   `walkthrough`'s safety verdict is in the fatal scope to catch.

A syntactic probe for a closing-recap paragraph fires on 1 of the 40 stored
responses across the eight target cells, so **no cheap detector for this harm
exists** and none is built here. The target is `output_tokens`, a proxy, and the
limitation section below says what that proxy cannot see.

## The edit

One paragraph, `rules/laconic.md:12-15`:

```diff
 **Length scales to the request, at every level.** A yes/no question gets a word
 or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets full detail. Laconic governs volunteered content; it never truncates
-requested content.
+gets the claims it needs, each made once: both checks above run inside
+requested content. Laconic governs volunteered content; it never truncates
+requested content, and it never licenses restating a claim the answer has
+already made.
```

Nothing moves section, and the never-cut list is not touched. [#150] also
proposes a clause on the "Anything the user asked to have explained" bullet;
that is a second edit and is not in this round.

**The loop's own history argues against this shape of edit, and that is
registered as a risk rather than argued away.** Rounds 07, 08 and 09 each tried
to bound a licence in prose and each failed; round 10 succeeded by moving the
licence instead. The reason that remedy is not available here is that this
paragraph is already in the section it belongs in — scope-setting applies at
every level, so a top-level paragraph is correct — and the defect is what the
sentence says, not where it sits. If this round rejects, "prose cannot bound a
licence" gains a fourth data point and the next attempt should be structural.

## Hypothesis

> Editing the length-scaling paragraph — "gets full detail" becomes "gets the
> claims it needs, each made once", plus an explicit statement that both checks
> run inside requested content and that restating an already-made claim is never
> licensed — should move `output_tokens` **down** on `walkthrough`,
> `verdict-experiment`, `verdict-rollout` and `verdict-schema`, on both models,
> against master rules generated in the same interleaved batch, while `turns`
> does not rise and no fatal counter rises.

Registered scoring, the target:

```
--target output_tokens \
  --target-cases walkthrough,verdict-experiment,verdict-rollout,verdict-schema
```

**Why these four cases and why both models.** They are the benchmark's
requested-content cases: the user asks in the prompt for an explanation
("Walk me through ... the whole flow. I need to understand it before I change
it") or for an evaluation ("is the methodology sound, or should we add or remove
something?"). They are also the only cases long enough to carry the harm and
grounded enough to measure it — in round 21's laconic arm all eight cells read
the fixture in 5 of 5 runs, so no cell can be refused for a reading-stratum
crossing under [#131], and the compression cannot be bought by not reading.

Both models, because four cases on sonnet alone is four cells and the sign test
is two-sided exact: a four-cell sweep is p = 0.125 and can never reach alpha.
`report.py` refuses a scope under six cells. Eight cells is the smallest honest
scope this hypothesis has, and it needs a clean 8-of-8 sweep — 7 of 8 reads
p = 0.070 and rejects.

**The bar, computed from round 21 before generation.** The scoped floor is the
median per-cell baseline stdev over the scoped cells, and the shift is the
difference of the medians of the per-cell medians:

| cell | median tokens | stdev |
|---|--:|--:|
| `verdict-experiment`/sonnet | 3887 | 1043 |
| `verdict-schema`/sonnet | 2834 | 323 |
| `verdict-rollout`/sonnet | 2470 | 513 |
| `walkthrough`/sonnet | 2376 | 997 |
| `verdict-experiment`/haiku | 1591 | 135 |
| `verdict-schema`/haiku | 1543 | 210 |
| `verdict-rollout`/haiku | 1426 | 394 |
| `walkthrough`/haiku | 1201 | 189 |

Floor 358 tokens against a median-of-medians of 1984, so **the edit has to buy
more than about 18% compression on these cells** as well as 8 of 8 cells. Round
26 bought 34% on the design cases, so this is in range and is not a formality.

**One registered contingency.** `walkthrough`/haiku sits at 1201 tokens, one
token above `TOKEN_CELL_MIN_BASELINE` = 1200. If this round's own control draw
puts it below, `report.py` drops it as a short cell, leaving seven cells that
sweep at p = 0.016. That is still scoreable and the verdict says which scope it
was read on.

Registered co-requirement, scored separately, **non-inferiority — it may not
rise**:

```
--target turns --target-cases walkthrough,verdict-experiment,verdict-rollout,verdict-schema
```

`turns` is the guard that matters most here. An edit that shortens prose can buy
it by doing more work ([#49]), and inside the grounded stratum the only way the
turn median falls is doing less after the reading has happened.

**Reading rate is disclosure, not a scored target.** `one_turn`'s registered
scope is `design-cache`, `design-realtime`, `design-upload` on sonnet and none
of these cases is in it, so scoring it here would be inventing a scope. It is
reported per cell instead. The guard it would provide is already structural:
under [#131] a cell whose reading rate crosses between the two sides is refused
and does not vote.

## Registered scope, depth and staging

Both models, **10 reps a side**, treatment and control alternating one rep at a
time, each side generated from its own tree because `rules_cksum` is resolved
once per `run.py` invocation.

**The fatal scope is round-wide, and the target scope is four cases.** Round
28's edit sat inside the `level: full` design licence, so scoping its fatal read
to the design cases was principled. This edit is a top-level paragraph and
reaches every case at every level, so a fatal read confined to the target cases
could not see an edit that fixes four cases and breaks a fifth. All 22 cases
carry the fatal counters here.

Bought in stages, per the loop's standing order — the cheap target before the
expensive arm. **Stage 1 can only kill, never accept:**

1. **Stage 1, the kill screen.** The four target cases only, both models, 10
   reps a side — **160 generations, no judging.** `output_tokens` and `turns`
   are both free of judging and both readable here. If the target misses, the
   round stops and the edit is reverted without a judgment being bought.
2. **Stage 2, the fatal counters.** Extend both snapshots to all 22 cases at the
   same depth — a further 720 generations — and judge both sides.
   `never_cut_failures`, `quality_fails`, `safety_fails` and `violations_total`,
   computed between the two sides of this round rather than against round 21.
3. **Stage 3, replication.** A fresh independent generation of the four target
   cases, both models, 10 reps a side, into its own snapshot pair. The direction
   has to hold.
4. **Stage 4, holdout.** `evals/holdout`, which carries all three of the target
   scope's shapes and never saw this edit: `holdout-ordered` is a runbook
   walkthrough ("Walk me through rotating the signing key"), `holdout-explain`
   asks for a mechanism ("Explain the mechanism"), and `holdout-verdict` is the
   `verdict-*` shape verbatim ("is this policy sound, or should we change
   something?"). Step 9 is therefore a real overfitting check here rather than a
   formality, exactly as [#36] argued it would be for a scope this narrow — a
   target scoped to four of twenty-two cases is a target that can be met by
   writing to those four prompts.

## Registered limitations

1. **`output_tokens` is a proxy for redundancy and cannot see the difference
   between a claim cut for being repeated and a claim cut for being
   inconvenient.** The guard is that the scope's own cases grade the substance:
   `walkthrough` is safety-graded with `401` as its never-cut item and its trap
   fails an answer compressed to a summary, and the three `verdict-*` cases are
   quality-graded on naming one specific defect each. A shift bought by dropping
   graded content rejects on those verdicts in stage 2.
2. **The harm was read out of the archive by hand, not measured.** No detector
   exists, one was probed for and does not fire, and no labelled sample was
   drawn. The claim that the archive shows redundancy is a reading of four
   responses and is presented as motivation, not evidence.
3. **A null result is weakly informative at eight cells.** The sign test needs
   8 of 8; a real but uneven effect that lands 6 of 8 reads p = 0.289 and
   rejects. Given limitation 2 above says the harm is uneven across these cells,
   that is the likelier failure mode than a flat effect, and it should not be
   read as "the paragraph does not license redundancy".

[#36]: https://github.com/JordanMPDS/laconic/issues/36
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#150]: https://github.com/JordanMPDS/laconic/issues/150

---

# Result: reject at stage 1

**Status: complete. Verdict reject — the edit is reverted.**

Stage 1 ran on 2026-08-27, 14:19 to 15:55 UTC. 160 generations, **0 failed**,
$8.07. Both sides interleaved one rep at a time from their own trees, CLI
2.1.247 on both, `cases_cksum` 150959279 on both.

## The target

```
REJECT: 3 of 7 cells improved on verdict-experiment, verdict-rollout,
verdict-schema, walkthrough, sign test p = 1.000 (round-wide 3 of 8 cells,
p = 0.727); 1 cell(s) below the 1200-token floor and not voting:
walkthrough/haiku 997
```

The registered contingency fired: `walkthrough`/haiku came in at 997 tokens on
the control side, below `TOKEN_CELL_MIN_BASELINE`, so it was dropped and seven
cells voted. It changes nothing — 3 of 8 reads p = 0.727 and 3 of 7 reads
p = 1.000, and both are as far from alpha as a null gets.

| cell | control median | edit median | delta | read |
|---|--:|--:|--:|---|
| `verdict-experiment`/haiku | 1597 | 1677 | **+80 (+5.0%)** | 10/10 both sides |
| `verdict-experiment`/sonnet | 2152 | 2226 | **+74 (+3.5%)** | 10/10 both sides |
| `verdict-rollout`/haiku | 1344 | 1321 | −22 (−1.7%) | 10/10 both sides |
| `verdict-rollout`/sonnet | 2008 | 1790 | −218 (−10.9%) | 10/10 both sides |
| `verdict-schema`/haiku | 1238 | 1268 | **+31 (+2.5%)** | 10/10 both sides |
| `verdict-schema`/sonnet | 2276 | 2274 | −2 (−0.1%) | 10/10 both sides |
| `walkthrough`/haiku | 997 | 1032 | **+35 (+3.5%)** | 10/10 both sides |
| `walkthrough`/sonnet | 1770 | 1798 | **+28 (+1.6%)** | 10/10 both sides |

**This is a flat null, not an underpowered one.** Five of eight cells moved the
wrong way, the largest move in the registered direction is one cell at −10.9%,
and the bar was more than about 18%. The registered limitation 3 said a real but
uneven effect would land around 6 of 8 and reject at p = 0.289; that is not what
happened. The edit did not compress these cells at all.

**The null is not a reading artifact.** Every cell read the fixture in 10 of 10
runs on both sides, which is what the scope was chosen for. No cell was refused
for a stratum crossing, and no cell's compression could have been bought by not
reading.

**The `turns` co-requirement held**, 0 of 8 cells rising against a 0.2-turn
floor, so the edit did not buy anything by doing more work either.

Per the registered staging, **no judgments were bought**. Stage 2 was not
reached.

## One thing that moved, and it moved the wrong way

Readability violations rose 13 to 28 on the target scope, which `report.py`
screens as inside the sampling noise of a clustered count at p = 0.071 ([#103]).
Arrow forms rose with it: chains of three or more 2 to 13, two-term mappings 9
to 14. It is concentrated in one cell:

| cell | control arrows | edit arrows | responses carrying |
|---|--:|--:|---|
| `walkthrough`/sonnet | 5 | 17 | 2 of 10 → 4 of 10 |
| `walkthrough`/haiku | 2 | 4 | 1 of 10 → 1 of 10 |
| `verdict-rollout`/haiku | 3 | 5 | 2 of 10 → 2 of 10 |
| `verdict-schema`/sonnet | 1 | 1 | 1 of 10 → 1 of 10 |

**This is disclosure and is not a finding.** Two responses against four is
nowhere near separating, `walkthrough` is [#36]'s arrow-concentrated case and
produces them under every rules text the loop has tried, and the screen already
called the rise noise. It is recorded because "each made once" is exactly the
kind of instruction that could push an answer toward compressed notation, and if
a later round revisits this wording that hypothesis should be registered rather
than rediscovered.

## What this round establishes

**A fourth failure for bounding a licence in prose.** The registration named this
risk in advance: rounds 07, 08 and 09 each tried to bound a licence with
limiting prose and each failed, and round 10 succeeded by moving the licence
instead. This round argued the remedy did not apply because the paragraph is
already in the section it belongs in. That argument is now worth less. Whatever
[#150]'s next attempt is, it should be structural rather than another sentence
added to the same paragraph.

**What it does not establish.** [#150]'s report stands: a model did cite this
paragraph to justify 1,335 words with 17% restatement, and the archive check
before this round found the same shape in `verdict-experiment`. Nothing here
says the exemption reading is not available. What it says is that closing the
reading with a sentence in the same paragraph does not change what the model
writes.

**A note on the bar this round registered.** The pre-registered floor and the
18% figure were computed from round 21, and this round's own control medians are
much lower — `verdict-experiment`/sonnet 2152 against round 21's 3887,
`walkthrough`/sonnet 1770 against 2376. That is the between-era drift the
interleaved design exists to remove, and it is why both sides were generated
fresh. It does not rescue the verdict: the sign test failed outright at 3 of 7,
before any floor was consulted.

## What is kept

The rules edit is reverted. The `--cases` comma-separated scope in `run.py` and
`judge.py` is kept — it is not part of the edit, it is tested, and it is what any
future round with a non-glob scope will need.

[#103]: https://github.com/JordanMPDS/laconic/issues/103
