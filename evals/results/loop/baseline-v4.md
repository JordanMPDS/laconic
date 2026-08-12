# The `-v4` baseline

**Date:** 2026-08-12
**Snapshot:** `evals/snapshots/loop/round-01-n10-v4.json` and
`round-01-n10-v4-judgments.json`
**Rules:** `rules_cksum` 1830906901, master, like every cell in `-v3`
**Shape:** 22 cases, 1100 runs, 1100 judgments. 0 failed generations and 0
infrastructure failures in judging.

`-v4` is `-v3` plus the three design cases admitted for [#88]: `design-cache`,
`design-realtime` and `design-upload`. They exist because the five older design
cases cannot tell an answer derived from the fixture from one recalled from
convention, which is why round 15 passed every dev-set gate and was killed by
the holdout. Working:
[`design-discrimination.md`](design-discrimination.md).

## It changes nothing that was already measured

| | `never_cut_failures` | `quality_fails` | `safety_fails` | `violations_total` |
| --- | --: | --: | --: | --: |
| `-v3` | 2 | 52 | 4 | 139 |
| **`-v4` with the three new cases removed** | **2** | **52** | **4** | **139** |
| `-v4` | 2 | **83** | 4 | 158 |

The 19 shared cases are the same runs and the same verdicts, carried verbatim.
Every counter is identical. The three new cases add 31 `quality_fails` and 19
readability violations and touch neither `never_cut_failures` nor
`safety_fails`, which is what a `quality`-graded case with an empty `never_cut`
list should do.

## What the three cost, and what was carried

120 generations and 90 judge calls. The `baseline` and `word-compression` arms
of the three cases were **carried from the discrimination snapshot** rather than
regenerated: same `rules_cksum`, same models, same reps, against byte-identical
`prompt.md` and `fixture/` files. `expect.json` gained a `discrimination` block
afterwards, and `run.py` never reads `expect.json`; the `trap` the judge reads
was not touched, so the verdicts carry with them. This is the argument
`carry_arms` already makes for the controls, and the provenance is stamped in
`metadata.carried_runs_from` rather than left to memory.

**The carried controls were trimmed to `-v3`'s shape.** The discrimination check
ran its controls at 10 reps per model; `-v3` runs controls at 5 and `laconic` at
10. The extra 90 runs were dropped from the baseline and remain in
`design-discrimination.json`, so every one of the 22 cases in `-v4` has the same
50 runs. A baseline whose cases have different shapes is how a per-cell rate
computed over an uneven denominator ends up wrong later.

## Headroom on the arm the gates read

The discrimination check measured `baseline` and `word-compression` pooled. On
the `laconic` arm alone, at n = 20 per case, the property holds:

| case | resolves the fixture | pass, resolved | pass, not resolved | Fisher | mean tokens |
| --- | --: | --: | --: | --: | --: |
| `design-cache` | 16 of 20 | 10 of 16 | **0 of 4** | 0.087 | 2711 |
| `design-realtime` | 6 of 20 | 6 of 6 | **0 of 14** | <0.0001 | 1471 |
| `design-upload` | 14 of 20 | 11 of 14 | **0 of 6** | 0.002 | 2697 |

Not one response that failed to resolve the fixture passed. `design-cache`'s
0.087 is n = 20 alone and does not reach alpha on its own; its pooled n = 40
measurement is p = 0.0005 and the direction is the same.

`design-realtime` has the most headroom and the highest failure rate: 14 of 20
laconic responses reach for WebSockets or a held-open stream without engaging
`PLATFORM.md`.

**The baseline fail rate on the three is 31 of 60, against 36 of 100 on the five
older design cases.** That is deliberate. A case near 0 or near 20 cannot show
movement in one of the two directions, and these sit where a rule edit can move
them either way.

## What this does and does not license

**It does not change any gate**, and no stored round is re-scored. A round
scored against `-v4` is comparing against a strictly larger case set, and its
`quality_fails` is not comparable to a round scored against `-v3` — 83 against
52 is the case set, not a regression.

**`-v3` stays the baseline for the scoped `output_tokens` target.** That target
runs over the five older design cases and is a length measurement, which does
not depend on the property they lack.

~~The three new cases have **no per-cell measured rates** in `cell-rates.json`,
so the [#66] screen cannot clear them.~~

**Measured 2026-08-12**, in [`design-quality-rates.md`](design-quality-rates.md).
All six cells are in `cell-rates.json` under `quality_fails` at n = 40 each, and
three of them turned out not to be usable as instruments: `design-realtime`
/haiku fails 40 of 40, `design-cache`/haiku 37 of 40, and `design-upload`/sonnet
0 of 40. The screen behaves correctly on all three — the two ceiling cells clear
any rise, and a rate of zero clears nothing — but the sonnet cells of
`design-cache` and `design-realtime` and the haiku cell of `design-upload` are
where the usable signal is.

[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#88]: https://github.com/JordanMPDS/laconic/issues/88
