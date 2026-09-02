# Other agents

Gemini CLI runs the hooks. Everything else takes a static rule file.

## Gemini CLI: run the hooks

Gemini CLI's hook system takes the same `{"type": "command", "command": "..."}`
shape laconic already ships for Claude Code, so `hooks/laconic.sh` and
`hooks/laconic.ps1` serve it unchanged. Two of its events inject into model
context, and they line up with laconic's two modes:

| Gemini event | Injects | laconic mode |
| --- | --- | --- |
| `SessionStart` | `additionalContext`, as the first turn | `start` |
| `BeforeAgent` | `additionalContext`, appended to the prompt for that turn | `remind` |

Copy [`hooks/gemini-settings.json`](../hooks/gemini-settings.json) into
`~/.gemini/settings.json` (or `.gemini/settings.json` for one project), merging
it with whatever is already there, and replace
`/absolute/path/to/laconic` with your clone:

```bash
git clone https://github.com/JordanMPDS/laconic ~/projects/laconic
```

Then set a level. `/laconic full` in Claude Code writes the same
`~/.claude/.laconic-level` both tools read, or write it directly:

```bash
printf full > ~/.claude/.laconic-level
```

### Why the command looks like that

- **`LACONIC_JSON_PATH=hookSpecificOutput.additionalContext`.** Claude Code reads
  the rule slice as raw stdout; Gemini reads a field out of a JSON object. That
  variable wraps the same bytes at the given dotted path. Unset, the hook behaves
  exactly as it does under Claude Code.
- **`env` rather than a bare `VAR=value` prefix.** A `VAR=value` prefix only works
  if the command goes through a shell. `env` is the command either way.
- **`"timeout": 5000`.** Gemini's timeouts are milliseconds; Claude Code's
  `hooks/hooks.json` uses seconds for the same 5 seconds.
- **No `matcher`.** The field is optional and omitting it fires on every source,
  which is what laconic wants — `startup`, `resume`, and `clear` all need the
  rules reloaded. If a hook does not fire, add `"matcher": "*"`.

On native Windows, Gemini's schema has no `commandWindows` field, so substitute
the PowerShell command in place, JSON-escaped as shown:

```json
"command": "powershell -NoProfile -ExecutionPolicy Bypass -Command \"$env:LACONIC_JSON_PATH='hookSpecificOutput.additionalContext'; & 'C:\\path\\to\\laconic\\hooks\\laconic.ps1' start\""
```

### What is different from Claude Code

- **`/laconic` does not switch the level from inside Gemini.** The switch is
  parsed out of the `"prompt"` field of Claude Code's `UserPromptSubmit` payload,
  and Gemini's `BeforeAgent` payload carries `llm_request.messages` instead. The
  level comes from the flag file or `LACONIC_DEFAULT`. Nothing misfires — the
  hook simply finds no switch to apply.
- **No compaction reload.** Gemini's `SessionStart` sources are `startup`,
  `resume`, and `clear`; compaction is a separate `PreCompress` event that
  injects nothing.
- **Not verified against a running Gemini CLI.** The JSON shape is checked by
  `tests/test_laconic.sh` against Gemini's documented schema, and schema validity
  is not evidence of loading. [#13](https://github.com/JordanMPDS/laconic/issues/13)
  stays open until someone confirms it on a real install.

## Everything else: copy a rule file

Agents without a hook system take a static instructions file. `rules/dist/` holds
one pre-sliced file per level — copy the one you want:

| Level | File |
| --- | --- |
| `lite` | [`rules/dist/laconic-lite.md`](../rules/dist/laconic-lite.md) |
| `full` | [`rules/dist/laconic-full.md`](../rules/dist/laconic-full.md) |
| `ultra` | [`rules/dist/laconic-ultra.md`](../rules/dist/laconic-ultra.md) |

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

## What you give up

A static file is the rule text and nothing else. Specifically:

- **No `/laconic` switching.** The level is whichever file you copied. Changing it
  means copying a different one.
- **No off switch.** Delete the file. There is no `/laconic off`, which is the
  guarantee the hook exists to provide.
- **No per-turn reminder**, so nothing reinforces the rules as context fills.

Codex CLI, Copilot, and Cursor all have shell-command hooks that could run
`laconic.sh` and `laconic.ps1` properly, the way Gemini CLI now does. That work is
tracked in [#14](https://github.com/JordanMPDS/laconic/issues/14),
[#15](https://github.com/JordanMPDS/laconic/issues/15), and
[#16](https://github.com/JordanMPDS/laconic/issues/16) — until one lands, the
copied file is what those agents get.

Regenerate after editing `rules/laconic.md`:

```bash
bash tools/build-rules.sh
```

`tests/test_rules.sh` fails if the committed copies are stale, since a drifted copy
sitting in someone's `.cursor/rules/` gives no sign it went out of date.
