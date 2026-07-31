# laconic

Terse responses that stay readable. Laconic cuts how many claims a response
makes, not the grammar of each one.

Word-level compression — dropped articles, abbreviations, arrows standing in for
conjunctions — buys its token savings by making you reassemble the sentence
before you can trust it. Drop the conjunction out of a conditional ("bump the
limit if the curve is flat") and the advice changes meaning. Laconic deletes
whole claims instead and leaves the survivors as ordinary English.

## Install

```bash
/plugin marketplace add JordanMPDS/laconic
/plugin install laconic@laconic
/laconic full
```

From a clone, which is also how you develop against it:

```bash
git clone https://github.com/JordanMPDS/laconic ~/projects/laconic
ln -s ~/projects/laconic ~/.claude/skills/laconic
```

Restart Claude Code, then run `/laconic full`. With no level set, laconic is
inert — it injects nothing until you opt in. See
[Default level](#default-level) to skip the manual step.

## Levels

Cumulative — each level adds cuts on top of the one before it. All three keep
complete sentences, real articles, and real conjunctions. See
[Never cut](#never-cut).

| Level | Cuts |
| --- | --- |
| `lite` | Ceremony: preamble, pleasantries, closing offers, stacked hedging, recap of work already visible in the diff. |
| `full` | Also unrequested substance: leads with the answer, one recommendation instead of a survey, no unrequested alternatives, no unasked next-steps list. |
| `ultra` | Also compresses to the result: a decision, a value, a `file:line`, a yes or no — reasoning only where withholding it would make the answer unusable or unsafe. |

*"Our deploy failed with an OOM kill on the worker. Should I bump the memory
limit?"*

| Level | Response |
| --- | --- |
| `lite` | "Bump it, but check the trend first. An OOM kill at a steady memory ceiling means the limit is too low; a climbing curve means a leak, and a bigger limit only delays the next kill. `kubectl top pod` over a few minutes tells you which one you have." |
| `full` | "Check the trend first. If memory sits at a steady ceiling, raise the limit; if it is climbing, you have a leak and a bigger limit only delays the next kill. Watch `kubectl top pod` for a few minutes." |
| `ultra` | "Only if memory is flat, not climbing. Check `kubectl top pod` first." |

Ultra kept the conditional because dropping it would give wrong advice half the
time.

Length scales to the request at every level: a yes/no question gets a line, and
a report, walkthrough, or explanation you asked for gets full detail. Laconic
governs volunteered content — it never truncates requested content.

## Never cut

Every level, including `ultra`:

- Code, config, commands, and error strings — verbatim and complete.
- Security warnings, and the reasoning that makes them actionable.
- Confirmation before destructive or irreversible actions, including exactly
  what will be affected.
- Anything you asked to have explained: "why", "how", "walk me through", "explain".
- Ordered instructions: every step, and the words that fix their order.
- Bad news: a failure, a broken test, a limit hit, a thing not done.
- Uncertainty that changes what you should do.

## Turning it off

```
/laconic off
```

Every hook — `SessionStart`, `SubagentStart`, and `UserPromptSubmit` — then
exits without emitting anything, and the `LACONIC MODE ACTIVE` line stops on
the next turn. No lingering state.

## Default level

Laconic is opt-in per machine. To skip `/laconic full` on a fresh install, set
a default in the `env` block of `settings.json`:

```json
{
  "env": {
    "LACONIC_DEFAULT": "full"
  }
}
```

Valid values are `lite`, `full`, `ultra`, and `off`. An invalid value is
rejected and no flag file gets created, so a typo cannot silently brick the
plugin.

## Optional: statusline badge

`hooks/laconic-statusline.sh` prints a small `[LACONIC]` badge with the active
level. It ships with the plugin but is not wired up. Find where the plugin
landed on your machine first:

```bash
# marketplace install
ls $HOME/.claude/plugins/cache/laconic/laconic/*/hooks/laconic-statusline.sh
# local skills-dir install
ls $HOME/.claude/skills/laconic/hooks/laconic-statusline.sh
```

A marketplace install resolves under a version-specific directory that changes
on every update, so re-check the path after updating. Then add it to
`settings.json`, substituting the path you found:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash \"<path-to-laconic>/hooks/laconic-statusline.sh\""
  }
}
```

## Requirements

- bash 3.2+ and POSIX awk. No `jq`, no node.
- No native-Windows PowerShell port exists yet. Run it under WSL or Git Bash.

## How this differs from caveman

[`caveman`](https://github.com/JuliusBrussee/caveman) is a separate project by a
different author. It compresses at the word level, dropping articles and
conjunctions and abbreviating common terms; laconic compresses at the claim
level, removing whole sentences and leaving the rest as ordinary prose. Caveman
goes further on token count, laconic keeps output that survives a conditional,
so pick by which you want.

`evals/run.sh`'s two-arm design — same prompt, with and without the rules, read
side by side — is a direct descendant of caveman's three-arm eval harness.
Credit to that project for the approach.

## Development

```bash
bash tests/test_rules.sh && bash tests/test_laconic.sh \
  && bash tests/test_evals_layout.sh \
  && python3 tests/test_metrics.py && python3 tests/test_bench.py \
  && claude plugin validate . --strict \
  && claude plugin validate .claude-plugin/plugin.json --strict
```

No framework, bash 3.2-safe. Covers the marker contract in `rules/laconic.md`
and the hook script's level whitelist, off switch, and write guard against a
symlinked flag file. `claude plugin validate .` resolves the marketplace
manifest and does not check skills or commands, so the second invocation points
at `.claude-plugin/plugin.json` directly.

```bash
./evals/run.sh full
```

Runs all eight cases (`badnews`, `code-fidelity`, `conditional`, `decision`,
`destructive`, `floor`, `ordered-steps`, `walkthrough`) with and without the
rules, writing paired output under `evals/scratch/<level>/<case>.md` to read
side by side. Grading criteria and the trap each case checks for are in
`evals/CRITERIA.md`. Single-sample, cheapest-model runs for catching rule-set
regressions, not a benchmark.

### End-to-end check

The unit and eval suites drive the hook script directly. This exercises the real
plugin in a live session, the only place the failure it guards against — a mode
that keeps injecting after being switched off — shows up.

In a fresh session:

1. Run `/laconic full`.
2. `cat ~/.claude/.laconic-level` → prints `full`.
3. Ask something ordinary — the response should come back with no preamble
   and no closing offer.
4. Run `/laconic off`.
5. `cat ~/.claude/.laconic-level` → prints `off`.
6. Ask something else — no `LACONIC MODE ACTIVE` line on that turn or after.

## Benchmark

320 single-turn API calls: 8 cases × 5 reps × 2 models × 4 arms — baseline, a
terse-only control, a synthetic word-compression foil, and laconic. Scored
offline on compression, readability, trap-avoidance, and a deterministic
never-cut safety check. Full method, every honesty note, and every table:
[`evals/results/2026-07-31-benchmark.md`](evals/results/2026-07-31-benchmark.md).

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | never-cut failures |
|---|--:|--:|--:|--:|--:|
| **laconic** | **-28%** | +5% | **-25%** | **0** | 2 / 50 |
| terse-control | +1% | -3% | -1% | 5 | 1 / 50 |
| word-compression | -7% | +7% | -16% | 4 | 0 / 50 |
| baseline | 0% | 0% | 0% | 0 | 0 / 50 |

Every column is reported as measured, on both models and all four arms. The
per-case tables and the method notes behind each number follow.

### Compression

Median output tokens per case, n=5 per cell. The comparison that matters is
laconic against `terse-control` — a plain "be terse, no preamble, no closing
offers" instruction — because that isolates the rule set from merely asking for
brevity.

**Sonnet 4.5**

| case | baseline | terse-control | laconic | saved |
|---|--:|--:|--:|--:|
| `walkthrough` | 3701 | 3682 | 1628 | **56%** |
| `floor` | 201 | 220 | 82 | **59%** |
| `ordered-steps` | 1329 | 1630 | 801 | **40%** |
| `decision` | 839 | 786 | 513 | **39%** |
| `code-fidelity` | 307 | 315 | 214 | **30%** |
| `conditional` | 908 | 981 | 740 | 19% |
| `badnews` | 435 | 414 | 372 | 14% |
| `destructive` | 2336 | 2775 | 2462 | **-5%** |
| **median** | **874** | **884** | **626** | **28%** |

`destructive` is the one case that gets longer, which is the design working:
naming exactly what a `DROP TABLE` affects is never-cut content, so laconic has
nothing to trim there.

<details>
<summary><strong>Haiku 4.5</strong></summary>

| case | baseline | terse-control | laconic | saved |
|---|--:|--:|--:|--:|
| `floor` | 266 | 236 | 225 | 15% |
| `badnews` | 469 | 432 | 443 | 6% |
| `conditional` | 956 | 1017 | 911 | 5% |
| `walkthrough` | 1228 | 1008 | 1185 | 4% |
| `code-fidelity` | 425 | 421 | 418 | 2% |
| `decision` | 522 | 506 | 515 | 1% |
| `ordered-steps` | 653 | 636 | 715 | -9% |
| `destructive` | 711 | 791 | 837 | -18% |
| **median** | **588** | **571** | **615** | **-5%** |

Haiku's result depends on the aggregation convention, so no compression claim is
made for it in either direction. The table above is a median of per-case
medians; a flat median over the 40 raw runs gives 604 against 552, a 9% cut.
Sonnet compresses on both estimators, and the Sonnet figures are the ones quoted
above.

</details>

On Sonnet, laconic's stdev (119) is the lowest of the four arms and its max
(832) sits below baseline's band, so the median gap is not one or two short
outliers. Dispersion per arm and model is in the results doc.

### Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | violations | responses affected (of 80) |
|---|--:|--:|
| baseline | 0 | 0 |
| terse-control | 5 | 3 |
| word-compression | 4 | 3 |
| **laconic** | **0** | **0** |

This number was 16 on the 2026-07-30 run. Every violation went through one of
the two openings in the earlier phrasing, "no arrows standing in for
conjunctions in running prose": a sequence arrow is not a conjunction, and a
`**Bolded label**: ...` line does not read as running prose. The rule now bans
arrows anywhere in a sentence and names both forms. Re-measured with the
**unchanged** detector, the count is 0, and the arms that still violate are the
two whose instructions did not change.

### Cost, reported net

The injected rules cost tokens of their own, so the net per-call cost sits
slightly above baseline on both models even where output tokens drop.

| median USD per call | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0139 | 0.0605 |
| laconic | 0.0164 | 0.0653 |

These are single-turn `--append-system-prompt` calls, not multi-turn sessions,
so this **overstates** what a real session pays once the first turn's cache
write becomes a cache read on every turn after it.

### Never-cut check

`report.py` gates on the never-cut contract and exits 1 against the committed
snapshot: 2 failures out of the 50 responses per arm that carry a keyword list
to verify by design. Both were read and confirmed. One `destructive` response
pointed at foreign keys generally rather than naming the two tables in the
fixture, and one `conditional` response stopped short of diagnosing the leak.

The difference from the previous run's 0 is not statistically distinguishable
(Fisher p = 0.50), and `terse-control` scores 1 on the same snapshot. The
threshold is unchanged from the run that passed it.

### Scope

What the numbers cover:

- **The compression, readability, latency and cost figures are the load-bearing
  ones.** They come from deterministic offline scoring of the raw responses.
- **The trap table is published as method detail rather than as a claim.**
  Laconic's rule text reaches the treatment arm's own prompt, overlaps two of
  the five discriminating cases almost verbatim, and two more of those five
  grade adherence to that same rule text.
- **Never-cut coverage is 50 of 80 responses per arm.** Three cases carry an
  empty keyword list and are not checked — those lists were emptied once an
  earlier `"if"` keyword turned out to match "different", "specify" and
  "identify", which made the assertion pass regardless of content.
- **n=5 per cell, two models, one vendor.** Differences smaller than the
  published stdev are treated as noise, and the results speak only to Claude
  models.
- **The judge is a Claude model grading Claude outputs,** blind to arm with the
  rules text withheld. It is not an independent evaluator.

Reproduce:

```bash
python3 evals/bench/run.py      # generate (~320 calls, 1.5-2 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```
