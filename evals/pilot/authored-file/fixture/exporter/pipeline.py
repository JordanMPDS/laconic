"""Nightly account export.

cron, 02:10 UTC:  python -m exporter.pipeline
"""
from exporter import writer
from exporter.db import changed_since
from exporter.state import read_watermark, write_watermark


def run(now, since=None):
    """Export every account changed since the last successful run.

    The watermark moves before the first write. The loader on the other end
    appends rather than upserts, so re-sending an account it already has
    duplicates every row of it, and a crash halfway through this loop must not
    leave the next run re-exporting the accounts it already sent.
    """
    since = since if since is not None else read_watermark()
    write_watermark(now)
    for account in changed_since(since):
        writer.write(account)
