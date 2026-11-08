# Planned primary switchover: db-a to db-b

Run during the announced maintenance window. db-b is a streaming replica of
db-a, and the application reaches the database through pgbouncer.

1. Put the application in read-only mode from the admin panel (Settings,
   Maintenance, Read-only). Writes fail fast with a banner; reads keep working.
2. On db-a, run `SELECT pg_current_wal_lsn();` and note the value. On db-b,
   wait until `SELECT pg_last_wal_replay_lsn();` has reached it. Promoting
   before it has throws away every write that had not replayed yet.
3. Stop db-a (`sudo systemctl stop postgresql`) and confirm it refuses
   connections. If db-a is still up when db-b is promoted, both accept writes
   and the two histories cannot be merged afterwards.
4. Promote db-b: `sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main`.
5. Point pgbouncer at db-b (`host=db-b` in `/etc/pgbouncer/pgbouncer.ini`,
   then `RELOAD;` on the pgbouncer admin console), and only then turn
   read-only mode off.
