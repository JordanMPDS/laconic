# `unread_asks` v3: frozen, drawn, and not promoted

**Status: v3 failed the bar registered before its validation sample was drawn,
and it is not promoted. `report.py` is untouched and still calls v2.** The full
record — the freeze, the registration, batch 3's result, and the labeller check
that followed — is [`../unread-asks-v3.md`](../unread-asks-v3.md).

| batch | detector | precision | recall |
|---|---|--:|--:|
| 2 (published) | v2 | 73.7% | 87.5% |
| 2 (in sample) | v3 | 78.9% | 93.8% |
| 3 (fresh) | v2 | 66.7% | 50.0% |
| 3 (fresh) | v3 | 70.0% | 58.3% |

The bar, registered in [#224] under [#153]'s protocol and before the draw, was
fresh precision above v2's 73.7% and fresh recall no worse than its 87.5%. v3
reads 70.0% and 58.3%. It beats v2 on this batch on every measure, and both are
far below what batch 2 said either was worth.

**The result that outlives v3 is v2's.** Its published out-of-sample figure does
not replicate on a second fresh batch drawn the same way from the same
population. The leading alternative explanation — that batch 3 carries a
different labeller's judgement — is refuted in [#226]: 61 of batch 2 re-labelled
under batch 3's conventions agree with the stored labels at 96.7%, Cohen's kappa
0.902. **Neither 73.7% nor 66.7% is v2's precision.** The two together say the
quantity moves by 7 points of precision and 37 of recall between samples drawn
the same way, and that is what a decision about `unread_asks` has to be made
against.

## Files

- `detector_v3.py` — **not the v3 that batch 3 scored.** This is the earlier
  narrowing draft from [#191], which read only the last two sentences of the
  final paragraph; it failed in sample and no sample was ever drawn for it. It
  is kept as evidence about a design direction. The frozen v3 that batch 3
  scored is [`../unread-asks/detector_v3.py`](../unread-asks/detector_v3.py),
  committed in [#224] beside the v2 it was built from. Neither is promoted:
  nothing in `evals/bench/` calls either, and the `asks_back` pin in
  `tests/test_bench.py` still points at `detector_v2.py`.
- `key.json`, `blind.md`, `labels.json` — batch 3. 80 responses, seed 153, from
  the same eight snapshots and the same `laconic`/`sonnet`/`design-*` population
  as batches 1 and 2, disjoint from all 140 already labelled, out of a pool of
  1,220. Labelled blind from `blind.md` under batch 2's rule verbatim, before
  either detector was run on it, so v2 and v3 are scored against one definition.
- `relabel-batch2.json` — the [#226] check. 61 of batch 2's 80 re-labelled
  without consulting the stored labels; the other 19 excluded as contaminated,
  because this session had already seen their labels while diagnosing v2's
  errors. Agreement is therefore measured on a slightly easier subset than the
  full batch, and 96.7% is an upper bound rather than a point estimate.

There is no draw or resample script here. `key.json` is the record of the draw —
id, snapshot, case and rep for all 80 — and `blind.md` was written from it
against the committed snapshots. A copy of
[`../unread-asks-v2/resample.py`](../unread-asks-v2/resample.py) would be a
second thing to keep in sync, which the restatement batches already paid for
once.

## What this directory does not settle

Nothing about round 28, which was scored through v2 and says so. Nothing about
whether `unread_asks` should be fatal — but the case for ever making it fatal is
weaker than it was, not stronger, because the counter's precision and recall are
now known to move between fresh samples.

[#153]: https://github.com/JordanMPDS/laconic/issues/153
[#191]: https://github.com/JordanMPDS/laconic/pull/191
[#224]: https://github.com/JordanMPDS/laconic/pull/224
[#226]: https://github.com/JordanMPDS/laconic/pull/226
