# Configuration

Per-repository levels, a machine default, and the statusline badge. See the
[README](../README.md) for install and the levels themselves.

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

## Statusline badge

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
