# Round 71: the file has never rendered a one-word answer

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are the reason this round takes the
shape it does. This file, the edit, the regenerated `rules/dist/*.md` and
`evals/pilot/score_settled.py` are committed before any generation, following
[round 38](round-38.md) through [round 70](round-70.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_settled.py \
  --control evals/snapshots/loop/round-71-control-*.json \
  --edit    evals/snapshots/loop/round-71-edit-*.json
```

## Why this round exists

`bash tools/candidate-due.sh` exits 0: [round 70](round-70.md) carried a
candidate, so round 71 is permitted to measure. It is not going to. The
instrument [#136] and [#305] both asked for was built yesterday
([`true-premise-136.md`](true-premise-136.md)), it has a measured fire rate on
the cells where the harm is, and the thing to do with an instrument built for a
candidate round is to run the candidate round.

## The instrument, and what it measured

Three `settled-*` cases under `evals/pilot/`: a decision record, a closed
`correct?` question whose stated premise is **true**, so a bare confirmation is
the complete answer and every word after it is surplus **by construction**
rather than by judgement. Each has an `unsettled-*` twin sharing its fixture by
symlink with the premise made false, where a denial plus the record's version
is the complete answer and the words are required.

360 generations on 2026-09-20, one CLI release, no unread fixture, no mutation.
180 of 180 settled responses confirmed the premise and 0 of 180 carried a
correction marker, so the fixture is not being argued with. The laconic arm,
settled cells:

| | above 40 words | above 80 words | median |
|---|--:|--:|--:|
| haiku | 45/45 = 100.0% | **34/45 = 75.6%** [61.3, 85.8] | 98.0 |
| sonnet | 14/45 = 31.1% | **0/45 = 0.0%** [0.0, 7.9] | 32.0 |

Per settled cell on haiku: retention 10/15, failover 12/15, rounding 12/15
above 80 words. The surplus is one shape in every hand-read response — a
confirmation followed by the record's own rationale quoted back to a user who
has just said they read it.

**This round is haiku-only on the target, and that is decided rather than
guessed.** Sonnet reads 0 of 45 above 80 words with an upper bound of 7.9%:
there is nothing there for an edit to move, and a round scoped to both models
would spend half its generations on a cell at the floor. That inverts the
loop's usual sonnet-first habit and the reason is specific to this endpoint.

## The edit

`rules/laconic.md`, immediately after the demonstration block's coda — the
same position [round 64](round-64.md) used, which is inside the
`## Never cut (every level, including ultra)` section and above every level
marker, so the specimen reaches `lite`, `full` and `ultra` alike and a reader
passes the whole never-cut list before reaching it:

```diff
 Ultra kept the conditional because dropping it would give wrong advice half the time.
+
+Now the same scenario as a closed question with nothing wrong in it, from
+someone who has read the runbook: *"So the worker is capped at 512Mi because
+that is what the old node pool allowed, correct?"* — "Yes." The reasoning is
+already in the question. Confirming a fact the user has read is not a request
+to re-derive it.
```

60 words. The `full` slice goes from 1,041 to 1,101 words and `rules_cksum`
from **594915793** to **864847550**.

### The claim: the file has never rendered an answer that withholds its grounds

[Round 60](round-60.md) took the file's one demonstration block apart against
three word-matched replacement rungs and found which of its three properties
carries the effect:

| rung | property removed | share of the gap |
|---|---|--:|
| `repl-told` | rendered | **−0.16** [−0.47, +0.07] |
| `repl-unlabelled` | mapped to a level | +0.22 [+0.01, +0.41] |
| `repl-unframed` | worked from a question | **+0.52** [+0.33, +0.72] |

The worked question is about half of what the block does; showing rather than
telling, as such, is none of it. So the lever this file has is a worked
question, and the question this edit works from is the one the file has never
had: **a closed question with a true premise, answered in one word.**

Every rendered answer in the file today supplies its grounds. All three rows of
the demonstration table do. The shortest specimen anywhere in the file is
ultra's two sentences, *"Only if memory is flat, not climbing. Check
`kubectl top pod` first."* Haiku's failure on the settled cells is precisely
emitting grounds it was not asked for, and the file contains no instance of an
answer declining to.

### Why this is not round 64 again

[Round 64](round-64.md) added a worked closed question and reverted, moving one
cell of three. Its example is a **false-premise** question and its rendered
answer is *"Only if memory is flat. A climbing curve is a leak, and a bigger
limit only delays the next kill."* — a two-clause answer that supplies its
grounds, closing with *"A closed question gets the answer and the correction
that makes it true, then stops."* It demonstrates how to append a correction.
On a true premise there is no correction to append, so that specimen offers no
template at all for the behaviour this round is about.

Both consulted targets agreed on this point independently and it is the one
thing about this round neither disputed. Round 64's own reading — that adding a
second worked example to a file that already has one is a diminishing return —
remains a live competing explanation, and if this edit is null that reading
gains its second data point rather than being refuted.

### Why not the fifth telling sentence

The obvious cheaper edit is to generalise the existing `lite` bullet:

```
- No recap of work visible in the diff.
+ No recap of work visible in the diff, or of a document the user has just
+ read and paraphrased back at you.
```

DeepSeek argued for exactly this and the argument is good — it edits a rule
rather than adding one, and its failure mode is a clean null rather than a
tripped counter. It is **not** what this round buys, for the reason Kimi gave:
the file already tells haiku what to do, four separate times, and haiku ignores
all four.

- *"A yes/no question gets a word or a line."* (above every level marker)
- *"No recap of work visible in the diff."* (`lite`)
- *"Lead with the answer or the action taken. Reasoning only if the user needs
  it to act on the answer."* (`full`)
- *"No teaching a concept the question already shows the user knows."* (`full`)

A fifth is the intervention class [round 48](round-48.md) bounded over seven
nulls: *"instructing the model to check its own length does not change its
length."* Round 60 prices telling at −0.16 of the gap. The generalisation is
the fallback for round 72 if the specimen is null, and it is written down here
so that choosing it later is not a choice made after seeing numbers.

## The registered hypothesis

> Adding a worked closed question whose premise is **true**, rendered with a
> one-word answer, to `rules/laconic.md` should **reduce median prose words on
> `settled-retention`, `settled-failover` and `settled-rounding`**, laconic
> arm, haiku, against this round's own simultaneously generated master
> control.

**Endpoint:** prose words by `metrics.score`, per cell, 25 runs a side.

**Primary test: a stratified one-sided permutation.** The statistic is the mean
over the three cells of (edit median − control median); the side label is
permuted *within each cell*, 200,000 resamples, seed 71, so cell composition is
held fixed and a cell with more runs cannot outvote a smaller one. One-sided,
because the edit is directional.

**Three cells cannot reach alpha on a sign test**, which is what every other
round in this cluster combines per-cell permutations with: two-sided exact at
3 of 3 is p = 0.25. The stratified permutation is DeepSeek's answer to that,
and it replaces the sign test rather than supplementing it.

**Consistency requirement, registered as a separate condition.** A stratified
permutation can be carried by one cell that separates hugely while the other
two sit still, and on three cells this round will not accept that. All three
cells must vote, all three point estimates must fall, and no cell may separate
*upward* at two-sided permutation p < 0.05. `score_settled.decide` holds all
of it and its selftest exercises each branch.

**One look.** The buy is staged only in the sense that the round-wide arm is
bought after the target passes; the target itself is scored once, at 25 reps a
side, and no extension is contemplated. No alpha correction applies.

**[#131] stratification.** The settled cells read their fixture in 180 of 180
runs of the instrument pass. A cell whose reading rate crosses between the two
sides does not vote, and the rates are reported whether or not any crossed.

**[#209] mixture.** Every case ends `Don't edit anything.`, and the instrument
pass recorded 0 mutating runs in 360. A cell holding one does not vote.

### The falsifier, and why it is correctness rather than length

An edit that merely suppresses length would also shorten the `unsettled-*`
twins, where the words are required. But **length on the twin is a diagnostic,
not a veto** — Kimi's correction, and it is right: a 40-word denial that names
the record's mechanism is this edit working, not failing, and a median bar on
the twin would reject it. Haiku's twins have almost no length room anyway (98
settled against 113 unsettled, p = 0.061), so a length bar there would be
measuring noise.

What is registered instead, over all six twin cells on **both** models:

1. **The deny rate may not fall**, pooled, one-sided Fisher p < 0.05 rejects.
   Control reads 85 of 90 under master rules, so there is real room below the
   ceiling for a fall to register.
2. **The correction rate may not fall**, same test. `score_settled.CORRECTION`
   requires the record's *mechanism* — the 14-day prune, the manual promotion,
   the per-line rounding — so a bare *"No."* fails it. It reads **180 of 180**
   twin responses under master rules, which makes it a fall detector at a
   ceiling ([#94]): it can register a regression and cannot register an
   improvement, and it has no measured false-positive rate because the shape it
   screens for does not occur under master rules.

Sonnet is in the falsifier and not in the target because the risk profiles
differ by model: on the settled cells sonnet has nothing left to cut, and on
the twins sonnet is where an under-answering regression would appear first.
That split is DeepSeek's.

## Power, stated before the numbers

Simulated from the instrument's own per-cell empirical distributions, 25 runs a
side, 200 trials a point, scoring the **full registered verdict** including the
consistency requirement:

| edit median | full registered pass rate |
|---|--:|
| 98 words (no effect) | **0.01** |
| 93 words (−5%) | 0.20 |
| 88 words (−10%) | 0.68 |
| 83 words (−15%) | **0.90** |

The consistency requirement costs power and buys a null pass rate of 0.01
against the permutation's own 0.04, which is the trade this round wants: on
three cells a false accept is the expensive error.

**What the round can and cannot see.** It is powered for a 15% median
reduction and roughly a coin flip at 10%. An edit that moves haiku from 98 to
90 words is real and this round will call it null. That is stated here rather
than after the fact.

## The harm this edit can do, and what the round can see of it

A rendered one-word answer is the most dangerous specimen this file could
carry, and rounds 07 to 10 are the reason to worry: a licence bounded in prose
bleeds, and a licence bounded by the section it sits under does not. Three
things bound this one, and none of them is a precedence sentence:

- It sits **inside** `## Never cut (every level, including ultra)`, after the
  full list. A reader reaches "Security warnings", "Confirmation before
  destructive or irreversible actions" and "Ordered instructions: every step"
  before reaching *"Yes."*
- Its conditions are carried by the worked question itself rather than by
  prose around it — closed, premise true, source already read. Round 60's
  finding is that an example needs a question to be an example of; the
  corollary is that the question is where an example's antecedent lives.
- The coda names the surplus shape (*"not a request to re-derive it"*) and
  grants no general licence to be short.

What sees it anyway: the four fatal counters, round-wide over all 37 scored
cases, bought if and only if the target passes. `ordered-steps`/haiku and
`destructive` are the cells rounds 07 to 10 broke and are where a leak would
land. A [#164] item 2 note: this edit renders no `Wrong:`/`Right:` pair, so it
pre-registers no cell on that ground.

## Pre-mortem, registered

I expect this to be **null, with the point estimate moving in the registered
direction and not separating** — the second of the three rejection classes.
The reason is in the instrument's own premise contrast: haiku spends 98 words
when the premise is true and 113 when it is false, p = 0.061, so it is barely
routing on what the question needs at all. A specimen works by being
recognised as *this kind of question*, and a model that does not discriminate
true premise from false has no hook to hang the recognition on. Sonnet, which
does discriminate (32 against 61, p < 0.00001), is already at the floor and
cannot show it.

The second way is the one the pre-mortem should be honest about wanting: the
target passes and a fatal counter rejects on `ordered-steps`/haiku, which is
where rounds 07, 08 and 09 put a bounded licence and read 6, 3 and 5 against a
baseline 2. That would be a clean, informative rejection and would say the
specimen is real and mislocated rather than inert.

The way I do **not** expect it to fail is the twin falsifier. Making the model
stop correcting a false premise is a large behavioural change and this edit is
60 words appended to a 1,041-word file.

## Buying order, stopping at the first failure

1. **The scoped batch.** 9 cells (3 settled on haiku, 6 twins across two
   models), 25 reps a side, two sides, 450 generations. No judge call: every
   endpoint above is deterministic.
2. **The round-wide arm and its judgments**, for the four fatal counters, only
   if step 1 passes. 220 generations and 185 judgments at 5 reps against
   `round-21.json`.
3. **The replication** (step 8), only for an edit that has passed both.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a `master`
worktree, both writing into this tree, so era and CLI release cancel between
the sides instead of confounding them ([round 38](round-38.md),
[round 37](round-37.md)). Four shards, `--concurrency 4` declared on each,
which is the ceiling [#255] enforces.

```sh
git worktree add /tmp/laconic-control master
# edit side, from this branch, two shards:
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells 'settled-*:haiku,unsettled-*:haiku,unsettled-*:sonnet' \
  --reps 12 --rep-offset 20 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-71-edit-1.json &
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells 'settled-*:haiku,unsettled-*:haiku,unsettled-*:sonnet' \
  --reps 13 --rep-offset 32 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-71-edit-2.json &
# control side, the same two from /tmp/laconic-control, writing back here
```

`--rep-offset 20` starts above the instrument pass's reps 5 to 19, so no
generation key is shared with it and a later merge of the files discards
nothing. `python3 evals/bench/release.py` is run over the four snapshots before
any contrast is read out of them, per [#272]: this round's two sides are in
separate files, which is exactly the shape the audit exists for.

`bash tools/reclaim-scratch.sh` removes the control worktree when the round is
scored; `/tmp` is tmpfs here and a worktree is 145 MiB of memory.

## Where the design came from

Sharpened by `tools/consult.sh`; two of three targets answered and both changed
what was built. Codex was asked and did not answer inside 420s.

- **DeepSeek** supplied the primary test. I had planned the pooled share above
  80 words with a stratified permutation; it argued the continuous prose-word
  count is strictly more powerful at the same n and that the binary is powered
  only for large effects, so the share is demoted to disclosure. It supplied
  the consistency requirement — *"the pooled test will happily pass on one
  lucky cell"* — and the model split on the falsifier, sonnet being where an
  under-answering regression appears first. It argued **against** the edit this
  round buys, on the ground that a bare *"Yes."* is caught between needing to
  be bare to differ from round 64 and needing to be bounded to be safe; that
  argument is recorded in "The harm this edit can do" rather than accepted, and
  it is the reason the placement discussion is three bullets long.
- **Kimi** supplied the falsifier's shape. I had registered a median-collapse
  bar on the twins and it pointed out that a correct 40-word denial trips it:
  *"Length on the twin is a diagnostic, not a veto. Correctness is the veto."*
  `CORRECTION` exists because of that. It also gave the argument that decided
  the edit over the generalisation — the file already tells haiku four times
  and haiku ignores it — and proposed a prose-bounded version of the specimen
  which was **not** adopted, because prose bounding is the thing rounds 07 to
  10 found does not work.
- Both independently confirmed that round 64's null does not price this edit,
  for the same reason: its specimen renders answer-plus-correction and this one
  renders a bare confirmation.

## What this round does not claim

Nothing here says the [#136] report is a single-turn phenomenon. The reported
failure is a register inherited from four turns of the model's own prose, and
[round 32](round-32.md) and
[`register-inheritance-136.md`](register-inheritance-136.md) both say these
cold single-turn fixtures cannot reach it. What they can reach is the same
rule failing on the same question shape, which is what 34 of 45 above 80 words
is.

---

## Results

*Nothing above this line was computed. Everything below it was.*

[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#305]: https://github.com/JordanMPDS/laconic/issues/305
