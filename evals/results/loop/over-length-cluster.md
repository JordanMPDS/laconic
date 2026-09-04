# The over-length cluster: what eleven rounds established

Six issues report over-long answers at level `full`: [#46], [#60], [#113],
[#116], [#136] and [#150]. Rounds 29, 32, 33, 34, 35, 36, 37, 38, 40, 41 and 42
have been spent on them. This is what is now known, and what each issue
should do next.

> **Rewritten 2026-09-03.** The version of this document written after round 35
> concluded that conversational investment lengthens the answer, and sent four of
> the six issues in that direction. Round 40 showed the measurement was of
> `--turn-delivery repeat`, a harness mode that re-appends the whole rule slice
> every turn, and that under the shipped wiring the effect reverses. The
> conclusion, the group structure and the next-step table have all been rederived
> below. What the old version got right — [#46]'s reading-rate mechanism, [#150]'s
> instrument problem, [#116]'s miscategorisation — is unchanged, because none of
> it came from the multi-turn family.

## The cluster's own framing is wrong twice over

Round 32 stated the shape the six were thought to share:

> a short question about a large subject, **where the subject's size sets the
> answer's size** and the question's size has no effect

Round 34 measured the emphasised half and it is null. Scaling a fixture 2.3–3.8×
moved median words +2.3% on baseline and +4.8% on laconic, 4 of 6 cells,
p = 0.688. Rounds 33 and 35 then measured two other variables on the same
instrument and both moved:

| Variable | cells | rep-paired | laconic median |
|---|--:|--:|--:|
| **ownership** — confirming a conclusion the model wrote | 6 of 6, p = 0.031 | 29 of 30, p < 0.0001 | 93 → 127 |
| **accumulated own output** — 1 → 4 prior answers | 6 of 6, p = 0.031 | 26 of 30, p = 0.0001 | 114 → 156 |
| **subject size** — +3% of context | 4 of 6, p = 0.688 | 16 of 29, p = 0.711 | 126 → 132 |

**Every row of that table is a measurement of `--turn-delivery repeat`,** which
re-appends the whole rule slice as a system prompt on every turn. The plugin
sends the slice once and a one-line reminder after. Round 40 generated the same
cells under `plugin` and the chain reverses:

| family | prior own answers | `repeat` | `plugin` |
|---|--:|--:|--:|
| `confirm-*` (turn 1) | 0 | 94.0 | 88.5 |
| `recall-*` (turn 2) | 1 | 115.0 | **17.0** |
| `deep-*` (turn 5) | 4 | 159.5 | **27.0** |

Turn 1 is the internal control — both modes send byte-identical turn-1 material —
and it does not move (p = 0.576). The second family behaves the same way:
`cold-service` to `drift-service` reads 263 to 364 under `repeat` and 284 to
134.5 under `plugin`.

**So the laconic answer is not longer deep in a session. Under the wiring the
reports came from, it is about a fifth as long, and round 41 established that this
costs nothing measurable** — 30/30, 28/30 and 28/30 on the identical final
question at the three depths, p = 0.4915, against 90/90 on a matched `repeat`
batch that spends six times the words.

**The unruled answer does get longer, and round 42 measured it: +51.4% at the
same depths.** So the depth effect the cluster was built on is real; what was
wrong was the arm it had been measured on.

Rounds 33 to 35 did not find the mechanism behind [#60], [#113] and [#136] —
they measured a harness mode. Round 42 found it, on the arm that carries no
rules. What is now known is that **the mechanism the reports name is real, the
plugin reverses it, and the instrument still does not reproduce the reported
failure** — a laconic session going long at depth — in either its single-turn
form (round 32) or its multi-turn one.

The subject-size null is bounded and the bound was registered before the words
were read: tripling the fixture moved it from ~2% of turn-1 context to ~5%. A
manipulation that made the subject the bulk of context is untested, and so is
subject size under `plugin`.

## Two reports name the mechanism, and it measures real on the unruled arm

[#136] locates it itself — the pull is strongest *"when the model has a lot of
recent context it is proud of"* — and [#60] describes the same thing without
naming it:

> Earlier turns in the same session had legitimately long outputs... nothing
> resets the calibration afterward. After several turns where long *was* right,
> long stopped feeling like a violation, and the next turn inherited the
> register even though the request had changed shape entirely.

Two independent field reports converging on one mechanism, which then measures
real against a matched control, is the strongest evidence this cluster has
produced. Round 42 puts it at **+51.4%** on baseline, replicating the +65.4% that
rounds 33 and 35 measured on the same arm under the other delivery mode.

What was withdrawn is the reading of it as *laconic's* behaviour. Round 35 had
laconic at +36.8% under `repeat`; under `plugin` the same manipulation reads
−68.9% against a baseline at +51.4%.

**The gap between the reports and the instrument is the cluster's central
question**, and it is now a narrower one: not "what lengthens the answer" but
"why does laconic fail in the field where it binds hardest here". Two candidate
explanations, neither tested:

- **The harness's earlier turns are not the reports' earlier turns.** Both
  reports describe a session whose prior answers were *legitimately long* —
  [#136] says the turn before the failure was "a real explanation with a table",
  which was the correct response. The `deep-*` turns are short analysis answers
  about a one-page fixture. A register can only be inherited from a register that
  was set.
- **A real session interleaves work with questions.** Every turn in these cases
  ends `Don't edit anything.`, which `CRITERIA.md` requires so the diagnosis
  lands in the response rather than the diff.
  [`closing-offers.md`](closing-offers.md) already found this shape-dependence
  for a different metric, and it was task shape rather than that clause.

Both are case-authoring problems rather than rule problems, and neither is worth
buying until the measurement below is in.

## The six issues are three groups, not one

### Group A — deep in a long session: [#60], [#113], [#136]

All three are *deep into a long session*, and all three describe a short question
answered at length after earlier turns established a register. The round-35
version of this document called this "the group the measured mechanisms explain".
Its mechanism has since been measured on the other arm: round 42 finds an
unruled model running **+51.4%** longer at turn 5, which is what all three
describe, while laconic runs **−68.9%** against it. So the group's mechanism is
explained and the plugin already answers it on this instrument; what is
unexplained is why the field reports show laconic failing where the instrument
shows it binding hardest.

| | Trigger | Reported |
|---|---|--:|
| [#60] | evaluative, *"is this sound?"* | ~650 w |
| [#113] | feasibility, *"could we test this on X?"* | ~600 w |
| [#136] | closed confirmation, *"you said X, correct?"* | ~400 w |

The chain measured for [#136] ran +68% end to end under `repeat` and −70% under
`plugin`, from the same turn 1. The round-35 reading — that the remaining gap to
~400 words was plausibly degree rather than a fourth mechanism — depended on the
`repeat` figure and does not survive it. Under `plugin` there is no gap to close
in that direction; there is a sign disagreement to explain.

**[#113] adds something the other two cannot.** Its report is of a *binary*
signal — a closing offer, which `lite` prohibits and `full` inherits — appearing
on one turn and not the adjacent one, same level, same session, same request
shape. Word count is a judgement call; *"did the last sentence offer to do more
work"* is not. If ceremony and length decay together, the cheap binary detector
measures the expensive one. It also **flickered rather than decayed**, which is
evidence against monotonic drift and against any fix that merely re-asserts the
level periodically.

That detector now exists, as `metrics.closing_offers()`, and measuring it
produced a result and a correction — see
[`closing-offers.md`](closing-offers.md). **Laconic emits closing offers at 3.5%
against baseline's 13.1%** (Fisher p = 8.6e-18, deduplicated), while every
control arm sits at or above baseline: `concise-style` 16.8%, `terse-control`
19.6%, `word-compression` 22.0%. Generic brevity does not suppress the shape and
the rule does.

**The correction is to this document's own first recommendation.** Running it
over `deep-*` costs no generation, and it finds nothing: zero hits in both arms
across all 315 turn-responses of rounds 33 to 35. The reason is task shape rather
than the `Don't edit anything.` clause those prompts carry — `design-audit-log`
carries the same clause and reads 9.3%, while `walkthrough` lacks it and reads
0.1%. Offers appear where the answer names something buildable that the model has
not built; they vanish where the deliverable is the answer. Measuring [#113]'s
drift needs a five-turn family whose **turns are design-shaped**.

**That family was built and run, and it answers [#113] in the negative.** Round
36's `cold-service` and `drift-service` share a five-file Express fixture and a
byte-identical final question, asked alone and asked at turn 5. Baseline reads
68.0% cold against 20.0% at turn 5 (Fisher p = 0.0014): **conversational depth
suppresses the offer rather than eroding the rule.** Laconic reads 0 of 125
turn-responses and 1 of 25 cold, so it has nothing to decay from — the largest
arm separation the loop has measured, 17/25 against 1/25 at p < 0.0001.

Round 36 ran `repeat`, so it inherits the objection this document's opening
raises. The check is free, because round 40's control holds the same two cells
under `plugin` and the detector is syntactic: laconic reads **0 in 50
`drift-service` turn-responses and 0 in 10 `cold-service` responses** under
`plugin` too. By the rule of three that bounds the rate at about 6% rather than
demonstrating zero, but it is the first evidence from the delivery mode [#113]
describes and it agrees. What remains unreproduced is [#113]'s own report: the
flicker, on one turn and not the adjacent one.

### Group B — cold-read design answers: [#46]

[#46] does not belong with Group A, and the difference is in its own report:
*"Several turns had gone well and stayed terse. Then I asked a design question
and got an essay."* Terse prior turns is low accumulated own output — the
opposite of [#60]'s condition.

Its mechanism was found separately, in round 23: on design questions, **reading
rate is the only axis**. Pooled over five arms, answers that read the codebase
fail 4 of 93 and answers that do not fail 55 of 57 (Fisher p = 1.5e-33), and
laconic's apparent compression on `design-*` was largely mix-shift from
suppressed reading. Round 26 then accepted the earned-licence edit — median shift
1294 tokens, 8 of 8 cells, p = 0.008 against a 1032.5 floor.

[#46] is the one issue in the cluster with a shipped, measured improvement
against it.

### Group C — not length problems: [#150], [#116]

Neither is fixable by a rule about how long an answer is.

**[#150] is a metric problem.** Round 29 ran the edit and returned a flat null,
3 of 7 cells at p = 1.000 with five of eight moving the wrong way. More
importantly it found the scope could not have worked: the harm [#150] measured
is 230 of 1,335 prose words, **17.2%**, against a scoped floor of **17.7%**. An
edit that removed every restated word would have landed 8 tokens short of
passing. And more reps cannot fix it — the floor is a per-cell standard
deviation, not a standard error, so more runs estimate the same spread more
precisely rather than shrinking it. **This instrument cannot answer [#150]
however the edit is worded.** It needs a judged redundancy verdict, frozen
before its validation sample is drawn, on the route [#146] established.

**[#116] is an action problem.** It is about volunteered *work*, not volunteered
prose: a comprehension question answered correctly in one line, followed by
unrequested analysis over the project's data. Both of laconic's pre-send checks
are scoped to the response being written and neither fires before a tool call.
The asymmetry its report names is the reason it needs a stricter default rather
than the same one: unrequested prose costs a reader seconds, unrequested work
costs tokens, wall-clock and sometimes money.

**It is no longer uninstrumented.**
[`volunteered-work.md`](volunteered-work.md) surveyed the 5,557 archived `tools`
lists and found the behaviour already in the suite: every `Edit` call ever
recorded is on `conditional`, whose prompt asks *"Should I raise the pool size?"*
and which gets edited instead. A matched batch reads **baseline 25/40 against
laconic 14/40, p = 0.0247**, so laconic halves it.

Two things follow. **Laconic already acts on this**, which is more than the
cluster could say for [#116] before. And **the prose metric rewards the
failure** — an editing run's median is 45 words against 144, p = 5e-06, so an
answer that edits instead of answering scores as excellent compression ([#209]).

What was missing is a case this can be optimized against: `conditional` grades
`rule-adherence`, so no rule edit may be proposed from it. **The obstacle to
building one is now gone.** `CRITERIA.md` requires every case to end
`Don't edit anything.` "or its verdicts measure whether the model chose to act",
which is why no scorable case admits an edit. Judging the 80 runs says the
premise does not hold: an editing response passes the trap **24 of 39** against
**22 of 41** for a non-editing one, p = 0.5055, so the diagnosis does not migrate
into the diff. A `quality` case may drop the clause, grade fixture-derived
content only, and read the behaviour off the tool list.

Nothing measured in rounds 29 to 43 bears on [#150].

## Six instrument lessons, all from this cluster

1. **Bounding a licence in prose has failed four times** — rounds 07, 08, 09 and
   29. Relocating one worked, once, in round 10. Round 40 then tried the
   structural alternative this list recommended — a third pre-send check, "Would
   this be the same answer if this were the session's first turn?" — and it was
   rejected: five of seven cells moved up, sign test p = 0.4531, point estimate
   +7.5 tokens against a 29.3 floor. So the score is four wording attempts
   rejected, one relocation accepted, and one structural attempt rejected. The
   next edit here does not have an obvious form, and buying one before the
   measurement below is in would be a fifth guess.
2. **`output_tokens` is not comparable across the single-turn/multi-turn
   boundary.** Every `confirm-*` graded turn carries a tool-use block and no
   `recall-*` graded turn does, so it read backwards on two of six pairs while
   words rose on all six. Compare words, or multi-turn against multi-turn.
3. **At 5 reps the baseline family median is stable and the laconic one is
   not** — `recall-*` across three batches reads baseline 175/173/172 (1.7%) and
   laconic 127/126/114 (10.3%). A round comparing laconic across batches needs
   its own control. Round 34 claimed both were stable from two draws; round 35
   corrected it from three.
4. **A trap can fail answers that read the fixture correctly.** The `metric`
   stem requires confirming that lift is the wrong metric, while its fixture
   concludes that *neither* metric supports a decision — so a response reframing
   it as a sample-size problem is right and fails anyway. Filed as [#172].
5. **A multi-turn round measures whichever delivery mode it takes, and the two
   are different treatments.** Four rounds took `repeat` without choosing it. Its
   figures are not the plugin's, and the sign is not preserved. Since 2026-09-03
   `run.py` refuses to generate multi-turn cells without `--turn-delivery`; see
   [`turn-delivery.md`](turn-delivery.md).
6. **Style drifts across CLI releases and judged correctness has not.** Round 37
   held the rules byte-identical and watched the syntactic preamble rate on
   `walkthrough` move 4.7x in five days (p = 1.0e-05), while round 38's matched
   control graded 30 of 30 on the same case a criterion had not touched since
   08-27. A rate quoted from a snapshot needs its date; a `rules_cksum` cannot
   see era.

## What each issue should do next

| Issue | Status | Next |
|---|---|---|
| [#46] | mechanism found (reading rate), edit shipped in round 26 | nothing; closest thing to resolved |
| [#60] | structural edit tried in round 40 and rejected; its depth premise is now measured on the baseline arm (round 42) | the inflation it describes is real and the plugin already reverses it on this instrument; what is unreproduced is a *laconic* session going long at depth |
| [#113] | detector built and validated; the design-shaped family was built (round 36) and answers *no decay*, under both delivery modes | the flicker itself is still unreproduced; needs a case that admits it, not another round on these cells |
| [#116] | **case built and piloted** — `quota-merge` is the first case to drop the "Don't edit anything." clause and it grades cleanly, but it elicits **0 edits in 10** against `conditional`'s 39 of 80 (p = 0.0042) | the question shape is wrong, not the fixture: a closed confirmation invites confirmation. Build the open-advisory sibling, and probably at depth — the same wall round 32 hit for [#136]. See [`quota-merge-pilot.md`](quota-merge-pilot.md) |
| [#136] | mechanism restored on the baseline arm by round 42: depth inflates an unruled answer +51.4%, and laconic runs −68.9% against it | the diagnosis is no longer the open part. The gap is between the report and the product, and closing it needs a case that reproduces a laconic session going long at depth — see the two case-authoring candidates above |
| [#150] | instrument proven incapable | redundancy metric on the [#146] route, before any further round |
| [#172] | **resolved** — affirmation widened, rounds 33–35 re-judged on that stem | none; round 35 moves 57/60 to 60/60 and rounds 33–34 do not move |

## The measurement this cluster needed: bought, and it answers

> **Round 42 ran this and the falsifier did not fire.** Baseline does not fall at
> depth — it rises by half again, 139.0 to 210.5 median words (+51.4%), while
> laconic falls 98.0 to 30.5 (−68.9%). Six of six cells move as predicted,
> p = 0.0312, and the arm gap widens from −39.5 words at turn 1 to −181.0 at
> turn 5 (p = 5e-06). **So depth inflates an unruled answer by about half, which
> is what [#136] and [#60] describe, and the plugin is what reverses it.** What
> rounds 33 to 35 measured was laconic *failing to resist* that inflation under
> `repeat`. The section below is the registration, kept as written.
>
> Baseline turns out to be a delivery-invariant control by construction —
> `arms["baseline"]` carries no system prompt, so both modes send it identical
> material on every turn — and it replicates across the boundary: +65.4% under
> `repeat` (rounds 33 and 35) against +51.4% under `plugin`.
>
> **Round 43 then judged both arms of that snapshot: 120 of 120 pass, every cell
> 10/10.** So at turn 5 an unruled model writes seven times as much and answers
> the same question no better. That comparison sits at its ceiling and rules out
> a laconic deficit of a fifth of correctness, not a smaller one. Full write-ups
> in [`round-42.md`](round-42.md) and [`round-43.md`](round-43.md).

## The one measurement this cluster now needs, registered here

Every `plugin`-delivery run in the archive is a laconic run: round 39's 45,
round 40's 220 across two rules revisions. **There is no baseline arm at depth
under `plugin` anywhere**, so the central number above has two readings and
nothing separates them:

- **The plugin is working.** Laconic holds the level as a session deepens, and 17
  words at turn 2 is the rule binding on a closed question.
- **The harness gets terse at depth regardless.** An unruled model in the same
  five-turn chain would also answer in 17 words, and laconic is being credited
  with something the setup produces.

Round 41 rules out the third reading, that the terseness is harm: quality holds
at every depth. It cannot rule out the second, because it judged one arm.

**Hypothesis, written before the batch:** generating `baseline` beside `laconic`
under `--turn-delivery plugin` will show the depth fall on the laconic arm only.
The falsifier is a baseline arm that falls by a comparable proportion, which
would mean the shipped multi-turn behaviour is the harness rather than the
plugin, and would retire this cluster's whole multi-turn instrument.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 10 \
  --cases 'confirm-*,deep-*' --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-42.json
```

Six cases, two arms, ten reps: 360 calls, because `confirm-*` is one turn and
`deep-*` is five. `confirm-*` is the internal control and must not move between
arms by more than its own between-batch variation. Scored on median words per
cell, no judging, because the question is about length and round 41 already
bought the quality verdict on the laconic side. `recall-*` is omitted to keep the
round at one contrast; it can be added if the two-turn midpoint matters.

**Do not register a scoped `output_tokens` target across the boundary** — lesson
2 above, and it is why this is scored on words.

**[#113]'s detector was the next unit and it has been built and used.** It is
binary rather than judged, it clears the precision bar [#155] could not (30 of 30
against 55.3%), and it produced the cluster's clearest arm separation. Round 36
then answered the drift question with it. What no case yet admits is [#113]'s
own report — the flicker, present on one turn and absent on the adjacent one.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#146]: https://github.com/JordanMPDS/laconic/issues/146
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#172]: https://github.com/JordanMPDS/laconic/issues/172
