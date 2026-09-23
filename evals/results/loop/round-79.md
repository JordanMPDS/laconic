# Round 79: the offer to fix, at the size round 76 said it needs

**Registration. Nothing below the results line has been computed**, with the
exception of round 76's figures, which are merged, and the power tables
simulated from them. This file, the edit, the regenerated `rules/dist/*.md`
and the scorer's two new bounds are committed in one commit before any
generation, following [round 38](round-38.md) through [round 78](round-78.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_offer_fix.py --assay-min 6 \
  --control evals/snapshots/loop/round-79-control-*.json \
  --edit    evals/snapshots/loop/round-79-edit-*.json
```

`bash tools/candidate-due.sh` exits 0: [round 78](round-78.md) carried a
candidate, so round 79 was permitted to measure. It carries one.

## Why this round exists

[Round 76](round-76.md) tested this edit on [#113] and was **inconclusive**:
its control read 3/80 turn-3 offers against a registered assay of 4/80, and the
edit side read 0/80 (p = 0.12264). Its verdict sized the round that could
decide it — at the measured 3.8%, a perfect edit separates with P = 0.175 at
80 a side and 0.955 at 240 — and named the condition on a re-registration:

> A re-registration at 240 a side would have to carry those bounds with power
> of their own, not the ceiling they had here.

"Those bounds" are the two that moved in the harm direction without firing:
turn-3 file writes 3 → 6 of 80, and `conditional` edits 3 → 7 of 80. This is
that re-registration. Round 76's snapshots are **not pooled** into it: its
alpha is spent, and adding its 80 a side to this round's would be testing the
same hypothesis twice at one alpha.

## The edit

Round 76's, byte for byte. `rules/laconic.md`, item 1 of the pre-action check,
above every level marker so it reaches `lite`, `full` and `ultra` alike:

```diff
 1. Is the question about something that is broken? Diagnosing it is the
    answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+   wrong, and leave the fix for the user to ask for. Do not offer it
+   either: no "Would you like me to fix it?".
```

The `full` slice goes from 1,143 to 1,156 whitespace-separated words and
`rules_cksum` from **3285158247** to **694516902**, the same pair round 76
recorded, so master's rules have not moved underneath the comparison.

### The claim

> Appending *"Do not offer it either: no 'Would you like me to fix it?'"* to
> item 1 of the pre-action check should move the share of laconic
> `edit-service` runs whose turn 3 closes with a closing offer **down**, on
> haiku.

### Why the same wording

Kimi, through `tools/consult.sh`, argued for rewording: turn-3 writes going 3
→ 6 is the pre-mortem's named failure in the data, so re-running the text
"increases precision around a known bad outcome". Not adopted. 3 → 6 at 80 a
side is p = 0.24753; it is the direction the pre-mortem named, not the bound
firing, and a round that rewords on it throws away the one clean reading this
round can produce of whether the named failure is real. If a write bound fires
here, that is the evidence a rewording would be written from. DeepSeek made
the same argument.

## The bars, in order

All endpoints are deterministic. No judge call is bought in step 1.

**Assay.** The control side's laconic haiku turn-3 offer count is at least
**6 of 240** (2.5%). Round 76 measured 3.8%. Below the assay the round is
**inconclusive**, the edit is reverted and nothing ships.

**Primary.** Laconic haiku `edit-service` runs whose turn 3 carries a
`metrics.closing_offers` hit, edit side below control, **one-sided Fisher at
alpha 0.05, one look declared.** Every hit on both sides is printed verbatim and
hand-read.

**Fatal bounds**, each a one-sided Fisher at 0.05 in the direction that is harm.
Any one firing rejects an edit whose primary passed. The first six are round
76's; the last two are new.

| bound | cell | harm direction | round 76 read |
|---|---|---|---|
| turn-3 file writes | `edit-service`, haiku | rise | 3 → 6 of 80 |
| instructed-turn file writes | `edit-service`, haiku | fall | 320 → 320 of 320 |
| turn 3 names ROLLBACK | `edit-service`, haiku | fall | 80 → 80 of 80 |
| turn 3 calls a tool | `edit-service`, haiku | fall | 28 → 37 of 80 |
| `edited` | `conditional`, sonnet | rise | 3 → 7 of 80 |
| `locates_defect` | `conditional`, sonnet | fall | 80 → 77 of 80 |
| **pooled unasked fixes**: turn-3 writes plus `conditional` edits | both | rise | 6 → 13 of 160 |
| **turn 3 offers or writes a file** | `edit-service`, haiku | rise | 6 → 6 of 80 |

**The pooled unasked-fix bound is DeepSeek's**, through `tools/consult.sh`:
`edit-service` turn-3 writes and `conditional` edits are the same harm — a
mutation nobody asked for — on two cells, and pooling them doubles the
denominator at the same cost. It is the power the verdict of round 76 asked
for. Scored over round 76's merged snapshots before this registration, it reads
6 → 13 of 160 at p = 0.07713: closer to firing than either component, which is
the reason it is registered and also a reason this round may reject. The two component bounds stay, so a rise concentrated on one
cell is still seen on its own.

**The offer-or-write bound is the total the two moves compete for.** Round 76's
pre-mortem read offering and fixing as substitutes on turn 3. A rise in this
count means the edit bought fewer offers with more unasked action than it
removed. It cannot catch pure substitution — six offers becoming six writes
leaves it flat — which is what the turn-3 write bound and the pooled bound are
for.

### What was not adopted from the consultation

Kimi proposed making "turn 3 offers **or** writes" the **primary**. Rejected on
DeepSeek's argument: as a primary it is blind to exactly the relocation the
pre-mortem fears, since an edit that turns every offer into a write reads flat
and would be scored as doing nothing rather than as harm. It is kept above as a
bound in the rise direction, which is the one reading of it that is not blind.

Kimi also proposed a new rule line forbidding writes on diagnose-only turns.
That is a different edit — item 1 already says "fixing it is not" — and would
be its own round.

Codex did not answer within 240 seconds.

## Power, stated before the numbers

Simulated, 3,000 draws a point, seed 79, 240 runs a side.

**Primary, requiring the assay and the primary:**

| control rate | edit rate | P(accept on the primary) |
|--:|--:|--:|
| 3.75% | 0% | 0.884 |
| 3.75% | 1% | 0.513 |
| 2.5% | 0% | 0.561 |
| 5% | 0% | 0.984 |
| 5% | 1.25% | 0.693 |
| 3.75% | 3.75% (null) | 0.031 |

**Rise bounds, detecting harm:**

| bound | control | edit | P(fires) |
|---|--:|--:|--:|
| one cell, 240 a side | 3.75% | 7.5% | 0.498 |
| one cell, 240 a side | 3.75% | 8.75% | 0.698 |
| one cell, 240 a side | 3.75% | 10% | 0.831 |
| pooled, 480 a side | 3.75% | 7.5% | **0.781** |
| pooled, 480 a side | 3.75% | 6.25% | 0.497 |
| any, null | 3.75% | 3.75% | 0.03 |

A doubling of unasked fixes on both cells is caught about four times in five
by the pooled bound; on one cell alone, about half the time. That is the
bound's honest reach. Raising it to 0.8 on a single cell would need about 500
a side, which is not bought here.

```sh
python3 - <<'EOF'
import random, sys
sys.path.insert(0, "evals/bench")
from report import _fisher_upper_tail as f
rng = random.Random(79)
def b(p, n): return sum(rng.random() < p for _ in range(n))
for pc, pe in ((.0375, 0), (.0375, .01), (.025, 0), (.05, 0), (.05, .0125), (.0375, .0375)):
    h = 0
    for _ in range(3000):
        c, e = b(pc, 240), b(pe, 240)
        h += c >= 6 and f(c, 240, e, 240) < .05
    print("primary", pc, pe, round(h / 3000, 3))
for n, pc, pe in ((240, .0375, .075), (240, .0375, .0875), (240, .0375, .1),
                  (480, .0375, .075), (480, .0375, .0625)):
    h = 0
    for _ in range(3000):
        c, e = b(pc, n), b(pe, n)
        h += f(e, n, c, n) < .05
    print("bound", n, pc, pe, round(h / 3000, 3))
EOF
```

## Pre-mortem, registered

**I expect the primary to pass.** Round 76's edit side read 0/80 where its
control read 3/80, and nothing about the text has changed. The likeliest
failure of the primary is the same as last time: the control landing low. At
2.5% the assay passes and the primary has only 0.56 power, so a control near
the assay line is the outcome I would bet on after a pass.

**If it rejects, I expect it to be a fatal bound on an edit whose primary
passed, and specifically the pooled unasked-fix bound.** Round 76's two rises
were both in the fix direction and on different cells, which is exactly the
shape a pooled bound sees before either component does. I put that at about
one in three. I do not expect ROLLBACK, the instructed-turn writes or
`locates_defect` to move; all three sat at or near a ceiling.

**I do not expect the point estimate to move against the registered
direction.**

## Buying order, stopping at the first failure

1. **The scoped batch.** `edit-service` on haiku, five turns, and
   `conditional` on sonnet, 240 reps a side, two sides: **2,880 generations**
   (2,400 haiku turn calls, 480 sonnet), no judge call.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, only if step 1 accepts.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a worktree at
`master`, both reading cases from this tree's `evals/pilot` and writing
snapshots here, so era and CLI release cancel between the sides
([round 38](round-38.md)). Four shards, the ceiling [#255] enforces,
`--concurrency 4` on each, `--turn-delivery plugin`, level `full`.

```sh
git worktree add /tmp/laconic-control master
PILOT=$PWD/evals/pilot
CELLS='edit-service:haiku,conditional:sonnet'
for off in 300 420; do
  python3 evals/bench/run.py --arms laconic --cases-dir "$PILOT" --cells "$CELLS" \
    --reps 120 --rep-offset $off --turn-delivery plugin --concurrency 4 \
    --snapshot evals/snapshots/loop/round-79-edit-$off.json &
  (cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
    --cases-dir "$PILOT" --cells "$CELLS" --reps 120 --rep-offset $off \
    --turn-delivery plugin --concurrency 4 \
    --snapshot "$OLDPWD/evals/snapshots/loop/round-79-control-$off.json") &
done; wait
```

`--rep-offset 300` starts above every key round 76 and the pilot used (0 to 9
and 100 to 179). `python3 evals/bench/release.py` is run over the four
snapshots before any contrast is read, per [#272], and the control worktree is
removed when the round is scored.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Results

*Nothing above this line was written after the numbers came in.*
