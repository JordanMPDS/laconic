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

1100 API calls: 22 cases x 5 reps x 2 models x 5 arms — baseline, a terse-only
control, a synthetic word-compression foil, Claude Code's own built-in `Concise`
output style, and laconic. Scored offline on compression, readability, latency
and cost, with a deterministic never-cut safety check and a blind judge for
answer quality.

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | quality pass rate | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| **laconic** | -32% | -9% | -32% | **66** | 59.7% | 0 / 50 † |
| concise-style | **-55%** | **-12%** | **-52%** | 113 | 58.4% | 3 / 50 † |
| terse-control | -3% | -2% | 0% | 107 | **71.9%** | 1 / 50 |
| word-compression | +7% | +5% | +6% | 176 | 70.3% | 1 / 50 |
| baseline | 0% | 0% | 0% | 134 | 68.1% | 0 / 50 |

† **The never-cut column is not a gap between laconic and `concise-style`.**
Both figures are five-rep draws, and re-measuring the only two cells they differ
on at n = 20 a side puts the two arms level at 4 failures of 40 each. See below.

**What laconic wins.** It is the cleanest arm on readability by a wide margin —
66 violations against baseline's 134, and 31 of 220 responses carrying one
against baseline's 49. It is the cheapest arm per call on Sonnet, $0.0636
against baseline's $0.1099, despite not being the shortest. And it leads the
rule-adherence cases, 63.3% against baseline's 43.3%, which is the grading that
tests the style prohibitions the rules actually state.

**What it does not win, and this is the important half.** Laconic does not beat
baseline on answer quality: 59.7% against 68.1%. That gap is z = -1.45 and does
not reach significance, so it is not a demonstrated regression — but it is not a
win either, and nothing in this table supports a claim that the rules make
answers better. Against `terse-control` the 12.2-point gap **is** significant
(z = -2.14): a plain "Answer concisely." instruction produced better answers on
the quality-graded cases than the whole rule file did.

**Claude Code now ships a competitor, and on compression it wins.** The built-in
`Concise` output style cuts Sonnet output 55% against laconic's 32%, at half the
latency, and is statistically indistinguishable from laconic on answer quality
(58.4% against 59.7%, z = +0.22). **Laconic's remaining edge over it is prose
quality, and not safety** — 113 readability violations against laconic's 66.

The never-cut column above was previously read as a safety edge, and it is not
one. Round 21's three `concise-style` failures were all on Haiku and all in two
cells, `conditional` and `destructive`. Re-running exactly those two cells on
2026-08-24 in one matched interleaved batch — `baseline`, `concise-style` and
`laconic`, n = 20 a side, 120 generations on one CLI build — put the two
compression arms level at 4 failures of 40 each (Fisher p = 1.0), with laconic
the worse of the two on `destructive`, 4 of 20 against 2 of 20. Laconic's 0 in
the table is a five-rep draw. Under the blind judge that case separates nothing
at all on Haiku: every arm fails 20 of 20. The full tables are in
[docs/benchmark.md](docs/benchmark.md#compression).

If you want maximum compression, the built-in style is free and already
installed.

**One column contradicts another, and the judge is the one to believe.** On
`destructive`, laconic has a clean never-cut sheet and still passes only 2 of 10
under the blind judge. The never-cut check is a substring test: it confirms the
response names the `sessions` table, which laconic always does. The judge also
applies the criterion added in
[#18](https://github.com/JordanMPDS/laconic/issues/18), which fails a response
that names the affected table and then tells the user it is safe. Laconic is
producing that shape. Read the never-cut column as a floor, not as evidence that
the safety contract holds.

**`report.py` exits 1 on the committed snapshot.** 18 case/model gates fail on
laconic's readability, and the samples are dominated by arrows — the arm that
ships the no-arrows rule is breaking it, most heavily on the design cases
(`design-retry`/sonnet alone carries 13 violations at a median of 3 per
response).

Every figure is a `full`-level figure over all 22 cases, from
`evals/snapshots/loop/round-21.json` at `rules_cksum` 1830906901, the rules this
repository ships. The three control arms were generated eleven days before the
two new ones and on an older CLI, so read the comparison against baseline with
that confound in mind; laconic against `concise-style` is the clean one.
Per-case tables, cost, and what each number does and does not support are in
[`docs/benchmark.md`](docs/benchmark.md).

**These numbers do not say a reader prefers the result.** A blind judge asked
exactly that, over 130 comparisons of an archived arm, did not prefer laconic to
baseline — and its own length and position biases came out larger than the gap
between the arms, so that run supports no conclusion either way:
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
