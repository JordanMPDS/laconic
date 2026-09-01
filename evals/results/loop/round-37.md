# Round 37: the preamble finding was drift, not a defect

**This round proposes no rule edit.** It settles the one result in
[`preamble.md`](preamble.md) that pointed against the plugin, and the answer is
that the result was an artifact of *when* its data was generated.

It also demonstrates between-era drift more cleanly than anything else in this
archive, because the metric is syntactic and the instrument is provably
identical.

## What it was testing

[`preamble.md`](preamble.md) read `walkthrough` at **laconic 42.7% against
baseline 10.0%**, Fisher p = 0.0508, and said so plainly:

> That is not a finding and it is not nothing. It points against the plugin on a
> rule the plugin itself states, it is the only properly matched comparison
> available, and it is one response away from significance in either direction.
> A baseline cell of ten cannot settle it.

It named the settling experiment too — `walkthrough` and a procedure case,
baseline against laconic, one interleaved batch, 40 a side, no judging because
the metric is syntactic. This is that batch: `walkthrough` and `ordered-steps`,
40 reps an arm, 160 runs, 0 failed.

## Result: it does not reproduce, and it runs the other way

| Case | baseline | laconic | |
|---|--:|--:|--:|
| `walkthrough` | 7/40 — **17.5%** | 4/40 — **10.0%** | p = 0.518 |
| `ordered-steps` | 0/40 — 0.0% | 0/40 — 0.0% | p = 1.000 |

Against the archive figure this was built to test:

| | baseline | laconic |
|---|--:|--:|
| archive ([`preamble.md`](preamble.md)) | 1/10 — 10.0% | 320/750 — **42.7%** |
| this matched batch | 7/40 — 17.5% | 4/40 — **10.0%** |

**Laconic is lower than baseline, not higher, and the difference is not
significant.** The reading that the plugin breaks its own "No preamble" rule
more often than an unruled control is withdrawn.

`preamble.md` is corrected in this round rather than left standing.

## Why the archive said otherwise, and this is the round's real finding

The archive figure was not wrong about its own data. It was wrong about *now*.

Holding the rules text byte-identical — `rules_cksum` 136269960 throughout,
`laconic_level` `full` throughout, same case, same arm, no judge anywhere:

| Generated | laconic `walkthrough` preamble | CLI |
|---|--:|---|
| 2026-08-27 | 11/20 — 55.0% | 2.1.247 |
| 2026-08-28 | 31/80 — 38.8% | 2.1.250 |
| 2026-08-31 | 42/80 — 52.5% | 2.1.251, 2.1.252 |
| **2026-09-01** | **4/40 — 10.0%** | **2.1.257** |

August pooled 84/180 (46.7%) against today's 4/40 (10.0%), Fisher
**p = 1.0e-05**. The last two days alone, 52.5% against 10.0%,
**p = 3.3e-06**.

**Five days and five CLI patch releases moved a syntactic behaviour from about
half of responses to one in ten, with the rules text unchanged.**

This repo already knew control arms drift — `terse-control`'s one-turn rate went
4 of 40 to 11 of 40 with nothing changed but the calendar
([`interleaved-batch.md`](interleaved-batch.md)). This is the same phenomenon
measured on the *treatment* arm, on a metric with no judgement in it at all, at
a magnitude of 4.7×.

### What it means for archive-derived rates

[`closing-offers.md`](closing-offers.md) already names two confounds in
whole-archive rates: carried arms inflating a denominator tenfold, and case
mix-shift. **This is a third and it is the most severe: an archive rate for the
laconic arm describes the era its runs were generated in, not the rules text
they were generated under.**

The `rules_cksum` guard does not protect against this. It certifies that two
sets of runs used the same rules, which is exactly what makes this measurement
clean — and exactly why it is alarming. Identical instrument, different answer.

**A rate quoted from the archive needs a date, or a fresh matched batch.** The
closing-offer rates in [`docs/benchmark.md`](../../../docs/benchmark.md) are
computed from one snapshot rather than pooled across eras, and round 36 and this
round both reproduce their ordering in matched batches, so they stand — but they
stand because they were checked, not because the archive is trustworthy.

## The closing-offer axis reproduces again, on a new case

Measured in the same batch, from the same responses:

| Case | baseline | laconic | |
|---|--:|--:|--:|
| `ordered-steps` | 22/40 — **55.0%** | 5/40 — **12.5%** | Fisher **p = 0.0001** |
| `walkthrough` | 1/40 — 2.5% | 0/40 — 0.0% | p = 1.000 |

`ordered-steps` had never been measured in a matched batch. It lands where every
other matched measurement has: laconic far below baseline, significant.
`walkthrough` sits near zero in both arms, which is what
[`preamble.md`](preamble.md) predicts for a case whose deliverable is the answer
rather than something buildable.

So the two ceremony detectors behave oppositely under drift. The closing-offer
gap has held across the archive, round 36 and round 37; the preamble gap did not
survive five days.

## What was not done, and why

**No judging.** This round proposes no edit, so no gate reads a verdict, and the
loop's own rule is that re-grading text no gate reads is waste. Every claim above
is syntactic and reproducible from the snapshot with `metrics.preamble()` and
`metrics.closing_offers()`.

160 generations, 0 failed, $8.32.

## Correction issued

[`preamble.md`](preamble.md)'s "one result worth following up" is withdrawn. The
detector itself is unaffected — precision was 18 of 18 on a fresh draw and this
round does not re-test it — and its central conclusion stands and is
strengthened: **the archive could not score arms with it**, and the reason is now
known to include era as well as base rate and corpus balance.

[#179]: https://github.com/JordanMPDS/laconic/issues/179
