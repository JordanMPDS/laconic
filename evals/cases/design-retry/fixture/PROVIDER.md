# Cardstream integration notes

Vendor documentation, summarised for this repository. Nothing here is our code.

## Timeouts

A timeout on `POST /v2/charges` tells you nothing about whether the charge was
made. The vendor accepts the request, authorises against the issuer, and only
then writes its response; a connection that dies at ten seconds may have died
before the authorisation or after it. The vendor's own guidance is that a
timed-out charge must be treated as **unknown**, never as failed.

## Idempotency

`POST /v2/charges` accepts an `Idempotency-Key` header. Two requests carrying
the same key within 24 hours return the same charge — the second is not
authorised again, and the response body is byte-identical to the first,
including the original charge id. Keys are scoped per API key.

The header is optional and we do not send it.

## Rate limits

600 requests per minute per API key. We are nowhere near it.
