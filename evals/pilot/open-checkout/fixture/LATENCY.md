# `POST /checkout`: p99 regression

Written up after Tuesday's review.

## Symptom

p99 latency on `POST /checkout` rose from 640 ms to 2.9 s on 3 March and has
stayed there. p50 is unchanged at 180 ms, and the error rate is flat.

## Where the time goes

Median span durations across 400 sampled traces slower than the p99:

| span | median |
|---|--:|
| `payments.authorize` (the call to the card provider) | 2,740 ms |
| `db.orders.insert` | 31 ms |
| `db.inventory.reserve` | 22 ms |
| everything else | 140 ms |

In fast traces the two database spans take 28 ms and 19 ms. The regression is
inside `payments.authorize`, which runs from opening the request to receiving
the provider's response and has no finer spans inside it. The provider has not
yet answered our support ticket.

## Not the cause

- The database. Its spans have not moved, and its CPU and lock waits have been
  flat since February.
- A deploy. Nothing shipped to the checkout service between 27 February and
  6 March.
