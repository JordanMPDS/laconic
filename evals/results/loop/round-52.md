# Round 52: the same effect, bought from a sentence that only speaks to defects

**Registration. Nothing below the results line has been computed.** This file,
the edit and the regenerated `rules/dist/*.md` are committed in the same
commit, before any generation, following [round 38](round-38.md),
[round 47](round-47.md), [round 48](round-48.md), [round 49](round-49.md),
[round 50](round-50.md) and [round 51](round-51.md).

## The hypothesis

> Editing `rules/laconic.md:7-13` — narrowing the pre-action check so that it
> fires on a question about something broken rather than on answering in
> general — should keep the **median prose words** falling on `fail-open`,
> `silent-success` and `stale-cache`, sonnet, against this round's own
> interleaved control, and should clear the round-wide `quality_fails`
> counter that rejected [round 51](round-51.md).

Two registered bars, both fatal, and a rise is not a fall:

- **The target survives the narrowing.** At least **2 of the 3**
  `Don't edit anything.` cases fall at permutation p < 0.05, and
  `conditional`'s answering stratum falls at permutation p < 0.05. These are
  [round 51](round-51.md)'s bars, unchanged and scored by the same script.
- **The design cost is gone.** Round-wide `quality_fails` does not rise
  against this round's own interleaved control, over all 22 cases and both
  models. That is the counter round 51 lost, and the only reason it lost.

Two registered bounds, each fatal on its own whatever the target did, both
carried unchanged from round 51:

- **An answer must still name the defect.** `locates_defect` on
  `conditional`'s answering stratum.
- **The reading rate must not fall**, on any of the four cases.

## The edit

```diff
-Two checks before sending:
+One check before acting, and two before sending:

+1. Is the question about something that is broken? Diagnosing it is the
+   answer; fixing it is not. Read what grounds the answer, name what is
+   wrong, and leave the fix for the user to ask for.
-1. What is the smallest set of claims that fully answers this?
-2. Is anything here something the user did not ask for?
+2. What is the smallest set of claims that fully answers this?
+3. Is anything here something the user did not ask for?
```

**One clause differs from round 51 and nothing else does.** The frame, the
numbering and the whole second half of the check are byte-identical; only the
trigger sentence changes:

| | trigger |
|---|---|
| round 50, round 51 | *"Does answering this require changing anything? A question asks for an answer, not a work product."* |
| **round 52** | *"Is the question about something that is broken? Diagnosing it is the answer; fixing it is not."* |

Both keep the same instruction after it, word for word: *"Read what grounds
the answer, name what is wrong, and leave the fix for the user to ask for."*
That is what makes this a scope contrast rather than a rewrite. The earlier
trigger asks a question of every turn; this one asks it only of a turn about
something broken, which is the shape all four target cases have and no
`design-*` case has.

## Why this round exists

[Round 51](round-51.md) ended with a result and a named next step. The result:
the pre-action check compresses a diagnostic answer hard and reproducibly —
`conditional` 72.5 to 62.0 (p = 0.0050), `fail-open` 112.5 to 75.0,
`silent-success` 90.5 to 76.5, `stale-cache` 177.5 to 147.0, the last three all
at p < 0.001 on 40 runs a side, with both content bounds perfect. The reject
came from somewhere else: round-wide `quality_fails` rose 47 to 54, seven cells
rose, five reproduced under arbitration, and every bit of the movement sat in
the `design-*` family.

The next step, quoted from that round:

> A future candidate wanting the effect has to buy it without the `design-*`
> cost, and the obvious next question is whether the target survives a text
> that speaks only to the diagnostic shape ("a question about a defect")
> rather than to answering in general. This round cannot answer that: it never
> varied the wording.

This round varies the wording, and nothing else.

## What this round can and cannot conclude from bar 2

**Round 51's rise was not significant, and that bounds what clearing it
means.** Round-wide the rate read 47 of 133 against 54 of 135, Fisher
p = 0.4516; on the `design-*` family alone, 35 of 73 against 41 of 75,
p = 0.5108. The loop's fatal counters are strict counts over harm and carry no
significance test by design, which is why round 51 rejected — but it also
means a counter that never separated cannot be *shown* to have been repaired
by a round that clears it.

So bar 2 is registered as a gate result and not as an inference. If this round
clears `quality_fails`, what it has established is that this edit passes the
gate; the claim that the narrowing is *why* would need the design cost to have
been a real effect in the first place, and round 51 could not establish that
either. Stated here, before the numbers, so it cannot be read back in after
them.

The mechanism round 51 chased and could not confirm — a reading collapse on
the [#46] `one_turn` scope, 0 of 15 against 5 of 15 on the edit side, which the
arbitration batch then read at the control's 5 of 15 — is disclosed again
below rather than registered. A cell whose one replication called it a draw is
not a falsifier.

## The scope, and why these four cases

Unchanged from round 51, so the two rounds are directly comparable. All four
hand the model a fixture that hides a defect and ask what is wrong.

| case | grading | asks | admits an edit |
|---|---|---|---|
| `conditional` | rule-adherence | *"Should I raise the pool size?"* | **yes** |
| `fail-open` | quality | *"tell me what let those requests through"* | no |
| `silent-success` | quality | *"tell me why nothing is landing in the bucket"* | no |
| `stale-cache` | quality | *"tell me why it is still an hour"* | no |

`conditional` is the only case in the archive that admits a mutating call and
is therefore scored inside its answering stratum, per [#209]. It is
`rule-adherence`, and this round may still use it for the reason
[`volunteered-trap-116.md`](volunteered-trap-116.md) and `evals/CRITERIA.md`
record: the prohibition is on optimizing against a criterion that restates the
rules the treatment was handed, and a prose word count does not read that
criterion.

## Design

**Both sides generated simultaneously**, the control from a `master` worktree
and the edit from this branch, per round 38. A count target takes its
registered baseline from the round's own control and never from a prior
snapshot — and this round has a fresh demonstration of why. Round 50 and round
51 measured the same cell at master rules one day apart and read
`conditional`'s answering median at **83.0 (n=94) and 72.5 (n=28)**. A round
scored against yesterday's control would be scoring the calendar.

**The reps are unequal by case, and the reason is a power calculation from
round 51's own stored runs.** Round 51 sized itself from round 50's runs and
registered `conditional` at 1.00 power on a 21-word fall. Its own batch then
read that fall at **10.5 words against a 16.8-word control stdev**, which at
40 runs a side is about 0.44 — so round 51 passed its binding bar on a cell it
had roughly a coin flip's chance of passing. Sizing against the least
favourable estimate, which is [round 46](round-46.md)'s rule, means sizing
`conditional` against 10.5 and not against 21.

Bootstrapped from `round-51-control.json` directly, 400 trials per figure, at
the fall each cell actually showed in round 51 and at two thirds of it:

| case | generated per side | scored per side | fall | power | at ⅔ of it |
|---|--:|--:|--:|--:|--:|
| `conditional` | **160** | ~112 | 10.5 | **0.82** | 0.50 |
| `fail-open` | 60 | 60 | 37.5 | **0.98** | 0.69 |
| `silent-success` | 60 | 60 | 14.0 | **0.78** | 0.56 |
| `stale-cache` | 60 | 60 | 30.5 | **0.99** | 0.77 |

`conditional`'s scored stratum is about 70% of its runs (28 of 40 in round
51's control, 33 of 40 in its edit), so 160 generated buys about 112 scored.
Against the 2-of-3 bar the three generalisation cells give about 0.99, and the
round's registered power is that times `conditional`'s 0.82, or **about 0.81**.
Round 50 was bought at an assumed 0.84 and had 0.56; round 51 was bought at an
assumed 1.00 and had about 0.44.

```sh
# edit side, from this branch, one shard per case
python3 evals/bench/run.py --arms laconic --models sonnet --reps <reps> \
  --cases <case> --concurrency 8 \
  --snapshot evals/snapshots/loop/round-52-edit-<case>.json

# control side, from a master worktree, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps <reps> \
  --cases <case> --concurrency 8 \
  --snapshot <abs path>/evals/snapshots/loop/round-52-control-<case>.json
```

Eight processes, so `--concurrency 8` on every one of them, per [#120].

**No judging is bought in step 1.** The target and both bounds are
deterministic, so it costs 680 generations and nothing else. Step 2 buys the
round-wide arm and its judgments, and only for an edit that survives step 1.

## Scoring

```sh
python3 evals/pilot/score_compression.py \
  evals/snapshots/loop/round-52-edit.json \
  --against evals/snapshots/loop/round-52-control.json
```

The script is round 51's, unchanged, and so are its bars — that is the point
of registering the same scope. Step 2 is `report.py` over the round-wide arm
against this round's own control, at `--judge-all` because the hypothesis
names `conditional`, whose verdicts the default grading skips.

## What this round cannot establish

- **Four cases, one model, one shape of question.** Nothing here speaks to
  design questions, walkthroughs or ordered procedures directly; the
  round-wide counters in step 2 are what would catch a loss on those, and they
  are the same 5-rep draws every round's are.
- **Why bar 2 lands where it lands**, per the section above.
- **Not an accept on its own.** Step 8's replication and step 9's holdout are
  conditional on both steps passing.
- **It does not settle [#116].** The issue's endpoint is whether volunteered
  work displaces the answer, and that is a null at 0.56 power from round 50.
  This round measures the other thing the same family of sentences does, on a
  trigger narrowed to the shape where the effect was found.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#209]: https://github.com/JordanMPDS/laconic/issues/209

---

## Results

_Pending. This round is registered; nothing below has been computed._
