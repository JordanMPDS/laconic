# The deliverable the harness could not see

[#150]'s status comment names the half of the issue nothing has tested:

> the second half of this issue — whether the rules govern **files the model
> authors** as deliverables, which nothing has tested yet. That second question
> is untouched by all three attempts above, and it is where the harm reported
> here actually happened.

It was untouched for a mechanical reason, not an analytical one. **The harness
deleted the evidence.**

## What was in the way

`run.py` gives every generation a throwaway workspace: a `mkdtemp`, the case's
`fixture/` copied into it, the model pointed at it. When the call returns the
directory is removed. Every file the model wrote went with it, unread — nothing
in the snapshot, nothing on disk, no trace anywhere.

So a case whose deliverable is an authored document could not be written. Not
because the grading was hard, but because there was nothing left to grade by the
time anything looked.

## The change

`tree_state()` checksums the workspace before the call. `workspace_diff()`
compares it after and records what changed, into a new `artifacts` field on the
run record. Files created, files edited, files deleted.

Three things it refuses to do quietly, because each would misreport a
deliverable:

- A file that is not valid UTF-8 records `binary` and its size, rather than
  being dropped. An absent entry would read as *"the model wrote nothing"*,
  which is the one claim this must never make by accident.
- A file over 40,000 bytes is stored truncated and carries `truncated` plus its
  real size.
- More than 20 changed files stores the first 20 and records the true count
  beside the names of the ones it left out.

The retry path used to be a second copy of the copy-and-call block. Capture
would have made it a third place to keep in sync, so both attempts now go
through one `attempt()`. `tests/test_bench.py` had a guard asserting the two
sites spelled the delivery fallback identically; that guard is now structural —
there is exactly one call site, so a retry cannot disagree with itself — which
is the stronger form of the same invariant.

## The pilot, one call

A throwaway case outside `evals/cases/`, run through the real CLI on haiku:

> Write a file called NOTE.md in this directory containing one sentence that
> says what config.json sets the timeout to. Then reply with just the word done.

The recorded run:

    text:      "done"
    tools:     ["Bash", "Read", "Write"]
    artifacts: {"NOTE.md": {"new": true, "bytes": 51,
                "text": "config.json sets the timeout to 4500 milliseconds.\n"}}

**That single run is the argument.** Every metric the loop has ever scored reads
`text`. On this run `text` is one word, which `output_tokens` scores as
maximally terse and `one_turn` scores as a grounded answer that read its
fixture. The work product — the thing the user actually asked for — is 51 bytes
the instrument could not see. [#150]'s reported harm is 1,335 words in an
authored document, and it would have been just as invisible.

## What this does not establish

**Nothing is graded.** No gate reads `artifacts`, `report.py` and `judge.py` do
not know it exists, and no case in `evals/cases/` produces one. This is the
enabling change and only that.

**No stored round carries the field**, which is deliberate and is the reason not
to build a metric on it yet. A gate with no measured null rejects on whatever
its first round happens to do; `turns` went live only because `num_turns` could
be re-scored offline across rounds 05 to 26 first. The `tools` list [#142] added
has sat unscored for the same reason and is the precedent being followed. The
field accumulates first.

**And it says nothing about [#150]'s claim.** Whether *"Length scales to the
request"* reads as a length exemption is still unmeasured. What changed is that
the question is now askable: a case can be written whose deliverable is a
document, and the document survives the run.

## What the next unit needs to decide

- **What grades an authored file.** The never-cut check is a substring test and
  the quality judge reads `text`. Neither reaches a file today.
- **Whether the case belongs in `evals/cases/`.** Adding one changes
  `cases_cksum` for every round that includes it, and the [#209] mixture rule
  already refuses a cell that mixes edited and non-edited answers — a case whose
  every answer writes a file is uniform rather than mixed, but that wants
  checking before it ships rather than after.
- **Snapshot size.** Artifacts are stored text. The caps bound one run; a
  round-wide arm on a document case would still be the largest snapshot the
  repository holds.

[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#209]: https://github.com/JordanMPDS/laconic/issues/209
