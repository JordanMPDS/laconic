# Round 90: the design licence's reading instruction, moved to the head of the bullet (#264)

**Registration. Nothing below the results line has been computed**, except the
round 77 and 78 figures, which are merged. This file, the new arm, its
`BUILT-FROM.json` entry, the scorer's `--model` flag and the tests that pin the
arm are committed in one commit before any generation.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_read_hoist.py --edit-arm laconic-design-read \
  evals/snapshots/loop/round-90-*.json
python3 evals/pilot/score_read_hoist.py --edit-arm laconic-design-read \
  --model opus evals/snapshots/loop/round-90-*.json
```

`bash tools/candidate-due.sh` exited 1 at registration: rounds 88 and 89 both
measured, so round 90 has to carry a rule edit. It does, under **The edit**.

## Why this round exists

[#264]: on sonnet `design-*` questions, most laconic answers open no file, and
on design questions an unread answer is the documented failure ([#88]). Rounds
77 and 78 cut the unread share hard by putting a reading instruction in item 1
of the pre-action check: −16.2 and −26.0 points, MH p < 0.00001, every cell
falling. Both were rejected on the same fatal bound. Prose length on the four
no-fixture sentinel cells rose 1.111x and 1.208x against a 1.10x margin, and no
sentinel run opened anything. Round 78 closed that line: a third wording of
item 1 is not registered.

This round does not touch item 1. Item 1 sits above every level marker and
every question goes through it, including `What does git restore --staged do?`
in an empty directory. The design licence under `## Level: full` already tells
the model to read: its sub-bullet ends *"Read what the question is about, then
be brief about it."* At master that sentence coexists with a 64.5% unread rate
(round 78's control), so it is close to inert where it stands. It is the last
sentence of a sub-bullet, and it ends on a competing instruction to be brief.

**The deciding model is sonnet**, which is where #264 was observed (round 56's
benchmark) and where rounds 77 and 78 measured it. Opus is generated beside it
at small reps as a disclosure, per `AGENTS.md`. No stage-1 precheck is bought:
the defect fired in round 78's control at 387 of 600 eight days ago, and this
round's own control re-measures it in the same pass.

## The edit

`rules/laconic.md`, the design-question bullet under `## Level: full`:

```diff
-- A design question asks for an approach, not a treatise. "How would that be
-  built?" is about something that does not exist yet, and what it wants is the
+- A design question is answered from its files: open them first. A design
+  question asks for an approach, not a treatise. "How would that be
+  built?" is about something that does not exist yet, and what it wants is the
 ...
   - **This licence is earned by reading, not by being brief.** It covers an
     approach derived from the files the question is about. An approach recalled
     from general practice has not earned it and stays subject to everything
-    above. Read what the question is about, then be brief about it.
+    above.
```

The 11-word sentence replaces an 11-word sentence, so the `full` slice is
1,146 words on both sides and a length difference cannot come from the file
growing. The pre-action check is byte for byte the shipped one, which
`tests/test_bench.py` asserts.

**Tested as an arm, so `rules/laconic.md` does not move until step 1
accepts.** `evals/arms/laconic-design-read.md` is the live `full` slice at
`rules_cksum` **288018845** with these two swaps, checked by exact equality
against the hook's output. Both arms go through `--append-system-prompt`, so
each shard samples them at adjacent moments under one CLI trajectory.

**Where the ideas came from.** Moving the instruction out of item 1 and into
the design bullet is this round's own. Through `tools/consult.sh`, DeepSeek
supplied the exact wording and the word-matched swap (the first draft was nine
words long), and pointed out that round 10's "location bounds a licence"
finding was retracted by round 12, so it is not cited here. Kimi asked for the
sentinel length to be reported per cell, with `decision` named in advance as
the cell at risk, and for the sentinel reps to be cheap enough to report per
cell; both are below. Kimi's calibration arm (an inert word-matched sentence)
and DeepSeek's `-read` disclosure arm were not taken: `-read` is stale at this
slice and rebuilding it buys a disclosure that decides nothing. Codex did not
answer.

### The claim

> Moving the design licence's reading instruction to the head of the design
> bullet should move the share of `design-*` answers on sonnet that open no
> file **down**, without the sentinel's prose length rising past 1.10x.

## The bars

Round 77's bars, unchanged, scored by the same code with
`--edit-arm laconic-design-read`. Every endpoint is deterministic, and no judge
call is bought in step 1.

**Primary.** Unread rate, `laconic-design-read` below `laconic`, on
`design-cache`, `design-rate-limit`, `design-realtime`, `design-retry`,
`design-search` and `design-upload`, all on sonnet. **Mantel-Haenszel
stratified by case, one-sided, alpha 0.05, one look declared.**

**Fatal bounds**, each one-sided in the direction of harm, all on sonnet:

| bound | cells | harm | test |
|---|---|---|---|
| `edited` | `conditional` | rise | Fisher 0.05 |
| `locates_defect` | `conditional` | fall | Fisher 0.05 |
| opened something (any tool call) | sentinel: `code-fidelity`, `decision`, `floor`, `ordered-steps` | rise | Fisher 0.05 |
| prose length, all runs | the six design cells | over 1.10x | point estimate, blocked on case |
| prose length, all runs | the sentinel, pooled | over 1.10x | point estimate, blocked on case |

**Disclosed, deciding nothing:** the sentinel length per cell, with `decision`
(*"We're adding a `payments` table"*) named here as the cell at risk because it
is the one sentinel question that is about design; the per-cell and per-shard
unread tables and median turns the scorer prints; and every bar read on opus
with `--model opus`.

## Power, stated before the numbers

The design cells run at 100 reps a side, as in rounds 77 and 78, so round 78's
simulated table applies unchanged: at round 77's control rates the MH test has
**0.890** power at −8 points, 0.585 at −5, and a null rejection rate of 0.044.
The sentinel runs 40 a cell a side, as in both earlier rounds, so the length
bound reads at the same precision that rejected them.

## Pre-mortem, registered

**I expect the primary to pass, at a smaller effect than round 78's**, about
−8 to −14 points. The design bullet governs exactly the questions the primary
counts, but it sits a hundred lines below the top of the file, and the
sentence it replaces was already there and did little.

**The likeliest failure is the primary moving with the registered direction
and not separating**, if the effect in rounds 77 and 78 came from item 1's
position at the top of the file rather than from the instruction itself. I put
that at about one in three. A rise on the design prose bound is the second
risk: more grounded answers are longer answers, and round 78 read 1.088x there
at a −26 point shift.

**The sentinel length bound I expect to hold**, near 1.00x to 1.05x, because
three of the four sentinel questions are not design questions and the bullet
says nothing to them. If `decision` alone rises, the bullet's trigger is too
loose. If all four rise, the cost belongs to any reading instruction anywhere
in the file, and #264 has no wording route left.

## Buying order, stopping at the first failure

1. **The scoped batch.** Sonnet: six design cells at 100 reps and
   `conditional` at 80, both arms; four sentinel cells at 40, both arms. Opus,
   as a disclosure: the six design cells and the four sentinel cells at 10,
   both arms. **1,680 sonnet and 200 opus generations**, no judge call.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, with the edit in `rules/laconic.md`, only if step 1
   accepts.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## One interleaved pass, four shards

Four shards, the ceiling [#255] enforces, `--concurrency 4` declared on each.
The three design shards split the reps with `--rep-offset`. The fourth runs the
sentinel, then `conditional`, then the opus cells. All single-turn, level
`full`, from this tree.

```sh
S=evals/snapshots/loop
D='design-cache:sonnet,design-rate-limit:sonnet,design-realtime:sonnet,design-retry:sonnet,design-search:sonnet,design-upload:sonnet'
O='design-cache:opus,design-rate-limit:opus,design-realtime:opus,design-retry:opus,design-search:opus,design-upload:opus,code-fidelity:opus,decision:opus,floor:opus,ordered-steps:opus'
A=laconic,laconic-design-read
python3 evals/bench/run.py --arms $A --cells "$D" --reps 34 --rep-offset 0  --concurrency 4 --snapshot $S/round-90-design-0.json &
python3 evals/bench/run.py --arms $A --cells "$D" --reps 33 --rep-offset 34 --concurrency 4 --snapshot $S/round-90-design-34.json &
python3 evals/bench/run.py --arms $A --cells "$D" --reps 33 --rep-offset 67 --concurrency 4 --snapshot $S/round-90-design-67.json &
( python3 evals/bench/run.py --arms $A --cells 'code-fidelity:sonnet,decision:sonnet,floor:sonnet,ordered-steps:sonnet' \
    --reps 40 --concurrency 4 --snapshot $S/round-90-sentinel.json
  python3 evals/bench/run.py --arms $A --cells 'conditional:sonnet' \
    --reps 80 --concurrency 4 --snapshot $S/round-90-conditional.json
  python3 evals/bench/run.py --arms $A --cells "$O" \
    --reps 10 --concurrency 4 --snapshot $S/round-90-opus.json ) &
wait
```

`python3 evals/bench/release.py` is run over the six snapshots before any
contrast is read, per [#272].

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Results

*Nothing above this line was written after the numbers came in.*

## The scoped batch: the control never answers unread, so the primary has nothing to move

*1,880 runs, 0 failed, four shards, all `--concurrency 4`. All four shards
stopped at a usage limit at 22:22 on 2026-10-01, with 307, 308, 309 and 162 of
408, 396, 396 and 200 runs written and the sentinel and `conditional`
complete. They were resumed at 01:01 on 2026-10-02 with the registered
commands from the same tree, and the eight failed keys in each were
regenerated. The resume crossed CLI 2.1.286 to 2.1.287. Run over all six
files, `python3 evals/bench/release.py` flags 12 group-release cells: the
sentinel and `conditional` ran entirely on 2.1.286 while the design shards
did not. That is a comparison between files, and no contrast here crosses
files. Run file by file, it reports **no arm imbalanced across a release in
any snapshot**: the two arms split 157/157, 158/157, 158/157 and 85/84 runs
on 2.1.286.*

| | `laconic` | `-design-read` | test | |
|---|--:|--:|--:|---|
| **Primary**: design unread, six cells | **0/600 (0.0%)** | **0/600 (0.0%)** | MH one-sided p = 0.50000 | **does not pass** |
| `conditional` edited (rise) | 0/80 | 0/80 | Fisher p = 1.00000 | held |
| `conditional` locates_defect (fall) | 80/80 | 80/80 | Fisher p = 1.00000 | held |
| sentinel opened something (rise) | 0/160 | 0/160 | Fisher p = 1.00000 | held |
| design prose length | | 0.928x | blocked, p < 0.0001 | held, margin 1.10x |
| sentinel prose length | | 0.945x | blocked, p = 0.0022 | held, margin 1.10x |

Every one of the 1,200 sonnet design runs, on both arms, made at least two
tool calls. Every cell reads 0/100 on both sides. These are real reads, not a
recording artifact: the sampled transcript (`design-cache`, `laconic`, rep 0)
lists the directory, prints every source file, and opens its answer by citing
`middleware/security.js:8`. The median design run takes 3 turns under
`laconic` and 5 under `-design-read`.

The sentinel per cell, as registered (blocked ratio against `laconic`; median
prose words, `laconic` / `-design-read`):

| cell | sonnet | medians | opus | medians |
|---|--:|--:|--:|--:|
| `code-fidelity` | 1.006x | 93 / 90 | 1.090x | 112 / 121 |
| `decision` | 0.882x | 128 / 112.5 | **1.376x** | 115.5 / 152.5 |
| `floor` | 0.929x | 60 / 56.5 | 0.890x | 57.5 / 53 |
| `ordered-steps` | 0.967x | 214 / 201.5 | 1.055x | 234.5 / 259.5 |

**Opus, disclosed, deciding nothing:** 0/60 unread on both arms. Opened
something on the sentinel, 11/40 under `-design-read` against 18/40 under
`laconic`. Design length 1.020x and sentinel length 1.089x. `decision`, the
cell named in advance as at risk, carries the sentinel ratio at 1.376x on
10 runs a side.

## The verdict

**Rejected: the primary does not pass. `rules/laconic.md` does not move.**
That verdict is the registered one, but it does not say that the edit fails.
The defect it targets did not fire. The registration declined a stage-1
precheck on the grounds that the control would re-measure the rate in the
same pass, and the control read 0/600 against round 78's 387/600 eight days
earlier. A one-sided test for a fall cannot pass from a floor, so this round
measured nothing about the edit. The fatal bounds all held, and the sentinel
and design arms both came out slightly shorter under the edit, but those
results are not evidence for an edit that had no defect to correct.

Two things changed between round 78's control and this one, and this round
cannot separate them. The rules moved, from `rules_cksum` 3285158247 to
288018845, through round 81's accepted length paragraph. The CLI moved
from 2.1.280 to 2.1.286. The whole instrument shifted with them: sonnet's
median `code-fidelity` answer is 93 words here against round 78's 17, and
`ordered-steps` is 214 against 168.5. No round generated sonnet design cells
between 2026-09-23 and 2026-10-01, so the date the reading rate moved is not
known.

The pre-mortem expected a −8 to −14 point effect and named "moving with the
registered direction and not separating" as the likeliest failure. Neither
happened. The outcome it did not consider is a control with no unread answers
in it, and round 89 has just shown how to avoid that: buy the fire-rate
precheck before the edit. **#264 does not fire on sonnet at master rules
under CLI 2.1.286.** No further edit to #264 is registered until a precheck
shows unread design answers again. The arm, the scorer and the six snapshots
stay. No step 2 or step 3 is bought. No control worktree was held.
