# laconic

Terse responses that stay readable. Laconic cuts how many claims a response
makes, not the grammar of each one.

Word-level compression — dropped articles, abbreviations, arrows standing in for
conjunctions — buys its tokens by making you reassemble the sentence before you
can trust it. Drop the conjunction out of a conditional ("bump the limit if the
curve is flat") and the advice changes meaning.

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

Restart Claude Code, then run `/laconic full`. With no level set, laconic
injects nothing. To skip that step, set `LACONIC_DEFAULT` — see
[Configuration](docs/configuration.md#default-level).

## Levels

Cumulative. All three keep complete sentences, real articles, and real
conjunctions — see [Never cut](#never-cut).

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
a report, walkthrough, or explanation you asked for gets full detail.

**The levels do not produce three measurably different lengths.** Across 330
generations, `full` was not shorter than `lite` on either model, and `ultra`
shortened the model's tool turns more than its answer. Pick by which cuts you
want — [`evals/results/2026-07-31-levels.md`](evals/results/2026-07-31-levels.md).

## Never cut

Every level, including `ultra`:

- Code, config, commands, and error strings — verbatim and complete.
- Security warnings, and the reasoning that makes them actionable.
- Confirmation before destructive or irreversible actions, naming exactly what
  will be affected, from the material you were pointed at rather than by
  telling you to go check.
- Anything you asked to have explained: "why", "how", "walk me through", "explain".
- Ordered instructions: every step, and the words that fix their order.
- Bad news: a failure, a broken test, a limit hit, a thing not done.
- Uncertainty that changes what you should do.

## Turning it off

```
/laconic off
```

Both hooks — `SessionStart` and `UserPromptSubmit` — then exit without emitting
anything. No lingering state.

To turn it off in one repository only, see
[Per-project level](docs/configuration.md#per-project-level).

## Configuration

[`docs/configuration.md`](docs/configuration.md) covers the three settings:

- **[Per-project level](docs/configuration.md#per-project-level)** — `/laconic ultra project` writes a flag under the repository that overrides the machine-wide one, `off` included.
- **[Default level](docs/configuration.md#default-level)** — `LACONIC_DEFAULT` in `settings.json` seeds the machine flag so a fresh install needs no `/laconic full`.
- **[Statusline badge](docs/configuration.md#statusline-badge)** — an optional `[LACONIC]` badge under the input box, colored by level.

## Other agents

Agents without a hook system take a static instructions file. `rules/dist/` holds
one pre-sliced file per level — copy
[`laconic-lite.md`](rules/dist/laconic-lite.md),
[`laconic-full.md`](rules/dist/laconic-full.md), or
[`laconic-ultra.md`](rules/dist/laconic-ultra.md) into your agent's rules path.

Do not copy `rules/laconic.md` itself. It carries level markers the hook slices
at load time, so copied whole it delivers all three levels at once.

Destinations per agent, and what a static file gives up against the hook, are in
[`docs/other-agents.md`](docs/other-agents.md).

## Requirements

- macOS, Linux, WSL, Git Bash: bash 3.2+ and POSIX awk.
- Native Windows: Windows PowerShell 5.1+, which ships with Windows 10 (1607+),
  Windows 11, and Server 2016+.
- No `jq`, no node, no `pwsh` install.

Both implementations share one flag file, so a machine used from both WSL and
native Windows keeps a single level. CI runs the bash suites on `ubuntu-latest`
and the PowerShell suite on `windows-latest`, including a check that each
implementation reads a flag the other wrote.

## Benchmark

440 API calls: 11 cases × 5 reps × 2 models × 4 arms — baseline, a terse-only
control, a synthetic word-compression foil, and laconic. Scored offline on
compression, readability, answer quality, and a deterministic never-cut safety
check.

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | answers correct | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| **laconic** | **-33%** | +1% | **-29%** | **35** | 27 / 30 | 2 / 50 |
| terse-control | -11% | +3% | -13% | 50 | 27 / 30 | 1 / 50 |
| word-compression | +3% | +4% | -13% | 60 | 27 / 30 | 0 / 50 |
| baseline | 0% | 0% | 0% | 60 | 28 / 30 | 0 / 50 |

The readability column was published as 0 / 9 / 11 / 1 until 2026-08-03, when
the detector was corrected. It had been skipping bullets, numbered steps and
blockquotes — the positions where the forbidden arrow most often appears, and
three of the ones `rules/laconic.md` names. Laconic is still the cleanest arm,
on 7 affected responses of 110 against baseline's 16, but it does not score 0.
See [`docs/benchmark.md`](docs/benchmark.md#readability--the-whole-point).

Every figure here is a `full`-level figure. Per-case tables, cost, and what each
number does and does not support are in
[`docs/benchmark.md`](docs/benchmark.md); the method and every honesty note are
in
[`evals/results/2026-07-31-benchmark.md`](evals/results/2026-07-31-benchmark.md).

**These numbers do not say a reader prefers the result.** A blind judge asked
exactly that, over 130 comparisons, did not prefer laconic to baseline — and its
own length and position biases came out larger than the gap between the arms, so
that run supports no conclusion either way:
[`evals/results/2026-08-01-preference.md`](evals/results/2026-08-01-preference.md).

## How this differs from caveman

[`caveman`](https://github.com/JuliusBrussee/caveman) is a separate project by a
different author. It compresses at the word level, dropping articles and
conjunctions and abbreviating common terms; laconic compresses at the claim
level. Caveman goes further on token count, laconic keeps output that survives a
conditional, so pick by which you want.

`evals/run.sh`'s two-arm design — same prompt, with and without the rules, read
side by side — is a direct descendant of caveman's three-arm eval harness.
Credit to that project for the approach.

## Development

Test commands, the eval harness, and how to reproduce the benchmark:
[`docs/development.md`](docs/development.md).
