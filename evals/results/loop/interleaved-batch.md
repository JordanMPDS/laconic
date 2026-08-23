# Both sides in one batch: the licence suppresses reading, and that is the harm

**Date:** 2026-08-22
**Issue:** [#46], with a method finding that touches every round
**Cost:** 200 generations and 80 judge calls, $16.24. **0 failed generations,
0 infrastructure failures in the final judging pass.**
**Artefacts:** `evals/snapshots/loop/one-turn-cli-control.json`,
`licence-vs-master-master.json`, `licence-vs-master-licence.json` and the two
matching `-judgments.json` files.

## Why these two experiments exist

[`one-turn-investigation.md`](one-turn-investigation.md) established that
laconic's design-answer failures are ungrounded rather than long, and that
`num_turns == 1` on sonnet means the model never opened a file. It could not
size any effect, for one reason: **every comparison available in the archive
puts its two sides in different batches.** The control arms have been frozen
since round 16, and between-batch variance at fixed rules text (phi 3.0 to 4.5)
exceeded the rules effects being measured. Batch alone moved the statistic
0.144 to 0.400 at p = 0.0078 while the rules contrast on the same cases read
p = 0.121.

Both experiments below therefore generate every arm they compare **in one
interleaved pass on one CLI**, which the corpus had never contained.

## Experiment 1: it is not laconic, it is brevity

`baseline`, `terse-control` and `laconic` generated in a single interleaved
sequential pass, CLI 2.1.240, sonnet, all eight `design-*` cases, n = 5.

| arm | one-turn rate |
|---|--:|
| `baseline` | 4/40 (10.0%) |
| `terse-control` | **11/40 (27.5%)** |
| `laconic` | 10/40 (25.0%) |

- laconic against baseline: Fisher **p = 0.140**
- laconic against `terse-control`: Fisher **p = 1.000**

`terse-control` is the two-word system prompt `"Answer concisely."`. On the
current CLI it suppresses investigation exactly as much as the entire 130-line
plugin does.

**This retires a claim that looked well-supported.** Round 21 reads
`terse-control` at 4/40, which made "a bare brevity instruction does not
suppress tools, a document does" seem measured. That arm is frozen runs from
2026-08-11 on CLI 2.1.227, eleven days and twelve releases stale. Regenerated
alongside laconic it lands on top of it.

The consequence for [#46] is that the mechanism is a property of brevity
pressure, not a defect in laconic's wording — and it is a live risk to any
rules edit aimed at it, because an edit inside the plugin cannot remove a
pressure that two words also produce.

## Experiment 2: the licence, measured cleanly for the first time

Master rules against the design-question licence, **interleaved one rep at a
time** so the two arms alternate at roughly 20-minute granularity rather than
the eight days and seven CLI releases separating round 20 from round 21. Master
ran from the repository; the licence ran from a separate tree with the 11-line
patch applied, so `rules/laconic.md` was never modified. Both sides read the
same `evals/cases` and carry `cases_cksum` 2423244529; checksums came out at
1830906901 and 3980812364 as required, verified before and after.

| | master | licence | Fisher |
|---|--:|--:|--:|
| one-turn rate, all 8 cases | 15/40 | **25/40** | **0.0435** |
| quality fails, all 8 cases | 10/40 | **16/39** | 0.155 |
| one-turn, the three [#88] cases | 7/15 | **13/15** | 0.0502 |
| quality fails, the three [#88] cases | 6/15 | **11/14** | 0.0604 |

Per case, one-turn: `design-search` 1/5 to 5/5, `design-cache` 2/5 to 4/5,
`design-realtime` 2/5 to 4/5, `design-upload` 3/5 to 5/5, `design-rate-limit`
3/5 to 4/5, `design-retry` 3/5 to 3/5, `design-audit-log` 1/5 to 0/5,
`design-alerting` 0/5 both. `design-search` is the strongest cell again, as it
has been in every generation since round 10.

The token effect reproduces at full size: median output 3588 to 1442 overall,
and 4202 to 2633 among responses that read the repository.

### The mediation chain, end to end

This is what the archive could not supply. Pooling both sides:

| stratum | quality fails |
|---|--:|
| answered without opening a file | **20/39 (51%)** |
| read the repository | **6/40 (15%)** |

Fisher **p = 7.6e-4**. And conditioning on reading behaviour removes the
licence's effect almost entirely:

| stratum | master | licence | Fisher |
|---|--:|--:|--:|
| answered without opening a file | 8/15 | 12/24 | 1.000 |
| read the repository | 2/25 | 4/15 | 0.174 |

**The licence does not make answers worse. It makes the model stop reading, and
not reading is what makes answers worse.**

`one-turn-investigation.md` registered six rules for this endpoint, the fifth of
which required "at least one round where the surrogate moved and quality was
then scored at adequate n and moved as predicted", and recorded that no such
round existed. This is that measurement, and both moved together.

### What it still does not establish

The quality endpoint is p = 0.155 round-wide and p = 0.060 on the three cases
that matter — the right direction, short of alpha at 40 runs a side, exactly as
the power table in `one-turn-investigation.md` predicts. The read stratum hints
at a residual direct effect, 4/15 against 2/25, that this sample cannot resolve.
**The six registered rules stand unchanged**, including that an edit must clear
the one-turn target *in addition to* not regressing `quality_fails`, never
instead of it.

## The method finding, which outlives [#46]

The loop compares a round against a stored baseline. This session showed that is
the dominant error term, and that interleaving removes it: a contrast the
archive could not resolve at any sample size resolved at 40 runs a side in one
pass.

That **supersedes the phi calibration** proposed in `one-turn-investigation.md`.
Measuring between-batch variance is the wrong move when the design can avoid
generating it. Both experiments here were produced strictly sequentially —
maximum one run in flight, verified by the overlap sweep in [#120], with the
single apparent overlap being a 0.01-second rounding artefact out of 119 gaps.

**Recommendation: every future comparison on this endpoint generates both sides
in one interleaved batch.**

## Judging note

The first judging pass ran `--jobs 6` and lost **62 of 80 calls** to
`judge call failed`, returning the licence side as 40 of 40 `not_exercised`.
Read as verdicts those counts would have said the licence *improved* quality,
0 fails against 5, Fisher p = 0.055 — the exact inversion of the real result.
`judge.py:194` excludes `INFRA_REASONS` from resume, so the failures were
retryable; both files were set aside and regraded from scratch at `--jobs 2`,
sequentially, to 0 infrastructure failures. The failed pass is not committed.

This is [#67]'s failure mode recurring at a different concurrency, and it is the
second time in this session that reading a count without reading its reasons
would have published an inverted finding.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#67]: https://github.com/JordanMPDS/laconic/issues/67
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#120]: https://github.com/JordanMPDS/laconic/issues/120
