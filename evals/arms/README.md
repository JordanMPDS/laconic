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
the figure round 59 registered. An edit to `rules/laconic.md` retires that
check rather than failing it, because the arm would no longer isolate what it
was built to isolate — see **Staleness** below.

## `laconic-repl-*.md` — the [#277] replacement arms

Round 59 found `abl-shown` load-bearing: deleting its 209 words of rendered
demonstration lengthened answers by 1.119x overall and by 1.284x on the three
`design-*` cells. But those 209 words are three things welded together — the
file's only rendered short answer, its only side-by-side calibration of `lite`,
`full` and `ultra`, and its only worked application of the rule to a specific
question — and a deletion cannot tell them apart.

These three arms can, because each one **puts a substitute back at the two
sites `abl-shown` deletes from** and each removes exactly one of the three
properties while keeping the other two. So every arm is compared against the
shipped slice on a single difference, rather than against the arm one rung
below it on a cumulative ladder.

| arm | words | rendered? | mapped to a level? | worked from a question? |
|---|--:|---|---|---|
| `laconic` (ceiling) | 1,041 | yes | yes | yes |
| `laconic-repl-told` | 1,049 | **no**, the same content in prose | described | described |
| `laconic-repl-unlabelled` | 1,042 | yes | **no**, three answers with no level names | yes |
| `laconic-repl-unframed` | 1,034 | yes | yes | **no**, the answers stand free of the question |
| `laconic-abl-shown` (floor) | 832 | no | no | no |

**They are word-matched, and that is the point.** Every rung sits within 8 words
of the shipped slice, against a floor 209 words below it. On the design cells
round 59 bounds bulk removal at 1.070x per 100 words at the 95% upper bound, so
a 20-word band bounds any length artefact at 1.014x — comfortably under the
round's 1.10x detection floor. Round 59's own `abl-arrow` result is *not* enough
on its own here: pooled over six cells it was 0.967x, but on the design cells
alone it reads 1.058x with an interval that reaches 1.119x, so length is
something this ladder had to design out rather than argue away.

`tests/test_bench.py` holds each arm to pure replacement: every line of
`laconic-abl-shown.md` must appear in it, in order, so nothing the floor keeps
can be dropped or reworded, and the arm must land within 20 words of the shipped
slice. Because the floor is itself checked against the live hook output, an edit
to `rules/laconic.md` that moves the block retires all five arms at once — see
**Staleness** below.

## `laconic-precheck-off.md`, `laconic-precheck-read.md` — the [#264] arms

Round 56 measured the pre-action check costing 7.8 points of reading rate on
`design-*`/sonnet with no quality cost the loop can resolve, and proposed a
mechanism it could not test: the check's trigger is a broken thing, a design
question has none, so the clause still in force is the one about not acting —
and answering without acting means answering without reading.

These two arms are the narrowest construction in this directory. **Each is the
shipped `full` slice with the opening numbered list swapped and every other
byte identical**, so `tests/test_bench.py` checks them by exact equality
against the live hook output rather than structurally. Any edit to
`rules/laconic.md`, inside the block or outside it, retires both — see
**Staleness** below.

| arm | words | the list it carries |
|---|--:|---|
| `laconic-precheck-off` | 1,000 | the two-item list the file carried before round 55 — the check deleted, nothing put back |
| `laconic` (shipped) | 1,041 | the check as round 55 accepted it |
| `laconic-precheck-read` | 1,041 | the check with the reading instruction hoisted out of the broken-thing conditional |

`-read` is **word-matched to the shipped slice**, which is the property that
makes the recovery contrast interpretable: the two arms differ in where one
instruction sits and not in how much file there is. `-off` is 41 words shorter,
and those 41 words are the check itself — the thing round 55 bought.

`-off` is not a rung on a ladder, it is a positive control. It re-establishes
that the check costs reading *in the round's own window* before the round asks
whether a rewording gives it back, which the loop needs because a control
generated in a different window has misread this repo before.

[#264]: https://github.com/JordanMPDS/laconic/issues/264

## Staleness: `BUILT-FROM.json`

Seven of these arms are not free-standing texts. `laconic-abl-*`,
`laconic-repl-*` and `laconic-precheck-*` are each defined as a transformation
of the shipped `full` slice, so each one means what the section above says it
means only against the slice it was cut from. `BUILT-FROM.json` records that
slice's `rules_cksum` per arm.

When `rules/laconic.md` moves, those arms go **stale**, and stale is a third
state rather than a synonym for wrong. The text still reads as a plausible
rules file and would go on producing numbers; what it no longer is, is a
transformation of the file on disk. `laconic-abl-shown` is "the slice minus its
rendered demonstrations", and against a slice carrying a demonstration it never
saw, it is a deletion of something else.

Two things follow, and round 64 added both:

- `tests/test_bench.py` skips the invariants of a stale arm rather than failing
  them, because "removes exactly 209 words" is a claim about a file that is no
  longer there.
- `evals/bench/run.py` **refuses to generate with a stale arm**, naming it and
  both checksums, before anything is written. `--allow-stale-arm` is the
  override, for a round that deliberately compares against the older text.

The refusal is what replaces the skipped checks, so the protection moves rather
than lapsing. Rebuilding a stale arm belongs to whichever round next needs it:
doing it silently inside a rules edit would produce a text no round ever ran,
while this file went on describing the old one.

Round 64 left all seven stale at `594915793`, the slice rounds 59 through 63
measured. The word counts in the tables above are that slice's.


[#275]: https://github.com/JordanMPDS/laconic/issues/275
[#277]: https://github.com/JordanMPDS/laconic/issues/277
