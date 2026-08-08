# Checkout redesign — experiment plan

## Goal

The redesigned checkout collapses the shipping and payment steps onto one
page. We believe this lifts completed orders per session. This document is the
plan we will follow to decide whether it ships.

## Assignment

Users are bucketed by a hash of their account id into `control` and
`treatment`, 50/50. The hash is stable, so a user stays in the bucket they
were first assigned for the life of the experiment. Logged-out sessions are
excluded entirely; they are about 8% of checkout starts and we accept losing
them rather than deal with device-id churn.

Assignment happens server-side in `checkout/bucket.py` at the first request of
a session, and the bucket is written to the session record before any
checkout markup is rendered. There is no client-side flicker because nothing
is decided in the browser.

## Instrumentation

Every checkout event already flows through the existing `events` pipeline:

- `checkout_started`
- `shipping_completed`
- `payment_completed`
- `order_placed`

We add no new events. `order_placed` divided by `checkout_started` per bucket
is the metric of record. The pipeline has a known 0.3% event-loss rate that
applies to both buckets equally.

## Metrics

We track eight metrics per bucket:

| metric | why |
| --- | --- |
| completed orders per session | the metric of record |
| revenue per session | guardrail — a lift in orders that cuts basket size is not a win |
| median checkout duration | guardrail |
| payment error rate | guardrail |
| shipping-step drop-off | diagnostic |
| payment-step drop-off | diagnostic |
| support tickets tagged `checkout` | guardrail |
| refund rate within 14 days | guardrail |

A result counts as a win if any of the eight reaches statistical significance
in the treatment's favour and no guardrail has moved against us by more than
2%.

## Duration and decision rule

We expect roughly 4,000 checkout starts per day across both buckets.

The experiment opens on a Monday. **Each morning we pull the dashboard, which
reports a two-sample z-test p-value per metric. The first morning any metric
shows p < 0.05 in the treatment's favour, we stop the experiment and ship the
redesign.** If we reach four weeks without that happening, we stop and keep
the control.

This gives us a 5% false-positive rate, which the team has agreed is an
acceptable risk for a change of this size.

## Rollback

The redesign sits behind the `checkout_v2` flag. Turning the flag off restores
the previous checkout on the next request; no deploy is required and no data
migration is involved. We have tested the flag flip in staging.

## Out of scope

Mobile web is not included in this experiment. The native apps have their own
checkout and are unaffected.
