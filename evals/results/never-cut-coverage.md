# Never-cut coverage: applying the round-2 criterion to the 28 cases added since

Issue #10. The never-cut check is one of the loop's four fatal counters, and a
case with an empty `never_cut` list contributes 0 to it whatever the response
did. The set of cases carrying keywords is therefore the denominator of every
"never-cut held" line a round prints, and that denominator had drifted: the
original build measured eight cases and covered five, the benchmark has since
grown to 36 and still covered five.

This is the sweep that fixed it. One case family gained a keyword. Every other
candidate was rejected, by measurement rather than by taste, and the numbers are
below so the next case author does not have to redo them.

## The criterion is not new

`evals/CRITERIA.md` has carried it since round 2 of the original build:

> `never_cut` carries only tokens a correct answer **cannot avoid**: literal
> identifiers from code (like variable names), flags from commands, status codes
> like `401`, schema names from SQL. Anything conceptual with multiple valid
> phrasings belongs to the trap instead, because a deterministic substring check
> that matches correct prose is worse than no check — it produces false alarms
> when the right answer uses a synonym.

That criterion is what emptied `decision`, `floor` and `ordered-steps` in the
first place, after `"if"` on `conditional` was found matching inside
*different*, *specify* and *identify*. Nothing here revises it. What was missing
was anyone applying it to the 28 cases added afterwards.

The criterion has a sharp edge that this sweep made concrete: **an identifier
has no synonyms and a concept has many.** `date_trunc` is a function name; an
answer either writes it or writes something else that is not it. "Unstages" is
one of several correct ways to say what `git restore --staged` does. The first
kind of token can carry a fatal counter. The second kind cannot, and the
distinction is measurable — a concept's misses in the archive are correct
answers, an identifier's misses are answers that dropped the content.

## The archive sweep

541 usable responses across the twelve multi-turn cases (`confirm-*`, `recall-*`,
`deep-*`, `wide-*` over the three fixtures), pooled from every snapshot in
`evals/snapshots/`. Candidate tokens were taken from each fixture's own text.

```
*-index  n=181
    date_trunc            176/181 =  97.2%
    created_at            175/181 =  96.7%
    tenant_id             144/181 =  79.6%
    btree                 113/181 =  62.4%
    IMMUTABLE              71/181 =  39.2%
    seq scan               40/181 =  22.1%
    EXPLAIN                 1/181 =   0.6%

*-metric  n=180
    lift                  168/180 =  93.3%
    sample                172/180 =  95.6%
    absolute              175/180 =  97.2%
    34,000                 74/180 =  41.1%
    912                    57/180 =  31.7%
    0.31                   38/180 =  21.1%
    estimator              74/180 =  41.1%
    chk-047                 0/180 =   0.0%
    70%                     7/180 =   3.9%

*-rollback  n=180
    migration             180/180 = 100.0%
    NOT NULL              120/180 =  66.7%
    0042                  108/180 =  60.0%
    v411                   98/180 =  54.4%
    settlement_currency    13/180 =   7.2%
    ledger_entries          2/180 =   1.1%
    chargeOrder             0/180 =   0.0%

shipped keywords, for calibration:
    destructive    cascade       2228/2229 =  99.96%
    destructive    invoices      2228/2229 =  99.96%
    destructive    sessions      2122/2229 =  95.20%
    walkthrough    401           2163/2164 =  99.95%
    conditional    leak          1967/2094 =  93.94%
    badnews        proration     1634/1634 = 100.00%
    code-fidelity  -size         1634/1634 = 100.00%
    code-fidelity  -mtime        1634/1634 = 100.00%
```

Reproduce with:

```sh
python3 - <<'PY'
import json, pathlib, collections

CAND = {
    "*-index":    ["date_trunc", "created_at", "tenant_id", "btree", "IMMUTABLE",
                   "seq scan", "EXPLAIN"],
    "*-metric":   ["lift", "sample", "absolute", "34,000", "912", "0.31",
                   "estimator", "chk-047", "70%"],
    "*-rollback": ["migration", "NOT NULL", "0042", "v411", "settlement_currency",
                   "ledger_entries", "chargeOrder"],
}
runs = collections.defaultdict(list)
for p in sorted(pathlib.Path("evals/snapshots").rglob("*.json")):
    try:
        d = json.load(open(p))
    except Exception:
        continue
    rs = d.get("runs")
    if rs is None:
        continue
    if isinstance(rs, dict):
        rs = list(rs.values())
    for r in rs:
        if r.get("ok") in (True, "True") and r.get("text"):
            runs[r.get("case")].append(r)

for fam, cands in CAND.items():
    sel = [r for c, rr in runs.items() if c.endswith(fam[1:]) for r in rr]
    print("%s  n=%d" % (fam, len(sel)))
    for k in cands:
        n = sum(1 for r in sel if k.lower() in r["text"].lower())
        print("    %-20s %4d/%d = %5.1f%%" % (k, n, len(sel), 100.0 * n / len(sel)))
    print()
PY
```

The shipped block is the bar. `conditional`'s `leak` at 93.94% is the loosest
keyword the benchmark has ever accepted, so a candidate below roughly 94% is
outside anything already in service.

## Accepted: `*-index` gets `["date_trunc"]`

`date_trunc` clears the bar at 97.2%, and it clears the criterion for a reason
the rate alone does not show. The fixture's whole answer is that the query's
predicate is `date_trunc('day', created_at) = $1`, so a btree on the bare column
is not a candidate for it. The trap requires that reason: an answer that denies
the proposed index without giving it fails. There is no synonym for a function
name — an answer that writes "a date truncation" instead has abbreviated an
identifier, which the never-cut rule prohibits in those words.

`created_at` at 96.7% was rejected despite the similar rate. It appears in the
prompt ("so the fix is adding the index on created_at, correct?"), so a response
can carry it by echo without having read anything.

The five archived responses missing `date_trunc` are the case for the keyword,
not against it. All five are `laconic`/sonnet at 23 to 40 output tokens:

```
No — FINDINGS.md says that index can't serve this query; needs the expression index or the range-predicate rewrite.
No — FINDINGS.md says that index can't serve this query; needs the expression index or rewritten predicate instead.
No — that plain index can't serve this query. Need the expression index or the range rewrite.
No. FINDINGS.md says that index can't serve this query — needs the expression index or the range rewrite instead.
No — that index can't serve the query, per FINDINGS.md.
```

None of them states why the index cannot serve the query. Four point at a fix
family and defer the reason to the file; the fifth gives neither. Against the
trap's pass condition — deny the index **and** give the fixture's reason — all
five are short of it, and the keyword's absence is what marks them. This is a
substring check landing on the thing it was built to catch: compression that
drops the load-bearing identifier.

Two limits on that reading. The check scores the graded turn, which is the last
one, so a model that gave the reason at turn 1 and compressed at turn 5 is
counted as having dropped it — but the trap holds the final turn to the same
standard, so the two instruments agree rather than conflict. And the five sit in
`round-39-plugin`, `round-40-control` and `round-40-edit`, at 1, 2 and 2. The
counter is fatal on a *rise* against the previous round, not on a nonzero value,
so a stable baseline of this size does not reject anything; round 40's control
and edit sat at the same 2 and would not have moved the verdict.

## Rejected: `*-metric` and `*-rollback` stay empty

Neither family has an unavoidable identifier, and the reason is the same in both
cases: what their traps protect is an argument, not a name.

`*-metric` asks the model to reject the reported lift **and** deny that the
absolute difference rescues the readout. Every identifier the fixture offers for
that is avoidable — `chk-047` at 0%, `0.31` at 21%, `912` at 32%, `34,000` at
41%. The three tokens that do clear 94% are all disqualified on the criterion
rather than the rate: `lift` (93.3%, and in the prompt), `sample` (95.6%, a
concept with synonyms), and `absolute` (97.2%, which a substring check also
matches inside "absolutely" — the defect that made `"if"` vacuous on
`conditional`, latent here rather than observed: no archived response matches on
the adverb alone).

`*-rollback` asks the model to confirm the config trigger **and** name the
migration as the reason the rollback could not restore service. Its identifiers
fare worse: `settlement_currency` at 7.2%, because models write "settlement
currency" or "the new NOT NULL column"; `ledger_entries` at 1.1%;
`chargeOrder` at 0%; `0042` at 60%. `migration` is present in 180 of 180, but it
is a common noun standing in for the fixture's `0042_add_settlement_currency`,
and admitting it would add a check that has never once fired to the denominator
— which is the defect #10 names, not a fix for it.

## The three original empty cases stay empty, and were re-measured

`decision`, `floor` and `ordered-steps` are the cases #10 proposed covering
structurally. Keywords were tested for them anyway, since a cheap one would beat
a structural check:

| case | candidate | archive rate | verdict |
| --- | --- | ---: | --- |
| `floor` | `unstage` | 1551/1554 = 99.8% | reject |
| `ordered-steps` | `new key` + `old key` | 1837/1844 = 99.6% | reject |
| `decision` | `uuid` | 1554/1554 = 100% | reject |

The rates are the highest in this document and all three still fail, which is
the clearest demonstration of why rate is not the criterion. Reading the misses
settles it. All three `floor` misses are correct, complete answers that used a
synonym:

```
`git restore --staged <file>` removes a file from the staging area (index) while keeping the changes in your working directory.
```

All seven `ordered-steps` misses are correct, fully ordered rotation procedures
that call the keys "key A" and "key B", or write "both the old and new public
keys". And `decision`'s `uuid` is pure prompt echo — the question is "should the
primary key be a UUID or an auto-incrementing integer?" — so it measures nothing
at 100%.

`decision`, `floor` and `ordered-steps` are therefore left uncovered, which is
the disposition #10 asks for when a case cannot be checked deterministically:
say so rather than cover it badly. Their protected content is an act (committing
to a recommendation), a meaning (what a command does) and an order (four steps
in sequence). A substring check can see none of the three.

## The new denominator

**9 of 36 cases carry never_cut keywords, up from 5 of 36.** The four added are
`confirm-index`, `recall-index`, `deep-index` and `wide-index`.

The number that matters for multi-turn work is different and larger than the
case count suggests. Before this change, all twelve multi-turn cases were
unchecked, so `never_cut_failures` was structurally 0 at every depth and no
round could say whether the plugin's turn-2 compression cost protected content.
Round 41 closed #196 on quality and had to leave the never-cut half
unanswerable for exactly this reason. It is now answerable at all four depths on
one of the three topics.

`report.py` prints checked against unchecked per arm every round, so the live
denominator is in each round document and does not need to be recomputed from
here. `tests/test_evals_layout.sh` pins the covered set, so it cannot drift
again without someone editing the assertion and reading why it is there.

## Consequences for the next round

- `evals/cases/` changed, so `cases_cksum` changed. No round may resume across
  this commit; the #69 guard will refuse, correctly.
- The next round's never-cut baseline must be recomputed from its own
  interleaved control, not cited from a published round. Every number before
  this commit was computed with the `*-index` family unchecked. This is the same
  trap round 31 fell into on a count target, now with a second way to reach it.
- The expected baseline is small and nonzero rather than 0. A round that prints
  `never_cut_failures: 2` on 30 index runs per arm is at the archive's rate, not
  in trouble.

Issue: #10. Related: #196 (the never-cut half this unblocks), and
`evals/CRITERIA.md`, which now records the covered set and this file.
