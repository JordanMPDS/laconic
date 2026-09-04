Our rate limiter keeps `minute_counter` and `hour_counter` per account and folds
them into a day total in the reconcile pass. Should we replace all three with one
sliding window keyed on account plus route?
