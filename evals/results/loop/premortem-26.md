# Can a round's author call a weak idea in advance? The pre-mortems, scored

**No generation calls.** The predicted classes come from 75 blind panel calls,
three per round; everything else is arithmetic over committed files:

```sh
python3 evals/results/loop/candidate-defects/premortem.py
python3 evals/results/loop/candidate-defects/premortem.py --selftest
```

## Why this unit exists

[#26] proposed replacing the loop's one-candidate step with several proposers
and an adversarial panel that tries to refute each candidate before it earns a
confirmation round. [`candidate-defects-26.md`](candidate-defects-26.md) (#311)
left it deferred and named the measurement that would decide it:

> After a handful of rounds, [#26] is decidable on whether the loop's own author
> can call a weak idea in advance; if the author cannot, a panel of proposers
> reading the same inventory is very unlikely to.

It made that measurement step 5 of the loop skill: every candidate round
registers a pre-mortem, *how do I expect this to fail, and which of the three
rejection classes would that be*, committed before any generation. Twenty-five
candidate rounds have registered one since, rounds 71 to 104. Nobody has scored
them, and eleven of the twenty-five had no outcome label either.

## Registration

*Everything in this section was committed before any panel call was made.*

### What the author of this unit already knew

`labels.json` carries a free-text `note` on fourteen of these rounds, written
after their results, and several of those notes say whether the pre-mortem
was right. This unit's author has read them. That is why the predicted class is
not this author's reading: it comes from a panel that sees only the
registration-time document and has never seen a result.

### The material

Each round's **registration commit**: the first commit on its pull request that
contains `round-N.md`, fetched from `refs/pull/<PR>/head` because the loop
squash-merges and master holds only the final version. Every one of the 25 has
an empty `## Results` section at that commit, and every one has a
`## Pre-mortem, registered` section that is **byte-identical** to the same
section in the final document on master, so no pre-mortem was edited after its
result. `premortems.json` records each commit and a checksum of the section;
`premortem.py --selftest` fails if a round document's pre-mortem stops matching.

### The predicted class

A panel of sonnet, opus and kimi (the Kimi Code subscription), called through
`judge.py`'s own `_call_blind` and `_call_kimi`, so each call runs in a fresh
temporary directory outside the repository with nothing to read. Each member gets
the registration-time document, cut at `## Results`, and classifies the failure
its pre-mortem names as likeliest into one of five classes. The first three are
the ones the loop skill asked the author to choose between, in its own words:

| class | the pre-mortem expects |
|---|---|
| `idea-defect` | the primary's point estimate to move **against** the registered direction, or a registered check to show the edit's mechanism does not operate |
| `noise-floor` | the point estimate to move **with** the registered direction, or barely at all, and not separate: too small, too noisy, underpowered, under a magnitude bar, or failing to replicate |
| `failed-gate` | the primary to pass and another registered bar, bound or fatal counter to reject |
| `unscored` | a stage registered before the primary, such as a fire-rate precheck or a control assay, to fail |
| `none` | no failure, or several without saying which is likeliest |

The prompt is `PROMPT` in `premortem.py`. Two agreeing votes decide. A three-way
split is recorded as `split`, and a vote that failed or did not parse is retried
on the next `--label` run, as `judge.py` does.

### The outcome class

`labels.json`, under the criterion `candidate-defects-26.md` registered. The
eleven rounds that had no label were labelled in this unit from the printed
numbers in their results sections, by readers instructed not to read the
pre-mortem. That needed one new class. Rounds 89, 92 and 99 registered an edit
and never generated it, because a fire-rate precheck at master rules did not
fire. **`unscored`** says that: no point estimate exists, and an unscored round
enters no rejection count and neither breaks nor extends a run, as an accept
does not. A round whose control missed an assay but whose two arms were both
generated is not unscored. It has a point estimate, so its sign decides, as
round 79's already did.

One label disagrees with its round document. **Round 100 calls itself
`noise-floor` while saying its primary "pointed the wrong way"**: the ratio of
ratios read 1.015 against a registered fall. The criterion is the sign, so it is
labelled `idea-defect`, as rounds 74 and 85 were.

### The endpoint

**Population:** the 22 of the 25 rounds whose primary was scored (the three
`unscored` rounds are out, because a precheck that stops a round tests no idea).
Three of the 22 are idea-defects: rounds 74, 85 and 100.

**Primary:** a one-sided Fisher exact test on the 2×2 of *the pre-mortem names
`idea-defect`* against *the round ended `idea-defect`*, testing for a positive
association. It is read two ways:

- **majority:** the panel's majority class is `idea-defect`;
- **any vote:** at least one member said `idea-defect`.

The second reading exists because the consequential outcome here is closing
[#26], so an ambiguous pre-mortem is counted in the direction that keeps it open.

**What the endpoint can and cannot detect, computed before any call.** With
three idea-defects in 22 rounds, a single correct call cannot reach 0.05 even
with no false alarm (p = 3/22 = 0.136). Two correct calls with none wrong read
p = 0.013, two correct with one wrong 0.038, and two correct with two wrong
0.073. So "callable" means the author named the wrong-direction failure in
advance at least twice, and rarely named it otherwise.

### The decision, fixed now

- **Callable** if either reading gives p < 0.05. [#26] stays open, and its next
  step is a prospective test: a blind refutation panel run on each new
  registration, scored the same way. A filter that the author can apply has
  something for a panel to apply.
- **Not callable** if both readings give p ≥ 0.05. [#26] is closed as not
  planned, citing this unit. The revisit rule `classify.py` computes, the current
  run of weak-idea rejections exceeding the archive's longest, stays as the
  condition for reopening it.

**Secondary, descriptive, and deciding nothing:** the full confusion table of
predicted against outcome class over all 25 rounds.

### This author's prediction

**The pre-mortems will name `idea-defect` at most once among the three rounds
that ended that way.** An author who expected the sign to go the wrong way
would not have registered the edit, so the pre-mortem is written by someone who
has already bet against that class. If that is right, the test measures the bet
rather than foresight. That is also what #26's panel would have to beat: a
reader who does not share the bet.

## Results

*Nothing above this line was computed from a panel call. Everything below it
was.*

[#26]: https://github.com/JordanMPDS/laconic/issues/26
