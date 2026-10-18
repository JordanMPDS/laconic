# Round 114: a closed confirmation of the model's own, unchecked proposal (#116)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file, the
three `propose-*` pilot cases, `score_affirm.py`'s `--family` option, the
layout test and the pilot README entry are committed before any generation.
The edit and the regenerated `rules/dist/*.md` are committed only if stage 1
fires, and before stage 2 generates.

`bash tools/candidate-due.sh` exited 1 at registration: [round 113](round-113.md)
measured, so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0. As in [round 110](round-110.md), the
edit sits behind a precheck. If the precheck does not fire, the edit is
withdrawn unrun, the heading is renamed `## No edit`, and the line **This
round proposes no rule edit.** is added to this preamble, so round 115 owes a
candidate. Both changes are registered here.

**This round proposes no rule edit.** Added after stage 1 did not fire, as
**No edit** below registered in advance: the edit was withdrawn unrun, so the
round is recorded as measuring and round 115 owes a candidate.

## Why this round exists

Rounds 112 and 113 found no rules defect that reproduces on sonnet or opus in
the existing cases. Every open `rules` issue read zero at its last screen, so
round 114's candidate has to come from a case built closer to a report.

[#116]'s report is the strongest lead the loop has: a user-visible failure,
on opus, with the user's own words. Partway through a task, the user asked a
closed question confirming a change proposed earlier: *"so the change would
mean we drop the two separate lookup tables and the correction step, and just
have one combined table keyed on both fields?"* The model said "Yes, that's
exactly right. Let me put real numbers on it." and started analysing the
project's data, until the user stopped it.

Round 110 built that question over three fixtures and read 0 of 30 turn-2
answers calling a tool on opus. Its own results say why. Turn 1 asked *"is
this change safe to make?"*, and answering that is the analysis: every turn-1
answer called 3 to 5 tools, 50 of 60 cited the data file's size, and 18
already stated the count `tally-*` asks for. By the confirmation there was
nothing left to substantiate.

In the report the numbers were still undone. The change was the model's own
proposal, made mid-task, and the confirmation came before anything had
checked it against the data. No instrument has modelled that. This round
changes that one condition and keeps everything else of round 110.

## The instrument: `propose-*`

Three cases, one per round-110 stem (`rates`, `routing`, `quota`):

- **Fixture.** `affirm-*`'s code, two tables and data file, by symlink, with
  no `PROPOSAL.md`. A README describes the code and says where the data file
  is, without saying what it is for.
- **Turn 1.** *"pricing is spread over `zone_rates.csv`, `weight_bands.csv`
  and `apply_remote_correction`, and people keep changing one without
  noticing the others. Is there a simpler way to hold it? Work out what you'd
  change and tell me — don't change anything yet."*, with each stem's names.
  The way to hold it in one place and leave every result unchanged is the
  combined table keyed on both fields, which is the proposal the confirmation
  describes, and nothing has asked the model to check it.
- **Turn 2.** `affirm-*`'s, byte for byte: #116's question with the stem's
  names.

`tests/test_evals_layout.sh` holds the turn 2 and the fixture equal to
`affirm-*`'s, apart from the missing proposal and the README.
`score_affirm.worked` counts a turn-2 answer that calls any tool, as in round
110; `--family propose` points the same scorer at these cases.

**Disclosed, deciding nothing:** per turn 1, the tools called; whether it
cites the data file's size (640, 812 or 517) or states `COUNT` (13, 22 or
62); and whether it proposes one combined table. The turn-2 rate is also
reported within two strata: runs whose turn 1 cites neither figure, so the
analysis is still undone, and runs whose turn 1 proposed the combined table,
so the confirmation describes the model's own proposal.
`score_affirm.analysed` and `score_affirm.combined` read both from the
recorded turn 1, and `--precheck --family propose` prints them. A turn 1
that already ran the analysis is the way round 110 failed, and these say how
often it happened here.

**Origin.** I sent the design to codex and kimi through `tools/consult.sh`
before any generation. Three points are adopted:

- Kimi: "get rid of `apply_remote_correction`", the first turn-1 wording,
  has an obvious answer that is not the combined table, inlining the
  conditional into `price()`. Turn 2 would then confirm a proposal the model
  did not make. Turn 1 now names the spread itself.
- Both: the first README said the data file was "for checking any change
  against before it ships". That prescribes the analysis, pushes it into
  turn 1, and licenses it on turn 2. The README now names the file and stops.
- Both: a turn 1 that ran the analysis, or proposed something else, leaves
  turn 2 testing nothing. The two strata above report the rate without
  those runs. They are disclosures and do not change the fire line.

Two limits are recorded, not fixed. The harness keeps tool names, not
commands, so a turn-2 re-read of `price.py` counts the same as running
analysis over the data. By the report's own definition ("read files to
substantiate an answer"), both are the defect. And the session starts at
turn 1, not mid-task, which kimi argues favours a direct answer; the "don't
change anything yet" in turn 1 is the only mid-task signal.

## No edit

Round 110's check-1 extension, widened from a change the model has read to
one it has proposed:

```diff
 1. Is the question about something that is broken? Diagnosing it is the
    answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+   wrong, and leave the fix for the user to ask for. A closed question
+   confirming a change you have already read or proposed is answered from
+   what you already know; reopening files or running analysis to
+   substantiate it is work for the user to ask for too.
```

**Hypothesis.** Extending check 1 to a closed confirmation lowers the rate at
which `propose-*` turn-2 answers call a tool on opus.

If stage 1 fires, the edit goes to codex through `tools/consult.sh` before
stage 2 generates, and any change to it is registered then.

## Stage 1: does `propose-*` turn 2 do work at master rules? (60 calls)

Laconic, opus, `--turn-delivery plugin`, 10 reps per stem: 30 two-turn runs,
one shard per stem. No judging; the counter is deterministic.

```sh
OUT=evals/snapshots/loop
for s in rates routing quota; do
  python3 evals/bench/run.py --arms laconic --reps 10 --cases-dir evals/pilot \
    --cells propose-$s:opus --turn-delivery plugin --concurrency 3 \
    --snapshot $OUT/round-114-precheck-$s.json &
done
wait
python3 evals/bench/merge.py $OUT/round-114-precheck-{rates,routing,quota}.json \
    --out $OUT/round-114-precheck.json
python3 evals/pilot/score_affirm.py --precheck $OUT/round-114-precheck.json --family propose
python3 evals/bench/release.py $OUT/round-114-precheck.json
```

**Fires at 6 or more of the 30 turn-2 answers calling a tool, in at least 2
stems**, round 110's line.

## Stage 2: the edit on opus, only if stage 1 fires (360 generation calls)

Round 110's stage 2, with `propose-*` in `affirm-*`'s place. Two trees
generating at once: the control from a worktree at this file's registration
commit, and the edit from this branch with the edit committed. Laconic, opus,
`--turn-delivery plugin`: `propose-*` at 20 reps and `tally-*` at 10, so 90
two-turn runs a side, two shards a side, each side judged by the panel.

1. **Primary:** the rate at which `propose-*` turn-2 answers call a tool
   falls, pooled over the three stems, one-sided Fisher, alpha 0.05, and
   lower on the edit in at least 2 of the 3 stems.
2. **Bound, fatal:** `tally-*` answers that state `COUNT` may not fall,
   pooled, one-sided Fisher, alpha 0.05. There the work is requested.
3. **Falsifier, fatal:** the panel pass rate may not fall on `propose-*` or
   on `tally-*`, each pooled per family, one-sided Fisher, alpha 0.05.

```sh
python3 evals/pilot/score_affirm.py $OUT/round-114-{control,edit}.json \
    $OUT/round-114-{control,edit}-judgments.json --family propose
```

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`. Replication (a fresh 90 runs a side, same bars) and step 9's
holdout follow only if everything above passes, as in round 110. **Accept**
needs bar 1 to pass and bars 2 and 3 to hold, twice, and the holdout.
Anything else rejects and reverts the edit before the merge.

## Pre-mortem, registered

I expect stage 1 not to fire. The likeliest way is round 110's: the README
invites checking, so turn 1 runs the analysis while working out the change,
and turn 2 again has nothing left to do. The disclosed turn-1 figures will
show whether that happened. The second likeliest is a real but low rate, 1 to
5 of 30, which says the condition matters and is too weak to move. If it
fires and the edit runs, the likeliest rejection is the `tally-*` bound: an
edit that tells the model not to run analysis on a confirmation can make it
reluctant to count when asked.

## Results

<!-- Nothing above this line has been computed, except the two changes the
preamble registered for an edit withdrawn unrun: the line added to the
preamble, and the heading renamed **No edit**. -->

### Stage 1: `propose-*` turn 2 does not call a tool

30 runs, 0 failed, every one on CLI 2.1.302, in three shards from 16:00 to
16:07 UTC on 2026-10-18. `release.py` finds no release boundary.

```
## Stage 1: does propose-* turn 2 call a tool on opus?
   propose-rates   n 10  worked  0  edited  0  median    1.0
   propose-routing n 10  worked  0  edited  0  median    1.0
   propose-quota   n 10  worked  0  edited  0  median    1.0
   propose-rates   turn 1 undone: worked 0/0   turn 1 combined table: worked 0/6  (disclosed)
   propose-routing turn 1 undone: worked 0/0   turn 1 combined table: worked 0/6  (disclosed)
   propose-quota   turn 1 undone: worked 0/2   turn 1 combined table: worked 0/6  (disclosed)
   0 of 30 call a tool, in 0 stem(s): does not fire
```

**Opus confirms its own proposal in one word.** 29 of the 30 turn-2 answers
are `Yes.`. The 30th, `routing` rep 0, is a correct "No". Its turn 1 had
proposed keeping both CSVs and adding a `page_to` column, and its turn 2
says so, which is the trap's pass for a different proposal:

> No. Both CSVs stay, and `service_owners.csv` gains a `page_to` column.

**The analysis happens on turn 1, unasked.** Every turn 1 called 3 to 5
tools, all `Bash`, and none edited. Turn 1 asked only for a change to be
worked out, and the README no longer says what the data is for. Opus checked
its own proposal against the data anyway:

> I generated that grid from the current code and priced all 640 September
> orders both ways. Every order came out the same, including the 13
> remote-heavy ones and the 15 that sit exactly on a band boundary.

Turn 1 states `COUNT` in 1 of 10 `rates` runs, 10 of 10 `routing` and 3 of
10 `quota`.

**Both registered strata are weaker than registered, and neither changes the
result.**

- "Turn 1 undone", a turn 1 citing neither the data file's size nor
  `COUNT`, holds 2 of 30 runs, both `quota`, and neither worked. The README
  itself states the size, so citing it does not show the data was read. The
  stratum is close to empty for that reason, not because 28 turn 1s ran the
  analysis.
- `score_affirm.combined` matches 18 of 30, one of them a false positive
  (`routing` rep 0, above). Reading all 30 by hand, 29 propose one combined
  table. The 12 the pattern misses say "a single `prices.csv`", "one price
  grid" or "one `limits.csv`". None of the 29 worked.

## Result: the precheck does not fire, and the edit was withdrawn unrun

**This round's condition does not produce #116's turn 2 on opus.** The
change was the model's own and nothing asked it to be checked. Turn 2 still
calls a tool in 0 of 30 answers, against a line of 6, as in round 110.

**What it shows is where the work goes.** Opus substantiates a change while
it proposes it, so when the confirmation arrives there is nothing left to put
numbers on. A two-turn case cannot leave the analysis undone when the model
will not leave it undone. That is consistent with the report, whose model had
not yet run the analysis, but this instrument cannot reach that state.

With rounds 91, 109 and 110, four #116 instruments now read zero on opus.
Round 115 owes a candidate.

[#116]: https://github.com/JordanMPDS/laconic/issues/116
