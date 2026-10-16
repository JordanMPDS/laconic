# `db-primary-2`: data volume at 97%

Investigated for the on-call handoff.

## Symptom

The 800 GB volume mounted at `/var/lib/postgresql` on `db-primary-2` went from
46% to 97% used in nine days. `DataVolumeHigh` fired at 02:10 this morning.

## What is on the volume

`du -sh` at 09:40:

```
423G    /var/lib/postgresql/16/main/pg_wal
351G    /var/lib/postgresql/16/main/base
2.1G    /var/lib/postgresql/16/main/log
48M     /var/lib/postgresql/16/main/global
```

The backup job's inventory from nine days ago recorded `pg_wal` at 22G and
`base` at 341G. Nothing past this `du` has been run; the on-call who found it
went off shift.

## Where the growth is

`pg_wal`. It grew by 401G in nine days, while `base` grew by 10G.

The application's logs are not on this volume. The app servers write them to
`/var/log/app` on their own hosts and ship them from there. Postgres's own
server log, under `main/log`, is 2.1G and rotates daily; it has not grown.
