# Measured `quality_fails` rates for the three new design cases

**Date:** 2026-08-12
**Rules:** `rules_cksum` 1830906901, master
**Artefacts:** `evals/snapshots/loop/quality-rates-design.json` and
`quality-rates-design-judgments.json`
**Cost:** 180 generations and 180 judge calls. 0 infrastructure failures in
judging; the generation pass needed a resume, below.
**Result:** six cells measured, and **three of them are not usable as
instruments.** The rates are recorded anyway, because that is what makes the
[#66] screen behave correctly on them.

## Why

`design-cache`, `design-realtime` and `design-upload` were admitted in [#88] and
entered the [`-v4` baseline](baseline-v4.md) with no measured rate, so a round
that saw one move would have been comparing it against a single n = 10 draw —
the exact defect [#66] exists to correct. The method here is the one [#66] and
[#78] used: generate the cell on the `laconic` arm under master rules, pool with
every committed laconic run of that cell at the same `rules_cksum`, and
deduplicate by response text.

n = 30 fresh per cell, pooled with `-v4`'s 10, giving **n = 40 per cell**.
Nothing deduplicated away: all 240 responses are distinct.

## The rates

| cell | fails | runs | rate | reading |
| --- | --: | --: | --: | --- |
| `design-cache`/haiku | 37 | 40 | **92.5%** | at the ceiling |
| `design-cache`/sonnet | 4 | 40 | 10.0% | usable |
| `design-realtime`/haiku | 40 | 40 | **100%** | saturated at fail |
| `design-realtime`/sonnet | 18 | 40 | 45.0% | usable, and the best of the six |
| `design-upload`/haiku | 28 | 40 | 70.0% | usable |
| `design-upload`/sonnet | 0 | 40 | **0.0%** | a tripwire, not a rate |

**The failures live on haiku.** Two of the three haiku cells are at or above
92.5%, and `design-realtime`/haiku has never passed in 40 attempts. That is a
genuine capability difference rather than a defect in the case: on the `laconic`
arm only 6 of 20 `design-realtime` responses engage `PLATFORM.md` at all, and
haiku is where the other 14 are.

**This does not undo [#88].** The discrimination property is about whether a
verdict depends on the fixture having been read, and it holds: no response that
failed to resolve the fixture has passed, on any of the three cases, on any arm.
What these rates add is the separate question of whether each *cell* has room to
move, and three of the six do not.

## What the screen does with them

`_rate_covers` at alpha = 0.05, against counts a round of n = 10 could produce:

| cell | 1 | 3 | 5 | 8 | 10 |
| --- | --- | --- | --- | --- | --- |
| `design-cache`/haiku | clear | clear | clear | clear | clear |
| `design-cache`/sonnet | clear | clear | REJECT | REJECT | REJECT |
| `design-realtime`/haiku | clear | clear | clear | clear | clear |
| `design-realtime`/sonnet | clear | clear | clear | REJECT | REJECT |
| `design-upload`/haiku | clear | clear | clear | clear | REJECT |
| `design-upload`/sonnet | REJECT | REJECT | REJECT | REJECT | REJECT |

The two ceiling cells clear everything, which is correct: a cell that fails
almost always cannot produce a *rise* that means anything, and the fatal
counters only ever reject on a rise. They can still fall, and a fall is what a
[#46] edit would be trying to produce.

`design-upload`/sonnet is the other end. **A rate of zero clears nothing** —
[#66] registered that deliberately, and `_rate_covers` bears it out, because at
p = 0 the upper tail of any count of 1 or more is 0. So the cell is a genuine
tripwire that rejects a round on one failure in ten, exactly like
`conditional`/haiku. That is a known and deliberate property of the screen, not
a surprise, and it is named here so the first round it fires on is not read as
news. See [`conditional-haiku.md`](conditional-haiku.md) for how much a
single-draw rejection from a near-zero cell is actually worth.

## What is deliberately not done here

**No cell is marked `saturated_models`.** `design-realtime`/haiku at 40 of 40 is
the same shape as `destructive`/haiku, which is marked, and the case for marking
it is real. It is not being made in a measurement:

- Saturation excludes a cell from the fatal judge-verdict counters, which is a
  gate change, and gate changes in this loop are pre-registered separately and
  re-scored across stored rounds before they govern an edit. That is what
  [`ordered-steps-haiku.md`](ordered-steps-haiku.md) did.
- The exclusion runs in both directions. A cell at 40 of 40 cannot rise, so it
  cannot cause a false rejection — the screen above already handles that — but
  it *can* fall, and a fall on `design-realtime`/haiku is close to the best
  outcome an [#46] edit could produce. Excluding it would hide the win it exists
  to detect.

So the rate is recorded, the screen uses it, and whether the cell should stop
voting is left as its own decision with its own registration.

## The outage, and what it cost

The first generation pass returned **100 failures in 180 runs**, concentrated
overnight, with the three parallel processes finishing to completion rather than
stopping. `run.py`'s resume ([#61]) repaired all of it in place: 180 usable runs
with no duplicate keys. Judging ran afterwards with 0 infrastructure failures.

This is the second overnight outage in two days to be repaired rather than
re-paid for, after round 15's 128 lost generations and 257 lost judge calls.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#61]: https://github.com/JordanMPDS/laconic/issues/61
[#66]: https://github.com/JordanMPDS/laconic/pull/66
[#78]: https://github.com/JordanMPDS/laconic/issues/78
[#88]: https://github.com/JordanMPDS/laconic/issues/88
