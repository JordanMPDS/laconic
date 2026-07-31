# laconic

Terse responses that stay readable. Laconic cuts how many claims a response
makes, not the grammar of each one.

## The problem

Default responses pad: preamble, restated questions, closing offers, options
nobody asked for. The usual fix for this is to delete words — drop articles,
abbreviate, swap conjunctions for arrows — which leaves prose you have to
reassemble in your head before you can trust it. Dropping a conjunction out of
a conditional ("bump the limit if the curve is flat") turns advice ambiguous,
which is a correctness bug, not a style preference.

## Install

```bash
/plugin marketplace add JordanMPDS/laconic
/plugin install laconic@laconic
/laconic full
```

Or install from a clone, which is also how you'd develop against it:

```bash
git clone https://github.com/JordanMPDS/laconic ~/projects/laconic
ln -s ~/projects/laconic ~/.claude/skills/laconic
```

Restart Claude Code, then run `/laconic full`.

With no level set, laconic is completely inert — it injects nothing until you
opt in. See [Making it permanent](#making-it-permanent) to skip the manual step.

## Levels

Each level adds cuts on top of the one before it. Every level keeps complete
sentences, real articles, and real conjunctions — see [Never cut](#never-cut).

| Level | Cuts |
| --- | --- |
| `lite` | Ceremony: preamble, pleasantries, closing offers, stacked hedging, recap of work already visible in the diff. |
| `full` | Also unrequested substance: leads with the answer, one recommendation instead of a survey, no unrequested alternatives, no unasked next-steps list. |
| `ultra` | Also compresses to the result: a decision, a value, a `file:line`, a yes or no — reasoning only where withholding it would make the answer unusable or unsafe. |

Worked example — *"Our deploy failed with an OOM kill on the worker. Should I
bump the memory limit?"*

| Level | Response |
| --- | --- |
| `lite` | "Bump it, but check the trend first. An OOM kill at a steady memory ceiling means the limit is too low; a climbing curve means a leak, and a bigger limit only delays the next kill. `kubectl top pod` over a few minutes tells you which one you have." |
| `full` | "Check the trend first. If memory sits at a steady ceiling, raise the limit; if it is climbing, you have a leak and a bigger limit only delays the next kill. Watch `kubectl top pod` for a few minutes." |
| `ultra` | "Only if memory is flat, not climbing. Check `kubectl top pod` first." |

Ultra kept the conditional because dropping it would give wrong advice half the time.

Length always scales to the request: a yes/no question gets a word or a line
at any level; a report, walkthrough, or explanation you asked for gets full
detail regardless of level. Laconic governs volunteered content — it never
truncates requested content.

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

Off means off: every hook — `SessionStart`, `SubagentStart`, and
`UserPromptSubmit` — exits without emitting anything. No rules get injected,
and the `LACONIC MODE ACTIVE` reminder line stops appearing on the next turn.
There is no lingering state to work around.

## Making it permanent

By default laconic is opt-in per machine: with no flag file and no
`LACONIC_DEFAULT` set, it does nothing at all. To skip the `/laconic full`
step on every fresh install, set a default in the `env` block of
`settings.json`:

```json
{
  "env": {
    "LACONIC_DEFAULT": "full"
  }
}
```

Valid values are `lite`, `full`, `ultra`, and `off`. An invalid value is
rejected outright and no flag file gets created, so a typo can't silently
brick the plugin.

## Optional: statusline badge

`hooks/laconic-statusline.sh` prints a small `[LACONIC]` badge reflecting the
active level. It ships with the plugin but is not wired up by default — add it
to `settings.json` to opt in, pointing at wherever the plugin actually landed
on your machine. Find that path first:

```bash
# marketplace install
ls $HOME/.claude/plugins/cache/laconic/laconic/*/hooks/laconic-statusline.sh
# local skills-dir install
ls $HOME/.claude/skills/laconic/hooks/laconic-statusline.sh
```

A marketplace install resolves under a version/commit-specific directory that
changes on every update, so re-check the path after updating the plugin. Then
add it to `settings.json`, substituting the path you found for
`<path-to-laconic>`:

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
- No native-Windows PowerShell port exists yet. On Windows, run it under WSL or
  Git Bash.

## How this differs from caveman

[`caveman`](https://github.com/JuliusBrussee/caveman), a separate project by a
different author, compresses at the word level: it drops articles and
conjunctions and abbreviates common terms, which is how it reaches its token
savings. Laconic compresses at the claim level: it removes whole sentences and
leaves the ones that remain as ordinary prose.

They optimize for different things, so pick by which you want. Caveman goes
further on token count. Laconic keeps output that reads like normal writing,
which matters most for conditional advice, where a dropped conjunction changes
the meaning.

`evals/run.sh`'s two-arm design — same prompt, with and without the rules,
read side by side — is a direct descendant of caveman's three-arm eval
harness. Credit to that project for the approach.

## Development

```bash
bash tests/test_rules.sh && bash tests/test_laconic.sh \
  && bash tests/test_evals_layout.sh \
  && python3 tests/test_metrics.py && python3 tests/test_bench.py \
  && claude plugin validate . --strict \
  && claude plugin validate .claude-plugin/plugin.json --strict
```

Unit tests for the marker contract in `rules/laconic.md` and the hook script's
behavior — level whitelist, off switch, the write guard against a symlinked
flag file. No framework, bash 3.2-safe. `claude plugin validate .` resolves the
marketplace manifest and does not check skills or commands; pointing it at
`.claude-plugin/plugin.json` directly closes that gap.

```bash
./evals/run.sh full
```

Runs all eight eval cases (`badnews`, `code-fidelity`, `conditional`, `decision`,
`destructive`, `floor`, `ordered-steps`, `walkthrough`)
with and without the rules, writing paired output under
`evals/scratch/<level>/<case>.md` for you to read side by side. Grading
criteria and the trap each case is checking for are in `evals/CRITERIA.md`.
These are single-sample, cheapest-model runs meant to catch regressions in the
rule set, not a benchmark.

### End-to-end check

The unit and eval suites exercise the hook script directly; this checks the
real plugin in a live session, which is the only place the failure it guards
against (a mode that keeps injecting after being switched off) would show up.

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
never-cut safety check. Full method, every honesty note, every correction, and
every table: [`evals/results/2026-07-31-benchmark.md`](evals/results/2026-07-31-benchmark.md).

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | never-cut failures |
|---|--:|--:|--:|--:|--:|
| **laconic** | **-28%** | +5% | **-25%** | **0** | 2 / 50 |
| terse-control | +1% | -3% | -1% | 5 | 1 / 50 |
| word-compression | -7% | +7% | -16% | 4 | 0 / 50 |
| baseline | 0% | 0% | 0% | 0 | 0 / 50 |

Two of those columns are bad news for laconic and are printed at the same size
as the good ones: it does not compress on Haiku, and it is the only arm that
fails the safety gate on this snapshot.

### Compression

Median output tokens per case, n=5 per cell. The comparison that matters is
laconic against `terse-control` — a plain "be terse, no preamble, no closing
offers" instruction — not against baseline, because that isolates the rule set
from merely asking for brevity.

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

`destructive` is the one case that gets longer, and that is the design working:
naming exactly what a `DROP TABLE` affects is never-cut content, so laconic has
nothing to trim there.

<details>
<summary><strong>Haiku 4.5 — no compression</strong></summary>

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

The aggregation convention flips this result's sign, so no Haiku compression
claim is made in either direction. The table above is a median of per-case
medians; a flat median over the 40 raw runs gives 604 → 552 (−9%). Sonnet
compresses on both estimators, Haiku does not agree with itself.

</details>

Dispersion is published per arm and model in the results doc. On Sonnet,
laconic's stdev (119) is the lowest of the four arms and its max (832) sits
below baseline's band, so the gap is not one or two short outliers dragging a
median.

### Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | violations | responses affected (of 80) |
|---|--:|--:|
| baseline | 0 | 0 |
| terse-control | 5 | 3 |
| word-compression | 4 | 3 |
| **laconic** | **0** | **0** |

**This number used to be 16, and that was a real defect.** The 2026-07-30 run
found laconic violating its own no-arrows rule more than any other arm — more
than a foil that had been told outright to use arrows instead of conjunctions.
The rule said "no arrows standing in for conjunctions in running prose", and
every single violation went through one of the two openings that phrasing left:
a sequence arrow is not a conjunction, and a `**Bolded label**: ...` line does
not read as running prose. The rule now bans arrows anywhere in a sentence and
names those forms. Re-measured with the **unchanged** detector, the arms that
still violate are the two whose instructions did not change.

### Cost, reported net

The injected rules cost tokens of their own, so laconic costs **more per call
than baseline on both models** even where it produces fewer output tokens.

| median USD per call | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0139 | 0.0605 |
| laconic | 0.0164 | 0.0653 |

These are single-turn `--append-system-prompt` calls, not multi-turn sessions,
so this **overstates** what a real session pays once the first turn's cache
write becomes a cache read on every turn after it.

### The gate is red

`report.py` exits 1 against the committed snapshot with 2 never-cut failures out
of the 50 responses per arm that carry a keyword list to verify by design. Both
were read, and both are real: one `destructive` response told the user to go
look for foreign keys instead of naming the two tables in the fixture in front
of it, and one `conditional` response never diagnosed the leak.

The difference from the previous run's 0 is not statistically distinguishable
(Fisher p = 0.50) and `terse-control` scores 1 on the same snapshot, but it is
not zero and it is not reported as zero. The gate was not loosened to turn it
green.

### What this benchmark does not claim

- **No trap-based claim.** The cases that discriminate at all are contaminated:
  laconic's rule text reaches the treatment arm's own prompt, overlaps two of
  the five discriminating cases almost verbatim, and two more of those five
  grade adherence to that same rule text. The trap table is still published, but
  it is not evidence for the plugin.
- **Never-cut coverage is 50 of 80 responses per arm,** not 80. Three cases
  carry an empty keyword list and are not checked at all — their lists were
  emptied after an earlier `"if"` keyword turned out to match "different",
  "specify" and "identify", making the assertion vacuous.
- **n=5 per cell, two models, one vendor.** Differences smaller than the
  published stdev are not claims, and nothing here says anything about how these
  rules behave on a non-Claude model.
- **The judge is a Claude model grading Claude outputs,** blind to arm with the
  rules text withheld. Still not an independent evaluator.

Reproduce:

```bash
python3 evals/bench/run.py      # generate (~320 calls, 1.5-2 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```
