# The `fragment` criterion

The labelling rule for #11's telegraphic-fragment detector. Committed before any
label was written, for the reason `restatement/criterion.md` records: a criterion
written after the errors are visible is a description of the detector, not a
standard it can fail against.

## The rule

`rules/laconic.md` forbids one thing, in four words:

> No telegraphic fragments.

A **segment** is one sentence of running prose, or the body of one bullet or
numbered item.

A segment is a **fragment** when it is presented as running prose and carries no
finite verb, so that a reader supplies one to parse it.

    Critical for race conditions
    All 20 connections in use (idle=0) at every checkpoint
    Monitoring/alerting for tokens still using old key
    Harmless in practice, just inconsistent with the rest of the dedup story.

Each of those is a predication with the verb removed. That is the defect the rule
names, and it is the only thing this criterion counts.

## Not fragments

Four shapes lack a finite verb and are correct English anyway. None of them is
running prose, and counting them would make the metric a count of markdown.

- **A list lead-in.** `Two options:` introduces the list that answers it. The
  sentence continues into the items.
- **A heading or a bold label.** `**Normal path — currentToken (auth.js:6-10)**`
  is a section title set in bold, and a title takes no verb.
- **A definition gloss.** `-type f — only regular files (excludes directories)`
  glosses the term the bullet names. A glossary entry takes no verb either, and
  `code-fidelity` is a case about `find` flags, so the corpus is full of them.
- **A residue of code stripping.** Every detector here runs on code-stripped
  prose, so `: (same kind of rounding discrepancy)` is what is left of a line
  that was mostly an identifier. There is not enough prose left to judge.

## Ellipsis is a fragment

The one judgement call. An elliptical answer — `UUID — specifically UUIDv7 (or
ULID), not a random v4.` — drops "use" rather than a copula, and reads as a
deliberate style rather than as broken grammar.

It is labelled a fragment. The rule does not carve out ellipsis, the reader still
supplies the verb, and exempting it would let a detector be tuned by arguing
about intent. Recorded here so that a later reader can subtract these if they
disagree: they are marked `"elliptical": true` in `labels.json`.
