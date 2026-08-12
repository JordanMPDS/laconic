# Edge

Every request already arrives through the CDN. It has been in front of this
service since launch and it terminates TLS for `shop.example.com`.

Its cache is configured to respect origin headers and nothing else: no path
rules, no forced TTLs, no cookie stripping. Whatever the app sends in
`Cache-Control` is what the edge does.

Current hit rate across all paths: **0%**.

The contract with platform engineering is that cache policy is the
application's decision, expressed in response headers. They will not add path
rules on our behalf, and a request to do so was declined last quarter on the
grounds that it would put the policy in two places.
