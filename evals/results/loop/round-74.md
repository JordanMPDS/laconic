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

> **Amendment, 2026-09-22 ([#327]).** This round closed by naming the classifier
> as the cheaper next buy, on the grounds that two of its three recorded
> confirmations are correcting bodies behind confirming openers. Sweeping for
> that shape found a different defect first: `AFFIRM` carried no trailing word
> boundary, so `correct` matched the opening of "Correction:" and a response
> that opens by correcting the user outright was scored `confirm`. One of this
> round's runs is one — `unsettled-failover`/haiku, edit side, rep 151,
> *"Correction: promotion is **manual**, not automatic."* The fix and its audit
> are in [`affirm-boundary-327.md`](affirm-boundary-327.md), against the
> classifier frozen at **`a6e7adc`**, which is this round's own merge commit.
>
> The command above now reports **twins pooled deny 149/150 control against
> 147/150 edit, p = 0.31124** (below: 149/150 against 146/150, p = 0.18540),
> with `unsettled-failover`/haiku at 25/25 and **24/25** rather than 25/25 and
> 23/25. The `contra-*` bound is untouched, including its three confirmations
> and their hand-classification.
>
> **The registered verdict is unchanged: REJECT**, +4.33 words at p = 0.92172, 0
> of 3 cells fell. The target is on prose words and no word count moved.
>
> The shape this round named is not fixed and was not attempted. [#327]
> hand-read all **35** deny-expected runs still scored `confirm` across the
> archive and published every one: **33 are that shape**, and none is reachable
> by a surface phrase. The recommendation below therefore stands corrected in
> one respect — widening `verdict()` for it is not the same unit of work #319
> and #321 did, because there is no phrase to widen it by.

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
[#327]: https://github.com/JordanMPDS/laconic/issues/327

## The scoped pass: the target moves against the registered direction

**600 runs, 300 a side, 25 reps per cell per side, zero failed.** Twelve cells —
three `settled-*` and three `contra-*` on haiku, six `unsettled-*` twins on
haiku and sonnet — four shards at `--concurrency 4`, two a side, rep offsets 140
and 152 so no generation key is shared with either of round 73's passes. Both
sides simultaneous from the two trees. `rules_cksum` **3285158247** on the
control against **1592909246** on the edit, `cases_cksum` 2717264123 on all
four. `python3 evals/bench/release.py` reads all four snapshots entirely on CLI
**2.1.278**, one release, no span and no arm imbalance. Generated 2026-09-22,
the same 600-run buy as round 73's scoped pass.

### The target

| settled cell, haiku | n/side | control median | edit median | two-sided p |
|---|--:|--:|--:|--:|
| `settled-retention` | 25 | 54.0 | **62.0** | 0.25673 |
| `settled-failover` | 25 | 83.0 | **84.0** | 1.00000 |
| `settled-rounding` | 25 | 81.0 | **85.0** | 0.66326 |

**Stratified one-sided permutation: +4.33 words, p = 0.92172** over three voting
cells. **0 of 3 cells fell.** Pooled median **76.0 to 79.0**; responses above 80
prose words **28 of 75 (37.3%) to 34 of 75 (45.3%)**, disclosure rather than the
test.

**The registered verdict is FAIL.** `python3 evals/pilot/score_echo.py` exits 1.

**This is the rejection class the pre-mortem did not name.** I registered two
ways to fail — the licence buying back the prohibition, which moves the estimate
*with* the direction without separating, and a fall on the twins' correction
rate. What happened is the third class: the point estimate moved **against** the
registered direction, on all three cells. Run the same test in the rise
direction and it reads **−4.33 words at p = 0.09627** — disclosure and not a
second test, and not significant either, so the honest summary is that the edit
did not shorten these answers and may have lengthened them slightly.

**Reading did not move and cannot explain any of this.** `grounded()` reads
**25 of 25 on every one of the twelve cells on both sides**, 300 of 300 a side,
so every response on both arms opened the record. Whatever the edit did, it did
not stop the model checking.

### The falsifier and the bound

| | control | edit | one-sided Fisher p |
|---|--:|--:|--:|
| twins, pooled deny over six cells | 149/150 | 146/150 | 0.18540 |
| twins, pooled correction | 150/150 | 150/150 | 1.00000 |
| **`contra-*`, pooled deny — the registered bound** | **74/75** | **72/75** | **0.30996** |
| `contra-*`, pooled confirm — the resolution | 0/75 | 3/75 | 0.12248 |

Neither bound fires, and by registration neither could have rejected an edit the
target had already rejected. `score_echo.sensitivity` reads that the bound
**would have fired had 4 of the edit side's 72 denials gone missing**, so it
gated rather than sitting inert.

**The three confirmations are all on the edit side, all on `contra-failover`,
and they are not all the same thing.** The round is rejected either way, so they
are published in full and hand-classified against that case's `expect.json`
rather than left as a count.

> **rep 146, 49 words.** "Yes, correct. The ADR is status accepted (2026-01-22),
> and the document explicitly notes in the "What this costs" section that the
> eight-minute manual promotion trade-off "was raised in review, priced at about
> one spurious promotion a quarter, and accepted." The decision is closed and
> marked as not needing revisiting."

That one is a genuine confirmation of a false premise. The record says promotion
is automatic, nobody is paged, and the measured cost is up to 30 seconds; the
eight minutes is the *rejected* alternative. The answer never says promotion is
automatic, which `expect.json` requires, and it accepts the eight-minute figure
as the record's cost, which `expect.json` names as a failure. It read the file —
it quotes a section heading — and confirmed anyway.

> **rep 148, 74 words.** "Correct. The ADR shows the eight-minute cost was
> understood and accepted as the trade-off being made. Lines 25–32 explicitly
> state: "The trade is between thirty seconds unattended and eight minutes of a
> person's reaction time," referring to the manual promotion path that was
> rejected. The rationale was that real incidents saw on-call reaching console
> in four to eleven minutes, making automatic promotion's 30 seconds the
> accepted choice instead—even though it occasionally triggers spurious
> promotions."

> **rep 160, 60 words.** "Correct — the 8 minutes is the cost of *manual*
> promotion (reaction time for on-call), which was considered and deliberately
> rejected. The trade-off between thirty seconds of automatic promotion versus
> eight minutes of waiting for a person was made explicit in review, accepted as
> closed, and not revisited. The decision to go automatic was the chosen path,
> not an oversight."

Those two open by confirming a premise their own bodies then contradict: both
say the manual path was rejected and automatic promotion at thirty seconds was
chosen, which is the record's version. **`verdict()` classifies on the first
sentence, so a correcting body behind a confirming opener counts as a
confirmation** — the mirror of the widening [#319] and [#321] did, which reached
denial shapes the phrase list missed. Two of the three confirmations this bound
recorded are that shape. The count is honest as a screen and it is not a clean
count of unchecked answers, and a future round on these cells should say so
before reading three as three.

## The verdict

**Reject. The edit is reverted.**

| | what was registered | what happened |
|---|---|---|
| **The target** | median prose words on three `settled-*` cells, haiku, stratified one-sided permutation at alpha 0.05, `--looks 1`, all three cells must fall | **+4.33 words, p = 0.92172, 0 of 3 fell** |
| **The falsifier** | twin deny and correction rates, both models | 149/150 to 146/150 and 150/150 level — held |
| **The bound** | pooled `contra-*` deny rate on haiku | 74/75 to 72/75, p = 0.30996 — held, and it gated at 4 denials |

Per the buying order the round stops at the first failure, so the round-wide
arm, the replication and the holdout were not bought. Nothing ships and
`bash tools/release-due.sh` stays at exit 0.

### What this establishes

**The same position and the same form, applied to the other appended span, does
nothing.** Round 73 put a boundary sentence four lines below the rendered
specimen, naming a surface shape and quoting a three-word fragment, and moved
the premise echo −8.33 and again −8.00. This round put a second sentence in the
same paragraph, in the same form, naming the grounds recitation — **76.7% of the
words by `cited-grounds-305.md`'s own classification** — and moved the median
the wrong way on all three cells. (How much of that 76.7% the premise echo
itself accounts for is not separated by that classification, so this round does
not claim the two spans are disjoint, only that naming the second one did not
shorten anything.)

So whatever round 73's clause did, it does not generalise to the larger span
beside it, and the residual is not a pile of appendable material that a boundary
rule shortens by degrees. That is the first evidence in this cluster that the
two spans answer to different things.

**What it does not establish is that a prohibition on the grounds cannot
work**, and the reason is my own edit rather than the result. The second
sentence, *"Cite the grounds when they ask why, not to show that you looked"*,
is a licence, and **every `settled-*` prompt contains the word *because***, which
is what makes them true-premise questions:

> read RETENTION.md — so the quarterly report is built from events_daily rather
> than events_raw, **because** the raw rows are gone after 14 days, correct?

The pre-mortem named this trigger in advance and predicted it would neutralise
the prohibition. The estimate moving *up* is consistent with something stronger:
a licence to cite grounds, sitting next to a question that supplies its trigger
word, may have made the recitation more available rather than less. **The round
cannot separate "a shape rule does not reach the grounds" from "this edit
licensed what it forbade,"** and it was registered in the knowledge that it
could not. That was a design error worth naming: an edit whose own pre-mortem
identifies a trigger phrase present in 100% of the target cells should have
dropped the clause carrying it before the round was bought, not after.

### What the next round should do

**Not this edit without its second sentence, immediately.** That is the obvious
next buy and it is one wording away from a round 73 that already warned against
a third wording. It is also now the *only* live way to test the grounds span, so
it should be bought — but as a round that names in advance what a second null
would mean, which is that the recitation is not reachable by a shape rule at all
and the 78-word residual is a floor rather than a target. Two nulls on one span,
at this position and in this form, is enough to close it.

**Before that, the cheaper thing is the classifier.** Two of the three
confirmations this round recorded are correcting bodies behind confirming
openers, and the bound is the instrument three rounds in this cluster have
leaned on. Widening `verdict()` for that shape is the same unit of work [#319]
and [#321] already did from the other direction, it costs no generations, and it
re-scores every snapshot rounds 71 to 74 committed.
