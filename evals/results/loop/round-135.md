# Round 135: is #500 gone on specs no rule was drafted against? (#500)

**Registration. Nothing below the results line has been computed.** This file,
the three `unseen-*` pilot cases, and `score_relay.py unseen` with its three
reference answers are committed before any generation.

**This round proposes no rule edit.** It is a fire-rate screen at the shipped
rules on three specs written after round 134, so that [#500] either closes on
evidence that does not come from the cells its rules were tuned on, or hands
round 136, which has to carry a candidate, a target that still fires.

`bash tools/candidate-due.sh` exited 0 at registration: round 134 tested a
candidate, so this round may measure. `bash tools/release-due.sh` exited 0:
v0.9.0, which ships round 134's sentence, is tagged and current.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" answered at 620
words after the model read about 125 lines of a spec, relaying most of it,
internal identifiers included. [Round 126](round-126.md) built the instrument,
`relay-rollout`, `relay-migration` and `relay-retention`, and registered when
the defect fires on opus: over 30 answers, at least 15 run 300 prose words or
more **and** at least 15 carry two or more of their fixture's planted
identifiers. Rounds 126, 129, 132 and 134 were accepted against those three
cells.

At the shipped rules (`rules_cksum` 2816272927) the bar is nowhere near
firing. `score_relay.py precheck` over round 134's two edit samples, 60
answers each:

| sample | >= 300 prose words | >= 2 planted identifiers |
|---|--:|--:|
| `round-134-edit-target.json` | 0 of 60 | 4 of 60 |
| `round-134-rep-edit-target.json` | 0 of 60 | 3 of 60 |

The issue stayed open because the answers run 1.1 to 1.3 times a 163-word
hand-written reference. That ratio was never registered as a fire bar, and
any answer longer than the shortest correct one would keep it open. What
those 120 answers cannot show is whether the defect is gone or only gone from
three specs that seven rounds of rule drafting have read. That is the question
this round buys.

## The instrument

`unseen-trust`, `unseen-pricing` and `unseen-limits` copy the `relay-*` shape
in three new domains: a two-part spec of 101 to 110 lines (642 to 719 words),
a caveat that changes how to read the second part, 19 or 20 planted
identifiers no explanation needs, and round 126's prompt form.

| case | the two parts | the caveat |
|---|---|---|
| `unseen-trust` | cross-signing a new internal root, then retiring the old one | the 99.5% gateway figure counts only recent check-ins, and revocation strands the rest |
| `unseen-pricing` | a grandfather period, then a forced plan migration | annual contracts move only at renewal, so the migration takes a year |
| `unseen-limits` | a rate limiter's observe mode, then enforce mode | the limiter fails open at peak, so observe mode's counts are a floor |

Each `trap` grades the two parts and the caveat, as round 126's do. This
round judges nothing: both conditions are deterministic, read by
`score_compression.words` and `score_relay.relayed`. `selftest` checks that
every planted string is in its fixture and none is in its prompt.

## The reference answers

One per case in `score_relay.REFERENCE`, written before generation and
frozen in this commit. Each explains both parts and the caveat and names none
of the planted identifiers, which `selftest` checks. Prose words:
`unseen-trust` 177, `unseen-pricing` 146, `unseen-limits` 171, against
`relay-rollout`'s 163. The ratio to the reference is printed for every cell
and **decides nothing**.

## The design

One `run.py` invocation from this commit: the `laconic` arm at the shipped
rules and the `baseline` arm, which carries no rules, on the three cells on
opus, 10 reps each, 60 generations. Opus because that is where #500 was
seen and where every round since 126 measured it.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
python3 evals/bench/run.py --arms laconic,baseline --cells 'unseen-*:opus' \
    --reps 10 --cases-dir evals/pilot --turn-delivery plugin --concurrency 1 \
    --snapshot $OUT/round-135.json
python3 evals/pilot/score_relay.py unseen $OUT/round-135.json
```

## The reading, registered

1. **Validity.** A case is valid when at least 5 of its 10 `baseline`
   answers meet each condition: 300 prose words or more, and two planted
   identifiers or more. A case that does not draw the defect without rules
   cannot show the rules removed it. The reading needs two valid cases;
   with fewer the round is **INVALID** and concludes nothing about #500.
2. On the valid cases' `laconic` answers, n of them:
   - **FIRES**: round 126's bar, at least half of n on both conditions.
     #500 stays open, the `relay-*` cells are read as overfit, and round 136
     drafts its candidate against these cases.
   - **GONE**: each condition's one-sided 95% Clopper-Pearson upper bound is
     under 0.30, which at n = 30 is 4 answers or fewer on each. 0.30 is the
     per-answer rate at which round 126's own bar fires on 0.017 of draws,
     so a defect below it is one that bar was designed to withdraw an edit
     over. **#500 closes**, with the reference ratios recorded as
     description.
   - **OPEN**: neither. #500 stays open, and these cases are where its next
     candidate is measured.

Each condition is bounded on its own as well as in conjunction, so an answer
that drops every identifier and relays the spec in paraphrase is still caught
by its length.

**What GONE would not show.** The new specs hold the shape, the prompt form
and the identifier density constant, so this round can detect overfitting to
the three `relay-*` fixtures and not to the shape itself. A GONE reads as "gone
on new specs of the shape #500 reported", which is the shape the report has.

## Pre-mortem

The likeliest failure is INVALID through `unseen-pricing`: its spec is the
shortest at 642 words, and an opus answer without rules may explain it in
under 300 prose words. One invalid case still leaves the round two. The
likeliest live result is GONE on length and close on identifiers, since
round 134's control relayed 7 and 13 identifiers on the cells it was not yet
tuned for and its edit relayed a median of 1 on `relay-retention`; an
`unseen-limits` answer that names the limiter `quota-gate` and its flag
`ratelimit.enforce` already carries two.

## Where this design came from

`bash tools/consult.sh` asked codex, deepseek and kimi with the plan above in
draft. Codex and deepseek did not answer within the timeout; kimi did, and
four of its points are adopted: keep round 126's bar absolute and use a
reference answer per case to check the fixture rather than to score it;
give the positive control a per-case validity rule, so one weak case does not
void the round; close on a bound with a stated smallest rate that matters,
not on a bar failing to fire; and bound the length condition on its own, for
paraphrased relay. Its wording note, that a GONE covers new fixtures of the
same shape and not the shape in general, is the paragraph above. Not adopted:
a spare fourth case, for cost, and a separate paraphrase-overlap read, which
the length condition already covers.

[#500]: https://github.com/JordanMPDS/laconic/issues/500

---

## Results
