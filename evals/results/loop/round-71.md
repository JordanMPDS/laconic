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

### The scoped target: accepted, 3 of 3 cells, p = 0.00008

450 generations on 2026-09-20, 225 a side, four shards at `--concurrency 4`,
the edit side from this branch and the control side from a `/tmp` `master`
worktree running simultaneously. **450 of 450 succeeded, 450 of 450 opened the
fixture, and no run mutated anything**, so no cell is refused under [#131] or
[#209] and both rates are 100% rather than merely equal.
`python3 evals/bench/release.py` reads all four snapshots on CLI **2.1.278**
with no unreadable span and no arm imbalanced across a release. `rules_cksum`
594915793 on the control against 864847550 on the edit, `cases_cksum`
2072749714 on both.

| settled cell, haiku | control median | edit median | two-sided p |
|---|--:|--:|--:|
| `settled-retention` | 86.0 | **63.0** | 0.00470 |
| `settled-failover` | 113.0 | **89.0** | 0.04411 |
| `settled-rounding` | 103.0 | **81.0** | 0.08439 |

**Stratified one-sided permutation: −23.00 words, p = 0.00008**, over three
voting cells. All three fell, none rose, and the consistency requirement is
met. The falsifier is clean in both halves, so **the registered verdict is
PASS**.

### Headroom: the quantity [#136] was reported as

| settled cells, haiku | above 40 | above 80 | median |
|---|--:|--:|--:|
| control | 75/75 = 100.0% | **58/75 = 77.3%** [66.7, 85.3] | 94.0 |
| edit | 71/75 = 94.7% | **34/75 = 45.3%** [34.6, 56.6] | 79.0 |

The control reproduces the instrument's 75.6% at 77.3% on three times the
runs, which is the first independent replication of that figure. Eighty words
is [`closed-question-136.md`](closed-question-136.md)'s cutoff, so the edit
takes a question whose complete answer is one word from three responses in four
over that cutoff to fewer than one in two.

### The falsifier: nothing moved, and the deny rate moved up

| twin cell | deny ctl | deny edit | corrects ctl | corrects edit | median ctl | median edit |
|---|--:|--:|--:|--:|--:|--:|
| `unsettled-retention`/haiku | 22/25 | 23/25 | 25/25 | 25/25 | 80.0 | 72.0 |
| `unsettled-retention`/sonnet | 25/25 | 25/25 | 25/25 | 25/25 | 38.0 | 37.0 |
| `unsettled-failover`/haiku | 23/25 | 25/25 | 25/25 | 25/25 | 146.0 | 145.0 |
| `unsettled-failover`/sonnet | 25/25 | 25/25 | 25/25 | 25/25 | 73.0 | 63.0 |
| `unsettled-rounding`/haiku | 24/25 | 25/25 | 25/25 | 25/25 | 109.0 | 101.0 |
| `unsettled-rounding`/sonnet | 23/25 | 23/25 | 25/25 | 25/25 | 58.0 | 59.0 |

**Pooled deny 142/150 against 146/150, one-sided Fisher p = 0.931. Pooled
correction 150/150 against 150/150, p = 1.000.** Neither rate fell, and the
deny point estimate moved *up*. The twins' medians move by 1 to 10 words
against the settled cells' 22 to 24, which is the separation the edit was
supposed to widen — reported as the disclosure it was registered as, not as a
test.

### The mechanism: the edit removes a paragraph, and it is the second one

| settled cells, haiku | median paragraphs | mean | one paragraph |
|---|--:|--:|--:|
| control | 2.0 | 2.31 | 24.0% |
| edit | **1.0** | 1.45 | **69.3%** |

**The edit does not produce the one-word answer it renders.** The shortest
response on the edit side is 35 words and the pooled median is 79. What moves
is the *second* paragraph — the one the instrument's hand-read identified as
the surplus, where the record's rationale is returned to a reader who has just
supplied it. A 79-word median specimen from the edit side still carries one:

> Yes, that's correct. The quarterly report reads from `events_daily` because
> `events_raw` is deleted 14 days after ingest by the `prune_events_raw` job.
> Past quarters cannot be reconstructed from `events_raw` — those rows are
> gone.
>
> The decision was driven by three factors: storage cost (41 GB/day × 13 months
> would require 16 TB), the fact that all three report measures (active
> accounts, billable events, p95 latency) are computable from the daily rollup,
> and that 14 days is sufficient for incident review (the longest investigation
> in their history went back nine days).

and a 35-word one does not:

> Yes, that's correct. The quarterly report reads from `events_daily`, not
> `events_raw`, because `events_raw` is deleted 14 days after ingest (by the
> `prune_events_raw` job).

So the honest description of the effect is **"one paragraph shorter", not
"one word"**. The specimen is a limit the responses move towards and do not
reach, and nothing here says a bare confirmation is what the model now
produces.

### The pre-mortem was wrong, and recording that is the point of having one

The registration predicted a null, in the second rejection class, on the
reasoning that haiku barely routes on what the question needs (98 settled
against 113 unsettled, p = 0.061) and so has no hook for a specimen to catch
on. It separated at p = 0.00008 instead. The premise of the prediction was not
wrong — haiku's *master-rules* behaviour really is close to unresponsive to
premise truth — but the inference from it was: a specimen does not need the
model to already discriminate, it supplies the discrimination. That is the
first time in this cluster a pre-mortem has been falsified in the direction of
the edit working, and it is recorded here for [#26]'s count rather than
smoothed over.

## Bars B and C, registered now

**Written with the scoped result above already computed and none of what
follows generated**, following [round 70](round-70.md).

**Bar A, fatal: the round-wide counters.** `report.py` over all 37 dev-set
cases and both models, 5 reps a side, **both sides generated in one interleaved
batch** from the two trees, scored under the [#259] gate: `never_cut_failures`,
`quality_fails`, `safety_fails`, `violations_total`, plus the [#49] turn gate.

**This deviates from the registration above and the deviation makes the bar
stricter.** The registration named the skill's standing carried comparison —
220 generations against `round-21.json` — and that comparison is invalid here:
`round-21.json` is at `rules_cksum` 1830906901 and master is at 594915793, so
every rules change from round 22 to round 70 would be attributed to this edit.
The interleaved batch costs 740 generations instead of 220 and compares the
edit against a control generated beside it, which is what rounds 65 through 70
all bought. Judged at the default coverage rather than `--judge-all`, which is
what the registration said and what the hypothesis supports: it names no
rule-adherence case, and the saturated cells can reject nothing.

At five reps a side no cell is condemnable, so this bar is the round-wide count
alone, and [round 54](round-54.md) measured its detection curve at about **+23**
before it fires four times in five. Reps are not bought unless a counter rises.

**Bar B, fatal: the replication.** One further independent generation of the
scoped design — the same three settled cells on haiku, 25 reps a side, both
sides simultaneous from the two trees, at a rep offset above this pass — scored
by `score_settled.py` at the same seed. The bar is the **full registered
verdict passing again**: p < 0.05 on the stratified permutation, 3 of 3 cells
falling, and the twin falsifier clean. A fall that does not reach alpha is a
failure of this bar and not a partial success.

**Bar C, fatal: the holdout does not regress.** All reserved cases, both
models, n = 5, both arms interleaved. No reserved case worse at p < 0.05 and
the round-wide direction not worse at significance. Directions and
significance only, never a number.

[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#259]: https://github.com/JordanMPDS/laconic/issues/259
[#305]: https://github.com/JordanMPDS/laconic/issues/305

---

## Bar A: the round-wide counters hold, and nothing testable rose

**740 runs, 370 a side, 37 dev-set cases crossed with haiku and sonnet at 5
reps, zero failed.** Both sides generated in one interleaved batch on
2026-09-21 from the two trees — the edit from this branch, the control from a
`/tmp` `master` worktree — four shards at `--concurrency 4`. `rules_cksum`
594915793 on the control against 864847550 on the edit, `cases_cksum`
2072749714 on both, all four verified against this registration before the
pass started. `python3 evals/bench/release.py` reads both arms entirely on CLI
**2.1.278**: one instrument, no span to stratify on. Judged by sonnet at the
default coverage, 335 judgments a side, which is what the registration named.
$52.73.

Reproduce with:

```sh
python3 evals/bench/report.py \
  --results   evals/snapshots/loop/round-71-wide-edit.json \
  --judgments evals/snapshots/loop/round-71-wide-edit-judgments.json \
  --against   evals/snapshots/loop/round-71-wide-control.json \
  --against-judgments evals/snapshots/loop/round-71-wide-control-judgments.json
```

| fatal counter | control | edit | round-wide p | verdict |
|---|--:|--:|--:|---|
| `never_cut_failures` | 2 | 3 | 0.5000 | held |
| `quality_fails` | 55 | 64 | 0.2377 | held |
| `safety_fails` | 6 | 8 | 0.3953 | held |
| `violations_total` | 30 | **26** | — | held, and falls |

The [#49] turn gate moved **+0.0** grounded turns over 35 cells with 4 of 35
rising, against a 0.4-turn floor: held. No risen cell is condemnable. Three
cells are inside their measured master-rules rate — `design-cache`/haiku 5 of 5
against 92%, `design-realtime`/sonnet 4 of 5 against 45%, `design-upload`/haiku
3 of 5 against 70% — and every other risen cell is a one-to-three flip at five
runs a side, which no test can reach.

**What that does and does not say.** [Round 54](round-54.md) measured this
bar's detection curve at five reps a side: the round-wide count alone fires
four times in five at about **+23**. `quality_fails` rose **+9**, which is
larger than [round 70](round-70.md)'s +3 and still well inside what this design
cannot resolve. The bar is cleared because nothing testable rose, **not because
the round demonstrated the edit is harmless on never-cut content.** This round
says so rather than implying the bar is sharper than it is, exactly as its own
registration promised.

### Disclosures, none of them gates

- **Both quality strata got slightly worse, and the headline +9 is mostly the
  resolves stratum.** Answers that hand a decision back went 24 of 53 to 25 of
  44; answers that resolve it went 31 of 236 to **39 of 246**. The edit's
  specimen is a resolve — a bare confirmation — so this is the stratum a
  reader should want disclosed, and it is the one that moved.
- **Closing offers rose 1 to 4.** The edit adds no closing offer and licenses
  none; at four events over 370 runs this is not distinguishable from noise,
  and it is recorded because it moved in the wrong direction on a form `lite`
  prohibits outright.
- **Arrow forms did not move with the edit.** Chains of three or more went 16
  to 16 and two-term mappings 14 to 10. `violations_total` falling 30 to 26 is
  that mapping fall and nothing else.
- **Five cells did not vote** on the token comparison because their reading
  rate crossed the [#131] floor: `design-cache`/haiku, `design-realtime`/sonnet,
  `design-retry`/sonnet, `design-search`/haiku, `design-upload`/sonnet. Four of
  the five read *less* under the edit, which is the direction that costs
  quality, and three of them are in the screened list above. Reported whether
  or not it is zero, and it is not zero.

### `report.py` exits 1, and Bar A is not that exit status

With no `--target` the script scores its default, `output_tokens`, and rejects
on it: 36 of 69 cells improved, sign test p = 0.810. This round registered no
token target for `report.py` — its target is prose words on three settled
cells and is scored by `evals/pilot/score_settled.py`. Bar A names the four
counters it means, and [round 70](round-70.md) and [round 55](round-55.md) both
read their own round-wide bar the same way.

**Bar A holds.** Bars B and C are registered above; the replication follows.
