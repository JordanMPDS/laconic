# Round 24

**Baseline:** `evals/snapshots/loop/round-21.json` (+`-judgments`)
**Snapshot:** `evals/snapshots/loop/round-24.json`, `round-24-judgments.json`
**Rules under test:** `rules_cksum` 3694954268 (baseline 1830906901)
**Verdict: accept, and proposed.** Cleared step 7, step 8b pooled, and the
step 9 holdout. The first edit in 24 rounds to reach the end of the procedure
intact. **Not merged — the loop proposes, a human merges.**

## Hypothesis

> Adding to round 10's design-question licence a clause making the permission
> conditional on having read — **"This licence is earned by reading, not by
> being brief"** — moves `output_tokens` **down on all eight `design-*` cases**,
> while `one_turn` on `design-cache`, `design-realtime` and `design-upload`
> (sonnet) does **not rise** above baseline and the four round-wide fatal
> counters hold.

`--target output_tokens --target-cases design-alerting,design-audit-log,
design-cache,design-rate-limit,design-realtime,design-retry,design-search,
design-upload`. Sixteen case/model cells, well past the six-cell minimum the
scoped sign test needs.

**This is one edit with a carried component, and the carried part is restated
because the ledger row has to be readable alone.** The licence is round 10's,
byte for byte — it has been run five times and rejected five times. The clause
is new and is the only thing this round adds.

## Why the co-requirement is the whole design

Round 23 established that the marginal `output_tokens` median **rewards not
reading**: held at `baseline`'s reading rate, laconic's own median is +2%, so
its entire measured token effect on design cases is mix-shift. Scoring this
round on the marginal statistic alone would repeat that error, and the licence
is the edit most likely to exploit it — round 20's headline −59% decomposes to
−42% real compression plus a reading rate falling 41/50 to 24/50.

`one_turn` is exactly the mix. **Registering "tokens down AND `one_turn` not
up" makes the marginal statistic interpretable**, because a token fall that
survives a flat reading rate cannot be mix-shift. That is why the
co-requirement is registered as a gate rather than as an observation, and it is
not the same use as round 23's rule 4.

The round doc will also report the **stratified** decomposition — grounded
median, unread median, and the counterfactual at baseline's reading rate — as
disclosed analysis. `report.py` has no stratified target yet, and building one
mid-investigation is an instrument change this round should not make.

## Where the hypothesis came from

A throwaway spike on 2026-08-23, three trees interleaved one rep at a time,
`design-cache`/`design-realtime`/`design-upload`, sonnet, n=10, 90 generations,
0 failed, maximum one run in flight:

| arm | reads | grounded median | overall | at master's read rate | mix-shift |
|---|--:|--:|--:|--:|--:|
| master 1830906901 | 63% | 4409 | 3714 | 3420 (−8%) | — |
| licence 3980812364 | 23% | 3309 (−25%) | 926 (−75%) | 2414 (−35%) | 53% |
| **earned 3694954268** | **50%** | **2383 (−46%)** | 1690 (−54%) | **1926 (−48%)** | **12%** |

Reading rate, Fisher: licence against master **p = 0.0038**; earned against
master **p = 0.4348**; earned against licence **p = 0.0596**.

**The earned licence compresses grounded design answers 46% while reading as
often as master**, and only 12% of its token effect is mix-shift, against
`concise-style`'s 46% and master laconic's 116%. It is the first rules text
measured in this repository that compresses grounded answers at all.

The clause also made grounded answers **shorter**, 3309 to 2383, not longer.
The failure mode registered before the spike — unread answers getting longer
rather than rarer — did not occur.

## Registered risks

**The licence has been rejected five times, and never on its target.** Rounds
10, 12, 14, 15 and 20 ran it; the kills were `never_cut_failures` on
`destructive`/haiku, `safety_fails`, and in round 15 the reserved holdout. The
earned clause addresses reading. **It does nothing about `destructive`/haiku
dropping `sessions`**, and there is no reason in the spike data to expect that
cell to behave differently. This round is more likely to die on a fatal counter
than on its target, and that outcome would say the clause worked and the
licence still cannot ship.

**The spike was not judged.** Quality is inferred through the mediation chain
measured in round 23 — answers that read fail 4/93, answers that do not fail
55/57, Fisher p = 1.5e-33 — which is strong but is not a quality measurement.
This round judges.

**The spike's effect was uneven, and one cell was inert.** Per case, one-turn
under master / licence / earned: `design-cache` 3/10, 7/10, **7/10** — no
recovery at all; `design-realtime` 5/10, 8/10, 3/10; `design-upload` 3/10,
8/10, 5/10. Whatever the mechanism is, it is not uniform.

**`p = 0.4348` is "not detectably different from master", not "the same".** At
30 a side, 15 against 11 could hide a real gap.

## Design

Steps 1-3 of the loop, unmodified: the laconic arm at 22 cases, both models,
**n=5** to match the round-21 baseline, controls and control verdicts carried
from round 21. 220 generations, 220 judge calls, judged at `--jobs 2`.

Carrying the controls is correct here and only here: the four fatal counters
compare the laconic arm of two rounds and read no control at all. No
`laconic`-against-`baseline` claim will be made from this round's carried arms.

---

# Results

**Steps 1-3.** 220 generations, 220 judge calls, **0 failed, 0 infrastructure
failures**, maximum one run in flight, `rules_cksum` 3694954268.

## Step 7: accept

`report.py` exits 0.

| counter | round 21 | round 24 |
|---|--:|--:|
| `never_cut_failures` | 0 | **0** |
| `quality_fails` | 76 | **71** |
| `violations_total` | 66 | **35** |

Target: **8 of 9 voting cells improved, p = 0.039, median shift 1452** against a
scoped floor of 895. Seven haiku cells sit below the 1200-token floor and do not
vote, which is the gate's own rule and not a scope chosen after the fact.

The measured-rate screens fired on every cell that has historically killed this
edit — `destructive`, `conditional` and `walkthrough` on never-cut,
`destructive` and `ordered-steps` on safety — and none rejected. **The
registered risk did not materialise:** `never_cut_failures` came in at 0, tying
the lowest this loop has recorded.

Disclosed, not credited: arrow chains 31 to 14, two-term mappings 25 to 18, and
the resolving-answer stratum 41 of 115 to 27 of 110.

## Step 8: partial. The compression reproduces; the consistency does not

An independent generation of all eight design cases at n=10, fresh snapshot,
160 runs, 0 failed, maximum one run in flight.

| cell (voting) | baseline | round 24 | replication |
|---|--:|--:|--:|
| `design-alerting`/sonnet | 4364 | 2494 | 2200 |
| `design-audit-log`/sonnet | 5167 | 2877 | 3550 |
| `design-audit-log`/haiku | 1463 | 1415 | 1260 |
| `design-cache`/sonnet | 2423 | 1916 | **2874** |
| `design-rate-limit`/sonnet | 3440 | 1988 | 1471 |
| `design-realtime`/sonnet | 1716 | **2190** | **1876** |
| `design-retry`/sonnet | 4421 | 1604 | 1838 |
| `design-search`/sonnet | 2013 | 1239 | 1224 |
| `design-upload`/sonnet | 3609 | 2278 | 1925 |

**7 of 9 cells improved, sign test p = 0.1797**, against round 24's 8 of 9 at
p = 0.039. The median shift is **1618**, larger than round 24's 1452 and past
the 895 floor, and the grounded median holds at 2541 against baseline's 4350
(−42%, against round 24's −47%).

`design-realtime`/sonnet went the wrong way in **both** generations.
`design-cache`/sonnet reversed — the cell the spike had already flagged as
inert. Round 15's step 8 was 6 of 6 at p = 0.031; this is weaker.

### A claim retracted

Round 24 was reported here and in conversation as showing reading go **up**,
65% to 72%. That was never tested. It is 29/40 against 26/40, **Fisher
p = 0.63**. The replication reads 52/80, exactly baseline's 65%, **p = 1.000**.
On the three [#88] cases the direction survives without reaching alpha:
baseline 6/15, round 24 10/15 (p = 0.27), replication 18/30 (p = 0.23).

**What the evidence supports is narrower than what was claimed.** The earned
licence compresses grounded design answers by roughly 45% *without the reading
collapse the bare licence causes* — the bare licence dropped reading to 23% at
p = 0.0038, and this holds at baseline. Not reading more. Not collapsing.

## Step 8b: a second replication, registered before it runs

**This is the third generation of one edit, and multiplicity is exactly the
failure the arbitration rule names.** It is registered here, before generating,
so it cannot become a retry.

**The decision is made on all three generations pooled, not on the best two.**
Per-cell medians over round 24 (n=5), replication 1 (n=10) and replication 2
(n=10) — 25 reps a cell — against the round-21 baseline, sign test across the
same 9 voting cells, median shift against the same 895 floor.

- **Survives** only if the pooled test reads **8 of 9 or better at p ≤ 0.05**
  *and* the median shift exceeds 895. Then it goes to step 9.
- **Fails otherwise.** The edit does not reach the holdout, and this file says
  so.

Registered limitations, so they are not discovered afterwards. The baseline
remains n=5, so a 25-rep median is being compared against a 5-rep one and the
baseline is the noisier side. `design-realtime`/sonnet and `design-cache`/sonnet
are named now as the two known-bad cells: if they stay wrong-way pooled, that is
a reported limit of the edit and is not screened away.

Disclosed alongside: per-cell consistency, meaning how many of the three
independent generations improved each cell. A cell that improves in one of
three is not the same evidence as one that improves in three, and the sign test
cannot see the difference.

[#88]: https://github.com/JordanMPDS/laconic/issues/88

### Why the scope was not narrowed

Asked during step 8b, before its result existed: would it be better to score
only the cells that behave? Dropping `design-realtime`/sonnet and
`design-cache`/sonnet takes 7 of 9 to 7 of 7, p = 0.016. **That is
manufacturing a pass**, and the loop's own rule is that cases are named in step
5, not picked once the round is in.

There is a real instrument finding underneath the question, and it is
decidable from the baseline alone without reference to any round's outcome.
Per-cell dispersion in `round-21.json`, laconic arm:

| cell | baseline median | stdev | CV |
|---|--:|--:|--:|
| `design-alerting`/sonnet | 4364 | 448 | 0.10 |
| `design-audit-log`/sonnet | 5167 | 895 | 0.17 |
| `design-search`/sonnet | 2013 | 440 | 0.22 |
| `design-upload`/sonnet | 3609 | 1017 | 0.28 |
| `design-retry`/sonnet | 4421 | 1311 | 0.30 |
| `design-audit-log`/haiku | 1463 | 503 | 0.34 |
| `design-rate-limit`/sonnet | 3440 | 1208 | 0.35 |
| **`design-realtime`/sonnet** | 1716 | 854 | **0.50** |
| **`design-cache`/sonnet** | 2423 | 1528 | **0.63** |

**The two cells that misbehaved are the two most dispersed voting cells**, CV
0.50 and 0.63 against a voting-cell median of 0.30. `design-cache`/sonnet
disperses 1528 tokens on a 2423 median, so a 1452-token effect sits inside one
standard deviation of that cell's own noise: it cannot resolve what is being
measured.

**The 1200-token floor gates on level and should gate on dispersion.** That is
`instrument-notes.md`'s complaint about `design-search` in sharper form, and the
same class of defect as [#51].

It is not applied here, for three reasons. Swapping the criterion mid-round is
still choosing after the fact even with a principled story attached, and the
story arrived after seeing which cells failed. The registered step 8b rule
already answers dispersion the right way — pooling to 25 reps a cell more than
halves `design-cache`/sonnet's standard error, so a real effect surfaces and an
absent one is exposed. And a dispersion floor would change which cells voted in
rounds 07 through 24, so it has to be validated by re-scoring the stored rounds
and publishing what moves, the way [#51] and [#94] were.

[#51]: https://github.com/JordanMPDS/laconic/issues/51
[#94]: https://github.com/JordanMPDS/laconic/issues/94

## Step 8b: survives, on the rule registered before it ran

A second independent generation at n=10, 160 runs, 0 failed, maximum one run in
flight. The decision is the pooled one registered above.

| cell | base | r24 | rep 1 | rep 2 | pooled | improved | consistency |
|---|--:|--:|--:|--:|--:|:--|--:|
| `design-alerting`/sonnet | 4364 | 2494 | 2200 | 3030 | 2539 | yes | 3/3 |
| `design-audit-log`/sonnet | 5167 | 2877 | 3550 | 3252 | 3452 | yes | 3/3 |
| `design-audit-log`/haiku | 1463 | 1415 | 1260 | 1228 | 1272 | yes | 3/3 |
| `design-cache`/sonnet | 2423 | 1916 | 2874 | 1216 | 1916 | yes | 2/3 |
| `design-rate-limit`/sonnet | 3440 | 1988 | 1471 | 1839 | 1893 | yes | 3/3 |
| **`design-realtime`/sonnet** | 1716 | 2190 | 1876 | 1507 | 1887 | **NO** | 1/3 |
| `design-retry`/sonnet | 4421 | 1604 | 1838 | 2411 | 1842 | yes | 3/3 |
| `design-search`/sonnet | 2013 | 1239 | 1224 | 1425 | 1378 | yes | 3/3 |
| `design-upload`/sonnet | 3609 | 2278 | 1925 | 1702 | 1898 | yes | 3/3 |

**8 of 9 cells improved, sign p = 0.0391, median shift 1547** against the 895
floor, on 25 reps a cell. The registered rule was 8 of 9 or better at p ≤ 0.05
with a shift past 895. It clears all three.

Disclosed consistency: **7 of 9 cells improved in all three independent
generations**, one in two, one in one, none in zero.

Both cells named in advance resolved, in opposite directions. `design-cache`/
sonnet — the CV 0.63 cell — pooled to an improvement, reading 1916, 2874, 1216
across the three draws, which is what a real effect inside a noisy cell looks
like; **pooling was the right answer to dispersion, not exclusion.**
**`design-realtime`/sonnet fails pooled**, improving in one generation of three,
and it stands as a named limit of this edit rather than a screened-out cell.

Reading rate across baseline and the three generations: 65%, 72%, 65%, 62%.
**Flat.** The retraction above stands.

## Step 9: the holdout is level

Both arms generated on the reserved set, **interleaved one rep at a time**
between two trees, all six holdout cases, both models, n=10. 240 generations
and 240 judge calls, **0 failed, 0 infrastructure failures**, maximum one run in
flight. `round-15-holdout-master.json` was deliberately *not* reused as the
control: it is from 2026-08-11 and twelve CLI releases back, and this session
retired stale controls twice.

Per the loop's rule, directions and significance only.

| holdout case | direction | p |
|---|---|--:|
| `holdout-design` | better | 1.0000 |
| `holdout-verdict` | better | 1.0000 |
| `holdout-ordered` | level | 1.0000 |
| `holdout-short` | level | 1.0000 |
| `holdout-destructive` | worse | 1.0000 |
| `holdout-explain` | worse | 1.0000 |

**Round-wide: level, Fisher p = 1.0000.** Every case differs by at most one
verdict.

The uniform 1.0000 was checked before being reported, because a judging pass
that failed to discriminate produces exactly that pattern. It discriminated:
both arms returned substantial failure counts on a 120-run side, in the same
range round 15's holdout produced. This is a tie, not an artefact.

**`holdout-design` is the case that killed round 15**, and it comes back
better. The bare licence made ungrounded design answers worse on unseen cases;
the earned clause is the only difference between the two rules texts.

**The limit, stated rather than left implicit.** At 120 runs a side against a
28% control failure rate, the smallest regression this run could have detected
is a rise of 16 failures, 48% relative. Round 15's regression exceeded that and
cleared alpha comfortably. **This rules out a round-15-sized harm. It does not
rule out a modest one**, and "no detectable regression" is not "no harm".

## What this edit earns, stated no more strongly than the evidence

`rules_cksum` 3694954268 **compresses grounded design answers by roughly 45%
without the reading collapse the bare licence causes** — the bare licence drops
reading to 23% at Fisher p = 0.0038, this holds at baseline — at no measurable
quality cost on the dev set or the holdout.

It does **not** improve investigation. That claim was made from round 24 and is
retracted. `design-realtime`/sonnet is a cell where it does not work.

**The first edit in 24 rounds to clear every gate the loop has.** Steps 7, 8,
8b and 9. It is proposed, not merged.
