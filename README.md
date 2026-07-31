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

To turn it off in one repository while leaving the rest of the machine alone,
see [Per-project level](#per-project-level).

## Per-project level

Add `project` to any level to scope it to the current repository:

```
/laconic ultra project
```

That writes `.claude/.laconic-level` under the project directory. The machine
flag at `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level` is left untouched,
and `/laconic ultra` without the suffix still writes the machine flag as before.

The project flag wins wherever both exist, `off` included, so a repository where
you want full explanations can opt out of a machine-wide `ultra`:

| Machine flag | Project flag | Active |
| --- | --- | --- |
| `full` | none | `full` |
| `full` | `ultra` | `ultra` |
| `full` | `off` | off |
| none | `lite` | `lite` |
| none | none | inert, unless `LACONIC_DEFAULT` is set |

`/laconic status` reports the active level, which of the two flags it came from,
and that flag's path.

Two things worth knowing before you use it:

- **The file is a personal preference, not a project setting.** Add
  `.claude/.laconic-level` to your `.gitignore` unless your team genuinely wants
  a shared house style.
- **A repository you open can set your level.** The flag is read from the
  project directory, so cloning someone else's repo can change your verbosity or
  switch laconic off. The contents are whitelisted to `lite`, `full`, `ultra`,
  and `off`, so that is the whole blast radius — but it is the same trust model
  as any other file under a project's `.claude/`.

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
plugin. It seeds the machine flag only — it never writes into a repository.

## Optional: statusline badge

A small `[LACONIC]` badge under the input box, colored by level and following
the same project-flag precedence the hook uses. One edit, one time:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash \"$HOME/.claude/laconic-statusline.sh\""
  }
}
```

On native Windows, point at the PowerShell copy instead:

```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\laconic-statusline.ps1\""
  }
}
```

The plugin installs the badge script at that path itself and refreshes it on
every session start, so there is no script to copy and no path to re-check after
an update. Each platform's hook installs its own copy, so a machine used from
both WSL and native Windows ends up with both and neither goes stale. It writes
only while a level is active — with laconic `off`, or with no level ever set, the
hook does nothing at all, including this.

Wiring it into `settings.json` is the one step that cannot be automated, because
Claude Code reads `statusLine` from your settings and a plugin cannot register
one. `claude plugin validate` rejects the field outright:

```
❯ statusLine: Unknown field 'statusLine'. Claude Code ignores it at load time.
```

For the same reason, do not write `${CLAUDE_PLUGIN_ROOT}` into the command.
Claude Code substitutes that variable only where it has a plugin context, and a
`statusLine` command has none, so using it raises an error that goes to the debug
log and is swallowed. The badge would render nothing and the terminal would show
no message at all.

## Other agents: copy a rule file

Agents without a hook system take a static instructions file. `rules/dist/` holds
one pre-sliced file per level — copy the one you want:

| Level | File |
| --- | --- |
| `lite` | [`rules/dist/laconic-lite.md`](rules/dist/laconic-lite.md) |
| `full` | [`rules/dist/laconic-full.md`](rules/dist/laconic-full.md) |
| `ultra` | [`rules/dist/laconic-ultra.md`](rules/dist/laconic-ultra.md) |

```bash
curl -fsSL https://raw.githubusercontent.com/JordanMPDS/laconic/master/rules/dist/laconic-full.md \
  > .github/copilot-instructions.md
```

Conventional destinations, by agent:

| Agent | Path |
| --- | --- |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cursor | `.cursor/rules/laconic.mdc` |
| Windsurf | `.windsurf/rules/laconic.md` |
| Cline | `.clinerules/laconic.md` |
| opencode | `.opencode/AGENTS.md` |
| Anything reading `AGENTS.md` | `AGENTS.md` |

Check your agent's own documentation before trusting a path — these follow the
locations [caveman's installer](https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md)
writes to, not a spec. Cursor's `.mdc` rules also take YAML frontmatter that
controls when a rule applies; without it the file may not be always-on.

**Do not copy `rules/laconic.md` itself.** It carries `<!-- level:lite -->`
markers and the hook slices it at load time. Copied whole it delivers all three
level blocks at once, and they contradict each other — lite keeps full reasoning
and trade-offs, ultra cuts to the answer alone.

### What you give up

A static file is the rule text and nothing else. Specifically:

- **No `/laconic` switching.** The level is whichever file you copied. Changing it
  means copying a different one.
- **No off switch.** Delete the file. There is no `/laconic off`, which is the
  guarantee the hook exists to provide.
- **No per-turn reminder**, so nothing reinforces the rules as context fills.

Gemini CLI, Codex CLI, Copilot, and Cursor all have shell-command hooks that could
run `laconic.sh` and `laconic.ps1` properly. That work is tracked in
[#13](https://github.com/JordanMPDS/laconic/issues/13),
[#14](https://github.com/JordanMPDS/laconic/issues/14),
[#15](https://github.com/JordanMPDS/laconic/issues/15), and
[#16](https://github.com/JordanMPDS/laconic/issues/16) — until one lands, the copied
file is what those agents get too.

Regenerate after editing `rules/laconic.md`:

```bash
bash tools/build-rules.sh
```

`tests/test_rules.sh` fails if the committed copies are stale, since a drifted copy
sitting in someone's `.cursor/rules/` gives no sign it went out of date.

## Requirements

- macOS, Linux, WSL, Git Bash: bash 3.2+ and POSIX awk.
- Native Windows: Windows PowerShell 5.1+, which ships with Windows 10 (1607+),
  Windows 11, and Server 2016+.
- No `jq`, no node, no `pwsh` install. Both hooks use only what the OS already
  provides, and `hooks.json` picks the right one per platform.

The two implementations share one flag file, so a machine used from both WSL and
native Windows keeps a single level. CI runs the bash suites on `ubuntu-latest`
and the PowerShell suite on `windows-latest` for every push, including an
explicit check that each implementation reads a flag the other wrote.

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

The PowerShell hook has its own suite, running the same numbered cases against
`hooks/laconic.ps1`. It needs a Windows host, so CI is the normal place to see
it; on Windows you can run it directly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests\test_laconic.ps1
```

```bash
./evals/run.sh full
```

Runs all eleven cases (`badnews`, `code-fidelity`, `conditional`, `decision`,
`destructive`, `fail-open`, `floor`, `ordered-steps`, `silent-success`,
`stale-cache`, `walkthrough`) with and without the rules, writing paired output
under `evals/scratch/<level>/<case>.md` to read side by side. Grading criteria
and the trap each case checks for are in `evals/CRITERIA.md`. Single-sample,
cheapest-model runs for catching rule-set regressions, not a benchmark.

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

For the project flag, in a repository you do not mind writing a file into:

1. Run `/laconic full` first, so the machine flag is set and there is something
   for the project flag to override.
2. Run `/laconic ultra project`.
3. Confirm `cat .claude/.laconic-level` prints `ultra` and
   `cat ~/.claude/.laconic-level` still prints `full`.
4. Ask something ordinary and confirm the response is at `ultra`, not `full`.
5. Delete `.claude/.laconic-level`, start a fresh session, and confirm the level
   is back to `full`.

## Benchmark

440 API calls: 11 cases × 5 reps × 2 models × 4 arms — baseline, a terse-only
control, a synthetic word-compression foil, and laconic. Scored offline on
compression, readability, answer quality, and a deterministic never-cut safety
check. Full method, every honesty note, and every table:
[`evals/results/2026-07-31-benchmark.md`](evals/results/2026-07-31-benchmark.md).

| vs baseline | tokens (sonnet) | tokens (haiku) | latency (sonnet) | readability violations | answers correct | never-cut failures |
|---|--:|--:|--:|--:|--:|--:|
| **laconic** | **-33%** | +1% | **-29%** | **0** | 27 / 30 | 2 / 50 |
| terse-control | -11% | +3% | -13% | 9 | 27 / 30 | 1 / 50 |
| word-compression | +3% | +4% | -13% | 11 | 27 / 30 | 0 / 50 |
| baseline | 0% | 0% | 0% | 1 | 28 / 30 | 0 / 50 |

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
| `floor` | 201 | 220 | 82 | **59%** |
| `walkthrough` | 3701 | 3682 | 1628 | **56%** |
| `silent-success` | 1105 | 947 | 511 | **54%** |
| `ordered-steps` | 1329 | 1630 | 801 | **40%** |
| `decision` | 839 | 786 | 513 | **39%** |
| `fail-open` | 1265 | 1234 | 877 | **31%** |
| `code-fidelity` | 307 | 315 | 214 | **30%** |
| `conditional` | 908 | 981 | 740 | 19% |
| `badnews` | 435 | 414 | 372 | 14% |
| `stale-cache` | 1660 | 2245 | 1640 | 1% |
| `destructive` | 2336 | 2775 | 2462 | **-5%** |
| **median** | **1105** | **981** | **740** | **33%** |

`destructive` is the one Sonnet case that gets longer, which is the design
working: naming exactly what a `DROP TABLE` affects is never-cut content, so
laconic has nothing to trim there. `stale-cache` sits at 1% for the same reason
— it is the case that needs a mechanism explained, and a requested explanation
is not something laconic cuts.

<details>
<summary><strong>Haiku 4.5</strong></summary>

| case | baseline | terse-control | laconic | saved |
|---|--:|--:|--:|--:|
| `floor` | 266 | 236 | 225 | 15% |
| `silent-success` | 775 | 732 | 711 | 8% |
| `badnews` | 469 | 432 | 443 | 6% |
| `conditional` | 956 | 1017 | 911 | 5% |
| `walkthrough` | 1228 | 1008 | 1185 | 4% |
| `code-fidelity` | 425 | 421 | 418 | 2% |
| `decision` | 522 | 506 | 515 | 1% |
| `fail-open` | 922 | 843 | 960 | -4% |
| `ordered-steps` | 653 | 636 | 715 | -9% |
| `stale-cache` | 1246 | 1355 | 1404 | -13% |
| `destructive` | 711 | 791 | 837 | -18% |
| **median** | **711** | **732** | **715** | **-1%** |

Haiku's result depends on the aggregation convention, so no compression claim is
made for it in either direction. The table above is a median of per-case
medians (-1%); a flat median over the 55 raw runs gives 731 against 715, a 2%
cut. Sonnet compresses on both estimators — 33% and 37% — and the Sonnet figures
are the ones quoted above.

</details>

On Sonnet, laconic's stdev (175) is the lowest of the four arms and its max
(865) sits below baseline's median, so the gap is not one or two short outliers.
Dispersion per arm and model is in the results doc.

### Readability — the whole point

Counted on code-stripped prose: arrows standing in a sentence, telegraphic
abbreviations (`impl`, `req`, `w/`), sentences starting lowercase.

| arm | violations | responses affected (of 110) |
|---|--:|--:|
| baseline | 1 | 1 |
| terse-control | 9 | 4 |
| word-compression | 11 | 6 |
| **laconic** | **0** | **0** |

This number was 16 for laconic on the 2026-07-30 run. Every violation went
through one of the two openings in the earlier phrasing, "no arrows standing in
for conjunctions in running prose": a sequence arrow is not a conjunction, and a
`**Bolded label**: ...` line does not read as running prose. The rule now bans
arrows anywhere in a sentence and names both forms. Re-measured with the
**unchanged** detector, the count is 0.

The three cases added in the last revision replicate this on prompts the
detector had never scored: over those 30 responses per arm, baseline 1,
terse-control 4, word-compression 7, laconic 0.

### Answer quality

The three `quality` cases each present a fixture with a buried mechanism and a
plausible decoy, and ask a diagnostic question. The criterion is whether the
response names the mechanism, and every word of it comes from the fixture rather
than from `rules/laconic.md` — which is what makes these the only cases in the
suite from which a comparison between arms is legitimate.

| arm | answers correct (of 30) |
|---|--:|
| baseline | 28 |
| terse-control | 27 |
| word-compression | 27 |
| **laconic** | **27** |

**Laconic's answers were as often correct as baseline's** while being 31%
shorter on Sonnet across those same three cases. A one-response difference,
Fisher's exact two-sided p = 1.00.

This is a coarse instrument and the results doc publishes its power curve: at
n=30 per arm it would have caught a drop to about 64% and would have missed
anything smaller. Two of the three cases are at ceiling — every arm passes — so
the only separation comes from `stale-cache` on Haiku, where all four arms sit
within one response of each other. Read it as ruling out a large regression, not
as a fine-grained quality measurement.

### Cost, reported net

The injected rules cost tokens of their own, so the net per-call cost sits
slightly above baseline on both models even where output tokens drop.

| median USD per call | haiku | sonnet |
|---|--:|--:|
| baseline | 0.0165 | 0.0716 |
| laconic | 0.0190 | 0.0767 |

Each generation is one `--append-system-prompt` call with a single question, not
a multi-turn session, so this **overstates** what a real session pays once the
first turn's cache write becomes a cache read on every turn after it.

### Never-cut check

`report.py` gates on the never-cut contract and exits 1 against the committed
snapshot: 2 failures out of the 50 responses per arm that carry a keyword list
to verify by design. Both were read and confirmed. One `destructive` response
pointed at foreign keys generally rather than naming the two tables in the
fixture, and one `conditional` response stopped short of diagnosing the leak.

The difference from the previous run's 0 is not statistically distinguishable
(Fisher p = 0.50), and `terse-control` scores 1 on the same snapshot. The
threshold is unchanged from the run that passed it. Adding the three quality
cases did not change either failure — they carry no keyword list — but it did
drop the checked fraction from 63% of responses to 45%.

### Scope

What the numbers cover:

- **The compression, readability, latency and cost figures are the load-bearing
  ones.** They come from deterministic offline scoring of the raw responses.
- **Only 3 of the 11 cases can be compared between arms.** Every case declares
  where its criteria came from in a `grading` field. Five grade the never-cut
  contract, which the treatment arm was instructed to follow and the controls
  were not; three grade adherence to laconic's own style prohibitions. Neither
  kind supports a comparison, and the trap table publishes the field as a column
  so a row cannot be read out of context.
- **The quality result rules out a large regression and nothing finer.** Power
  at n=30 per arm reaches 0.78 only by a drop to 65%. Two of the three cases are
  at ceiling.
- **The headline compression figure moved from 28% to 33% on Sonnet** when the
  case set grew from 8 to 11. Both are published; the added cases give 31% on
  their own.
- **Never-cut coverage is 50 of 110 responses per arm.** Six cases carry an
  empty keyword list and are not checked — three were emptied once an earlier
  `"if"` keyword turned out to match "different", "specify" and "identify", and
  the three quality cases turn on mechanisms with several correct phrasings, so
  any required substring would fail correct answers.
- **The snapshot is mixed for the original 8 cases.** Their laconic arm was
  regenerated on 2026-07-31 after the arrow fix while their controls were
  carried over from 2026-07-30, so treatment and control were not sampled at
  the same time. The 3 quality cases have all four arms generated together and
  do not inherit this.
- **n=5 per cell, two models, one vendor.** Differences smaller than the
  published stdev are treated as noise, and the results speak only to Claude
  models.
- **The judge is a Claude model grading Claude outputs,** blind to arm with the
  rules text withheld. It is not an independent evaluator, and the answer-quality
  claim is the one result that rests on it.

Reproduce:

```bash
python3 evals/bench/run.py      # generate (~440 calls, 2-3 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```
