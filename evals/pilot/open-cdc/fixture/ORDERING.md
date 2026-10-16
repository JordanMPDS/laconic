# Out-of-order changes in `raw.order_events`

Measured for the ticket and reviewed with the pipeline's owner.

## The pipeline

1. `wal2queue`, the change-data-capture connector, reads the `orders`
   database's write-ahead log and publishes one message per row change to the
   `order-changes` topic. Its sink settings live in the pipeline owner's
   deployment and were not collected for this write-up.
2. The topic stamps each message with `publish_time` at the moment it accepts
   the message from the connector.
3. The `orders-raw` subscription writes each message into `raw.order_events`,
   copying the message's `publish_time` and `lsn` (the change's position in the
   log) into columns of the same names. It does not record when it wrote the
   row.

## What was measured

Seven days, 2.1 million changes. Among rows that changed more than once within
a minute, 1.4% have a change whose `lsn` is older than the next change to the
same row but whose `publish_time` is later. The gap between a change's commit
time and its `publish_time` has a median of 0.4 seconds and a maximum of 38
seconds.

## Where the reordering happens

Between the connector and the topic. `publish_time` is assigned when the topic
accepts a message, and the subscription only copies it. If the subscription
wrote rows out of order, the stored `publish_time` values would not change, so
nothing the subscription does can put an older `lsn` behind a newer one in
`publish_time`. A change with an older `lsn` and a later `publish_time` reached
the topic late.

The subscription is not the cause. Its delivery order decides only the physical
insert order of `raw.order_events`, and nothing reads the table in insert
order.
