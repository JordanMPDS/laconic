# Round 78: the reading instruction, scoped to a workspace with files

**Registration. Nothing below the results line has been computed**, except the
round 77 figures quoted from [round 77](round-77.md), which is merged, and the
power table simulated from them. This file, the new arm, its `BUILT-FROM.json`
entry, the scorer's `--edit-arm` flag and the tests that pin the arm are
committed in one commit before any generation, following [round 38](round-38.md)
through [round 77](round-77.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_read_hoist.py --edit-arm laconic-precheck-scoped \
  evals/snapshots/loop/round-78-*.json
```

`bash tools/candidate-due.sh` exits 0: round 77 carried a candidate. Round 78
carries one too, the successor round 77's verdict named.

## Why this round exists

[Round 77](round-77.md) made the reading instruction in item 1 of the
pre-action check unconditional. On sonnet `design-*` questions the share of
answers that opened no file fell from 396/600 to 299/600, **−16.2 points,
MH p < 0.00001**, with all six cells moving the same way. On design questions
not opening the fixture is the documented mechanism of failure ([#88]). The
edit was rejected on a fatal bound. Prose length on the four no-fixture
sentinel cells rose **1.111x** against a 1.10x margin, p = 0.0006, with all
four cells up. [Round 63](round-63.md) had read 1.103x on the same cells.

Round 77's verdict named the successor: keep the reading instruction, but
scope it so that it has nothing to say where there is nothing to read. The
sentinel runs in an empty scratch directory and asks questions whose answer
depends on no file (`What does git restore --staged do?`). The design cases
run inside a fixture repository and name no file either (`how would caching
be built?`). So the scope cannot be "a question that names a file". It has to
be whether the answer depends on the workspace's files.

## The edit

`rules/laconic.md`, item 1 of the pre-action check, above every level marker:

```diff
 One check before acting, and two before sending:

-1. Is the question about something that is broken? Diagnosing it is the
-   answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+1. Does the answer depend on files in this workspace? Read them first. If
+   something is broken, diagnose it rather than fix it: name what is wrong
+   and leave the fix for the user to ask for.
 2. What is the smallest set of claims that fully answers this?
 3. Is anything here something the user did not ask for?
```

It differs from round 77's block in two places. The reading sentence becomes
a question scoped to the workspace, and the broken-thing clause is shortened
from "If the question is about something that is broken" to "If something is
broken". The shortening keeps the arm **word-matched to the shipped slice**:
the `full` slice is 1,143 words on both sides, as it was in round 77, so a
length difference cannot come from the file getting longer.

**It is tested as an arm, and `rules/laconic.md` does not move until step 1
accepts.** `evals/arms/laconic-precheck-scoped.md` is built from the live
`full` slice at `rules_cksum` **3285158247** with only this block swapped, and
`tests/test_bench.py` checks that by exact equality against the hook's output.
Both arms go through `--append-system-prompt`, so each shard samples them at
adjacent moments under one `rules_cksum` and one CLI trajectory. No control
worktree is needed.

### The claim

> Scoping item 1's reading instruction to *"files in this workspace"* should
> move the share of `design-*` answers on sonnet that open no file **down**,
> without the sentinel's prose length rising past 1.10x.

## The bars

These are round 77's bars, unchanged, scored by the same code with
`--edit-arm laconic-precheck-scoped`. All endpoints are deterministic, and no
judge call is bought in step 1.

**Primary.** Unread rate, `-scoped` below `laconic`, on `design-cache`,
`design-rate-limit`, `design-realtime`, `design-retry`, `design-search` and
`design-upload`, all on sonnet. **Mantel-Haenszel stratified by case,
one-sided, alpha 0.05, one look declared.** The within-case permutation is
printed beside it.

**Fatal bounds**, each one-sided in the direction of harm:

| bound | cells | harm | test |
|---|---|---|---|
| `edited` | `conditional`, sonnet | rise | Fisher 0.05 |
| `locates_defect` | `conditional`, sonnet | fall | Fisher 0.05 |
| opened something (any tool call) | sentinel: `code-fidelity`, `decision`, `floor`, `ordered-steps`, sonnet | rise | Fisher 0.05 |
| prose length, all runs | the six design cells | over 1.10x | point estimate, blocked on case |
| prose length, all runs | the sentinel, pooled | over 1.10x | point estimate, blocked on case |

**The opened-something bound stays "any tool call", although this wording
makes it likelier to fire.** A question asking whether the answer depends on
the workspace can be answered by listing the workspace, and on `decision`
("We're adding a `payments` table") or `ordered-steps` ("rotate *our* JWT
signing key") a model may reasonably look. Redefining the bound as "read a
file" before the round would be loosening a fatal counter because the new edit
is expected to strain it. A tool call spent on `What does git restore --staged
do?` in an empty directory is a real cost, so the bound keeps round 77's
definition.

### A disclosure arm, deciding nothing

`laconic-precheck-read`, round 77's arm, is generated beside the other two on
the sentinel cells only: 160 runs. Round 77's length cost came from one
window. This shows, in the same window, whether `-scoped` costs less prose
than `-read` did. It is printed as a disclosure and cannot accept or reject
anything.

## Power, stated before the numbers

> **Computed 2026-09-23, before this registration.** 2,000 simulated draws
> per figure at `laconic`'s round-77 per-cell rates (68, 59, 58, 62, 68 and
> 81%), scored by the MH test above, seed 78.

| reps per cell | per arm | null | −3 pts | −5 pts | −8 pts |
|--:|--:|--:|--:|--:|--:|
| **100** | **600** | 0.044 | 0.300 | 0.585 | **0.890** |

Round 77 measured −16.2 points. A scoped wording is expected to keep only part
of that, because the model has to judge that a design question depends on the
workspace before the instruction applies. At 100 reps the round has 0.89
power at half the round-77 effect.

## Consultation

`tools/consult.sh` was asked about the wording, whether the opened-something
bound should become "read a file", and whether to add `-read` as a third arm.
**None of the three targets answered** within 240 seconds (codex, deepseek and
kimi all timed out). Every decision above is this round's own, and none has an
outside origin to cite.

## Pre-mortem, registered

**I expect the primary to pass at a smaller effect than round 77's**, about
−6 to −10 points. The design prompts refer to a system ("product pages",
"/v1", "sellers") without naming files, so the model has to decide that the
answer depends on the workspace, and some of the time it will not.

**The likeliest failure is the opened-something bound, not the length bound.**
The question "does the answer depend on files in this workspace?" can be
answered by listing an empty directory, and on `decision` and `ordered-steps`,
whose prompts say "we're adding" and "our", I expect some runs to do it. At
0/160 on the control, about 5 runs on the edit side fire the bound. I put that
at about one in three. That would be a fatal counter rejecting an edit whose
target passed.

**The sentinel length bound I expect to hold**, near 1.03x to 1.06x. On a
question like `What does git restore --staged do?` the scoped question
answers itself "no", and nothing in the block then asks for more prose. If it
reads above 1.10x anyway, the length cost is a property of adding a reading
instruction rather than of its scope, and this line of edits is finished.

**`conditional` I expect to hold.** Its prompt names `pool.log` and `db.js`,
so the scoped question fires, and the not-acting clause is intact.

## Buying order, stopping at the first failure

1. **The scoped batch.** Six design cells at 100 reps and `conditional` at 80,
   on both arms; four sentinel cells at 40 on three arms. All sonnet:
   **1,840 generations**, no judge call.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, with the edit in `rules/laconic.md`, only if step 1 accepts.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## One interleaved pass, four shards

Four shards, the ceiling [#255] enforces, with `--concurrency 4` declared on
each. The three design shards split the reps with `--rep-offset`. The fourth
runs the sentinel on three arms and then `conditional` on two. All run at
level `full` from this tree, and all cases are single-turn.

```sh
S=evals/snapshots/loop
D='design-cache:sonnet,design-rate-limit:sonnet,design-realtime:sonnet,design-retry:sonnet,design-search:sonnet,design-upload:sonnet'
A=laconic,laconic-precheck-scoped
python3 evals/bench/run.py --arms $A --cells "$D" --reps 34 --rep-offset 0  --concurrency 4 --snapshot $S/round-78-design-0.json &
python3 evals/bench/run.py --arms $A --cells "$D" --reps 33 --rep-offset 34 --concurrency 4 --snapshot $S/round-78-design-34.json &
python3 evals/bench/run.py --arms $A --cells "$D" --reps 33 --rep-offset 67 --concurrency 4 --snapshot $S/round-78-design-67.json &
( python3 evals/bench/run.py --arms $A,laconic-precheck-read --cells 'code-fidelity:sonnet,decision:sonnet,floor:sonnet,ordered-steps:sonnet' \
    --reps 40 --concurrency 4 --snapshot $S/round-78-sentinel.json
  python3 evals/bench/run.py --arms $A --cells 'conditional:sonnet' \
    --reps 80 --concurrency 4 --snapshot $S/round-78-conditional.json ) &
wait
```

`python3 evals/bench/release.py` is run over the five snapshots before any
contrast is read, per [#272].

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Results

*Nothing above this line was written after the numbers came in.*
