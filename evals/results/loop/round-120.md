# Round 120: a coverage tally that only supports the answer is a run (#116)

**Registration. Nothing below the results line has been computed.** This file
is committed before any generation; the edit and the regenerated
`rules/dist/*.md` are the next commit, also before generation. The instrument,
`simplify-quota`/`verify-quota`/`count-quota` and `score_proof.py`, is
[round 118](round-118.md)'s unchanged, so no case or scorer changes with this
round.

`bash tools/candidate-due.sh` exited 1 at registration: round 119 measured,
and the last candidate was round 118. So this round carries a rule edit, under
**The edit** below. Its instrument fires at the current release: 15 fresh
`simplify-quota` runs on opus at master rules, CLI 2.1.310, analysed the data
in **4 of 15** (`runs code` 9 of 15). The round generates its own control and
edit simultaneously and accepts or rejects on the control it measures, so it is
not a precheck that can withdraw the edit unrun. `bash tools/release-due.sh`
exited 0: v0.3.9 is tagged and current.

## Why this round exists

[#116] reports a question answered and then substantiated with analysis nobody
asked for. Round 116 built its instrument and round 118 shipped the fix: a
check of its own, appended to `rules/laconic.md`, that leaves running the data
for the user to ask for. It took `simplify-rates` and `simplify-routing` from
20/20 to 0/20 "runs the data" and held both samples at 0.

It left one shape on one stem. On `simplify-quota` — asked for a simpler way to
hold limit logic spread over `plan_limits.csv`, `region_factors.csv` and
`apply_legacy_cap` — opus proposes one combined table and then runs
`cut -d, -f2- accounts.csv | sort | uniq -c`, a tally of which plan and region
pairs appear in the 517-row data file, to assert that "accounts use all 20
combinations, so the table can't be smaller." Round 118's replication read this
at 12/20; the fresh precheck above reads it at 4/15. The proposal is derivable
from the code and the two tables alone — every pair and the cap rule are
explicit there — so the coverage tally is work the question did not ask for.

Two things let it survive round 118's check 2. First, the tally is **bundled**:
`cut ... accounts.csv | sort | uniq -c` rides along in the same `Bash` command
that `cat`s the code and the tables, so at the moment the command is composed
the prohibition, keyed on the *motive* of a separate act, never fires. Second,
check 2's closing sentence — *"A question that asks for a fact only the data
holds has asked for the run"* — is an escape hatch opus reads itself into: it
construes "does my proposal cover the real accounts" as a fact the question
implicitly wanted, and the tally becomes part of "reading what grounds the
answer." Both readings were named by the `kimi` consult target when this round
was scoped; the edit below is its re-keying of the rule from motive to command
shape, with the escape hatch narrowed.

## The instrument: `simplify-quota`, `verify-quota`, `count-quota`

All three are round 118's, unchanged, over the same fixture (a module, two
lookup tables, a correction function, and `accounts.csv`: 517 account rows the
README names without saying what they are for). See
[round 118](round-118.md#the-instrument-simplify--verify--and-count-).

- `simplify-quota` asks for a simpler way to hold the logic, worked out and
  described but not applied. The coverage tally is unasked work.
- `verify-quota` is the same prompt plus *"check it against the current
  accounts"* — an explicit request, where the fact wanted (does the proposal
  match?) **is** the answer, so the edit must leave it running the data.
- `count-quota` asks *"How many of the current accounts does `apply_legacy_cap`
  change today?"* — a count only the data holds, which **is** the answer, so
  the edit must leave it counting and stating 62.

`score_proof.py` reads both events from the recorded tool inputs, never from
the prose. `analyses_data` is a command running `accounts.csv` through an
interpreter or an aggregating pipeline, or a `Grep` count over it; `runs_code`
is the wider disclosed event. Only `simplify-quota` is generated into the
scored snapshot, so the scorer's pooled total over its three stems equals
quota's; `simplify-rates` and `simplify-routing` are generated into a separate
disclosure snapshot as a regression guard.

## The edit

A full replacement for check 2, re-keying it from the motive of a separate act
to the shape of the command, and narrowing the exception to a fact that is
itself the answer:

```diff
-2. Does the answer need the user's data run through code? Reading what
-   grounds the answer is part of answering. Running the data is not,
-   whether it would prove the answer, size a finding or tally what the
-   data covers: name the run, and leave it for the user to ask for. A
-   question that asks for a fact only the data holds has asked for the run.
+2. Does the answer need the user's data run through code? Reading what
+   grounds the answer is part of answering; running the data is not,
+   whether to prove the answer, size a finding, or confirm your answer
+   fits the data's rows. The command's shape decides this, not your
+   motive: a command that pipes a data file through something counting,
+   sorting or aggregating it is a run even when it also reads the code you
+   needed, so read those files plainly and leave the run for the user to
+   ask for. A question has asked for the run only when the fact it wants
+   is itself the answer; a fact that would merely support the answer has
+   not.
```

Check 1 is master's, unchanged. Round 116's and round 118's wording is carried
except for check 2's two defeated readings.

The mechanism of this edit — deciding on command shape rather than motive, and
narrowing "a fact only the data holds has asked for the run" to "a fact that is
itself the answer" — was proposed by the `kimi` consult target
(`bash tools/consult.sh`). `codex` and `deepseek` did not answer.

**Hypothesis:** editing check 2 this way should lower the rate at which
`simplify-quota` answers analyse the data (`accounts.csv` through an
aggregating pipeline) on opus, to at most half the control's and past a
one-sided Fisher at alpha 0.05, without lowering it on `verify-quota`, the rate
at which `simplify-quota` calls any tool, or the panel's pass rate on
`simplify-quota`, `count-quota`, `quota-merge` and `verdict-experiment`.

**Pre-mortem.** The likeliest failure is the point estimate moving **with** the
registered direction and not separating: the edit lowers the coverage-tally
rate but not to at most half the control, nor past significance, because at the
~27% rate the precheck measured the round is powered to catch a near-kill, not
a mere halving. The consult's power estimate agrees — about 50% power for a
true halving at 100 runs an arm, and this round buys 40 a side. A second, less
likely failure is a fatal counter rejecting: the command-shape sentence could
make opus decline the asked-for run on `verify-quota` or `count-quota`, or stop
reading the files on `simplify-quota`, which the bounds catch. I do not expect
the point estimate to move **against** the direction; check 2's prose already
moved this exact behaviour to zero on two of three stems, and this edit only
closes the two readings the third survived through.

**One look, declared here.** The round generates 40 reps a side of the primary
cell in one pass and scores it once; there is no staged extension to correct
for.

## Generation (176 generation calls)

Two trees generating simultaneously: the control from a worktree at this
registration commit (master rules), the edit from this branch with the edit
committed and `rules/dist/` regenerated. Laconic, opus, `--concurrency 2` on
both (two CLI invocations in flight):

```sh
OUT=$PWD/evals/snapshots/loop
P="--arms laconic --models opus --cases-dir evals/pilot --concurrency 2"
for side in control edit; do
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases 'simplify-quota' --reps 40 \
      --snapshot $OUT/round-120-$side-simplify.json &&
    python3 evals/bench/run.py $P --cases 'verify-quota,count-quota' --reps 12 \
      --snapshot $OUT/round-120-$side-vc.json &&
    python3 evals/bench/run.py $P --cases 'simplify-rates,simplify-routing' --reps 8 \
      --snapshot $OUT/round-120-$side-guard.json &&
    python3 evals/bench/run.py --arms laconic --reps 10 --concurrency 2 \
      --cells quota-merge:opus,verdict-experiment:opus \
      --snapshot $OUT/round-120-$side-core.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-120-$side-{simplify,vc}.json \
    --out $OUT/round-120-$side.json
done
python3 evals/pilot/score_proof.py $OUT/round-120-{control,edit}.json
# only if the primary passes and the two judge-free bounds hold:
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-120-$side.json \
    --cases-dir evals/pilot --cases 'simplify-quota,count-quota' --jobs 2 \
    --out $OUT/round-120-$side-judgments.json
  python3 evals/bench/judge.py --results $OUT/round-120-$side-core.json \
    --jobs 2 --out $OUT/round-120-$side-core-judgments.json
done
python3 evals/pilot/score_proof.py $OUT/round-120-{control,edit}.json \
  $OUT/round-120-{control,edit}-judgments.json \
  $OUT/round-120-{control,edit}-core-judgments.json
python3 evals/bench/release.py $OUT/round-120-{control,edit}.json
```

## The bars

1. **Primary: `simplify-quota` answers that analyse the data fall**, opus,
   one-sided Fisher, alpha 0.05, **and the edit's rate is at most half the
   control's.** Round 118's bar, scoped to the one stem that still fires.
2. **Bounds, fatal**, each a one-sided Fisher for a fall at alpha 0.05,
   uncorrected per `AGENTS.md`:
   - `verify-quota` answers that analyse the data — the asked-for check still
     runs the data;
   - `simplify-quota` answers that call any tool — the proposal is still read
     from the files;
   - the panel's pass rate on `simplify-quota`;
   - the panel's pass rate on `count-quota`;
   - the panel's pass rate on `quota-merge` and `verdict-experiment`, opus.

Judging is bought only if the primary passes and the two judge-free bounds
hold, because nothing it can show turns a failed primary into an accept.

**Disclosed, deciding nothing:** `simplify-rates` and `simplify-routing`
`analyses_data` and `runs_code` (the regression guard: the two fixed stems must
not rise); each cell's `runs_code`, tool rate, median prose words, median
output tokens and cost; `count-quota`'s `analyses_data` rate and the judge-free
count of answers stating 62; answers reporting a check result; `panel_agreement.py`;
`release.py`; and a hand-read of ten edit-side `simplify-quota` runs the
classifier scores as not analysing the data, drawn at seed 120.

**Replication, bought only if the primary passes and every bound holds:** a
fresh 40 runs a side of `simplify-quota` and 12 a side of `verify-quota` and
`count-quota` from the same two trees (reps 40 to 79 and 12 to 23, into
`round-120-rep-*`), scored on the same bars at the same alpha. **Then step 9's
holdout:** all six reserved cases, sonnet and opus, 5 reps, both trees, judged;
no reserved case worse at p < 0.05, directions only.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `rules/laconic.md` and `rules/dist/` are
reverted before the merge.

[#116]: https://github.com/JordanMPDS/laconic/issues/116

---

## Result: accepted

**Accept.** The primary passed and every fatal bound held on both samples, and
the holdout held. The edit stays in `rules/laconic.md` and `rules/dist/`. All
generation was opus on CLI 2.1.310, control and edit from two trees at once
(`release.py` clean on every pair, no arm imbalanced across a release), about
$73 of generation and the panel's judging on top.

The control fired higher than the precheck: `simplify-quota` analysed the data
19/40 (47.5%) in the first sample and 16/40 (40.0%) in the replication, against
the precheck's 4/15.

### First sample

| metric (opus) | control | edit | one-sided p |
|---|--:|--:|--:|
| **Primary: `simplify-quota` analyses the data** | **19/40** | **0/40** | **7e-07** |
| `verify-quota` analyses the data (bound) | 12/12 | 12/12 | 1.0 |
| `simplify-quota` calls a tool (bound) | 40/40 | 40/40 | 1.0 |
| panel passes `simplify-quota` (bound) | 40/40 | 40/40 | 1.0 |
| panel passes `count-quota` (bound) | 12/12 | 12/12 | 1.0 |
| panel passes `quota-merge`, `verdict-experiment` (bound) | 19/20 | 20/20 | 1.0 |

The edit's rate is 0.000 of the control's, inside the 0.50 margin. The one
control miss on `quota-merge` is a control-side verdict; no edit-side scored
cell fell.

### Replication

A fresh 40 runs a side of `simplify-quota` and 12 a side of `verify-quota` and
`count-quota`, reps 40 to 79 and 12 to 23, from the same two trees:

| metric (opus) | control | edit | one-sided p |
|---|--:|--:|--:|
| **Primary: `simplify-quota` analyses the data** | **16/40** | **0/40** | **2e-06** |
| `verify-quota` analyses the data (bound) | 12/12 | 12/12 | 1.0 |
| `simplify-quota` calls a tool (bound) | 40/40 | 40/40 | 1.0 |
| panel passes `simplify-quota` (bound) | 40/40 | 39/40 | 0.5 |
| panel passes `count-quota` (bound) | 12/12 | 12/12 | 1.0 |

The one edit-side `simplify-quota` fail is a proposal the panel marked wrong on
its merits, not a tally; it still read the files and did not run the data.

### Disclosed, deciding nothing

- **`count-quota` still counts, and states 62.** Both samples: `analyses_data`
  12/12 both sides, and the judge-free count of answers stating 62 is 12/12 both
  sides. A question whose answer only the data holds still runs the data, and
  the answer is right.
- **The two fixed stems did not regress.** `simplify-rates` and
  `simplify-routing`, 8 reps a side, read `analyses_data` 0/8 on both sides;
  `runs_code` is 2/8 (control rates, two module imports) and 0/8 elsewhere.
- **`runs_code`, the wider event, fell too.** `simplify-quota` went 35/40 to
  4/40 (first sample) and 28/40 to 8/40 (replication): closing the coverage
  tally also cut the module imports that computed the table from the code,
  which is disclosed rather than gated because that import is arguably the
  proposal.
- **Prose did not shrink.** `simplify-quota` median prose words 189.5 to 205.0
  (first sample) and 197.5 to 216.0 (replication); median output tokens 2445 to
  2838 and 2628 to 2723. The edit removed a run, not words.
- **Hand audit.** Ten edit-side `simplify-quota` runs the classifier scores as
  not analysing the data, drawn at seed 120: none tallies or aggregates
  `accounts.csv`. Every one `cat`s the code and the two tables and then
  `head -5 accounts.csv` with `wc -l accounts.csv` — reading the file's shape
  plainly, which is what the edit instructs in place of `cut ... | sort | uniq
  -c`.
- **Panel.** `panel_agreement.py`: the first sample's `simplify-quota`/`count-quota`
  52/52 decided, no three-way splits (sonnet 52/52, opus 51/52, kimi 52/52);
  the replication 52/52; the core cells 20/20. kimi voted on every record this
  round.

### Holdout

All six reserved cases, sonnet and opus, 5 reps, from both trees: 60 runs a
side, 0 failed, CLI 2.1.310, judged by the panel. Every case passed 10 of 10 on
both sides, none undecided. No reserved case is worse under the edit.

### What the edit did

Round 118's check 2 killed the data-run on two stems and left one, `quota`'s
coverage tally, because it was keyed on the motive of a separate act and opus
bundled the tally into the command that read the code, and because its closing
sentence licensed the run as "a fact the question asked for." Re-keying the
check to command shape and narrowing the exception to a fact that is itself the
answer closed both readings: `simplify-quota`'s coverage tally went 19/40 to
0/40 and 16/40 to 0/40, while the asked-for runs — `verify-quota`'s check and
`count-quota`'s count of 62 — stayed at 12/12, and no quality bound or holdout
case moved. opus now reads `accounts.csv` plainly where it used to tally it.

The pre-mortem's likeliest failure — the point estimate moving with the
direction but not separating — did not happen: the edit killed the behaviour
rather than halving it, so the ~27% precheck rate was not the limit the
power estimate feared. The second failure it named, a fatal counter rejecting
because the command-shape sentence stopped an asked-for run, did not happen
either: `verify-quota` and `count-quota` both held at 12/12.
