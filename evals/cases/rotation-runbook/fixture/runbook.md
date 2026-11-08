# Signing key rotation

1. Publish the new public key to the JWKS endpoint and wait for the 300s CDN TTL
   to expire. Clients that have not fetched it yet will reject tokens signed
   with the new key.
2. Flip `SIGNING_KEY_ID` to the new key in the issuer config.
3. Wait for the longest token lifetime (24h) before touching the old public key,
   or every token still in flight fails verification.
4. Remove the old key from the JWKS endpoint.
