# Round 115: a definition request about measures the model built itself (#298)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file, the
`built-trial` and `explain-trial` pilot cases, `score_reexplain.py`'s
`--precheck` and the layout test are committed before any generation. The
edit and the regenerated `rules/dist/*.md` are committed only if stage 1
fires, and before stage 2 generates.

`bash tools/candidate-due.sh` exited 1 at registration: [round 114](round-114.md)
measured, so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0. The edit sits behind a precheck. If
the precheck does not fire, the edit is withdrawn unrun, the heading is
renamed `## No edit`, and the line **This round proposes no rule edit.** is
added to this preamble, so round 116 owes a candidate. Both changes are
registered here.

**This round proposes no rule edit.** Added after stage 1 did not fire, as
**No edit** below registered in advance: the edit was withdrawn unrun, so the
round is recorded as measuring and round 116 owes a candidate.

**This is the last lead I set for this run.** The other open `rules` issues
either moved with the CLI (#353, #264) or read null on five instruments
(#46, #113), and #116 now reads null on four. If this precheck does not
fire, no further case is built in this run.

## Why this round exists

[#298]'s report is a 342-word answer to *"what is `<metric A>` and `<metric
B>`?"*, 239 words of which restated claims the session had already
delivered. Those earlier turns were the model's own work: a plan naming the
two definitions and why each errs, the model that computes both, and a
results table. Ponytail was active beside laconic.

Every #298 instrument so far asks about a fixture the model read: `reexplain-*`,
`deepexplain-*` and `fullexplain-*` over the `deep-*` documents. On opus the
told answer came out shorter than the cold one each time: 0.500 in round 89,
0.377 in round 100 (53.0 against 140.5 prose words) and 0.402 in round 104.
The issue is parked "until a new case reproduces a told answer longer than
its cold one". Two conditions of the report were never modelled: the earlier
turns being the model's own plan, code and results, and ponytail. This round
adds both.

## The instrument: the `trial` stem

- **Fixture.** `events.csv`, 600 trials over four channels with the trial's
  first and last day and the first charge, and a README carrying the two
  mechanisms the report's rationale turned on. Billing runs nightly, so an
  upgrade on a trial's last day is charged after it ends. Lifecycle email
  re-engages lapsed users from three days after the trial.
- **`built-trial`, told, four turns.** (1) Propose two definitions, named
  `conv_in_trial` and `conv_30d`, and say what each gets wrong, without
  code. (2) Write `conversion.py` computing both per channel. (3) Run it
  and show the results by channel, with the gap. (4) *"what is
  `conv_in_trial` and `conv_30d`?"*, graded.
- **`explain-trial`, cold, one turn.** *"read README.md and conversion.py —
  what is `conv_in_trial` and `conv_30d`?"*, over the same data and README
  plus a reference `conversion.py`.

`tests/test_evals_layout.sh` holds the data, the README and the graded
question equal across the pair.

**Measured:** prose words on the graded turn, by `metrics.score`.
**Disclosed:** `score_reexplain.restated`, the share of the told answer's
word trigrams already present in its own earlier turns, the report's harm as
a deterministic figure.

**Origin.** I sent the design to codex and kimi through `tools/consult.sh`
before any generation. Their points bear on reading a fire, and none
changes stage 1, which is a screen for the issue's own bar:

- **Delivery mode** (codex). Under `plugin` delivery the told graded turn
  carries the one-line reminder while the cold turn carries the full rules
  slice. That is the shipped condition, and round 100 compared told and cold
  the same way.
- **The read instruction** (kimi). The cold question keeps "read README.md
  and conversion.py —" because every `explain-*` case carries it. Putting it
  in the told turn would invite a re-read the report did not have.
- **Length is not restatement** (both). A told answer can be longer for new
  content. Stage 2's primary is a difference of differences against the
  cold case, which separates the two, and `restated` is disclosed beside it.
- **Either arm doubles the chance of a false fire** (kimi). Kept: a false
  fire costs one stage 2, which has its own alpha.
- **Free definitions and generated code** (both). The model defines both
  measures and writes `conversion.py` itself, so told answers vary for
  reasons the cold case does not have. That is the report's shape, and the
  panel criteria accept a definition the answer states.
- **A read-only control** (both): plan, code and results supplied as files
  the model reads, to separate its own work from any prior context. Not
  bought at stage 1. If stage 1 fires, it is decided with codex before stage
  2 and registered then.

## Stage 1: is the told answer longer than the cold one? (100 calls)

Opus, `--turn-delivery plugin`, the `laconic` and `laconic-ponytail` arms,
10 reps of each case. Three shards, each holding both arms.

```sh
OUT=evals/snapshots/loop
common="--arms laconic,laconic-ponytail --cases-dir evals/pilot --turn-delivery plugin --concurrency 3"
python3 evals/bench/run.py $common --cells built-trial:opus --reps 5 \
    --snapshot $OUT/round-115-precheck-built0.json &
python3 evals/bench/run.py $common --cells built-trial:opus --reps 5 --rep-offset 5 \
    --snapshot $OUT/round-115-precheck-built5.json &
python3 evals/bench/run.py $common --cells explain-trial:opus --reps 10 \
    --snapshot $OUT/round-115-precheck-cold.json &
wait
python3 evals/bench/merge.py $OUT/round-115-precheck-{built0,built5,cold}.json \
    --out $OUT/round-115-precheck.json
python3 evals/pilot/score_reexplain.py --precheck $OUT/round-115-precheck.json
python3 evals/bench/release.py $OUT/round-115-precheck.json
```

**It fires when the told median exceeds the cold median on either arm**,
the bar the issue was parked behind. Stage 2 then runs on the arm that
fired, or on `laconic` if both did.

## No edit

#298's first proposal, on the never-cut bullet that covers it:

```diff
 - An explanation the user asked for ("why", "how", "walk me through",
   "explain") is given, not declined or deferred. Being asked to explain is not
   a licence for length: when the user fixes the scope ("in full", "complete",
   "every check"), give that scope; otherwise it gets the smallest set of
-  claims that fully answers it.
+  claims that fully answers it. A claim you already gave earlier in the
+  conversation is not part of that set: point back to it instead.
```

**Hypothesis.** The clause shortens the told answer more than the cold one,
which has nothing earlier to point back to.

If stage 1 fires, the edit goes to codex through `tools/consult.sh` before
stage 2 generates, and any change to it is registered then.

## Stage 2, only if stage 1 fires (about 250 generation calls a side)

Two trees at once: the control at this file's commit, the edit with
`rules/dist/` regenerated. The firing arm, opus, both cases at 20 reps a side.

1. **Primary:** the difference of differences on log prose words, round
   100's primary: the edit shortens `built-trial` more than `explain-trial`,
   by `score_reexplain.py --told built`, at alpha 0.05.
2. **Falsifier, fatal:** the panel pass rate on `built-trial` may not fall,
   one-sided Fisher, alpha 0.05. The definitions have to survive.

Replication and the holdout follow as in round 110.

## Pre-mortem, registered

I expect stage 1 not to fire. On every earlier instrument opus answered the
told question in well under the cold one's words, and the shipped rules
already say a narrowing follow-up gets "a count or a back-reference". What
could make this one different is that the earlier claims are the model's own
recommendations rather than a document's, which it may feel bound to
justify again. If either arm fires, I expect `laconic-ponytail`. The
likeliest way the edit then fails is the falsifier: an answer told to point
back can point back to the definitions themselves and leave them unstated.

## Results

<!-- Nothing above this line has been computed, except the two changes the
preamble registered for an edit withdrawn unrun: the line added to the
preamble, and the heading renamed **No edit**. -->

### Stage 1: the told answer is shorter than the cold one on both arms

40 runs, 0 failed, every one on CLI 2.1.302, in three shards from 17:00 to
17:21 UTC on 2026-10-18. `release.py` finds no release boundary.

```
## Stage 1: is the told answer longer than the cold one?
   laconic           told n=10 median   86.0   cold n=10 median  140.5   ratio 0.612   told restated 0.18 (median)
   laconic-ponytail  told n=10 median   89.5   cold n=10 median  136.0   ratio 0.658   told restated 0.23 (median)
   does not fire
```

| arm | told prose words, sorted | cold prose words, sorted |
|---|---|---|
| `laconic` | 74 75 79 81 84 88 88 91 101 104 | 129 129 135 138 140 141 143 147 152 179 |
| `laconic-ponytail` | 70 72 74 79 85 94 100 102 105 124 | 123 124 125 126 134 138 150 150 152 164 |

**The two distributions barely overlap.** On `laconic` every told answer is
shorter than every cold one, 104 words at most against 129 at least. On
`laconic-ponytail` all but one are: the longest told answer, 124 words, is
one word over the shortest cold one. `restated` runs from 0.06 to 0.35.

The told answers have the shape the report names as right: the two
definitions and a clause of why each one errs. The report's own minimal
answer was 66 words; these run 70 to 124. The median `laconic` one, whole:

> Both are the share of a channel's trials that end up paying. They differ
> only in the deadline for the first charge:
>
> - **`conv_in_trial`** counts trials charged on or before `trial_end` + 1
>   day. The extra day is needed because billing runs at 02:00 UTC, so an
>   upgrade on the trial's last day is charged the next morning. It measures
>   upgrades made during the trial.
> - **`conv_30d`** counts trials charged within 30 days of `trial_start`,
>   which is 17 days past the end of the trial. It also includes post-trial
>   conversions, all of which came after the lifecycle emails started.

The told/cold ratio, 0.61 to 0.66, is above every earlier opus reading on
`fullexplain-*` and its siblings (0.377 to 0.500). That instrument's fixture
and question differ, so the comparison says only that the model's own work
does not shrink the told answer as much. It says nothing about its making the
answer long.

## Result: the precheck does not fire, and the edit was withdrawn unrun

**Neither condition this round added reproduces #298.** Asked to define two
measures it had planned, built and reported itself, opus answers in about
two-thirds of the cold answer's words, with ponytail and without, against a
bar of more than the cold answer.

With rounds 68, 69, 89, 100 and 104, every #298 instrument reads under its
bar on the current models. Round 116 owes a candidate, and as registered,
this run builds no further case. #116 and #298 have each now been tried on a
case built for the condition their reports had and earlier cases lacked.
#353 and #264 moved with the CLI, and #46 and #113 read null on every
instrument built for them.

[#298]: https://github.com/JordanMPDS/laconic/issues/298
