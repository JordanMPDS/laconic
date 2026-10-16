"""Requests-per-minute limit for an account: the plan's limit scaled by the
region's capacity factor, then the legacy free-tier cap."""
import csv
from pathlib import Path

HERE = Path(__file__).parent
CAPPED_REGIONS = {"ap-south", "sa-east"}
LEGACY_FREE_CAP = 20


def _load(name, key, value, cast):
    with (HERE / name).open() as f:
        return {r[key]: cast(r[value]) for r in csv.DictReader(f)}


PLANS = _load("plan_limits.csv", "plan", "requests_per_minute", int)
FACTORS = _load("region_factors.csv", "region", "factor", float)


def apply_legacy_cap(plan, region, limit):
    """Free accounts in the two smallest regions keep the cap they launched
    with, because those regions share one gateway pool."""
    if plan == "free" and region in CAPPED_REGIONS:
        return min(limit, LEGACY_FREE_CAP)
    return limit


def limit_for(plan, region):
    scaled = int(PLANS[plan] * FACTORS[region])
    return apply_legacy_cap(plan, region, scaled)
