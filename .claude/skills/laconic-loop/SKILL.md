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

## Steps 1-3: measure the round you have (405 calls at n=5)

```bash
python3 evals/bench/run.py --arms laconic --reps 5 \
  --carry-arms-from "$PREV" \
  --snapshot "evals/snapshots/loop/round-$N.json"
python3 evals/bench/judge.py --results "evals/snapshots/loop/round-$N.json" \
  --carry-judgments-from "$PREV_J" --jobs 6 \
  --out "evals/snapshots/loop/round-$N-judgments.json"
```

220 generations, one per case/model/rep of the laconic arm, and 185 judgments —
37 gate-reading cells at 5 reps. Both commands print that number before they
spend anything, so check the budget line against what you meant to buy.

**Either pass stops itself after eight consecutive failures.** A usage limit
fails every remaining key and each one costs two calls, because both harnesses
retry once: on 2026-08-24 two limit windows ground through 152 keys on round 25
and 152 on its arbitration, roughly 600 generation calls that produced no data,
and round 12's judging pass returned 850 judgments of which 666 were judge-call
failures. Neither a failed key nor a failed judgment is recorded as done, so
re-running the identical command redoes exactly what the stop left behind — the
resume path is what makes stopping free. In `judge.py` the run is counted over
completions, so the `--jobs` calls already in flight still finish.
`--max-consecutive-failures 0` restores the old behaviour in both, and nothing
else needs it.

**`judge.py` grades only what a gate can read.** `quality_fails` and
`safety_fails` are the only counters that read verdicts, and both skip
rule-adherence cases and saturated cells, so `conditional`, `decision`, `floor`
and `ordered-steps`/haiku were graded every round and could reject nothing: 35
of the 220 judge calls a round used to buy at n=5. What that gives up is
disclosure, not scoring — those verdicts are how a round sees whether the rules
were obeyed on the cases that grade adherence to them. **Pass `--judge-all` when
the hypothesis names one of those cases, and when re-judging a snapshot another
round will be compared against**, so both sides of a comparison carry the same
coverage. A file judged either way says which it is, in its metadata and at the
top of the rendered report.

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

**Generate 10 reps a side, score, and extend only if the round needs it.**
`run.py` resumes by key, so extending a snapshot from 10 reps to 25 costs only
the 15 new ones — the staged round and the full one buy exactly the same data if
you go all the way. Extend when a fatal counter rises, or when the target lands
close enough to the floor that reps would settle it; otherwise stop at 10. The
sign test that decides an `output_tokens` target counts cells, not reps, and
round 26 read 8 of 8 at p = 0.008, which 10 reps would very likely also have
read. The one thing that genuinely needs 20 a side is [#133]'s rate screen, and
that only matters when a counter rises, which is exactly the case where you
extend. Round 26 generated and judged 800 calls; staged, it would have opened
with 320.

[#133]: https://github.com/JordanMPDS/laconic/issues/133

**If you shard a round across processes, declare it.** One `run.py` is
sequential, so a merged snapshot from five of them describes a regime no single
process could produce, and until [#120] nothing in the file recorded it - ten
committed snapshots had to have it reconstructed from timestamps. Sharding is
still the right call for a 440-run pass; pass `--concurrency N` to every
process, which stamps `metadata.concurrency_declared`, and each pass warns if
its own timestamps reconstruct to more invocations than it declared. Check the
whole archive with `python3 evals/bench/concurrency.py`. What the regime does to
a measurement is bounded in `evals/results/loop/concurrency-audit.md`: nothing
detectable on `output_tokens`, and the one-turn rate moves in opposite
directions on the two sides of the contrast, so it is batch rather than regime.

[#120]: https://github.com/JordanMPDS/laconic/issues/120

`run.py` loops arms innermost, so a single invocation already interleaves them.
Two rules revisions cannot share one invocation — `rules_cksum` is resolved once
at startup — so when the round compares master against an edit, run each side
from its own tree, which is what `interleaved-batch.md` records and what resolved
a contrast at 40 runs a side that the archive could not resolve at any n.

**Run the two sides simultaneously, not one after the other.** Rounds 30, 31 and
29 ran their control and edit passes sequentially, which puts hours between the
two halves of the comparison. Round 37 then measured a *syntactic* behaviour
moving **4.7x in five days** at byte-identical rules
([`round-37.md`](../../../evals/results/loop/round-37.md)), so a sequential
window is exactly the exposure to avoid.

Round 38 is the first round run the other way and the pattern is cheap to copy:

```bash
git worktree add /tmp/laconic-control master
# edit side, from the branch:
python3 evals/bench/run.py --arms laconic --models sonnet --reps 30 \
  --cases '<scope>' --concurrency 2 \
  --snapshot evals/snapshots/loop/round-$N-edit.json &
# control side, from the worktree, writing back to the main tree:
cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 30 --cases '<scope>' --concurrency 2 \
  --snapshot <abs path>/evals/snapshots/loop/round-$N-control.json &
```

Declare `--concurrency 2` on **both**, because two CLI invocations really are in
flight. Each snapshot still reconstructs to one generator of its own, so the
[#120] audit is satisfied and the declaration is conservative rather than false.
Round 38's two sides tracked within two runs of each other for 90 runs a side.

It costs nothing extra, halves wall time, and makes era and regime cancel between
the sides instead of confounding them.

**Carrying is still correct for the round-wide fatal counters**, which compare
the laconic arm of two rounds and read no control at all. What it is not correct
for is any statement of the form "laconic against baseline". Nor for the baseline a
scoped count target is registered against, which step 5 requires the round to
generate for itself.

**But carrying the laconic arm is a bet that the counted behaviour is
era-stable, and round 37 watched that bet lose.** Holding `rules_cksum`
136269960 and `laconic_level` `full` fixed - same case, same arm, no judge
anywhere - the share of `walkthrough` responses opening with a pure announcement
read 55.0%, 38.8% and 52.5% across 2026-08-27 to 08-31, then **10.0%** on 09-01.
August pooled against that day is Fisher **p = 1.0e-05**, over five CLI patch
releases with the rules text unchanged.

The same test on a counter a gate actually reads is reassuring and does not
settle it: the share of laconic `walkthrough` responses carrying any readability
violation went 15.0%, 36.2%, 26.2%, 27.5% over those same four dates, and the
widest pair is **p = 0.11** - not significant. Its per-response *mean* swung 0.35
to 1.35, which is the clustering [#103] already documents rather than drift.

So the position is not "fatal counters drift" and it is not "carrying is safe".
It is that **one syntactic behaviour moved 4.7x and another did not, at the same
rules text on the same case, and nothing told us in advance which would be
which.** Practical consequences:

- Generate both sides when the round can afford it. A scoped round always can.
- When a counter moves in a carried comparison, **movement is not evidence the
  edit caused it** until the era is ruled out. Re-generating the baseline arm for
  that one counter is cheaper than a wrong accept.
- A rate quoted from a snapshot needs its date. `rules_cksum` certifies the
  instrument was identical, which is exactly what made round 37's measurement
  clean - the guard cannot see era at all.

See [`round-37.md`](../../../evals/results/loop/round-37.md).

[#103]: https://github.com/JordanMPDS/laconic/issues/103

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

**A `Wrong:`/`Right:` edit pre-registers the cells that carry the demonstrated
form**, whether or not the hypothesis names them. That is [#164] item 2, and it
exists because round 31's propagation into `destructive`/sonnet was found only
because the safety screen happened to cover that cell — the hypothesis was about
`walkthrough`.

Half of such a pair is a rendered instance of the form it prohibits, so the file
gains a specimen of the thing it bans. Round 38 tested whether that specimen is
the carrier by replacing both rendered arrow examples with prose, and **it is
not**: arrows did not fall (control 36, edit 62, p = 0.341) and the point estimate
moved the wrong way. What survives both rounds is the narrower reading that the
*recency of a newly added example* matters rather than the standing presence of
one — untested, and the reason the pre-registration is worth keeping.

[#164]: https://github.com/JordanMPDS/laconic/issues/164

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

**A count target takes its registered baseline from the round's own control,
never from a prior round's snapshot.** Round 31 registered `walkthrough`/sonnet
at 46 arrows off `round-30-control.json`, three days old and generated at
byte-identical master rules. Its own interleaved control read 31 over the same
40 runs, and at equal reps the cell fell from 2.00 arrows per run to 0.60 with
nothing changed but the calendar and the CLI. A prior control is fine for
choosing a scope and sizing a round; the number the hypothesis is scored
against has to come from the control generated beside the edit. This holds for
every count target, not only [#36]'s arrows — the same drift that made carried
arm comparisons unusable from round 16 reaches a registered baseline too.

[#36]: https://github.com/JordanMPDS/laconic/issues/36

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

## Steps 6-7: confirm and compare (405 calls)

**Score the cheap target before buying the expensive arm.** A token target needs
no judging at all, and `one_turn` is free off `num_turns`, so a scoped batch of
those two costs generations only and can kill a bad edit before the round-wide
arm is bought. Round 23 already worked this way and recorded it: its scoped
batch failed, so its 220-generation round-wide arm was never generated. That was
treated as one round's judgement call; it is the standing order now. Buy in this
sequence, and stop at the first step that fails:

1. The scoped batch the hypothesis named, scored on its own target.
2. The round-wide laconic arm and its judgments, for the fatal counters.
3. Step 8's replication, and only for an edit that has passed both.

Repeat steps 1-3 with `N` incremented, then:

```bash
python3 evals/bench/report.py \
  --results "evals/snapshots/loop/round-$M.json" \
  --judgments "evals/snapshots/loop/round-$M-judgments.json" \
  --against "evals/snapshots/loop/round-$N.json" \
  --against-judgments "evals/snapshots/loop/round-$N-judgments.json" \
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

**`output_tokens` is scored inside one reading stratum, never on the marginal
median ([#131]).** A cell whose answers opened a file in both rounds is compared
on the median of those answers; a cell that opened one in neither is compared on
the median of the answers that did not; a cell whose reading rate crossed
between the two rounds has nothing to compare and does not vote. The third case
is what a round has to be designed around. At 10 reps a side rounds 07, 08, 11
and 14 lose enough cells that way to fall under the six the sign test needs, and
the target is refused rather than scored; at 25 reps on eight sonnet cases,
rounds 25 and 26 lost none. Prefer that shape, and prefer a sonnet scope: the
`num_turns` proxy separates cleanly on sonnet and leaks on haiku. The verdict
prints where every cell voted, which cells it refused with their reading rates,
and what the marginal shift the old target read would have been.

[#131]: https://github.com/JordanMPDS/laconic/issues/131

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

**`turns` is a `--target` from 2026-08-25, and it IS fatal ([#49]).** It is the
per-cell median of `num_turns` over the grounded stratum, and it measures action
scope: how much work an answer did once it had already started reading. Laconic
bounds prose and nothing else, so an edit can buy shorter answers by doing more
— [#49] reports a one-line factual question that spent four tool calls and a
file edit, and the prose it produced passed every prose rule in the ruleset.

1. **Grounded stratum only, and there is no fallback.** An unread answer has 0
   or 1 turns by construction, so an unread turn median cannot move; a cell
   compared inside it would vote a guaranteed tie. Cells without a grounded
   stratum on both sides are absent, not tied. This is also what keeps the
   metric off the axis [#131] protects: turns falling because answers stopped
   reading is the [#46]/[#138] failure `one_turn` already gates, and inside the
   grounded stratum the only way down is doing less after the reading happened.
2. **Fatal in one direction.** A rise rejects whatever the round named as its
   target; a fall never rejects and is simply the target direction. That is
   what `FATAL` holds — harm counters — and it is the line that separates this
   from `one_turn`: not opening a file is not harm, spending the user's tokens
   on work they did not ask for is.
3. **A rise needs both estimators: broad *and* past the floor.** `num_turns` is
   a small integer, so a cell whose grounded runs all took the same number of
   turns has stdev 0 and the median-of-stdevs floor collapses to 0.0, at which
   point any rise clears it. Under a floor alone the archive re-score rejected
   rounds 07, 08 and 10 on `destructive`/sonnet, a cell that went from 3.0
   turns to 4.0 — one risen cell of
   eighteen, moving the round-wide median half a turn because half the cells
   sat either side of it. A rise must also win a sign test across cells.
4. **The floor is measured, never published.** `NOISE["stdev"]` is 260 tokens
   and says nothing about turns, and a turn constant would be tuned to the
   rounds that already exist. It is the median per-cell grounded stdev of the
   baseline, the same estimator the scoped token floor is built from.
5. **Power is thin on a small scope.** The sign test is two-sided exact, so at
   eight cells — the scope rounds 25 and 26 used — only a clean 8-of-8 sweep
   reaches alpha; 7 of 8 reads p = 0.070. On a round-wide scope of 18 to 31
   cells it has room. Do not read "held" on eight cells as "no effect".
6. **Every stored round holds under it.** Re-scoring rounds 05 through 26
   changes no verdict: the largest movement is +0.5 turns and the most cells
   ever rising is 3 of 31. The gate is live and has never fired on the archive,
   so a round that trips it is reporting something new.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#138]: https://github.com/JordanMPDS/laconic/issues/138
[#142]: https://github.com/JordanMPDS/laconic/issues/142

`num_turns` cannot tell a read from a write, so `turns` measures the volume of
action and not its kind. Since [#142] the CLI is invoked with
`--output-format stream-json`, and every run record carries a `tools` list of
the tool names that response actually invoked, in order.

**Nothing scores that list yet, and a round you run does not gate on it.** The
field is absent on every round below 27, so a read-versus-write metric built
from it today could not be re-scored against a single stored round, and a gate
with no measured null rejects on whatever its first round happens to do. `turns`
went live only because `num_turns` re-scored rounds 05 to 26 offline first. The
list accumulates until enough rounds carry it to say what a normal tool mix
looks like.

**Required to accept:** the metric your hypothesis named beats the noise floor
— a sign test across the case/model cells *and* a median shift larger than the
published stdev of the committed snapshot, which `report.py`'s `NOISE` tracks.

**Preference is no longer part of a round.** It was 220 comparisons plus 20
flipped rerolls, roughly a third of a round's calls, and `report.py` says in its
own output that it is never decisive: it cannot reject an edit that passed every
deterministic gate, and it may not be cited at all from a round whose flip rate
reached 35%. The judge behind it favours the longer answer 63% of the time and
laconic is the short arm by construction. Round 22 bought 240 comparisons and
could cite none of them.

It stays as an opt-in pass, for a publication that wants a preference column and
is willing to pay for it. Nothing else changes — `report.py` still reads
`--preferences` when a round has bought one:

```bash
python3 evals/bench/prefer.py --results "evals/snapshots/loop/round-$M.json" \
  --control baseline --jobs 6 --out "evals/snapshots/loop/round-$M-preferences.json"
```

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
