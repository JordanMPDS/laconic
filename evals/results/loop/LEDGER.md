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
