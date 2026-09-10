# Round 62 — does the block have to quote the rule?

**Registered 2026-09-10, before any run. No rule edit.** The second round to
change the mechanism rather than the text. `rules/laconic.md` is byte-identical
between the two arms and unchanged from round 61, at `rules_cksum` 594915793.

## Why the round exists

[#283] is round 61's leftover, and it is a shipping question rather than a
curiosity.

Round 61 measured a `Stop` hook that reads the completed turn, runs the
benchmark's own deterministic detectors, and — when one fires — blocks the turn
with a reason quoting **one** rule line verbatim from `metrics.POLICY_RULE`,
asking for a single rewrite. Responses carrying a level-`full` finding fell from
12/60 (20.0%) to 1/60 (1.7%), Fisher p = 0.0020. Twenty rounds of rule edits
have never moved that number that way. The blind judge could not tell the arms
apart, which was the registered primary and is why round 61 did not itself
license shipping.

Shipping the hook means a bash path and a PowerShell path kept in sync, per
`AGENTS.md`. **Both need the detectors. Only the quoting version additionally
needs `metrics.POLICY_RULE`** — the detector-to-rule-text table, whose entries
are verbatim lines of `rules/laconic.md` and which `tests/test_bench.py` already
has to police against drift in one implementation. Carrying it down two more is
the largest single piece of the maintenance burden [#283] says round 61 did not
buy, and it is the piece most likely to rot silently: a rule line edited in
`rules/laconic.md` and not in the PowerShell table ships a hook that quotes text
the model was never given.

So: **does the block need the rule quoted, or does the signal alone suffice?**
If a sentence works as well as the table, the shipped mechanism is materially
smaller and has one fewer thing that can drift.

Round 61 declined this variant for `codex`'s reason — a null under vague
feedback cannot distinguish a weak mechanism from underspecified feedback. That
argument does not survive round 61's own result. The named variant did **not**
return a null on the mechanism, so the comparison is now against a working
reference rather than against nothing, and it is buyable on the same cells.
`kimi` argued for it before round 61 and this round is that argument bought.

## The arms

Both generated in one interleaved pass, arms innermost, so they are sampled at
adjacent moments and no CLI release can correlate with an arm. Same rules text,
resolved from one `hooks/laconic.sh` call; same detectors; same fire condition;
same one-rewrite ceiling. **The only difference is one sentence of the block
reason.**

| arm | first sentence of the block reason |
|---|---|
| `laconic-enforced` | `Your completed reply broke this rule, which was already in your instructions: "<rule>".` |
| `laconic-enforced-reminder` | `Your completed reply broke one of the rules that was already in your instructions.` |

Both then continue, identically:

> Rewrite the reply once so it complies, keeping every piece of content the
> answer needs. Do not satisfy the rule by swapping punctuation or wording while
> leaving the problem in place. Reply with only the rewritten answer and no
> commentary.

Safe mode is off on both arms, as in round 61 and for the same reason: hooks do
not run under `CLAUDE_CODE_SAFE_MODE=1`, so it has to be off for the treatment,
and a regime differing between arms would confound the mechanism with the
regime. `metadata.safe_mode` is false, and this round's absolute rates are
therefore not comparable with the pre-round-61 archive's.

### Two deviations from round 61's reason, and why each is there

**The last sentence is new, and it is in both arms.** Round 61's single residual
was not a surviving violation: the response rewrote the offending line correctly
and then prepended `Found it — "No refresh token → throws" used an arrow.
Rewritten:`, and the detector fired on the arrow *inside that quotation* — on
commentary the block reason itself caused. A reason that does not name the rule
invites exactly that narration. Left alone, the artefact would load the
`reminder` arm differentially and could manufacture this round's entire effect
out of nothing. `codex` argued for suppressing it in both arms on
`tools/consult.sh` and that is what is done; `kimi` argued the other way, for
keeping round 61's text byte-identical and classifying residuals after the fact,
which was rejected because the classifier would be a hand-rolled phrase list
sitting next to the primary.

**The cost of that choice is stated in advance: this round's `laconic-enforced`
arm is an internal replication of round 61, not a reuse of its number.** Any
comparison drawn to round 61's 1/60 is descriptive and across passes.

**The `reminder` reason does not say "find it".** `codex`'s point, adopted: an
extra instruction is a second difference between the arms, and it is the one
most likely to provoke the narration the last sentence exists to stop. The arms
differ in rule specificity and in nothing else.

## Scope

The three highest-firing cells from round 61's scan of stored `laconic` runs at
this `rules_cksum`, which is where the shipped rules demonstrably fail:

| cell | archive finding rate | round 61 fire rate |
|---|--:|--:|
| `walkthrough`/haiku | 15/15 (100%) | 5/10 |
| `fail-open`/haiku | 7/16 (44%) | 2/10 |
| `walkthrough`/sonnet | 5/15 (33%) | 2/10 |

**Three cells, 30 reps a side: 180 generations plus one delivery probe, then
180 judgments.** Round 61's pooled fire rate on these three cells was 9/30
(30%), so the expected fired stratum is roughly 25 to 30 per arm; the archive
rates are higher and round 61 flagged its own `walkthrough`/haiku shortfall at
p = 0.0522, so 40 per arm is possible and is not planned for.

`walkthrough` carries a never-cut safety contract — the answer must keep the 401
path — so it is where a forced rewrite under vague feedback can do real harm.
`fail-open` is quality-graded against a fixture that has to be read.

`design-upload`, round 61's third case, is dropped: it fired 1/10 there and it
is the cell whose `not_exercised` rate made its own judged denominators thin.
Two cases rather than three is the cost, and it is paid to put the reps where
the mechanism can be observed at all.

## Registered endpoints

**Primary, and the decision endpoint: the residual level-`full` finding rate on
the final response, within the fired stratum, `reminder` against `named`.**

Conditioning on firing is legitimate here in a way it was not in round 61, and
the argument is the round's foundation so it is stated plainly. The arm's
treatment — which block reason — is revealed only *after* the fire decision, and
the fire decision is made by identical detectors on text generated before any
arm-specific input existed. The fired subpopulation is therefore the same
function of the same pre-treatment distribution in both arms, and the estimand
is the effect among fired responses, which is exactly the population a shipping
decision is about. Both `codex` and `kimi` were asked this directly and both
confirmed it independently; round 61's fired stratum was confounded because it
compared against *control* responses that never carried a hook, which is a
different comparison.

**Registered as superiority, one-sided, in the direction expected, and a null
does not license shipping the sentence.** Rounds 58 and 59 ran non-inferiority
tests at n = 90 to 120 and returned `inconclusive` three times in four; at
n ≈ 27 a non-inferiority framing on this endpoint is guaranteed to buy nothing,
and widening the margin to make it pass is what pre-registration exists to
prevent. Both targets said the same. Power, from `codex`'s table at 27 fired
responses an arm and a one-sided exact test at alpha = 0.05, against a `named`
residual near 10%:

| `named` residual | `reminder` residual | power |
|---:|---:|---:|
| 10% | 30% | 46% |
| 10% | 40% | 77% |
| 10% | 50% | 94% |

**So the round is honest about what it can see: a 30-point harm, reasonably; a
20-point harm, not.** The effect expected is larger than either, because several
of the detectors are conventions rather than things a model would guess it had
violated — round 61's twelve control findings were seven `preamble`, four
`symbol_connectors` and one `sentence_initial_lowercase` — and a model told only
that it broke *a* rule has to guess which.

Reported with exact counts, a Fisher exact p-value and a confidence interval on
the difference, and as a permutation test on the arm label **within cell**, so
the inference matches the allocation rather than pooling three cells that fire
at different rates.

**Secondaries, all deterministic and free from the stored hook record**, which
holds the pre-revision text, the post-revision text, the detectors that fired on
each, and the target detector in both arms:

- **Target clearance** — whether the detector the hook selected (`record.named`,
  recorded under `reminder` too, `codex`'s point: without it, a response with
  two findings could clear either one and "did it fix the right thing" is
  unanswerable) still fires on the final response.
- **Introduced findings** — detectors present on the final response that were
  not present before it. This is the flail hazard: a model hunting for an
  unnamed violation can break something that was not broken.
- **Word delta**, pre-revision to post-revision. Round 61's revisions were
  surgical at a median of −3 words; a `reminder` arm that rewrites wholesale is
  a different mechanism wearing the same label.

**Guardrails:**

- `quality_fails` and `safety_fails` from the blind judge, arm against arm, over
  all 180 runs. Round 61 established the named hook costs no measured quality or
  safety; the unnamed one is a *new* hazard and gets its own reading.
- **Never-cut keyword failures**, deterministic, on `walkthrough`. A rewrite
  that complies by deleting the 401 path is the specific harm vague feedback
  could cause, and this detector sees it without a judge.

**Balance checks, not gates:** fire count, fire rate per cell, and the mix of
detectors that fired, per arm. All three are determined pre-treatment and any
difference is sampling noise, so a large one is a signal that something about
the allocation is wrong rather than a finding. `codex` argued for assigning the
reason at the moment the hook fires, which would balance the fired stratum
exactly rather than in expectation; that is declined because run.py's run key,
interleave, judging and reporting are all keyed on the arm, and a treatment
living only in the hook record would be invisible to every one of them. These
checks are what is given up in exchange, and reporting them is the price.

## Where the design came from

`bash tools/consult.sh` was run against all three delegate targets before
anything was built. `codex` and `kimi` answered; `deepseek` did not — its
configured model is not in this CLI release's catalogue. What was adopted, and
from whom:

- **The no-commentary sentence in both reasons, and dropping "find it" from the
  unnamed one** — `codex`. Adopted, over `kimi`'s post-hoc residual classifier,
  and the cost to round-61 comparability is disclosed above.
- **Recording the target detector in both arms** — `codex`. Adopted; it is what
  makes target clearance a well-defined secondary when more than one detector
  fires.
- **The fired stratum is a legitimate primary here** — both, independently.
  Adopted as the decision endpoint.
- **Superiority rather than non-inferiority, and a null that does not license
  shipping** — both, independently. Adopted, with the power table stated in
  advance.
- **Keeping three cells rather than pooling into `walkthrough`/haiku for a
  higher fire count** — `kimi`, explicitly: a shipping decision needs the
  mechanism to hold across model and case, and one cell cannot say that.
  Adopted.
- **A within-cell permutation test rather than a pooled Fisher** — `codex`.
  Adopted, and reported alongside the pooled figure rather than instead of it.
- **Not adopted:** `codex`'s fire-time randomisation of the reason, for the
  harness reason given above.

## What this round cannot answer

It compares two block reasons on two cases and two models. It cannot say whether
post-hoc enforcement should ship — round 61 left that open and this round does
not close it — and a `reminder` arm that performs as well as `named` is evidence
about the reason text, not a licence to ship either. It also cannot exercise
[#283]'s other leftover, the named-against-unnamed residual estimator, which
needs cells where detectors co-fire; whether any appear here is reported if they
do and registered as nothing.

[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#268]: https://github.com/JordanMPDS/laconic/issues/268
[#269]: https://github.com/JordanMPDS/laconic/issues/269
[#283]: https://github.com/JordanMPDS/laconic/issues/283

## Result

Pending: registered above, before generation.
