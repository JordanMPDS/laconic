# Round 76: the offer to fix, named in the pre-action check

**Registration. Nothing below the results line has been computed**, with the
exception of the pilot figures quoted from
[`closing-edit-113.md`](closing-edit-113.md), which is merged, and the power
table simulated from them. This file, the edit, the regenerated
`rules/dist/*.md`, the scorer and one pilot symlink are committed in one commit
before any generation, following [round 38](round-38.md) through
[round 75](round-75.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_offer_fix.py \
  --control evals/snapshots/loop/round-76-control-*.json \
  --edit    evals/snapshots/loop/round-76-edit-*.json
```

`bash tools/candidate-due.sh` exits 0: [round 75](round-75.md) carried a
candidate, so round 76 was permitted to measure. It carries one, because the
pilot that merged today named an edit, a target cell and a size.

## Why this round exists

[#113] reports the `lite` rule against closing offers breaking on one turn of a
long editing session at `full`. [`closing-edit-113.md`](closing-edit-113.md)
built the regime and found the break in one place:

| laconic, `edit-service` | offers |
|---|--:|
| instructed turns 1, 2, 4, 5, both models | 0/80 |
| turn 3, sonnet | 0/10 |
| **turn 3, haiku** | **2/10** |

Both hits are the same sentence, closing the response:

> The fix is to catch the ROLLBACK error separately and not let it mask the
> original failure. **Would you like me to fix it?**

Turn 3 is the walk-through in an editing session: it finds a defect and does
not grant the edit. No arm writes a file on it (0 of 80 turn-3 responses), so
the offer is not accompanying volunteered work but replacing it. The shipped
pre-action check already names the right move on that turn — *"Diagnosing it is
the answer; fixing it is not"* — and [round 65](round-65.md) measured it cutting
the unasked edit sixfold. The pilot's reading is that the offer is where the
pressure goes once the edit is closed, and that the candidate belongs beside the
check rather than as a new terminal check in `lite`, where laconic is already at
0 of 80.

## The edit

`rules/laconic.md`, item 1 of the pre-action check, above every level marker so
it reaches `lite`, `full` and `ultra` alike:

```diff
 1. Is the question about something that is broken? Diagnosing it is the
    answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+   wrong, and leave the fix for the user to ask for. Do not offer it
+   either: no "Would you like me to fix it?".
```

Appended, not rewritten: the sentence round 65 measured is left byte for byte.
The `full` slice goes from 1,143 to 1,156 whitespace-separated words and
`rules_cksum` from **3285158247** to **694516902**.

### The claim

> Appending *"Do not offer it either: no 'Would you like me to fix it?'"* to
> item 1 of the pre-action check should move the share of laconic
> `edit-service` runs whose turn 3 closes with a closing offer **down**, on
> haiku.

The quoted fragment is the verbatim string haiku wrote, not a paraphrase of the
shape. That is a deliberate response to [round 75](round-75.md), whose clause
quoted *"The file says ..."* and left *"The file explicitly notes"* — one word
off — exactly where it was. Here the target is a fixed sentence rather than a
family, and the lite bullet already covers the family (*"Want me to...?"*).

## Where it goes, and why there

Item 1 rather than the `lite` closing-offer bullet. Under `plugin` delivery the
two placements are equally far from turn 3 — both arrive in the turn-1 slice,
and turn 3 carries only the one-line reminder — so the choice is about which
rule the model is applying when it writes the sentence. The offer is produced on
the broken-thing turn, completing the move item 1 half-forbids, and the lite
bullet was present in the pilot and was written past. DeepSeek made the same
argument through `tools/consult.sh`, adding that item 1 demonstrably reaches
turn 3 already: no arm on either model wrote a file there.

## The bars, in order

All endpoints are deterministic. No judge call is bought in step 1.

**Assay.** The control side's laconic haiku turn-3 offer count is at least
**4 of 80**. The pilot's 2/10 has a Wilson interval of 5.7% to 51.0%, and if
the control re-measures near the bottom of it the rate this edit targets is not
there to cut. Below the assay the round is **inconclusive**, the edit is
reverted and nothing ships — a round that could not have separated is not
evidence the edit fails, and is not evidence it works.

**Primary.** Laconic haiku `edit-service` runs whose turn 3 carries a
`metrics.closing_offers` hit, edit side below control, **one-sided Fisher at
alpha 0.05, one look declared.** Every hit on both sides is printed verbatim and
hand-read; the detector measured 30 of 30 precision before the pilot and the
pilot's hand-read found no miss in 100 turn-responses.

**Fatal bounds**, each a one-sided Fisher at 0.05 in the direction that is harm.
Any one firing rejects an edit whose primary passed.

| bound | cell | harm direction | why |
|---|---|---|---|
| turn-3 file writes | `edit-service`, haiku | rise | The obvious way to stop offering to fix is to fix. That is [#116]'s harm, and the pilot has it at 0/80. |
| instructed-turn file writes | `edit-service`, haiku | fall | Turns 1, 2, 4 and 5 grant the edit; the edit must not read as "never fix". Pilot 159/160. |
| turn 3 names ROLLBACK | `edit-service`, haiku | fall | The defect the fixture hides. "Don't offer the fix" can collapse into "say less about the defect". Pilot 20/20, a ceiling, so this detects a fall only. |
| turn 3 calls a tool | `edit-service`, haiku | fall | The edit must not buy its number by not reading ([#46], [#138]). Pilot 3/10 on haiku. |
| `edited` | `conditional`, sonnet | rise | [Round 65](round-65.md)'s endpoint for the same check, 3.8% under the shipped text. |
| `locates_defect` | `conditional`, sonnet | fall | That endpoint's content bound. |

The ROLLBACK and tool bounds came from DeepSeek through `tools/consult.sh`.

## Power, stated before the numbers

Simulated, 4,000 draws a point, seed 76, 80 runs a side, requiring the assay
*and* the primary:

| control rate | edit rate | P(accept on the primary) |
|--:|--:|--:|
| 20% | 0% | 1.000 |
| 20% | 5% | 0.871 |
| 10% | 0% | 0.907 |
| 10% | 2% | 0.591 |
| 5% | 0% | 0.367 |
| 20% | 20% (null) | 0.036 |

```sh
python3 - <<'EOF'
import random, sys
sys.path.insert(0, "evals/bench")
from report import _fisher_upper_tail as f
rng = random.Random(76)
for pc, pe in ((.2, 0), (.2, .05), (.1, 0), (.1, .02), (.05, 0), (.2, .2)):
    h = 0
    for _ in range(4000):
        c = sum(rng.random() < pc for _ in range(80))
        e = sum(rng.random() < pe for _ in range(80))
        h += c >= 4 and f(c, 80, e, 80) < .05
    print(pc, pe, round(h / 4000, 3))
EOF
```

**80 a side, not the pilot's suggested 60.** At 60 a side a perfect edit
against a true 10% control separates about three times in four; at 80 about
nine in ten. Below a 10% control no affordable round separates, which is what
the assay is for.

### What was not adopted from the consultation

DeepSeek recommended making the primary **presence** on the edit side — accept
on 0 of 60 — as the pilot did. That was right for the pilot, whose null was a
measured zero on `drift-service`. It is wrong for a candidate round: the
control here is the same cell at master rules, and if it also reads 0 of 80 an
accept on presence would ship an edit that did nothing measurable. The assay is
the version of that concern this round keeps: a low control rate makes the
round inconclusive, not accepted.

Codex and Kimi did not answer within 240 seconds.

## Pre-mortem, registered

**I expect this to pass, with the edit side near zero.** The target is a single
fixed sentence, it is quoted verbatim, and it sits in the check whose other
half already holds on this exact turn — item 1 is why nothing writes a file on
turn 3. That is the strongest position a prohibition in this file has had: the
closing-offer bullet, which is the same shape of rule, runs 3.5% against 13.1%
at p = 8.6e-18.

**The way I most expect it to fail is the assay.** The pilot's 2/10 is a draw,
and a haiku rate of 5% at master would leave the round unable to separate
anything. That is inconclusive, not a rejection class, and I judge it the
likeliest outcome after a pass.

**The rejection class I would bet on, if it rejects, is a fatal counter on an
edit whose target passed — specifically turn-3 writes.** Round 65's reading is
that offering and fixing compete for the same turn; closing one off pushes
towards the other. A haiku that is told neither to fix nor to offer has one
move left, which is to stop, and I expect it to take that move. But if it does
not, the write rate is where it shows.

**I do not expect the point estimate to move against the registered
direction.** A sentence that names the exact offer is not a licence for it.

## Buying order, stopping at the first failure

1. **The scoped batch.** `edit-service` on haiku, five turns, and `conditional`
   on sonnet, 80 reps a side, two sides: **960 generations** (800 haiku turn
   calls, 160 sonnet), no judge call.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, only if step 1 accepts.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a `master`
worktree, both reading cases from this tree's `evals/pilot` — byte-identical to
master's apart from the `conditional` symlink this commit adds, which points at
the scored case — and both writing snapshots here, so era and CLI release cancel
between the sides ([round 38](round-38.md)). Four shards, the ceiling [#255]
enforces, `--concurrency 4` declared on each, `--turn-delivery plugin` because
this is a claim about the product, level `full`, the level [#113] reports.

```sh
git worktree add /tmp/laconic-control master
PILOT=$PWD/evals/pilot
CELLS='edit-service:haiku,conditional:sonnet'
for off in 100 140; do
  python3 evals/bench/run.py --arms laconic --cases-dir "$PILOT" --cells "$CELLS" \
    --reps 40 --rep-offset $off --turn-delivery plugin --concurrency 4 \
    --snapshot evals/snapshots/loop/round-76-edit-$off.json &
  (cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
    --cases-dir "$PILOT" --cells "$CELLS" --reps 40 --rep-offset $off \
    --turn-delivery plugin --concurrency 4 \
    --snapshot "$OLDPWD/evals/snapshots/loop/round-76-control-$off.json") &
done; wait
```

`--rep-offset 100` starts above the pilot's reps 0 to 9, so no generation key is
shared with it. `python3 evals/bench/release.py` is run over the four snapshots
before any contrast is read, per [#272], and the control worktree is removed
when the round is scored.

A [#164] item 2 note: the edit renders no `Wrong:`/`Right:` pair. The quoted
sentence is a fragment inside a prohibition, the form the closing-offer bullet
already ships.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#138]: https://github.com/JordanMPDS/laconic/issues/138
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Results

*Nothing above this line was written after the numbers came in.*
