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

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#327]: https://github.com/JordanMPDS/laconic/issues/327
