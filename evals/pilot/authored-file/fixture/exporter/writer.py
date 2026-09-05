import csv
from pathlib import Path

OUT = Path("/srv/exports")

COLUMNS = ("account_id", "name", "plan", "seats", "mrr_cents", "renewed_on")


def write(account):
    path = OUT / ("%s.csv" % account.slug)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for row in account.rows():
            w.writerow([row[c] for c in COLUMNS])
    return path
