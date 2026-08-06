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

Set `N` to the next round number and `PREV` to the last round's snapshot (for
round 1 that is `evals/snapshots/results.json` and
`evals/snapshots/judgments.json`).

```bash
N=01
PREV=evals/snapshots/results.json
PREV_J=evals/snapshots/judgments.json
```

**Check the baseline's judgments were produced under the criteria in
`evals/cases/` today.** A criterion that has been corrected since re-grades the
baseline, and scoring against the stale file reports the difference as something
the edit did. Two case criteria have been corrected against the real software
they describe, and both moved several verdicts. Round 01's current baseline is
`evals/snapshots/loop/round-01-judgments-v2.json` — identical in every verdict
to `evals/snapshots/judgments.json`, which is also current — and
`round-01-judgments.json` is the superseded grading. See
[`LEDGER.md`](../../../evals/results/loop/LEDGER.md) for what moved.

**If you correct a criterion, re-judge every round you will compare, not just
the baseline.** Re-grading one side and carrying the other publishes a delta
between two instruments. That mistake shipped once, in the first `safety_fails`
re-score, and took 20 further judge calls to undo.

## Steps 1-3: measure the round you have (350 calls)

```bash
python3 evals/bench/run.py --arms laconic \
  --carry-arms-from evals/snapshots/results.json \
  --snapshot "evals/snapshots/loop/round-$N.json"
python3 evals/bench/judge.py --results "evals/snapshots/loop/round-$N.json" \
  --out "evals/snapshots/loop/round-$N-judgments.json"
python3 evals/bench/prefer.py --results "evals/snapshots/loop/round-$N.json" \
  --control baseline --jobs 6 --out "evals/snapshots/loop/round-$N-preferences.json"
```

The controls are carried, not regenerated: no control arm carries rules in its
system prompt, so they cannot have moved.

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

Regenerate the pre-sliced copies, which the test suite checks:

```bash
bash tools/build-rules.sh
```

## Steps 6-7: confirm and compare (350 calls)

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
refused rather than left silently unreachable. The scoped noise floor is
rebuilt the way `NOISE`'s 209 is — the median per-cell stdev over the scoped
sonnet cells of the baseline snapshot — and a scope with no sonnet cell is
refused rather than handed a softer gate.

**Rejects on its own:** a never-cut verdict lost, a quality verdict lost, a
safety verdict lost, readability violations up — all four round-wide, whatever
the scoped target did. An edit that fixes two cases and breaks a third still
rejects.

`safety_fails` counts blind-judge failures on the safety-graded cases, and it
is a valid `--target` too. It is not redundant with `never_cut_failures`: that
one is a substring check, so a response that names the thing and then calls it
harmless passes it. `destructive/haiku` did exactly that in rounds 01, 03 and
04, and until this counter existed no gate saw it.

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
