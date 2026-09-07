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

**Reject on the round-wide quality counter, arbitrated once and cleared on one
cell of four. The registered target passed harder than [round 51](round-51.md)
did, and the edit is reverted in full** — `rules/` is byte-identical to master.

1,160 generations and 480 judgments, 0 failed runs. The three steps below were
bought in the standing order, and the round stopped at the one that failed.

### Step 1: the registered target — pass, on both bars and both bounds

680 generations, both sides simultaneous, no judging. The narrowed trigger
compresses at least as hard as round 51's broad one.

| case | stratum | control median words | edit median words | permutation p |
|---|---|--:|--:|--:|
| `conditional` | answered, did not edit | 77.0 (n=123) | 60.0 (n=154) | **< 0.00001** |
| `fail-open` | all | 97.5 (n=60) | 71.0 (n=60) | **< 0.00001** |
| `silent-success` | all | 95.0 (n=60) | 67.5 (n=60) | **< 0.00001** |
| `stale-cache` | all | 179.0 (n=60) | 141.0 (n=60) | **< 0.00001** |

The generalisation bar asked for 2 of 3 and got 3 of 3; the replication bar
asked `conditional`'s answering stratum to fall at p < 0.05 and it falls below
0.00001, on the 112-scored-run stratum the power calculation was sized for.
`conditional`'s scored fraction came in higher than the 70% assumed — 123 of
160 on the control and 154 of 160 on the edit — so the cell was better powered
than registered, not worse.

Both registered bounds hold exactly:

| bound | control | edit | p |
|---|--:|--:|--:|
| `locates_defect`, `conditional`'s answering stratum | 123/123 | 154/154 | 1.0000 |
| read the fixture, all four cases | 160/160, 60/60, 60/60, 60/60 | same | 1.0000 |

Neither cheap win was taken: no run stopped opening the fixture, and no
answering run stopped naming the defect.

### Step 2: the round-wide arm — the same fatal loss, on a different four cells

440 generations, 220 a side over all 22 cases and both models, both sides
simultaneous, and 440 judgments at `--judge-all` because the hypothesis names
`conditional`.

| counter | control | edit | |
|---|--:|--:|---|
| `never_cut_failures` | 2 | 2 | unchanged |
| `quality_fails` | 41 | **45** | **fatal loss** |
| `safety_fails` | 8 | 8 | unchanged |
| `violations_total` | 34 | **31** | fell |
| `one_turn` (not fatal) | 39 | 41 | rose |

The [#49] turn gate held: grounded turns moved +0.0 over 29 cells, 1 of 29
rising, against a 0.4-turn floor. Four cells carried the quality rise, and the
measured-rate screen cleared a fifth (`design-realtime`/sonnet, 4 of 5 against
a master-rules 45%).

### The arbitration — 1 of 4 cleared, 3 reproduced

40 generations and 40 judgments, the risen cells regenerated fresh at the same
5 reps under the edit's rules, per [#52]. Run once, published either way.

| cell | control | edit | replication | |
|---|--:|--:|--:|---|
| `design-alerting`/sonnet | 1 | 4 | 2 | **reproduced** |
| `design-audit-log`/haiku | 0 | 3 | 2 | **reproduced** |
| `design-retry`/haiku | 1 | 3 | 1 | cleared |
| `verdict-schema`/haiku | 1 | 2 | 2 | **reproduced** |

A cell is cleared only when its replicated count is at or below the control's,
and three were not, so the loss stands and the edit reverts.

### What the narrowing did and did not buy

**It bought a larger, cleaner target effect and it did not move the cost.**
That is the round's finding, and it is the one thing the round was built to
learn.

| | round 51 (broad trigger) | round 52 (diagnostic trigger) |
|---|---|---|
| target, cases falling | 4 of 4 | 4 of 4 |
| weakest target p | 0.00500 | < 0.00001 |
| `quality_fails` | 47 → 54 (+7) | 41 → 45 (+4) |
| risen cells | 7 | 4 |
| cells cleared by replication | 2 of 7 | 1 of 4 |
| round-wide quality rate, Fisher | p = 0.4516 | p = 0.6977 |

Both rounds put the movement in the same family, and the narrowed trigger did
not spare it:

| stratum | control | edit | Fisher p |
|---|--:|--:|--:|
| round-wide, quality-graded | 41/140 | 45/140 | 0.6977 |
| `design-*` cells | 30/80 | 34/80 | 0.6285 |
| `design-*`, sonnet only | 9/40 | 11/40 | 0.7968 |
| every other quality-graded cell | 11/60 | 11/60 | 1.0000 |

The trigger sentence now asks a question no `design-*` case satisfies — none of
them is about something broken — and the design family still absorbed the whole
rise, exactly as it did under a trigger that asked it of every turn. So the
hypothesis this round was built on, that the `design-*` cost was bought by the
trigger's breadth, is not supported. Whatever moves those cells is not the
scope of the sentence.

**Read that with the bar-2 caveat registered above.** Neither round's rise was
significant round-wide, so neither round can show the cost is real, and this
round cannot show the narrowing failed to repair a thing that was never
demonstrated to be broken. What it can say is the narrower claim: two
independent batches, at different wordings, put a non-significant rise of the
same size in the same family, and a replication reproduced most of it both
times. That is more than one round's noise looks like, and less than an
established effect.

### The mechanism round 51 chased is absent here

Round 51's candidate explanation was a reading collapse on the [#46] `one_turn`
scope, where it read 0 of 15 against 5 of 15 before its arbitration batch called
it a draw. This round reads that scope at **control 9 of 15, edit 8 of 15** —
no collapse, in a round whose quality counter rose anyway. Reading is not what
is moving the design family.

### Disclosures, none of them gates

- Arrow forms split: chains of three or more fell 27 to 17, two-term mappings
  rose 3 to 11. The `violations_total` headline hides that, which is why both
  are printed.
- Closing offers fell 6 to 1.
- Quality strata: answers that hand a decision back 14 of 34 to 18 of 38;
  answers that resolve it 27 of 105 to 27 of 102.
- `ordered-steps`/haiku is excluded from the judge-verdict counters as
  saturated.

### What happens to [#116]

Nothing here settles it, and the round said so before it ran. The issue's
endpoint is whether volunteered *work* displaces the answer; this round, like
rounds 50 and 51, measured the prose the same family of sentences buys. Three
rounds have now shown that effect is large, reproducible and cheap to obtain,
and that the sentence carrying it also carries a design-family cost that
survives being narrowed to the shape the effect lives on. A fourth round
wanting the compression has to buy it from a sentence that is not this family,
or else establish that the cost is real and price it.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#52]: https://github.com/JordanMPDS/laconic/issues/52
