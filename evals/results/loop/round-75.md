# Round 75: the grounds recitation as a bare shape, and the last live wording

**Registration. Nothing below the results line has been computed**, with the
exception of the base figures marked as computed and dated in place, which come
from the six already-committed snapshots named there — all at `rules_cksum`
**3285158247**, which is master today and this round's control arm, byte for
byte — and the power table resampled from them. This file, the edit and the
regenerated `rules/dist/*.md` are committed in one commit before any
generation, following [round 38](round-38.md) through [round 74](round-74.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_echo.py --title 'Round 75: the grounds recitation as a bare shape' \
  --control evals/snapshots/loop/round-75-control-*.json \
  --edit    evals/snapshots/loop/round-75-edit-*.json
```

`bash tools/candidate-due.sh` exits 0: [round 74](round-74.md) carried a
candidate, so round 75 is permitted to measure. It carries one anyway, because
the span round 74 named is still open and the wording that would close it costs
one round.

## Why this round exists

[Round 74](round-74.md) appended two sentences to round 73's coda and rejected
at **+4.33 words, p = 0.92172, 0 of 3 cells fell**. Its own registered verdict
names what should come next:

> **Not this edit without its second sentence, immediately.** That is the
> obvious next buy and it is one wording away from a round 73 that already
> warned against a third wording. It is also now the *only* live way to test the
> grounds span, so it should be bought — but as a round that names in advance
> what a second null would mean.

This round is that buy, with one change to the edit that came from
`tools/consult.sh` and is credited below. **It is the last wording this cluster
buys on this span**, and the closure rule is registered in the verdict section
rather than decided afterwards.

### What round 74 established, and what it did not

Round 74 put a prohibition at the position round 73 measured to work, in the
form this file's working prohibitions share, aimed at **76.7% of the words** by
[`cited-grounds-305.md`](cited-grounds-305.md)'s own sentence classification.
The median moved the wrong way on all three cells. Round 74's own reading of
why is not the result but the edit:

> The second sentence, *"Cite the grounds when they ask why, not to show that
> you looked"*, is a licence, and **every `settled-*` prompt contains the word
> *because***, which is what makes them true-premise questions.

That was registered in the pre-mortem, before any generation, and git dates it.
So round 74 cannot separate "a shape rule does not reach the grounds" from "this
edit licensed what it forbade", and the separation costs exactly one round.

## What `tools/consult.sh` said, and what this round took from it

Asked with the issue, this design, and the four things I was least sure of.
**Codex and DeepSeek did not answer** — codex timed out at 240s, DeepSeek exited
on a model-catalog error. Kimi answered, and two of its four points changed this
registration.

**Adopted: strip the rationale clause as well as the licence.** Round 74's
surviving sentence ended *"because reading it is how you know the answer and not
part of it."* Kimi:

> The rationale clause ("because reading it is how you know the answer…") invites
> the model to make its epistemic process visible. It does not command a
> recitation, but it primes the same semantic neighborhood that produces the
> recitation.

This is not the general claim that a rationale hurts — round 73's accepted coda
carries one (*"because the premise is what you are confirming"*) and moved the
target −8.33. The claim is narrower and survives that: round 73's rationale is
about the *premise*, while round 74's is about *reading*, which is the very act
whose written trace this edit is trying to suppress. The edit below drops both
sentences' worth of surplus and keeps nothing but the shape.

**Adopted: do not frame this round as a test of the licence hypothesis.** Kimi:

> If round 75 succeeds, you cannot confidently attribute it to removing the
> licence; if it fails, you can move the blame to the surviving "because"
> clause. That is a heads-you-win-tails-you-do-not-learn pattern.

Correct, and the second half of it is why the rationale goes too — with both
clauses removed there is no third thing left to blame. The hypothesis below is
therefore stated on the edit rather than on the mechanism: *the bare shape
prohibition moves the endpoint*, not *the licence was the problem*.

**Adopted as a disclosure: the grounds may be the model's own working memory.**
Kimi's sharpest point, and the one the bound does not fully reach:

> The contra bound only rules out ungrounded confirmation; it does *not* rule
> out a model that writes the grounds to stabilize its own answer.

It reaches part of it. `contra-*` is the case where the record contradicts the
prompt, which is exactly where an answer needs whatever stabilises it most, and
its deny rate is fatal here. What that cannot see is a *graded* effect on a case
the model gets right either way. Registered as a disclosure, not as a check.

**Not adopted: close the span now without buying the round.** Kimi's
recommendation rested on "two nulls on this span", and that count is wrong — it
came from a sloppy line in my own question. Round 72's null was on the **premise
echo**, the other appended span, and round 73 then moved that same span −8.33
and replicated at −8.00. The grounds span has exactly **one** null, round 74's,
and it is confounded by a licence its own pre-mortem named in advance. One
confounded null does not close a span that is three quarters of the residual.

## The residual this is aimed at

*Computed 2026-09-22 from `round-73-edit-{1,2}.json`,
`round-73-repl-edit-{1,2}.json` and `round-74-control-{1,2}.json`, pooled —
75 runs a cell, all six at `rules_cksum` 3285158247.*

| settled cell, haiku | n | median | per-cell stdev |
|---|--:|--:|--:|
| `settled-retention` | 75 | 59.0 | 16.16 |
| `settled-failover` | 75 | 83.0 | 23.85 |
| `settled-rounding` | 75 | 81.0 | 18.67 |
| **pooled** | **225** | **77.0** | — |

The complete answer on these cases is one word. Round 71 took the median from 94
to 79 with a rendered specimen; round 73 took it from 88 to 80.5 by naming where
the answer stops. **Master still answers at 77 words**, and
[`cited-grounds-305.md`](cited-grounds-305.md) measured where they go: 72.1% of
control-side words and 76.7% of round-71-edit-side words are the model citing
grounds out of the record the user has just read, against 2.3% for the verdict
itself.

The measured floor — median per-cell control-side standard deviation — is
**18.67 words**.

## The edit

`rules/laconic.md`, appended to round 73's coda inside
`## Never cut (every level, including ultra)`, above every level marker, so it
reaches `lite`, `full` and `ultra` alike:

```diff
 own sentence in your words, because the premise is what you are confirming.
+The record you checked is appended too: no "The file says ..." retelling
+what you read to be sure.
```

**19 words**, against round 74's 45. The `full` slice goes from 1,143 to 1,162
words and `rules_cksum` from **3285158247** to **2715680794**.

### The claim

The one appended span round 73's boundary sentence did not name, prohibited as a
surface shape and nothing else: a clause, a quoted three-word fragment, no
licence, no rationale, no judgement asked of the model. That is the form of the
two prohibitions in this file with measured effects — *"No closing offers and no
offers to do more work: no 'Let me know if...'"* moves `closing_offers` 13.1% to
3.5% at p = 8.6e-18, and the no-narration prohibition suppressed at p = 0.0062.
Neither carries a licence and neither explains itself.

> Editing the coda in `## Never cut` to append *"The record you checked is
> appended too: no 'The file says ...' retelling what you read to be sure"*
> should move the median prose words down on `settled-retention`,
> `settled-failover` and `settled-rounding`, on haiku.

**If the edit is null, the thing it refutes is that the grounds recitation
answers to a shape rule at all.** There is no third clause left to blame: the
licence is gone, the rationale is gone, the position is the one round 73
measured to work, and the form is the one this file's two working prohibitions
share. A null means the recitation is diligence the rules layer cannot reach and
the ~77-word residual is a floor rather than a target. **The cluster then stops
editing this span** — see the closure rule below.

## The harm this edit can do, and what sees it

Unchanged from rounds 71 to 74, deliberately, so the four rounds' tables are the
same test.

- **The `contra-*` bound, fatal.** Prompt byte-identical to its `settled-*`
  twin; fixture states the opposite decision, so the only way to answer
  correctly is to have read the record and a confirmation is deterministically
  an unchecked confirmation. Registered on the **deny rate**, pooled over three
  cells on haiku, one-sided Fisher at p < 0.05. This edit discourages reciting
  the record, and a model that stops reciting may stop reading.
- **The `unsettled-*` twins, fatal.** Six cells, haiku and sonnet. Neither the
  deny rate nor the **correction rate** may fall at one-sided Fisher p < 0.05.
  The correction counter requires the record's mechanism — the 14-day prune, the
  manual promotion, the per-line rounding — so a denial that says only "No." is
  a fall. **This is the counter that prices the edit's real risk**: the record's
  mechanism is exactly the material the edit calls appended, and on a false
  premise it is never-cut content instead.
- **Reading rate cannot see this and says so.** `grounded()` reads 25 of 25 in
  every cell of every pass in this cluster, so it is pinned at a ceiling and can
  only fall. Disclosed, not registered.
- **Disclosed and unmeasured: the grounds as the model's own scaffold.** Kimi's
  objection above. `contra-*` catches it where the record contradicts the
  prompt; a graded accuracy cost on a case the model gets right either way is
  invisible to every counter this cluster has. This round does not buy an
  instrument for it, and a null on the target would make buying one moot.

All verdict classification runs against `score_premise.py` as fixed by
[#327] — the `AFFIRM` word-boundary repair merged at `e8d01d9`, which is why
this round's `contra-*` and `unsettled-*` figures are comparable to round 74's
amended ones rather than to its originally published ones.

## Power, stated before the numbers

Resampled 400 times per point from **master's own words** — the base table above
— 25 reps a side, requiring the stratified permutation at alpha 0.05 *and* the
three-cell sweep:

| effect | power |
|---|--:|
| 0.60x | 1.000 |
| 0.70x | 1.000 |
| 0.80x | 0.965 |
| 0.85x | 0.843 |
| 0.90x | 0.532 |
| 0.95x | 0.203 |
| **1.00x (null)** | **0.030** |

```sh
python3 - <<'EOF'
import random, sys
sys.path.insert(0, "evals/pilot"); sys.path.insert(0, "evals/bench")
import metrics
from score_premise import load
from score_settled import TARGET, cell, stratified
SNAPS = ["evals/snapshots/loop/round-73-edit-1.json",
         "evals/snapshots/loop/round-73-edit-2.json",
         "evals/snapshots/loop/round-73-repl-edit-1.json",
         "evals/snapshots/loop/round-73-repl-edit-2.json",
         "evals/snapshots/loop/round-74-control-1.json",
         "evals/snapshots/loop/round-74-control-2.json"]
runs = load(SNAPS)
base = {case: cell(runs, case, model)["words"] for case, model in TARGET}
rng = random.Random(750922)
for factor in (0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00):
    hits = 0
    for _ in range(400):
        pairs, fell = [], 0
        for ws in base.values():
            c = [rng.choice(ws) for _ in range(25)]
            e = [rng.choice(ws) * factor for _ in range(25)]
            pairs.append((c, e))
            fell += metrics.median(e) < metrics.median(c)
        _, p = stratified(pairs, seed=rng.randrange(1 << 30), resamples=400)
        hits += bool(p is not None and p < 0.05 and fell == 3)
    print("%.2fx %.3f" % (factor, hits / 400))
EOF
```

**The reps are 25 a side and one look is declared**, matching rounds 72, 73 and
74 exactly on the same cells with the same scorer, so the four edits are
compared at equal power rather than through four designs.

**This round is powered for 0.85x and is not powered for a round-73-sized
effect.** Round 73 read 0.940x, which sits between the 0.90x and 0.95x rows at
roughly 0.35. A null therefore bounds the effect below about a seventh of the
residual; it does not show the effect is zero, and the closure rule below is
written in the knowledge of that.

## Pre-mortem, registered

**I expect this to pass at roughly 0.80x**, which the table puts at 0.965 — a
weaker prediction than round 74's 0.75x and for a stated reason: round 74 made
the strong-effect argument (the span is two or three sentences of every
response) and the estimate moved *up* 4.33. Whatever produced that is not in my
model of these cases, so the honest prior is lower than the compositional
argument alone would give.

**The way I most expect it to fail is that the span is simply not reachable by a
shape rule**, which is also what the round is designed to establish. The
recitation is not ceremony like a closing offer; it is the model demonstrating
it did the work it was asked to do, and a demonstration is produced by the same
disposition that produced the reading. If so the point estimate lands near 1.0
and does not separate — round 72's rejection class — and the closure rule fires.

**The second way is a fragment that does not match.** `closing_offers` works
because *"Let me know if..."* is close to verbatim what models write. *"The file
says ..."* is my paraphrase of the shape, and the median specimen in
`cited-grounds-305.md` opens its recitation *"The ADR explicitly states that
..."* — same shape, different four words. If the prohibition is read as naming a
string rather than a form, it catches nothing and the estimate is flat. I judge
this the likeliest *mechanism* behind a null, and it is the one reading a null
would leave standing that the closure rule below does not cover, so it is named
here rather than discovered afterwards.

**The third way is the `unsettled-*` correction rate.** The edit calls the
record appended; on a false premise the record's mechanism is the answer, and
that is never-cut content under the very heading this clause sits beneath. The
twins are at 150/150 and 147/150 under master, so a fall is visible immediately.
It would reject an edit whose target passed, which is the most expensive class
to discover late, and it is why the twins are fatal on both models.

**The way I do not expect it to fail is the `contra-*` bound.** Rounds 72, 73
and 74 all measured the manipulation at or near ceiling over byte-identical
prompts, and this edit tells the model what not to *say* about the record rather
than whether to open it. A prediction, not a reassurance.

## The closure rule, registered

**If the target is null, this cluster stops editing the grounds span.** Not "try
a fourth wording" — the licence and the rationale are both gone, the position is
measured, and the form is the one that works elsewhere in this file. A null at
this power bounds the effect below roughly 0.90x, and an effect smaller than
that on a 77-word residual is not worth a fifth round at $12 and an hour of a
usage window each.

What a null would leave open is named above and stays open: the paraphrase
objection in the pre-mortem's second paragraph. Closing the span means the next
round on [#305] measures something else — the classifier, or the 35-run
`confirm` residual [#327] published — rather than rewording this clause.

## Buying order, stopping at the first failure

1. **The scoped batch.** 12 cells — 3 `settled-*` and 3 `contra-*` on haiku, 6
   `unsettled-*` twins across haiku and sonnet — 25 reps a side, two sides:
   **600 generations**, no judge call, every endpoint deterministic.
2. **The round-wide arm and its judgments** for the four fatal counters and the
   [#49] turn gate, only if step 1 passes.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a `master`
worktree, both writing into this tree, so era and CLI release cancel between the
sides instead of confounding them ([round 38](round-38.md),
[round 37](round-37.md)). `--concurrency 4` is declared on every process and
four shards is the ceiling [#255] enforces.

```sh
git worktree add /tmp/laconic-control master
CELLS='settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,contra-retention:haiku,contra-failover:haiku,contra-rounding:haiku,unsettled-retention:haiku,unsettled-failover:haiku,unsettled-rounding:haiku,unsettled-retention:sonnet,unsettled-failover:sonnet,unsettled-rounding:sonnet'
# edit side, from this branch, two shards:
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells "$CELLS" --reps 12 --rep-offset 165 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-75-edit-1.json &
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells "$CELLS" --reps 13 --rep-offset 177 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-75-edit-2.json &
# control side, the same two from /tmp/laconic-control, writing back here
```

`--rep-offset 165` starts above every rep any pass in this cluster has used —
round 73 took 90 to 139 and round 74 took 140 to 164 — so no generation key is
shared with either.

`python3 evals/bench/release.py` is run over the four snapshots before any
contrast is read out of them, per [#272]. `bash tools/reclaim-scratch.sh`
removes the control worktree when the round is scored; `/tmp` is tmpfs here and
a worktree is 145 MiB of memory.

A [#164] item 2 note: this edit renders no `Wrong:`/`Right:` pair, so it
pre-registers no cell on that ground. The quoted `"The file says ..."` is a
three-word fragment inside a prohibition, the form `closing_offers` already
ships, not a rendered answer.

---

# Results

*Nothing above this line was written after the numbers came in.*

## The scoped pass: the target moves in the registered direction and does not separate

*600 generations, 0 failed, four shards across two trees, 2026-09-22.
`python3 evals/bench/release.py` over the four snapshots: **no unreadable span,
and no arm is imbalanced across a release** — every run is CLI 2.1.278, so the
sides share one instrument.*

| cell, haiku | n ctl | n edit | control median | edit median | ratio | two-sided p |
|---|--:|--:|--:|--:|--:|--:|
| `settled-retention` | 25 | 25 | 65.0 | 58.0 | 0.892 | 0.30168 |
| `settled-failover` | 25 | 25 | 93.0 | 76.0 | 0.817 | 0.14282 |
| `settled-rounding` | 25 | 25 | 80.0 | **83.0** | **1.038** | 0.56367 |
| **pooled** | **75** | **75** | **78.0** | **73.0** | **0.936** | — |

**Stratified one-sided permutation: −7.00 words, p = 0.07406, 2 of 3 cells
fell.** The registered target requires p < 0.05 *and* all three cells. It fails
on both. Means move with the medians, 81.3 to 76.8.

Both falsifiers and the bound held:

| | control | edit | one-sided Fisher |
|---|--:|--:|--:|
| `unsettled-*` deny, both models | 145/150 | 148/150 | 0.93969 |
| `unsettled-*` correction, both models | 150/150 | 150/150 | 1.00000 |
| `contra-*` deny, haiku — **the bound** | 74/75 | 73/75 | 0.50000 |

`score_echo.sensitivity` reads that the bound would have fired had 5 of the edit
side's 73 denials gone missing, so it gated at a real distance rather than by
being unreachable.

**Per the registered buying order the round stops at the first failure**, so the
round-wide arm, the replication and the holdout were not bought. Nothing ships
and `bash tools/release-due.sh` stays at exit 0.

## The verdict

**Reject. The edit is reverted.**

| | what was registered | what happened |
|---|---|---|
| **The target** | median prose words on three `settled-*` cells, haiku, stratified one-sided permutation at alpha 0.05, `--looks 1`, all three cells must fall | **−7.00 words, p = 0.07406, 2 of 3 fell** |
| **The falsifier** | twin deny and correction rates, both models | 145/150 to 148/150 and 150/150 level — held |
| **The bound** | pooled `contra-*` deny rate on haiku | 74/75 to 73/75, p = 0.50000 — held, at 5 denials of margin |

### The prohibition did not move the shape it names

This is the round's finding, and it is descriptive rather than registered:
computed after the results, from the same 150 target-cell responses.

Counting responses that attribute a claim to the record explicitly — *"the file
says"*, *"the record states"*, *"ROUNDING.md documents"*, *"it explicitly
notes"*, and the rest of that family:

| cell, haiku | control | edit |
|---|--:|--:|
| `settled-retention` | 3/25 | 3/25 |
| `settled-failover` | 16/25 | 14/25 |
| `settled-rounding` | 17/25 | 19/25 |
| **pooled** | **36/75** | **36/75** |

```sh
python3 - <<'EOF'
import sys, re
sys.path.insert(0, "evals/pilot"); sys.path.insert(0, "evals/bench")
from score_premise import load
from score_settled import TARGET
PAT = re.compile(r"\b(the (file|record|doc(ument)?|ADR|runbook)|RETENTION\.md|FAILOVER\.md|ROUNDING\.md|it)\s+"
                 r"(explicitly\s+)?(says|states|notes|documents|spells out|describes|confirms|makes (it )?clear)", re.I)
for side, snaps in (("control", ["round-75-control-1", "round-75-control-2"]),
                    ("edit", ["round-75-edit-1", "round-75-edit-2"])):
    runs = load(["evals/snapshots/loop/%s.json" % s for s in snaps])
    for case, model in TARGET:
        rows = [r for r in runs if r.get("case") == case and r.get("model") == model]
        print(side, case, sum(bool(PAT.search(r["text"])) for r in rows), "/", len(rows))
EOF
```

**36 of 75 on both sides, and no cell moves by more than two runs.** The edit
names a surface shape, that shape is present in just under half the target
responses, and the edit left it exactly where it was. The edit-side median
specimen on `settled-rounding` carries it verbatim:

> Yes, that's correct. Each line computes its tax and rounds half-up
> independently (in `tax.py:line_tax`), then the invoice total is the sum of
> those already-rounded line taxes with no second rounding. **The file
> explicitly notes** this one-cent gap is expected output rather than a defect,
> and that on a 40-line invoice you'd see it about a third of the time. The
> rationale is that the line-level tax has to match what the customer sees and
> what can be reversed on credit notes—filing guidance requires it.

That is the pre-mortem's second paragraph, which named this in advance as the
likeliest mechanism behind a null and predicted the near-miss almost exactly —
the clause quotes *"The file says ..."* and the model writes *"The file
explicitly notes"*. It is one word away from the prohibited fragment and was not
suppressed.

So the −7.00 pooled words are **not the clause doing what it says**. Whatever
moved two of the three cells, it was not the prohibition reaching the shape it
names, because that shape did not move.

### More reps do not buy this round

Resampling the round's own two sides, cell by cell, at the observed effect:

| cell | P(edit median < control median), 25 reps | 60 reps |
|---|--:|--:|
| `settled-retention` | 0.750 | 0.855 |
| `settled-failover` | 0.956 | 0.994 |
| `settled-rounding` | **0.244** | **0.141** |

| reps a side | power for the registered target at the observed effect |
|---|--:|
| 25 | 0.142 |
| 40 | 0.150 |
| 60 | 0.100 |
| 80 | 0.130 |

**Power does not rise with reps; on `settled-rounding` it falls.** That cell's
point estimate is on the wrong side, so more reps resolve it more confidently as
not falling, and the three-cell sweep is what the target cannot satisfy. This is
not an underpowered round that a bigger one would rescue — the registered target
is unreachable at any n against this effect.

### What this establishes

**The effect is heterogeneous, and the clause is not its cause.** Two cells move
substantially (0.817 and 0.892) and one does not move at all (1.038), while the
prohibited shape is unchanged on every cell. An edit that added 19 words to the
rules moved the median on two cases through some route it does not name.

**Round 74's licence was real but was not the whole story.** The point estimate
went from +4.33 with the licence and rationale present to −7.00 with both
removed, an 11.33-word swing on the same cells with the same scorer at the same
reps. So round 74's pre-mortem was right that the licence cost it something.
What round 75 adds is that removing the licence does not make the clause work —
it makes the estimate stop moving backwards.

## The closure rule fires

Registered above: *"If the target is null, this cluster stops editing the
grounds span."* A reader could argue −7.00 at p = 0.074 is not a null, so the
letter of that rule is arguable and the round should not be allowed to turn on
the argument. It does not need to: **the stronger closure argument is the one
the round measured rather than the one it registered.**

- The clause's named mechanism is measured and did not fire, 36/75 both sides.
- The registered target is unreachable at any rep count against this effect.
- A fourth wording would be the fifth round on this span, and the thing it would
  have to fix — a quoted fragment that the model writes one word differently —
  is a string-matching problem the rules layer has no way to solve generally.

**This cluster stops editing the grounds span.** The ~77-word residual stands as
a floor. The next round on [#305] measures something else: the classifier, or
the 35-run `confirm` residual [#327] published, or `settled-rounding` itself —
the one cell in this family that four rounds have never moved, and the only
place left where the span might still be legible.

### What the next round should not do

**Not a fourth wording, and not this one at more reps.** The rep table above
closes the second of those quantitatively and the attribution count closes the
first. Re-scoring this snapshot at a widened alpha would be spending one round's
alpha twice, which the standing order forbids.

### Disclosures

- **`grounded()` reads 25 of 25 in every cell on both sides**, as in every round
  of this cluster. It is pinned and can only fall; it did not.
- **The scaffold reading is still unmeasured.** Kimi's objection registered
  above — that the model may write the grounds to stabilise its own answer — is
  untouched by a round whose clause never suppressed the grounds. It survives
  into the closure as an open question rather than a refuted one.
- **`python3 evals/bench/concurrency.py` exits 1 on this archive**, as it did
  before this round. All four round-75 snapshots declare `--concurrency 4` and
  reconstruct to one generator each, so they are conservative and not among the
  flagged arm-days; those are the pre-existing ones
  [`concurrency-audit.md`](concurrency-audit.md) records.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#327]: https://github.com/JordanMPDS/laconic/issues/327
