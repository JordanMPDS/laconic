# rollup

A scheduled job recomputes the `rollup` table **once a minute**, on the minute,
and writes `computed_at` on every row.

It is the only writer. Nothing else touches the table, and no other process can
know a number changed before this job runs. The schedule is set by the finance
close window and is not something we can shorten.
