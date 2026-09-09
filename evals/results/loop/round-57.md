# Round 57: which clause of the pre-action check costs the reading

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from the already-committed round 56 snapshots and are what sizes this
round. This file is committed before any generation, following
[round 38](round-38.md), [round 47](round-47.md), [round 48](round-48.md),
[round 49](round-49.md), [round 50](round-50.md), [round 51](round-51.md),
[round 52](round-52.md), [round 53](round-53.md), [round 54](round-54.md),
[round 55](round-55.md) and [round 56](round-56.md).

**This round proposes no rule edit and registers no revert.** It runs a third
rules text as a diagnostic arm, which is never merged and is carried in this
branch as a patch rather than as an edit to `rules/laconic.md`. Nothing in
`rules/` changes on this branch, under any outcome below.

## Why this round exists

[#264](https://github.com/JordanMPDS/laconic/issues/264), question 2, which the
issue names a round for:

> **Is the mechanism the one the round 56 registration proposed?** The check
> reads *"Read what grounds the answer, name what is wrong, and leave the fix
> for the user to ask for."* Its trigger is a broken thing; a design question
> has none; so the clause that still applies is the one about not acting.
> Plausible, and **untested** — both endpoints are measured on the same
> responses, so nothing here shows reading is *why*. A wording round that keeps
> the not-acting clause and removes the broken-thing trigger would separate
> them.

Round 56 established that adding the pre-action check costs 7.8 points of
reading rate on `design-*`/sonnet at p = 0.0258, and that no quality cost the
loop can buy will resolve the roughly +2.2 points that composition shift
implies. What it could not establish is **which part of the check does it**,
because it ran two arms and the check is four clauses.

Knowing that matters more than it looks. If the carrier is the not-acting
clause bleeding past a trigger that does not fire, the repair is a wording that
binds the clause to its trigger, and the compression win round 55 and round 56
both measured survives. If the carrier is the trigger itself, no rewording of
the clause helps and the repair is somewhere else entirely.

## The three arms, and the fork they discriminate

The shipped check is one numbered item under a preamble the same edit rewrote:

```
One check before acting, and two before sending:

1. Is the question about something that is broken? Diagnosing it is the
   answer; fixing it is not. Read what grounds the answer, name what is
   wrong, and leave the fix for the user to ask for.
```

Four things are in there: a **trigger** (*is the question about something that
is broken?*), a **diagnose-not-fix** clause, a **read** instruction, and a
**leave-the-fix** clause. The last three are what #264 calls the not-acting
clause plus its reading instruction, and the round 56 mechanism story is that
on a design question the trigger is false, the not-acting clause applies
anyway, and answering without acting means answering without reading.

| arm | rules text | `rules_cksum` | tree |
|---|---|--:|---|
| **A** | no pre-action check at all | 136269960 | `4da6314`, round 54's merge |
| **B** | the check as shipped | 594915793 | `a879c8f`, master |
| **C** | the check with its trigger removed, everything else byte-identical | 658995990 | master plus [`round-57-arm-c.patch`](round-57-arm-c.patch) |

Arm C's item 1 reads:

```
1. Diagnosing is the answer; fixing is not. Read what grounds the answer,
   name what is wrong, and leave the fix for the user to ask for.
```

The preamble line is unchanged from B, items 2 and 3 are unchanged, and the
only difference from B is the deleted question and the pronoun it bound
(*Diagnosing it* becomes *Diagnosing*, because *it* no longer refers to
anything). That is one change, which is what makes the arm attributable.

**Three outcomes are distinguishable, and they are different findings.**

- **C sits at B.** The not-acting clause is sufficient on its own. The trigger
  never gated it, so removing the trigger changes nothing, and #264's mechanism
  is supported. The repair is a wording that actually binds the clause.
- **C sits at A.** The not-acting clause is not sufficient. Something about the
  trigger — the conditional form, or the word *broken* — is carrying the fall,
  and rewording the clause cannot fix it.
- **C sits below A.** *Read what grounds the answer* is a real reading
  instruction, and in arm B the conditional gates it off: a model that answers
  the trigger with "no" treats the whole item as satisfied and skips the
  reading instruction with it. Ungated, the same words raise reading above a
  rules text that never mentions reading. That is a shippable direction and
  gets its own issue.

The third possibility is why this is a three-arm round rather than a two-arm
one. A C-versus-B contrast alone cannot tell "the clause is not the carrier"
from "the clause is the carrier and removing the trigger reversed it".

## What the archive says, and the scope it fixes

> **Computed 2026-09-08, before this registration**, from `num_turns` on the
> committed `round-56-control-*` and `round-56-edit-*` snapshots. No judging,
> no new calls.

Round 56 reported its secondary over all eight `design-*` cases. Two of those
cells are pinned at a structural floor and contributed nothing:

| cell | A (control) | B (edit) |
|---|---|---|
| `design-alerting` | 0/40 | 0/40 |
| `design-audit-log` | 0/40 | 0/40 |
| `design-cache` | 17/40 | 21/40 |
| `design-rate-limit` | 11/40 | 15/40 |
| `design-realtime` | 11/40 | 17/40 |
| `design-retry` | 18/40 | 23/40 |
| `design-search` | 23/40 | 29/40 |
| `design-upload` | 32/40 | 32/40 |

Every unread run in round 56 is in the lower six. **This round scopes to those
six**, which reads the same difference on 25% fewer calls:

| scope | A | B | difference |
|---|---|---|--:|
| eight cases (round 56's published figure) | 112/320 (35.0%) | 137/320 (42.8%) | +7.8 |
| **six cases (this round's scope)** | **112/240 (46.7%)** | **137/240 (57.1%)** | **+10.4** |

**The two dropped cells are selected on a structural property, not on their
effect.** They read 0 of 80 unread runs across both arms of round 56, so they
cannot vote for either side at any reps, and the loop's own `one_turn` rules
already list `design-alerting` and `design-audit-log` among the sixteen cases
with a structurally fixed rate. Choosing cells by which of the *moving* ones
moved would be the post-hoc subgroup selection that round 56 caught and named,
and this round does not do it: all six cells with variance are in, including
`design-upload`, which moved by zero.

## What the round buys

**1,440 generations and no judgments.** The endpoint is `num_turns`, which is
recorded on every run, so this round buys no judge call at all — against round
56's 640 generations plus 640 judgments.

Six cases, **sonnet only**, **80 reps an arm**, three arms generated
simultaneously from three trees so era and CLI release cancel between them
rather than confounding them, which is the pattern [round 38](round-38.md)
established. Three `run.py` processes, one an arm, `--concurrency 3` declared
on all three, one below the [#255] ceiling.

`git diff` over `evals/cases` is empty between all three trees, so the three
snapshots carry byte-identical case material and all three carry `cases_cksum`
**2801628494**, which is the value over exactly these six cases. It is not
round 56's 2423244529, which is the value over its eight, and it is not the
suite-wide 2389944869 — since [#69] the field covers exactly the cases a
snapshot holds, and naming the wrong constant is the mistake round 56's
registration made.

```sh
# arm B, master, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 80 \
  --cases design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --concurrency 3 --snapshot evals/snapshots/loop/round-57-arm-b.json

# arm A, from a worktree at 4da6314, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps 80 \
  --cases design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --concurrency 3 --snapshot <abs>/evals/snapshots/loop/round-57-arm-a.json

# arm C, from a worktree carrying round-57-arm-c.patch, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps 80 \
  --cases design-cache,design-rate-limit,design-realtime,design-retry,design-search,design-upload \
  --concurrency 3 --snapshot <abs>/evals/snapshots/loop/round-57-arm-c.json
```

## Registered power

> **Computed 2026-09-08, before this registration.** 4,000 simulated draws per
> figure, cell by cell at the round 56 per-cell rates above, pooled and scored
> by the exact test this round registers.

| endpoint | assumed | n/arm | power |
|---|---|--:|--:|
| **primary:** unread rate, C against A | 46.7% to 57.1% | 480 | **0.947** |
| secondary: unread rate, B against A | 46.7% to 57.1% | 480 | 0.947 |
| secondary: unread rate, C against B | no assumption registered | 480 | — |

The primary is sized against round 56's own measured effect, which is the only
estimate of it that exists. **0.95 is the point of the round**, for the reason
round 56 gave: at that power a null on the primary is a result rather than
another draw, and it is what tells "the clause is not the carrier" from "the
round was too small to see it".

The C-against-B contrast is registered as a test but not powered, because no
defensible effect size for it exists in advance: under the first outcome above
it is zero by hypothesis, and a test powered against zero is not a thing.

## Registered bars

**Primary: the unread rate on the six cases, arm C against arm A**, one-sided
Fisher exact in the direction of more unread, α = 0.05. Unread is
`num_turns <= 1`, the definition `report.py`'s `one_turn` counter uses, over
`ok` runs only.

**Secondary 1: the same test for arm B against arm A.** This is a direct
replication of round 56's secondary against a control this round generates for
itself, on the narrowed scope. Registered because a single round's p = 0.0258
is one draw, and because a failure to replicate would put the whole of #264 in
question — which is a result, and one this round would otherwise find by
accident and be tempted to explain away.

**Secondary 2: arm C against arm B**, two-sided Fisher exact, α = 0.05.

**The [#131] scope is reported for all three contrasts.** `design-cache`,
`design-realtime` and `design-upload` are the cells with an established link to
answer quality, and the loop's standing rule is that a reading endpoint is read
there as well as over the family. At 80 reps that scope is n = 240 an arm and
carries less power than the primary; it is disclosure, and no decision below
turns on it.

**No bar here is fatal, and there is nothing for a fatal bar to reject.** The
four fatal counters compare a rules edit against a baseline; this round ships
no edit. Arm C is a diagnostic tree and is never a candidate for merge on any
outcome, so no result below can be argued into one.

**Per-cell counts are published for all three arms whatever the tests do.**

## The decision rule

Registered here so that no outcome can be argued into another afterwards. Let
`p_CA` be the primary and `p_CB` secondary 2.

- **`p_CA` fires and `p_CB` does not** (C is at B, above A): the not-acting
  clause is sufficient without its trigger. #264 question 2 is answered yes,
  and the round files a follow-up issue proposing a wording that binds the
  clause to the broken-thing case, to be tested on its own reading endpoint.
- **`p_CA` does not fire and `p_CB` does** (C is at A, below B): the clause is
  not the carrier. #264 question 2 is answered no, the mechanism paragraph in
  round 56 and in #264 is marked as refuted in place, and the round says what
  is left standing — the trigger's own form — without proposing a wording for
  it, because nothing in this round measures that.
- **C is significantly *below* A**, two-sided at α = 0.05: the ungated reading
  instruction raises reading. The round files that as its own issue with the
  arithmetic, and does not propose the wording as an edit here, because a rules
  text that says *fixing is not the answer* unconditionally contradicts what
  the plugin is for and would need its own quality round before it could ship.
- **Neither fires**: at 0.95 power against the only effect size on the table,
  the round reports that C is distinguishable from neither arm and publishes
  both confidence intervals. That is a weaker result than either branch above
  and the round will say so rather than picking the nearer arm.

Secondary 1 is reported in every branch and gates none of them. If it fails to
replicate, that is stated first, above the primary, and every conclusion below
it is read against a finding that did not reproduce.

## What this round cannot establish

- **Anything about quality.** No judging is bought, deliberately: round 56
  showed at 0.95 power that the quality cost of a shift this size is about
  +2.2 points and that no round the loop buys can resolve it. Spending 1,440
  judge calls to fail to resolve it again is the fourth underpowered round
  round 56 refused to be. What the reading rate translates to is arithmetic,
  not measurement: round 56's strata differ by 28.0 points, so X points of mass
  crossing predicts about 0.28X points of failure rate.
- **Anything about haiku**, unchanged from round 56. The scope is sonnet
  because that is where three rounds put the effect and where the `num_turns`
  proxy separates cleanly.
- **Anything about the non-design cells**, which have no reading variance to
  measure.
- **Which of the three surviving clauses carries it, if C sits at B.** Arm C
  removes one thing. Separating *diagnose-not-fix* from *leave the fix for the
  user to ask for* from the rewritten preamble line — *One check before acting*
  is itself an instruction about acting, and tool calls are acting — would need
  three more arms and is the round after this one.
- **That the ten fewer words in arm C are not the carrier.** A clause cannot be
  removed without removing its words, and this round cannot separate the clause
  from its length. What bounds it is that arm A is 38 words shorter than arm B
  and reads *more*, in the direction opposite to a pure length effect.
- **[#116]'s own endpoint**, which is volunteered work displacing the answer,
  still [round 50](round-50.md)'s null at 0.56 power.

---

# Results

**Everything above this line was committed before any generation. Everything
below it is computed from the three snapshots.**

1,440 generations, 0 judgments, **0 failed calls in the scored data**. Three
arms at 480 usable runs each, six `design-*` cases, sonnet, 80 reps an arm,
generated from three trees simultaneously. All three snapshots carry
`cases_cksum` **2801628494** as registered, and
`python3 evals/bench/concurrency.py` on the three files reports *no arm-day
exceeds its declared concurrency*.

## Secondary 1 first: the round 56 effect did not replicate

The registration requires this to be stated above the primary, and it is the
reason every number below is weaker than the round was designed to produce.

| contrast | arm | unread | rate | 95% CI |
|---|---|---|--:|---|
| | **A** (no check) | 266/480 | 55.42% | [50.9, 59.8] |
| | **B** (check as shipped) | 284/480 | 59.17% | [54.7, 63.5] |
| | **C** (trigger removed) | 282/480 | 58.75% | [54.3, 63.1] |

**Secondary 1, B against A: +3.75 points, 95% CI [-2.5, +10.0], one-sided
Fisher p = 0.1337.** It does not fire. Round 56 read the same contrast on the
same six cells at **+10.4 points**, and this round was powered at 0.947 to
find exactly that.

The power was really there. Re-simulated at the control rate this round
actually observed, 4,000 draws at n = 480 an arm put power at **0.943** against
a +10.4 point effect and **0.807** against +8. So this is a round that would
almost certainly have seen the round 56 effect, and did not.

## The primary

**C against A: +3.33 points, 95% CI [-2.9, +9.5], one-sided Fisher
p = 0.1640.** It does not fire.

**Secondary 2, C against B: -0.42 points, 95% CI [-6.6, +5.8], two-sided
Fisher p = 0.9477.** It does not fire either, and it is the tightest null in
the round: whatever arm B does, arm C does within half a point of it.

C is not significantly below A, so the third branch does not apply either
(C against A two-sided, p = 0.3280).

**This is the registered "neither fires" branch.** Arm C is distinguishable
from neither arm, both intervals are published above, and per the registration
the round says so rather than picking the nearer arm. **#264 question 2 is not
answered by this round.** The ordering the point estimates give — A below C,
with C level with B — is the shape #264's mechanism predicts, and at these
intervals it is not evidence for it.

## Per-cell counts, all three arms

Published whatever the tests do, as registered.

| case | A | B | C | A % | B % | C % |
|---|--:|--:|--:|--:|--:|--:|
| `design-cache` | 45/80 | 46/80 | 50/80 | 56.2 | 57.5 | 62.5 |
| `design-rate-limit` | 30/80 | 38/80 | 33/80 | 37.5 | 47.5 | 41.2 |
| `design-realtime` | 31/80 | 45/80 | 31/80 | 38.8 | 56.2 | 38.8 |
| `design-retry` | 45/80 | 44/80 | 51/80 | 56.2 | 55.0 | 63.8 |
| `design-search` | 51/80 | 52/80 | 50/80 | 63.8 | 65.0 | 62.5 |
| `design-upload` | 64/80 | 59/80 | 67/80 | 80.0 | 73.8 | 83.8 |
| **total** | **266/480** | **284/480** | **282/480** | **55.4** | **59.2** | **58.8** |

## The [#131] scope

Disclosure, as registered. No decision turns on it.

| arm | unread | rate | 95% CI |
|---|--:|--:|---|
| A | 140/240 | 58.33% | [52.0, 64.4] |
| B | 150/240 | 62.50% | [56.2, 68.4] |
| C | 148/240 | 61.67% | [55.4, 67.6] |

C against A +3.33 points (p = 0.2572), B against A +4.17 points (p = 0.2005),
C against B -0.83 points (p = 0.9251). The same three nulls, with less power.

## What happened to arm A, and what it did not do

**Arm A stopped 9 keys short of its 480 on a usage limit** and was completed on
2026-09-09 at 05:23 UTC, from the same `4da6314` worktree, cases verified
byte-identical. The 8 failures and the 1 absent key were consecutive, in reps
78 and 79, which is the eight-consecutive-failure stop doing its job. The
repair runs landed under CLI **2.1.266**, a release neither of the other arms
carries, so they are disclosed and tested rather than assumed harmless:

- The 9 repair runs read 7/9 unread against 259/471 for the rest of arm A,
  two-sided p = 0.3103.
- **Dropping them entirely** moves the primary to +3.76 points (p = 0.1345) and
  secondary 1 to +4.18 points (p = 0.1083). Neither fires.
- **Restricting all three arms to reps 0 to 77**, the block where all three are
  balanced at 468 runs, reads C-A +3.21 (p = 0.1780), B-A +4.49 (p = 0.0932),
  C-B -1.28 (p = 0.7399). Neither fires.

No conclusion in this round depends on the repair.

## Why the effect went missing: a CLI release landed inside the round

**Post-hoc. Nothing in this section was registered, and none of it changes a
verdict above.** It is here because the registration's whole design rests on
the premise that running three arms simultaneously makes era cancel between
them, and that premise did not hold.

The round ran across the **2.1.263 to 2.1.265** boundary. The arms did not
cross it together, because they generate at different speeds and arm A was the
one that hit the limit:

| arm | on 2.1.263 | on 2.1.265 | on 2.1.266 |
|---|--:|--:|--:|
| A | 225 | 246 | 9 |
| B | 276 | 204 | 0 |
| C | 254 | 226 | 0 |

Inside each release the picture is not the pooled one:

| stratum | A | B | C | B-A | C-A | C-B |
|---|--:|--:|--:|--:|--:|--:|
| **2.1.263** | 108/225 (48.0%) | 162/276 (58.7%) | 138/254 (54.3%) | **+10.70** (p = 0.0107) | +6.33 (p = 0.0982) | -4.36 (p = 0.3350) |
| **2.1.265** | 151/246 (61.4%) | 122/204 (59.8%) | 144/226 (63.7%) | **-1.58** (p = 0.6695) | +2.33 (p = 0.3344) | +3.91 (p = 0.4273) |

**Round 56 ran entirely on 2.1.263**, on 2026-09-08 between 05:52 and 14:30
UTC. Round 57's own 2.1.263 block ran from 15:15 to 20:54 the same day. On that
release the two rounds agree almost exactly:

| round | A | B | B-A |
|---|---|---|--:|
| 56 (all of it) | 112/240 (46.7%) | 137/240 (57.1%) | **+10.42** |
| 57, 2.1.263 only | 108/225 (48.0%) | 162/276 (58.7%) | **+10.70** (p = 0.0192) |

The control arm is what moved. Across the release boundary **arm A rises 48.0%
to 61.4%** while **arm B is flat at 58.7% to 59.8%**. Comparing the rounds
directly, arm A rises 46.7% to 55.4% (p = 0.0325) and arm B does not move
(57.1% to 59.2%, p = 0.6304). A rules text with no pre-action check started
producing the unread rate that the check used to produce.

Formally this is suggestive and not established: the B-A interaction across the
two strata is **z = 1.875, p = 0.0608**, and it is post-hoc. Mantel-Haenszel
pooling over the two releases does not rescue any contrast — C-A odds ratio
1.197 (p = 0.1744), B-A 1.221 (p = 0.1296), C-B 0.973 (p = 0.8357).

## What this round establishes

- **The round 57 primary and both secondaries are null**, at genuine 0.94 power
  against the effect the round was sized for. #264 question 2 is unanswered.
- **Arm C is indistinguishable from arm B** at the tightest interval in the
  round, [-6.6, +5.8] points. If there is a trigger effect it is small.
- **Round 56's +7.8/+10.4 point reading-rate finding is release-conditional on
  the evidence available.** It reproduces at +10.70 on the release it was
  measured on and is absent at -1.58 on the next one. That is one boundary, one
  observation, and post-hoc.
- **Simultaneity does not protect a round from a release landing inside its
  window.** It equalises the *calendar* across arms, not the *instrument*, and
  it stops equalising even the calendar as soon as the arms drift apart in pace
  — which they do, because a usage limit hits the slowest arm hardest. Round 37
  established that style drifts between releases; this round is the first where
  a release moved a counter a registered test was reading, mid-round.

## What it does not establish

- **That the round 56 effect was an artefact.** Two draws either side of one
  boundary cannot separate "the release changed the behaviour" from "both
  rounds' first halves ran high". The pooled B-A over both rounds is still
  +5.97 points at p = 0.0259.
- **Anything about quality**, unchanged: no judging was bought, deliberately.
- **Anything about haiku**, or about the non-design cells.
- **Which clause carries the reading cost**, if any does. That was the round's
  purpose and it is exactly what the null leaves open.

## What follows

`rules/laconic.md` is unchanged on this branch, as registered, under this and
every other outcome. Arm C was never a merge candidate and is not one now.

Filed as [#272](https://github.com/JordanMPDS/laconic/issues/272): the
instrument moved under a live round, and both the #264 question and the round 56
finding need re-running inside a single CLI release before either can be read.

[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#264]: https://github.com/JordanMPDS/laconic/issues/264
