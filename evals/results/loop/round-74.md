# Round 74: the record you checked, and whether it is inside the answer

**Registration. Nothing below the results line has been computed**, with the
exception of the base figures marked as computed and dated in place, which come
from [round 73](round-73.md)'s already-committed *edit*-side snapshots — the
same rules text this round controls against, byte for byte — and the power table
resampled from them. This file, the edit and the regenerated `rules/dist/*.md`
are committed in one commit before any generation, following
[round 38](round-38.md) through [round 73](round-73.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_echo.py --title 'Round 74: the record you checked' \
  --control evals/snapshots/loop/round-74-control-*.json \
  --edit    evals/snapshots/loop/round-74-edit-*.json
```

## Why this round exists, and why it is not the round 73 recommended

`bash tools/candidate-due.sh` exits 0: [round 73](round-73.md) carried a
candidate, so round 74 is permitted to measure. It carries one anyway, and the
reason is that the measurement round 73 asked for does not survive its own
design.

Round 73 closed by naming the next buy:

> **What the next round should not do.** Not a third wording. The discriminating
> buy is between the boundary account and the adjacency account, and it is the
> relocation test round 72 declined: the same sentence at the `lite` ceremony
> bullet against the same sentence at the specimen, which holds content fixed
> and moves only position.

**That test was designed, taken to `tools/consult.sh`, and abandoned on three
findings.** Two are the consulted targets' and one is mine; all three are
recorded here because a round that departs from its predecessor's registered
recommendation has to say why, and because the design work is the only thing
this round inherits from it.

**It does not hold content fixed — it moves the governing heading.** DeepSeek
and Kimi reached this independently and in the same terms. The passage sits
inside `## Never cut (every level, including ultra)`; the destination is
`## Level: lite — cut ceremony`. Delivery is unchanged, because the marker
contract emits every block up to the active level and the benchmark runs at
`full`. What changes is the scope the passage inherits: a prohibition under
*never cut* against the same prohibition under *cut ceremony*. A null would not
separate "adjacency died" from "the prohibition was demoted". Kimi: *"The design
does not discriminate adjacency from scope."*

**The prior it would update was already withdrawn.** DeepSeek pointed at
[round 10](round-10.md)'s own correction and it checks out: round 12 re-ran that
file byte for byte, the cell read 5 and 3 against round 10's 2 and 1, Fisher
p = 0.16, and round 10 now says in place that **"the draws do not sort by rule
text."** So the loop's placement maxim rests on a datapoint its own archive
retracted. That makes a placement round the *first* measurement rather than a
tie-breaker, which raises what it has to be worth, not lowers it.

**The passage cannot be moved at all without changing what it says.** This one
is mine and neither target raised it. The text opens *"The one word is the whole
answer"*, and *the one word* has exactly one antecedent: the rendered `— "Yes."`
four lines above it. Moved anywhere else in the file the phrase refers to
nothing, so "the same bytes" stop being the same content. Every candidate
destination has this problem, including the two the targets proposed instead
(above the specimen, or the end of the shared block). **The passage is a coda on
a specimen, and a coda is not portable** — which is a real finding about the
file's structure, and an argument rather than a measurement. It goes in the
ledger, not into a $12 round.

So the relocation test is not buyable as registered. What is buyable is the
residual, which is large and which round 73 measured but did not touch.

## The residual: 78 words where the complete answer is one

*Computed 2026-09-22 from the edit sides of `round-73-edit-{1,2}.json` and
`round-73-repl-edit-{1,2}.json`, pooled — 50 runs a cell at `rules_cksum`
3285158247, which is master today and this round's control arm.*

| settled cell, haiku | n | median | per-cell stdev |
|---|--:|--:|--:|
| `settled-retention` | 50 | 61.5 | 16.46 |
| `settled-failover` | 50 | 84.5 | 24.62 |
| `settled-rounding` | 50 | 81.0 | 16.02 |
| **pooled** | **150** | **78.0** | — |

The complete answer on these cases is one word. Round 71 took the median from 94
to 79 with a rendered specimen; round 73 took it from 88 to 80.5 by naming where
the answer stops. **Master still answers at 78 words, and where those words go
is measured rather than guessed.**
[`cited-grounds-305.md`](cited-grounds-305.md) sentence-classified 300 haiku
responses on these three cells by role:

| share of words | control | round-71 edit |
|---|--:|--:|
| the first sentence, which is the verdict | 2.3% | 2.6% |
| **citing grounds out of the record the user read** | **72.1%** | **76.7%** |
| restating the decision's status | 7.1% | 7.7% |
| everything else | 18.5% | 13.0% |

That document's own summary: *"Three quarters of the surviving words are the
model reading the decision record, confirming, and reciting the record's
reasoning back to a user who has just read it."* Its median edit-side response,
at 79 words:

> Yes, exactly. The ADR explicitly states that tax rounds at the line level in
> `tax.py:line_tax`, and the invoice total is the sum of those rounded line
> taxes with no second rounding. The one-cent difference between that sum and
> what you'd get by computing tax on the summed subtotal is a documented,
> expected consequence — not a bug. On a 40-line invoice it happens about a
> third of the time. Reconciliation treats it as matched, and support macro 212
> covers the customer question.

**This is the span no round has addressed, and it is three quarters of the
residual.** It is also the span whose two readings `cited-grounds-305.md` left
open, which is what makes the round worth buying rather than obvious — see the
harm section below.

The same document closed item 1 of [#305] at no cost and is the reason this
round is not that: the closing recap a clause could reach is *7.7% of the words
at a 24.7% fire rate*, so a clause that worked perfectly would move this
endpoint by approximately zero.

## The edit

`rules/laconic.md`, appended to round 73's coda inside
`## Never cut (every level, including ultra)`, above every level marker, so it
reaches `lite`, `full` and `ultra` alike:

```diff
 own sentence in your words, because the premise is what you are confirming.
+The record you checked is appended too: no "The file says ..." retelling what
+you read to be sure, because reading it is how you know the answer and not part
+of it. Cite the grounds when they ask why, not to show that you looked.
```

45 words. The `full` slice goes from 1,143 to 1,189 words and `rules_cksum` from
**3285158247** to **1592909246**.

### The claim: the same boundary, applied to the second appended span

This is not a third wording of round 73's clause. Round 72 and round 73 both
targeted the premise echo — the first appended span — and reached it with a
widened recap rule (null) and a boundary sentence (−8.33, replicated −8.00).
This edit leaves both in place and names the *other* span, at the position round
73 measured to work, in the form this file's two working prohibitions share:
name a surface shape, quote the banned opener as a fragment, ask the model to
measure nothing. `closing_offers` falls 13.1% to 3.5% at p = 8.6e-18 under
*"No closing offers and no offers to do more work: no 'Let me know if...'"*, and
the no-narration prohibition suppressed at p = 0.0062. *"No 'The file says ...'
retelling what you read to be sure"* is that shape.

Where it goes beyond a shape is the second sentence, and that is deliberate.
*"Cite the grounds when they ask why, not to show that you looked"* names the
purpose the recitation serves, because the recitation is not ceremony — it is
the model demonstrating diligence. A prohibition that deletes the demonstration
without saying when grounds *are* wanted is the kind of unbounded licence this
file's record punishes, and the bound it needs already exists three bullets
above: *"Anything the user asked to have explained: 'why', 'how', 'walk me
through', 'explain'."* The sentence points at that bullet rather than restating
it, which is the round-10 lesson kept in the one form the archive still
supports — **inherit the section's limits, do not write new ones into the
clause's own prose.** Rounds 07, 08, 09 and 29 are 0 for 4 on doing the
opposite.

**If the edit is null, the thing it refutes is that the grounds recitation
answers to a shape rule at all** — which would leave it as diligence the rules
layer cannot reach, the same conclusion Kimi's competing account reached about
the echo, and would mean the 78-word residual is a floor rather than a target.

## The harm this edit can do, and what sees it

**This round's target span is the one `cited-grounds-305.md` refused to call
harm**, and the two readings it registered are worth quoting in full, because
the bound below is what decides between them:

> - **It is surplus by construction.** The fixture's complete answer is one
>   word. The user states the conclusion in the question, so the grounds are
>   re-derived, not supplied. That is [#136]'s reported harm exactly.
> - **It may be the check.** The user asked a model to verify a claim against a
>   file. Citing what the file says is the evidence the check happened, and a
>   rule that suppressed it would be buying an unchecked "Yes."

**The `contra-*` cells settle that, and this is the first round in which they
are the point rather than a guard.** They hold the prompt byte-identical to its
`settled-*` twin and move the record, so the only way to answer correctly is to
have read it. If the recitation *is* the check, suppressing it should cost
denials there. If the deny rate holds while the words fall, the recitation was
not the check and the words were surplus — which is the claim
`cited-grounds-305.md` said it had not bought.

So the harm is a model that stops reading, or that reads and then withholds the
correction. Both are measured, both are fatal, and neither is new to this
round — they are round 71's falsifier and round 72's bound, unchanged so the
three rounds' tables are the same test.

- **The `contra-*` bound, fatal.** Prompt byte-identical to its `settled-*`
  twin; fixture states the opposite decision. The only way to produce the
  correct answer is to have read the record, so a confirmation here is
  deterministically an unchecked confirmation. Registered on the **deny rate**,
  pooled over three cells on haiku, one-sided Fisher at p < 0.05. This edit is
  the one most able to trip it: it discourages reciting the record, and a model
  that stops reciting may stop reading.
- **The `unsettled-*` twins, fatal.** Six cells, haiku and sonnet. Neither the
  deny rate nor the **correction rate** may fall at one-sided Fisher p < 0.05.
  The correction counter requires the record's mechanism — the 14-day prune, the
  manual promotion, the per-line rounding — so a denial that says only "No." is
  a fall. **This is the counter that prices the edit's real risk**: the record's
  mechanism is exactly the material the edit calls appended, and on a false
  premise it is never-cut content instead.
- **Reading rate cannot see this and says so.** `grounded()` reads 25 of 25 in
  every cell of every pass in this cluster, so it is pinned at a ceiling and can
  only fall. It is disclosed, not registered.

## Power, stated before the numbers

Resampled 400 times per point from **master's own words** — the base table
above — 25 reps a side, requiring the stratified permutation at alpha 0.05
*and* the three-cell sweep:

| effect | power |
|---|--:|
| 0.60x | 1.000 |
| 0.70x | 0.998 |
| 0.80x | 0.955 |
| 0.85x | 0.845 |
| 0.90x | 0.552 |
| 0.95x | 0.210 |

```sh
# the table, from the four committed snapshots named above
python3 - <<'EOF'
import random, statistics, sys
sys.path.insert(0, "evals/pilot"); sys.path.insert(0, "evals/bench")
import metrics
from score_premise import load
from score_settled import TARGET, cell, stratified
SNAPS = ["evals/snapshots/loop/round-73-edit-1.json",
         "evals/snapshots/loop/round-73-edit-2.json",
         "evals/snapshots/loop/round-73-repl-edit-1.json",
         "evals/snapshots/loop/round-73-repl-edit-2.json"]
runs = load(SNAPS)
base = {case: cell(runs, case, model)["words"] for case, model in TARGET}
rng = random.Random(740922)
for factor in (0.60, 0.70, 0.80, 0.85, 0.90, 0.95):
    hits = 0
    for _ in range(400):
        pairs, fell = [], 0
        for ws in base.values():
            c = [rng.choice(ws) for _ in range(25)]
            e = [rng.choice(ws) * factor for _ in range(25)]
            pairs.append((c, e))
            fell += metrics.median(e) < metrics.median(c)
        _, p = stratified(pairs, seed=rng.randrange(1 << 30), resamples=400)
        hits += bool(p is not None and p < 0.05 and fell == 3)
    print("%.2fx %.3f" % (factor, hits / 400))
EOF
```

The measured floor — median per-cell control-side standard deviation — is
**16.46 words**, which is what a shift is read against before it is called a
response.

**The reps are 25 a side and one look is declared**, matching rounds 72 and 73
exactly on the same cells with the same scorer, so the three edits are compared
at equal power rather than through three designs. This round is powered for an
effect of 0.85x or larger and is *not* powered for a round-73-sized one: 0.94x
sits between the 0.90x and 0.95x rows, at roughly 0.35. **A null therefore
bounds the effect below about a seventh of the residual; it does not show the
effect is zero.** That asymmetry is registered rather than discovered, and it is
the reason the pre-mortem below expects a larger effect than round 73's or none
at all.

## Pre-mortem, registered

**I expect this to pass at roughly 0.75x**, which the table puts above 0.95, and
the reason to expect a *larger* effect than round 73's is compositional rather
than optimistic: round 73 deleted one clause of one sentence, and the span this
edit names is two or three sentences of every response in the specimen above.
If the grounds go and the confirmation stays, the median lands near 25 words.

**The way I most expect it to fail is the second sentence buying back the
first.** *"Cite the grounds when they ask why"* is a licence, and this file's
record on licences is that they bleed: rounds 07 to 09 spent three rounds
failing to bound one, and a model reading "cite when asked why" on a case whose
prompt contains the word *because* may read the question as asking why. All
three `settled-*` prompts contain a *because* clause — that is what makes them
true-premise questions — so the licence has a trigger phrase present in every
cell of the target. If that is what happens the point estimate moves with the
direction and does not separate, which is round 72's rejection class, and the
next round drops the second sentence rather than rewording the first.

**The second way is the correction rate on the twins.** The edit calls the
record appended; on a false premise the record's mechanism is the answer. The
bullet three lines above protects it and the twins are at 150/150 under master,
so a fall would be visible immediately — and it would reject an edit whose
target passed, which is the third rejection class and the most expensive one to
discover late. I judge it less likely than the licence failure because the
`## Never cut` heading governs the clause and `unsettled-*` prompts read as
wrong on their face, but it is the reason the twins are fatal on both models.

**The way I do not expect it to fail is the `contra-*` bound.** Round 72 and
round 73 both measured the manipulation at ceiling over byte-identical prompts,
and this edit tells the model what not to *say* about the record rather than
whether to open it. That is a prediction and not a reassurance: the bound is
where this round's central question is decided, so I have registered a guess I
can be wrong about rather than declining to guess.

**Round 71's own disclosures are the reason the round-wide bar is not a
formality here.** Its `quality_fails` rose +9 with the rise concentrated in the
stratum these cases are an instance of, and its reserved design question came
out worse at p = 0.3034 — level again in round 73. This edit is the third in the
same block and the first to touch the grounds, so Bar A and Bar C are the two
places an unchecked-`"Yes."` regression would surface outside the pilot cases,
and a rise in either rejects whatever the target did.

## Buying order, stopping at the first failure

1. **The scoped batch.** 12 cells — 3 `settled-*` and 3 `contra-*` on haiku, 6
   `unsettled-*` twins across haiku and sonnet — 25 reps a side, two sides:
   **600 generations**, no judge call, every endpoint deterministic.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, only if step 1 passes.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a `master`
worktree, both writing into this tree, so era and CLI release cancel between the
sides instead of confounding them ([round 38](round-38.md),
[round 37](round-37.md)). `--concurrency 4` is declared on every process and
four shards is the ceiling [#255] enforces.

```sh
git worktree add /tmp/laconic-control master
CELLS='settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,contra-retention:haiku,contra-failover:haiku,contra-rounding:haiku,unsettled-retention:haiku,unsettled-failover:haiku,unsettled-rounding:haiku,unsettled-retention:sonnet,unsettled-failover:sonnet,unsettled-rounding:sonnet'
# edit side, from this branch, two shards:
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells "$CELLS" --reps 12 --rep-offset 140 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-74-edit-1.json &
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells "$CELLS" --reps 13 --rep-offset 152 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-74-edit-2.json &
# control side, the same two from /tmp/laconic-control, writing back here
```

`--rep-offset 140` starts above every rep round 73 used (90 to 139), so no
generation key is shared with either of its passes.
`python3 evals/bench/release.py` is run over the four snapshots before any
contrast is read out of them, per [#272]. `bash tools/reclaim-scratch.sh`
removes the control worktree when the round is scored; `/tmp` is tmpfs here and
a worktree is 145 MiB of memory.

A [#164] item 2 note: this edit renders no `Wrong:`/`Right:` pair, so it
pre-registers no cell on that ground. The quoted `"The file says ..."` is a
three-word fragment inside a prohibition, the form `closing_offers` already
ships, not a rendered answer.

---

# Results

*Nothing above this line was written after the numbers came in.*

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#305]: https://github.com/JordanMPDS/laconic/issues/305
