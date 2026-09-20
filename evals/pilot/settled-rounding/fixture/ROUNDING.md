# ADR 021: tax rounds at the invoice line

Status: **accepted**, 2025-09-30. Closed. The rationale below is the whole
argument as it was made; nothing in it was deferred.

## Decision

Money is stored as integer cents in `amount_cents`. Tax is computed per invoice
line and rounded half-up **at the line**, in `tax.py:line_tax`. The invoice
total is the sum of the rounded line taxes. Nothing rounds a second time.

A consequence follows and is expected: the invoice total can differ by one cent
from the tax computed on the summed subtotal. On a 40-line invoice it is a cent
either way about a third of the time. Reconciliation treats a difference of one
cent per invoice as matched; support macro 212 answers the customer question.

## Why at the line

1. The filing guidance we are assessed against requires the tax shown against
   each line to be the tax charged for that line. A total-level rounding
   produces line numbers that do not add up to what was charged, and the audit
   in March 2025 raised exactly that against the previous implementation.
2. The line is what the customer sees. A credit note reverses one line, so the
   line has to carry a number that can be reversed exactly.
3. Every downstream system already reads the line. The ledger posts per line
   and the revenue export groups by line.

## What this costs, and why it was accepted anyway

The one-cent difference is real, it reaches customers, and it generates about
four support contacts a month. That was raised in review, priced against a
filing exposure the audit had already named, and accepted. It is expected
output rather than a defect, and the decision is closed.
