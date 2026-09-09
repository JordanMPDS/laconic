# Benchmark-only arms

Rule texts that exist to be measured against `rules/laconic.md`, never to ship.
`evals/bench/run.py` loads each file at import and exposes it as an arm, so an
arm here is delivered through exactly the same `--append-system-prompt` path as
the `laconic` arm and the comparison is treatment against treatment.

Nothing here is level-aware. The shipped rules slice into `lite`, `full` and
`ultra`; a benchmark arm is one fixed text, and it is written to compete with
the `full` slice, which is the level the product defaults to and the level
every clause with a measured effect in `LEDGER.md` was measured at.

## `laconic-min-a.md`, `laconic-min-b.md` — the [#270] dilution arms

Two minimal slices, built to the same content specification and worded
differently. The specification is: the whole never-cut contract, the thesis
sentence that separates fewer claims from fewer words, the level-`full` cuts,
and the two design-question clauses that hold an accept in `LEDGER.md`
(rounds 26 and 28) plus round 55's pre-action check. Everything the full slice
carries beyond that — the worked OOM example, the level table, the arrow
section with its four `Wrong:`/`Right:` pairs, the section headings, and the
six clauses rounds 44 through 49 measured at zero — is absent.

**Two variants rather than one, because one is not interpretable.** A single
hand-authored slice that loses to the full file cannot distinguish "the full
file is load-bearing" from "that slice was written badly". Two slices carrying
the same instructions in different words split those readings: both losing
implicates the content, one losing implicates the wording. `laconic-min-a` is
an extract, assembled from the shipped file's own sentences so wording is held
constant; `laconic-min-b` is a rewrite from the specification, sharing almost
no phrasing with the file or with `-a`.

They are two drafts by one author in one sitting, not two independent authors,
and any round citing them says so.

[#270]: https://github.com/JordanMPDS/laconic/issues/270
