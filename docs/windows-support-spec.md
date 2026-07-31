# Spec: native-Windows support and the hook language decision

**Date:** 2026-07-30
**Status:** Implemented (issue #2), on trigger 2 — the repo gained CI. The one deviation
from the table below: the port also carries the project-level flag from issue #5, which
landed after this spec was written.
**Applies to:** `laconic` v0.1.1 and later
**Supersedes:** the "no PowerShell port" entry in [`v0.1.0-known-limits.md`](v0.1.0-known-limits.md)

## Problem

`hooks/laconic.sh` is bash, so laconic works on macOS, Linux, WSL, and Git Bash, but not on
native Windows. A Windows user without WSL or Git Bash cannot run the plugin at all.

The v0.1.0 plan originally specified a `hooks/laconic.ps1` and then dropped it. The stated
reason is worth restating precisely, because it determines what to do now: it was dropped
because **no PowerShell interpreter existed on the development machine to verify it against**,
and an unverified script that writes into model context is worse than no script. It was not
dropped for any technical objection to PowerShell.

That constraint no longer holds. The repo is public at `github.com/JordanMPDS/laconic`, and
GitHub Actions gives public repositories unlimited free minutes on `windows-latest` runners.
A `.ps1` can now be verified by a real Windows host on every push.

## Decision

**Ship a PowerShell port alongside the bash script, and verify both in CI. Do not rewrite the
hook in JavaScript.**

- `hooks/laconic.sh` stays authoritative for macOS, Linux, WSL, and Git Bash.
- `hooks/laconic.ps1` handles native Windows, invoked through the `commandWindows` key that
  Claude Code's hook manifest already supports.
- A two-job GitHub Actions workflow runs the bash suites on `ubuntu-latest` and the PowerShell
  suites on `windows-latest`.

### Why

**Availability is the deciding factor.** Windows PowerShell 5.1 is part of the operating
system on Windows 10 (1607+), Windows 11, and Server 2016+ — there is nothing for a user to
install, and `ConvertFrom-Json` has been available since PowerShell 3.0, so the Windows side
gets correct JSON payload parsing for free. Paired with bash on Unix, laconic then depends on
nothing but shells the OS already ships.

Node is the weaker guarantee. Claude Code installs as a native binary, so `node` may be absent
entirely. The `ponytail` plugin concedes this in its own manifest:

```json
"command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/ponytail-activate.js\"",
"commandWindows": "if (Get-Command node -ErrorAction SilentlyContinue) { node \"$env:CLAUDE_PLUGIN_ROOT\\hooks\\ponytail-activate.js\" }"
```

On a Windows machine without node, that guard makes the plugin silently do nothing. A silent
total no-op is a worse failure mode than maintaining a second implementation, and it is
especially bad for laconic, whose entire value proposition is that its on/off state is
trustworthy.

Startup cost also favors shells. Measured on the development machine, 20 invocations of the
bash hook took 0.30s wall-clock against 1.82s for 20 bare `node -e ''` startups — roughly 15ms
per turn, on a hook that fires on every prompt.

## Rejected alternatives

### Node / JavaScript — the strongest alternative, and the consolidation path if this decision is ever reversed

The honest argument for it: one implementation covers all three platforms, and `JSON.parse`
retires the raw-payload grep in `laconic.sh` outright. That grep has a real defect history —
two review rounds in v0.1.0 went to it. An unanchored pattern let ordinary prose flip the
level (`does /laconic off actually work?` wrote `off`, which could re-enable the mode after
the user disabled it), and the level alternation prefix-matched, so `/laconic fullscreen` set
`full`. Neither defect could exist with a real parser.

It loses anyway, on two grounds. First, that correctness has already been bought by other
means: the pattern is now anchored to the `"prompt"` field, boundary-checked against prefix
matches, and pinned by asserts covering the exact prose cases that broke it, leaving a
residual limit that requires a malformed payload to reach. Second, it trades a tested
correctness property for an untested availability risk — and the availability failure is
silent, which is the failure class this project treats as most serious.

If maintaining two implementations ever becomes the larger cost, JS is the move: one file,
`JSON.parse`, and a presence check that **fails loudly** rather than silently no-opping.

### Python

A plugin cannot ask its users to install a toolchain. macOS has no usable stock `python3` (the
system shim prompts for Xcode Command Line Tools), and Windows ships none at all. Strictly
worse availability than both shells and node.

### Go, Rust, or another compiled binary

Best startup (~1-5ms) and a stdlib JSON parser, but distribution is the blocker: the
marketplace installs by cloning the repo, so shipping a binary means committing prebuilt
executables for five or six platform/arch pairs, plus CI to build them. That is a large trust,
size, and maintenance cost for roughly 70 lines of logic.

### Status quo — document WSL/Git Bash and stop there

Defensible while nobody has asked, which is why v0.1.x ships this way. It stops being
defensible the moment a user with a native Windows setup wants the plugin, because the
workaround is "install a Unix environment," which is a larger ask than the plugin is worth.

## Trigger

Implement when **either** holds:

1. A native-Windows user asks for support, or reports the plugin doing nothing on Windows.
2. The repo gains CI for any other reason — at that point the marginal cost of the
   `windows-latest` job is close to zero, and shipping the port becomes cheaper than
   documenting its absence.

## Implementation

### Files

| File | Change |
| --- | --- |
| `hooks/laconic.ps1` | New. Port of `laconic.sh`, honoring the contract below |
| `hooks/hooks.json` | Add `commandWindows` to all three hook entries |
| `hooks/laconic-statusline.ps1` | New. Port of the badge script (optional, ship with the port) |
| `tests/test_laconic.ps1` | New. Port of the 62 asserts in `tests/test_laconic.sh` |
| `.github/workflows/ci.yml` | New. Two jobs: `ubuntu-latest` bash suites, `windows-latest` PowerShell suites |
| `README.md` | Remove the "no native-Windows port" limitation; state PowerShell 5.1+ |
| `docs/v0.1.0-known-limits.md` | Strike the PowerShell entry, referencing this spec |

### Hook manifest

Each of the three entries gains a `commandWindows` sibling. Do **not** add a `node`-style
presence guard — `powershell.exe` is always present, and a guard would reintroduce the silent
no-op this decision exists to avoid. Use `-NoProfile` so a user's PowerShell profile cannot
inject output into the hook's stdout.

```json
{
  "type": "command",
  "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/laconic.sh\" remind",
  "commandWindows": "powershell -NoProfile -ExecutionPolicy Bypass -File \"$env:CLAUDE_PLUGIN_ROOT\\hooks\\laconic.ps1\" remind",
  "timeout": 5
}
```

`-ExecutionPolicy Bypass` is required: the default `Restricted` policy on Windows client SKUs
refuses to run an unsigned `.ps1` from a cloned repo, and that refusal would surface as the
plugin silently not working.

### Contract the port must honor

Byte-identical behavior to `laconic.sh`, because both implementations read and write the same
state and a user may switch between WSL and native Windows against the same `~/.claude`:

1. **Flag path.** `$env:CLAUDE_CONFIG_DIR` if set, else `$HOME/.claude`, file `.laconic-level`.
2. **Modes.** Exactly `start`, `subagent`, `remind`. Anything else, including a missing
   argument, exits 0 emitting nothing.
3. **Whitelist.** Exactly `lite`, `full`, `ultra`, `off`. Read at most 16 characters, strip to
   `[a-z]`, and emit nothing for any value outside the list — including `off`.
4. **Never emit when off or unset.** No flag file and no `LACONIC_DEFAULT` means no output.
5. **Symlink refusal.** Refuse to read *or* write through a symlinked or reparse-point flag
   file. On Windows check `(Get-Item $flag -Force).LinkType`; note that the Unix script needs
   the write guard separately from the read guard because the `remind` write happens first.
6. **Switch detection.** Match `/laconic <level>` only when anchored to the start of the
   `prompt` field's value, with a trailing boundary so `fullscreen` does not match `full`.
   Use `ConvertFrom-Json` rather than porting the regex — a real parser is the correct tool
   and it is available here.
7. **`LACONIC_DEFAULT` validation.** Validate against the whitelist *before* writing the flag
   file. An unvalidated typo creates a file the whitelist then rejects forever, with no
   re-seed path — a silent permanent brick.
8. **Marker slicing.** Print the shared block plus every block up to the active level, keying
   on `<!-- level:lite -->`, `<!-- level:full -->`, `<!-- level:ultra -->` matched as whole
   lines.
9. **No BOM.** Write the flag file as ASCII with no byte-order mark. PowerShell 5.1's
   `Set-Content`/`Out-File` add one by default; use
   `[System.IO.File]::WriteAllText($flag, $level, [System.Text.UTF8Encoding]::new($false))`.
   A BOM would be invisible in an editor and would make a hand-inspected flag file look
   correct while failing the whitelist.
10. **Line endings.** Emit `\n`, not `\r\n`. The output becomes model context, and stray
    carriage returns are noise in the prompt.

### Acceptance criteria

The port is done when all of these hold:

- `windows-latest` CI runs the PowerShell suite green, and `ubuntu-latest` runs both bash
  suites green, on the same commit.
- These invariants pass on **both** platforms, since they are the plugin's promises:
  - no flag file and no `LACONIC_DEFAULT` → zero bytes on stdout, exit 0
  - flag `off` → zero bytes on all three modes
  - malformed flag contents → zero bytes, and the contents are never echoed
  - `{"prompt":"does /laconic off actually work?"}` → the stored level is unchanged
  - `/laconic fullscreen`, `/laconic offline`, `/laconic ultraviolet` → level unchanged
  - `{"prompt":"/laconic ultra"}` → level becomes `ultra`; reminder line names it
  - a symlinked flag file is neither read through nor written through
  - `lite`/`full`/`ultra` each emit exactly their cumulative slice
- A flag file written by the PowerShell hook is accepted by the bash hook and vice versa,
  verified explicitly — this is the cross-platform state-sharing case that a per-platform
  test suite would otherwise miss.
- Installing from the marketplace on a real Windows host loads the plugin with no error.
  v0.1.0 shipped a manifest that passed both `claude plugin validate --strict` invocations
  and still failed to load at runtime; only a real install caught it. Do not treat validation
  as evidence of loading.

## Open questions

- **PowerShell 7 (`pwsh`) on Unix as a single implementation.** Would collapse this to one
  file, but `pwsh` is not installed by default on macOS or Linux, so it has node's
  availability problem without node's ubiquity. Not pursued; recorded because it looks
  attractive and is not.
- **Whether the statusline badge is worth porting.** It is opt-in and cosmetic. Shipping it
  with the port is cheap; deferring it is also defensible. Decide when implementing.
