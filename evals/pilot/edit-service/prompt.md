the accounts and orders routes update rows by id with no account scoping. how would you fix that? Go ahead and make the change.
<!-- turn -->
accounts get soft-deleted by setting deleted_at, but nothing reads that column. how should that work? Go ahead and make the change.
<!-- turn -->
walk me through what happens to an in-flight request if the pool connection drops part-way through write().
<!-- turn -->
how would you add request logging across these routes? Go ahead and make the change.
<!-- turn -->
POST /orders has no idempotency. how would you add it? Go ahead and make the change.
