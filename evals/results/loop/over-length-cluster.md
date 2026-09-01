# The over-length cluster: what five rounds established

Six issues report over-long answers at level `full`: [#46], [#60], [#113],
[#116], [#136] and [#150]. Rounds 29, 32, 33, 34 and 35 have been spent on them.
This is what is now known, and what each issue should do next.

## The cluster's own framing is partly wrong

Round 32 stated the shape the six were thought to share:

> a short question about a large subject, **where the subject's size sets the
> answer's size** and the question's size has no effect

Round 34 measured the emphasised half and it is null. Scaling a fixture 2.3–3.8×
moved median words +2.3% on baseline and +4.8% on laconic, 4 of 6 cells,
p = 0.688. Rounds 33 and 35 measured two other variables on the same instrument
and both are real:

| Variable | cells | rep-paired | laconic median |
|---|--:|--:|--:|
| **ownership** — confirming a conclusion the model wrote | 6 of 6, p = 0.031 | 29 of 30, p < 0.0001 | 93 → 127 |
| **accumulated own output** — 1 → 4 prior answers | 6 of 6, p = 0.031 | 26 of 30, p = 0.0001 | 114 → 156 |
| **subject size** — +3% of context | 4 of 6, p = 0.688 | 16 of 29, p = 0.711 | 126 → 132 |

**What lengthens an answer is the model's own investment in the conversation,
not the size of the thing it is answering about.** That is a different claim from
the one the cluster was built on, and it re-sorts the six issues.

The null is bounded and the bound was registered before the words were read:
tripling the fixture moved it from ~2% of turn-1 context to ~5%. A manipulation
that made the subject the bulk of context is untested.

## Two reports named the mechanism before it was measured

[#136] locates it itself — the pull is strongest *"when the model has a lot of
recent context it is proud of"* — and [#60] describes the same thing without
naming it:

> Earlier turns in the same session had legitimately long outputs... nothing
> resets the calibration afterward. After several turns where long *was* right,
> long stopped feeling like a violation, and the next turn inherited the
> register even though the request had changed shape entirely.

Round 35 measured that: four prior own answers instead of one is worth +36.8% on
laconic, and it scales. Two independent field reports converging on one
mechanism, which then measures real, is the strongest evidence this cluster has
produced.

## The six issues are three groups, not one

### Group A — conversational investment: [#60], [#113], [#136]

All three are *deep into a long session*, and all three describe a short question
answered at length after earlier turns established a register. This is the group
the measured mechanisms explain.

| | Trigger | Reported |
|---|---|--:|
| [#60] | evaluative, *"is this sound?"* | ~650 w |
| [#113] | feasibility, *"could we test this on X?"* | ~600 w |
| [#136] | closed confirmation, *"you said X, correct?"* | ~400 w |

The chain measured for [#136], each step against a control from its own batch:

| | prior own answers | turns | laconic median | widest of 15 |
|---|--:|--:|--:|--:|
| `confirm-*` | 0 | 1 | 93 | 114 |
| `recall-*` | 1 | 2 | 127, 114 | 144 |
| `deep-*` | 4 | 5 | 156 | 266 |

+68% end to end. Still short of ~400, but the remaining gap is plausibly degree
rather than a fourth mechanism, because accumulated own output scales and four
prior answers is not many.

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

Nothing measured in rounds 29 to 35 bears on either.

## Four instrument lessons, all from this cluster

1. **Bounding a licence in prose has failed four times** — rounds 07, 08, 09 and
   29. Relocating one worked, once, in round 10. Any next edit here should be
   structural rather than another sentence in the same paragraph.
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

## What each issue should do next

| Issue | Status | Next |
|---|---|---|
| [#46] | mechanism found (reading rate), edit shipped in round 26 | nothing; closest thing to resolved |
| [#60] | mechanism measured, not yet acted on | wait for a structural edit; its drift half is Group A |
| [#113] | detector built and validated; arm rates measured | **a five-turn family with design-shaped turns** — `deep-*` reads 0/315 because its deliverable is the answer, not because it forbids editing |
| [#116] | uninstrumented, wrong category | needs an action rule and a way to score behaviour, not prose |
| [#136] | all three candidates measured; two real, one null | remaining gap is degree; more turns would test it |
| [#150] | instrument proven incapable | redundancy metric on the [#146] route, before any further round |
| [#172] | found in round 35 | widen the `metric` affirmation, re-judge rounds 33–35 together |

**[#113]'s detector was the next unit and it has been built.** It is binary
rather than judged and it clears the precision bar [#155] could not (30 of 30
against 55.3%), and it has already produced the cluster's clearest arm
separation. What it cannot yet do is answer [#113]'s own question, because no
existing case admits the behaviour. The next unit is that family.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#146]: https://github.com/JordanMPDS/laconic/issues/146
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#172]: https://github.com/JordanMPDS/laconic/issues/172
