We agreed to replace the two rate-limit counters with one sliding window. So
that means we drop `minute_counter` and `hour_counter` and the reconcile pass,
and just key the window on account plus route — right?
