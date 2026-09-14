# Round 63: the pre-action check's reading cost, and whether one clause of it is why

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures and power simulations marked as computed and
dated in place, which come from already-committed snapshots and are the reason
this round takes the shape it does. This file is committed before any
generation, following [round 38](round-38.md) through
[round 62](round-62.md).

**This round proposes no rule edit yet.** It measures two candidate wordings of
one that already shipped, and the only way `rules/laconic.md` changes in this
branch is by the registered decision rule below.

## Why this round exists

[#264](https://github.com/JordanMPDS/laconic/issues/264), filed by
[round 56](round-56.md) under a decision rule that named this outcome in
advance: *"the primary does not fire and the secondary does: the edit stands,
and the round files the reading-rate finding as its own issue."*

Round 56 bought 640 generations and 640 judgments at 0.95 power on
`design-*`/sonnet. Its primary was null and bounded — `quality_fails` 68/318
against 66/313, 95% CI [−6.7, +6.1]. Its secondary fired: the share of runs
that opened no file rose from 112/320 (35.0%) to 137/320 (42.8%), **+7.8
points, one-sided Fisher p = 0.0258**.

Splitting the same verdicts by whether the run read is what makes both true at
once:

| stratum | control | edit |
|---|---|---|
| opened a file | 24/207 (11.6%) | 19/183 (10.4%) |
| opened none | 44/111 (39.6%) | 47/130 (36.2%) |

Inside each stratum the check changes nothing. It changes how much mass lands
in each. The strata differ by 28.0 points, so 7.8 points crossing implies a
quality cost near **+2.2 points** — inside round 56's own interval, and roughly
five times smaller than the effect it was powered for. Round 55 computed about
1,188 verdicts a side for a 5-point shift; +2.2 needs several times that. So
the loop has a number it cannot buy its way to on the quality counter, and
#264's second open question is the one that is affordable:

> **Is the mechanism the one the round 56 registration proposed?** The check
> reads *"Read what grounds the answer, name what is wrong, and leave the fix
> for the user to ask for."* Its trigger is a broken thing; a design question
> has none; so the clause that still applies is the one about not acting.
> Plausible, and **untested** — both endpoints are measured on the same
> responses, so nothing here shows reading is *why*. A wording round that keeps
> the not-acting clause and removes the broken-thing trigger would separate
> them.

## The three arms

All three are the shipped `full` slice with the opening numbered list swapped
and **every other byte identical**. `tests/test_bench.py` builds each one from
the live hook output and compares by exact equality, so an edit to
`rules/laconic.md` anywhere fails the arm rather than silently confounding the
round with it. `evals/arms/README.md` carries the same table.

| arm | words | the list it carries |
|---|--:|---|
| `laconic-precheck-off` | 1,000 | the two-item list the file carried before round 55 |
| `laconic` | 1,041 | the check as round 55 accepted it |
| `laconic-precheck-read` | 1,041 | the check with the reading instruction hoisted out |

`laconic-precheck-read` reads:

```
One check before acting, and two before sending:

1. Before writing, read what grounds the answer. If the question is about
   something that is broken, diagnose it rather than fix it: name what is
   wrong and leave the fix for the user to ask for.
2. What is the smallest set of claims that fully answers this?
3. Is anything here something the user did not ask for?
```

The reading instruction is now unconditional and the not-acting clause is still
bound to the broken-thing trigger. That is exactly the separation #264 asked
for, and it is one instruction moved rather than a rewrite: **`-read` is
word-matched to the shipped slice**, so the recovery contrast cannot be
explained by how much file there is. Round 59 bounds bulk removal at 1.070x per
100 words on the design cells, and this arm differs by zero.

`-off` is 41 words shorter and those 41 words are the check itself. It is not a
rung on a ladder — it is the positive control, and it exists because a control
generated in another window has misread this repo before. Round 31 registered a
count against a three-day-old control that read 31 where its own simultaneous
control read 46, at byte-identical rules. Citing round 56's 35.0% instead of
generating `-off` beside the other two would repeat that.

**One interleaved pass, not three worktrees.** Because all three arms are
`--append-system-prompt` texts, `run.py` samples them at adjacent moments
inside one process. One snapshot, one `rules_cksum`, one CLI-release
trajectory shared by every arm. Every previous round that compared a rule
variant paid for two trees and a checksum guard to approximate this; the arms
directory makes it exact.

## Scope: six cells, and the two that are not bought

`design-cache`, `design-rate-limit`, `design-realtime`, `design-retry`,
`design-search`, `design-upload`. Sonnet only, following round 56, which scoped
to sonnet because that is where three rounds put the effect and where haiku sits
flat at 67/120 → 70/120.

`design-alerting` and `design-audit-log` are excluded **in advance and on a
mechanical criterion**: both read 0/40 unread on both sides of round 56. A
stratum with no variance contributes exactly zero to a stratified contrast — the
scorer's selftest checks that property directly — while costing a quarter of the
generations. This is selection on the endpoint's variance in the control, not on
the effect, and it is the same argument round 56 used to drop the flat haiku
half.

> **Computed 2026-09-10, before this registration.** 8,000 simulated draws per
> figure at round 56's own per-cell rates, scored by the exact test this round
> registers.

| design | n per arm | total | pooled Fisher | MH stratified |
|---|--:|--:|--:|--:|
| 8 cells, 40 reps | 320 | 960 | 0.634 | 0.784 |
| **6 cells, 53 reps** | 318 | 954 | 0.834 | **0.875** |
| 6 cells, 70 reps | 420 | 1,260 | 0.924 | **0.942** |

At constant cost the reallocation is worth 0.09 of power. What it gives up is
stated rather than left to a reader: if those two cells are off the floor in
this window they were informative and were not bought.

## The endpoint, and what promoting it does not license

The primary is the **arm's own rate of answering a design question without
opening the fixture**. On this family that is not one correlate of quality among
several — [#88] and
[`design-discrimination.md`](design-discrimination.md) record that the three
`-v4` cases exist precisely because the older five cannot tell a derived answer
from a recalled one, and no response that failed to resolve the fixture has ever
passed.

The loop's standing rule makes reading rate non-fatal, on the ground that not
opening a file is not itself harm — it is the mechanism `quality_fails` is
supposed to catch. Round 56 then showed `quality_fails` cannot resolve a cost
this size at any reps the loop buys. This round promotes the mechanism to
primary and **states the limit of that promotion rather than arguing around
it**: the estimand is the process, not the outcome. The 28-point stratum gap is
measured on a post-treatment split and is not identified by the randomisation,
so it motivates the round and may not be used to convert a result into points of
quality. A firing gate 2 supports *"the rewording reduces the known mechanism of
design-case failure"*. It does not support *"the rewording improves quality"*,
and the round document will not say so.

## The two gates, in a fixed sequence

One alpha covers both because they are tested in a registered order.

**Gate 1, the assay: `laconic` against `laconic-precheck-off`**, one-sided at
α = 0.05, in the direction of the check raising the unread rate. Does the check
cost reading in this round's own window at all? **If it does not fire the round
is assay-inconclusive**: it says nothing about the rewording, gate 2 is not
tested, and nothing ships. A failed assay is not evidence that the check is
harmless — the design cannot deliver that, and reading it that way afterwards is
the failure mode this sentence exists to prevent.

**Gate 2, recovery: `laconic-precheck-read` against `laconic`**, one-sided at
α = 0.05, in the direction of the rewording lowering the unread rate. Tested
only if gate 1 fired.

**The test is Mantel-Haenszel stratified by case**, with a within-case
permutation of the arm label printed beside it as the exact check on the normal
approximation. The cells run from 27% to 80% unread in round 56's table, so a
pooled 2x2 discards blocking the design already has; the table above is what
that is worth. The permutation is the null the design supports — the case is
fixed before the round, the arm is assigned within it — and a disagreement
between the two is a warning about the approximation rather than about the
finding.

The four outcomes the pair produces, written down before they are seen:

| gate 1 | gate 2 | reading |
|---|---|---|
| fires | fires | the check costs reading and the rewording recovers it |
| fires | does not | the check costs reading and this rewording is not the fix |
| does not fire | not tested | assay-inconclusive; the round measured nothing |
| fires the wrong way | not tested | the check *helped* reading here; everything upstream is suspect |

## Registered power

> **Computed 2026-09-10, before this registration.** Same simulator, at round
> 56's per-cell rates, assuming `-read` recovers the whole 7.8 points.

| quantity | 70 reps, n = 420 per arm |
|---|--:|
| gate 1 alone | 0.944 |
| gate 2 alone | 0.940 |
| **both, which is what a ship needs** | **0.899** |

Under a partial recovery of 70% the joint figure falls to 0.708, and that is
the honest ceiling on what a non-firing gate 2 rules out. Registered here so a
null is read against the effect it was powered for and not against the one the
round would have preferred.

## Guardrails

The edit's risk is that it buys reading by writing more, or by reading where
there is nothing to read. Neither is caught by the primary.

**Prose length, `-read` against `laconic`, blocked on the case**, at a
registered non-inferiority margin of **1.10x**. Reported **all-runs first and
blocked on the reading stratum second**, in that order: conditioning on "opened
a file" conditions on the very mechanism the arm changes, so the stratified
figure ([#131]) is the diagnostic and the unconditional one is the guardrail.
Same estimator rounds 59 and 60 used, imported from
`evals/pilot/score_dilution.py` rather than re-implemented. The margin is not
derived — round 59 measured 1.119x for deleting 209 words and calls 1.10x its
detection floor, so a tighter margin would certify nothing this design can
resolve.

**Median turns per run**, all runs, per arm. A run that opens a file, fails to
find what it wants and gives up costs a turn without costing output tokens.

**The sentinel: the four cases that ship no fixture directory** —
`code-fidelity`, `decision`, `floor`, `ordered-steps`. Across 1,509 archived
`laconic`/sonnet runs of those cases the tool count is **zero** and `num_turns`
is 1 in 1,506 of them, so the floor needs no model and any reading there is
gratuitous by construction. All three arms, 40 reps, generated in the same
window. This is where an unconditional "read what grounds the answer" would show
up and where `design-*` is blind. Its prose-length comparison is four cells,
below the six a scoped sign test needs, so it is published per cell as a
disclosure and gates nothing.

**No judging in this pass, and that is a decision rather than thrift.** Both
endpoints and every guardrail are deterministic. Round 56 established at 0.95
power that `quality_fails` cannot resolve the ~2.2 points implied here, so 1,740
judgments would buy a null that resolves nothing — which is exactly the
"fourth underpowered round is worth nothing" trap round 56 was built to escape.
The loop's standing order is to score the cheap target before buying the
expensive arm; this is that order applied. What judging would be bought for, and
when, is in the decision rule below.

## What the round buys

**1,740 generations, sonnet, no judgments.** Round 56 spent 1,280 calls.

Four `run.py` processes at once, which is the [#255] ceiling, all declaring
`--concurrency 4`. This machine has 7.6 GiB — the machine of the 2026-09-06
incident — so the ceiling is not raised.

```sh
# the round: 6 design cells, 3 arms, 70 reps, split by rep range over 3 shards
python3 evals/bench/run.py --arms laconic-precheck-off,laconic,laconic-precheck-read \
  --models sonnet --cases design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --reps 24 --rep-offset 0  --concurrency 4 --snapshot evals/snapshots/loop/round-63-a.json
python3 evals/bench/run.py --arms laconic-precheck-off,laconic,laconic-precheck-read \
  --models sonnet --cases design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --reps 23 --rep-offset 24 --concurrency 4 --snapshot evals/snapshots/loop/round-63-b.json
python3 evals/bench/run.py --arms laconic-precheck-off,laconic,laconic-precheck-read \
  --models sonnet --cases design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --reps 23 --rep-offset 47 --concurrency 4 --snapshot evals/snapshots/loop/round-63-c.json

# the sentinel, in the same window, in the fourth shard
python3 evals/bench/run.py --arms laconic-precheck-off,laconic,laconic-precheck-read \
  --models sonnet --cases code-fidelity,decision,floor,ordered-steps \
  --reps 40 --concurrency 4 --snapshot evals/snapshots/loop/round-63-sentinel.json

python3 evals/bench/merge.py evals/snapshots/loop/round-63-{a,b,c}.json \
  --out evals/snapshots/loop/round-63.json
python3 evals/pilot/score_precheck.py evals/snapshots/loop/round-63.json \
  evals/snapshots/loop/round-63-sentinel.json
```

Every shard gives every case, so the per-shard read of each gate that the
scorer prints is a genuine robustness check rather than a restatement of which
cases a process owned. The sentinel is its own snapshot rather than a merge
partner: `cases_cksum` is computed over exactly the cases a snapshot covers
([#69]), and folding four unrelated cases into the round's union would change
the number the round is identified by.

Control `rules_cksum` is **594915793** for all three arms, because the arms are
system-prompt texts and the field records the shipped slice they were built
against. CLI release at registration is **2.1.267**; `run.py` stamps every run
([#272]) and `evals/bench/release.py` reports the composition if the round spans
one.

## The decision rule

Registered here so that neither outcome can be argued into the other afterwards.

- **Gate 1 does not fire.** The round is assay-inconclusive. Gate 2 is not
  tested, no wording ships, `rules/laconic.md` is untouched, and #264 stays open
  with this round recorded against it as a failed assay. The round document may
  not report the check as harmless.
- **Gate 1 fires, gate 2 does not.** The check's reading cost replicates on a
  simultaneous control and this rewording does not fix it. Nothing ships. #264's
  second question is answered in the negative: hoisting the reading instruction
  is not the mechanism, and the issue keeps its first and third questions.
- **Gate 1 and gate 2 both fire, and every guardrail holds.** The rewording is
  adopted into `rules/laconic.md`, `bash tools/build-rules.sh` regenerates
  `rules/dist/*.md` in the same commit, and the ledger records it. **The
  adoption is conditional on the guardrails**: length over 1.10x all-runs, or a
  sentinel reading rate above the archive floor on `-read` and not on `laconic`,
  blocks it whatever the primary did.
- **Gate 1 fires in the wrong direction** — the check *improves* reading here —
  the round reports it and nothing ships. Round 56's finding would then be in
  question on its own terms and that is a bigger result than this round's.

**What a firing round does not buy, and what would.** Adoption here rests on a
deterministic endpoint over six design cells on one model. It does not re-clear
the round-wide fatal counters, which round 55 bought over 22 cases and both
models. If gate 2 fires, the next round's business is the round-wide arm and its
judgments against a simultaneous control — the loop's step 2, bought only for an
edit that passed step 1. That is registered here as the sequence rather than
left as a suggestion, and the ledger row for round 63 says "adopted on the
mechanism, fatal counters not re-bought".

## What this round cannot establish

- **Anything about quality.** See the endpoint section. The conversion from
  reading to `quality_fails` is a post-treatment stratification and is not
  identified here.
- **Anything about haiku**, or about the two excluded design cells, or about
  non-design cells beyond the four-case sentinel. `codex` named this as the
  round's largest external-validity gap on `tools/consult.sh`: the round is
  scoped to design cases and the rule ships globally, so a wording that wins
  here could still cost something in the broken-question population the check
  was written for. The sentinel is a floor check, not a bridge, and the bridge
  is the round-wide pass named in the decision rule.
- **That "hoisting" specifically is what did it.** `-read` is a bundled
  intervention: the instruction moved, its verb changed from "Read" to "Before
  writing, read", and the not-acting clause was recast from "Diagnosing it is
  the answer; fixing it is not" to "diagnose it rather than fix it". A result
  attributes to the arm, not to one of those three.
- **Whether a different wording does better.** One arm, one alternative.

## Where the design came from

`bash tools/consult.sh` was run against the delegate targets with the issue, the
two-arm design I was leaning towards, and the three things I was least sure of.
`codex` and `kimi` answered; `deepseek` was asked and did not answer.

- **`codex`**: the necessary-process framing that replaced my "surrogate for
  quality" wording; the assay-inconclusive verdict as a named third outcome; the
  all-runs length guardrail, on the ground that the grounded stratum conditions
  on the mechanism the arm changes; and the observation that the round is scoped
  to design cases while the rule ships globally. It also caught that my draft
  cited round 56's "~0.93" power for an effect size round 56 never observed —
  the simulations above are the correction, and 40 reps over eight cells would
  have been a 0.63-power round wearing a 0.93 label.
- **`kimi`**: the four-outcome table above; the fixed-sequence ordering of the
  two gates, so one alpha covers both; and the demand that the trigger for a
  later judged pass be written down rather than left to reading.
- **Both, independently**: buy the positive-control arm, and add an
  over-reading sentinel on cases with nothing to read. Neither was in the
  design that went to them; the sentinel is the larger of the two additions.

`codex` also proposed a longer wording — *"read the relevant files or other
material that grounds the answer"* — to guard against pointless tool use. Not
taken: it costs the word-match against the shipped slice, which is what makes
the recovery contrast free of a length artefact, and "what grounds the answer"
already has nothing to name when nothing does. The sentinel is what tests that
reading rather than a longer sentence asserting it.

[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Results

**Gate 1 does not fire. The round is ASSAY-INCONCLUSIVE**, which the
registration named in advance. Gate 2 was not tested, nothing ships,
`rules/laconic.md` is untouched, and [#264] stays open with this round recorded
against it as a failed assay.

Per the registration, and stated here rather than left to a reader: **this is
not evidence that the pre-action check is harmless.** The design cannot deliver
that, and the sentence forbidding that reading was written before the numbers
were in for exactly this outcome.

1,740 generations, sonnet, no judgments, 0 failed calls. Generated 2026-09-10
and resumed 2026-09-14 after a usage limit stopped all three design shards at
the 8-consecutive-failure rule; no failed key counts as done, so the resume
regenerated exactly what was missing.

## Gate 1, the assay

| arm | unread | rate |
|---|--:|--:|
| `laconic-precheck-off` | 226/420 | 53.8% |
| `laconic` | 232/420 | 55.2% |

Difference **+1.4 points**, 90% CI **[-4.2, +7.1]**. Mantel-Haenszel
**z = +0.428, one-sided p = 0.3343** over 6 strata; within-case permutation
**p = 0.3619**. The two agree, so the normal approximation is not the issue.

The sign is the direction round 56 predicted and the magnitude is not. The
interval excludes both round 56's headline **+7.8** and its **+10.4** on these
six cells, so this is a well-powered null against the effect the round was
built for, not an absence of data. Registered power was 0.944 for gate 1 alone
at this n against +7.8.

## What actually moved, and why the positive control earned its cost

Round 56's `design-*` contrast, recomputed on the six cells this round scores —
`design-alerting` and `design-audit-log` were excluded in advance for reading
0/40 unread on both sides, so they contribute nothing:

| | no check | check | difference |
|---|--:|--:|--:|
| round 56 (2026-09-08) | 112/240 (46.7%) | 137/240 (57.1%) | **+10.4 pts** |
| round 63 (this round) | 226/420 (53.8%) | 232/420 (55.2%) | **+1.4 pts** |

Difference of differences +9.0 points, **z = 1.579, two-sided p = 0.1142**. The
two rounds are therefore **not formally distinguishable**, and this round does
not claim round 56 measured an artefact. What it claims is narrower and is what
its own data support: with a control generated beside the treatment, the gap
is not there.

**The drift is on the no-check arm.** The check arm barely moved between the two
windows, 57.1% to 55.2%; the arm without the check went 46.7% to **53.8%**, up
7.1 points. That is the era effect this repository has been bitten by before,
and it lands on precisely the arm a round would have been tempted not to buy.

Had this round cited round 56's control instead of generating
`laconic-precheck-off` in the same window, it would have read:

> 55.2% against 46.7% = **+8.6 points, one-sided p = 0.0168** — gate 1 fires.

The round would then have gone on to test gate 2 and could have shipped a
wording on the strength of a control from another window. Round 31 registered a
count against a three-day-old control that read 31 where its own simultaneous
control read 46; this is the same failure, caught the same way, and it is the
strongest argument in the archive for the positive-control arm being
non-negotiable rather than a nicety.

## Per-cell disclosure

No second alpha rides on these.

| cell | `-off` | `laconic` | `-read` |
|---|--:|--:|--:|
| `design-cache` | 40/70 (57%) | 32/70 (46%) | 33/70 (47%) |
| `design-rate-limit` | 26/70 (37%) | 30/70 (43%) | 23/70 (33%) |
| `design-realtime` | 24/70 (34%) | 38/70 (54%) | 31/70 (44%) |
| `design-retry` | 46/70 (66%) | 39/70 (56%) | 33/70 (47%) |
| `design-search` | 35/70 (50%) | 38/70 (54%) | 38/70 (54%) |
| `design-upload` | 55/70 (79%) | 55/70 (79%) | 44/70 (63%) |

The check raises the unread rate on two cells, lowers it on two, and ties on
two. That dispersion is what a +1.4-point round-wide difference looks like from
underneath, and it is why the round-wide reading is the registered one.

## Guardrails

All reported, though with nothing shipping none of them gate anything.

| guardrail | result | |
|---|--:|---|
| prose length, `-read` against `laconic`, all runs | 1.057x | within the 1.10x margin |
| prose length, blocked on the reading stratum ([#131]) | 1.055x | within margin |
| median turns per run, `laconic-precheck-off` | 1 (mean 3.59) | |
| median turns per run, `laconic` | 1 (mean 3.54) | |
| median turns per run, `laconic-precheck-read` | **4** (mean 4.01) | disclosure |

**The sentinel is clean on the endpoint it was built for.** Across the four
cases that ship no fixture, every arm opened nothing:

| arm | opened something | tool calls |
|---|--:|--:|
| `laconic-precheck-off` | 0/160 (0.0%) | 0 |
| `laconic` | 0/160 (0.0%) | 0 |
| `laconic-precheck-read` | 0/160 (0.0%) | 0 |

An unconditional "read what grounds the answer" produced **no** gratuitous
reading where there is nothing to read. That was the larger of the two
additions `codex` and `kimi` both asked for, and it answers its question
cleanly even though the round it was attached to did not.

**The sentinel's prose length does not clear the margin.** `-read` against
`laconic` is **1.103x, p = 0.0004** on both scopes, against a 1.10x margin.
Four cells is below the six a scoped sign test needs, so per the registration
this is published as a disclosure and gates nothing — but it is the one signal
in the round that would have needed answering before `-read` could ship, and
any future round proposing this wording inherits it.

**Context, not a gate:** the check itself buys real compression. `laconic`
against `laconic-precheck-off` is **0.894x** all-runs and **0.881x** on the
reading stratum, both at p < 0.0001. Whatever it costs, it is not costing
nothing in return.

## Instrument audits

- **Release ([#272]).** The round spans 2.1.267 and 2.1.270.
  `evals/bench/release.py` flags the day split, which is 39%/61% rather than
  50/50. The question that matters is whether release is correlated with *arm*,
  and it is not: the three arms sit at 39.0%, 39.3% and 38.8% on 2.1.267, a
  chi-square of arm against release of **0.020, dof 2, p = 0.99**. The endpoint
  itself is flat across the boundary, 52.2% unread on 2.1.267 against 52.5% on
  2.1.270. One interleaved pass is what bought that, as registered.
- **Concurrency ([#120]).** Scoped to this round's five snapshots,
  `evals/bench/concurrency.py` reports **no arm-day exceeds its declared
  concurrency** and exits 0. Three shards in flight against the 4 declared, and
  under the [#255] ceiling. The archive-wide run still exits 1 on the legacy
  snapshots `AGENTS.md` already documents.

## Disclosure: the scorer was run on partial data mid-round

After the first generation window stopped, `score_precheck.py` was run against a
scratch copy of the then-incomplete snapshots to verify the merge-and-score
pipeline executed end to end. It read assay-inconclusive then as well. This
changed nothing: the decision rule is mechanical and fixed in this file, the
round completed to its registered n regardless, and no arm, case, scope or
threshold was altered afterwards. It is recorded because this loop does not
discover its analyses at the end.

## What this leaves

[#264] keeps all three of its questions. Its second one — whether hoisting the
reading instruction is the mechanism — is **not answered**, because the sequence
is registered and gate 1 gates gate 2. `laconic-precheck-read` is measured and
not judged, and what exists on it is the length signal above rather than a
reading result.

The finding worth carrying forward is not about the wording at all. It is that
**round 56's reading cost did not reproduce against a simultaneous control**,
and that a design citing the older control would have shipped on it. Whether
round 56's effect was era or is real and merely smaller than 10 points is open,
and the arithmetic round 55 recorded still applies: an effect of the size this
round's interval permits is not one the loop can buy its way to on
`quality_fails`.

[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#272]: https://github.com/JordanMPDS/laconic/issues/272
