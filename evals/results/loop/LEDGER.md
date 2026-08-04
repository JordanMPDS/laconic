# Loop ledger

One line per attempt, **including rejected ones**.

Twenty attempts scored at p < 0.05 produce one winner from noise alone, so the
attempt count has to be visible next to any claim the loop produces.
Replication is the defence against noise; this count is the disclosure. A
ledger showing only accepted edits lies by omission.

`rules_cksum` is the checksum of the rules revision the attempt was tested
against — the same value `run.py` stamps into every snapshot's metadata, so a
row can be traced back to the exact rule text that produced it.

**Rounds 01, 03 and 04 were scored before the gate counted safety verdicts.**
`safety_fails` was added on 2026-08-04 ([#18]). Re-scoring the committed
snapshots, rounds 03 and 04 each also lost `safety 4 -> 8` — a reason neither
verdict printed at the time. Both still reject, and the verdict column below is
what the gate said on the day. The re-scores are in each round's own document.

[#18]: https://github.com/JordanMPDS/laconic/issues/18

| round | hypothesis | target | verdict | rules_cksum |
|---|---|---|---|---|
| [01](round-01.md) | Naming the colon-introduced chain in the arrow prohibition (`rules/laconic.md:49`) lowers `violations_total` | `violations_total` | **reject** — never-cut lost 0 → 1, edit reverted | 1790259539 |
| [03](round-03.md) | "A bullet and a numbered step are prose too", plus a branch-list example, lowers arrows on `walkthrough` and `ordered-steps` | `violations_total` | **reject** — never-cut lost 0 → 1, quality lost 0 → 3, target 26 → 20 at p = 0.231; edit reverted. Landed unverified in `77ac790` and carried that disclosure until this round | 2868055581 |
| [04](round-04.md) | A read-it-aloud substitution test, added on top of the enumeration, lowers arrows on `walkthrough` and `ordered-steps` | `violations_total` on `walkthrough`, `ordered-steps` | **reject** — quality lost 0 → 3, readability lost 26 → 33, target 21 → 27 at p = 0.844; edit reverted. First round scored by `--target-cases` | 4156872742 |
