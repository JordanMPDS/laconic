"""The watermark: the last instant the exporter claims to have covered.

Kept in one file rather than in the database, because the database is the
thing being exported and a read-only replica cannot hold it.

There is no record of which accounts a given run actually wrote. If a run
dies partway, the accounts it had not reached yet are simply skipped: the
watermark is already past them. Recovering one means re-running by hand with
an explicit --since, which is what run(since=...) is for.
"""
from datetime import datetime
from pathlib import Path

WATERMARK = Path("/var/lib/exporter/watermark")


def read_watermark():
    return datetime.fromisoformat(WATERMARK.read_text().strip())


def write_watermark(now):
    WATERMARK.write_text(now.isoformat())
