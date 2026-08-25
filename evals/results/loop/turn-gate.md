# The turn gate, and what the archive says under it

`turns` became a fatal condition on 2026-08-25, for [#49]. This is the evidence
the decision rests on: what the metric is, why it needs two estimators rather
than one, and what every stored round reads under it.

[#49]: https://github.com/JordanMPDS/laconic/issues/49

## What it measures

The per-cell median of `num_turns`, over the grounded stratum only.

Laconic bounds prose and nothing else. Both of its pre-send checks are about
the text being written, and both run after the tool calls have already
happened, so an edit can cut words and relocate the excess into actions with
every prose gate still reading clean. [#49] is that failure measured: a
one-line factual question — "what is the command to get gke cluster name" —
ran a command, answered, then ran a second command. The prose was short enough
to pass every rule in the ruleset. The turn was still a gross over-answer.

`num_turns` is the only action proxy the archive carries. `run.py:302` asks the
CLI for `--output-format json`, which reports how many agentic turns a response
took and nothing about which tools ran, so this measures the volume of action
and not its kind. [#142] is the other half.

[#142]: https://github.com/JordanMPDS/laconic/issues/142

## Why grounded only

An unread answer has 0 or 1 turns by construction. A turn median taken over
every run therefore falls whenever answers stop reading — which is the
[#46]/[#138] failure `one_turn` already gates, and the behaviour rounds 24
through 26 spent five rounds suppressing. An unconditioned turn metric would
have paid an edit for causing it.

Inside the grounded stratum that route is closed. Every response being compared
already opened a file, so the only way the median falls is an answer doing less
after the reading happened, which is what [#49] reports. There is no fallback
stratum for the same reason: an unread turn median cannot move, so a cell
compared inside it would vote a guaranteed tie. Cells without a grounded
stratum on both sides are absent rather than tied.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#138]: https://github.com/JordanMPDS/laconic/issues/138

## Why a floor alone is not enough

The floor is measured, not published: the median per-cell grounded stdev of the
baseline, the same estimator the scoped token floor is built from.
`NOISE["stdev"]` is 260 tokens and says nothing about turns, and a turn
constant would be tuned to the rounds that already exist.

But `num_turns` is a small integer, and a cell whose grounded runs all took the
same number of turns has stdev exactly 0. The median across such cells collapses
to 0.0, at which point any rise at all clears the floor.

That is not hypothetical. Scored under a floor alone, this gate rejected rounds
07, 08 and 10 outright:

```
REJECT: action scope lost - grounded turns rose 0.2 over 18 cell(s), past the
0.2-turn floor measured from the baseline's own dispersion (#49 turn gate);
risen on destructive/sonnet 3.0 -> 4.0
```

One risen cell of eighteen. With half the cells sitting either side of the
round-wide median, moving a single cell across it shifts that median by half a
turn while nothing else moves at all. A gate that rejects a round for that is
not stricter, it is broken — the same failure `CELL_TEST_MIN_RUNS` documents
for the cell-rate test.

So a rise must be broad as well as larger than the floor: it has to win a sign
test across cells. `sign_test` is two-sided, so a majority guard comes with it,
because 1 of 10 reaches alpha in the falling direction and must not be read as
a rise.

## The archive under the gate as shipped

Rounds are re-scored through `report.py` itself, so this is the line the gate
prints and not a reimplementation of it. Any single round reproduces with the
same invocation the loop uses, and the turn line appears whatever `--target`
is named:

```sh
python3 evals/bench/report.py \
  --results evals/snapshots/loop/round-26-licence.json \
  --judgments evals/snapshots/loop/round-26-licence-judgments.json \
  --against evals/snapshots/loop/round-26-control.json \
  --against-judgments evals/snapshots/loop/round-26-control-judgments.json \
  --target turns --no-gate
```


| round | grounded turn shift | cells rising | measured floor |
|---|--:|--:|--:|
| 05 | +0.0 | 0 of 14 | 0.0 |
| 06 | +0.0 | 0 of 14 | 0.0 |
| 07 | +0.2 | 1 of 18 | 0.2 |
| 08 | +0.2 | 1 of 18 | 0.2 |
| 09 | -0.5 | 0 of 19 | 0.3 |
| 10 | +0.5 | 1 of 19 | 0.3 |
| 11 | +0.0 | 2 of 24 | 0.0 |
| 12 | +0.0 | 1 of 25 | 0.0 |
| 14 | +0.0 | 1 of 23 | 0.0 |
| 15 | +0.0 | 1 of 26 | 0.0 |
| 19 | +0.0 | 3 of 31 | 0.3 |
| 20 | +0.0 | 3 of 27 | 0.0 |
| 24 | +0.0 | 3 of 28 | 0.0 |
| 25 | +0.0 | 0 of 8 | 0.7 |
| 26 | +0.5 | 1 of 8 | 0.7 |

Every round holds. The largest movement is 0.5 turns, the most cells ever
rising is 3 of 31, and no stored verdict changes. The gate is live and has
never fired on the archive, which is the point: a round that trips it is
reporting something the loop has not seen before.

Rounds 01, 03, 04, 13, 16, 17, 18, 21, 22 and 23 are absent because they did
not score an `output_tokens` target and the re-score harness walks that list.
Their snapshots carry `num_turns` and can be scored on request.

## What this does not establish

**Power is thin on a small scope.** The sign test is two-sided exact, so at
eight cells — the scope rounds 25 and 26 used — only a clean 8-of-8 sweep
reaches alpha, and 7 of 8 reads p = 0.070. On a round-wide scope of 18 to 31
cells there is room. "Held" on eight cells is not "no effect".

**Zero floors are real, not a bug to patch.** A 0.0 floor means every grounded
run in every cell took the same number of turns, so an effect that moved them
would be unambiguous. The broadness test is what stops that from firing on
noise, not the floor.

**No round below 27 was screened for this.** A verdict from round 27 on rests
on five fatal conditions where every one before it rests on four.
