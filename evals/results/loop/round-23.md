# Round 23

**Baseline:** `evals/snapshots/loop/round-21.json` (+`-judgments`)
**Snapshot:** `evals/snapshots/loop/round-23.json`, `round-23-judgments.json`,
plus the matched batch `round-23-matched.json` and `round-23-matched-judgments.json`
**Rules under test:** baseline `rules_cksum` 1830906901
**Verdict: reject.** The edit did not move its target and is reverted. The
round's substantive result is about a control arm, not about the rules.

First round to score [#46] on `one_turn`, and the first to generate its target
comparison as a **matched interleaved batch** rather than against a stored
baseline.

## Hypothesis

> Adding an ungated third pre-send check to the shared block at
> `rules/laconic.md:7-10` — asking whether the answer claims anything about the
> codebase that was not read, and stating that brevity is a reason to write
> less and never a reason to look less — should move **`one_turn` down** on
> `design-cache`, `design-realtime` and `design-upload`, **sonnet only**, while
> `quality_fails` on those same three cases does not rise and the four
> round-wide fatal counters hold.

`--target one_turn --target-cases design-cache,design-realtime,design-upload
--target-models sonnet`, which is rules 1, 2 and 3 of the six governing this
target. Rule 4 is the `quality_fails` clause above: the surrogate clears **in
addition to** the harm counter, never instead of it.

## Where the hypothesis came from

[`one-turn-investigation.md`](one-turn-investigation.md) established that
laconic's design-answer failures are ungrounded rather than long, and that on
sonnet `num_turns == 1` means the model never opened a file.
[`interleaved-batch.md`](interleaved-batch.md) then measured the mediation chain
end to end in one batch: pooling both sides, answers given without opening a
file fail quality **20 of 39** against **6 of 40** for answers that read the
repository, Fisher p = 7.6e-4, and conditioning on reading removes the rules
effect almost entirely. The harm is not that laconic writes short answers. The
harm is that it stops the model reading, and unread answers are wrong.

**Rounds 16 and 17 aimed at this and missed for a locatable reason.** Their
rule required "a question about code you were pointed at to be resolved from
that code". Every one of the 14 one-turn failures in the investigation falls on
a prompt that names no file, so the gate that rule opens with never fired. The
one change this round makes is removing that gate.

## The edit

`rules/laconic.md`, the shared block above `<!-- level:lite -->`, so it applies
at `lite`, `full` and `ultra` alike:

```diff
-Two checks before sending:
+Three checks before sending:

 1. What is the smallest set of claims that fully answers this?
 2. Is anything here something the user did not ask for?
+3. Am I claiming anything about this codebase that I have not read?
+
+Brevity is a reason to write less, never a reason to look less. A short answer
+about code you did not open is a guess with the hedging removed.
```

Placement is deliberate, and it is round 10's lesson applied: where a rule lives
outranks what it says about where it lives. The pre-send checklist is the
ritual the model already runs before answering, and a grounding check belongs
inside it rather than beside it. It is not in `Level: full`, where rounds 16 and
17 put their version, because the failure is not a full-level behaviour — the
model skips reading at every level, and `ultra` has the least room to recover.

The second sentence is aimed at the mechanism rather than the symptom. What
`interleaved-batch.md` found is that the pressure is **brevity itself**:
`terse-control`, the two-word system prompt `"Answer concisely."`, suppresses
investigation exactly as much as the entire plugin (11/40 against 10/40,
p = 1.000). An edit that only says "read the code" competes with that pressure.
An edit that says brevity does not license skipping the reading contradicts it
directly.

## The registered risk

**This edit may not be able to work.** If a two-word brevity instruction
produces the same suppression as 130 lines of rules, then the pressure is a
property of asking for terseness and not of anything `rules/laconic.md` says,
and no sentence inside the plugin can remove a pressure that two words also
create. Registering that now: if the target does not move, the reading is that
the mechanism is out of the rules file's reach, and [#46] closes as a property
of brevity rather than as a defect to be fixed. That is a real answer.

## Design

**Batch A — the matched target measurement.** `design-cache`,
`design-realtime`, `design-upload`, sonnet, **n=10**, generated as one
interleaved pass alternating one rep at a time between two trees: master from a
`git archive` of the pre-edit commit, and the edit from the repository. Master
runs all five arms; the edit runs `laconic`. 180 generations.

`concise-style` is in it, per the standing rule that it belongs in every
interleaved batch. Round 21's figures for it are from carried arms generated ten
days before the treatment, and inherit exactly the provenance defect that
retired the `terse-control` claim this week; this is the first matched
measurement of the native output style against the plugin.

n is 10 rather than the round's 5 because batch A carries its own master side
and is not scored against the round-21 baseline, so the reps are free to choose.
At 15 a side the target would need something near a 6-of-15 to 0-of-15 collapse
to reach alpha; at 30 a side it can resolve the size of drop that is actually
plausible.

**Batch B — the round-wide fatal counters.** The edit's `laconic` arm at 22
cases, both models, **n=5** to match the round-21 baseline, controls and control
verdicts carried from round 21. 220 generations. This is what
`never_cut_failures`, `quality_fails`, `safety_fails` and `violations_total` are
read from, and carrying is correct for them because they compare the laconic arm
of two rounds and read no control at all.

Batch B also covers the three target cells on sonnet a second time, at n=5 and
cross-batch. That reading is **disclosed, not scored** — it is the comparison
this session spent 200 generations establishing to be unreliable.

**Both batches run strictly sequentially**, one CLI invocation in flight, per
[#120]. The overlap sweep goes in this file when the round reports.

## Cost

About 400 generations and 280 judge calls, roughly $30.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#120]: https://github.com/JordanMPDS/laconic/issues/120

---

# Results

**Batch A completed at n=10: 180 generations, 30 matched cells an arm, 0
failed.** Strictly sequential across both trees — **maximum one run in
flight**, wall 113.9 minutes against 109.8 summed, ratio 0.96. Checksums
verified before and after at 1830906901 and 496307668; `cases_cksum` 1067281786
on both sides.

Batch C, the 220-generation round-wide arm, was **not run**. The target failed,
so the four fatal counters could not have changed the verdict, which is the
precedent rounds 11, 12 and 14 set. This round therefore reports **no
round-wide counters** and does not substitute the scoped ones for them.

## The target: an exact null

| arm | one-turn | grounded median | unread median | overall |
|---|--:|--:|--:|--:|
| `baseline` | 4/30 | 3988 | 2266 | 3834 |
| `terse-control` | 8/30 | 3354 (−16%) | 1365 | 2912 (−24%) |
| `word-compression` | 10/30 | 3421 (−14%) | 1291 | 2879 (−25%) |
| `laconic`, master | 12/30 | 4211 (+6%) | 1894 | 3415 (−11%) |
| `laconic`, **edit** | 12/30 | 4322 (+8%) | 1472 | 2864 (−25%) |
| `concise-style` | **23/30** | 2787 (−30%) | 1319 | 1542 (−60%) |

**Master 12/30 against the edit's 12/30, Fisher p = 1.0000.** The edit moves
`one_turn` by exactly nothing. It does compress — overall −25% against master's
−11% — but every token of that comes from the unread stratum (1894 to 1472),
and the grounded stratum went *up*.

**Three interim readings of this contrast were taken while the batch ran, and
all three were wrong.** At 9 matched cells it read 1/9 against 5/9; at 15,
4/15 against 9/15 at p = 0.139; at 18, 6/18 against 9/18 at p = 0.50; at 30 it
is 12/30 against 12/30 at p = 1.000. Nothing changed but the sample. The first
two supported "the edit actively suppresses reading" and were spoken aloud
mid-batch; they are retracted here. **No interim number from a running batch
should be cited.**

## Quality: the co-requirement holds, and reading explains everything

Rule 4 requires the surrogate to clear **in addition to** `quality_fails` on the
same cases, never instead of it. It does:

| | quality fails | grounded | unread |
|---|--:|--:|--:|
| master `laconic` | 12/30 | 0/18 | 12/12 |
| edit `laconic` | 10/30 | 1/18 | 9/12 |

Fisher p = 0.789. Quality did not rise, so the round rejects on its target
alone.

**The five-arm split is the round's most important table.** Counting
`not_exercised` as a failure, over the master batch's 150 verdicts:

| arm | quality fails | grounded | unread |
|---|--:|--:|--:|
| `baseline` | 6/30 (20%) | 2/26 (8%) | 4/4 (100%) |
| `word-compression` | 9/30 (30%) | | |
| `terse-control` | 10/30 (33%) | | |
| `laconic` | 12/30 (40%) | **0/18 (0%)** | 12/12 (100%) |
| `concise-style` | 22/30 (73%) | **0/7 (0%)** | 22/23 (96%) |

`concise-style` against `baseline` is p = 0.0001; `laconic` against `baseline`
is p = 0.158.

Pooled over all five arms: **answers that read the repository fail 4 of 93
(4%); answers that do not fail 55 of 57 (96%), Fisher p = 1.5e-33.**

This is the mediation chain from
[`interleaved-batch.md`](interleaved-batch.md) — there p = 7.6e-4 — reproduced
at near-total strength. **Conditional on reading, the compression style has no
measurable effect on quality.** laconic's grounded answers failed 0 of 18;
`concise-style`'s failed 0 of 7; baseline's failed 2 of 26. The arms' quality
ranking is exactly their reading-rate ranking inverted, and nothing else about
their wording registers.

The consequence for the product is that **there is only one axis.** Compression
is free — laconic's grounded answers cost nothing in quality, and
`concise-style` compresses grounded answers 30% at no quality cost either. What
separates the arms is entirely how often they open a file. A terse mode that
reads as often as no instruction at all would carry baseline's quality and its
own compression, and that is the only differentiation this data supports.

## The mechanism, which survives the null

The count went nowhere, but the transcripts show something the count cannot.
**None** of the edit's one-turn responses acknowledges that no file was opened.
They answer confidently and generically:

> Recommended flow, given mobile-camera-sized photos (typically 2–12MB each):
> **Client side** — Resize/compress in the browser or app before upload…

against a master response on the same case that read the fixture:

> **The binding constraint:** `nginx.conf:12` caps every request through the
> shared listener at 1m, and the comment says raising it — even per-location —
> was already declined by the payments team for PCI reasons.

The check was **"Am I claiming anything about this codebase that I have not
read?"** That question has two exits. One is to read the code. The other is to
stop making claims about the codebase, answer generically, and pass the check
honestly. The unread median falling 1894 to 1472 is that second exit being
taken and *measured*: the edit made ungrounded answers shorter and more
generic without making them rarer.

**A verification check phrased against claims can always be satisfied by
deleting the claims.** Rounds 16 and 17 failed because their rule was gated on
being pointed at a file; this one failed because its check could be satisfied by
retreating to generality. A rule that works has to make *reading* the cheaper
branch, not make *claiming* more expensive.

## The finding that outranks the round

Held at `baseline`'s 87% reading rate, each arm's own writing produces:

| arm | actual | at baseline's reading rate | share that is mix-shift |
|---|--:|--:|--:|
| `terse-control` | 2912 (−24%) | 3089 (−19%) | 19% |
| `word-compression` | 2879 (−25%) | 3137 (−18%) | 27% |
| `concise-style` | 1542 (−60%) | 2591 (−32%) | 46% |
| `laconic`, master | 3415 (−11%) | **3902 (+2%)** | **116%** |
| `laconic`, edit | 2864 (−25%) | **3942 (+3%)** | **111%** |

**On design questions, laconic does not compress. It stops the model reading,
and shorter answers follow from that.** Held at baseline's reading rate it is
2% *longer* than baseline. Its entire measured token effect on these cases is
mix-shift. The two-word `terse-control` compresses genuinely at −19%; the
native style at −32%; laconic at zero.

And laconic's suppression is not marginal: **12/30 against baseline's 4/30,
Fisher p = 0.0391**. The plugin significantly stops the model reading, on the
cases where reading is what makes answers correct.

`concise-style` is worse — 23/30 against 4/30, **p = 1.3e-06**, and worse than
laconic at p = 0.0082 — but "we suppress investigation less than the native
style does" is not a product claim. Both arms are on the wrong side of
`baseline`.

### What the native style installs

Delivered through `--settings '{"outputStyle":"Concise"}'`, it **replaces** the
opening of Claude Code's system prompt rather than appending to it, which is why
`--append-system-prompt` cannot reproduce it and why the arm carries no
`system_prompt`. From the 2.1.240 bundle:

> You are an interactive CLI tool that helps users with software engineering
> tasks. Keep your responses short and direct while doing the work just as
> thoroughly.
>
> \# Concise Style Active
>
> The user chose brevity over narration. You should:
>
> 1. **Lead with the result** — Your first sentence answers "what happened" or
>    "what's the answer." No preamble ("Let me...", "Now I'll...") and no
>    closing recap of what you already said.
> 2. **Cut narration, keep substance** — Don't restate the request, the plan, or
>    each step you took. Report outcomes, decisions, and anything the user must
>    act on.
> 3. **Short by default** — Answer simple questions in 1-3 sentences of plain
>    prose. Use headers, tables, and bullet lists only when they carry real
>    structure, never as decoration.
> 4. **State things plainly** — Skip hedging boilerplate. Mention a caveat only
>    when it changes what the user should do next.
> 5. **Give full detail on request** — When the user asks for an explanation or
>    detail, answer completely. Conciseness never means withholding requested
>    information.
> 6. **Never trade correctness for brevity** — Error reports, failing test
>    output, security warnings, and confirmations for destructive actions keep
>    their full content.
>
> Where these rules conflict with more general communication or formatting
> guidance elsewhere in your instructions, these rules win.

Its per-turn reminder is "Be concise: lead with the result, skip preamble and
narration, keep only what the user needs." `keepCodingInstructions` is true, so
the tool-use instructions remain.

Rules 5 and 6 are laconic's "length scales to the request" and its never-cut
list, nearly clause for clause, and the opening line says *"while doing the work
just as thoroughly"* outright. **The instruction not to trade thoroughness for
brevity is present, explicit, and does not hold.** A purpose-built native style
that names the failure mode in its own first sentence still stops reading 23
times in 30. That is the strongest available evidence for this round's
registered risk.

### The metric this invalidates

`output_tokens` as this loop has scored it for 23 rounds is the **marginal**
median, and it pays for not reading. Round 20's headline −59% on the five older
design cases decomposes to −42% real within-stratum compression plus mix-shift;
its reading rate fell 41/50 to 24/50 in the same edit. Every token target this
loop has accepted or rejected was measured on a statistic that a suppressed
reading rate improves.

**The instrument needs a stratified token target** — compression measured
within the grounded stratum, with `one_turn` guarding the mix — before any
further token work is meaningful. Filed as the first consequence below.

## Consequences

**For [#46].** Three edits have now failed for three different reasons: rounds
16 and 17 on a gate that never fired, round 23 on a check satisfiable by
retreating to generality. The control arms say the pressure is not laconic's
wording — `terse-control` at two words suppresses comparably, `concise-style`
far more. The next attempt must make reading the *cheaper* branch. A spike
testing exactly that is queued: the round-10 licence, which is the best grounded
compressor ever measured here at −41%, with its permission made conditional on
having read.

**For the benchmark.** A stratified `output_tokens` target, as above. This is
the highest-value instrument change available and it is independent of any
rules decision.

**For the product.** `docs/benchmark.md` publishes the `concise-style`
comparison from arms generated ten days before their treatment, and its
compression figures are now known to be roughly half a reading effect on both
sides. It needs rewriting against this batch.

**Still unmeasured.** Round 21 shows `concise-style` with 3 never-cut failures
against laconic's 0, all on haiku, 2 on `destructive` and 1 on `conditional`.
`destructive`/haiku has a measured master-rules rate of 5 of 65, putting 2 of 5
at roughly p = 0.05 — suggestive and unsettled at five reps. With compression
now shown to be a wash, that is the plugin's last claimed edge, and it deserves
its own batch.
