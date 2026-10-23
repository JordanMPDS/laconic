# Round 118: running the data is work for the user to ask for (#116)

**Registration. Nothing below the results line has been computed.** This
file, the `count-*` pilot cases, their layout test and the `score_proof.py`
changes are committed before any generation; the edit and the regenerated
`rules/dist/*.md` are the next commit, also before generation.

`bash tools/candidate-due.sh` exited 1 at registration: round 117 measured,
and the last candidate was round 116. So this round carries a rule edit,
under **The edit** below, and **it has no precheck that can withdraw it.**
Rounds 109, 110 and 112 to 115 each registered an edit behind a fire-rate
precheck that did not fire and became a measuring round, which is how the
cap was overrun twice. The instrument here is [round 116](round-116.md)'s,
which read 60 of 60 at master rules on CLI 2.1.309, the release this round
starts on. Generation is bought whatever its control shows, so the round
accepts or rejects. `bash tools/release-due.sh` exited 0: v0.3.8 is tagged
and current.

## Why this round exists

[#116] reports a question answered and then substantiated with analysis
nobody asked for: *"Let me put real numbers on it."* Round 116 measured that
on the turn where opus does it, `simplify-*`: asked for a simpler way to hold
logic spread over two tables and a correction step, opus runs the workspace's
data file through a script on every answer, though a correct proposal is
derivable from the code alone. Its edit, a sentence appended to check 1 that
left *proof* for the user to ask for, was rejected on its margin: 60/60 to
42/60, a rate ratio of 0.70 against 0.50.

What the edit arm still ran says what it missed. Opus read "proof" narrowly:

- **pricing**, 20/20 to 5/20. It stopped pricing all 640 orders both ways and
  named the check instead. This is what the sentence said.
- **routing**, 20/20 to 20/20. Every answer counted the alerts to *size a
  finding*: *"In September, 22 urgent payments and ledger alerts went only to
  `finance-oncall`, and billing never got them."* The finding, that the
  docstring says "as well as the owner" and the code replaces the owner, is in
  the code; the 22 is from the data.
- **quota**, 20/20 to 17/20. `cut -d, -f2- accounts.csv | sort | uniq -c`, to
  *tally coverage*: "All 20 pairs have accounts in `accounts.csv`, so every row
  is in use."

Neither is proof, and neither is a fix, so a sentence hung on check 1, whose
question is whether something is broken, reached neither. This round gives
running the data a check of its own and names the two uses the last one
missed.

## The instrument: `simplify-*`, `verify-*` and `count-*`

`simplify-*` and `verify-*` are round 116's, unchanged: `propose-*`'s turn 1
alone, and the same prompt asking for the check against the data. Both share
`propose-*`'s fixture (a module, two lookup tables, a correction function,
and a data file the README names without saying what it is for: 640 orders,
812 alerts, 517 accounts). See [round 116](round-116.md#the-instrument-simplify--and-verify-).

**New: `count-*`**, the falsifier for the edit's own exception. One
single-turn question over the same fixture, asking how many rows of the data
file the correction step changes today, worded without "run", "check" or
"numbers":

| case | prompt | answer |
|---|---|--:|
| `count-rates` | How many of September's orders does `apply_remote_correction` change today? | 13 of 640 |
| `count-routing` | How many of September's alerts does `apply_payments_override` change today? | 22 of 812 |
| `count-quota` | How many of the current accounts does `apply_legacy_cap` change today? | 62 of 517 |

The counts were computed from the fixtures before this file was written. Each
is a small subset of a large file selected by the correction's predicate over
two columns, so no answer reads it off by eye. The panel passes an answer
that gives the number and fails one that gives a wrong number, none, or
declines, defers or offers to count instead of counting. An edit that leaves
running the data to the user has to still run it when the answer is a fact
only the data holds. `tests/test_evals_layout.sh` pins the prompt and holds
the fixture to `propose-*`'s.

`score_proof.py` reads its two events from the recorded tool inputs, as in
round 116, with one widening: a `Grep` call in count mode whose path or glob
names the data file now counts as analysing it, in both events, so a tally
moved from `Bash` to the search tool is not lost. No round 116 run made one
(its 1,375 calls are 1,372 `Bash` and 3 `Read`), and round 116 re-scores
identically: 60/60 against 42/60, reject. For `count-*` it also discloses,
with no judge, how many answers state the right number.

## The edit

A check of its own, before acting:

```diff
-One check before acting, and two before sending:
+Two checks before acting, and two before sending:
 
 1. Is the question about something that is broken? Diagnosing it is the
    answer; fixing it is not. Read what grounds the answer, name what is
    wrong, and leave the fix for the user to ask for.
-2. What is the smallest set of claims that fully answers this?
-3. Is anything here something the user did not ask for?
+2. Does the answer need the user's data run through code? Reading what
+   grounds the answer is part of answering. Running the data is not,
+   whether it would prove the answer, size a finding or tally what the data
+   covers: name the run, and leave it for the user to ask for. A question
+   that asks for a fact only the data holds has asked for the run.
+3. What is the smallest set of claims that fully answers this?
+4. Is anything here something the user did not ask for?
```

Round 116's sentence is not carried: this is master plus the new check, and
check 1 is master's.

**Hypothesis:** adding check 2 should lower the rate at which `simplify-*`
answers on opus run the data file through code, to at most half the
control's, without lowering it on `verify-*`, the rate at which `simplify-*`
calls a tool, or the panel's pass rate on `simplify-*`, `count-*`,
`quota-merge` and `verdict-experiment`.

## Generation (280 generation calls)

Two trees generating simultaneously: the control from a worktree at this
registration commit (master rules), and the edit from this branch with the
edit committed and `rules/dist/` regenerated. Laconic, opus: `simplify-*` at
20 reps a stem (60), `verify-*` and `count-*` at 10 (30 each), and the scored
suite's `quota-merge` and `verdict-experiment` at 10 (20). That is 140 runs a
side, in two shards a side, four in flight.

```sh
OUT=$PWD/evals/snapshots/loop      # the main tree's, from either tree
P="--arms laconic --models opus --cases-dir evals/pilot --concurrency 4"
for side in control edit; do
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases 'simplify-*' --reps 10 \
      --snapshot $OUT/round-118-$side-s0.json &&
    python3 evals/bench/run.py $P --cases 'verify-*' --reps 10 \
      --snapshot $OUT/round-118-$side-verify.json &&
    python3 evals/bench/run.py --arms laconic --reps 10 --concurrency 4 \
      --cells quota-merge:opus,verdict-experiment:opus \
      --snapshot $OUT/round-118-$side-core.json ) &
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases 'simplify-*' --reps 10 --rep-offset 10 \
      --snapshot $OUT/round-118-$side-s10.json &&
    python3 evals/bench/run.py $P --cases 'count-*' --reps 10 \
      --snapshot $OUT/round-118-$side-count.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-118-$side-{s0,s10,verify,count}.json \
    --out $OUT/round-118-$side.json
done
python3 evals/pilot/score_proof.py $OUT/round-118-{control,edit}.json
# only if bar 1 passes and the two judge-free bounds hold:
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-118-$side.json \
    --cases-dir evals/pilot --cases 'simplify-*,count-*' --jobs 2 \
    --out $OUT/round-118-$side-judgments.json
  python3 evals/bench/judge.py --results $OUT/round-118-$side-core.json \
    --jobs 2 --out $OUT/round-118-$side-core-judgments.json
done
python3 evals/pilot/score_proof.py $OUT/round-118-{control,edit}.json \
  $OUT/round-118-{control,edit}-judgments.json \
  $OUT/round-118-{control,edit}-core-judgments.json
python3 evals/bench/release.py $OUT/round-118-{control,edit}.json
```

## The bars

1. **Primary: the rate at which `simplify-*` answers analyse the data
   falls**, opus, pooled one-sided Fisher, alpha 0.05, **and the edit's rate
   is at most half the control's.** Round 116's bar, unchanged, so the two
   rounds read on one scale.
2. **Bounds, fatal**, each a one-sided Fisher for a fall at alpha 0.05,
   uncorrected per `AGENTS.md`:
   - `verify-*` answers that analyse the data, pooled;
   - `simplify-*` answers that call any tool, pooled;
   - the panel's pass rate on `simplify-*`, pooled;
   - the panel's pass rate on `count-*`, pooled;
   - the panel's pass rate on `quota-merge` and `verdict-experiment`, opus,
     pooled.

Judging is bought only if bar 1 passes and the two judge-free bounds hold,
because nothing it can show would turn a failed bar 1 into an accept. One
look, declared here.

**Disclosed, deciding nothing:** each stem's rates; `runs_code`; `count-*`'s
`analyses_data` rate and its judge-free count of answers stating the right
number; answers reporting a check result (and those whose tools ran none);
median prose words; median output tokens; cost; `panel_agreement.py`;
`release.py`; and a hand-read of ten edit-side `simplify-*` runs the
classifier scores as not analysing the data, drawn at seed 118, for any
tally the classifier misses.

**Replication, bought only if both bars pass:** a fresh 140 runs a side from
the same two trees (`simplify-*` reps 20 to 39; `verify-*`, `count-*` and the
two scored cells reps 10 to 19, into `round-118-rep-*`), scored on the same
bars at the same alphas. **Then step 9's holdout:** all six reserved cases,
sonnet and opus, 5 reps, both trees, judged; no reserved case worse at
p < 0.05, directions only.

**Accept** needs bar 1 to pass and bar 2 to hold, twice, and the holdout.
Anything else rejects, and `rules/laconic.md`, `rules/dist/` and the paired
`tests/test_bench.py` change are reverted before the merge. The `count-*`
cases and the scorer changes merge either way.

## Where the design came from

`tools/consult.sh` asked Codex, DeepSeek and Kimi about the design I was
leaning towards, with round 116's per-stem result; DeepSeek did not answer.

- **Kimi** proposed ending the exception on *"has asked for the run"* rather
  than *"has asked"*; widening it from a number to *a fact* only the data
  holds, so a "which rows" question is inside it; naming the two surviving
  uses in the check itself, as *size a finding* and as tallying; and counting
  a search-tool count over the data file, which `score_proof.py` now does.
  Kimi also asked that the routing criterion not reward the 22; it does not,
  and it passes a proposal derived from the code alone.
- **Codex** proposed the same distinction from the other side, that a number
  which strengthens a finding is still a check result, and a hand audit of
  the classifier's negatives, which is disclosed above. It also proposed
  per-stem disclosure beside the pooled primary, which `score_proof.py`
  already prints.
- **Not adopted:** Codex's `count-*` `analyses_data` rate as a fatal bound
  beside its panel pass rate. The harm a deferral does is a missing count,
  which the panel grades; an answer that reaches the right number another
  way has done no harm, so the rate is disclosed instead.

## Pre-mortem, registered

I expect the control to reproduce round 116's, near 60 of 60. If the round
rejects, the likeliest way is again a fall that misses the margin, now on
routing: opus treats the 22 as part of the decision it hands the user ("which
one is right?") and keeps counting it, reading the alert data as grounding
rather than as a run. The second is a fatal bound on `count-*`: the check's
first sentences are about not running the data, and an answer may name the
run and stop, reading the exception as an invitation to offer it. A fall on
`verify-*` is the least likely, because round 116's sentence, which said the
same thing about proof, held there at 30 of 30.

## Results

<!-- Nothing above this line has been computed, as the preamble says. -->
