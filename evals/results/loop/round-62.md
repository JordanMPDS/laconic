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

**180 generations, 0 failed. 180 judgments, 0 judge failures. One `rules_cksum`
(594915793, unchanged from round 61), one CLI release (2.1.267), sequential,
safe mode off on both arms as registered, two delivery probes (one per shard).
$23.18.**

**The primary fired, in the registered direction, and it is one detector.**

| endpoint, fired stratum | `laconic-enforced` | `laconic-enforced-reminder` | |
|---|--:|--:|---|
| **any level-`full` finding on the final response** | **1/22 (4.5%)** | **11/18 (61.1%)** | **p = 0.0002** |
| the target detector still fires | 1/22 (4.5%) | 8/18 (44.4%) | p = 0.0055 |
| a finding not present before the revision | 0/22 | 0/18 | — |

**+56.6 points, 95% CI [+28.2, +75.5]**, Fisher two-sided p = 0.0002, one-sided
p = 0.0001. The within-cell permutation test on the arm label registered in
advance agrees: observed difference +0.566, one-sided p = 0.00027 over 200,000
permutations at seed 62. Per cell, `walkthrough`/haiku reads 1/14 against 8/12
and `walkthrough`/sonnet 0/5 against 3/6, both in the same direction.

The effect is larger than the round was designed to see. The registered power
table gave 94% at a 40-point difference and the observed one is 57.

### The whole difference is `preamble`, and that is the finding

Scored per detector — of the blocks where a detector was present, how often it
still fires afterwards:

| detector | `laconic-enforced` | `laconic-enforced-reminder` |
|---|--:|--:|
| `preamble` | **0/16** | **11/12** |
| `symbol_connectors` | 1/6 | 0/9 |

**An unnamed block clears the arrow every time and the preamble almost never**
(p = 5.6e-07 on the `preamble` split; the arrow split is 1/6 against 0/9,
p = 0.400, if anything the other way). Told only that it broke a rule, the model
reliably finds a `→` in its prose and reliably does not consider `Here's the
token refresh flow:` a violation of anything. The residuals are not subtle and
not artefacts: eleven of the twelve reopen with a fresh preamble in the answer
proper.

The three responses in the `reminder` arm where two detectors fired say the same
thing from inside one response. All three were `preamble` plus
`symbol_connectors`, and all three came back with the arrow gone and the
preamble intact.

**So the round answers [#283]'s shipping question, and the answer is no.** The
block has to quote the rule. A hook that ships a sentence would clear the
readability findings that a model already agrees are wrong and leave the ones
the rules exist to teach — which are the ones the plugin is for. The shipped
mechanism needs `metrics.POLICY_RULE` down both paths, and the maintenance
burden [#283] priced is the price of the mechanism working at all rather than an
implementation detail that could be optimised away.

### The registered artefact control worked

Round 61's only residual was the model quoting its own offending line back
inside a `Found it — ... Rewritten:` preamble, and this round added a
no-commentary sentence to both reasons to stop that from loading the `reminder`
arm differentially. **No residual in either arm is that artefact.** All eleven
`reminder` residuals are ordinary preambles in the answer, and the single
`named` residual is not commentary either — it is an arrow the revision left in
a markdown heading:

> `## Normal flow: `currentToken()` → `refresh()``

which is the one place the rewrite did not look, having cleared the arrows from
the prose around it. The `symbol_connectors` detector does not distinguish a
heading from a sentence and the rule it implements says "inside a sentence", so
this is a detector-scope observation rather than a rule violation, and it is
reported rather than screened.

### Guardrails, all null and all bounded rather than certified

| guardrail | `laconic-enforced` | `laconic-enforced-reminder` |
|---|--:|--:|
| `safety_fails` (`walkthrough`, ITT) | 0/60 | 0/60 |
| `quality_fails` (`fail-open`, ITT) | 0/30 | 0/30 |
| never-cut keyword failures (all runs) | 0/90 | 0/90 |
| reading rate, a `Read` in the fixture workspace | 90/90 | 90/90 |

**The judge returned `pass` on all 180 runs and no `not_exercised`.** So the
worry that drove the guardrail — a model hunting for an unnamed violation and
mangling the answer — did not show up, and neither arm is distinguishable from
the other on quality or safety. The rule of three bounds a safety failure rate
at about 2.5% per arm and a never-cut failure at about 1.7%; the reading rate is
at ceiling in every cell and certifies nothing beyond not being destroyed. This
is a smaller judged design than round 61's and it agrees with it.

**The `reminder` arm rewrites rather than edits.** Word delta from pre-revision
to post-revision: `named` median **−6** words on a median 349.5-word original,
16 shorter and 6 longer; `reminder` median **+6** on a median 363.0-word
original, 3 shorter and 12 longer. Round 61 reported surgical revisions at a
median of −3, and the `named` arm replicates that. A model that has to find the
violation itself produces a different kind of revision, and a longer one.

### Balance, as registered

The fire decision is pre-treatment and any difference is sampling noise, so
these are checks that the design ran as described rather than findings:

- **Fire count 22/90 against 18/90** (p = 0.5910), pooled fire rate 40/180 =
  22.2% [16.8%, 28.8%].
- **Detector mix at fire**: 16 `preamble` and 6 `symbol_connectors` under
  `named`, 12 and 9 under `reminder`.
- **Co-firing responses**: 0 under `named`, 3 under `reminder`. This is the
  imbalance that matters most and it went the wrong way for [#283]'s other
  leftover — the named-against-unnamed residual estimator needs co-firing in the
  **named** arm, and there was none again. Two rounds have now failed to supply
  it on these cells, and the estimator needs a scope chosen to produce co-fires
  rather than one chosen for fire rate.
- **`fail-open`/haiku fired 3/30 under `named` and 0/30 under `reminder`**, so
  that cell contributes nothing to the primary. Its fire rate was 2/10 in round
  61 and the round planned for about 6 per arm; it delivered 3 and 0. The
  primary rests on `walkthrough` at both models.

### Cost

Within model, arm medians are $0.0572 against $0.0566 on haiku and $0.1827
against $0.1891 on sonnet. Inside each arm the cost is on the responses the hook
fires on: blocked haiku responses cost $0.0650 at 19.8s under `named` and
$0.0708 at 29.0s under `reminder`, against $0.0561 and 13.2s unblocked. **The
unnamed block is the more expensive one** — it takes longer and produces a
longer answer while clearing less.

### Three disclosures

**The round was generated as two shards and merged, and it did not plan to be.**
`cases_cksum` covers the cases an invocation names, so a second invocation into
the same snapshot scoping to `fail-open` was refused by the [#69] guard even
though no case file had changed — the guard cannot tell a narrowed scope from an
edited case, and `--allow-case-change` would have stamped the snapshot with a
claim that was false. `evals/bench/merge.py` is the supported path and
recomputes `cases_cksum` over the union, which is what was used. The cost is
that `merge.py` sets `concurrency_declared` to at least the shard count, so the
merged file declares 2 for a round that ran strictly sequentially;
`max_runs_in_flight` reconstructs to 1 from the timestamps and the two together
say what happened. **A round whose cells are not a full case-by-model cross
product cannot be generated in one snapshot**, and that is [#285].

**The judged denominators are thin on quality.** Only `fail-open` is
quality-graded here and it contributes 30 runs an arm, against round 61's two
quality cells. A round scoped for fire rate is not scoped for judging, and the
0/60 above should be read as "nothing visible at this size" rather than as
evidence of equivalence.

**Every workspace picked up a `.remember/` tree.** An unrelated plugin's hooks
write into the generation workspace, and `run.py`'s workspace diff ([#231])
records them as artifacts the response authored. They appear in both arms
identically and nothing in this round reads the artifact field, so no number
here is affected — but the committed snapshot carries them and a later reader
should not mistake them for model output.

[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#285]: https://github.com/JordanMPDS/laconic/issues/285
[#231]: https://github.com/JordanMPDS/laconic/issues/231

### What [#283] gets, and what it does not

**The reminder-only variant is answered and it loses.** The comparison the issue
said was buyable on the same cells was buyable, and the block needs the rule
quoted. `kimi`'s argument before round 61 — that naming the rule tests
enforcement-as-instruction rather than enforcement-as-reminder — is right about
the distinction and the distinction turns out to matter: this mechanism works as
an instruction, and as a reminder it works only on the violations the model
would have agreed with anyway.

**The shipping half of [#283] is not answered and this round does not move it.**
Round 61 left it open on a null primary, this round's judge is null again at a
smaller size, and nothing here says a `Stop` hook should ship. What it does say
is that if one ships, it ships the table.
