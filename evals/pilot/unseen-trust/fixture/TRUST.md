# Internal CA rotation: root R1 to root R2

Owner: platform-security. Reviewers: SRE (edge), device fleet team.
Status: cross-signing approved, 2026-11-04.

Every internal TLS certificate, from service-to-service mTLS to the admin
consoles and the 14,000 field gateways, chains to the internal root R1, which
expires on 2027-03-31. Its replacement, root R2, has a new key held in the HSM
cluster `hsm-sec-2`. The rotation runs in two stages, cross-signing and then
R1's retirement, and the second does not start until the first has passed.

## Stage 1: cross-signing

### What runs

- R2 is issued, and R1 signs a cross-certificate for it,
  `r2-cross-r1.pem`, so a client that trusts only R1 can still validate a
  chain that ends at R2.
- The trust bundle `ca-bundle-2026q4` adds R2 beside R1. It reaches every
  service image through the base-image pipeline `baseimg-nightly`, which
  rebuilds at 02:15 UTC.
- Field gateways fetch the bundle on their monthly check-in, over the update
  channel `gw-stable`.
- Leaf certificates are still issued from R1's intermediate `int-r1-07`.

No client relies on R2 yet. If R2 were wrong, no connection would depend on
it.

### Checks

The scanner `trust-audit` runs every 6 hours. It connects to every registered
service endpoint and records, in the table `trust_audit_results`, which roots
that endpoint's trust store accepts. Gateways report their bundle version in
the check-in payload, in the field `bundle_rev`.

### Exit criteria

All of these must hold before stage 2 starts:

1. Every service image built after 2026-11-10 carries the new bundle.
2. `trust-audit` shows R2 accepted by 100% of service endpoints for 7
   consecutive days.
3. At least 99.5% of field gateways report the new bundle.
4. A canary set of 50 leaf certificates issued from R2's intermediate
   `int-r2-01` has served traffic for 14 days with no handshake failure.

### Alerts

- `PKI-201`: handshake failure rate above 0.2% on any canary endpoint for 10
  minutes.
- `PKI-202`: `trust-audit` finds an endpoint that rejects R2.

Both page `#pki-oncall`.

## Stage 2: R1's retirement

### What runs

1. **Issuance switch.** The flag `pki.issue_from_r2` moves all new leaf
   issuance to R2's intermediate. Existing R1 leaves keep working until they
   expire, and a leaf lives 30 days, so within a month every service presents
   an R2 chain.
2. **Bundle trim.** After 45 days of R2 issuance, the bundle
   `ca-bundle-2027q1` drops R1.
3. **Revocation.** R1's cross-certificate and its intermediate are revoked,
   and R1's key is destroyed in a witnessed ceremony under change ticket
   `CHG-9120`.

### Exit criteria

The retirement is done when no handshake in 14 days has used an R1 chain, as
counted by the edge metric `tls_chain_root`, and the key destruction is signed
off by the security lead and an external witness.

### The gateway caveat

**The 99.5% in stage 1 is counted over gateways that checked in during the
last 30 days, not over the fleet.** A gateway that is offline, at a customer
site with its link down or powered off in a warehouse, keeps the old bundle
until it next connects, and the fleet team's records show 2.3% of gateways go
more than 90 days between check-ins. Until the revocation those gateways
still work, because the cross-certificate lets an R1-only trust store
validate an R2 chain. The revocation removes exactly that path. A gateway
that has not taken the new bundle by then cannot reach the control plane, and
so cannot fetch the bundle over it either: each one needs a site visit or a
USB recovery image. The bundle trim can be undone by pushing R1 back; a
revoked cross-certificate cannot be un-revoked.

### Alerts

- `PKI-301`: any handshake on an R1 chain after the bundle trim.
- `PKI-305`: gateway check-ins below 97% of the fleet in a day.

Both page `#pki-oncall` and post to `#ca-rotation`.

## Timeline

| step | dates |
|---|---|
| R2 issued and cross-signed | 2026-11-10 |
| new bundle in all images | about 2026-11-17 |
| canary leaves | 2026-11-18 to 2026-12-02 |
| issuance switch | 2026-12-03 |
| bundle trim | 2027-01-17 |
| revocation and key destruction | 2027-02-14, needs sign-off |
| R1 expires | 2027-03-31 |

The device team's holiday freeze runs 2026-12-18 to 2027-01-04, and no
gateway bundle is pushed during it. A gateway that misses its December
check-in gets the new bundle in January at the earliest.
