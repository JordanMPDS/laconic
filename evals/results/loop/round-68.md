# Round 68: an explanation the user already has, asked for again (#298)

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are why this round has the scope and
the power it has. This file, the case pair, the layout contract and the scorer
are committed in one commit before any generation, following
[round 38](round-38.md) through [round 67](round-67.md).

`bash tools/candidate-due.sh` exits 1: [round 67](round-67.md) was the one
measuring round the cap allows, so round 68 has to carry a rule edit. It does,
under **The edit** below.

## The issue

[#298] is a user report at level `full`. In a long analytical session the user
asked seven words — a definition request for two metrics the model had just
built — and got **342 prose words across 11 paragraphs**, of which the reporter
classified **239 (69.9%)** as restating claims already delivered in earlier
turns: the mechanism paragraph from the plan turn, the error-direction bullets
from the same turn, and figures that were in a table in the immediately
preceding turn. Only 85 words were new. Asked to rate the answer, the model
produced the correct one in **66 words**, a 5.2x reduction with no new
information.

The reporter's diagnosis is that this violates no rule. The never-cut bullet

    - Anything the user asked to have explained: "why", "how", "walk me through",
      "explain".

fires on *"what is X?"* and grants affirmative cover to explaining X. It is
silent on whether X was explained two turns ago, and it is stated in absolute
terms, so it overrides the per-response check at the top of the file. The one
already-seen-content clause in the ruleset covers *work* — "No recap of work
visible in the diff" — and not prose.

This is [#150]'s principle failing in a plain conversational turn. [#150]'s own
instance is intra-document, at 17%; this is 70% across turns. It is also not
[#136]: #136's case violates two explicit rules and is a rule failing to fire,
where this one has affirmative cover and no rule to fire.

## The edit

One sentence, appended in place to the bullet that grants the cover:

```diff
 - Anything the user asked to have explained: "why", "how", "walk me through",
-  "explain".
+  "explain". Explain what is new; where the answer needs something you have
+  already said this session, point back to it rather than saying it again.
```

**The wording is not [#298]'s proposal, and the difference is the round's main
design decision.** #298 proposes *"a claim they have already been given is not
part of it"* — a set difference the model computes against the transcript.
`tools/consult.sh` put three objections to that shape and `kimi` answered; two
of them are the reason the edit reads as it does.

- **Negative framing tells the model what to delete, not what to produce**, and
  "claim" is the wrong abstraction for a definition request — a model may
  reasonably decide a definition is not a claim and restate it anyway. The
  edit is positive and names the behaviour wanted: point back.
- **It writes the bullet's limit into the bullet's own prose**, which is the
  shape rounds 07, 08 and 09 lost with and round 10 won by avoiding — "where a
  rule lives outranks what it says about where it lives". The edit here makes
  no precedence claim at all. It does not say the explanation stops surviving;
  it says how to deliver the part the user already has.
- A back-reference also answers the third objection, which is that a blanket
  suppression would cut a restatement the user needs in order to act. "As
  above" leaves the claim findable; deleting it does not.

`codex` and `deepseek` were asked and neither answered inside the timeout. That
is recorded so a reader can tell "nobody objected" from "nobody was asked".

## The instrument: one turn of difference, same question

`evals/pilot/{explain,reexplain}-{index,metric,rollback}` is a cold/warm pair
over `deep-*`'s three fixtures, built in the shape `confirm-*` and `recall-*`
already established:

- **`reexplain-*`** is two turns. Turn 1 is `deep-*`'s open diagnosis question,
  byte for byte. Turn 2 is the graded turn and asks a bare definition request
  for two objects the turn-1 answer has already reasoned about.
- **`explain-*`** is one turn and asks the same question cold, carrying the read
  instruction that `reexplain-*`'s turn 1 already carried. That single-clause
  asymmetry is exactly how `confirm-*` is `recall-*`'s cold twin.
- The fixture is shared by symlink, not copied, and the `trap`, `never_cut` and
  `grading` are byte-identical across the pair.

`reexplain-metric`, in full:

    read ANALYSIS.md — what is wrong with how this experiment is being reported? Don't edit anything.
    <!-- turn -->
    what is lift and what is the absolute difference here? Don't edit anything.

**The premise was verified before the round was designed, and it is what makes
the pair mean anything.** `kimi` named it as the thing that would break the
instrument: if turn 1 does not deliver the material turn 2 asks about, there is
nothing for the edit to suppress. Reading the stored laconic `deep-metric`
turn-1 responses in the committed `register-136-metric.json`, turn 1 already
says that the reported lift rests on four purchases, that moving one swings the
headline from +36% to +125%, and that the absolute difference does not rescue
it because resolving 0.3 points needs about 34,000 sessions per arm against the
912 and 934 collected. What it does **not** give is either definition: not
`(treatment_rate / control_rate) - 1`, not the percentage-point form. So the
graded turn has a genuinely new core wrapped in a rationale the user already
holds, which is #298's 24.9%/69.9% structure reproduced in the instrument.

`tests/test_evals_layout.sh` holds the whole contract: one turn against two, the
warm case's turn 1 equal to `deep-*`'s, the graded question equal across the
pair up to the read instruction, one shared fixture, and identical traps.

## Registered endpoints

**Primary.** Prose words on the graded turn, **laconic** arm, as a difference of
differences on the log scale:

    (reexplain_edit − reexplain_control) − (explain_edit − explain_control)

two-sided permutation of the rules-revision label within each family, seed 68,
alpha = 0.05. **Registered direction: negative** — the edit shortens the
already-told question by more than it shortens the cold one. Reported as a ratio
of ratios, where below 1 is the registered direction.

**`explain-*` is the placebo, and it is what makes the primary mean the thing
#298 asks for.** A cold question has nothing already given for the new clause to
remove. An edit that shortens both families equally is a general brevity effect
and the interaction is zero, so it cannot pass by being terser across the board —
which is how [round 64](round-64.md) and [round 66](round-66.md) failed, both on
edits that did not separate.

**Secondary, and underpowered by construction.** The same interaction per cell
over the three stems, as a two-sided exact sign test. `kimi` is right that three
paired cells cannot reach alpha — the minimum two-sided p over three is 0.25 —
and its recommendation was six cells. Six is not available: there are three
fixtures, and the only other route to six is a second model, for which this
family of cases has **no stored runs at all** and therefore no power basis to
register against. So the sign test is reported as a consistency reading and
carries no verdict. Three of three in the registered direction is the reading
that supports the primary; two of three does not contradict it.

**Falsifier, and it rejects outright.** The edit may not buy its brevity by
dropping a definition. Judged quality on the `reexplain-*` graded turn, both
sides, against a trap that grades only whether the two objects were correctly
identified. **Registered bar: the edit side's pass rate may not fall below the
control side's.** Bought only if the primary fires — a round that does not
reject on length has nothing to protect.

**Harm check, deterministic and free.** The `index` stem's one never-cut
keyword, `date_trunc`, present on the graded turn. It covers a third of the
batch and the other two stems carry none, exactly as in rounds 67 and the
register pilot.

**Descriptive, on the control side alone: does the reported harm exist here at
all?** `reexplain-*` against `explain-*` at master rules. If the warm family is
not longer than the cold one, #298's mechanism did not reproduce in this
instrument, and a null on the primary says nothing about the edit. This is
reported whichever way the primary goes.

## The registered decision rule, written before any generation

1. **The interaction is negative and reaches alpha, and the falsifier holds.**
   The edit does what #298 asks and does not cost the definitions. Accept,
   replicate, holdout, release.
2. **The interaction is negative and reaches alpha, and the falsifier fails.**
   The edit bought brevity by dropping content the user asked for. Reject and
   revert, and record that the scoped carve-out is reachable but that this
   wording overshoots.
3. **The interaction does not reach alpha.** Reject and revert. Read against the
   descriptive contrast: if the control side shows the warm family longer, the
   mechanism is present and this wording did not move it; if it does not, the
   instrument did not reproduce #298 and the round bounds nothing about the
   rule.
4. **The interaction is positive and reaches alpha.** The edit lengthens the
   already-told answer relative to the cold one. Reject and revert, and record
   it — a back-reference instruction that makes the model narrate the
   back-reference is a real and reportable failure mode for the wording.

## Power, stated before the numbers

Computed from committed snapshots of this instrument's nearest relatives, both
laconic and both under `plugin` delivery on sonnet: `confirm-*` reads a
standard deviation of **0.219 on the log scale** (n = 30) and `deep-*` turn 5
reads **0.506** (n = 510). The graded turn here is a definition request, closer
in shape to `confirm-*`; taking a conservative 0.35, the standard error of the
log-scale difference of differences at n per group is `sqrt(4 × 0.35² / n)`.

| reps per group | detectable ratio of ratios at 80% power |
|---:|---:|
| 10 | 0.54 |
| 20 | 0.65 |
| 30 | 0.70 |

**The round is registered at 30 reps a side per family**, which detects a 0.70
ratio of ratios. #298 reports 5.2x, and the register pilot reproduced #136's
mechanism at roughly an eighth of its reported size, so budgeting for a modest
effect rather than the reported one is the point of the third row.

**Ten reps are generated first as an instrument check and are not scored against
the gate.** The check is whether the text is what the design assumes: turn 1
delivering the rationale, the graded turn answering the definition, neither
family degenerate. `run.py` resumes by key, so extending to 30 buys exactly the
data a single 30-rep pass would have. Reading the gate at 10 and stopping on a
hit would be optional stopping, so the analysis point is 30 and is fixed here.

## The command

Two shards, one per rules revision, launched together and declaring each other,
following [round 38](round-38.md). The two sides cannot share an invocation —
`rules_cksum` is resolved once at startup — and they may not run one after the
other, because this project has measured a syntactic behaviour moving 4.7x in
five days at byte-identical rules ([round 37](round-37.md)).

```sh
git worktree add /tmp/laconic-68-control master
python3 evals/bench/run.py --arms laconic --models sonnet --reps 30 \
  --cases 'explain-index,explain-metric,explain-rollback,reexplain-index,reexplain-metric,reexplain-rollback' \
  --cases-dir evals/pilot --turn-delivery plugin --concurrency 2 \
  --snapshot evals/snapshots/loop/round-68-edit.json &
cd /tmp/laconic-68-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 30 \
  --cases 'explain-index,explain-metric,explain-rollback,reexplain-index,reexplain-metric,reexplain-rollback' \
  --cases-dir evals/pilot --turn-delivery plugin --concurrency 2 \
  --snapshot /home/jordan/projects/laconic/evals/snapshots/loop/round-68-control.json &
wait
```

Six cases, one arm, 30 reps: 180 runs and **270 calls a side**, because the warm
family is two turns and the cold family is one. 540 calls over the round. Two
shards is inside [#255]'s ceiling of four, and `--concurrency 2` is declared on
both per [#120] — two CLI invocations really are in flight, and each snapshot
still reconstructs to one generator of its own, so the declaration is
conservative rather than false. `--turn-delivery plugin` because this is a claim
about the product: #298 is a report from a real session, and the cluster's
multi-turn instrument reverses under `repeat` — see
[`turn-delivery.md`](turn-delivery.md).

The control worktree is removed when the round is scored. `/tmp` is tmpfs on
this machine, so it is 145 MiB of memory rather than disk until it goes.

Scored by:

```sh
python3 evals/pilot/score_reexplain.py \
  evals/snapshots/loop/round-68-control.json \
  evals/snapshots/loop/round-68-edit.json 68
```

## What this round cannot establish

- **It does not measure restatement.** The endpoint is words on the graded turn.
  A shorter answer that is shorter for some other reason would read the same,
  and the placebo family is the only thing separating the scoped effect from a
  general one. [#155]'s detectors cannot help: as #298 argues, every restated
  word in its instance is perfectly non-redundant *within* the response, so a
  single-turn judge scores it clean. A cross-turn detector is the follow-up this
  round does not build.
- **It tests one wording.** A null rejects this sentence, not the idea that the
  carve-out should be scoped.
- **Sonnet only.** The instrument has no haiku runs to register against, and the
  round buys none.
- **Three stems.** The per-cell sign test cannot reach alpha, and says so above.

[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#298]: https://github.com/JordanMPDS/laconic/issues/298

## Results

<!-- Nothing above this line has been computed. -->

## Result: the model already points back, and there was nothing left to remove

**The primary is null and the descriptive check is why.** At master rules the
already-told question is not longer than the cold one — it is **less than half
as long**. The mechanism [#298] reports did not appear in this instrument at
all, so the registered decision rule's third branch applies in its second
sub-case: reject and revert, and the round bounds the wording rather than the
idea.

360 runs, 180 a side, 0 failed.

### The descriptive check, which was meant to confirm the harm and refuted it

    explain (cold)     n = 90   median  65.0 prose words
    reexplain (told)   n = 90   median  27.0 prose words
    ratio 0.415, permutation p = 0.0000

On geometric means the same contrast reads **0.357, with a 95% bootstrap
interval of 0.287 to 0.444**. Every stem moves the same way and none of them is
marginal:

| stem | cold, median | warm, median | ratio |
|---|--:|--:|--:|
| `index` | 67.0 | 32.5 | 0.485 |
| `metric` | 34.0 | 6.0 | 0.176 |
| `rollback` | 79.0 | 29.0 | 0.367 |

**It is not a markup artefact.** `metrics.score` drops fenced blocks and inline
spans, and a definition answer carries its formula in one, so the round reports
a raw whitespace-token count beside the prose count. Raw reads 78.5 cold against
35.5 warm, a ratio of 0.452 against prose's 0.415. The two counts agree.

**It is not a degenerate warm answer either.** The falsifier's content was not
bought, because the primary did not fire, but the free harm check covers the one
stem that has a never-cut keyword and it is clean at ceiling: `date_trunc` is
present in **30/30** graded turns in all four cells. Reading the warm texts
directly, `reexplain-metric` at 6 prose words is
`"Lift: +70% (relative). Absolute difference: +0.31 percentage points (0.75% − 0.44%)."`
— both objects identified, both definitions given, the arithmetic shown. The
warm answer is short because it is only the answer. The cold answer is longer
because it wraps the same answer in the rationale the warm turn had already
delivered.

The instrument shows why in a second, structural way that needs no scoring: the
graded turn of `reexplain-*` makes **zero tool calls in 90/90 runs** and
`explain-*` makes one or two in 90/90. The cold family goes and reads the file;
the warm family answers from what it already has. That is the pair working as
designed, and it is also the shortest statement of the result — given the
material once, the model does not fetch it or restate it again.

### The primary: the edit moves neither family

| family | n | control | edit | ratio | p |
|---|--:|--:|--:|--:|--:|
| `explain` | 90 | 65.0 | 63.0 | 0.969 | 0.8226 |
| `reexplain` | 90 | 27.0 | 27.0 | 1.000 | 0.9957 |

    interaction, log words: ratio of ratios 0.988, p = 0.9430
    interaction, raw words:                        p = 0.8418
    95% bootstrap interval on the ratio of ratios: 0.724 to 1.357

The registered direction is negative and the point estimate is essentially
zero. The per-cell sign test reads **2 of 3 negative, two-sided exact
p = 1.0000**, which the registration wrote down in advance as carrying no
verdict.

**The interval is the one thing the round buys about the wording.** It excludes
a ratio of ratios below 0.724, which is very close to the 0.70 the power table
registered at 30 reps a side, so the round is at the sensitivity it planned for
and the effect is not hiding under it. What it cannot do is generalise that
bound, because a scoped carve-out cannot be measured on an instrument where the
scope is already empty: the warm answer had 27 words, and an instruction to say
less of what you already said has nothing to act on there.

### What this closes and what it does not

**[#298]'s wording is rejected and reverted.** The edit is not in
`rules/laconic.md` and `rules/dist/*.md` is regenerated from master's text.

**The round does not refute [#298].** The report is a real transcript, and the
distance between it and this instrument is the finding worth carrying forward:
#298's instance is **one definition request deep in a long analytical session**,
and this instrument's is **one definition request after exactly one prior
turn**. At one turn of depth the model compresses by 2.4x unprompted. The report
describes 342 words where 66 would do, which is a 5.2x expansion, and the two
observations are only compatible if the behaviour is a function of session
depth rather than of the material having been delivered once.

That is a testable follow-up and this round did not test it. It is also the
second time this cluster has found the reported magnitude absent from a
short instrument: [`register-inheritance-136.md`](register-inheritance-136.md)
reproduced [#136]'s mechanism at roughly an eighth of its reported size, and
[round 67](round-67.md) closed the over-length cluster's last named candidate
without finding the gap. Depth is now the common shape in three results, and
[`over-length-cluster.md`](over-length-cluster.md) has no named candidate that
is not depth.

**The instrument is kept.** `explain-*`/`reexplain-*` is a clean cold/warm pair
that reproduces a large, tight, three-of-three effect in the *opposite*
direction to the one it was built to find, which makes it a usable control for
any future round about restatement. It cost $15.75 and 360 runs to establish
that a behaviour the loop assumed needed a rule is already the model's default
at one turn.

## Registration and generation notes

**All 360 runs are on one CLI release**, 2.1.272, per-run stamped on both sides.
`python3 evals/bench/release.py` reports no unreadable span and no arm
imbalanced across a boundary. `python3 evals/bench/concurrency.py` reconstructs
a peak of **1 CLI invocation in flight** per arm-day against a declared 2, so
neither snapshot exceeds its declaration; both are absent from the audit's
failure list.

**Generation was interrupted twice and resumed, and the resumes are recorded in
the files.** Each snapshot names three generator ids: the first pass covered
reps 0 to 9, the second reps 10 to 13, and the third completed the round through
rep 29. The second pass stopped mid-rep and left 8 empty-text runs a side. A
failed key is not recorded as done, so the third pass regenerated all 16 rather
than carrying them, and both files finish at **180 runs and 0 failed**. The [#69] checksum guard permitted each resume,
which is the check that says the three passes are one instrument: `rules_cksum`
594915793 on the control side throughout and 3488167215 on the edit side
throughout, `cases_cksum` 1818115439 on both.

**The interruptions cost nothing that the design depends on.** The two sides
were launched together on every pass and stopped together, so the simultaneity
[round 38](round-38.md) requires holds pass by pass rather than only in
aggregate, and the 2.1.272 stamp is the same on every run of both sides.

**Nothing was judged.** The falsifier is bought only if the primary fires, and
it did not.

**The scorer was changed twice after registration, during the instrument check
and before the analysis point.** This is disclosed rather than argued around,
because the scorer was committed with the registration precisely so that it
could not be tuned against the result. Generation began at 20:58:07Z; `a95cc71`
is timestamped 21:00:21Z and `b30e949` 21:09:01Z, both inside the first pass.

1. **`a95cc71` makes the per-cell test iterate three stems rather than six
   cases.** The registration says three and the scorer said six; the scorer now
   follows the registration. It changes the **secondary**, which the
   registration wrote down in advance as carrying no verdict.
2. **`b30e949` adds the raw-token column** reported above, which the
   registration did not specify and which exists because a definition answer's
   formula lives in an inline span. It is additive reporting and computes no
   test.

**Neither touches the primary.** `difference_of_differences`, `log_words` and
`interaction` are byte-identical to the versions committed with the
registration, so the number the verdict rests on is computed by registered code.

**What was visible when those commits were written, stated plainly.** `b30e949`'s
own message quotes the descriptive contrast off the 10-rep instrument check — 65
prose words cold against 26 warm — so the refutation of [#298]'s premise was
already in view at rep 9, and the raw-token column was added in response to it.
The registration authorises exactly that: the instrument check exists to read
the text and is explicitly not scored against the gate. What it forbids is
reading the gate early and stopping on a hit, and that did not happen — the
primary was first computed at the registered 30 reps a side, on the completed
files, once.
