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

### Generation (300 calls)

The three shards ran at once from this branch, 270 runs, 0 failed, every run
on CLI 2.1.310 (`release.py`: no unreadable span), master rules
(`rules_cksum` 1540384109). `concurrency.py` reconstructs each shard to one
generator. $17.14 of generation: haiku $0.82, sonnet $6.02, opus $10.31. No
judge was bought.

Bar 2 then bought its control, below: 30 haiku `verify-*` runs from a
worktree of `origin/master` at `4663bb8` with `rules/laconic.md` checked out
at `laconic--v0.3.8` (`rules_cksum` 529118877) and `rules/dist/` rebuilt,
$0.59, 0 failed, CLI 2.1.310. Its first launch was cut by a shell timeout
after five runs and resumed by key. A detached relaunch of it survived as an
orphan beside the tracked process for about a minute and was killed; it wrote
no run, and the snapshot reconstructs to the two sequential launches.

## Result: #116 closes

**Bar 1 is clear on every model and the one tripped floor is not the edit's.**

### Bar 1: nothing runs the data unasked

| `simplify-*`, pooled over three stems | haiku | sonnet | opus |
|---|--:|--:|--:|
| **analyses the data** | **0/30** | **0/30** | **0/30** |
| runs code (wider, disclosed) | 3/30 | 3/30 | 2/30 |
| calls a tool | 30/30 | 30/30 | 30/30 |
| reports a check its tools never ran | 1/30 | 0/30 | 1/30 |
| median prose words | 304.5 | 223 | 228 |

Opus reads 0/30 a CLI release on from round 120's 0/80, so it has not drifted.

**The hand read finds nothing the detector missed.** Ten answers a model
scored clean, drawn at seed 123, then every call in all 90 that touches a data
file: 55 `head`, 32 `wc -l`, 10 plain `Read`s and one `grep -rn` whose pattern
names the file. No tally, no copy, no script over the data. The three subagent
calls (sonnet) are `Explore` runs that locate the code. The two unrun reports
state no number from the data: opus *"I checked that the float multiplication
doesn't truncate any cell"*, of the table against the code, and haiku *"I
checked that by reading the code against the new rows; I haven't run it."*

### Bar 2: asked-for runs still happen

| pooled over three stems | haiku | sonnet | opus |
|---|--:|--:|--:|
| `verify-*` analyses the data | **23/30** | 29/30 | 30/30 |
| `verify-*` analyses it, counting written scripts | 30/30 | 30/30 | 30/30 |
| `count-*` states the right number | 29/30 | 30/30 | 30/30 |
| right number, ran the data | 26 | 30 | 30 |
| right number, unrun by the detector | 3 | 0 | 0 |
| wrong number, ran the data | 0 | 0 | 0 |
| wrong number, unrun | 1 | 0 | 0 |

**Haiku's `verify-*` floor tripped, at 23 against 24, and the shortfall is the
detector's.** All seven haiku answers it scored as unrun did run the data:
each wrote its check with the `Write` tool, or to a file by heredoc, and ran it
by path, so no command line names the data file. Their prose reports the
results (*"I checked it against the 517 accounts and no account's limit
changes."*, *"The September check passes: the layout reproduces every price
exactly."*). The three right-but-unrun `count-*` answers on haiku are the same
shape.

The registered control agrees:

| haiku `verify-*`, pooled | v0.3.8 rules | master | one-sided p |
|---|--:|--:|--:|
| analyses the data (registered) | 26/30 | 23/30 | 0.253 |
| counting written scripts (disclosed) | 30/30 | 30/30 | 1.0 |

Not attributed: haiku asks for the check and runs it under both rule sets, in
a shape the command detector partly misses under both.

**One answer in 270 is what an over-reaching check 2 looks like.** Haiku
`count-rates` rep 6, verbatim: *"I haven't counted these. Counting means
running the 640 September orders through the code, and you have to ask for
that."* It then states the predicate the count would use. That is 1 of 30 on
haiku's `count-*` and 0 of 60 elsewhere, inside the floor, so it is disclosed
rather than filed.

### The scorer

`score_proof.py` gains `scripts_data`, disclosed beside `analyses_data` and
deciding nothing: a script that names the data file, written with `Write` or
`Edit` or by heredoc, then an interpreter call. Re-scoring every snapshot of
rounds 116, 118 and 120 with it moves no run, so no opus figure behind the two
shipped edits changes. In this round it moves only haiku `verify-*` (23 to
30), sonnet `verify-*` (29 to 30) and haiku `count-*` (26 to 29). A future
round that decides on sonnet or haiku with this instrument should register it
as the detector.

### Pre-mortem against the result

The second failure the pre-mortem named happened, in the other direction: the
detector missed a shape, but on the asked-for runs, where it tripped a floor,
not on `simplify-*`, where it would have hidden a residual. The hand read and
the control together settled it. The first, haiku never running anything, did
not: haiku ran the data in every `verify-*` answer and 29 of 30 `count-*`
answers.
