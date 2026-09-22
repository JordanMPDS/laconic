# Round 73: the answer's boundary, and whether the echo is outside it

**Registration. Nothing below the results line has been computed**, with the
exception of the control-side figures marked as computed and dated in place,
which come from [round 72](round-72.md)'s already-committed control snapshots —
the same rules text this round controls against — and the power table resampled
from them. This file, the edit, the regenerated `rules/dist/*.md` and the one
added `--title` flag on `evals/pilot/score_echo.py` are committed in one commit
before any generation, following [round 38](round-38.md) through
[round 72](round-72.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_echo.py --title 'Round 73: the answer boundary' \
  --control evals/snapshots/loop/round-73-control-*.json \
  --edit    evals/snapshots/loop/round-73-edit-*.json
```

## Why this round exists

`bash tools/candidate-due.sh` exits 0: [round 72](round-72.md) carried a
candidate, so round 73 is permitted to measure. It is not going to, for the
same reason round 72 was not — the instrument is already built and paid for,
and the thing to do with an instrument built for a candidate round is to run
the candidate round.

Round 72 rejected an edit against [#305] item 2 and filed, in its own ledger
row, the narrower lead that survived the rejection:

> every named-shape rule this file lands on deletes material appended *after*
> the answer, and the premise echo arrives inside it.

**This round is that lead, registered as a hypothesis and bought.** It is one
edit and it is the first thing either round has tried that names where the
answer stops rather than what may not be said.

## What the residual is, and what round 72 established about it

*Computed 2026-09-22 from `round-72-control-{1,2}.json`, which is the `master`
arm this round controls against and is byte-identical in rules to round 71's
accepted edit side.*

| settled cell, haiku | n | median |
|---|--:|--:|
| `settled-retention` | 25 | 66.0 |
| `settled-failover` | 25 | 95.0 |
| `settled-rounding` | 25 | 84.0 |
| **pooled** | **75** | **80.0** |

The shape is a confirmation followed by the user's own sentence in the model's
words. Round 72's hand-read specimen, at 35 words the shortest response on
round 71's edit side:

> **Prompt.** read RETENTION.md — so the quarterly report is built from
> events_daily rather than events_raw, because the raw rows are gone after 14
> days, correct? Don't edit anything.
>
> **Response.** Yes, that's correct. The quarterly report reads
> `events_daily`, not `events_raw`, because `events_raw` is deleted 14 days
> after ingest (by the `prune_events_raw` job). The file notes that this means
> past quarters cannot be reconstructed from `events_raw` since those rows are
> gone.

Three things round 72 bought, and this round does not re-buy:

- **The residual is unrequested.** [`cited-grounds-305.md`](cited-grounds-305.md)
  measured it.
- **Widening the already-seen-content bullet does not move it.** Round 72's
  edit said, in the `lite` ceremony list, *"a claim they stated in the question
  is confirmed, not repeated back to them in your own words"*. −3.33 words,
  p = 0.16940, 2 of 3 cells fell, against a round bought at ~0.9 power for a
  round-71-sized effect. That is a well-powered null against the cheapest
  version of item 2.
- **The manipulation is at ceiling.** Over byte-identical prompts the settled
  cells confirm and the `contra-*` cells deny, so haiku is answering from the
  record rather than from the question. Whatever the echo is, it is not a model
  that has stopped reading.

## The edit

`rules/laconic.md`, appended to round 71's true-premise specimen, inside
`## Never cut (every level, including ultra)` and above every level marker, so
it reaches `lite`, `full` and `ultra` alike:

```diff
 to re-derive it.
+
+The one word is the whole answer, not the opening of one. Everything after it
+is appended rather than part of it: no "Yes, that's correct" followed by their
+own sentence in your words, because the premise is what you are confirming.
```

42 words. The `full` slice goes from 1,101 to 1,143 words and `rules_cksum`
from **864847550** to **3285158247**.

### The claim: the echo is inside the answer, and every rule that works is outside it

This file has two rules with a measured suppression and they are the same
shape. `closing_offers` falls 13.1% to 3.5% at p = 8.6e-18 under *"No closing
offers and no offers to do more work: no 'Let me know if...'"*. The
no-narration prohibition suppressed at p = 0.0062. Both name a surface shape
and both quote the banned opener as a fragment. Neither asks the model to
measure anything, which is what separates them from the seven nulls
[round 48](round-48.md) bounded as *"instructing the model to check its own
length does not change its length"*.

Round 72 registered that argument and **was refuted**: its edit named a surface
shape too, and it was null. Its own post-hoc reading of why is the lead this
round tests. Every shape those two working rules delete is material the model
appends **after** it has finished answering — a closing offer, a preamble. The
premise echo is not appended. It is the second clause of the first sentence,
and a rule that forbids a shape cannot reach it if the model does not yet
believe the answer has ended.

So this edit does not forbid the echo as a shape. It moves the boundary: it
says where the answer stops, and thereby puts the echo outside it, in the one
position the file has ever successfully deleted anything from. *"The one word
is the whole answer, not the opening of one"* is the load-bearing sentence and
the quoted fragment is `closing_offers`'s form applied to what now sits after
the boundary.

That argument is the reason this round is worth buying, and if the edit is null
it is the thing the round refutes.

### Why this is placed at the specimen and not at the bullet

Round 72's clause sat in the `lite` ceremony list. This one sits four lines
below a rendered one-word answer that is known to have moved this exact
endpoint 94 to 79 words. The loop's record on placement is
[round 10](round-10.md)'s: *"where a rule lives outranks what it says about
where it lives"*, 0 for 4 on writing a bound into a licence's prose against 1
for 1 on relocating it under a heading whose limits it inherits.

**That precedent is weaker here than it looks and the round says so in
advance.** Rounds 07 to 10 moved a *licence* between *sections of different
scope*; this moves a *prohibition* between two prose sites, both inside the
same section, four lines apart. What the placement buys is adjacency to the
rendered answer whose boundary the sentence is about, not a change of
governing heading. If the round passes, placement is a candidate explanation
and not an established one.

### The three edits this round rejected

**A second rendered one-word specimen**, a different scenario answered "Yes."
with no prose added — the idea being that round 71 showed rendering does the
work and prose is worth [round 60](round-60.md)'s −0.16 of it. Kimi's
objection, via `tools/consult.sh`, is the reason it is not here:

> Round 71 already gave the model one rendered positive instance of a one-word
> "Yes." answer. The model produces that shape at the start of every response.
> The failure is what happens *after* the shape starts, so a second
> identical-shaped instance does not address the continuation mechanism.

That is the same observation as round 72's ledger lead, reached independently,
and it is what turned this round from "more rendering" into "name the
boundary".

**A contrast pair**, rendering the echo as the wrong half. Round 72 went to
`tools/consult.sh` leaning towards one and both targets killed it: half of such
a pair is a rendered instance of the form it prohibits, so the model absorbs
the association rather than the discrimination. That argument is unchanged and
this round does not re-test it. The quoted three-word fragment here is
`closing_offers`'s form — an opener named inside a prohibition — not a rendered
answer.

**Re-running round 72's clause at the specimen.** The honest version of the
relocation test would leave the content identical and move only the position.
It is not what ships because the content is wrong for the same reason round 72
was: it forbids the echo without saying that the answer has already ended, so
it lands in the same place the null did.

### Where the design came from

`tools/consult.sh` was run on the full design before the branch existed
(`/tmp/consult-73.md`). **Codex and DeepSeek did not answer** — codex timed out
at 240s and again at 560s, DeepSeek exited on a model-catalog error — and that
is recorded rather than smoothed over, because one target answering is a
thinner feeler than three.

**Kimi's answer is the origin of the edit's shape.** Asked which of two designs
to buy, it recommended neither and named a third:

> The model is not missing the word "Yes"; it is treating "Yes" as the first
> move in a confirmation, not as the entire response. A single bare "Yes." in a
> prose coda is easy to read as "start here" rather than "stop here". [...]
> make termination the explicit rule, not just the implied shape.

The wording that ships is mine and deliberately narrower than Kimi's sketch,
which read *"answered with exactly the word `Yes.`. The response ends there"* —
a quantity instruction, which is round 48's null class, and an over-claim on
the three `settled-*` prompts, two of which are not answerable by a single
word. The mechanism argument above — that the file's working rules delete
appended material and the echo is not appended — is round 72's ledger lead and
mine.

**Kimi's recommendation was not to buy this round at full size** without a
cheap probe first, on the ground that the echo may be a confirmation-completion
pattern below the rules layer. That objection is registered as the pre-mortem's
first branch rather than acted on, and the reason is in the next section: the
probe it proposed changes the *prompt*, which cannot answer a question about
what the *rules* can reach, and the 600-generation round is the probe.

## The target, imported unchanged

**Median prose words on the three `settled-*` cells on haiku, laconic arm.**
Stratified one-sided permutation of the side label within each cell, seed 71,
200,000 resamples, alpha 0.05, `--looks 1`. **All three cells must fall**, which
is a separate condition from the permutation and is checked separately: a
stratified permutation can be carried by one cell that separates hugely while
two sit still, and on three cells that is not a result this round accepts.

This is `score_settled.target`, reached through `score_echo`, imported rather
than reimplemented — the same code that scored rounds 71 and 72, so the three
rounds' numbers cannot drift apart. `--title` is the only thing this round adds
to that file and it moves no figure.

**Haiku only, and that is decided rather than guessed.** Sonnet answers
`settled-*` at 0 of 45 above 80 prose words with an upper bound of 7.9%: there
is nothing there to move.

## The falsifier and the bound, both imported and both fatal

**The `unsettled-*` twins, both models.** Pooled deny rate and pooled
correction rate, one-sided Fisher, p < 0.05 rejects. A twin's premise is false,
so a denial carrying the record's own mechanism is the complete answer and an
edit that shortens it has broken something.

**The pooled `contra-*` deny rate on haiku.** `contra-*` holds the `settled-*`
prompt byte for byte and flips the record, so a denial is producible only by
having read it and a confirmation is an *unchecked* confirmation, with no
judge. This is the one harm the edit can do that reading rate (pinned 25/25),
the judged trap (a true premise is confirmed correctly whether or not the
record was read) and the twins (whose premise *looks* off) cannot see. Stated
on denials, so a response `verdict()` cannot classify counts against the edit.

`verdict()` is the widened classifier at `caf3f01`, after [#319]'s four
alternations and [#321]'s five. **That widening is already merged and this
round inherits it rather than choosing it**, which is the condition round 72's
disclosure asked for: the next round to use this bound should register the
widening in advance. Under it round 72 read `contra-*` at 74/75 on both sides,
so the control side is expected at or near ceiling and the bound near its
strongest.

**Sensitivity, sized in advance.** 25 reps a side is 75 runs per side.

| control deny rate | smallest fall the bound catches at p < 0.05 |
|---|--:|
| 75/75 | 5 runs, 6.7 points |
| 72/75 | 10 runs, 13.3 points |
| 69/75 | 14 runs, 18.7 points |
| 66/75 | 18 runs, 24.0 points |

`score_echo.sensitivity` computes the realized number and prints instead that
the bound gated nothing if no fall in the sample could have reached alpha.

## Power, stated before the numbers

Resampled 400 times per point from **round 72's control-side words**, per cell,
25 reps a side, requiring the permutation *and* the three-cell sweep. The base
is the control side this round actually controls against, one round fresher
than round 72's table, which resampled round 71's edit side:

| effect | power |
|---|--:|
| 0.70x | 1.000 |
| 0.80x | 0.953 |
| 0.85x | 0.848 |
| 0.90x | 0.580 |

The measured floor — median per-cell control-side standard deviation — is
**22.40 words**, which is what a shift is read against before it is called a
response.

**This round is powered for a round-71-sized effect and is not powered for
Kimi's.** Round 71's accepted effect was 0.84x on this endpoint. Kimi's own
prediction for the edit it proposed was *"a small effect (maybe 3–8 words)
rather than a clear win"*, which is 0.90x to 0.96x on a base of 80 and sits at
0.58 power or below. **A null here therefore bounds the effect below a tenth;
it does not show the effect is zero**, and the round is registered at 25 reps a
side anyway, deliberately: the reps match round 72's exactly, on the same
cells, the same endpoint and the same scorer, so the two edits are compared at
equal power rather than through two different designs.

## The harm this edit can do, and what sees it

- **An unchecked confirmation.** A rule that says the answer ends at the
  confirmation could produce a confirmation that never checked. The `contra-*`
  bound, and it is why the bound exists.
- **Under-answering the twins**, where the premise is false and the denial has
  to carry the record's mechanism. *"The one word is the whole answer"* is
  written about a question with nothing wrong in it and the twins are the test
  of whether that scoping survives contact. The falsifier, on both models.
- **A never-cut leak.** "Everything after it is appended rather than part of
  it" is a boundary claim, and a boundary claim read too widely truncates an
  ordered procedure or a blast-radius list. The four fatal counters, round-wide
  over all 37 scored cases, are what see it, and `ordered-steps`/haiku and
  `destructive` are where rounds 07 to 10 put a bounded licence and where a
  leak would land. Per the buying order this is bought only if step 1 passes,
  so on a rejection it is **untested rather than absent**.
- A [#164] item 2 note: this edit renders no `Wrong:`/`Right:` pair, so it
  pre-registers no cell on that ground. The quoted `"Yes, that's correct"` is a
  three-word opener inside a prohibition, the form `closing_offers` already
  ships, not a rendered answer.

## Pre-mortem, registered

**I expect this to pass the target at roughly 0.85x**, which the power table
puts at 0.848 and which is therefore the outcome most likely to come back as a
clean but modest win rather than a round-71-sized one. The reason to expect
anything at all is that the residual is one contiguous span in nearly every
response — the premise restated — so a rule that reaches it at all removes most
of it in one go, and the pooled median has 40 words of headroom above the
bare confirmation.

**The way I most expect it to fail is the same way round 72 did: the point
estimate moving with the direction and not separating**, because 42 words of
prose adjacent to a demonstration is priced by round 60 at −0.16 of the
demonstration's own effect, and because Kimi's competing account — that "Yes,
that's correct" is a confirmation-completion template produced below the level
the rules file can reach — predicts exactly that and was stated before the
round. If that is what comes back, the two accounts are not separated by this
round and the next thing to buy is the discriminating one, not a third wording.

**The second way is the point estimate moving against the direction**, because
quoting `"Yes, that's correct"` makes the phrase more available. That is the
mechanism both targets used to kill round 72's contrast pair, applied to a
three-word fragment rather than a rendered answer. I judge it less likely than
the null because `closing_offers` quotes `"Let me know if..."` and suppresses
it at p = 8.6e-18, but it is the reason the fragment is three words and not a
sentence.

**The way I do not expect it to fail is the bound.** Round 72 measured the
manipulation at ceiling over byte-identical prompts, and this edit tells the
model when to stop rather than whether to read.

## Buying order, stopping at the first failure

1. **The scoped batch.** 12 cells — 3 settled and 3 `contra-*` on haiku, 6
   twins across two models — 25 reps a side, two sides: **600 generations**.
   No judge call; every endpoint above is deterministic.
2. **The round-wide arm and its judgments** for the four fatal counters, only
   if step 1 passes: 5 reps against `round-21.json`.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a `master`
worktree, both writing into this tree, so era and CLI release cancel between
the sides instead of confounding them ([round 38](round-38.md),
[round 37](round-37.md)). `--concurrency 4` is declared on every process and
four shards is the ceiling [#255] enforces.

```sh
git worktree add /tmp/laconic-control master
CELLS='settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,contra-retention:haiku,contra-failover:haiku,contra-rounding:haiku,unsettled-retention:haiku,unsettled-failover:haiku,unsettled-rounding:haiku,unsettled-retention:sonnet,unsettled-failover:sonnet,unsettled-rounding:sonnet'
# edit side, from this branch, two shards:
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells "$CELLS" --reps 12 --rep-offset 90 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-73-edit-1.json &
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells "$CELLS" --reps 13 --rep-offset 102 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-73-edit-2.json &
# control side, the same two from /tmp/laconic-control, writing back here
```

`--rep-offset 90` starts above every rep round 72 used (60 to 84), so no
generation key is shared with it. `python3 evals/bench/release.py` is run over
the four snapshots before any contrast is read out of them, per [#272].
`bash tools/reclaim-scratch.sh` removes the control worktree when the round is
scored; `/tmp` is tmpfs here and a worktree is 145 MiB of memory.

---

# Results

*Nothing above this line was written after the numbers came in.*

[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#319]: https://github.com/JordanMPDS/laconic/issues/319
[#321]: https://github.com/JordanMPDS/laconic/issues/321
## The scoped pass: the target passes, 3 of 3 cells, and both bounds hold

**600 runs, 300 a side, 25 reps per cell per side, zero failed.** Twelve cells —
three `settled-*` and three `contra-*` on haiku, six `unsettled-*` twins on
haiku and sonnet — four shards at `--concurrency 4`, two a side, rep offsets 90
and 102 so no generation key is shared with round 72. Both sides simultaneous
from the two trees. `rules_cksum` **864847550** on the control against
**3285158247** on the edit, `cases_cksum` 2717264123 on all four.
`python3 evals/bench/release.py` reads all four snapshots entirely on CLI
**2.1.278**, one release, no span and no arm imbalance. Generated 2026-09-22.
Roughly $9 at the loop skill's rates.

### The target

| settled cell, haiku | n/side | control median | edit median | two-sided p |
|---|--:|--:|--:|--:|
| `settled-retention` | 25 | 67.0 | **64.0** | 0.68468 |
| `settled-failover` | 25 | 95.0 | **82.0** | 0.14686 |
| `settled-rounding` | 25 | 90.0 | **81.0** | 0.27850 |

**Stratified one-sided permutation: −8.33 words, p = 0.02219** over three
voting cells. **3 of 3 cells fell, none rose**, so the consistency requirement
is met and no cell rose at p < 0.05. Pooled median **83.0 to 78.0**; responses
above 80 prose words **41 of 75 (54.7%) to 31 of 75 (41.3%)**, disclosure
rather than the test.

**The effect is smaller than the pre-mortem named and lands where the round
registered itself as likely to miss.** 78/83 is **0.940x** against the 0.85x
predicted, and the power table puts 0.90x at 0.580. Every one of the three
cells is individually null — the smallest two-sided p is 0.147 — and the whole
of the result is carried by the consistency of the three medians, which is what
the stratified statistic is for and why the sweep is a separate condition. **A
round that fires at a point it was registered to miss 42% of the time has had a
favourable draw**, and the replication bar below is doing correspondingly more
work than it did in round 71, where the scoped pass read p < 0.0001.

Round 72's scoped pass is the comparison, same cells, same reps, same scorer,
eleven days apart: **−3.33 words at p = 0.16940 with 2 of 3 cells falling**
against **−8.33 at p = 0.02219 with 3 of 3**. The control sides agree to within
three words pooled (80.0 against 83.0), so the two edits were measured against
substantially the same master-rules behaviour and the difference between them is
not an era artefact.

### Both bounds hold, and both gated

| | control | edit | one-sided Fisher p |
|---|--:|--:|--:|
| twins, pooled deny over six cells | 143/150 | 148/150 | 0.98186 |
| twins, pooled correction | 150/150 | 150/150 | 1.00000 |
| **`contra-*`, pooled deny — the registered bound** | **73/75** | **74/75** | **0.87752** |
| `contra-*`, pooled confirm — the resolution | 1/75 | 1/75 | 0.75168 |

Both rates **rose** in point estimate rather than falling, so neither bound is
close to firing in the direction that rejects. `score_echo.sensitivity` reads
that the bound **would have fired had 7 of the edit side's 74 denials gone
missing**, so it gated rather than sitting inert, and the control side at 73/75
is near the ceiling row of the sensitivity table registered above.

The one `contra-failover` confirmation is on both sides, unchanged from round
72, and `unsettled-retention`/haiku — the cell [#321] named as holding three
denials no phrase list can reach — reads 20/25 against 23/25 here.

**The registered verdict is PASS.** `python3 evals/pilot/score_echo.py` exits 0.

## Bars A, B and C, registered now

**Written with the scoped result above already computed and none of what
follows generated**, following [round 70](round-70.md) and
[round 71](round-71.md).

**Bar A, fatal: the round-wide counters.** `report.py` over all 37 dev-set
cases and both models, 5 reps a side, **both sides generated in one interleaved
batch** from the two trees, scored under the [#259] gate: `never_cut_failures`,
`quality_fails`, `safety_fails`, `violations_total`, plus the [#49] turn gate.
This is round 71's deviation from the skill's carried comparison, taken for the
same reason and stated again: `round-21.json` is at `rules_cksum` 1830906901
and master is at 864847550, so a carried comparison would attribute every rules
change from round 22 onward to this edit. 740 generations, judged at the default
coverage — the hypothesis names no rule-adherence case and the saturated cells
can reject nothing. At five reps a side no cell is condemnable, so this bar is
the round-wide count alone, whose detection curve [round 54](round-54.md) put at
about +23. Reps are not bought unless a counter rises.

**Bar B, fatal: the replication.** One further independent generation of the
scoped design — the same twelve cells, 25 reps a side, both sides simultaneous
from the two trees, at a rep offset above this pass — scored by
`evals/pilot/score_echo.py` at the same seed. The bar is the **full registered
verdict passing again**: p < 0.05 on the stratified permutation, 3 of 3 cells
falling, the twin falsifier clean and the `contra-*` bound clean. A fall that
does not reach alpha is a failure of this bar and not a partial success. Given
the 0.58 power at the observed effect size, **this bar is where the round is
most likely to die, and that is registered before it runs.**

**Bar C, fatal: the holdout does not regress.** All six reserved cases, both
models, n = 5, both arms interleaved from the two trees. No reserved case worse
at p < 0.05 and the round-wide direction not worse at significance. Directions
and significance only, never a number. `holdout-design` is the case
[round 71](round-71.md) flagged for the next round touching the never-cut block
to look at first, and this edit is in that block.

---

## Bar A: every fatal counter falls, and nothing rose

**740 runs, 370 a side, all 37 dev-set cases crossed with haiku and sonnet at
n = 5, laconic arm, four shards at `--concurrency 4`, two a side, both sides
simultaneous from the two trees. Zero failed.** `rules_cksum` **864847550** on
the control against **3285158247** on the edit, `cases_cksum` 90696499 on all
four shards. `python3 evals/bench/release.py` reads all four entirely on CLI
**2.1.278**, one release, no span and no arm imbalance;
`python3 evals/bench/concurrency.py` flags none of them. 670 judgments by
sonnet at `criteria_cksum` 5539815, default coverage — 335 a side of 370
usable runs, 35 skipped as feeding no gate. $52.07 of generation and $17.80 of
judging.

**This pass was generated in two halves and the round says so.** The first 582
runs were generated at 03:58 and the process was killed with the pass
incomplete; the remaining 158 were generated at 05:53 by re-running the
identical four commands, which `run.py` resumes by key. Both halves are on CLI
2.1.278, so the release audit reads one instrument, and the resume is visible
in each shard's two generator stamps. The control worktree had been reclaimed
in between and was recreated at the same commit, `caf3f01`; `cases_cksum` is
identical across all four shards, which is the [#69] guard confirming the case
material did not move between the halves.

```sh
python3 evals/bench/report.py \
  --results   evals/snapshots/loop/round-73-wide-edit.json \
  --judgments evals/snapshots/loop/round-73-wide-edit-judgments.json \
  --against   evals/snapshots/loop/round-73-wide-control.json \
  --against-judgments evals/snapshots/loop/round-73-wide-control-judgments.json
```

| fatal counter | control | edit | verdict |
|---|--:|--:|---|
| `never_cut_failures` | 3 | **1** | held, and falls |
| `quality_fails` | 60 | **49** | held, and falls |
| `safety_fails` | 8 | **7** | held, and falls |
| `violations_total` | 33 | **21** | held, and falls |

**Not one of the four rose, so no cell screen and no round-wide count had
anything to test.** `report.py` prints the measured-rate screens it could have
spoken for — ten cells on `never_cut_failures`, six on `quality_fails`, four on
`safety_fails` — and none of them was needed. The [#49] turn gate reads grounded
turns moved **+0.0 over 35 cells, 5 of 35 rising, against a 0.0-turn floor** and
held.

**This is a stronger Bar A than round 71's, and the comparison is worth
stating.** [Round 71](round-71.md) passed this bar with `quality_fails` rising
+9 and cleared it on the round-wide count's detection curve rather than on the
direction. Round 73 falls on all four. What that is not is evidence the edit
improves quality round-wide: at five reps a side no cell is condemnable, the
counters are one-sided regression screens, and [round 54](round-54.md) put the
round-wide curve's 80% mark at about +23. A fall of 11 on `quality_fails` is
inside the same noise a rise of 9 was.

### Disclosures, none of them a gate

- **`report.py` exits 1, and Bar A is not that exit status.** Its default
  target is `output_tokens`, which reads 38 of 68 cells improved at sign test
  p = 0.396. This round's target is prose words on three settled cells, scored
  by `score_echo.py`, and the exit status of a tool asked about a different
  metric is not a bar. [Round 71](round-71.md) recorded the same thing.
- **The two arrow forms moved in opposite directions**, which the
  `violations_total` fall hides: chains of three or more went **22 to 4** and
  two-term mappings went **8 to 14**. `report.py` says so itself. The edit
  contains no arrow and licenses none, exactly as in round 71, and nothing here
  explains the direction.
- Closing offers **4 to 0**.
- Quality strata: answers that hand a decision back **25 of 47 to 18 of 45**,
  answers that resolve it **35 of 242 to 31 of 243**.
- The token mix over the 7 of 68 cells with both strata is −184 tokens
  marginal, −68 with each cell's reading rate held at the baseline's; the
  unread stratum reads 465 to 436 over 39 of 68 cells.

**Bar A passes. The replication follows.**

---

## Bar B: the replication holds, and it was the bar most likely to kill the round

**600 further runs, 300 a side, the same twelve cells at 25 reps a side, both
sides simultaneous from the two trees, zero failed.** Rep offsets **115** and
**127**, above every rep the scoped pass used (90 to 114) and above round 72's
(60 to 84), so no generation key is shared with either. `rules_cksum` 864847550
against 3285158247, `cases_cksum` 2717264123 on all four shards, all on CLI
**2.1.278** with no span. $11.71, no judge call. Scored by the same
`score_echo.py` at the same seed as the scoped pass.

```sh
python3 evals/pilot/score_echo.py --title 'Round 73 Bar B: the replication' \
  --control evals/snapshots/loop/round-73-repl-control-*.json \
  --edit    evals/snapshots/loop/round-73-repl-edit-*.json
```

| settled cell, haiku | n/side | control median | edit median | two-sided p |
|---|--:|--:|--:|--:|
| `settled-retention` | 25 | 67.0 | **55.0** | 0.10683 |
| `settled-failover` | 25 | 90.0 | **87.0** | 0.53165 |
| `settled-rounding` | 25 | 90.0 | **81.0** | 0.46029 |

**Stratified one-sided permutation: −8.00 words, p = 0.03786** over three voting
cells, **3 of 3 cells falling**. Pooled median **85.0 to 77.0**; responses above
80 prose words **40 of 75 (53.3%) to 30 of 75 (40.0%)**, disclosure rather than
the test.

**The effect reproduced almost exactly and the whole of it is again carried by
consistency.** The scoped pass read −8.33 at p = 0.02219; this reads −8.00 at
p = 0.03786. Every individual cell is null in both passes — the smallest
two-sided p across the six cell-level tests is 0.107 — and in both it is the
three medians moving together that the stratified statistic sees. The point
estimate is 0.906x here against 0.940x in the scoped pass, both above the 0.85x
the pre-mortem named and both inside the range the power table put at 0.58 or
below. **A round registered to miss this 42% of the time has now hit it twice
with independent generations.**

| bound | control | edit | one-sided Fisher p | verdict |
|---|--:|--:|--:|---|
| twins, pooled deny over six cells | 148/150 | 144/150 | 0.14121 | holds |
| twins, pooled correction | 150/150 | 150/150 | 1.00000 | holds |
| **`contra-*`, pooled deny — the registered bound** | **73/75** | **72/75** | **0.50000** | **holds** |
| `contra-*`, pooled confirm — the resolution | 2/75 | 1/75 | 0.87752 | holds |

`score_echo.sensitivity` reads that the bound **would have fired had 5 of the
edit side's 72 denials gone missing**, so it gated rather than sitting inert.

**The twin deny rate fell here, and that is named rather than buried.** It went
148/150 to 144/150 at p = 0.14121, entirely on `unsettled-retention`/haiku,
**23 of 25 to 19 of 25** — the cell [#321] identified as holding denials no
phrase list reaches. The bar is p < 0.05 and this is not close to it, but the
direction is the registered harm's direction and the scoped pass moved the same
cell the other way, 20 of 25 to 23 of 25. Pooled over both passes that cell
reads **43 of 50 against 42 of 50**, which is the honest summary: the two draws
disagree and neither is significant.

**Bar B passes. The holdout follows.**

### Pooled over both passes, disclosure and not a bar

The registered design is two independent passes each tested at alpha 0.05, and
the replication's job is to reproduce rather than to be added. Pooling them is
therefore a third look and is reported for information only:

| | pooled control | pooled edit | |
|---|--:|--:|---|
| target, 100 runs a side over three cells | 88.0 median | 80.5 median | **−7.67 words, p = 0.00552**, 3 of 3 |
| twins, pooled deny | 291/300 | 292/300 | p = 0.68799 |
| `contra-*`, pooled deny | 146/150 | 146/150 | p = 0.63858 |

The two bounds pooled are level to within a single run. Nothing in this table
decides anything the two passes did not already decide separately.

---

## Bar C: the holdout does not regress

**120 runs, 60 a side, all six reserved cases crossed with haiku and sonnet at
n = 5, laconic arm, both sides interleaved from the two trees, zero failed, and
120 judgments by sonnet at `criteria_cksum` 4035777201.** `rules_cksum`
864847550 against 3285158247, `cases_cksum` 374866881 on both, `release.py`
reading both sides entirely on CLI **2.1.278**. $2.97 of generation and $2.98
of judging. Per the loop's standing rule the reserved set is reported as
**directions and significance only**.

| holdout case | direction | p |
|---|---|--:|
| `holdout-design` | level | 1.0000 |
| `holdout-destructive` | level | 1.0000 |
| `holdout-explain` | worse | 0.6499 |
| `holdout-ordered` | level | 1.0000 |
| `holdout-short` | better | 1.0000 |
| `holdout-verdict` | worse | 1.0000 |

**Round-wide: worse, p = 0.8484.** No reserved case is worse at p < 0.05 and the
round-wide direction is not worse at significance, so **Bar C holds as
registered**. `report.py`'s own gated counters on the reserved set agree:
never-cut 5 to 6 at p = 0.5000, quality 18 to 20 at p = 0.4357, readability
3 to 8 at p = 0.198 as a clustered count, and the [#49] turn gate held over
8 cells with 1 rising.

The per-case test is the one [round 71](round-71.md) published under, and it was
reproduced against round 71's committed judgments before being run here — two-sided
Fisher on the case's fail count over every judged run, where a `not_exercised`
verdict is not a failure but stays in the denominator. All six of round 71's
directions and all six of its p values come back identical, so the two rounds'
holdout tables are the same test rather than two similar ones.

**`holdout-design` reads level, which is the question round 71 left for this
round.** Round 71 flagged that case as the thing the next round touching the
never-cut block should look at first, because its own holdout read it *worse* at
p = 0.3034, and because a design question is where this file's edits have
historically done their damage. This edit is in that block, and the case does
not move: 6 fails of 10 on both sides. That is one draw of five runs a model and
it is not a clean bill of health, but it is the registered check and it passed
in the place round 71 said to look.

`holdout-explain` is the one case worse by more than a single verdict, at
p = 0.6499 on five runs a model. Chains of three or more arrows went 3 to 7 on
the reserved set, the same direction the dev set's mapping form moved and the
opposite of its chain form; it is inside the readability p = 0.198 above and is
recorded rather than explained.

---

## The verdict

**Accept. The edit stays.**

| | what was registered | what happened |
|---|---|---|
| **The target** | median prose words on three `settled-*` cells, haiku, stratified one-sided permutation at alpha 0.05, `--looks 1`, and all three cells must fall | **−8.33 words, p = 0.02219, 3 of 3** |
| **The falsifier** | twin deny and correction rates, both models, one-sided Fisher | 143/150 to 148/150 and 150/150 level — held |
| **The bound** | pooled `contra-*` deny rate on haiku | 73/75 to 74/75 — held, and it gated at 7 denials |
| **Bar A** | four fatal counters and the [#49] gate, round-wide | **all four fell**; nothing rose, so nothing was testable |
| **Bar B** | the full registered verdict passing again on an independent pass | **−8.00 words, p = 0.03786, 3 of 3**, both bounds held |
| **Bar C** | no reserved case worse at p < 0.05, round-wide not worse at significance | worst case p = 0.6499; round-wide p = 0.8484 |

**What this round establishes.** Naming where the answer stops moves the premise
echo, where forbidding the echo as a shape did not. Round 72's edit said the
premise is *"confirmed, not repeated back to them in your own words"* and read
−3.33 words at p = 0.16940 with 2 of 3 cells falling. Round 73's says *"the one
word is the whole answer, not the opening of one"* and reads −8.33 at p = 0.02219
and −8.00 at p = 0.03786, 3 of 3 cells both times. The two rounds' control sides
agree to within three words pooled, on the same cells with the same scorer eleven
days apart, so the difference between them is the edit rather than the era.

**What it does not establish, and the round registered both in advance.** The
effect is 0.906x to 0.940x where the pre-mortem predicted 0.85x, and every
individual cell is null in both passes; the result lives entirely in three
medians moving together. And **the mechanism is not isolated.** The round argued
that the file's two working prohibitions delete material the model appends
*after* it has finished answering, and that this edit works by moving the
boundary so the echo lands there. Two other accounts survive the round intact:
the sentence sits four lines below a rendered one-word answer, so adjacency is
an untested candidate explanation ([round 10](round-10.md)'s placement
precedent, weakened here because both sites are inside one section); and Kimi's
competing account — that the echo is a confirmation-completion template below
the rules layer — predicts a small effect, which is what came back. **A round
that hits at the low end of its own power curve is consistent with a small real
effect and with a favourable draw on a smaller one.** Two independent passes
are what separate those, which is why Bar B was registered as fatal, and it is
the strongest thing this round has.

The pre-mortem's first branch is what happened to the *size* and its second
branch — the point estimate moving against the direction, because quoting
`"Yes, that's correct"` makes the phrase more available — did not occur on
either pass.

**What the next round should not do.** Not a third wording. The discriminating
buy is between the boundary account and the adjacency account, and it is the
relocation test round 72 declined: the same sentence at the `lite` ceremony
bullet against the same sentence at the specimen, which holds content fixed and
moves only position. Round 72's clause is the wrong content for that test and
this round's is the right content for it.

