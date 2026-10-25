# Round 123: does check 2 hold on sonnet and haiku? (#116)

**Registration. Nothing below the results line has been computed**, except the
opus figures quoted from rounds 118 and 120, which are merged. This file and
the scorer change below are committed before any generation.

**This round proposes no rule edit.** It measures the shipped rules on the two
models rounds 116 to 120 never generated, so round 124 owes a candidate.

`bash tools/release-due.sh` exited 0 at registration: v0.3.10 is tagged and
current. `bash tools/candidate-due.sh` exited 0: round 122 tested a
candidate, so this round may measure. `rules/laconic.md` at master is
v0.3.10's, byte for byte (`git diff laconic--v0.3.10 master -- rules/` is
empty).

## Why this round exists

[#116] reports volunteered work: a question answered, then substantiated with
analysis of the user's data that nobody asked for. Two edits for it shipped.
Round 118's check 2 before acting (v0.3.9) leaves running the user's data
through code for the user to ask for, and round 120 (v0.3.10) keyed that check
on command shape and narrowed its exception to a fact that is itself the
answer. Both were decided on **opus alone**:

| opus, at the accepted edit | sample | replication |
|---|--:|--:|
| `simplify-*` analyses the data (round 118, three stems) | 7/60 | 12/60 |
| `simplify-quota` analyses the data (round 120) | 0/40 | 0/40 |
| `verify-*` analyses the data when asked (bound) | 30/30, 12/12 | 30/30, 12/12 |
| `count-quota` states the right count, 62 (disclosed) | 12/12 | 12/12 |

Check 2 is a sentence in every session on every model, and nothing has
measured it on sonnet or haiku in either direction: whether either model still
runs the data unasked, and whether the check stops either one from running it
when asked, or from counting when the count is the answer. Those are the two
ways the shipped fix could be wrong for most of the plugin's users without any
round having seen it. Every other direction of [#116] is tested — the
`conditional` edit and the confirmation turn read zero on opus in rounds 91,
109, 110 and 114 — so this is the last open question on the issue, and its
answer decides whether the issue closes.

## The instrument

Round 118's, unchanged: `simplify-*`, `verify-*` and `count-*` over the
`rates`, `routing` and `quota` stems in `evals/pilot`, scored by
`evals/pilot/score_proof.py` from the recorded tool inputs and never from the
prose. `analyses_data` is a call that runs the data file through an
interpreter, an aggregating pipeline or a `Grep` count; the right number for
`count-*` is matched by pattern (13, 22 and 62). No judge is bought: every bar
below is read off the tool calls or the number.

**One scorer change, committed with this file.** `--calibrate` read opus
alone, because every round that used it was decided there. It now prints
every model the snapshots hold, each family pooled over its three stems, and
splits `count-*` four ways: right number and ran the data, right number
unrun, wrong number and ran, wrong number unrun. A wrong number from an answer
that counted is the model's arithmetic; a missing number from one that did not
count is what an over-reaching check 2 would produce. Nothing the scorer
already printed changes, and its selftest pins the split.

## Design

The laconic arm at master rules, `full`, on haiku, sonnet and opus, 10 reps a
case: 9 cases x 3 models x 10 = **270 generations**, three shards by family
run at once, `--concurrency 3` on each.

```bash
P="--arms laconic --models haiku,sonnet,opus --cases-dir evals/pilot --reps 10 --concurrency 3"
python3 evals/bench/run.py $P --cases 'simplify-*' --snapshot evals/snapshots/loop/round-123-simplify.json &
python3 evals/bench/run.py $P --cases 'verify-*'   --snapshot evals/snapshots/loop/round-123-verify.json &
python3 evals/bench/run.py $P --cases 'count-*'    --snapshot evals/snapshots/loop/round-123-count.json &
wait
python3 evals/bench/release.py evals/snapshots/loop/round-123-{simplify,verify,count}.json
python3 evals/pilot/score_proof.py --calibrate evals/snapshots/loop/round-123-{simplify,verify,count}.json
```

Opus is in the round as every round's is, and here it is the drift check: the
same cells at the same rules a CLI release or more after round 120.

## Bars, per model, one look

1. **Residual.** `simplify-*` answers that analyse the data, pooled over the
   three stems (n = 30):
   - **9 or more: fires.** The shipped check does not reach this model. The
     residual is recorded on [#116], the issue stays open, and round 124,
     which owes a candidate, may take it.
   - **4 to 8: undecided.** Recorded on [#116] and the issue stays open; no
     candidate is registered on this round alone.
   - **3 or fewer: clear.** Zero of 30 bounds the rate under about 10% at 95%.
2. **Over-suppression floors.** `verify-*` answers that analyse the data, and
   `count-*` answers that state the right number, each pooled (n = 30). A
   floor **trips below 24 of 30**.
   - A tripped floor buys a control: the same family on that model, 10 reps,
     from a worktree of master with `rules/laconic.md` checked out at
     `laconic--v0.3.8`, the release before check 2 existed, and its
     `rules/dist/` rebuilt. The shortfall is the edit's if the control is
     higher by one-sided Fisher at alpha 0.05, and then it is filed as a
     regression issue of its own.
   - Otherwise the shortfall is the model's, and the four-way split says how.
3. **#116 closes** when every model is clear on bar 1 and no tripped floor is
   attributed to the edit. Anything else leaves it open with this round's
   numbers on it.

The control's span covers both edits, v0.3.9 and v0.3.10, so an attributed
shortfall names check 2 as it now stands rather than either revision.

**Disclosed, deciding nothing:** each stem's rates; `runs_code`; answers that
call any tool; answers reporting a check their tools never ran (`claims
unrun`, the asserted-number screen); median prose words; median output tokens;
cost; `release.py`; and a hand read of ten `simplify-*` answers per model that
the classifier scores as not analysing the data, drawn at seed 123, for any
tally it misses — `rg -c`, a renamed copy of the data file, a script that
reads it indirectly.

## Where the design came from

`bash tools/consult.sh` asked codex, deepseek and kimi about this design;
codex and deepseek did not answer within the timeout. Three things here are
kimi's: the floors at n = 30 rather than 15, because at 15 a model whose true
rate is 85% to 90% trips by noise often enough to buy controls for nothing;
the four-way `count-*` split, which separates arithmetic from suppression
without a control; and the asserted-number screen and the hand read, for a
model that states numbers it never computed or tallies in a shape the command
detector cannot see. The undecided band in bar 1 is kimi's point that 9 of 30
is a decision line and not a confidence bound, so a middle reading should not
close anything.

## Pre-mortem

The likeliest way this round misleads is haiku. If haiku reads the code and
never runs anything, bar 1 is clear trivially, and its `count-*` floor trips
because it does not count rather than because check 2 stops it; the control
is there for exactly that, and would read low too. The next likeliest is the
detector: sonnet tallying the data in a shape `analyses_data` does not match,
so bar 1 reads clear while the behaviour is there. The hand read is the only
guard on that, and ten answers a model will miss a rate under about 20%.
Least likely is opus drifting back past bar 1, which round 120 measured at 0
of 80 a CLI release ago.

[#116]: https://github.com/JordanMPDS/laconic/issues/116

## Results
