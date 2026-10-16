# Proposal: one price table keyed on zone and weight band

**Status:** proposed, not started. **Owner:** shipping team.

## Today

`price.py` prices a parcel in three steps: it looks up the zone's base rate in
`zone_rates.csv` (7 zones), looks up the weight band's multiplier in
`weight_bands.csv` (6 bands), multiplies them, and then runs
`apply_remote_correction`, which adds a flat 4.50 to heavy parcels (bands B5
and B6) going to the remote zones Z6 and Z7. The result is rounded to the cent.

The correction step was added after launch, when the remote heavy lanes turned
out to lose money. It is the one place the price is not a plain product, and
it is the step people forget when they read the tables on their own.

## The change

Replace `zone_rates.csv`, `weight_bands.csv` and `apply_remote_correction`
with a single `price_table.csv` keyed on `(zone, band)`, one row per pair, 42
rows. Each row holds the final rounded price: base rate times multiplier, plus
the 4.50 where the correction step adds it today. `price()` becomes a band
lookup followed by one table lookup.

`weight_bands.csv` keeps only its `min_kg`/`max_kg` columns, folded into
`price.py` as a constant, because the band boundaries are still needed to find
the band. The multiplier column goes.

The table is generated once from the current three pieces, so every parcel
prices exactly as it does today. After that, the table is the source of truth
and is edited directly; a rate change is a reviewed edit to the rows it
touches.

September's 640 orders are in `orders_2026-09.csv` for checking the
generated table against.

## Why

The three-step lookup is the cause of both pricing incidents this year: each
time, someone changed a base rate in `zone_rates.csv` without noticing that
the correction step also applies to that zone. A single table shows the price
a customer pays, in one place.
