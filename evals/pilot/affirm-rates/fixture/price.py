"""Shipping price for one parcel: zone base rate times weight-band multiplier,
then the remote-zone correction."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
REMOTE_ZONES = {"Z6", "Z7"}
HEAVY_BANDS = {"B5", "B6"}
REMOTE_HEAVY_SURCHARGE = Decimal("4.50")


def _load():
    with (HERE / "zone_rates.csv").open() as f:
        zones = {r["zone"]: Decimal(r["base_rate"]) for r in csv.DictReader(f)}
    with (HERE / "weight_bands.csv").open() as f:
        bands = [(r["band"], float(r["min_kg"]), float(r["max_kg"]),
                  Decimal(r["multiplier"])) for r in csv.DictReader(f)]
    return zones, bands


ZONES, BANDS = _load()


def band_for(weight_kg):
    for band, lo, hi, _ in BANDS:
        if lo <= weight_kg < hi:
            return band
    raise ValueError("no band for %.1f kg" % weight_kg)


def apply_remote_correction(zone, band, price):
    """Remote zones lose money on heavy parcels at the plain rate."""
    if zone in REMOTE_ZONES and band in HEAVY_BANDS:
        return price + REMOTE_HEAVY_SURCHARGE
    return price


def price(zone, weight_kg):
    band = band_for(weight_kg)
    multiplier = next(m for b, _, _, m in BANDS if b == band)
    raw = ZONES[zone] * multiplier
    corrected = apply_remote_correction(zone, band, raw)
    return corrected.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
