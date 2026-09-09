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

## `laconic-abl-shown.md`, `laconic-abl-arrow.md` — the [#275] ablation arms

Round 58 found that both minimal slices produce answers roughly twice as long
as the shipped one, so the compression lives in the ~750 words they dropped.
These two arms ask which of those words, and they are a different construction
from the minimal slices: **each is the shipped `full` slice with one named
block deleted and nothing else changed.** Not a rewrite, not an extract — a
deletion, so a difference against the control attributes to that block alone.

| arm | words | block removed |
|---|--:|---|
| `laconic-abl-shown` | 832 | every rendered short answer: the worked OOM question with its three-row level table and coda, and the design licence's `Wrong:`/`Right:` pair. 209 words. |
| `laconic-abl-arrow` | 876 | the arrow rule entire: the prohibition, its enumeration of forbidden uses, the four `Wrong:`/`Right:` lines and the fenced-code exemption. 165 words. |

The instructions those blocks illustrate stay in both arms. `abl-shown` keeps
the design licence, the level ladder and the whole never-cut contract;
`abl-arrow` keeps the rest of `## Never do this`, including the anti-compression
clause that shares its section.

**They are word-matched on purpose, and the pairing is the design.**
`abl-shown` removes the file's only rendered instances of a brief answer.
`abl-arrow` removes a comparable bulk of on-topic instruction — including its
own rendered `Wrong:`/`Right:` demonstrations — that says nothing about length
anywhere in it. So `abl-shown` moving while `abl-arrow` does not separates
"showing a short answer is the carrier" from "any 200 words are".

`tests/test_bench.py` holds both to pure deletion: every line has to be a line
of the shipped slice, in order, and the removed word count has to be exactly
the figure round 59 registered. An edit to `rules/laconic.md` that moves either
block fails that check, which is correct — the arm would no longer isolate what
it was built to isolate.

[#275]: https://github.com/JordanMPDS/laconic/issues/275
