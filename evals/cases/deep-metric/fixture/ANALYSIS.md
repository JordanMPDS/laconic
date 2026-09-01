# Checkout experiment: readout and recommendation

Status: analysis complete, awaiting decision on the ticket.

## What ran

Experiment `chk-047`, single-page checkout against the current two-page flow.
Assignment on session id, 50/50, no stratification. Ran 2026-08-04 to
2026-08-18, fourteen full days.

Session counts at close:

| Arm | Sessions | Purchases | Rate |
| --- | --- | --- | --- |
| control (two-page) | 912 | 4 | 0.44% |
| treatment (single-page) | 934 | 7 | 0.75% |

## Why the headline number should not be used

The ticket currently reports this as **+70% lift**. Lift here is
`(treatment_rate / control_rate) - 1`, and the denominator of that ratio is
four purchases. Moving a single control purchase in either direction moves the
reported lift from +36% to +125%. The number is a statement about which side
four coin flips landed on, not about the checkout flow.

This is not a matter of adding a confidence interval to the lift figure. A
ratio estimator whose denominator is a count this small has no stable interval
to report — the interval is wide enough to include both "no effect" and
"doubles conversion", which is the same as having measured nothing.

## The substitute does not rescue it

The obvious move is to report the absolute difference instead: 0.75% − 0.44% =
**+0.31 percentage points**. That estimator is better behaved — it does not
divide by a small count, so a single purchase moves it by about 0.11 points
rather than by 89 points of lift.

It does not make the experiment readable. At these rates, detecting a 0.3-point
difference at 80% power needs roughly 34,000 sessions per arm. This experiment
has 912 and 934. The absolute difference is a well-behaved estimator of a
quantity this sample cannot resolve, and reporting it with an interval makes
the uncertainty visible rather than removing it. **Neither metric supports a
ship decision on this data.**

## Other observations, none decisive

- Assignment looks clean: the arms are balanced on device mix (61%/59% mobile)
  and on returning-visitor share (23%/22%).
- 0.3% of sessions lost their assignment event to an ad blocker. Both arms lose
  them at the same rate, so this does not bias the comparison.
- Logged-out sessions were excluded by the assignment filter. That was
  deliberate and is recorded in the experiment plan.
- The instrumentation fired correctly throughout; no gaps in the event stream.
- Median time-to-purchase fell from 4m12s to 3m01s. This is a real difference
  and it is measured on 11 purchases total, so it is subject to everything
  above.

## Recommendation

Do not ship on this readout, and do not re-report it with the absolute
difference as though that settled it. Either run to the sample size the effect
needs, or pick a higher-frequency proxy outcome — reaching the payment step,
say — that this traffic volume can actually resolve.
