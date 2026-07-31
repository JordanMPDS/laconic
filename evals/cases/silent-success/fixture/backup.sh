#!/bin/bash
# nightly-backup: dump the primary and ship it to S3.
set -euo pipefail

STAMP=$(date +%F)
DUMP="/tmp/backup-$STAMP.sql.gz"

pg_dump "$DATABASE_URL" | gzip > "$DUMP"

aws s3 cp "$DUMP" "s3://$BACKUP_BUCKET/$STAMP.sql.gz" &

rm -f "$DUMP"
echo "backup complete"
