<!-- Cost audit of the benchmark harness, 2026-08-24. Produced by DeepSeek
through `delegate`, in a separate worktree with no access to this session's
reasoning. Committed verbatim as received; its figures have not been
independently recomputed.

Read it beside `benchmark-cost-audit-kimi.md`, which audits the same harness on
the same day from the same brief. Neither report is cited by #140, which landed
the following day, but #140 implements several of the reductions both rank
highest: preference dropped from a round, judging scoped to the cells a gate
reads, and a stop after eight consecutive failures. -->

# Benchmark cost audit: reducing Claude API calls per loop round

**Author:** deepseek (delegate run)
**Date:** 2026-08-24
**Scope:** read-only analysis of the benchmark harness. Nothing here changes harness
behaviour, runs the benchmark, or makes an API call. Every number below names the
file and field it was counted from.

The binding constraint on a loop round is subscription quota, measured in Claude
CLI sessions, not dollars or wall-clock. Call counts are therefore the unit this
report ranks reductions in. Dollar figures appear only where a committed round
doc already states them.

---

## 1. Where the calls actually go

Every harness stage is visible in the committed snapshots under
`evals/snapshots/loop/`. A run snapshot records one entry per `(case, arm, model,
rep)`; each usable run carries `ok: true` plus `output_tokens`, `total_cost_usd`,
`num_turns` and `duration_ms` (`run.py:96-120`). Judgments and comparisons nest the
same fields under `usage` (`judge.py:43-92`, `prefer.py:387`). `report.py`'s
`cost_summary` (`report.py:1256-1299`) is the canonical per-stage split; the counts
below reproduce it with shell text counts over the committed files.

### Round 24, the last fully recorded round in this tree

Round 24 is the first edit to clear every gate (`evals/results/loop/round-24.md`,
`evals/results/loop/LEDGER.md` row 24). Its call budget:

| stage | generations | judge calls | source |
|---|---|--:|---|
| Steps 1-3 (round proper) | 220 | 220 | `round-24.md` lines 104, 114; `round-24.json` has 220 `laconic` runs, `round-24-judgments.json` 220 non-carried judgments |
| Step 7 (compare) | 0 | 0 | `report.py`, offline |
| Step 8 (replication 1) | 160 | 0 | `round-24-replication.json` 160 `laconic` runs; token target, no judgments needed |
| Step 8b (replication 2) | 160 | 0 | `round-24-replication-2.json` 160 runs |
| Step 9 (holdout) | 240 | 240 | `round-24-holdout.json` + `-master.json` = 240 runs; 240 judgments |
| **total** | **780** | **460** | `LEDGER.md` row 24: "780 generations … plus 240 holdout runs" |

**The round proper is 440 calls (35.5%). Replication plus holdout is 800 calls
(64.5%).** Two-thirds of a round's quota goes to confirmatory gates, not to the
measurement the edit was scored on. Round 24 is the high end: it ran *two*
replications because step 8 came back partial (7 of 9, p = 0.1797,
`round-24.md` step 8). A normal round runs one replication, 640 of 1080 calls
(59%) outside the round proper.

The 1100 runs in `round-24.json` are not 1100 generations: 880 are control arms
carried from `round-21.json` (baseline, terse-control, word-compression,
concise-style at 220 each), and only the 220 `laconic` runs were bought this
round. The 1100 judgments in `round-24-judgments.json` split the same way: 880
carried, 220 fresh. This carry mechanism (`run.py:160-186`, `judge.py:118-184`)
is the single largest call saving the harness has ever shipped, and it is
already in place — see section 2, item 4.

### Generation vs judging vs preference, recent rounds

| round | generations | judge calls | preference | source |
|---|---|--:|---|
| 14 | 340 fresh + 510 carried | 850 (510 re-graded carried) | — | `round-14.json` arm counts (340 `laconic` + 510 control runs); `judge.py:124-131`; `LEDGER.md` row 15 |
| 15 | — | 385 (carry on) | — | `LEDGER.md` row 15: "385 judge calls against round 14's 850" |
| 20 | 440 | 440 | — | `LEDGER.md` row 20 |
| 22 (n=5 + n=10) | 660 | 660 | 240 | `round-22.md:162-166` |
| 23 | ~400 | ~280 | — | `round-23.md:125` |

Preference is a **third, wholly redundant call stream**. Round 22 bought 240
comparisons and could cite none of them (order-flip rate 45% against the 35%
ceiling, `round-22.md:145`). Round 16 refused the purchase outright: "Preference
not run: it can neither reject a round that passed every deterministic gate nor
rescue one that failed, so 440 comparisons were not bought" (`LEDGER.md` row 16).
`report.py` makes the rule explicit — "Preference is disclosed and never
decisive" (`report.py:705-707`) — and the loop skill repeats it (`SKILL.md`
"Preference is disclosed and never decisive"). Preference is the most expensive
stage that carries no decision power at all.

### The most expensive stages, in call counts

1. **Judging** the fresh treatment arm — one judge call per usable response
   (`judge.py:406-407`, `judge_one` at `judge.py:409`). This is irreducible for
   the fatal counters, which read judge verdicts on every laconic response.
2. **Generation** of the treatment arm — one agentic CLI session per cell.
3. **Preference** — up to 240 calls, zero decision weight.
4. **Replication and holdout** — the confirmatory gates, 59-65% of the round.

---

## 2. Concrete reductions, ranked by calls saved

### 1. Stop buying preference — 240 calls per round, zero statistical cost

`prefer.py` issues one call per comparison, `--both-orders 20` on top of the
full pair set (`prefer.py:284-285`, work list at `prefer.py:336-337`). A full
round is 220 forward pairs plus 20 flipped = 240 calls (round 22, `round-22.md:163`).

**Power cost: none.** Preference may not reject an edit that passed every
deterministic gate, may not rescue one that failed, and is uncitable whenever
the flip rate reaches 35% — which happened in rounds 9, 16 and 22. Round 16
already proved the round survives without it. The only thing lost is a
disclosure column (the length-bias and flip-rate lines in `prefer.py:229-276`),
not a gate. The one real consumer is `report.py`'s `flip_rate` disclosure
(`report.py:1016-1030`), which only ever *suppresses* a citation, never changes
a verdict.

**Recommendation:** drop `prefer.py` from the loop procedure, or keep it as a
manual `--report-only` pass run only when a round is being published and someone
wants the preference disclosure. This is the largest single cut available with
no statistical consequence.

### 2. Early-stop the round-wide fatal batch when the scoped target fails — up to 440 calls

Round 23 did this and recorded it: batch A (the matched one-turn target, 180
generations) failed, so "Batch C, the 220-generation round-wide arm, was **not
run** … the four fatal counters could not have changed the verdict"
(`round-23.md:140-143`), the same precedent as rounds 11, 12 and 14. That is 220
generations plus 220 judge calls saved on the reject path.

**Power cost: none, but only on the reject path.** The fatal counters can *reject*
an edit whose target passed (round 15 died on quality via the holdout; round 20
on quality and safety), so they cannot be skipped when the target passes. The
safe rule is one-directional: score the cheap target first, and only run the
full round-wide arm when (a) the target passes or (b) the round is being
published with complete counters. Round 23 is the template; the loop skill still
lists the full round first, so this should be promoted from precedent to
standing procedure.

### 3. Use `one_turn` as the free screen; judge only what survives it

`one_turn` — whether the model opened a file — is read straight off `num_turns`,
which every run record already carries, so it costs **zero judge calls**
(`report.py:1106`, `evals/results/loop/one-turn-investigation.md`: "num_turns is
present on 27,291 of 27,291 usable runs"). On the design cases it is *more*
powerful than judging — power 0.72 against 0.29 at 40 runs a side
(`one-turn-investigation.md` power table) — because reading is the whole quality
mechanism there (answers that read fail 4/93, answers that do not fail 55/57,
Fisher p = 1.5e-33, `LEDGER.md` row 23).

**Power cost: none, when used as a screen.** Round 23's batch A is the model: 180
generations, 0 judge calls, and the edit failed the target before any verdict was
bought. The rule from the investigation stands: `one_turn` clears a candidate *in
addition to* `quality_fails`, never instead of it, and `quality_fails` still needs
full judging on the surviving rounds. What the screen buys is that bad edits die
at generation cost, not generation-plus-judging cost.

### 4. Reuse stored control arms and their verdicts — already captured, keep it scoped

`--carry-arms-from` copies control runs forward (`run.py:160-186`) and
`--carry-judgments-from` copies their verdicts (`judge.py:118-184`). This cut
round 15's judging from 850 to 385 calls (`LEDGER.md` row 15) — 465 calls a
round — and stopped round 14's worst waste, $25.05 of a $41.37 judging bill
spent re-grading 510 byte-identical carried responses (`judge.py:124-131`).

**Power cost: zero for the fatal counters, and only for them.** The four fatal
counters compare the laconic arm of two rounds and read no control at all, so a
carried control is exactly as good as a fresh one for that purpose. The trap is
in section 3, item 1: a carried control is *not* valid evidence for a
"laconic against baseline" claim, because a control arm drifts with the calendar
and CLI even at fixed rules text. The saving is real only while carrying stays
scoped to the round-wide counters and never feeds an arm comparison.

### 5. A cheaper judge model — dollars, not calls

`judge.py` defaults to `--model sonnet` (`judge.py:257`). Downgrading the judge to
haiku cuts dollars per call but not call count, so it does nothing for the quota
constraint this audit targets. It is also risky: the judge is already the flakiest
stage — round 12 lost 666 of 850 calls at high concurrency, and the interleaved
batch lost 62 of 80 at `--jobs 6` (`evals/results/loop/interleaved-batch.md`
"Judging note"). A cheaper model would not make verdicts *more* reliable.
**Recommendation:** leave the judge model alone. If it is ever revisited, the
archive of stored verdicts lets the agreement between two judge models be
measured offline before spending a single round on it.

### 6. Dedup judging of identical response text — measured zero collisions

The idea is sound in principle: the judge disagrees with itself on 5 to 10% of
identical text (`judge.py:129-131`), so re-judging identical text adds noise
rather than information. But measured on the recent corpus it saves nothing:
all 1100 `text` fields in `round-24.json` are distinct, as are all 1100 in
`round-21.json` (shell `sort | uniq` over `"text": "…"` lines). Because the
judge prompt embeds the response text (`judge.py:419`), unique text means unique
prompt, so there is nothing to dedup within a round; across rounds the carry
mechanism in item 4 already skips identical carried text.

**Recommendation:** not worth building now. It would matter only if a future arm
became deterministic enough to emit byte-identical responses, which the current
arms do not.

---

## 3. What must not be cut

### 1. Reusing stored control arms for arm comparisons

The loop carried this rule until 2026-08-23: "controls are carried because no
control carries rules, so they cannot have moved." The premise is false.
`terse-control` — a two-word prompt — moved **4 of 40 to 11 of 40** in one-turn
rate across eleven days and twelve CLI releases, with nothing changed but the
calendar and the CLI (`evals/results/loop/interleaved-batch.md`, experiment 1;
`SKILL.md` "Carrying the controls was wrong"). Round 21's laconic-against-baseline
p = 0.0052 is not usable, because the control arm is 11 days and 12 releases
older than the treatment (`one-turn-investigation.md` "The arm contrast is
confounded"). Between-batch variance at fixed rules (phi 3.0 to 4.5) exceeds the
rules effects being measured. **Any "laconic against baseline" claim must come
from both arms generated in one interleaved batch** (`interleaved-batch.md`
"Recommendation"). Carrying is correct only for the round-wide fatal counters,
which read no control.

### 2. The replication and the holdout

The holdout is the stage that caught the harm the dev set *reported the opposite
of*. Round 15 passed steps 1-8 — its `quality_fails` even improved 52 to 48 —
and was killed by the holdout, whose design case regressed significantly
(`LEDGER.md` row 15). The dev set was not merely blind to the harm; it inverted
it. No amount of cheaper in-round measurement substitutes for an unseen case set,
and the holdout is the loop's only protection against tuning to the dev set.
Round 24's holdout is run interleaved rather than against a 12-day-old control
for the same reason (`round-24.md` step 9). The replication, likewise, is the
response to a round being a sample rather than a measurement (`SKILL.md` step 8);
round 24's step 8 came back 7 of 9 at p = 0.1797 where step 7 read 8 of 9 at
p = 0.039, which is exactly the non-reproducibility it exists to catch.

### 3. Judging every laconic response

`quality_fails`, `safety_fails` and `never_cut_failures` are fatal and are read
from the full treatment arm (`report.py:113-116`, `_counts` at `report.py:517`).
`never_cut_failures` is a substring check (`metrics.py:265`), but `quality_fails`
and `safety_fails` are blind-judge verdicts that no deterministic metric
reproduces. Skipping judge calls here would either fabricate the fatal counters
or let a regression pass unseen — the exact failure `safety_fails` was added to
fix, after `destructive`/haiku cascaded sessions for four rounds with no gate
seeing it (`report.py:105-112`). The one legitimate reduction is the one already
in place: judge only the fresh arm and carry the controls' verdicts.

### 4. Dropping reps below the baseline's n = 5

The baseline laconic arm is n = 5, and every fatal counter is a five-rep draw
(`SKILL.md` "From round 22 the baseline is round-21"). Reducing reps below 5 would
break the comparison the fatal counters describe, and the counters are already at
their weakest there — an n = 5 draw reads 0 for a cell that fails 8% of the time
about 66% of the time (`SKILL.md`). The power tables point the *other* way: round
22's verdict effect needs 45 reps per cell, ~4.5x what was run, to resolve
(`round-22.md:130-135`). Cutting reps here is a cut to sensitivity on the gates
that already barely resolve anything.

### 5. Arbitration on a fatal-count rise

When a fatal counter rises, the response is a single replication of the risen
cells, not a decision to ignore the rise. Round 9 retired the idea that a rise
larger than +1 is automatically real: the same byte-identical rules text put
`ordered-steps`/haiku at +3 where round 8 had +1, two draws from one wide cell at
Fisher p = 0.65, on opposite sides of the cutoff (`SKILL.md`, `report.py:655-668`).
The arbitration itself is cheap relative to a round, and it is what stops a
lottery flip from rejecting an edit. It must stay.

### 6. Judge concurrency

`judge.py` defaults to `--jobs 6` and its help text warns that raising it "has not
been shown to get more work done": round 12 lost 666 of 850 calls strictly
sequentially, so the binding constraint was the service, not the harness
(`judge.py:267-274`). Higher concurrency is a way to *lose* calls to
infrastructure failures, not save them.

---

## 4. What the harness re-does that it could resume or skip

The harness is already unusually good at not redoing API work. The resume and
carry machinery is complete:

- `run.py:127` `completed_keys` skips any `(case, arm, model, rep)` already in
  the snapshot; a failed call is retried once and then recorded `ok=False`
  (`run.py:481-487`).
- `judge.py:197-213` `resume_index` treats a failed judgment as unfinished and
  a decided one as done; `carry_judgments` (`judge.py:118-184`) copies carried
  arms' verdicts instead of re-buying them.
- `prefer.py:364-368` skips comparisons already decided.

The one historical gap — round 14 re-grading 510 carried responses for $25.05 —
is closed by `--carry-judgments-from`, which the loop now always passes. What
remains is small and non-API, or deliberate:

- **Checksum guards re-hash on every invocation** (`run.py:230-260`,
  `judge.py:95-115`) and **`laconic_rules` re-runs the hook** (`run.py:51-64`),
  but none of these touch the model; they are not a call cost.
- **The output-style probe** is one call per styled arm per `run.py` invocation
  (`run.py:325-346`), a cheap guard against measuring baseline twice, and worth
  its one call.
- **Replication judgments depend on the target.** Round 24's two replications
  needed no judging because the target was `output_tokens` (a run field). A
  replication arbitrating a *count* target (`quality_fails`, `safety_fails`) does
  need judging, because the arbitration compares replicated verdicts against the
  baseline's (`report.py:772-793`). Scoping replications to token targets where
  possible keeps the replication at generation cost only.
- **`prefer.py` has no cross-round carry**, but that is moot under the current
  interleaved procedure, which regenerates both sides fresh each round; there is
  no identical pair to reuse. Dropping preference (section 2, item 1) removes the
  question entirely.

There is no remaining place where the harness regenerates a key a committed
snapshot already holds: the resume paths in all three entry points and the two
carry functions together cover every API call a round could re-issue.

---

## Bottom line

The biggest remaining savings, in order: stop buying preference (240 calls,
zero decision weight); early-stop the round-wide fatal batch when the scoped
target fails (440 calls on the reject path, round-23 precedent); and let
`one_turn` screen edits before any judge call is bought. Everything else that
would cut calls — carrying arms, carrying verdicts, resuming mid-pass — is
already implemented, and the things that *look* cuttable (reps, judging the full
arm, the holdout, the replication) are exactly the parts that caught, in three
separate rounds, a regression the cheaper measurement missed.
