# Four lenses on one dead end: [#26]'s pilot

**Registration. Committed before a single candidate was read.** Everything above
the results line — the design, the classification scheme, the decision rule and
the prediction — is fixed in advance, because the question this pilot asks is
whether a proposer produces something new, and a scheme written after reading
the candidates would classify whatever arrived.

## Why this exists

[#26] defers multi-agent candidate generation on an explicit trigger: *"several
consecutive rounds rejected at step 7 for a failed hypothesis rather than a
failed gate."* [`rejection-modes.md`](rejection-modes.md) classified all 28
stored rounds and the trigger is met — the last three rule-edit rounds are all
hypothesis failures, and each moved the wrong way rather than landing inside the
noise floor.

The issue's own comment declines to treat that as a green light, and names the
cheap thing to run first:

> Take one of the two dead ends and ask for candidates through the four lenses
> this issue names — never-cut, compression, readability, answer quality — and
> see whether **any lens produces an edit the single-reader loop did not already
> try**.

That is this pilot. It tests the assumption the whole approach rests on: that
the loop is short of ideas rather than short of places left to aim.

## The dead end, and why this one

Arrows. Six rounds, five rule edits, no accepts, indexed in
[`arrows.md`](arrows.md), which ends *"there is no form-shaped hole to aim at."*
It is the sternest of the two available tests: the over-length cluster has one
rejected structural attempt, and arrows has five rejected edits across three
distinct mechanisms, so "already tried" is answerable there with the most
confidence.

## The design

Four proposers, one lens each, **blind to every prior attempt**. Each works from
two files copied outside the repository:

- `rules/laconic.md` as it ships today.
- A failure inventory built for this pilot: every arrow-carrying line from the
  3,017 laconic responses in the archive generated at `rules_cksum` 136269960,
  the revision that ships. 225 responses carry at least one, 502 arrows in
  total, grouped by case and model, worst first, six responses sampled per
  group.

None of them sees `arrows.md`, `LEDGER.md`, any round document, the issue
tracker or the git log. **That blindness is the whole instrument.** A proposer
shown the list of five rejected edits would avoid them by construction, and
novelty produced that way answers nothing; a proposer that has never seen the
list either reproduces the loop's own reasoning independently, or does not.

Each returns up to three candidate edits with its mechanism and target cells, so
the pilot has twelve draws rather than four.

## Classification, fixed in advance

Every candidate is classified into exactly one of:

- **tried** — materially the same edit as one of the five in `arrows.md`: same
  mechanism, same location in the file.
- **variant** — a different wording or position of a mechanism a round has
  already scored, where that round's finding already speaks to it. Any sixth
  addition to the enumerated prohibition is a variant by this definition:
  rounds 01, 03 and 04 each added a position and each saw arrows appear in a
  position another covered.
- **new** — a mechanism no round has tried.

Each classification names the round it is matched against, so the call is
auditable rather than asserted.

A **new** candidate is then read a second time against the six findings
`arrows.md` records, and marked **new, and survives** or **new, but refuted by
round NN**. The second read is what separates an untried idea from a good one.

## The decision rule

- **Zero candidates classify as new.** The constraint is the target space and
  not the proposer, on this target. [#26] does not advance on this evidence.
- **At least one classifies as new and survives the second read.** The premise
  holds for at least one lens. The next unit is deciding whether that candidate
  earns a scoped round — **not** building the workflow, which this pilot cannot
  speak to.
- **New candidates that all fall to a round's finding.** Reported as its own
  outcome: the lenses reach untried ideas, and the untried ideas are ones the
  archive can already refute without spending a round.

## The prediction

**Fewer than two of the twelve classify as new.** Registered because
`arrows.md`'s conclusion predicts it, and a pilot whose author expected the
other answer would be worth reading differently.

## What this pilot may not claim

Not that multi-agent generation improves the loop. It tests one assumption, on
one target, with four proposers and one sampling of each. A null here says the
arrow target is exhausted, which `arrows.md` already argued from the other
direction; it does not say lenses would fail on a target with unexplored
surface. And it buys no generation calls, so nothing here is evidence about what
any candidate would do to a benchmark.

[#26]: https://github.com/JordanMPDS/laconic/issues/26

---

# Results

**Six of twelve candidates classify as new, across five distinct mechanisms, and
all five survive the second read. The registered prediction fails.** Nothing was
classified **tried**: no proposer reproduced one of the five rejected edits
outright.

## The twelve

| # | lens | the candidate, in one line | class | matched against |
|---|---|---|---|---|
| 1 | never-cut | Headline to "No arrows anywhere in your own prose", naming bullet, list item, table cell, heading and bold label; plus "not to pair a condition with what it does" in the enumeration | variant | round 03, plus round 01 for the added clause |
| 2 | never-cut | **Move** the connecting-words claim out of the style section into `Never cut` as its own bullet, deleting the sentence it replaces | **new** | — |
| 3 | never-cut | Extend the `Never cut` code-and-config bullet: a setting that changed keeps both values *and* the word for the change | **new** | — |
| 4 | compression | Append to the section's first paragraph: a bullet, a numbered step and a line after a bold label are sentences, and every rule in the section reaches them | variant | round 03 |
| 5 | compression | Rewrite the `full` level's shape budget to say it counts claims, not the words inside one | **new** | — |
| 6 | compression | Extend the fenced-code exemption: an arrow *between* two quoted things is not itself quoted | **new** | — |
| 7 | readability | Headline to "No arrows outside a fenced code block", replacing the context enumeration with one boundary | variant | round 03 |
| 8 | readability | Replace the exemption sentence: an arrow is allowed only *inside* quoted material, and name the value-change form | **new** | — |
| 9 | readability | A third `Wrong:`/`Right:` pair for the single-arrow condition bullet | variant | round 31, and round 03's branch-list example |
| 10 | quality | Replace the context enumeration with a relation test — an arrow stands in for a word, so write the word | variant | round 04 |
| 11 | quality | Add single-arrow `Wrong:`/`Right:` examples for the value assignment and the mapping | variant | round 31 |
| 12 | quality | Extend the `Never cut` ordered-instructions bullet: an arrow is not one of the words that fix an order | **new** | — |

Candidates 6 and 8 are the same mechanism reached independently by two lenses, so
the six new candidates are five distinct mechanisms.

## The second read

Each new candidate against the six findings `arrows.md` records:

- **2 and 12 relocate the claim into `Never cut`.** `arrows.md` names a
  structural move as the first of the three things the evidence leaves open, and
  says *"Nothing has tried that here."* It survives — with a risk the archive
  can already name. Rounds 07, 08 and 09 put a design-question **licence** into
  that same list and `ordered-steps`/haiku read 6, 3 and 5 against a baseline 2;
  round 10 fixed it by moving the licence out. So `Never cut` placement has
  propagated outside its scope before, in the direction opposite to this one.
  That is finding 6's propagation problem, and a round running either candidate
  has to pre-register the cells that carry it.
- **3 and 6/8 target an idiom no arrow round has seen.** Both aim at the value
  transition — ``(`legacy` → `split`)`` — which lives almost entirely in
  `confirm-rollback`, `deep-rollback` and `recall-rollback`. Those three cases
  were added after the arrow work stopped. No finding speaks to them.
- **5 attacks the incentive rather than the prohibition.** Every prior edit
  changed the rule that forbids arrows; this one changes the `full` level's
  length budget on the theory that the budget is what creates the pressure to
  compress at the word level. Nothing in the archive refutes it. It predicts its
  own cost honestly — response length should rise — which is a design
  constraint for a round rather than a refutation.

## What that settles, and what it does not

**`arrows.md`'s finding 4 is too strong as written.** *"There is no form-shaped
hole to aim at"* is true of the thing it was measuring — the four revisions all
lowered chains and mappings evenly, and a sixth enumeration is still the move
the evidence argues against. Every enumeration-shaped candidate here classified
as a variant, which is that finding holding. What the finding does not support
is the wider reading that the target is exhausted: the five new mechanisms are
all edits that are not enumeration edits, and `arrows.md` itself named the first
of them as untried.

**But this pilot cannot separate the lens effect from the inventory effect, and
that is its main limitation.** The inventory built for it sweeps 3,017 responses
across 37 cases; every arrow round read between 40 and 180 responses over 22.
Three of the five new mechanisms target case groups that did not exist when the
arrow work stopped. A single reader given this same inventory might have reached
them too, and if so the constraint that moved is the evidence, not the number of
proposers — which is a different conclusion about [#26], and a cheaper one to
act on.

**So [#26] advances by its own decision rule, and the thing to decide next is
not the workflow.** The rule says: at least one new candidate surviving means
the next unit is deciding whether a candidate earns a scoped round. That still
holds. But the confound above has to be resolved first, because it changes what
the pilot is evidence *for*.

## An unrelated finding the inventory turned up

`arrows.md` finding 3 says *"`walkthrough` is the residual, and it is still the
worst case in the set."* Over the whole archive at master rules it is not:

| case / model | responses carrying an arrow |
|---|--:|
| `confirm-rollback` / sonnet | 20 / 40 (50%) |
| `walkthrough` / sonnet | 60 / 180 (33%) |
| `verdict-rollout` / haiku | 6 / 20 (30%) |
| `cold-service` / sonnet | 9 / 35 (26%) |
| `walkthrough` / haiku | 27 / 110 (25%) |

`confirm-rollback` and `cold-service` are single-turn cases added after the arrow
work stopped, so no arrow round has ever scored them.

**Read this as a lead, not as a result.** The rates pool across eras, and round
37 measured a syntactic behaviour moving 4.7x in five days at byte-identical
rules, so a pooled rate is exactly the quantity that finding says not to trust.
No snapshot holds both cases, so the archive cannot supply a within-era
comparison; the nearest is 2026-09-02, `confirm-rollback`/sonnet 7 of 10 in
`round-40-control.json` against `walkthrough`/sonnet 3 of 5 in
`opus-model-set.json`, which separates nothing at that n.

Multi-turn cases are excluded from the table, because their arrow rate tracks
`--turn-delivery` rather than the case: `deep-rollback` reads 8 of 10 under
`repeat` and 0 of 10 under `plugin`, the same length effect
[`turn-delivery.md`](turn-delivery.md) records.

## The control, registered before it runs

**One reader, no lens, same inventory, same blindness, same budget of three
candidates.** It is asked for candidates the way the loop's own step 4 asks —
read the inventory, propose the edit — with no lens assigned.

- **If it reaches any of the five new mechanisms**, the inventory did the work
  and the lens structure did not. [#26]'s premise is then not supported by this
  pilot, and the cheap thing that actually helped is a wider inventory, which
  costs nothing and needs no workflow.
- **If it reaches none of them**, the lens structure is what produced the
  novelty, and [#26] has its first real evidence.
- **If it reaches one or two**, that is reported as the partial result it is.

This is one subagent and no generation calls. Registering it here, before it
runs, for the same reason everything above the results line was registered.

## Files

- [`lens-pilot-26/arrow-inventory.md`](lens-pilot-26/arrow-inventory.md) — the
  instrument, exactly as the proposers received it.
- `lens-pilot-26/lens-{nevercut,compression,readability,quality}.md` — the four
  reports verbatim, unedited. The classification above is only auditable against
  these.
