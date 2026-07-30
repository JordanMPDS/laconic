#!/usr/bin/env bash
# Asserts the evals directory layout the bench harness depends on.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fails=0
fail() { printf 'FAIL %s\n' "$1"; fails=$((fails + 1)); }
ok()   { printf 'ok   %s\n' "$1"; }

for c in decision walkthrough destructive badnews; do
  if [ -f "$ROOT/evals/cases/$c/prompt.md" ]; then
    ok "case $c has prompt.md under evals/cases"
  else
    fail "case $c has prompt.md under evals/cases"
  fi
done

if [ ! -d "$ROOT/evals/decision" ]; then
  ok "old top-level case dirs removed"
else
  fail "old top-level case dirs removed"
fi

if grep -q 'evals/cases/' "$ROOT/evals/run.sh"; then
  ok "run.sh globs evals/cases"
else
  fail "run.sh globs evals/cases"
fi

if grep -q 'evals/scratch' "$ROOT/evals/run.sh"; then
  ok "run.sh writes to evals/scratch"
else
  fail "run.sh writes to evals/scratch"
fi

if grep -qx 'evals/scratch/' "$ROOT/.gitignore"; then
  ok "gitignore excludes evals/scratch"
else
  fail "gitignore excludes evals/scratch"
fi

if grep -qx 'evals/results/' "$ROOT/.gitignore"; then
  fail "gitignore no longer excludes evals/results"
else
  ok "gitignore no longer excludes evals/results"
fi

count=$(ls -d "$ROOT"/evals/cases/*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$count" = "8" ]; then ok "8 cases present"; else fail "8 cases present (found $count)"; fi

for dir in "$ROOT"/evals/cases/*/; do
  name=$(basename "$dir")
  if [ -f "$dir/expect.json" ]; then
    ok "case $name has expect.json"
  else
    fail "case $name has expect.json"
  fi
  if python3 -c "
import json,sys
d=json.load(open('$dir/expect.json'))
sys.exit(0 if isinstance(d.get('never_cut'),list) and isinstance(d.get('trap'),str) and d['trap'] else 1)
"; then
    ok "case $name expect.json has never_cut list and trap text"
  else
    fail "case $name expect.json has never_cut list and trap text"
  fi
done

printf '\n%d failure(s)\n' "$fails"
[ "$fails" -eq 0 ]
