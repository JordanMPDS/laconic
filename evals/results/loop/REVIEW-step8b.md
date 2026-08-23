<!-- Third-party adversarial review of round 24 step 8b, 2026-08-23.
Produced by DeepSeek v4-pro through `delegate`, in a separate worktree with no
access to this session's reasoning. Committed verbatim as received; two of its
supporting figures were recomputed and are corrected in round-24.md's Re-score
section. Its central finding reproduces exactly. -->

# Adversarial review of round 24, step 8b

**Verdict: SUPPORTED WITH CAVEATS.**

Every number in the step 8b result reproduces exactly from the snapshots, the
registration provably preceded the generation it governs, and the 1200-token
floor is `report.py`'s own rule rather than a scope chosen for this round. The
edit does compress design answers, and the evidence for that is stronger than
the sign test the round leans on.

What is **not** supported is the weight the reported figures carry. `p = 0.0391`
is a third look at one edit and is not the procedure's error rate. The nine
"independent" cells are nine measurements of one mechanism against a *single,
unreplicated, CLI-mismatched* baseline draw. And the specific claims "8 of 9",
"`design-realtime`/sonnet is a cell where it does not work", and "median shift
1547" are properties of that one baseline draw, not of the edit: substituting an
independent draw of the **identical baseline rules text** turns the same pooled
treatment data into 8 of 8 at p = 0.0078 with a median shift of 1089, which
`report.py`'s own floor would **reject**.

One figure in the round doc does not reproduce: step 8's median shift of 1618.
See the last section.

---

## How the numbers below were produced

`python3` is blocked by this session's permission settings, so nothing here was
computed with the standard library. Everything was extracted from the committed
JSON with shell text utilities and the arithmetic done by hand and shown inline,
so each figure can be re-checked independently.

The snapshots are `json.dumps(indent=2, sort_keys=True)`, so each run record
carries its keys at a fixed six-space indent in alphabetical order (`arm`,
`case`, `model`, `num_turns`, `ok`, `output_tokens`, `rep`). That makes a
`grep`/`paste` reassembly exact. The extractor used throughout is:

```sh
# One line per run: arm|case|model|ok|output_tokens|rep
grep -hE '^      "(arm|case|model|ok|output_tokens|rep)": ' <FILES> \
  | paste - - - - - - | tr -d ' "' | tr '\t' '|'
```

Verified against the record counts, which are exact:

```sh
grep -cE '^      "(arm|case|model|ok|output_tokens|rep)": ' \
  evals/snapshots/loop/round-21.json \
  evals/snapshots/loop/round-24.json \
  evals/snapshots/loop/round-24-replication.json \
  evals/snapshots/loop/round-24-replication-2.json
# round-21.json:6600                  -> 1100 runs (22 cases x 5 arms x 2 models x 5 reps)
# round-24.json:6600                  -> 1100 runs
# round-24-replication.json:960       ->  160 runs (8 cases x 1 arm x 2 models x 10 reps)
# round-24-replication-2.json:960     ->  160 runs
```

Per-cell token lists are then taken with, for example:

```sh
grep -hE '^      "(arm|case|model|ok|output_tokens|rep)": ' \
    evals/snapshots/loop/round-24.json \
    evals/snapshots/loop/round-24-replication.json \
    evals/snapshots/loop/round-24-replication-2.json \
  | paste - - - - - - | tr -d ' "' | tr '\t' '|' \
  | grep '^arm:laconic,|case:design-cache,|model:sonnet,|ok:true,' \
  | cut -d'|' -f5 | cut -d: -f2 | tr -d ',' | sort -n | tr '\n' ' '
# 853 872 913 942 1054 1079 1128 1143 1144 1289 1506 1640 1916 2388 2568
# 2659 2744 2852 2897 2933 2979 3064 3147 3402 4190
```

`statistics.median` on an odd count is the middle element and on an even count
is the mean of the two middle elements; `"%.0f"` formatting in Python rounds
half to even. Both behaviours are needed to match the round doc's table and both
are used below.

---

## 1. Multiplicity

**This is the third scored look at one edit, and the reported `p = 0.0391` is
not the error rate of the procedure that produced it.**

The three looks are the same edit's `rules_cksum` 3694954268 measured three
times:

| look | snapshot | generated | result |
|---|---|---|---|
| step 7 | `round-24.json` | 2026-08-23T04:49:28Z | 8 of 9, p = 0.0391 — pass |
| step 8 | `round-24-replication.json` | 2026-08-23T14:03:48Z | 7 of 9, p = 0.1797 — fail |
| step 8b | all three pooled | 2026-08-23T15:31:29Z | 8 of 9, p = 0.0391 — pass |

```sh
grep -hE '^    "(generated_at|git_commit|rules_cksum)"' \
  evals/snapshots/loop/round-24.json \
  evals/snapshots/loop/round-24-replication.json \
  evals/snapshots/loop/round-24-replication-2.json
```

### The operating alpha per look is 0.0195, not 0.0391

`metrics.sign_test` is two-sided, but the gate at `report.py:883` also requires
`improved * 2 > len(cells)`. With nine cells, a pass therefore needs k ∈ {8, 9}
only. The per-look false-positive rate is the upper tail alone:

```
P(k >= 8 | H0) = (C(9,8) + C(9,9)) / 2^9 = (9 + 1) / 512 = 10/512 = 0.01953
```

The reported 0.0391 is exactly twice that, because the two-sided test doubles a
tail the procedure can never accept on.

### The inflation

Under H0 with three independent looks:

```
1 - (1 - 0.01953)^3 = 1 - 0.98047^3 = 1 - 0.94254 = 0.0575
```

The three looks are **not** independent — the pooled look contains the other
two's data, and all three share one baseline — so 0.0575 is an upper bound. The
honest statement of the operative family is narrower: step 7 was the entry
condition, and the confirmation stage then had **two** chances to declare
success (step 8 alone, or the pool). A Bonferroni bound over those two chances:

```
two-sided scale: 2 x 0.0391 = 0.0782   -> above alpha
one-sided scale: 2 x 0.0195 = 0.0391   -> exactly at alpha, no margin
```

So the corrected figure is either above alpha or precisely on it, depending on
which scale you use. Neither is 0.0391-with-room-to-spare.

### Pre-registration does not fix this, and the round doc says it does

Round doc lines 179-181:

> It is registered here, before generating, so it cannot become a retry.

The registration is genuine — I checked it, see question 5 — but it addresses
the wrong failure. Pre-registration protects against **outcome-dependent choice
of analysis**. It does not protect against **having taken an extra look**. Both
corrections are needed and only the first was applied.

The loop's own procedure says so. `SKILL.md:455-459`, step 8, in full:

> An accepted edit gets **one** more independent generation of the affected
> cases, into a fresh snapshot, and the effect has to survive it.

It did not survive it. `SKILL.md:386-388` names the failure mode by name:

> Arbitration is a replication, not a retry. Run it once, on the cells the
> comparison named, and publish the result whichever way it goes. **Regenerating
> until a round clears is the failure mode this whole gate exists to prevent.**

That paragraph governs fatal-count arbitration rather than the token target, so
step 8b does not violate a rule that literally binds it. But the round doc
invokes that same rule as its authority ("multiplicity is exactly the failure
the arbitration rule names"), and the rule it invokes says run it once.

### The wider family the loop itself discloses

`evals/results/loop/LEDGER.md:5-8`:

> Twenty attempts scored at p < 0.05 produce one winner from noise alone, so the
> attempt count has to be visible next to any claim the loop produces.

```sh
grep -nE '^\|' evals/results/loop/LEDGER.md | cut -c1-150 | tail -30
# rows for rounds 01, 03-12, 14-20, 22, 23, 24 -> 21 logged attempts
```

Round 24's own summary line is "**The first edit in 24 rounds to clear every
gate the loop has.**" By the ledger's own arithmetic, the first winner in
21 logged attempts at nominal p < 0.05 is what pure noise produces. The design
-question licence alone accounts for seven of those attempts (rounds 10, 11, 12,
14, 15, 20, 24).

**Answer: no, 0.0391 is not a fair number to report.** The defensible figures are
0.0195 as the per-look operating alpha, and 0.039-0.078 after correcting for the
two confirmation chances — with a further, unquantified discount for the 21
logged attempts the ledger says must be visible beside any claim.

---

## 2. Pooling validity

Pooling per-cell medians to 25 reps and comparing against a 5-rep baseline is
**not unsound, but it buys far less than the round doc claims, and what it buys
is on the wrong side of the comparison.**

### What is fine

The sign test's null of 0.5 per cell survives the asymmetry. For a continuous
distribution and **odd** n, `P(sample median < population median) = 0.5` exactly,
because the sample median falls below the population median precisely when more
than half the draws do, and `P(Bin(n, 0.5) > n/2) = 0.5` for odd n. Both sides
here are odd (5 and 25), so neither median is systematically biased relative to
the other, and skew in the token distribution does not push the null away from
0.5 to first order. The asymmetry does not manufacture improvements.

### What is not fine

The round doc justifies pooling at lines 243-244:

> pooling to 25 reps a cell **more than halves** `design-cache`/sonnet's standard
> error, so a real effect surfaces and an absent one is exposed.

That is true of the **treatment median in isolation** and false of the
**comparison**, which is what the gate reads. The baseline stays at n = 5, so
its error is untouched and becomes the dominant term.

Using the large-sample approximation SE(median) ≈ 1.2533·σ/√n:

```
design-cache/sonnet baseline (round-21, n=5): 1710 2025 2423 3688 5436
  mean = 15282/5 = 3056.4
  devs  = -1346.4, -1031.4, -633.4, +631.6, +2379.6
  SS    = 1812793 + 1063785 + 401196 + 398919 + 5662496 = 9339188
  s^2   = 9339188/4 = 2334797     s = 1528.0   (round doc: 1528)
  SE_base = 1.2533 * 1528.0 / sqrt(5) = 856

design-cache/sonnet treatment, pooled 25 reps (values listed above):
  mean = 51302/25 = 2052.1
  s ~= 1015   (two clusters: 12 values about 1139, 13 values about 2895)
  SE_treat(n=25) = 1.2533 * 1015 / 5      = 254
  SE_treat(n=5)  = 1.2533 * 1015 / sqrt(5) = 569

comparison SE, treatment at n=5 : sqrt(856^2 + 569^2) = sqrt(1056497) = 1028
comparison SE, treatment at n=25: sqrt(856^2 + 254^2) = sqrt( 797252) =  893
```

**Pooling 5 reps to 25 cut the comparison's standard error by 13%, not by more
than half.** The observed difference on that cell is 2423 − 1916 = **507**, which
is 0.57 of the 893-token comparison SE. The round doc's stated reason for
pooling does not hold, and the cell it was invoked to rescue is still inside the
noise after pooling.

(The 1.2533 factor assumes normality and these distributions are bimodal, so
treat those SEs as indicative. The rank test below does not assume normality and
agrees.)

### What the asymmetry does to the median shift

The shift is `median(9 baseline medians) − median(9 pooled medians)`
(`report.py:873-874`). Its baseline term is a median of nine 5-rep medians, so
its own sampling error is smaller than any single cell's — that part is fine.

But it is gated against a floor built from the baseline's **per-response**
stdevs (`report.py:853-870`), which is a different quantity from the sampling
error of a median-of-medians. The mismatch is the tool's own design and here it
happens to be conservative. It is not, however, a calibrated test: nothing about
895 tells you the probability of a 1547 shift under H0.

### The distribution-free per-cell picture

Because the medians hide how strong each cell actually is, here is a
Mann-Whitney U for each voting cell — every (pooled, baseline) pair in which the
pooled value is lower, out of 25 × 5 = 125 pairs. Under H0, E[U] = 62.5 and
sd(U) = √(25·5·31/12) = 17.97. No baseline value ties a pooled value in any
cell, so no tie correction applies. Two-sided normal approximation:

| cell | U / 125 | z | approx p |
|---|--:|--:|--:|
| `design-search`/sonnet | 123 | 3.37 | 0.0008 |
| `design-alerting`/sonnet | 122 | 3.31 | 0.0009 |
| `design-audit-log`/sonnet | 116 | 2.98 | 0.003 |
| `design-rate-limit`/sonnet | 115 | 2.92 | 0.004 |
| `design-upload`/sonnet | 114 | 2.87 | 0.004 |
| `design-retry`/sonnet | 113 | 2.81 | 0.005 |
| **`design-cache`/sonnet** | **88** | **1.42** | **0.16** |
| **`design-audit-log`/haiku** | **77** | **0.81** | **0.42** |
| `design-realtime`/sonnet | 58 | −0.25 | 0.80 |

Worked example, `design-cache`/sonnet — count of pooled values below each of the
five baseline values 1710, 2025, 2423, 3688, 5436:

```
< 1710 : 853 872 913 942 1054 1079 1128 1143 1144 1289 1506 1640          = 12
< 2025 : + 1916                                                          = 13
< 2423 : + 2388                                                          = 14
< 3688 : + 2568 2659 2744 2852 2897 2933 2979 3064 3147 3402             = 24
< 5436 : + 4190                                                          = 25
U = 12 + 13 + 14 + 24 + 25 = 88
z = (88 - 62.5) / 17.97 = 1.42
```

**Six of the nine cells are individually significant at p < 0.01. Two of the
"improved" votes come from cells that are individually indistinguishable from
noise.** That is the honest summary of the pooled evidence, and it is a stronger
statement about the edit than 8-of-9 is — while simultaneously showing that
8-of-9 is the wrong statistic to have quoted.

---

## 3. The sign test

**The nine cells are not independent, and the sign test's n = 9 overstates the
information in the data by a wide margin.**

The nine cells are eight `design-*` cases on sonnet plus `design-audit-log` on
haiku. They share:

1. **One baseline batch.** All nine comparisons use the laconic arm of
   `round-21.json`, generated 2026-08-21 in a single pass. Any batch-level shift
   moves all nine votes together. This is not hypothetical — see question 6.
2. **One CLI on each side, and they differ.**

   ```sh
   grep -hE '^      "(arm|claude_cli_version)": ' evals/snapshots/loop/round-21.json \
     | paste - - | tr -d ' "' | tr '\t' '|' | sort | uniq -c
   #  220 arm:laconic,|claude_cli_version:2.1.239(ClaudeCode),
   grep -hE '^      "(arm|claude_cli_version)": ' evals/snapshots/loop/round-24.json \
     | paste - - | tr -d ' "' | tr '\t' '|' | sort | uniq -c
   #  220 arm:laconic,|claude_cli_version:2.1.240(ClaudeCode),
   grep -h '"claude_cli_version"' evals/snapshots/loop/round-24-replication.json \
     | sort | uniq -c    # 160 at 2.1.240
   grep -h '"claude_cli_version"' evals/snapshots/loop/round-24-replication-2.json \
     | sort | uniq -c    # 160 at 2.1.240
   ```

   Baseline is CLI 2.1.239; all three treatment generations are 2.1.240. Nothing
   is interleaved. The CLI difference is common to all nine cells.
3. **One rules text and one mechanism.** The edit is a single clause in the
   `Level: full` design-question licence. Whatever it does, it does to every
   design answer at once. Eight of the nine cells are the same model answering
   the same family of prompt under the same clause.

### The effective n

The sign test's n counts independent Bernoulli trials of the *comparison*. The
design supplies:

- **one** independent baseline generation, and
- **three** treatment generations, all on one CLI within eleven hours.

The number of independent replicates of the comparison is therefore **one**. A
generous bound that treats the two models as independent strata gives n = 2, at
which the best attainable result is 2 of 2 and `sign_test(2, 2) = 2/4 = 0.5`.

I can bound the treatment-side clustering empirically. Per cell, the ratio of
each generation's median to the pooled median, then averaged across the nine
cells:

```
r24  mean ratio = 9.108/9 = 1.012
rep1 mean ratio = 9.056/9 = 1.006
rep2 mean ratio = 8.745/9 = 0.972
```

That is a ±4% common-mode component on the treatment side, against per-cell
ratios spanning 0.635 to 1.500. **So the treatment side is well behaved** — the
three generations are genuinely three samples of one stable quantity, and I will
not overstate the clustering there.

The clustering that matters is on the baseline side, and it cannot be estimated
from this design at all, because there is exactly one baseline batch. Question 6
estimates it from a snapshot outside this round, and it is large.

**Answer: the nine cells are not independent. The effective number of
independent comparisons is one (the single baseline batch), at best two if the
two models are treated as separate strata. `sign_test(2, 2) = 0.5`.** The
9-cell figure is a lower bound on the p-value, not an estimate of it.

---

## 4. Cell selection

**The 1200-token floor is the tool's own rule and predates this round by twelve
days. It also, on its own, converts a failure into a pass.**

### It is the tool's rule

`report.py:179`:

```python
TOKEN_CELL_MIN_BASELINE = 1200
```

Applied at `report.py:837-844`, inside the scoped-`output_tokens` branch, and
all-or-nothing: cells are dropped only if at least six survive, otherwise none
are dropped and the verdict says so.

```sh
git log --format='%h %ad %s' --date=short -S TOKEN_CELL_MIN_BASELINE -- evals/bench/report.py
# f8440e5 2026-08-11 Carry the carried arms' verdicts (#83), and stop the short
#                    cells voting in the token target (#85)
```

Introduced 2026-08-11, twelve days before round 24, in a commit about an
unrelated issue. **The round doc's claim at line 126 — "which is the gate's own
rule and not a scope chosen after the fact" — is correct.**

Which cells it drops, from the round-21 baseline medians (all 16 design cells,
laconic arm, n = 5, median = 3rd of 5 sorted):

| cell | baseline median | votes? |
|---|--:|---|
| `design-alerting`/haiku | 1070 | no |
| `design-cache`/haiku | 697 | no |
| `design-rate-limit`/haiku | 683 | no |
| `design-realtime`/haiku | 502 | no |
| `design-retry`/haiku | 655 | no |
| `design-search`/haiku | 528 | no |
| `design-upload`/haiku | 691 | no |
| `design-audit-log`/haiku | 1463 | **yes** |
| the eight sonnet cells | 1716 – 5167 | yes |

Seven dropped, nine remain, 9 ≥ 6 so the drop fires. Exactly as `report.py`
specifies.

### It helps the reported result, decisively

The seven excluded haiku cells, baseline against pooled (13th of 25):

```sh
# pooled median for each excluded haiku cell
... | grep '^arm:laconic,|case:design-alerting,|model:haiku,|ok:true,' \
    | cut -d'|' -f5 | cut -d: -f2 | tr -d ',' | sort -n | head -n 13 | tail -n 1
```

| cell | baseline | pooled | improved? |
|---|--:|--:|---|
| `design-alerting`/haiku | 1070 | 899 | yes |
| `design-cache`/haiku | 697 | 684 | yes (by 13 tokens) |
| `design-upload`/haiku | 691 | 690 | yes (by 1 token) |
| `design-rate-limit`/haiku | 683 | 752 | no |
| `design-realtime`/haiku | 502 | 676 | no |
| `design-retry`/haiku | 655 | 711 | no |
| `design-search`/haiku | 528 | 633 | no |

Had all sixteen cells voted, the result would be **11 of 16**:

```
sign_test(11, 16): min(11, 5) = 5
  tail = C(16,0)+C(16,1)+C(16,2)+C(16,3)+C(16,4)+C(16,5)
       = 1 + 16 + 120 + 560 + 1820 + 4368 = 6885
  p = 2 * 6885 / 65536 = 13770/65536 = 0.2101
```

**p = 0.21 — a clear fail. The floor is the entire difference between accept and
reject.** That is defensible on the merits (two of the "improvements" it removes
are 13 tokens and 1 token, which are obviously noise), and the round doc is
entitled to it. But a reader should know that the pass is produced by an
exclusion rule and not by the scope the hypothesis named.

### The floor is applied to a 5-rep draw, so which cells vote is itself a coin flip

`design-audit-log`/haiku clears the floor by 263 tokens. Its five baseline reps:

```
561  1087  1463  1505  1892      (median 1463; two of five below 1200)
```

The median of five exceeds 1200 only if at least three of the five draws do.
Taking the cell's own rate p̂ = 3/5:

```
P(>=3 of 5 above 1200) = C(5,3)(.6)^3(.4)^2 + C(5,4)(.6)^4(.4) + (.6)^5
                       = 0.3456 + 0.2592 + 0.07776 = 0.6826
```

So there was roughly a **one-in-three chance that cell would not have voted at
all**. Had it not:

```
8 voting cells, 7 improved
sign_test(7, 8): min(7,1) = 1, tail = C(8,0)+C(8,1) = 9
  p = 2 * 9 / 256 = 0.0703      -> REJECT
```

**Answer: the exclusion is the gate's own rule, correctly applied and correctly
described. It helps the reported result — without it the round fails at
p = 0.21. And the membership of the voting set is decided by a 5-rep draw whose
plausible alternative also fails, at p = 0.070.**

(The round doc concedes the underlying defect itself at lines 235-237: "The
1200-token floor gates on level and should gate on dispersion." That concession
is right, and it applies to `design-audit-log`/haiku exactly as it applies to
`design-cache`/sonnet.)

---

## 5. Reproducing the numbers

All three headline figures reproduce exactly.

### Baseline medians (round-21, laconic arm, n = 5)

```sh
grep -hE '^      "(arm|case|model|ok|output_tokens|rep)": ' evals/snapshots/loop/round-21.json \
  | paste - - - - - - | tr -d ' "' | tr '\t' '|' \
  | grep '^arm:laconic,|case:design-' | cut -d'|' -f2,3,5 \
  | tr -d ',' | tr '|' ' ' | cut -d: -f2- | sort
```

| cell | five reps | median | round doc |
|---|---|--:|--:|
| `design-alerting`/sonnet | 3568 4151 **4364** 4403 4791 | 4364 | 4364 |
| `design-audit-log`/sonnet | 5114 5120 **5167** 5650 7200 | 5167 | 5167 |
| `design-audit-log`/haiku | 561 1087 **1463** 1505 1892 | 1463 | 1463 |
| `design-cache`/sonnet | 1710 2025 **2423** 3688 5436 | 2423 | 2423 |
| `design-rate-limit`/sonnet | 2133 2337 **3440** 4337 4892 | 3440 | 3440 |
| `design-realtime`/sonnet | 1161 1166 **1716** 1738 3248 | 1716 | 1716 |
| `design-retry`/sonnet | 2408 3039 **4421** 4981 5518 | 4421 | 4421 |
| `design-search`/sonnet | 1585 1952 **2013** 2162 2791 | 2013 | 2013 |
| `design-upload`/sonnet | 1714 2321 **3609** 3905 3940 | 3609 | 3609 |

### Per-generation and pooled medians

Per generation: median of 5 (r24) or mean of the 5th and 6th of 10 (rep1, rep2);
pooled: 13th of 25. All match, including Python's round-half-to-even in the
`%.0f` cells (marked *).

| cell | r24 | rep 1 | rep 2 | pooled | doc row |
|---|--:|--:|--:|--:|---|
| `design-alerting`/sonnet | 2494 | (2111+2289)/2 = 2200 | (2979+3080)/2 = 3029.5\* | 2539 | 2494 2200 3030 2539 |
| `design-audit-log`/sonnet | 2877 | (3492+3607)/2 = 3549.5\* | (3198+3307)/2 = 3252.5\* | 3452 | 2877 3550 3252 3452 |
| `design-audit-log`/haiku | 1415 | (1214+1305)/2 = 1259.5\* | (1227+1230)/2 = 1228.5\* | 1272 | 1415 1260 1228 1272 |
| `design-cache`/sonnet | 1916 | (2852+2897)/2 = 2874.5\* | (1143+1289)/2 = 1216 | 1916 | 1916 2874 1216 1916 |
| `design-rate-limit`/sonnet | 1988 | (1453+1489)/2 = 1471 | (1726+1952)/2 = 1839 | 1893 | 1988 1471 1839 1893 |
| `design-realtime`/sonnet | 2190 | (1865+1887)/2 = 1876 | (1333+1681)/2 = 1507 | 1887 | 2190 1876 1507 1887 |
| `design-retry`/sonnet | 1604 | (1834+1842)/2 = 1838 | (2393+2429)/2 = 2411 | 1842 | 1604 1838 2411 1842 |
| `design-search`/sonnet | 1239 | (1151+1297)/2 = 1224 | (1402+1448)/2 = 1425 | 1378 | 1239 1224 1425 1378 |
| `design-upload`/sonnet | 2278 | (1898+1952)/2 = 1925 | (1522+1883)/2 = 1702.5\* | 1898 | 2278 1925 1702 1898 |

### 8 of 9

Comparing pooled against baseline, `cur < prev` per `report.py:871`:

```
alerting     2539 < 4364  yes
audit-log/s  3452 < 5167  yes
audit-log/h  1272 < 1463  yes
cache        1916 < 2423  yes
rate-limit   1893 < 3440  yes
realtime     1887 > 1716  NO
retry        1842 < 4421  yes
search       1378 < 2013  yes
upload       1898 < 3609  yes
                          8 of 9   REPRODUCED
```

### p = 0.0391

`metrics.sign_test(8, 9)`, two-sided exact:

```
min(k, n-k) = min(8, 1) = 1
tail = C(9,0) + C(9,1) = 1 + 9 = 10
p = 2 * 10 / 2^9 = 20/512 = 0.0390625   ->  0.0391   REPRODUCED
```

### Median shift 1547

```
baseline medians sorted: 1463 1716 2013 2423 [3440] 3609 4364 4421 5167 -> 3440
pooled   medians sorted: 1272 1378 1842 1887 [1893] 1898 1916 2539 3452 -> 1893
shift = 3440 - 1893 = 1547   REPRODUCED
```

### Floor 895

`report.py:853-870` takes the median of the baseline per-cell stdevs over the
voting cells. Sample stdev (ddof = 1) of each baseline cell, computed by hand:

```
alerting/s   : mean 4255.4, SS  803865 /4 =  200966 -> s =  448.3   (doc 448)
audit-log/s  : mean 5650.2, SS 3203985 /4 =  800996 -> s =  895.0   (doc 895)
audit-log/h  : mean 1301.6, SS 1010535 /4 =  252634 -> s =  502.6   (doc 503)
cache/s      : mean 3056.4, SS 9339188 /4 = 2334797 -> s = 1528.0   (doc 1528)
rate-limit/s : mean 3427.8, SS 5837027 /4 = 1459257 -> s = 1208.0   (doc 1208)
realtime/s   : mean 1805.8, SS 2917713 /4 =  729428 -> s =  854.1   (doc 854)
retry/s      : mean 4073.4, SS 6874972 /4 = 1718743 -> s = 1311.0   (doc 1311)
search/s     : mean 2100.6, SS  776021 /4 =  194005 -> s =  440.5   (doc 440)
upload/s     : mean 3097.8, SS 4140519 /4 = 1035130 -> s = 1017.4   (doc 1017)

sorted: 440.5 448.3 502.6 854.1 [895.0] 1017.4 1208.0 1311.0 1528.0
median  = 895.0   REPRODUCED    (1547 > 895, floor cleared)
```

### The other step 8b claims

**Consistency, "7 of 9 in all three, one in two, one in one"** — from the
per-generation table above, each generation's median against the baseline:

```
alerting   y y y = 3/3      rate-limit y y y = 3/3
audit-log/s y y y = 3/3     realtime   n n y = 1/3
audit-log/h y y y = 3/3     retry      y y y = 3/3
cache      y n y = 2/3      search     y y y = 3/3
                            upload     y y y = 3/3
-> seven at 3/3, one at 2/3, one at 1/3, none at 0/3   REPRODUCED
```

**Reading rate "65%, 72%, 65%, 62%"** — one-turn runs over sonnet design cells:

```sh
grep -hE '^      "(arm|case|model|num_turns|ok|output_tokens|rep)": ' <FILE> \
  | paste - - - - - - - | tr -d ' "' | tr '\t' '|' \
  | grep '^arm:laconic,|case:design-' | grep '|model:sonnet,' | grep -c '|num_turns:1,'
# round-21: 14 one-turn of 40  -> read 26/40 = 65.0%
# round-24: 11 one-turn of 40  -> read 29/40 = 72.5%
# rep1:     28 one-turn of 80  -> read 52/80 = 65.0%
# rep2:     30 one-turn of 80  -> read 50/80 = 62.5%
```

REPRODUCED.

### The registration really did precede the generation

```sh
git log --format='%h %ad %s' --date=iso -4
# 25133b4 2026-08-23 15:31:19 +0000  evals: round 24 results, step 8 partial,
#                                    and step 8b registered (#46)
grep -hE '^    "(generated_at|git_commit)"' evals/snapshots/loop/round-24-replication-2.json
#     "generated_at": "2026-08-23T15:31:29Z",
#     "git_commit": "25133b4",
```

The registering commit landed at 15:31:19Z; the second replication's first run
is stamped 15:31:29Z, ten seconds later, at that commit. **The claim that the
decision rule was written down before the third generation ran is true**, and
the round doc deserves credit for it.

### Two provenance checks I ran and cleared

- **`cases_cksum` differs** between the round-24 pair (2389944869) and the two
  replications (2423244529). This is *not* a case-set change: the checksum
  covers exactly the cases a snapshot spans, and the replications span 8 cases
  where round 24 spans 22. `git log -- evals/cases` shows the last change was
  2026-08-13, ten days before every generation here. No `--allow-case-change`
  stamp appears in any metadata block. Clean.
- **`rules_cksum`** is 3694954268 on all three treatment generations and
  1830906901 on the baseline. Correct.

One provenance item does not clear: `round-21.json` records
`"git_dirty": true`. The baseline snapshot was generated from an uncommitted
working tree, so its exact instrument state is not reconstructible from a
commit. Everything below rests on that one file.

---

## 6. The strongest argument against

**The nine per-cell directions, the count 8 of 9, and the shift 1547 are
properties of a single 5-rep baseline draw taken two days earlier on a different
CLI build, and that draw is demonstrably not reproducible.**

The repository contains a second, independent generation of the **identical
baseline rules text** on the **same eight design cases**:

```sh
grep -hE '^    "(generated_at|rules_cksum|cases_cksum|claude_cli_version|laconic_level)"' \
  evals/snapshots/loop/licence-vs-master-master.json
#     "cases_cksum": "2423244529",
#     "claude_cli_version": "2.1.240 (Claude Code)",
#     "generated_at": "2026-08-22T19:59:26Z",
#     "laconic_level": "full",
#     "rules_cksum": "1830906901"      <- byte-identical to round-21's baseline
```

Eight design cases, sonnet, five runs each, **on CLI 2.1.240 — the same build as
all three treatment generations**, and one day closer to them than round 21 is.
It is a strictly better-matched baseline than the one the round used.

Its per-cell medians, against round-21's:

| cell | round-21 baseline | second master draw | ratio |
|---|--:|--:|--:|
| `design-alerting`/sonnet | 4364 | 5784 | 1.33 |
| `design-audit-log`/sonnet | 5167 | 5137 | 0.99 |
| `design-cache`/sonnet | 2423 | 4202 | **1.73** |
| `design-rate-limit`/sonnet | 3440 | 2428 | 0.71 |
| `design-realtime`/sonnet | 1716 | 3369 | **1.96** |
| `design-retry`/sonnet | 4421 | 2600 | **0.59** |
| `design-search`/sonnet | 2013 | 1870 | 0.93 |
| `design-upload`/sonnet | 3609 | 2165 | **0.60** |

Two draws of the same rules text on the same cases disagree by up to a factor of
two in **both** directions. At the round level they nearly agree (median ratio
0.96), which is why the *compression* finding survives; per cell they do not
agree at all, which is why the *sign test* does not.

Now re-run step 8b's arithmetic with this baseline and the **unchanged** pooled
treatment medians. All eight cells clear the 1200 floor, so all eight vote:

```
alerting   2539 < 5784  yes      realtime  1887 < 3369  yes
audit-log  3452 < 5137  yes      retry     1842 < 2600  yes
cache      1916 < 4202  yes      search    1378 < 1870  yes
rate-limit 1893 < 2428  yes      upload    1898 < 2165  yes

8 of 8.  sign_test(8,8): tail = C(8,0) = 1, p = 2/256 = 0.0078

median shift:
  baseline sorted 1870 2165 2428 [2600 3369] 4202 5137 5784 -> (2600+3369)/2 = 2984.5
  pooled   sorted 1378 1842 1887 [1893 1898] 1916 2539 3452 -> (1893+1898)/2 = 1895.5
  shift = 2984.5 - 1895.5 = 1089.0

floor (median of the alternative baseline's per-cell stdevs, ddof=1):
  alerting  1232.0   audit-log 1588.8   cache     1786.0   rate-limit 1161.6
  realtime  1307.1   retry     1437.9   search     737.2   upload     1100.1
  sorted: 737.2 1100.1 1161.6 [1232.0 1307.1] 1437.9 1588.8 1786.0
  floor = (1232.0 + 1307.1)/2 = 1269.6

1089.0 <= 1269.6  ->  report.py:888  "REJECT: median shift is inside the
                                      scoped noise floor"
```

**Swap one 5-rep baseline draw for another equally valid one and `report.py`'s
own gate rejects the same treatment data.** Both of the gate's two estimators
change their story at once: the sign test gets *stronger* (8 of 8, p = 0.0078)
and the median shift gets *weaker* (1089 against 1547) and falls inside the
noise floor.

And the two per-cell conclusions the round doc states as findings both reverse:

> `design-realtime`/sonnet fails pooled ... it stands as a named limit of this
> edit (line 279-280)

Against the CLI-matched baseline, `design-realtime`/sonnet improves 3369 to
1887, a 44% fall. It is not a limit of the edit; it is a cell whose round-21
baseline draw came in low.

> `design-cache`/sonnet ... pooled to an improvement ... which is what a real
> effect inside a noisy cell looks like; **pooling was the right answer to
> dispersion, not exclusion** (lines 276-278)

Against the CLI-matched baseline that cell improves 4202 to 1916, a 54% fall,
with no pooling argument required. The 1916-versus-2423 knife-edge was a feature
of the baseline draw, not a demonstration that pooling works.

### Caveats on this counterfactual, stated so it is not overread

- The alternative baseline is also n = 5 and also a single draw. The claim is
  **not** that it is the right baseline and round-21's is wrong. It is that two
  equally defensible draws of the identical text give opposite verdicts from
  the same treatment data.
- It is sonnet-only, so the 8-cell scope is not the round's 9-cell scope
  (`design-audit-log`/haiku has no counterpart).
- It was generated for the licence-versus-master spike, interleaved with a
  licence arm. Interleaving should not affect an arm's own output, but I did not
  verify that, and it was not generated as a standalone baseline round.

### Why the fragility is structural, not bad luck

Even without the alternative baseline, the pass has no margin anywhere:

- **8 of 9 is the minimum that passes.** 7 of 9 is p = 0.1797. One cell flipping
  ends it.
- **The cell that decides it is `design-cache`/sonnet, at p ≈ 0.16 on its own.**
  Of its 25 pooled reps, 14 fall below the baseline median and 11 above; the
  median needs 13. A swing of two observations out of twenty-five reverses the
  round's verdict.
- **Whether `design-audit-log`/haiku votes at all is a ~2:1 coin flip**
  (question 4). If it does not, 7 of 8 is p = 0.0703 and the round fails.
- **Nothing was interleaved.** The repository's own
  `evals/results/loop/interleaved-batch.md` is cited in `SKILL.md:160-169` for
  exactly this: a control arm with no rules in it moved 4 of 40 to 11 of 40
  "with nothing changed but the calendar and the CLI", and `report.py:145-152`
  says the fix "is design, not statistics. Generating both sides of a comparison
  in one interleaved batch removes the between-batch component outright, and
  resolved a contrast at 40 runs a side that the archive could not resolve at
  any n." Step 8b is an archive comparison at 25 reps a side. The round's own
  step 9 refused to reuse a stale control for precisely this reason (round doc
  lines 290-293); step 8b did the thing step 9 refused to do.

**The single best reason not to believe this result: the baseline was never
replicated, and the one attempt in the repository to replicate it — same rules
text, same cases, better-matched CLI — disagrees with it by up to a factor of
two per cell and would have made `report.py` reject the round.** No amount of
pooling on the treatment side addresses that, because pooling reduces the error
on the side that was not the problem.

### What does survive

Stated so the review is not read as rejecting the edit:

- Six of the nine cells compress at p < 0.01 individually (question 2), and all
  eight sonnet cells compress against **both** available baselines.
- The three treatment generations agree with each other to ±4% at the round
  level (question 3).
- The round-level compression, roughly 40-45%, is the one claim that is
  insensitive to which baseline is used.

The edit compresses design answers. That conclusion is safe. "8 of 9 cells at
p = 0.0391 with a shift of 1547" is not the evidence for it, and should not be
the sentence that goes into the ledger.

---

## Figures in the round doc I could not reproduce

**One.**

### Step 8: "The median shift is 1618"

Round doc line 156: "The median shift is **1618**, larger than round 24's 1452
and past the 895 floor".

`report.py:873-874` defines the shift as the **difference of the two medians**:

```python
shift = (_median([prev["tokens"][c] for c in cells])
         - _median([cur["tokens"][c] for c in cells]))
```

Computed that way from replication 1:

```
baseline medians sorted: 1463 1716 2013 2423 [3440] 3609 4364 4421 5167 -> 3440
rep-1    medians sorted: 1224 1259.5 1471 1838 [1876] 1925 2200 2874.5 3549.5 -> 1876
shift = 3440 - 1876 = 1564          I get 1564, the doc says 1618
```

1618 is the **median of the per-cell differences**, a different estimator:

```
4364-2200   = 2164        1716-1876   = -160
5167-3549.5 = 1617.5      4421-1838   = 2583
1463-1259.5 =  203.5      2013-1224   =  789
2423-2874.5 = -451.5      3609-1925   = 1684
3440-1471   = 1969

sorted: -451.5 -160 203.5 789 [1617.5] 1684 1969 2164 2583  -> 1617.5 -> 1618
```

So step 8's figure was produced with an estimator `report.py` does not use, and
step 7's 1452 and step 8b's 1547 were produced with the one it does. Checked:

```
round 24  difference-of-medians = 3440 - 1988 = 1452  (doc 1452, matches)
          median-of-differences =               1331  (not the doc's number)
pooled    difference-of-medians = 3440 - 1893 = 1547  (doc 1547, matches)
          median-of-differences =               1547  (coincides here)
```

**Impact: contained but not zero.** The step 8b figure under review is
unaffected — both estimators give 1547 for the pool, by coincidence. The step 8
sentence "the median shift is 1618, larger than round 24's 1452" compares two
different estimators; under a consistent estimator it reads 1564 against 1452,
so the qualitative claim ("larger") survives and the number does not.

Everything else in the step 8b section — the four-column table, 8 of 9,
p = 0.0391, the shift 1547, the floor 895, the 7/9 consistency split, the seven
floor exclusions, and the reading rates 65/72/65/62 — reproduces exactly.
