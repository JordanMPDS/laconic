Our rate limiter keeps two counters per account and folds them into a day total
in a nightly reconcile pass. Should we replace all that with one sliding window
keyed on account plus route?
