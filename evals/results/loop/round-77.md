# Round 77: the reading instruction, hoisted out of the broken-thing check

**Registration. Nothing below the results line has been computed**, with the
exception of the round 63 figures quoted from [round 63](round-63.md), which is
merged, and the power table simulated from them. This file, the rebuilt arm,
its `BUILT-FROM.json` entry, the scorer and one corrected test are committed in
one commit before any generation, following [round 38](round-38.md) through
[round 76](round-76.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_read_hoist.py evals/snapshots/loop/round-77-*.json
```

`bash tools/candidate-due.sh` exits 0: [round 76](round-76.md) carried a
candidate, so round 77 was permitted to measure. It carries one anyway, because
[round 63](round-63.md) generated this exact contrast and its registered
sequence never let it be tested.

## Why this round exists

[#264] says the pre-action check costs sonnet reading on design questions: in
[round 56](round-56.md) the share of `design-*` answers that opened no file
rose 7.8 points under the check. On this family not opening the fixture is the
documented mechanism of failure ([#88], [`design-discrimination.md`](design-discrimination.md)).
The proposed cause is that item 1's trigger is a broken thing, a design
question has none, and the clause that still reads as in force is *do not
act*.

Round 63 generated three arms in one interleaved pass, sonnet, six `design-*`
cells, 70 reps an arm:

| arm | unread |
|---|--:|
| `laconic-precheck-off` | 226/420 (53.8%) |
| `laconic` (shipped) | 232/420 (55.2%) |
| `laconic-precheck-read` | **202/420 (48.1%)** |

Its gate 1, *does the check cost reading in this window*, did not fire, so by
its own registered sequence gate 2, `-read` against `laconic`, was never
tested. Read post hoc it is −7.1 points. That figure was selected after the
fact from a three-arm table, so this round treats it as a lead and powers
against less.

The round-63 question — whether the shipped check costs reading at all — is
not re-asked. The claim here is narrower and is the one that would ship:
**the reworded check reads more than the shipped one.**

## The edit

`rules/laconic.md`, item 1 of the pre-action check, above every level marker:

```diff
 One check before acting, and two before sending:

-1. Is the question about something that is broken? Diagnosing it is the
-   answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+1. Before writing, read what grounds the answer. If the question is about
+   something that is broken, diagnose it rather than fix it: name what is
+   wrong and leave the fix for the user to ask for.
 2. What is the smallest set of claims that fully answers this?
 3. Is anything here something the user did not ask for?
```

Word for word, this is the block round 63 wrote. The reading instruction
becomes unconditional and the not-acting clause stays bound to the broken-thing
trigger. The swap is word-matched: the `full` slice is 1,143 words on both
sides.

**It is tested as an arm, and `rules/laconic.md` does not move until step 1
accepts.** `evals/arms/laconic-precheck-read.md` is rebuilt from the live
`full` slice at `rules_cksum` **3285158247** with only this block swapped;
`tests/test_bench.py` checks that by exact equality against the hook's output.
Both arms are `--append-system-prompt` texts, so `run.py` samples them at
adjacent moments inside each process: one snapshot per shard, one
`rules_cksum`, one CLI trajectory shared by both sides. No control worktree is
needed, so none is held in `/tmp`. On an accept, the same block goes into
`rules/laconic.md` and `rules/dist/*.md` is regenerated before step 2. The
edit-side `rules_cksum` then becomes **2605215817**.

### The claim

> Hoisting *"read what grounds the answer"* out of item 1's broken-thing
> conditional should move the share of `design-*` answers on sonnet that open
> no file **down**.

## The bars

All endpoints are deterministic, and no judge call is bought in step 1.

**Primary.** Unread rate, `-read` below `laconic`, on `design-cache`,
`design-rate-limit`, `design-realtime`, `design-retry`, `design-search` and
`design-upload`, all on sonnet. The test is **Mantel-Haenszel stratified by
case, one-sided, alpha 0.05, with one look declared**. The within-case
permutation is printed beside it as the exact check on the approximation. These
are round 63's six cells, excluding `design-alerting` and `design-audit-log`
for round 63's mechanical reason: they read 0/40 unread on both sides of round
56.

**Fatal bounds**, each one-sided in the direction of harm. Any one of them
firing rejects an edit whose primary passed.

| bound | cells | harm | test | why |
|---|---|---|---|---|
| `edited` | `conditional`, sonnet | rise | Fisher 0.05 | [Round 65](round-65.md)'s endpoint for this check's not-acting clause. The rewording moves that clause into a subordinate sentence. |
| `locates_defect` | `conditional`, sonnet | fall | Fisher 0.05 | That endpoint's content bound. |
| opened something | sentinel: `code-fidelity`, `decision`, `floor`, `ordered-steps`, sonnet | rise | Fisher 0.05 | An unconditional reading instruction where there is nothing to read. Round 63 read 0/160 on every arm. |
| prose length, all runs | the six design cells | over 1.10x | point estimate, blocked on case | The rule is a brevity rule. Round 63 read 1.057x. |
| prose length, all runs | the sentinel, pooled | over 1.10x | point estimate, blocked on case | Round 63 read **1.103x at p = 0.0004** here, as a disclosure. |

The last row is promoted from a disclosure to a fatal bound. It is the one
signal round 63 said any round proposing this wording would inherit. Kimi,
through `tools/consult.sh`, asked for it to be fatal, pooled over the four
cells, and at the same 1.10x margin as the design cells. DeepSeek asked for it
to be fatal and pooled, but at 1.12x, arguing that 1.10x sits on round 63's own
post-hoc point. **1.10x is kept.** A looser margin chosen because the last
reading sat just above the tighter one would be a margin fitted to the data it
is meant to judge.

## Power, stated before the numbers

> **Computed 2026-09-23, before this registration.** 3,000 simulated draws
> per figure at `laconic`'s round-63 per-cell rates, scored by the MH test
> registered above, seed 77.

| reps per cell | per arm | null | −3 pts | −5 pts | −7.1 pts |
|--:|--:|--:|--:|--:|--:|
| 70 | 420 | 0.055 | 0.233 | 0.433 | 0.654 |
| **100** | **600** | 0.050 | 0.280 | **0.566** | **0.818** |
| 120 | 720 | 0.052 | 0.309 | 0.607 | 0.866 |
| 150 | 900 | 0.057 | 0.355 | 0.697 | 0.935 |

```sh
python3 - <<'EOF'
import random, sys
sys.path.insert(0, "evals/pilot")
from score_precheck import mantel_haenszel
rng = random.Random(77)
base = [32/70, 30/70, 38/70, 39/70, 38/70, 55/70]
for reps in (70, 100, 120, 150):
    row = []
    for d in (0, -0.03, -0.05, -0.071):
        h = 0; N = 3000
        for _ in range(N):
            t = []
            for p in base:
                a = sum(rng.random() < max(p + d, 0) for _ in range(reps))
                c = sum(rng.random() < p for _ in range(reps))
                t.append((a, reps - a, c, reps - c))
            z, _ = mantel_haenszel(t)
            h += z < -1.6449
        row.append("%+.3f:%.3f" % (d, h / N))
    print(reps, "  ".join(row))
EOF
```

**The round buys 100 reps per cell, 600 per arm.** That is 0.82 power at round 63's point and 0.57 at
−5. Going to 150 reps would buy 0.70 at −5 for half as many generations again.
The replication in step 3 is what answers the winner's curse. Its job is to
reproduce an effect, while the primary's job is to find one, and spending the
difference on the primary would pay twice for the same protection.

### What was not adopted from the consultation

- **DeepSeek: make the primary non-inferiority**, and ship `-read` unless it
  reads worse than `laconic` by more than 2 to 3 points. That would ship a
  rules edit on no evidence that it does anything, and every word in this file
  has to earn its place. The claim is superiority or nothing.
- **Kimi: add a minimum effect of 4 points as a co-primary.** A co-primary
  threshold lowers power against exactly the effect sizes the table above shows
  are likely, and replication already guards against a small true effect
  passing on a lucky draw.
- **Kimi: add lite and ultra arms at 20 reps.** Item 1 is byte-identical at all
  three levels, and a 20-rep diagnostic arm could not distinguish anything this
  round's primary cannot. It is disclosed instead: **this round measures
  `full` only.**

Codex did not answer within 240 seconds.

## Pre-mortem, registered

**I expect the primary to pass but not by much.** Round 63's −7.1 came from a
table the arm was not selected from, but three arms is little room for
selection, and 202 against 232 is a whole-round movement across four of six
cells rather than one cell carrying it. My expectation is a true effect of
about −4 to −5 points. At that size this round separates a little more often
than not.

**The failure I consider likeliest is not the primary but the sentinel prose
bound.** Round 63 measured 1.103x there with the same text and nothing
suggests it was a fluke — p = 0.0004 over 160 runs a side. If it reproduces at
its point the edit rejects on a fatal counter with its target passed, and I put
that at roughly even odds. The mechanism would be that "Before writing, read
what grounds the answer" reads as a general licence to ground the answer, and
where there is no file the grounding is done in prose.

**The class I do not expect is the point estimate moving against the registered
direction.** An unconditional reading instruction is not a licence not to
read.

**`conditional` edits I expect to hold.** The not-acting clause is still
present and still bound to the trigger that `conditional` fires, and round 76's
control read 3/80 there.

## Buying order, stopping at the first failure

1. **The scoped batch.** Six design cells at 100 reps, four sentinel cells at
   40, `conditional` at 80, both arms, all sonnet: **1,680 generations**, no
   judge call.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, with the edit in `rules/laconic.md`, only if step 1 accepts.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## One interleaved pass, four shards

Four shards, the ceiling [#255] enforces, with `--concurrency 4` declared on
each. The three design shards split the reps with `--rep-offset`, so no two
share a generation key. The fourth runs the sentinel and then `conditional`,
one after the other. All four run at level `full` from this tree, and all
cases are single-turn, so no `--turn-delivery` applies.

```sh
S=evals/snapshots/loop
D='design-cache:sonnet,design-rate-limit:sonnet,design-realtime:sonnet,design-retry:sonnet,design-search:sonnet,design-upload:sonnet'
A=laconic,laconic-precheck-read
python3 evals/bench/run.py --arms $A --cells "$D" --reps 34 --rep-offset 0  --concurrency 4 --snapshot $S/round-77-design-0.json &
python3 evals/bench/run.py --arms $A --cells "$D" --reps 33 --rep-offset 34 --concurrency 4 --snapshot $S/round-77-design-34.json &
python3 evals/bench/run.py --arms $A --cells "$D" --reps 33 --rep-offset 67 --concurrency 4 --snapshot $S/round-77-design-67.json &
( python3 evals/bench/run.py --arms $A --cells 'code-fidelity:sonnet,decision:sonnet,floor:sonnet,ordered-steps:sonnet' \
    --reps 40 --concurrency 4 --snapshot $S/round-77-sentinel.json
  python3 evals/bench/run.py --arms $A --cells 'conditional:sonnet' \
    --reps 80 --concurrency 4 --snapshot $S/round-77-conditional.json ) &
wait
```

`python3 evals/bench/release.py` is run over the five snapshots before any
contrast is read, per [#272]. Both arms share every shard, so a release
boundary cannot fall between them. The audit checks that.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Results

*Nothing above this line was written after the numbers came in.*
