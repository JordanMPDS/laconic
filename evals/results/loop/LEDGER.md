# Loop ledger

One line per attempt, **including rejected ones**.

Twenty attempts scored at p < 0.05 produce one winner from noise alone, so the
attempt count has to be visible next to any claim the loop produces.
Replication is the defence against noise; this count is the disclosure. A
ledger showing only accepted edits lies by omission.

`rules_cksum` is the checksum of the rules revision the attempt was tested
against — the same value `run.py` stamps into every snapshot's metadata, so a
row can be traced back to the exact rule text that produced it.

| round | hypothesis | target | verdict | rules_cksum |
|---|---|---|---|---|
| [01](round-01.md) | Naming the colon-introduced chain in the arrow prohibition (`rules/laconic.md:49`) lowers `violations_total` | `violations_total` | **reject** — never-cut lost 0 → 1, edit reverted | 1790259539 |
| — | "A bullet and a numbered step are prose too", plus a branch-list example, lowers arrows on `walkthrough` | `violations_total` | **unverified — landed ahead of its round.** A 20-call spot check moved `walkthrough` 17 → 3 and `ordered-steps` 4 → 9; no judging, no accept gate, no replication, no holdout. Owed a full round | 2868055581 |
