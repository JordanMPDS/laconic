# The over-length cluster: what fourteen rounds established

Eight issues report over-long answers at level `full`: [#46], [#60], [#113],
[#116], [#136] and [#150], joined later by [#298] and [#305]. Rounds 29, 32,
33, 34, 35, 36, 37, 38, 40, 41, 42, 64, 66, 67, 68, 69 and 70 have been spent
on them, and the rounds' own counter — *"fourteenth round in the over-length
cluster"* — reads 14 of those as cluster rounds proper. **None of them shipped
anything.** This is what is now known, and what each issue should do next.

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
explanations, **both now tested, and neither closes the gap**:

- **The harness's earlier turns are not the reports' earlier turns.** Both
  reports describe a session whose prior answers were *legitimately long* —
  [#136] says the turn before the failure was "a real explanation with a table",
  which was the correct response. The `deep-*` turns are short analysis answers
  about a one-page fixture. A register can only be inherited from a register that
  was set. **Tested** as `evals/pilot/register-*` in
  [`register-inheritance-136.md`](register-inheritance-136.md): the mechanism
  reproduces, laconic 31.0 words to 52.0 at 1.677x and p < 0.00001 against a
  baseline arm that does not move, three stems of three. It reproduces at
  roughly an eighth of [#136]'s reported ~400 words, so it is a mechanism
  finding and not a reproduction of the report.
- **A real session interleaves work with questions.** Every turn in these cases
  ends `Don't edit anything.`, which `CRITERIA.md` requires so the diagnosis
  lands in the response rather than the diff.
  [`closing-offers.md`](closing-offers.md) already found this shape-dependence
  for a different metric, and it was task shape rather than that clause.
  **Tested** as `evals/pilot/work-*` in [`round-67.md`](round-67.md), and
  **refuted in sign**: with turns 2 to 4 doing the work in 30 of 30 runs against
  0 of 30 on the control family, nothing rose on the graded turn in either arm.
  Laconic fell 56.0 to 37.5 and baseline fell with it, 188.5 to 145.0, at a
  log-scale ratio of ratios of 1.015 (p = 0.9559) — so the movement is the case
  family rather than the rules, and a session of work does not inflate the
  laconic answer on the turn that follows it.

Both were case-authoring problems rather than rule problems, and both have now
been bought. The first is a real mechanism at an eighth of the reported size;
the second is not a mechanism at all. **So the magnitude gap has no remaining
named candidate.** Naming a third is the cluster's open work, and round 67
registered that outcome in advance as its own finding rather than discovering it
afterwards.

**[Round 68](round-68.md) names it: session depth, and it names it by failing to
find the harm at one turn.** [#298] is a seventh field report in this cluster and
the sharpest one — a seven-word definition request answered in 342 prose words,
239 of them restating claims earlier turns had already delivered, where 66 words
were correct. `evals/pilot/{explain,reexplain}-*` puts that question **one turn**
after the turn that delivered the rationale. The harm does not merely fail to
reproduce; it inverts. At master rules the already-told question is answered in
27.0 prose words against the cold question's 65.0 — a ratio of **0.415 at
p = 0.0000**, geometric-mean 0.357 with a 95% interval of 0.287 to 0.444, all
three stems agreeing, and the graded turn making **0 tool calls in 90/90** warm
runs against 1 or 2 in 90/90 cold ones. Given the material once, the model
neither refetches nor restates it.

That is the third short-instrument result to land the same way, and together
they make depth the candidate rather than a leftover:

| instrument | turns of prior context | what it found |
|---|--:|---|
| `register-*` ([register-inheritance-136.md](register-inheritance-136.md)) | 1 | mechanism present, ~1/8 of the reported size |
| `work-*` ([round 67](round-67.md)) | 4 | nothing, in either arm |
| `explain`/`reexplain-*` ([round 68](round-68.md)) | 1 | the reverse, at 0.415x |

Every field report in this cluster describes a session that had been running for
a while; every instrument that has failed to reproduce one puts the graded turn
within a few turns of the start. **The cluster's open work is no longer naming a
candidate but building an instrument deep enough to test this one** — which is a
case-authoring problem again, and a more expensive one, because depth is bought
by the turn.

## [Round 69](round-69.md) bought that instrument, and depth is not the mechanism

The paragraph above is answered. `deepexplain-*` is `reexplain-*` with three of
`deep-*`'s ordinary questions inserted between the turn that delivers the
material and the graded definition request — turn 1 and the graded turn
byte-identical, the same fixture by symlink, four prior turns in place of one.
**The laconic answer does not inflate: 27.0 prose words to 30.5, a ratio of
1.130 at p = 0.1962, against the baseline arm's 1.205 on the same contrast.**
The small movement that exists is the movement the unruled arm also makes, a
ratio of ratios of 0.929 with a bootstrap interval of 0.807 to 1.068.

The same round put a third family beside it, `fullexplain-*`, whose three middle
turns are `register-*`'s verbatim and are therefore licensed long by
`rules/laconic.md` itself. That one does move the graded answer — 27.0 to 49.5,
1.833 at p = 0.0010 — but it moves the baseline arm too, 141.5 to 184.5 at
p = 0.0027, so round 67's clause applies and the movement is the case rather
than the rules. **The factor is the register of the intervening turns, at fixed
depth, and not the depth.**

| instrument | turns of prior context | what it found |
|---|--:|---|
| `deepexplain-*` ([round 69](round-69.md)) | 4, ordinary | depth alone: nothing, 1.130 at p = 0.1962 |
| `fullexplain-*` ([round 69](round-69.md)) | 4, licensed long | 1.833, and the baseline arm rises with it |

So the candidate this document named after round 68 is measured and refuted at
the depth this repository can generate, and the magnitude gap has no named
candidate again. What round 69 adds in its place is not a candidate but a
caution about the tests that produced these nulls: **the arm-label permutation
this cluster reads its interactions from builds a null 1.9x wider than the
sampling distribution of the statistic it tests**, because the arms sit about
8x apart and every shuffled group is a mixture of two separated modes. Round 42
disclosed that for raw words; round 69 measured that the log scale does not
escape it. Several stored interaction nulls bound less than they appear to, and
re-deciding them is a harness change rather than a round.

## [Round 70](round-70.md) tried the fifth relocation on [#150]'s paragraph, and it did not replicate

Lesson 1 below says a licence bounded in prose has failed four times and a
relocated one worked once. Round 70 was the relocation: the length-scaling
licence — *a report, walkthrough, comparison or explanation you asked for gets
full detail* — moved out of its own paragraph and into check 2, with no
precedence sentence written anywhere.

**The scoped arm accepted and the replication did not.** Prose summed over the
licensed turns of `register-*` fell to a stem-stratified **0.903 at p = 0.0247**,
95% interval [0.837, 0.990], all three stems down, with the unlicensed `deep-*`
family flat at 1.040 — the specificity that made the number readable as a
licence effect. Bar A, 740 generations over all 37 cases and both models, held.
**Bar B, the same design and seed at 240 runs, read 0.946 at p = 0.0721**, which
the registration had named in advance as a failure of the bar rather than a
partial success. The disclosure that decides it: in Bar B the unlicensed family
fell **0.945** beside the licensed family's 0.946, so one sample produced both
the effect and its discriminator and the next produced neither. The edit
reverted in full.

So the count on this paragraph is five interventions and one survivor, and that
survivor is round 10's. [#150] is owed [#155]'s judged redundancy verdict before
another edit to it, which is what the table below already says.

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
byte-identical final question, asked alone and asked at turn 5. Laconic has
nothing to decay from: pooled over every snapshot that has generated the pair,
**0 of 325 `drift-service` turn-responses and 1 of 65 cold**, against baseline's
29 of 125 (23.2%) at p = 5.4e-18. The 95% upper bound on any laconic rate at any
depth is **0.92%**. Round 36 ran `repeat` and inherits this document's opening
objection; round 40's control and round 70's wide arms hold the same cells under
`plugin` and agree, which is why the bound is quotable rather than a rule of
three on one round.

**Two sentences of the superseded version of this paragraph were wrong, and
[`closing-drift-113.md`](closing-drift-113.md) corrects them.** It read the
baseline's 68.0% cold against 20.0% at turn 5 (Fisher p = 0.0014) as
*"conversational depth suppresses the offer rather than eroding the rule"*.
That contrast is real and it does not support a depth claim: the within-case
series is non-monotone at 32.0%, 24.0%, 12.0%, 28.0%, 20.0%, and a permutation
test that shuffles the turn order inside each run reads slope −0.0200 at
**p = 0.266**. The cross-case drop conflates depth with the four answers already
given and the offers already made. What the data do support is the negative:
**no evidence that depth increases closing offers on either arm.**

**What the corpus does show is that the signal is not turn-local at all**, which
is the finding that outlives [#113]'s proposal. On the unruled arm an offer at
one turn predicts an offer at the next, 16 of 24 against 5 of 76, and the
clustered form of that reading is the distribution of per-run counts: **21 of 25
runs sit at 0 offers or at 4 and above**, variance 3.174 against the 0.891 five
independent draws would give, at **p < 1/20001**. A closing offer is a property
of the session, so it cannot proxy a per-turn quantity — and [#113] offered it
precisely as a cheap per-turn proxy for expensive per-turn length drift. What
remains unreproduced is [#113]'s own report: the flicker, on one turn and not
the adjacent one, which is the rarest pattern in the corpus.

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

## Seven instrument lessons, all from this cluster

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
7. **Every trap in the suite is a floor, and the archive already prices the
   ceiling.** A trap says what an answer must contain, so a longer answer passes
   it too, and an endpoint convicting a response for its length asserts something
   no criterion states. The shortest response a trap has already passed is that
   number, and it needs no labeller: 21,976 blind verdicts joined to the
   responses that earned them give all 37 cases a floor, 36 of them below their
   own median. It also says where no ceiling exists - `destructive` at 0.9x, and
   `deep-*` at 1.09x to 1.15x. See [`judged-floor-136.md`](judged-floor-136.md).

## What each issue should do next

| Issue | Status | Next |
|---|---|---|
| [#46] | mechanism found (reading rate), edit shipped in round 26 | nothing; closest thing to resolved |
| [#60] | structural edit tried in round 40 and rejected; its depth premise is now measured on the baseline arm (round 42) | the inflation it describes is real and the plugin already reverses it on this instrument; what is unreproduced is a *laconic* session going long at depth |
| [#113] | detector built and validated; the design-shaped family was built (round 36) and answers *no decay*, under both delivery modes | the flicker itself is still unreproduced; needs a case that admits it, not another round on these cells |
| [#116] | **four case designs tried and the re-trap refused.** Question form, reading rate and defect kind are eliminated; `conditional` still elicits the behaviour and still cannot grade it, because its criterion self-disagrees on 1 verdict in 8 | a case that both elicits the behaviour **and** grades stably. The fact-versus-framing heuristic that sentence used to give is **not established** — [`judge-self-disagreement.md`](judge-self-disagreement.md) measured four cells and the two shapes interleave. What is established is that stability is a criterion property: one cell moved 0 of 55. See [`conditional-retrap.md`](conditional-retrap.md) |
| [#136] | mechanism restored on the baseline arm by round 42: depth inflates an unruled answer +51.4%, and laconic runs −68.9% against it. **All three of its proposals are now answered:** 1 rejected by [round 64](round-64.md), 2 priced at −0.16 of the demonstration gap by [round 60](round-60.md), and 3 — the detector — measured over 1,953 archived responses at 30.0% precision strict and 63.3% counting every redundant restatement, so unpromotable at either figure. See [`closed-question-136.md`](closed-question-136.md). **Its "the correction is the length" reading then failed**: every one of the 11 hits it excused sits 39 to 129 words above a response that passed the same trap, so the 80-word cutoff is above the required correction rather than inside it. See [`judged-floor-136.md`](judged-floor-136.md) | **Proposal 3 is closed rather than parked.** The 30 labels this row asked for were not bought: re-scoring the 30 that exist under every floor-derived cutoff leaves strict precision between 25.0% and 36.4% against 30.0% at the global 80, the new cutoff sits below 80 on nine of thirteen cases so most of what it adds is shorter and unlabelled, and the only available labeller has read all 37 floor responses, so the delta against the 80-word figure would be the labeller rather than the threshold. Verbatim cross-turn reuse is measured and absent too — 3.1% mean on laconic against 3.8% on baseline over 1,112 multi-turn responses — which closes the last cheap alternative to the [#146] route for this issue. See [`judged-ceiling-136.md`](judged-ceiling-136.md). The true-premise case this row used to ask for was **designed and not built** — `tools/consult.sh` falsified its premise from committed data, and the floor delivers the same construct on the thirteen closed questions already in the suite at no generation cost. Note `deep-*` has no headroom to convict: floor 1.09x to 1.15x of median |
| [#150] | instrument proven incapable; a fifth intervention on the paragraph tried in [round 70](round-70.md) and reverted when the replication read 0.946 at p = 0.0721 | redundancy metric on the [#146] route, before any further round. The detector [#155] parks at 55.3% precision and may not be promoted inside a round |
| [#172] | **resolved** — affirmation widened, rounds 33–35 re-judged on that stem | none; round 35 moves 57/60 to 60/60 and rounds 33–34 do not move |
| [#298] | seventh field report; its shape is `explain`/`reexplain-*` and [round 68](round-68.md) found the harm **inverts** at 0.415x, with [round 69](round-69.md) refuting depth as the reason | the cross-turn redundancy it names is not reachable by a single-turn judge; it belongs in the [#146] verdict's scope, not in a round. It is not reachable lexically either: the graded turn shares a six-word run with the model's own earlier turns on 3.1% of laconic responses against 3.8% of baseline ones, median 0.000, over 1,112 multi-turn runs — see [`judged-ceiling-136.md`](judged-ceiling-136.md) result 4 |
| [#305] | eighth field report. Its cheapest item — *no rule forbids closing with a recap of your own opening* — was instrumented and **killed before registration**: 4.9% on laconic against 5.7% on baseline with three controls spanning 4.2–7.9%, at 12% hand-read precision. See [`closing-recap-305.md`](closing-recap-305.md) | item 1 joins [#150] and [#298] on the [#146] judged-verdict route. Items 2 and 3 inherit [#298]'s instrument problem and [round 70](round-70.md)'s reverted licence respectively. The true-premise case this row also asked for is answered by [`judged-floor-136.md`](judged-floor-136.md) without being built: the surplus a report's fixture makes knowable is the response's distance above its case's judged floor |

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
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
