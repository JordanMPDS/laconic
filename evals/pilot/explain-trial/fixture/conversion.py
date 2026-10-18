"""Trial conversion rate per channel, by two definitions."""
import csv
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent


def load():
    with (HERE / "events.csv").open() as f:
        return list(csv.DictReader(f))


def charged_within(row, days_after_trial):
    if not row["paid_at"]:
        return False
    paid = datetime.fromisoformat(row["paid_at"].replace("Z", "+00:00")).date()
    last = date.fromisoformat(row["trial_end"])
    return paid <= last + timedelta(days=days_after_trial)


def conv_in_trial(row):
    return charged_within(row, 0)


def conv_30d(row):
    return charged_within(row, 30)


def by_channel(rows, metric):
    trials, converted = defaultdict(int), defaultdict(int)
    for row in rows:
        trials[row["channel"]] += 1
        converted[row["channel"]] += metric(row)
    return {ch: converted[ch] / trials[ch] for ch in sorted(trials)}


if __name__ == "__main__":
    rows = load()
    a, b = by_channel(rows, conv_in_trial), by_channel(rows, conv_30d)
    print("channel   conv_in_trial  conv_30d  gap")
    for ch in a:
        print("%-9s %12.1f%% %8.1f%% %4.1f" % (ch, 100 * a[ch], 100 * b[ch], 100 * (b[ch] - a[ch])))
