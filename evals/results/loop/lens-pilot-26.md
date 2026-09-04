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
