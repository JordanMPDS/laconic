# The seven unmeasured never-cut cells, measured

**Date:** 2026-08-14
**Rules under test:** `rules_cksum` 1830906901, master
**Status:** an instrument measurement, not a round. It changes no rule, and it
turns out to change no verdict either.

## Why

Round 17 rejected on `walkthrough`/haiku going 0 to 1, a cell with no measured
rate and therefore still scored the pre-[#66] way, against a single n = 10
baseline draw. Round 19 rejected in part on `conditional`/sonnet, and its
write-up says the remedy for a cell that rejects rounds on a thin draw is "more
measurement, not an arbitration".

Before this, `cell-rates.json` held never-cut rates for three cells. The
never-cut check turns out to cover ten: only five of the twenty-two cases carry
any `never_cut` keywords at all — `badnews` (1), `code-fidelity` (2),
`conditional` (1), `destructive` (3), `walkthrough` (1) — and every other case
has an empty list. That is 100 of the 440 laconic responses a round generates,
which bears on [#10] without settling it.

So seven of the ten cells were unmeasured. This measures them.

## Method

The one [#66] and [#78] used, and the one
[`conditional-haiku.md`](conditional-haiku.md) documents: generate the cell at
n = 40 under master rules, pool with every committed laconic run of that cell at
the same `rules_cksum`, and deduplicate by response text.

Generation only, no judge calls: `never_cut_failures` is a substring check
(`metrics.never_cut_missing`), which is also why it catches `destructive`/haiku
even though that cell was `saturated_models` for judge verdicts.

280 generations, 0 failed, no service outage.

## Results

| cell | never-cut failures | pooled n |
| --- | --: | --: |
| `badnews`/haiku | 0 | 60 |
| `badnews`/sonnet | 0 | 60 |
| `code-fidelity`/haiku | 0 | 60 |
| `code-fidelity`/sonnet | 0 | 60 |
| `destructive`/sonnet | 0 | 105 |
| `walkthrough`/haiku | 0 | 60 |
| `walkthrough`/sonnet | 0 | 60 |

Seven of seven at zero. With the three already in the file, eight of the ten
never-cut cells fail zero times under master rules. The two that demonstrably
fail are `conditional`/sonnet (8 of 60) and `destructive`/haiku (5 of 65) — the
same two that have been rejecting rounds all along.

## What this does not do

**It changes no verdict, and it never could have.** [#66] registered that a rate
of zero clears nothing, and `_rate_covers` implements it: at p = 0 the upper tail
of any count of 1 or more is 0, which never reaches alpha. Every entry added here
is a zero. Round 17's `walkthrough`/haiku 0 to 1 would reject today exactly as it
did then.

That was foreseeable from [#66] and was not foreseen here before the calls were
spent. The measurement is recorded so that the next person reading "these cells
are unmeasured" does not spend the 280 calls again.

## What it does establish

These cells are not lotteries. A lottery is `conditional`/sonnet at 13.3%, where
a 4-in-10 draw is an ordinary event and the screen exists to say so. Eight of ten
cells are the opposite: they do not fire under master rules, so a rise on one is
about the edit rather than about sampling.

**The statistical caveat that keeps it from being decisive.** Zero failures in 60
runs puts the 95% upper bound near 5% by the rule of three, and a cell that truly
fails at 5% produces at least one failure in ten draws about 40% of the time. So
a single 0 to 1 remains weak evidence. The screen cannot say so, because it reads
the point estimate; the loop's arbitration can, because it replicates.

## What the next round should do with it

Rate measurement is now exhausted as a lever for the never-cut gate — all ten
cells are measured, and eight of them are structurally unable to clear anything.
Two levers remain:

1. **Arbitration**, which the loop already supports at about 40 calls per risen
   cell. Round 19 declined it only on the grounds that the round rejected on its
   target anyway. For a round that passes its target, it is the tool.
2. **More reps on the five never-cut cases**, which attacks the variance that
   actually dominates. At `conditional`/sonnet's measured 13.3%, the 60-run rate
   estimate has a standard error near 4 points and a round's 10-run draw one
   near 11 — the draw carries about two and a half times the noise, and it is
   the term a round controls. Doubling reps on those five cases costs about 100
   extra generations per round.

Lever 2 is untested and not free of complications: the `-v4` baseline is at
n = 10, and `report.py` compares per-cell counts rather than rates, so a round
generated at 20 reps would need the baseline extended to match before the
comparison means anything. Do not treat it as a drop-in flag change.

[#10]: https://github.com/JordanMPDS/laconic/issues/10
[#66]: https://github.com/JordanMPDS/laconic/issues/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
