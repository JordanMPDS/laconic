---
name: laconic-loop
description: Use when improving rules/laconic.md against the benchmark — running a loop round, reviewing what failed, proposing a rule edit, or deciding whether an edit earned its keep. Project-local maintainer procedure, not shipped in the plugin.
---

# The rules improvement loop

One round: benchmark, review the failures, propose one rule edit, confirm it,
and either open a PR or throw it away. **The loop proposes. A human merges.**

Design and the reasoning behind every threshold:
`docs/superpowers/specs/2026-08-01-rules-loop-design.md`.

## Before you start

Set `N` to the next round number and `PREV` to the last round's snapshot. The
current baseline is round 21 — all five arms at n=5 over all 22 cases, at
`rules_cksum` 1830906901:

```bash
N=22
PREV=evals/snapshots/loop/round-21.json
PREV_J=evals/snapshots/loop/round-21-judgments.json
```

**From round 22 the baseline is `round-21.json`, and its laconic arm is n=5
where `-v4`'s was n=10.** That is a real loss of power and it is the price of
the other three things round 21 has. Read it before running a round:

- **Every fatal counter is now a five-rep draw.** The baseline reads
  `never_cut_failures` 0, `quality_fails` 56, `safety_fails` 8 and
  `violations_total` 66. A cell that fails at a low rate is more often 0 in the
  baseline at n=5 than at n=10, so a single flip reaching the gate as
  "0 to 1" is correspondingly more likely. `cell-rates.json` is the mitigation
  and it matters more than it did: screen every risen cell against a measured
  rate where one exists, and prefer measuring a new cell over arbitrating the
  same one twice.
- **Generate the round's laconic arm at `--reps 5`,** matching the baseline. An
  n=10 round against an n=5 baseline gives the round twice the opportunity to
  fail a cell and is not the comparison the fatal counters describe.
- **What round 21 buys.** It carries a `cases_cksum` (2389944869), which `-v4`
  predates entirely, so the [#69] guard can verify it. It includes the
  `concise-style` arm, so no round has to seed it. And its judgments were
  produced under the criteria in `evals/cases/` today, at `criteria_cksum`
  997100469.
- **To restore n=10,** generate 220 more laconic runs into the baseline and
  re-judge that arm, then set `--reps 10` back:

  ```bash
  python3 evals/bench/run.py --arms laconic --reps 10 --snapshot "$PREV"
  python3 evals/bench/judge.py --results "$PREV" --jobs 6 --out "$PREV_J"
  ```

  `run.py` generates only the rep keys the snapshot lacks, so this adds reps 5
  to 9 and costs 220 calls rather than 440. **It does not rewrite
  `metadata.reps`,** which `new_snapshot` sets once at creation: the file would
  hold ten reps of laconic while its metadata still says 5. Correct the field
  by hand if you do this, or the next reader takes the arm for n=5.

**Rounds 16 to 21 used `-v4`, which is `-v3` plus `design-cache`,
`design-realtime` and `design-upload`.** Every cell in the file is at
`rules_cksum` 1830906901, and `-v4` is identical to `-v3` on every fatal counter
once the three new cases are removed.

The three exist because the five older design cases cannot tell a derived answer
from a recalled one: on all five the answer a model gives without opening a file
is already the fixture's answer, so `baseline`, `laconic`, `terse-control` and
`word-compression` all score alike. That is why the round 15 edit passed every
dev-set gate and was killed by the holdout. **On the three new cases, no
response that failed to resolve the fixture has ever passed** — see
[`design-discrimination.md`](../../../evals/results/loop/design-discrimination.md)
and [#88].

**`-v3` remains the baseline for the scoped `output_tokens` target.** The five
older design cases carry it, and they still do: it is a length measurement and
does not depend on the property they lack — see
[`token-scope.md`](../../../evals/results/loop/token-scope.md). What they may no
longer be read as is evidence about design-answer quality.

**A scoped `output_tokens` hypothesis must now name all five design cases.**
Naming three leaves four voting cells, which cannot reach alpha, so the gate
keeps the short cells and tells you to widen the scope:

```
--target-cases design-alerting,design-audit-log,design-search,design-rate-limit,design-retry
```

**From round 11 the baseline was `-v2`, which is `round-01-n10.json` plus the
three `verdict-*` cells** ([#60]'s instrument). Every original cell is
byte-identical and the new cells were generated under the same
`rules_cksum` 1830906901, so `never_cut_failures`, `quality_fails` and
`safety_fails` are unchanged at 2, 41 and 6. Only `violations_total` moves,
78 to 86, because there are three more cases producing text.

Rounds 01 to 10 were scored against the 14-case `round-01-n10.json`, rounds 11
to 14 against `-v2`, and each stays that way. **Do not re-score an old round
against a later baseline**: its snapshot has no runs for the added cases, so
every one of those cells reads as missing rather than as unchanged. That is not
a formality — re-scoring rounds 07 to 14 under the `-v3` scope turned round 10's
accept into a rejection, purely because the cases it needed did not exist when
it ran.

Generate the round's laconic arm at the same reps as the baseline
(`--reps 5`), and carry arms from `$PREV`, not from
`evals/snapshots/results.json` — the old committed snapshot has no control runs
for the three `design-*` cases, so carrying from it silently drops them from
preference and from the reduction tables.

**Check the baseline's judgments were produced under the criteria in
`evals/cases/` today.** A criterion that has been corrected since re-grades the
baseline, and scoring against the stale file reports the difference as something
the edit did. Two case criteria have been corrected against the real software
they describe, and both moved several verdicts. Before the #45 regeneration the
baseline was `evals/snapshots/results.json` with
`evals/snapshots/loop/round-01-judgments-v2.json` (identical in every verdict
to `evals/snapshots/judgments.json`); `round-01-judgments.json` is the
superseded grading. See
[`LEDGER.md`](../../../evals/results/loop/LEDGER.md) for what moved.

**If you correct a criterion, re-judge every round you will compare, not just
the baseline.** Re-grading one side and carrying the other publishes a delta
between two instruments. That mistake shipped once, in the first `safety_fails`
re-score, and took 20 further judge calls to undo.

**While a pass is running, the working tree is part of the instrument.** The
harnesses read `prompt.md`, `expect.json` and the fixtures live, and a round
takes hours, so editing a case or switching branches mid-pass produces one round
built from two different case sets. Since [#69] a snapshot records a
`cases_cksum` over exactly the cases it covers, and `run.py`, `judge.py` and
`prefer.py` all refuse to continue when the tree no longer matches it — with
`--allow-case-change` as the deliberate override, which stamps the fact into the
metadata.

The guard does not cover the harness source or `rules/laconic.md`. `rules_cksum`
covers the rules, and `run.py` resolves the system prompt once at startup, so an
in-flight generation keeps the text it began with. **A `git rebase` mid-round
still moved the tree under a live round on 2026-08-12** and nothing was
contaminated only because no new shard started inside the window. Do not edit
the harnesses or switch branches while a pass is running.

[#69]: https://github.com/JordanMPDS/laconic/issues/69

## Steps 1-3: measure the round you have (~345 calls at n=5)

```bash
python3 evals/bench/run.py --arms laconic --reps 5 \
  --carry-arms-from "$PREV" \
  --snapshot "evals/snapshots/loop/round-$N.json"
python3 evals/bench/judge.py --results "evals/snapshots/loop/round-$N.json" \
  --carry-judgments-from "$PREV_J" --jobs 6 \
  --out "evals/snapshots/loop/round-$N-judgments.json"
python3 evals/bench/prefer.py --results "evals/snapshots/loop/round-$N.json" \
  --control baseline --jobs 6 --out "evals/snapshots/loop/round-$N-preferences.json"
```

**Carrying the controls was wrong, and a scoped round must not do it.** The
rule this skill carried until 2026-08-23 was "the controls are carried, not
regenerated: no control arm carries rules in its system prompt, so they cannot
have moved." The premise is false. `terse-control` carries no rules either, and
its one-turn rate went **4 of 40 to 11 of 40** between 2026-08-11 and
2026-08-22 with nothing changed but the calendar and the CLI
([`interleaved-batch.md`](../../../evals/results/loop/interleaved-batch.md)).

A control arm can move a great deal. What it cannot do is move *because of the
edit* — a different claim, and conflating the two is what produced every arm
comparison since round 16 being against runs from another era. Round 21 reads
laconic 14/40 against a carried baseline 3/40 at p = 0.0052, and that number is
not usable: the control arm is 11 days and 12 CLI releases older than the
treatment.

**Generate every arm the round will compare, in one interleaved pass.** For a
scoped round this is cheap, and the expense that once justified carrying was
only ever 22 cases across two models. Three cases on sonnet at n=5 is 15 runs an
arm, so five arms is 75 generations:

```bash
python3 evals/bench/run.py --arms baseline,terse-control,word-compression,concise-style,laconic \
  --models sonnet --reps 5 --cases 'design-*' \
  --snapshot "evals/snapshots/loop/round-$N.json"
```

`run.py` loops arms innermost, so a single invocation already interleaves them.
Two rules revisions cannot share one invocation — `rules_cksum` is resolved once
at startup — so when the round compares master against an edit, run each side
from its own tree and alternate one rep at a time, which is what
`interleaved-batch.md` records and what resolved a contrast at 40 runs a side
that the archive could not resolve at any n.

**Carrying is still correct for the round-wide fatal counters**, which compare
the laconic arm of two rounds and read no control at all. What it is not correct
for is any statement of the form "laconic against baseline".

**`concise-style` belongs in every interleaved batch.** It is the native Claude
Code `Concise` output style, delivered through `--settings` rather than an
appended system prompt, and it is the one control that answers "does the plugin
beat what the CLI already ships". It carries no rules, so an edit cannot move
it, and it costs 15 runs in a scoped round. Round 21 measured it at n=5: on
compression it wins, -55% on sonnet against laconic's -32%, indistinguishable
on quality, and 3 never-cut failures against laconic's 0. See
[`docs/benchmark.md`](../../../docs/benchmark.md#the-concise-style-arm). Those
figures are from carried arms and inherit the problem above; the first matched
measurement is the one round 23 will produce.

If a future baseline is ever built from a snapshot predating an arm, `run.py`
prints a `no runs to carry` warning naming it and records it as `missing_arms`
in the metadata, but it does not stop the round. That warning is the signal to
seed the arm into the carry source before continuing:

```bash
python3 evals/bench/run.py --arms <arm> --reps 5 --snapshot "$PREV"
python3 evals/bench/judge.py --results "$PREV" --jobs 6 --out "$PREV_J"
```

`run.py` probes the style against the live CLI before generating anything and
exits if it is not reaching the model, because an output style the CLI does not
recognise is dropped without an error — that arm would otherwise run as a
second copy of `baseline` and the round would publish "the native style changes
nothing".

**When a round does carry control runs, carry their verdicts too.** Round 14
carried the control *runs* and then re-graded them anyway: 510 of its 850 judge
calls, and $25.05 of its $41.37 judging bill, spent re-grading text the baseline
had already graded and no fatal gate reads. Worse than wasted — the judge
disagrees with itself on 5 to 10% of identical text, so each round re-rolled its
own comparison rows.

This is not in tension with regenerating the controls above. Re-grading text
that has *already been graded* is waste; generating *fresh* control text in the
round's own batch is what makes an arm comparison mean anything. A round that
regenerates its controls must judge them, because there is nothing to carry.

`--carry-judgments-from` prints a warning when the source predates
`criteria_cksum`, which is every judgments file committed before 2026-08-11.
That warning is the rule below restated by the tool, and it is not decoration:
**if any case criterion has changed since the source was written, do not
carry — re-judge.**

## Step 4: review, no calls

```bash
python3 evals/bench/review.py "evals/snapshots/loop/round-$N.json" \
  --judgments "evals/snapshots/loop/round-$N-judgments.json" \
  --preferences "evals/snapshots/loop/round-$N-preferences.json"
```

Read the inventory top down. The classes are ranked, and the ranking is the
advice:

- **unruled** — the benchmark checks something `rules/laconic.md` never
  mentions. This points at writing a rule, not editing one, and it outranks
  everything else.
- **never-cut** — a safety item was dropped. Fix before anything about length.
- **quality** — the answer was wrong.
- **readability** — a rule exists and was disobeyed.
- **preference** — a judge preferred the other arm. Weakest signal in the file;
  see the ceiling below.

An entry marked _(rule-adherence case: not an optimization target)_ may not be
optimized against. Tuning the rules against a case that grades adherence to
those rules is circular.

## Step 5: propose exactly one edit

Write the hypothesis **before** running the confirming round, in this form:

> Editing `<rule line>` should move `<metric>` on `<cases>` in `<direction>`.

The `<cases>` in that sentence are what you pass to `--target-cases` in step 7.
Name them here, before the round runs, or the scope is chosen after the numbers
are in and scores whatever moved.

Then edit `rules/laconic.md`. One edit per round. A hypothesis written
afterwards is indistinguishable from a story about whatever happened to move,
and the ledger timestamps it against the round it predicted.

**Where a rule lives outranks what it says about where it lives.** When a new
licence bleeds into content it should not reach, move it rather than write
its limits into it. Rounds 07, 08 and 09 put a design-question licence in the
"Never cut" list and tried to bound it in prose — round 08 and 09 went as far
as "this bullet outranks the approach license above" — and `ordered-steps`/haiku
read 6, 3 and 5 against a baseline 2. Round 10 moved the same licence into
`level: full`, wrote no precedence sentence at all, and the cell returned to 2
while the token effect grew. The section headers already encode the hierarchy
("Never cut (every level, including ultra)"); a rule placed under one inherits
its limits without being told them.

**A rejected round reverts the whole edit, including the parts that worked.**
Carrying a proven component forward into the next round's edit is normal and
counts as one edit — rounds 08 and 09 carried round 07's bound, round 11
carries round 10's relocation. Re-state the carried part in the new
hypothesis so the ledger row is readable on its own.

Regenerate the pre-sliced copies, which the test suite checks:

```bash
bash tools/build-rules.sh
```

## Steps 6-7: confirm and compare (~345 calls)

Repeat steps 1-3 with `N` incremented, then:

```bash
python3 evals/bench/report.py \
  --results "evals/snapshots/loop/round-$M.json" \
  --judgments "evals/snapshots/loop/round-$M-judgments.json" \
  --against "evals/snapshots/loop/round-$N.json" \
  --against-judgments "evals/snapshots/loop/round-$N-judgments.json" \
  --preferences "evals/snapshots/loop/round-$M-preferences.json" \
  --target output_tokens
```

Exit 0 accepts, exit 1 rejects, and every reason prints.

**A hypothesis that named cases is scored on those cases.** Add
`--target-cases walkthrough,ordered-steps` to a count target, and the target is
computed over those cells while everything else stays round-wide. Without it a
count target is the whole-round sum, which is what round 03 was scored by: it
moved its two named cases 21 arrows to 5 and reached the gate as 26 to 20,
p = 0.231. The scoped line prints the round-wide number beside the scoped one,
and the cases must be named in step 5, not picked once the round is in.

`--target-cases` also scopes `output_tokens`, but only when the named cases
yield at least 6 case/model cells: the sign test is two-sided exact, so a sweep
of 4 cells is p = 0.125 and can never reach alpha, and smaller scopes are
refused rather than left silently unreachable. The scoped noise floor is the
median per-cell stdev over **all** the scoped cells of the baseline snapshot —
the same cells whose medians produce the shift it gates ([#51]: rounds 07 and
08 measured the same edit at 711 then 504 around a sonnet-only 575 floor). A
scoped cell with no baseline stdev leaves the floor unbuildable and the scope
is refused.

**`--target-models sonnet` narrows a count target to one model, and the round-wide
fatal counters stay over both.** Round 17 used it. Register the model in step 5
with the cases, for the same reason: a scope chosen once the numbers are in
scores whatever moved. Narrowing to a model you have not measured is how round
16 read "5 → 2, established on sonnet" off a single n = 10 baseline draw; the
same 2 of 30 against the measured 22 of 120 is p = 0.165 ([#96]). Where every
cell in the scope has a rate in `cell-rates.json`, `report.py` now scores the
count against the pooled rate rather than the draw, and prints which cells the
scope actually reports on.

[#96]: https://github.com/JordanMPDS/laconic/issues/96

**Rejects on its own:** a never-cut verdict lost, a quality verdict lost, a
safety verdict lost, readability violations up — all four round-wide, whatever
the scoped target did. An edit that fixes two cases and breaks a third still
rejects.

**A cell with a measured failure rate is screened against it first.** The
fatal counters compare a round's per-cell count against the baseline's, and the
baseline is one draw — n = 5 since round 21, where it was n = 10 through round
21's predecessor. For a cell that fails at 8% under master rules an n = 10 draw
is 0 about 43% of the time and an n = 5 draw about 66% of the time, so "0 to 1"
was the gate reporting a coin flip as a regression, and at n = 5 it is a
likelier coin flip. `evals/snapshots/loop/cell-rates.json` holds rates
measured under master rules at n ≥ 30; where one exists, a risen cell is a loss
only if its count is higher than that rate predicts at the same alpha. Every
screened cell is named in the reason line, and the metrics the screen can speak
for at all are printed whether or not anything rose. A cell with no measured
rate is scored exactly as before, and `--no-cell-rates` scores the way rounds
01 to 11 were scored.

Measuring a new cell costs about 40 calls and is worth it for any cell that has
rejected a round on a single flip. `destructive`/haiku runs at 5 of 65 and
`conditional`/sonnet at 8 of 60.

**A fatal count loss can be arbitrated by one replication ([#52], [#56]).**
The loss prints its per-cell composition. To arbitrate it, regenerate the
risen cells fresh at the same reps under the round's rules, judge them, and
re-run the comparison with `--arbitration-results` and
`--arbitration-judgments`. A cell whose replicated count stays at or below
the baseline's is cleared as sampling; one that reproduces stays fatal. A
cell the replication never covered cannot be cleared — zero failures from
zero checks is not evidence. Record the arbitration in the round doc either
way.

**Size of rise is not evidence; reproduction is.** [#52] originally refused
arbitration above +1, on the theory that concentration signals a real
regression. Round 09 retired it: running round 08's byte-identical rules text
put `ordered-steps`/haiku at +3 where round 08 had +1, two draws from one wide
cell at Fisher p = 0.65, landing on opposite sides of the cutoff. Removing it
changed no verdict in the loop's history — round 07's `ordered-steps`/haiku +4
still rejects, because it replicated at 3 and 5 against a baseline 2.

Arbitration is a replication, not a retry. Run it once, on the cells the
comparison named, and publish the result whichever way it goes. Regenerating
until a round clears is the failure mode this whole gate exists to prevent.

[#51]: https://github.com/JordanMPDS/laconic/issues/51
[#52]: https://github.com/JordanMPDS/laconic/issues/52
[#56]: https://github.com/JordanMPDS/laconic/issues/56

`safety_fails` counts blind-judge failures on the safety-graded cases, and it
is a valid `--target` too. It is not redundant with `never_cut_failures`: that
one is a substring check, so a response that names the thing and then calls it
harmless passes it. `destructive/haiku` did exactly that in rounds 01, 03 and
04, and until this counter existed no gate saw it. **That cell is no longer
marked saturated**: [#94] retired the marking on 2026-08-13 for a measured 53 of
55, re-scored across 15 stored rounds with 0 verdicts moved, so a *fall* on it
registers for the first time since [#45]. `ordered-steps`/haiku is the one cell
still carrying `saturated_models`, and it carries it for the other reason — a
coin flip whose draw reaches the round-wide total before any per-cell screen
runs. A saturated cell is still generated, judged and displayed, and `report.py`
prints the exclusion beside every verdict. The bar, and the level-versus-variance
distinction that decides which tool a cell needs, are in `evals/CRITERIA.md`.

[#45]: https://github.com/JordanMPDS/laconic/issues/45
[#94]: https://github.com/JordanMPDS/laconic/issues/94

**`one_turn` is a `--target` from 2026-08-23, and it is not fatal.** It counts
responses the model produced without calling a single tool, so on sonnet it
never opened a file. It is far more sensitive than the judge — power 0.72
against 0.29 at 40 runs a side — and costs nothing to grade, because
`num_turns` is already on all 27,291 stored runs. Six rules govern it, and
`report.py` enforces the first two:

1. **Scoped or nothing.** `--target one_turn` without `--target-cases` exits.
   Sixteen of 22 cases have a structurally fixed rate: four have no fixture and
   sit at 100%, ten are read every time and sit at 0%, and `design-alerting`
   and `design-audit-log` have read 0 or 1 of 10 in every stored round.
2. **`--target-models sonnet`.** The proxy leaks on haiku — 8 of 183 one-turn
   haiku runs quote fixture-only content, because the fixtures are small enough
   that reading barely moves the token counts — and haiku shows no effect there
   anyway.
3. **The scope is `design-cache`, `design-realtime`, `design-upload`.** Those
   are the cells with variance *and* a measured link to answer quality.
   `design-rate-limit`, `design-retry` and `design-search` have variance and no
   such link, and scoring a behaviour with no established consequence is how a
   surrogate goes wrong.
4. **It clears in addition to `quality_fails`, never instead of it.** The harm
   is already covered by a fatal counter; this one adds resolution, not
   coverage.
5. **Not fatal, deliberately.** The four fatal counters are harm counters, and
   on `floor`, `decision`, `code-fidelity` and `ordered-steps` one turn is the
   only possible behaviour.
6. **The gate inflates the variance by `ONE_TURN_PHI` = 3.39** for between-round
   drift, and prints the same test uninflated beside it. A round that generated
   both sides in one interleaved batch has removed that drift by design and may
   cite the uninflated figure in its round doc — say so explicitly if you do.

The evidence for all six is in
[`one-turn-investigation.md`](../../../evals/results/loop/one-turn-investigation.md)
and [`interleaved-batch.md`](../../../evals/results/loop/interleaved-batch.md).

**Required to accept:** the metric your hypothesis named beats the noise floor
— a sign test across the case/model cells *and* a median shift larger than the
published stdev of the committed snapshot, which `report.py`'s `NOISE` tracks.

**Preference is disclosed and never decisive.** It cannot reject an edit that
passed every deterministic gate, and it may not be cited at all from a round
whose flip rate reached 35%. The judge behind it favours the longer answer 63%
of the time and laconic is the short arm by construction.

## Step 8: replicate

An accepted edit gets one more independent generation of the affected cases,
into a fresh snapshot, and the effect has to survive it. A round is a sample,
not a measurement.

## Step 9: holdout

```bash
python3 evals/bench/run.py --arms laconic --cases-dir evals/holdout \
  --snapshot "evals/snapshots/loop/round-$M-holdout.json"
python3 evals/bench/judge.py --cases-dir evals/holdout \
  --results "evals/snapshots/loop/round-$M-holdout.json" \
  --out "evals/snapshots/loop/round-$M-holdout-judgments.json"
```

A regression here is fatal no matter what the dev set says. Holdout numbers
never enter a published benchmark table.

## Step 10: record it, then propose it

**Add a line to `evals/results/loop/LEDGER.md` whether the edit was accepted or
rejected.** This is not bookkeeping. Twenty attempts scored at p < 0.05 produce
one winner from noise alone, so an accept rate visible beside a claim is what
lets a reader discount it. A ledger showing only accepted edits is a ledger
that lies by omission.

Write `evals/results/loop/round-NN.md` with the hypothesis, the diff, the
before-and-after tables, the replication, and the holdout result. Then open a
PR carrying all of it. Do not merge it yourself.

## What this loop will not do

- Merge its own rule changes.
- Optimize against a `rule-adherence` case.
- Cite preference from a round at or above the flip-rate ceiling.
- Publish a holdout number.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
