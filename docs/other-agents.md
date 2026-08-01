# Other agents: copy a rule file

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
