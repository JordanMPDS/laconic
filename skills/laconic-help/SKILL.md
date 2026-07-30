---
name: laconic-help
description: Use when the user asks what laconic levels exist, how to switch or disable laconic, or invokes /laconic-help — a one-shot reference card, not a persistent mode.
---

# Laconic reference

One-shot display. Invoking this does not change the active level.

| Command | Effect |
| --- | --- |
| `/laconic` | Set `full` (the default level) |
| `/laconic lite` | Ceremony cut, full reasoning kept |
| `/laconic full` | Answer first, one recommendation, no volunteered extras |
| `/laconic ultra` | The result alone, still in complete sentences |
| `/laconic off` | Stops all injection. Nothing further is added to context |
| `/laconic status` | Report the active level and the flag file path |

Make it permanent with `LACONIC_DEFAULT=full` in the `env` block of
`settings.json`. With no flag file and no default set, the plugin is inert.

Never cut at any level: code, config, commands, error strings, security warnings,
destructive-action confirmations, ordered steps, bad news, uncertainty that changes
what the user should do, and anything the user asked to have explained. Read
`rules/laconic.md` for the authoritative list and the worked example at all three
levels — if this summary and that file ever disagree, that file wins.
