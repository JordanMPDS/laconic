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

Runs the four eval cases (`decision`, `walkthrough`, `destructive`, `badnews`)
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

`evals/bench/` runs the actual benchmark: 320 single-turn calls (8 cases × 5 reps
× 2 models × 4 arms — baseline, a terse-only control, a synthetic word-compression
foil, and laconic), scored on compression, readability, trap-avoidance, and a
deterministic never-cut safety check. Full methodology, every honesty note, and
every table: [`evals/results/2026-07-30-benchmark.md`](evals/results/2026-07-30-benchmark.md).

**The result is mixed — read both halves.** Median output tokens are **15% below
baseline on Sonnet (740 vs 874) but 5% *above* baseline on Haiku (618 vs 588)**:
the compression this plugin claims holds on the stronger model and does not on
the weaker one. Laconic also costs *more* per call than baseline on both models
($0.0159 vs $0.0139 haiku, $0.0674 vs $0.0605 sonnet) — the injected rules' own
token cost, reported net rather than left out.

**Where laconic wins:** trap pass rates rise monotonically across the four arms
— baseline 64%, terse-control 68%, word-compression 72%, laconic **76%** (80
judgments per arm; laconic 68% on haiku, 85% on sonnet) — the largest single
result in the benchmark. The deterministic never-cut safety check held
everywhere laconic was tested: 0 failures across 80 checked responses.

Readability violations scored 0.0 median for every arm, including the
word-compression foil, so the readability axis produced no usable signal in
this run — the foil never degraded its prose enough to give the detector
anything to catch.

These are single-turn `--append-system-prompt` calls, not multi-turn sessions,
so the per-call cost above **overstates** what a real session pays once the
first turn's cache write becomes a cache read.

```bash
python3 evals/bench/run.py      # generate (~320 calls, 1.5-2 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```
