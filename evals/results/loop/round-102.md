# Round 102: the build plan is the depth a design answer leaves out (#46)

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 90, 98 and 101, the 2026-09-24 benchmark, and the
fire check described below, which ran before this file was written and chose
the scope. This file, the edit, the regenerated `rules/dist/*.md` and
`evals/pilot/score_plan.py` are committed in one commit before any generation.

`bash tools/candidate-due.sh` exited 1 at registration: [round 101](round-101.md)
measured, so round 102 has to carry a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0: 0.3.4 is current.

**This edit runs unconditionally**, as [round 100](round-100.md)'s did. A
withdrawn edit records the round as measuring, and a second measuring round
in a row is what the cap forbids. What keeps it from being bought blind is
that the fire check below has already shown the behaviour it targets on the
control's rules, CLI and day.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_plan.py --control $OUT/round-102-control.json \
  --edit $OUT/round-102-edit.json \
  --control-judgments $OUT/round-102-control-judgments.json \
  --edit-judgments $OUT/round-102-edit-judgments.json
python3 evals/bench/release.py $OUT/round-102-{control,edit}.json
```

## Why this round exists, and why this issue

Every open `rules` issue has read zero at master in its last screen: #46 in
rounds 98 and 101, #353 in round 99, #298 in round 100, #264 in round 90, and
#116 and #113 in round 91. The one place the 2026-09-24 benchmark still showed
laconic below baseline on a quality-graded design case was sonnet
`design-alerting` (5 fails against 2) and `design-realtime` (4 against 1), and
no round has re-read either since.

**The fire check, run today at master (`rules_cksum` 3660436060, CLI
2.1.288), before this registration.** Sonnet, laconic and baseline, 10 reps,
judged by the panel. It is committed as `round-102-firecheck.json` and its
judgments, and is not part of the round's test.

| cell | laconic fails | baseline fails | laconic median prose words |
|---|--:|--:|--:|
| `design-alerting` | 1/10 | 6/10 | 311 |
| `design-realtime` | 2/10 | 5/10 | 284.5 |

The quality gap reversed, so it is not this round's target. What the check did
show is the shape #46 reported, at a smaller scale. On 09-24 these laconic
answers ran about 200 prose words; today they run about 300, and they are
build plans. `design-alerting` rep 3 is five numbered bold sections (return
conditions from `govern()`, streak counters in state, alert on transitions, a
heartbeat watchdog, a shadow week), and only then asks *"what monitoring stack
do you already run? If it's Prometheus-style ... that would drop items 2 to 4"*.
`design-realtime` rep 2 is a recommendation, four numbered implementation
steps, and a risk paragraph. The design bullet already asks for "the
recommendation, the one or two decisions that genuinely fork it, and a name
for the depth you left out"; the answers give the recommendation, then write
out the depth instead of naming it.

#46 is the issue this bullet came from, its report is an Opus 5 session, and
opus is the deciding model here. Rounds 98 and 101 measured opus
`design-alerting` cold at medians 242.5 and 240.5 prose words, so opus has the
same headroom sonnet does even though no opus answer has crossed #46's
600-word screen.

## The edit

`rules/laconic.md`, one sentence in the design bullet under `## Level: full`:

```diff
   recommendation, the one or two decisions that genuinely fork it, and a name
-  for the depth you left out. Ask for the fork that survives reading, not the
-  one reading would settle. Explaining something that already exists is a
-  different request, and it is protected above.
+  for the depth you left out. The build plan is the depth you left out, not
+  the approach. Ask for the fork that survives reading, not the one reading
+  would settle. Explaining something that already exists is a different
+  request, and it is protected above.
```

`rules_cksum` on the `full` slice goes **3660436060 to 4106391043**. The
sentence is in `full` and so reaches `ultra`; it does not reach `lite`. No
other file carries the design bullet: `skills/laconic/SKILL.md`, the help card
and `README.md` do not quote it.

**It does not say "steps".** "Ordered instructions: every step" is never-cut,
and a sentence telling the model to leave steps out shares that token with the
protection. "Build plan" names what the answers produced without touching it.
`walkthrough` and `ordered-steps` are bounds below for the same reason.

**It is half of the edit first drafted.** The draft added "when the approach
turns on a fork you are asking about, ask it before building out either
branch." That half is conditional on a fork existing and can be satisfied by
asking first and still writing the plan, so it is unlikely to carry the
length, and two clauses in one round leave a failed bound unattributable. It
is the natural next candidate if this one passes and fork-after-plan persists.

### The claim

> Adding "The build plan is the depth you left out, not the approach." to the
> design bullet should move prose words on the eight `design-*` cases on opus
> **down**, by at least 10%, without design answers failing the panel more
> often.

## Design

Two trees generating at once, per [round 38](round-38.md): the control from a
worktree at master (`rules_cksum` 3660436060), the edit from this branch.
Laconic arm, level `full`, single-turn cases, so no turn delivery is involved.
Each side runs as two shards by `--rep-offset`, four processes at
`--concurrency 4`, inside [#255]'s ceiling.

| cells | reps a side | runs a side |
|---|--:|--:|
| `design-*` on opus | 20 | 160 |
| `ordered-steps`, `walkthrough` on opus | 20 | 40 |
| `design-*` on sonnet | 10 | 80 |

560 generations in all, 400 of them opus.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
A='design-*:opus,ordered-steps:opus,walkthrough:opus'
for side in control edit; do
  tree=$([ $side = control ] && echo /tmp/laconic-control || echo /home/jordan/projects/laconic)
  ( cd $tree && python3 evals/bench/run.py --arms laconic --reps 10 --rep-offset 0 \
      --cells "$A,design-*:sonnet" --concurrency 4 \
      --snapshot $OUT/round-102-$side-shard0.json ) &
  ( cd $tree && python3 evals/bench/run.py --arms laconic --reps 10 --rep-offset 10 \
      --cells "$A" --concurrency 4 \
      --snapshot $OUT/round-102-$side-shard10.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-102-$side-shard{0,10}.json \
    --out $OUT/round-102-$side.json
done
```

Judging is bought only if stage 1 passes:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-102-$side.json --jobs 6 \
    --out $OUT/round-102-$side-judgments.json
done
```

## The bars

Scored by `evals/pilot/score_plan.py`, whose selftest pins each branch. One
look; no extension is registered, so a decision to extend would be a new round.

**Primary, opus.** Prose words on the eight `design-*` cases, over runs that
called at least one tool. The statistic is the mean over cases of the edit's
mean log prose words minus the control's, permuted within case, 20,000
resamples, seed 102, **one-sided in the registered direction**. It passes at
p < 0.05 **and** a ratio exp(shift) of at most **0.90**.

**Stage 1 bounds, deterministic, fatal:**

| bound | cells | harm | test |
|---|---|---|---|
| unread design answers | `design-*`, opus and sonnet pooled | rise | one-sided Fisher, 0.05 |
| sonnet design prose words | `design-*` on sonnet | ratio over 1.10 | point estimate, blocked on case |
| never-cut substring misses | `walkthrough` on opus | rise | one-sided Fisher, 0.05 |

**Stage 2 bounds, judged by the panel, fatal, bought only after stage 1
passes**, each one-sided Fisher at 0.05 and uncorrected, per `AGENTS.md`:
design fails on opus pooled, on sonnet pooled, and per opus case at 20 a side;
`ordered-steps` and `walkthrough` fails on opus, per case and pooled.

**Disclosed, deciding nothing:** per-case medians on both models; numbered
items and headings per answer; the share of design answers whose first
question mark falls in the first half of the answer, which is what the
withdrawn fork-first half would have moved; and the opus sentinel prose ratio.

**Accept** needs the primary and every bound. Then step 8's replication, a
fresh generation of the opus design cells at 20 a side from both trees with
the same primary and stage 1 bounds, and step 9's holdout: all six
`evals/holdout` cases on opus and sonnet at 5 reps a side, judged, rejecting
on any rise in pooled panel fails or never-cut misses at one-sided 0.05. The
pull request does not merge before both are bought. Anything else rejects and
reverts every file the edit touched.

## Power, stated before the numbers

The median per-case standard deviation of log prose words on opus `design-*`
was 0.129 in the 2026-09-24 benchmark. At 20 a side over eight cases the
blocked shift has a standard error of about 0.014, so the p-value half of the
primary is not what binds: a true ratio of 0.85 passes with probability above
0.99, and the 0.90 margin is the real bar, passed about half the time at a true
0.90. Twenty a side is bought for the judged per-case bounds, which cannot
reach a cell below 20 runs.

## Pre-mortem, registered

The likeliest failure is **the point estimate moving with the registered
direction and not reaching 0.90**. Opus answers on these cases already run
about 240 words and mostly as prose rather than numbered plans, so on opus
there may be less plan to remove than the sonnet answers suggest, and a
sentence the model reads as a restatement of "a name for the depth you left
out" changes little. The second likeliest is a **fatal bound rejecting a
passing target**, on `design-alerting` or `design-realtime` judged on opus.
Their traps reward naming where alerts live and what interval to poll at, and
an answer that stops at the approach may drop the one concrete detail the
criterion grades. I expect `walkthrough` and `ordered-steps` to hold: neither
is a design question, and the sentence does not say "steps".

## Where the ideas came from

The target, design-answer length rather than the quality gap the fire check
was bought for, is this round's own, from reading the fire check's answers.
Through `tools/consult.sh`, Kimi supplied the sentence as registered and argued
for splitting off the fork-first half, which is taken. DeepSeek and Kimi both
said to drop "steps" from my draft because it collides with the never-cut
ordered-instructions bullet. DeepSeek argued for 20 reps a side so the judged
per-case bounds can reach a cell, and for stratifying the primary on reading;
both are taken. Kimi's proposal to put sonnet on the same primary bar is taken
only as the sonnet length bound, because the deciding model is opus. Codex did
not answer within its timeout.

[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#46]: https://github.com/JordanMPDS/laconic/issues/46

## Results

<!-- Nothing below this line has been computed. -->
