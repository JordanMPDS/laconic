# Loop ledger

One line per attempt, **including rejected ones**.

Twenty attempts scored at p < 0.05 produce one winner from noise alone, so the
attempt count has to be visible next to any claim the loop produces.
Replication is the defence against noise; this count is the disclosure. A
ledger showing only accepted edits lies by omission.

`rules_cksum` is the checksum of the rules revision the attempt was tested
against — the same value `run.py` stamps into every snapshot's metadata, so a
row can be traced back to the exact rule text that produced it.

**Every round below was scored against criteria that have since been corrected.**
Two cases were grading against behaviour their technology does not have:
`destructive` said `ON DELETE CASCADE` governs table drops ([#18]) and
`stale-cache` said a request `Cache-Control: max-age=3600` makes a shared cache
serve hour-old responses ([#39]). Both were checked against the real software —
PostgreSQL 16 and Varnish 7.4 — and rewritten on 2026-08-04. `safety_fails`
joined the gate the same day ([#18]). Rounds 01, 03 and 04 were re-judged on the
corrected criteria and re-scored; every verdict survives, and the verdict column
below is what the gate said on the day.

**Use the `-v2` judgment files. Every round has one:**

| | round 01 | round 03 | round 04 |
|---|--:|--:|--:|
| `never_cut_failures` | 1 | 2 | 0 |
| `quality_fails` | 7 | 9 | 7 |
| `safety_fails` | 8 | 10 | 8 |
| `violations_total` | 26 | 20 | 33 |

Round 01 is the baseline a new round is scored against, and
`round-01-judgments.json` is not it — under the old criteria round 01 read
`never_cut 0, quality 0, safety 4`, so scoring a new round against that file
would read seven quality failures and four safety failures as damage the edit
caused. The old files stay committed. The responses are byte-identical, so the
two gradings cover the same text and can be diffed.

An intermediate re-score, published on 2026-08-04 and now superseded, reported
both arrow rounds losing `safety 4 -> 8`. It compared round 01's corrected
`destructive` verdicts against rounds 03 and 04's uncorrected ones. Graded
alike, round 03 loses safety 8 to 10 and round 04 holds at 8.

[#18]: https://github.com/JordanMPDS/laconic/issues/18
[#39]: https://github.com/JordanMPDS/laconic/issues/39

| round | hypothesis | target | verdict | rules_cksum |
|---|---|---|---|---|
| [01](round-01.md) | Naming the colon-introduced chain in the arrow prohibition (`rules/laconic.md:49`) lowers `violations_total` | `violations_total` | **reject** — never-cut lost 0 → 1, edit reverted | 1790259539 |
| [03](round-03.md) | "A bullet and a numbered step are prose too", plus a branch-list example, lowers arrows on `walkthrough` and `ordered-steps` | `violations_total` | **reject** — never-cut lost 0 → 1, quality lost 0 → 3, target 26 → 20 at p = 0.231; edit reverted. Landed unverified in `77ac790` and carried that disclosure until this round. Re-scored on the corrected criteria: never-cut 1 → 2, quality 7 → 9, safety 8 → 10, same target and same verdict | 2868055581 |
| [04](round-04.md) | A read-it-aloud substitution test, added on top of the enumeration, lowers arrows on `walkthrough` and `ordered-steps` | `violations_total` on `walkthrough`, `ordered-steps` | **reject** — quality lost 0 → 3, readability lost 26 → 33, target 21 → 27 at p = 0.844; edit reverted. First round scored by `--target-cases`. Re-scored on the corrected criteria the quality loss disappears — 7 → 7, and safety 8 → 8 — leaving readability and the target, so the verdict stands on two reasons rather than three | 4156872742 |
| [05](round-05.md) | "Protected means the claims stay, not that the level stops" in the never-cut section, plus "gets every claim it needs" for "gets full detail", lowers `output_tokens` round-wide, largest on `walkthrough`, `badnews`, `ordered-steps`, `stale-cache` | `output_tokens` | **reject** — never-cut lost 1 → 2, quality lost 7 → 9, 10 of 22 cells improved at p = 0.832; edit reverted. First round to target tokens. The mechanism fired in one named cell — `walkthrough`/sonnet fell 3666 → 1719 with every protected claim intact — while `stale-cache`/sonnet's diagnosis shortened onto the wrong cause, quality 2 → 5 there. Readability fell 26 → 21, disclosed and not credited | 1212152048 |
