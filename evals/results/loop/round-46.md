# Round 46: the incentive rather than the prohibition, and the chain component five edits have moved

**Registration. Nothing below the results line has been computed.** This file
and the rules text under test are committed in the same commit, before any
generation, following [round 38](round-38.md), [round 44](round-44.md) and
[round 45](round-45.md).

## Why this edit

[`lens-pilot-26.md`](lens-pilot-26.md) left five untried arrow mechanisms.
Two have been scored and both were rejected: [round 44](round-44.md) moved the
connecting-words claim into `Never cut` (41 arrows to 45, p = 0.830) and
[round 45](round-45.md) closed the quotation exemption (21 to 23, p = 0.8215).
The queue is three, and this round draws the one the pilot's second read
singles out as different in kind:

> **5 attacks the incentive rather than the prohibition.** Every prior edit
> changed the rule that forbids arrows; this one changes the `full` level's
> length budget on the theory that the budget is what creates the pressure to
> compress at the word level. Nothing in the archive refutes it. It predicts
> its own cost honestly — response length should rise — which is a design
> constraint for a round rather than a refutation.

That is the whole reason to prefer it over the other two remaining candidates,
and the reason is not a preference. Candidate 3 extends the `Never cut`
code-and-config bullet to cover a changed setting: it aims at the value
transition, which round 45 has now measured directly and found unmoved, from
inside the section round 44 found inert. Candidate 12 extends the `Never cut`
ordered-instructions bullet: another relocation into the section round 44
found inert. Both remaining candidates are combinations of two mechanisms this
loop has already scored and rejected. Candidate 5 shares a mechanism with
none of the seven arrow edits in [`arrows.md`](arrows.md).

**It is also the candidate that most separates the lens structure from a single
reader**, which is what [#26] is actually being asked. The pilot's unlensed
control reader did not merely miss this one — it considered the premise and
ruled it out:

> Its diagnosis says plainly: *"length pressure is not the driver … the fix is
> to close the scope loopholes and supply the sanctioned notation."* Candidate
> 5 is built on the opposite reading. One reader ruled that out; the reader
> assigned to look at compression built its central candidate on it. That is
> the clearest single instance of the lens changing what gets proposed rather
> than how it is worded.

Two scored candidates are two rejections, and the second was the one three of
five proposers converged on. If the lens structure is worth anything to this
loop, the disagreement is where it lives, and this is the disagreement.

## The target: chains, which is not where rounds 44 and 45 aimed

Both prior rounds registered total arrow count and both disclosed the same
unregistered split afterwards: `walkthrough` chains fell while mappings held or
rose. Round 44 read 9 chains to 4, round 45 read 15 to 0, and round 45 asked
that a later round test it deliberately:

> **a round targeting chains on `walkthrough`, registered as such, at reps
> sized for a 5-of-40 base rate.**

This is that round, and the pattern is older than those two rounds.
`metrics.arrow_forms` documents it for rounds 16, 17 and 18 in its own
docstring:

    form        baseline  r16  r17  r18
    chains            96   61   49   56
    two-term maps     44   56   61   55
    total            140  117  110  111

**Five edits, five falls in the chain component, and no round has ever
registered it as a hypothesis.** Every one of those five was scored on the
total, which sums a falling component with a flat or rising one and reports
the average of the two.

**Candidate 5 predicts the chain component specifically, and this is the second
independent reason to register it here.** A chain — `a → b → c` — is a
multi-step sequence compressed onto one line, which is exactly the artifact the
candidate's mechanism describes: a model that keeps every claim the request
earns and pays the shape budget at the word level. A mapping — `` `legacy` →
`split`` `` — is a naming idiom with no sequence in it and no words to save. So
the candidate is a sharper prediction than its own author made: chains fall,
mappings do not.

**And this edit never says "arrow".** That is what makes it a usable test of
the chain lead, which two arrow-rule edits could not be: if chains fall under
an edit that never mentions the prohibition, the fall is not the file saying
"arrows" one more time.

## The archive base rate, from this era

`walkthrough`/sonnet, laconic arm, master rules, the two control sides
generated beside rounds 44 and 45:

| control | n | arrows | carrying one | chains | chain-carrying | mappings | median words |
|---|--:|--:|--:|--:|--:|--:|--:|
| round 44 | 40 | 41 | 14 | 9 | 4 | 32 | 467.0 |
| round 45 | 40 | 37 | 13 | 15 | 5 | 22 | 500.5 |
| **pooled** | **80** | **78** | **27** | **24** | **9** | **54** | — |

Chain-carrying responses run at about 11%, which is the whole difficulty: 40
responses hold four or five of them. Both figures are quoted for sizing only.
**The registered baseline is this round's own control**, per round 31's lesson
and round 45's instrument note, which read the same cell at 21, 26 and 46-of-80
carrying an arrow at byte-identical rules.

## The edit

One edit, to the `full` level's closing shape budget, taken verbatim from the
pilot's candidate rather than rewritten — a rewrite would score my wording
instead of the one the lens produced.

```diff
 Typical shape: one to three sentences, or a short list. One sentence is a
-complete answer.
+complete answer. That budget counts claims, not the words inside one — a
+question that earns eight claims gets eight lines, each written out in full,
+not eight compressed ones.
```

The arrow prohibition, its four `Wrong:`/`Right:` lines, the enumeration and
the fenced-code exemption are all untouched. **The file gains no rendered arrow
specimen and no new example pair**, so [#164] item 2 — pre-registering every
cell that carries a demonstrated form — stays out of this round, as it did in
rounds 44 and 45.

The edit lands between the `<!-- level:full -->` and `<!-- level:ultra -->`
markers, so it ships at `full` and `ultra` and not at `lite`. `lite` is
byte-identical (`rules_cksum` 1146585023 both sides); `full` and `ultra` each
grow by 28 words. The benchmark runs at `full`.

## Hypothesis

> Rewriting the `full` level's shape budget to count claims rather than the
> words inside one — the one untried mechanism that attacks the length
> incentive rather than the arrow prohibition — should lower chain-carrying
> responses on `walkthrough`, sonnet.

## Falsifier, registered before the batch

**Chain-carrying responses on `walkthrough` not separating at p < 0.05, or
separating upward.** Direction is registered because four of the seven prior
arrow edits moved the wrong way on their own target.

## The discriminant, and why `confirm-rollback` is in the batch

`confirm-rollback` is the negative control this hypothesis needs, and it is one
the archive has already characterised. Round 45 measured every arrow it carries:
46 of 46 across 80 archived responses are two-term mappings and **not one is a
chain**, all of them the parenthesis ``(`legacy` → `split`)``. It is also short
— 86 to 88 median words against `walkthrough`'s 467 to 500 — so it is the case
where the candidate's own second failure mode would show.

| `walkthrough` chains | `confirm-rollback` | reading |
|---|---|---|
| fall | flat | the shape budget is the pressure, and it produces chains and not mappings. The candidate works as described, and the chain lead of rounds 44 and 45 is not arrow-rule re-emphasis |
| fall | falls as much | not the mechanism: an edit that lengthens everything lowers every arrow form, and the round has bought compression with words |
| flat | flat | the incentive is not the carrier either. [#26]'s third scored candidate fails, the queue is two, and both of those are combinations of mechanisms already rejected |
| flat | falls | the edit moved a form its mechanism does not describe, on the case that carries none of it. An anomaly to record, not a pass |

## Registered harm checks

The first is fatal on its own and the other two are the never-cut screen rounds
44 and 45 ran. All three are substring or word counts over text this batch
generates anyway, so none costs a judge call.

1. **`confirm-rollback` median words rising, permutation p < 0.05.** This is
   the candidate's own stated failure mode — *"length rising in cases that
   should stay short … would mean the edit bought arrow reduction with padding,
   a net loss against the file's own thesis"* — and it rejects the round
   whatever the target did. A rise on `walkthrough` is **not** harm by this
   check: the candidate predicts it, calls it the intended trade, and asks that
   it be measured rather than treated as a regression. It is reported below and
   weighed at step 2, not here.
2. **`walkthrough` names `401`**, which round 30 and round 31 damage would show
   in. Rounds 44 and 45 both read 40 of 40 on both sides.
3. **`confirm-rollback` names `0042` or `settlement_currency`**, the
   load-bearing half of its trap. Round 45 read 33 of 40 against 36 of 40.

Reading rate is reported for every cell, because a fall bought by not opening
the fixture is the [#131] stratum crossing rather than a result.

## Commands

```sh
git worktree add /tmp/laconic-r46-control master

# pass 1, the two sides of `walkthrough`, simultaneously:
python3 evals/bench/run.py --arms laconic --models sonnet \
  --reps 100 --cases walkthrough --concurrency 2 \
  --snapshot evals/snapshots/loop/round-46-edit.json
cd /tmp/laconic-r46-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 100 --cases walkthrough --concurrency 2 \
  --snapshot <abs>/evals/snapshots/loop/round-46-control.json

# pass 2, the two sides of `confirm-rollback`, after pass 1 finishes:
python3 evals/bench/run.py --arms laconic --models sonnet \
  --reps 30 --cases confirm-rollback --concurrency 2 \
  --snapshot evals/snapshots/loop/round-46-edit-confirm.json
cd /tmp/laconic-r46-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 30 --cases confirm-rollback --concurrency 2 \
  --snapshot <abs>/evals/snapshots/loop/round-46-control-confirm.json
```

260 generations, no judging. The two sides of a case run simultaneously, per
round 38, so era and regime cancel between them rather than confounding them.

**Four snapshots rather than round 45's two, because the two cases run at
different reps.** `--reps` is per invocation, and a snapshot's `cases_cksum`
covers exactly the case set it was created with, so resuming
`round-46-edit.json` with a second case would trip the [#69] guard and need an
`--allow-case-change` override that would misdescribe what happened. Two files
per side is the honest shape.

**`--concurrency 2` on all four**, because two CLI processes are in flight at
any moment and never four: pass 2 starts when pass 1 finishes. The declaration
describes the file, which is round 42's correction on the same field. Control
at `rules_cksum` 136269960, edit at **2741667431**.

Both cases are single-turn, so `--turn-delivery` does not apply and the batch
carries no multi-turn work.

## Scoring

`metrics.arrow_forms(text)`, which splits the arrows
`metrics.score(text)["symbol_connectors"]` counts into chains (two or more on a
line) and mappings (one), and whose components always sum to the total.

- **Primary: responses carrying at least one chain**, Fisher exact, two-sided.
  This is the statistic the base rate and the power below are computed on.
- **Secondary: chain arrow count**, by permutation of the side label over the
  per-response counts, 200,000 resamples, seed 46.
- **Disclosure, registered here so the second look is not a new one:** total
  arrows, mappings, and median words on both cases.

## Power, stated before the numbers

Against a control at 11 of 100 — the pooled rate above — this round reads a
disappearance at Fisher p = 0.0007, a fall to 2 of 100 at p = 0.0184 and a fall
to 3 of 100 at p = 0.0489. **It does not detect a halving:** 5 of 100 reads
p = 0.1913.

So the round is sized to resolve a disappearance or a fall of about three
quarters, and nothing smaller. That bound is the reason for 100 reps rather
than round 45's 40, and it is still the honest limit: the two prior edit sides
read 4 of 40 and 0 of 40, so a real effect of the size those suggest lands
inside this round's reach and a modest one does not.

## Cost

260 generations, 0 judgments. Roughly $13 API-equivalent, bought from a usage
window rather than an API budget.

## What this round does not buy

The round-wide laconic arm, the fatal counters, judging, `cold-service` — which
the candidate also names and which this round leaves untested — and any model
but sonnet. The staged rule stops at the first step that fails, and a passing
primary here does not accept the edit: it sends it to step 2, where
`output_tokens` and the four fatal counters would have to hold against an edit
that predicts its own inflation.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#164]: https://github.com/JordanMPDS/laconic/issues/164
