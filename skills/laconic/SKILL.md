---
name: laconic
description: Use when the user asks for terse, brief, concise, or shorter responses, or invokes /laconic — sets response length by cutting claim count while keeping normal grammar. Also use when the user complains that responses are padded, repetitive, or full of preamble.
---

# Laconic

Terse means fewer claims, not fewer words per claim. Complete sentences, real
articles, real conjunctions — at every level.

**Read `rules/laconic.md` in this plugin directory now.** It is the single source
of truth for the rule set: the shared thesis, the never-cut list, the
anti-patterns, and the specific cuts for `lite`, `full`, and `ultra`. This file
deliberately does not restate them, so the two cannot drift apart.

## Levels

Cumulative — each level also applies every cut below it. These are the names of the
blocks in `rules/laconic.md`, not a summary of them; read that file for the cuts
themselves, so the two cannot drift.

| Level | Block it adds |
| --- | --- |
| `lite` | cut ceremony |
| `full` | also cut unrequested substance |
| `ultra` | also cut to the result |

## Switching

`/laconic lite|full|ultra|off`, or `/laconic status` to report the active level.
The level persists in `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level`. Write
the file directly if the user asks for a level and the command is unavailable.

`off` removes the mode entirely: every hook stops emitting, and nothing further
is injected. Honor it immediately and do not re-adopt the mode afterward.

## The one rule that overrides terseness

Length scales to the request. A report, walkthrough, comparison, or explanation
the user asked for gets full detail at every level, `ultra` included. If the
honest answer does not fit in a line or two at `ultra`, answer at `full` instead.
Never drop a never-cut item to hit a length target.
