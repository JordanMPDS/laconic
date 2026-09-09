# Round 58 — is most of `rules/laconic.md` dilution?

**Registered 2026-09-09, before any run. No rule edit.** An arm round for
[#270]: three arms in one interleaved batch, the shipped `full` slice against
two minimal slices built to the same content specification.

## Why the round exists

Six rounds have each tested one clause of the file and read null — the lens
candidate (44), the quotation exemption (45), the incentive (46), round 40's
edit re-run through the other channel (47, 48), and the licence (49). Every one
of those nulls was read as a fact about its clause. The reading nobody has
tested is that it is a fact about the *file*: 1,055 words of rules at the
shipped `full` level, of which any one clause is a few percent, so a clause with
a real effect would have to overcome the other 1,000 words to show one.

Round 56 is the shape that makes this urgent, and it happened here rather than
in the prior art. The round 55 edit cleared `evals/pilot/score_compression.py`
on all four cases at p < 0.00001 and then cost 7.8 points of reading rate
([#264]) — the file won on the counter it was tuned against and lost on one a
reader sees. [#270] takes its experimental design, and nothing else, from
[SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), which measured a
50-plus rule skill against an eight-line hand prompt and found the prompt won
every reader-visible column while the skill won only on its own linter. That
project publishes no licence, so no text was copied from it.

## The arms

| arm | words | what it is |
|---|--:|---|
| `laconic` | 1,055 | `hooks/laconic.sh start` at level `full`, the shipped slice |
| `laconic-min-a` | 295 | extract: the specification below, in the shipped file's own sentences |
| `laconic-min-b` | 317 | rewrite: the same specification, worded from scratch |

The content specification both minimal slices are built to, fixed before either
was written: the whole never-cut contract (all seven items), the thesis sentence
that separates fewer claims from fewer words, the level-`full` cuts, round 55's
pre-action check, and the design-question licence in the form rounds 26 and 28
accepted. Everything else the full slice carries is absent — the worked OOM
example and its level table, the whole arrow section with its four
`Wrong:`/`Right:` pairs, the section headings, and the six clauses rounds 44
through 49 measured at zero.

Both slices are delivered by `--append-system-prompt`, the same path the
`laconic` arm uses, so the comparison is treatment against treatment rather than
treatment against a differently-delivered competitor. `run.py` reads them from
`evals/arms/` at import, and `tests/test_bench.py` asserts every never-cut item
survives in both — a minimal slice that quietly dropped one would answer a
question nobody asked.

**Two variants, not one, and this is the design's load-bearing decision.** A
single hand-authored slice that loses to the full file cannot separate "the full
file is load-bearing" from "that slice was written badly". Two slices carrying
the same instructions in different words do separate them. `-a` holds wording
constant and varies only what is present; `-b` varies the wording too.

They are two drafts by one author in one sitting, not two independent authors.

*Origin: the two-variant design and the framing of the registered reading below
came from the `codex` and `kimi` delegate targets, which reached it
independently of each other on `bash tools/consult.sh`. `deepseek` did not
answer.*

## Level: `full`, where [#270] says `ultra`

Registered deviation, with its reason. Every clause with a measured effect in
[`LEDGER.md`](LEDGER.md) was measured at `full`; `full` is what the plugin
delivers unless a user sets otherwise; and a headline has to quote the word
count of the slice actually tested. So this round tests 1,055 words and says
1,055. `ultra`'s 1,138 is the maximum the product can deliver and is not what
this round measures. A claim about the whole ladder needs its own round.

*Origin: both answering delegate targets raised the mismatch unprompted.*

## Scope and depth

Sonnet only, 30 reps per arm, six cases, 540 generations, no judging in step 1.

- **Reading rate and prose words:** `design-cache`, `design-realtime`,
  `design-upload`. These are the three cases that can tell a fixture-derived
  answer from a recalled one ([#88], `design-discrimination.md`), and they are
  the sanctioned `one_turn` scope — the cells with reading variance *and* a
  measured link to answer quality.
- **The never-cut contract:** `destructive`, `code-fidelity`, `badnews` — the
  three cases whose `expect.json` carries never-cut keywords, so the check is a
  substring test and costs nothing. `ordered-steps` is deliberately excluded
  from this scope: its `never_cut` list is empty, so the free check cannot see
  it, and it reaches the contract only through the judge.

## Endpoints, registered before generation

**Primary, both free, both on the three `design-*` cells:**

1. **Reading rate** — the share of responses with `num_turns > 1`, the same
   definition every round's reading strata use. Non-inferiority, one-sided, with
   a **margin of 15 points**: a minimal slice is non-inferior when the lower
   bound of the difference against `laconic` sits above −15.
2. **Prose words** — the per-cell median inside the grounded stratum ([#131]),
   permutation at seed 58, with a sign test across the three cells. Reported in
   both directions; the interesting result is a fall.

**Guardrail, free:**

3. **Never-cut keyword failures** pooled over `destructive`, `code-fidelity` and
   `badnews`, 90 runs per arm. **Registered as a smoke alarm, not an equivalence
   test.** The archive's rate on these cells is near zero, so 90 runs bound a
   rate at about 3.3% by the rule of three and certify nothing. It is fatal to a
   minimal slice only on a catastrophic loss, defined in advance as **more than
   5 failing runs of 90 where `laconic` fails 1 or fewer**.

*Origin: the "smoke alarm, not equivalence" framing and the explicit power
caveat came from both answering delegate targets, which independently refused
the stronger reading.*

**Step 2, bought only if step 1 does not kill the round:** judge the 270
`design-*` runs for `quality` and the 270 contract runs for `safety`. Reading
rate is a proxy for design-answer quality with a measured link, not a
substitute for it.

## The registered reading

Fixed before the numbers, because "the minimal slice won" is a claim the round
can only make one way:

- **Both minimal slices non-inferior on reading rate, no worse on words, no
  contract loss.** Then 1,055 words buy what 300 buy, and the per-session cost
  of the other 750 is the finding.
- **Both minimal slices worse.** Then dilution is ruled out on this content
  specification, the six nulls are facts about their clauses, and [#270] closes.
- **One worse, one not.** Then the round has measured slice quality, not the
  file, and it proposes nothing about either.

Anything the round reports outside these three endpoints is exploratory and says
so where it is written.

## Bound, fatal to the round

Zero failed runs is not required, but a single `rules_cksum` across every
snapshot is, and any pass that crosses a CLI release is reported through
`python3 evals/bench/release.py` before a contrast is read out of it ([#272]).

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#270]: https://github.com/JordanMPDS/laconic/issues/270
[#272]: https://github.com/JordanMPDS/laconic/issues/272
