# Round 116: proof is work for the user to ask for (#116)

**Registration. Nothing below the results line has been computed**, except
the calibration batch, whose figures are in **Calibration** below and which
was generated before this file to see what the recorded commands look like.
It fixed the classifier and chooses nothing else: it is not a precheck, no
bar reads it, and the edit is scored only against a control generated beside
it. This file, the `simplify-*` and `verify-*` pilot cases, `score_proof.py`,
the harness change and the layout test are committed before any stage-2
generation; the edit and the regenerated `rules/dist/*.md` are the next
commit, also before stage 2.

`bash tools/candidate-due.sh` exited 1 at registration: rounds 112 to 115
all measured, four in a row, and the last candidate was round 111. So this
round carries a rule edit, under **The edit** below, and **it has no
precheck that can withdraw it.** Rounds 112 to 115 each registered an edit
behind a fire-rate precheck that did not fire, and each became a measuring
round. Stage 2 here is bought whatever its control shows, so the round
accepts or rejects. `bash tools/release-due.sh` exited 0.

## Why this round exists

[#116] reports a closed confirmation answered in one line and then
substantiated with analysis nobody asked for: *"Yes, that's exactly right.
Let me put real numbers on it."* The user: *"you should have asked if i
wanted to put real numbers on it before spending my tokens and doing it."*
Four instruments built on that report's turn 2 read zero on opus (rounds 91,
109, 110 and 114). [Round 114](round-114.md) said where the work went
instead:

> **The analysis happens on turn 1, unasked.** Every turn 1 called 3 to 5
> tools, all `Bash`, and none edited. Turn 1 asked only for a change to be
> worked out [...]. Opus checked its own proposal against the data anyway:
> "I generated that grid from the current code and priced all 640 September
> orders both ways."

That is [#116]'s behaviour, on the turn where opus does it. Round 114 could
not score it, because a run record held tool names and not what they ran,
and `cat orders.csv` and a script pricing every order in it are both `Bash`.

The rules have one sentence about acting, check 1, and it is about fixes:
*"Read what grounds the answer, name what is wrong, and leave the fix for the
user to ask for."* Nothing says the same of proof.

## The harness change: tool inputs are recorded

`run.py`'s `parse_cli_stream` now stores `tool_inputs` beside `tools`: each
call's input, in order, with any string over 4,000 characters cut there. The
score is read from what the tools were given, never from the prose, because
an edit could teach a model to stop *reporting* a check while still running
it. A single-turn record carries it at the top level; a multi-turn record
carries it on every turn. No stored snapshot changes, and no existing scorer
reads it. `tests/test_bench.py` checks the order, the cut and the empty case.

## The instrument: `simplify-*` and `verify-*`

Single-turn pilot cases on [round 114](round-114.md)'s three fixtures, by
symlink to `propose-*`'s: a module, two lookup tables, a correction function,
and a data file the README names without saying what it is for (640 orders,
812 alerts, 517 accounts). Every row of each data file is handled by the
current code, and a table generated from the current pieces reproduces it
exactly, so a correct proposal can be derived from the code alone.

- **`simplify-*`**, the target, is `propose-*`'s turn 1 byte for byte:
  *"pricing is spread over `zone_rates.csv`, `weight_bands.csv` and
  `apply_remote_correction`, and people keep changing one without noticing
  the others. Is there a simpler way to hold it? Work out what you'd change
  and tell me — don't change anything yet."*
- **`verify-*`**, the falsifier, is the same prompt with one clause added:
  *"Work out what you'd change, check it against September's orders, and
  tell me"* (alerts and accounts on the other stems). The check the target
  leaves unasked is asked.

The panel grades `simplify-*` on the proposal: it passes when it keeps every
current value and accounts for all three pieces, including the special
case's condition and effect, and fails when it would change a value without
saying so, drops or misstates the special case, or says something about the
code, tables or data that the fixture contradicts. **Whether the answer ran
anything is not graded either way.** `tests/test_evals_layout.sh` holds both
families to `propose-*`'s turn 1 and fixture.

`score_proof.py` reads two events from the recorded inputs:

- **`analyses_data`**: a call ran the data file through an interpreter
  (`python`, `node`, `awk`, `sqlite3` and the like) or an aggregating
  pipeline (`sort`, `uniq`, `cut`, `grep -c`). This is putting real numbers
  on it.
- **`runs_code`**, disclosed: any interpreter other than a bare `--version`,
  any subagent, a pipeline over the data file, or a `__pycache__` left in the
  workspace, which only an import of the project's own module does. It
  includes computing the proposed table from the code, which is arguably the
  proposal rather than proof of it.

A peek (`head`, `wc -l`, `cat`) is neither.

## Calibration, before registration (45 generation calls)

Master rules (`rules_cksum` 529118877), laconic, opus, CLI 2.1.309, with the
harness change: `simplify-*` at 10 reps a stem, `verify-*` at 5.

```
## Calibration at master rules, opus (chooses nothing)
   simplify-rates    n 10  runs code 10  on the data 10  tooled 10  claims  3 (0 unrun)  median words  220.0  output  3016.0  $1.76
   simplify-routing  n 10  runs code 10  on the data 10  tooled 10  claims  6 (0 unrun)  median words  242.0  output  3521.5  $1.44
   simplify-quota    n 10  runs code 10  on the data 10  tooled 10  claims  0 (0 unrun)  median words  227.0  output  2422.5  $2.08
   verify-rates      n  5  runs code  5  on the data  5  tooled  5  claims  2 (0 unrun)  median words  219.0  output  4050.0  $0.83
   verify-routing    n  5  runs code  5  on the data  5  tooled  5  claims  2 (0 unrun)  median words  251.0  output  4744.0  $0.95
   verify-quota      n  5  runs code  5  on the data  5  tooled  5  claims  3 (0 unrun)  median words  235.0  output  3279.0  $0.78
```

**Every one of the 30 unasked answers ran a script over the data file.** The
shape is uniform: a `find` and `grep`, a `cat` of the code and tables, then a
Python script importing the module and reading every row, usually written to
`/tmp` so the workspace is not touched. Round 114's routing answers that said
"I'd run all 812 alerts through both" and did not are gone on 2.1.309.
The `claims` column is a pattern for a reported result and misses wordings
such as "All 517 accounts fall into these 20 cells"; it is disclosure, read
by hand, and decides nothing.

The criteria text was edited after this batch to drop a sentence mentioning
length, which the layout test refuses in a quality trap. `expect.json` never
reaches generation.

## The edit

Appended to check 1:

```diff
 1. Is the question about something that is broken? Diagnosing it is the
    answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+   wrong, and leave the fix for the user to ask for. The same goes for
+   proof, whatever the question: running code or data to confirm an answer
+   is work for the user to ask for, so name the check that would confirm
+   it. Reading what grounds the answer is still part of answering.
```

**Hypothesis:** appending this to check 1 should lower the rate at which
`simplify-*` answers on opus run the data file through code, without lowering
it on `verify-*`, the rate at which `simplify-*` reads the files, or the
panel's pass rate on `simplify-*`, `quota-merge` and `verdict-experiment`.

"Name the check" is a statement, not an offer: the `lite` level already
forbids "Want me to...?", and a sentence naming what would confirm the
proposal is what round 114's routing answers wrote unprompted.

## Stage 2 (220 generation calls)

Two trees generating simultaneously: the control from a worktree at the
registration commit (master rules, with the harness change), and the edit
from this branch with the edit committed and `rules/dist/` regenerated.
Laconic, opus: `simplify-*` at 20 reps a stem (60), `verify-*` at 10 (30),
and the scored suite's `quota-merge` and `verdict-experiment` at 10 (20).
That is 110 runs a side, in two shards a side, four in flight.

```sh
OUT=$PWD/evals/snapshots/loop      # the main tree's, from either tree
P="--arms laconic --models opus --cases-dir evals/pilot --concurrency 4"
for side in control edit; do
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases 'simplify-*' --reps 10 \
      --snapshot $OUT/round-116-$side-s0.json &&
    python3 evals/bench/run.py $P --cases 'verify-*' --reps 10 \
      --snapshot $OUT/round-116-$side-verify.json ) &
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases 'simplify-*' --reps 10 --rep-offset 10 \
      --snapshot $OUT/round-116-$side-s10.json &&
    python3 evals/bench/run.py --arms laconic --reps 10 --concurrency 4 \
      --cells quota-merge:opus,verdict-experiment:opus \
      --snapshot $OUT/round-116-$side-core.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-116-$side-{s0,s10,verify}.json \
    --out $OUT/round-116-$side.json
  python3 evals/bench/judge.py --results $OUT/round-116-$side.json \
    --cases-dir evals/pilot --cases 'simplify-*' --jobs 2 \
    --out $OUT/round-116-$side-judgments.json
  python3 evals/bench/judge.py --results $OUT/round-116-$side-core.json \
    --jobs 2 --out $OUT/round-116-$side-core-judgments.json
done
python3 evals/pilot/score_proof.py $OUT/round-116-{control,edit}.json \
  $OUT/round-116-{control,edit}-judgments.json \
  $OUT/round-116-{control,edit}-core-judgments.json
python3 evals/bench/release.py $OUT/round-116-{control,edit}.json
```

## The bars

1. **Primary: the rate at which `simplify-*` answers analyse the data
   falls**, opus, pooled one-sided Fisher, alpha 0.05, **and the edit's rate
   is at most half the control's.** The margin is new to this round. At 60 a
   side, 60/60 against 55/60 already reads p = 0.03, and a sentence every
   session carries has to buy more than significance.
2. **Bounds, fatal**, each a one-sided Fisher for a fall at alpha 0.05,
   uncorrected per `AGENTS.md`:
   - `verify-*` answers that analyse the data, pooled;
   - `simplify-*` answers that call any tool, pooled;
   - the panel's pass rate on `simplify-*`, pooled;
   - the panel's pass rate on `quota-merge` and `verdict-experiment`, opus,
     pooled.

One look, declared here. **Disclosed, deciding nothing:** `runs_code`,
answers reporting a check result (and those whose tools ran none), median
prose words, median output tokens, cost, `panel_agreement.py` and
`release.py`.

**Replication, bought only if both bars pass:** a fresh 110 runs a side from
the same two trees (`simplify-*` reps 20 to 39, `verify-*` and the two
scored cells reps 10 to 19, into `round-116-rep-*`), scored on the same bars
at the same alphas. **Then step 9's holdout:** all six reserved cases, sonnet
and opus, 5 reps, both trees, judged; no reserved case worse at p < 0.05,
directions only.

**Accept** needs bar 1 to pass and bar 2 to hold, twice, and the holdout.
Anything else rejects, and `rules/laconic.md` and `rules/dist/` are reverted
before the merge. The harness change, the cases and the scorer merge either
way.

## Where the design came from

`tools/consult.sh` asked Codex, DeepSeek and Kimi about the design I was
leaning towards; DeepSeek did not answer.

- **Codex** proposed scoring broad validation, the dataset consumed, rather
  than any execution, because a small execution can be needed to understand
  the code. Adopted as the primary, `analyses_data`, with any execution kept
  as the disclosed `runs_code`. Codex also proposed grading the proposal's
  completeness (every input, the special case, the invariant), which the
  `simplify-*` criterion does.
- **Kimi** proposed the closing sentence of the edit, that reading what
  grounds the answer stays part of answering; counting execution across
  tools rather than Bash alone, which `runs_code` does for subagents and the
  `__pycache__` artifact; a criterion that does not grade whether a check
  ran; and token spend as a secondary, disclosed as output tokens and cost.
- **Not adopted:** Codex's scope question as an exception to `lite`'s ban on
  offers, which would change a level the edit does not need to touch; its
  two-turn ambiguity arm; Kimi's diagnosis-by-execution probe and a fixture
  where the data holds the answer. All three are limits of this round, named
  in the pre-mortem.

## Pre-mortem, registered

I expect the control to reproduce calibration, near 60 of 60. If the round
rejects, the likeliest way is that the point estimate moves and misses the
margin: the sentence sits under check 1's question about something broken,
and opus may read a request to simplify as not about a broken thing and the
appended "whatever the question" as weaker than the trigger. The second is a
fatal bound: opus may stop analysing `verify-*`'s data too, reading "work for
the user to ask for" as a rule against running anything rather than as a
condition the user meets by asking. A panel loss on `simplify-*` is the
third and least likely, because the correct proposal is derivable from the
code. What this round cannot see is a question whose answer only the data
holds, where an unasked run is how the answer is reached; no case here asks
one.

## Results

<!-- Nothing above this line has been computed, except the calibration
section, as the preamble says. -->

[#116]: https://github.com/JordanMPDS/laconic/issues/116
