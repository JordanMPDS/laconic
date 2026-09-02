# Opus: does the compression claim generalise off the two models that made it?

**Status: pre-registration. No number below the line has been computed.** The
predictions and their bars are written here first, and the batch that scores
them is generated afterwards, so the scope cannot be chosen once the numbers
are in.

Answers step 1 of [#117].

## The question

`docs/benchmark.md` publishes every figure off two models, `haiku` and
`sonnet`, and says so under Scope. The compression headline — laconic cuts
Sonnet output 32% and Haiku output 9% — is therefore a claim about two points
on one vendor's ladder, and the gap between those two points is the reason the
question matters. On Haiku the median saving is 9% with eight of 22 cells
negative; on Sonnet it is 32%. Two points cannot say whether that is a
capability gradient or something specific to Sonnet, and the answer changes
what the plugin should tell a user about which models it helps.

Opus is also the model this repository is maintained from, so the one model the
plugin's own author runs is the one it has never been measured on.

## The design, and what it fixes about round 21

One interleaved batch. Three models, two arms, the 22 cases round 21 covered,
five reps: 660 generations.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models <model> --reps 5 \
  --cases '<the 22>' --concurrency 4 --snapshot <shard>
```

Two things about this design are deliberate and neither is round 21's.

**Both arms are generated in the same batch.** Round 21's baseline is carried
from round 20 and is eleven days and eleven CLI patch releases older than its
laconic arm. Round 37 then measured a syntactic behaviour moving 4.7x in five
days at byte-identical rules, so a cross-era arm comparison is exactly the
exposure to avoid. Every reduction figure below is laconic against a baseline
generated beside it, on the same day and the same CLI.

**It runs at the rules this repository ships.** Every published figure is at
`rules_cksum` 1830906901, two accepted edits behind master's 136269960, and
`docs/benchmark.md` says in as many words that no round-wide 22-case benchmark
has been generated at the shipped revision. This is that batch, which makes the
sonnet column news in its own right rather than only a control for the opus one.

## What is not bought, and why

`terse-control`, `word-compression` and `concise-style` are not generated. The
question registered here is whether *the compression claim* generalises, and
that claim is laconic against baseline; the three other arms are what rank the
field, which is a different question and roughly $50 more of Opus. So this
batch cannot restate round 21's five-arm table, and in particular **it cannot
say whether `concise-style` still out-compresses laconic on Opus** — round 21's
sharpest negative result. That stays open and belongs to step 2 of [#117].

Preference is not bought either, per the standing rule.

## Predictions, registered before the batch

| # | prediction | bar |
|---|---|---|
| 1 | The gradient is monotone in capability | median per-cell reduction: haiku < sonnet < opus |
| 2 | Fewer cells get *longer* under laconic as capability rises | negative cells: opus < sonnet < haiku |
| 3 | The matched sonnet figure restates the published one | sonnet reduction within 10 points of −32% |
| 4 | The quality deficit does not widen with capability | on opus, laconic's pass rate over the quality-graded cases is no more than 10 points below baseline's |

Bars 1 and 2 are the capability-gradient hypothesis stated two ways, one on the
central tendency and one on the tail; a gradient that shows up on neither is not
a gradient. Bar 3's 10-point band is the width the headline has already moved
across publications — 28%, 33%, 38%, 32% — so anything inside it restates the
claim and anything outside it is news about the matched design or the shipped
rules. Bar 4 is loose on purpose: round 21 read laconic 59.7% against baseline
68.1% at z = −1.45, which is not a demonstrated regression, and a bar tighter
than the effect round 21 could not resolve would be scored on noise.

Readability violations, never-cut failures, latency and cost are reported as
disclosure. They carry no bar, because nothing here predicted them.

[#117]: https://github.com/JordanMPDS/laconic/issues/117
