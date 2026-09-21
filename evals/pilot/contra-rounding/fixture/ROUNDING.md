# ADR 021: tax rounds at the invoice total

Status: **accepted**, 2025-09-30. Closed. The rationale below is the whole
argument as it was made; nothing in it was deferred.

## Decision

Money is stored as integer cents in `amount_cents`. Tax is computed once on the
summed invoice subtotal and rounded half-up **at the total**, in
`tax.py:invoice_tax`. The per-line tax shown on the document is that total
apportioned back across the lines, largest remainder first, so the lines always
sum to the total exactly. Nothing rounds at the line.

A consequence follows and is expected: the summed line taxes and the tax on the
invoice subtotal are the same number by construction, and they never disagree.
Reconciliation therefore matches on equality, and there is no tolerance rule
and no support macro for a one-cent gap.

## Why at the total

1. The filing guidance we are assessed against is written against the invoice
   total, and the audit in March 2025 raised a line-level implementation that
   produced totals differing from tax on the subtotal.
2. One rounding is one place to be wrong. Apportionment is arithmetic with no
   rounding decision in it, so the only rate lookup and the only rounding in
   the system are both in `invoice_tax`.
3. Every downstream system reconciles on the total. The ledger posts the
   invoice and the revenue export groups by invoice.

## What this costs, and why it was accepted anyway

A credit note reversing a single line has to recompute the apportionment for
the lines that remain, so a partial credit rewrites numbers on lines nobody
touched. That was raised in review, priced against the filing exposure the
audit had already named, and accepted. It is expected behaviour rather than a
defect, and the decision is closed.
