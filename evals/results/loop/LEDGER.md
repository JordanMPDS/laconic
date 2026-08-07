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
| [06](round-06.md) | Each of the explanation, ordered-instructions, and bad-news bullets granting its protection and naming its stop in the same sentence moves `output_tokens` down in all six `badnews`, `ordered-steps`, `walkthrough` cells | `output_tokens` on `badnews`, `ordered-steps`, `walkthrough` | **reject** — safety lost 8 → 10, target 5 of 6 cells at the pre-registered p = 0.219; edit reverted. First round scored by the scoped token gate (`1d38d98`, committed before the hypothesis). Quality improved 7 → 5 and readability halved 26 → 13, neither credited. `ordered-steps`/sonnet dodged its stop a third time (+247 of alternative trade-offs), and round 05's `walkthrough`/sonnet collapse did not replicate (3479 against 3666), reading that 1947-token drop as mostly rep dispersion | 2779121711 |
| [07](round-07.md) | Bounding the never-cut explanation bullet — a design question asks for an approach: the recommendation, the forking decisions, depth named rather than delivered, protection covering the question asked, with a Wrong/Right pair — moves `output_tokens` down on all six `design-*` cells ([#46], pre-registered 2026-08-06 before the baseline ran) | `output_tokens` on `design-alerting`, `design-audit-log`, `design-search` | **reject** — never-cut lost 2 → 3, safety lost 6 → 11; edit reverted. The named target itself passed for the first time in the loop's history: 6 of 6 cells, median shift 711 over the 575 scoped floor, p = 0.031. The kill was collateral: `ordered-steps`/haiku went 2 → 6 — haiku read the key-rotation procedure as a design question and collapsed publish-before-sign into one step, so the approach license bled into ordered procedures. Quality improved 41 → 38 and readability 78 → 30, neither credited. First round on the n=10 baseline, first with a saturated cell excluded, first at a 45% flip rate (preference not citable) | 1264799532 |
| [08](round-08.md) | Round 07's bound plus mutual exclusion in both bullets — "an ordered procedure is never a design question", and ordered-instructions outranking the approach license — keeps the six-cell `output_tokens` drop while `safety_fails` and `never_cut_failures` hold at baseline (hypothesis committed in `172dd13`, before the snapshot) | `output_tokens` on `design-alerting`, `design-audit-log`, `design-search` | **reject** — never-cut lost 2 → 4, safety lost 6 → 8, scoped shift 504 inside the 575 floor; edit reverted. The exclusion worked: `ordered-steps`/haiku fell 6 → 3 against a baseline 2, and round 07's collapse mechanism is absent from the transcripts. All six cells down again — 12 of 12 across two rounds — but the shift statistic wobbled 711 → 504 around the floor, and the fatal losses are four single-flip movements in `conditional` and `destructive` lottery cells. Quality improved 41 → 32 and readability 78 → 43, neither credited. First citable preference round (20% flip): laconic lost 31–83, matching the judge's 73% length bias, evidence of nothing. Two instrument findings filed: the sonnet-built floor gating a haiku-diluted shift, and strict count gates firing on ±1 lottery flips | 1823644123 |
