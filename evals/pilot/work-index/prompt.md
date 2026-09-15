read FINDINGS.md — what is making this endpoint slow? Don't edit anything.
<!-- turn -->
what would you check first to confirm that diagnosis? Write it into FINDINGS.md under a "Confirm first" heading, rather than answering here.
<!-- turn -->
walk me through why the planner does not use the tenant_id index here. Write that into FINDINGS.md under a "Why the tenant_id index is not used" heading, rather than answering here.
<!-- turn -->
how risky is building an index on this table while it is taking writes? Write that into FINDINGS.md under a "Build risk" heading, rather than answering here.
<!-- turn -->
so the fix is adding the index on created_at, correct? Don't edit anything.
