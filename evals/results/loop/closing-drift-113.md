# The closing offer is a property of the session, not of the turn

**This is not a round.** It proposes no rule edit, registers no revert, and buys
no generations. Every figure below comes from committed snapshots and is
reproduced by `python3 evals/results/loop/closing-drift/sweep.py`, which runs in
a second. Nothing in `rules/` changes.

## The gap this closes

[#113] reports, from a real session at level `full`, the no-closing-offers rule
breaking on one turn and holding on the adjacent one — same request shape, same
level, two consecutive turns. Its argument is that this matters as evidence
rather than as harm:

> word count is a judgment call — two readers can reasonably disagree about
> whether 600 words was right for a given question — whereas *"did the last
> sentence offer to do more work"* is binary and needs no interpretation. If
> ceremony rules and length rules decay together, the cheap binary one is a
> usable detector for the expensive judgment one.

And it is explicit about the shape it saw:

> it **flickered rather than decayed** — violated on one turn, clean on the
> next, same level, same session, adjacent turns, same request shape. That is
> evidence against monotonic drift and for something turn-local.

[`closing-offers.md`](closing-offers.md) built the detector — 30 of 30 hand-read
hits genuine — and could not answer any of that. The only multi-turn corpus then
was `recall-*`, `wide-*` and `deep-*`, which read **0 of 315 in both arms**,
because those cases ask analytical questions about a document: the deliverable
is the answer and there is nothing left to offer. That document ends by naming
what the measurement needs:

> A five-turn family whose **turns are design-shaped** — each answer naming
> something buildable ... The detector is ready and costs nothing to apply to
> such a family.

**That family was built on 2026-09-01 and has never been read.** `drift-service`
asks five design questions about one Express fixture; `cold-service` asks the
**byte-identical final question** cold, as a single turn. The pair exists so the
same question can be read at turn 1 and at turn 5. Three rounds have generated
them incidentally since, so the corpus is already bought.

## The corpus

180 distinct runs, deduplicated on the rules checksum, the arm, the case, the
model and the turn texts — a round that shards by model writes the same runs
into a per-model file and into the union file, and counting those twice is the
mistake `closing-offers.md` records at archive scale.

| | |
|---|---|
| snapshots | `round-36`, `round-40-control`, `round-40-edit`, `round-70-wide-{control,edit}-{haiku,sonnet}` |
| dates | 2026-09-01 to 2026-09-16 |
| level | `full` throughout, which is the level [#113] reports |
| delivery | `plugin` wherever the field exists; `round-36` predates it |

Runs at a round's edit-arm rules text are kept in a stratum of their own rather
than pooled with shipped rules. They were generated to be rejected and two of
them were; they are reported because they are more laconic-arm turn-responses of
the same shape, and they change nothing either way.

## Reading 1: the family works, which is the precondition for everything else

Pooled over all five turns of `drift-service`:

| arm | fired | rate |
|---|--:|--:|
| `laconic` | 0 / 325 | **0.0%** |
| `baseline` | 29 / 125 | **23.2%** |

Fisher two-sided **p = 5.4e-18**. The unruled arm fires at 23.2% where the old
multi-turn family sat at 0.0% in both arms, so the detector has headroom here
and a null on the ruled arm is a measurement rather than a floor of the
instrument.

## Reading 2: the ceiling on a within-session rise

`laconic` fired **0 times in 325 turn-responses**, across all five depths, both
models and every rules checksum in the file. The Clopper-Pearson 95% upper bound
on that rate is **0.92%**, and **1.32%** on the 225 turn-responses at shipped
rules alone.

The one hit anywhere on the ruled arm is on `cold-service`, 1 of 65, and it is
genuine rather than a detector error — `round-36.json`, sonnet, rep 14, ending
*"Want me to implement it?"*.

## Reading 3: the same question at turn 1 and at turn 5, and why it is a disclosure

| arm | `cold-service` turn 1 | `drift-service` turn 5 | p |
|---|--:|--:|--:|
| `baseline` | 17/25 (68.0%) | 5/25 (20.0%) | **0.0014** |
| `laconic` | 1/65 (1.5%) | 0/65 (0.0%) | 1.0 |

The two questions are byte-identical, so question identity — which is worth a
great deal here, 68.0% against 32.0% between the two cases' *different* turn-1
questions at **p = 0.0227** — is removed from this contrast by construction.

**It is still not readable as a depth effect, and is published as a disclosure
rather than a claim.** Three things move together between those two cells: the
turn index, the four design answers the model has already given, and the offers
it has already made. Nothing in the committed data separates them, and the
within-case series says the simple reading is wrong anyway:

| `baseline` `drift-service` | turn 1 | turn 2 | turn 3 | turn 4 | turn 5 |
|---|--:|--:|--:|--:|--:|
| rate | 32.0% | 24.0% | 12.0% | 28.0% | 20.0% |

That is not monotone — turn 3 is the lowest cell and turn 4 recovers above it —
and a permutation test that shuffles the turn order **inside each run**, so the
five turn-responses of one session are never treated as five independent draws,
reads slope **−0.0200, p = 0.266**. On the ruled arm the same test is exactly
null with nothing to shuffle.

So the honest statement is the negative one: **there is no evidence that session
depth increases closing offers on either arm.** The point estimates at depth are
lower, including on the byte-identical question, and that drop cannot be
attributed to depth alone.

## Reading 4: what actually varies, and it is not the turn

The adjacent-turn conditional inverts the suppression story that Reading 3's
confound suggests:

| `baseline` `drift-service` | next turn offers |
|---|--:|
| given this turn offered | 16 / 24 (**66.7%**) |
| given this turn did not | 5 / 76 (**6.6%**) |

An offer does not suppress the next one. It predicts it, tenfold. That table's
own exact test is anti-conservative, because the four adjacent pairs inside a
run are not independent of each other, so the reading that carries weight is the
clustered one — the distribution of per-run offer counts:

| offers in the run | 0 | 1 | 2 | 3 | 4 | 5 |
|---|--:|--:|--:|--:|--:|--:|
| runs | **16** | 2 | 1 | 1 | 3 | **2** |

**Twenty-one of 25 runs are at 0 or at 4-and-above.** The variance of those
counts is **3.174** against the **0.891** that five independent draws at the
pooled 23.2% rate would give, and a permutation that reassigns the same 29 hits
across the same 125 turn-responses with the run boundaries removed never once in
20,000 draws spreads as widely — **p < 1/20001**. That test assumes no
independence it does not have.

## What this decides for [#113]

**Proposal A has nothing to fix on this instrument.** The rule it would enforce
— *the last sentence of a response is never an offer to do more work* — is
already obeyed on 325 of 325 turn-responses at every depth the family reaches.
An edit cannot improve a cell that is at zero, and per [#94]'s directional
reading of a saturated cell, a cell at its floor can only detect a fall.

**The construct behind [#113]'s argument does not survive, and this part does
not depend on the ruled arm being at zero.** The issue proposes the binary
signal as a cheap proxy for expensive per-turn length drift. On the arm where
the signal fires at all, it does not vary per turn: the turn index explains
nothing (p = 0.266) and the session explains almost everything (p < 1/20001). A
quantity that is constant within a session cannot proxy a quantity that moves
within one, whatever that second quantity turns out to be. **A cheap proxy for
the over-length cluster has to be a per-turn quantity that actually varies per
turn, and this one does not.**

**The reported flicker is the rarest pattern in the corpus.** [#113] describes a
violation on one turn and a clean adjacent turn. Of 100 adjacent pairs on the
unruled arm, 8 are discordant in that direction; 16 of the 24 pairs following an
offer offer again. The archive does not reproduce the shape, let alone the drift
it was offered as evidence for.

**[#113] stays open on its length half, and on proposals B and C.** Proposal B
(widen the no-teaching rule from the question to the conversation) and proposal
C (feasibility as a named trigger) are untouched by any of this — neither is a
closing-offer claim, and C is explicitly parked behind [#46] and [#60].

## What this does not establish

- **That the rule cannot break.** It did not break under five read-only turns
  that each end `Don't edit anything.` [#113]'s session had editing turns, and
  `evals/CRITERIA.md` requires that clause of every case but `quota-merge`, so
  this instrument excludes the regime the report came from by construction. The
  bound is 0.92% *under these conditions*.
- **Anything about longer sessions.** Five turns is the deepest family in the
  suite. A rule that decays at turn 30 would read exactly like this.
- **Anything about `ultra` or `lite`.** Every run here is `full`.
- **A mechanism for the run-level clustering.** That it is a session property is
  measured; *why* one session offers five times and another none is not, and
  sampling temperature, the first answer's register, and the fixture's own shape
  are all live.

## What a future unit would buy, and it is one purchase

Both readings that stay open want the same thing, so they are one round rather
than three:

**An editing multi-turn case.** The model produces diffs across turns and the
detector runs on the turn-final prose, testing whether 0 of 325 survives the
regime [#113] actually reports. `quota-merge` is the precedent for dropping
`Don't edit anything.`, and it dropped it on evidence rather than on argument —
80 judged `conditional` runs put an editing response's trap pass rate at 24/39
against 22/41, p = 0.5055, so the diagnosis does not migrate into the diff.
That evidence is about a single-turn case and would have to be re-established
across turns.

**What would not be worth buying is reps on these two cases.** The open
questions are identification problems, not sample-size problems: more
turn-responses tighten 0.92% a little and cannot distinguish "the rule never
breaks" from "the rule breaks only while editing", which is the question.

## Where the design came from

`bash tools/consult.sh` was run against the draft before any of this was
written, and two of three targets answered. Both changed the document:

- **`deepseek` and `kimi` independently demoted the depth claim.** The draft
  headlined the 68.0%-to-20.0% drop as *"the behaviour decays with depth"*.
  Both refused it on the same two grounds — the within-case series is
  non-monotone, and the cross-case contrast conflates depth with prior offers
  and accumulated context. `deepseek` added that `drift-service`'s own
  `expect.json` says what the case varies is *"how much of its own prior output
  the model carries"*, not depth. Reading 3 is a disclosure because of that,
  and its wording is close to `kimi`'s proposed sentence.
- **Both narrowed the null.** The draft said the archive *closes* [#113]'s
  binary half. `kimi` set out the mismatch between the reported session and the
  instrument as a table, and `deepseek` drew the line this document uses: what
  0 of 325 kills is the *depth-erosion mechanism*, since there is no gradient to
  correlate against; what stays open is failure under an editing regime the
  instrument excludes.
- **They split on whether to buy generations, and `deepseek`'s answer is the one
  taken.** `kimi` wanted two probes, an editing-session replication and a
  neutral-history baseline arm. `deepseek` argued both holes are identification
  problems rather than sample-size ones, and that an editing case is a new
  instrument with its own trap and `criteria_source` that belongs in a round of
  its own rather than retrofitted here. The repository's own record decides it:
  `quota-advice` and `queue-lag` were both built as instruments for [#116] and
  both withdrawn the same day for failing to elicit the behaviour they were
  built for.

Neither target proposed Reading 4, which was not in the question put to them —
the clustering test was written after the adjacent-pair table came back
inverted from the suppression mechanism both of them had raised.

`codex` was asked and did not answer inside the timeout.

## Cost

No generations, no judge calls, no `claude` CLI sessions. Nothing was spent from
a usage window that a round would have wanted.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#150]: https://github.com/JordanMPDS/laconic/issues/150
