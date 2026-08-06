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
if [ "$count" = "14" ]; then ok "14 cases present"; else fail "14 cases present (found $count)"; fi

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

# --- Grading provenance ---
# Every case declares where its trap criteria came from, because that decides
# what its verdicts may be used for. A `quality` case is the only kind that
# supports a comparison between arms, so its criterion must be answerable from
# the task and the fixture alone. `decision` and `floor` were read as evidence
# once, and the claim had to be retracted when it turned out their criteria
# were laconic's own prohibitions restated - the treatment arm was being scored
# against the text it had been handed.
#
# The forbidden list below is the vocabulary of form: length, ceremony,
# structure. A criterion that reaches for any of it is grading how the answer
# was written rather than whether it was right, which is precisely the
# contamination. It is checked against the trap only, not criteria_source -
# that field names rules/laconic.md on purpose for the contaminated cases.
grading_report=$(python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
VALID = ("quality", "safety", "rule-adherence")
FORBIDDEN = ("terse", "concise", "brief", "shorter", "length", "verbose",
             "preamble", "closing offer", "unrequested", "survey", "padded",
             "padding", "hedg", "pleasantr", "recap", "arrow", "article",
             "word count", "one recommendation")

for d in sorted(p for p in (root / "evals" / "cases").iterdir() if p.is_dir()):
    e = json.loads((d / "expect.json").read_text())
    g = e.get("grading")
    print(("ok   " if g in VALID else "FAIL ")
          + "case %s declares a valid grading (%r)" % (d.name, g))
    src = e.get("criteria_source")
    print(("ok   " if isinstance(src, str) and src.strip() else "FAIL ")
          + "case %s records where its criteria came from" % d.name)
    # saturated_models drives a gate exclusion, so a malformed value must fail
    # loudly instead of silently excluding nothing (or everything).
    sat = e.get("saturated_models")
    if sat is not None:
        okv = (isinstance(sat, dict) and sat
               and all(isinstance(m, str) and m
                       and isinstance(r, str) and r.strip()
                       for m, r in sat.items()))
        print(("ok   " if okv else "FAIL ")
              + "case %s saturated_models maps each model to a non-empty reason" % d.name)
    if g != "quality":
        continue
    hits = [w for w in FORBIDDEN if w in e.get("trap", "").lower()]
    print(("ok   " if not hits else "FAIL ")
          + "quality case %s grades the task, not the rule text%s"
          % (d.name, "" if not hits else " (found: %s)" % ", ".join(hits)))
PY
)
printf '%s\n' "$grading_report"
fails=$((fails + $(printf '%s\n' "$grading_report" | grep -c '^FAIL ')))

# At least one case must actually be gradeable on answer quality. Without one,
# the benchmark can say the plugin is shorter and still say nothing about
# whether it is as useful, which is the gap issue #9 exists to close.
nq=$(grep -l '"grading": "quality"' "$ROOT"/evals/cases/*/expect.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$nq" -ge 1 ]; then
  ok "at least one quality-graded case exists (found $nq)"
else
  fail "no quality-graded case exists - no answer-quality claim is possible"
fi

# The holdout exists to be scored once, at ship time. A holdout case the
# default glob reaches is a dev case, and it stops being a holdout the moment
# somebody optimizes against it.
hcount=$(ls -d "$ROOT"/evals/holdout/*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$hcount" -ge 4 ]; then
  ok "at least 4 holdout cases present (found $hcount)"
else
  fail "at least 4 holdout cases present (found $hcount)"
fi

for d in "$ROOT"/evals/holdout/*/; do
  c=$(basename "$d")
  if [ -f "$d/prompt.md" ] && [ -f "$d/expect.json" ]; then
    ok "holdout case $c has prompt.md and expect.json"
  else
    fail "holdout case $c has prompt.md and expect.json"
  fi
done

if ls -d "$ROOT"/evals/cases/holdout-*/ >/dev/null 2>&1; then
  fail "a holdout case has leaked into evals/cases, where the default glob reaches it"
else
  ok "holdout cases stay outside the default case glob"
fi

# Two never-cut items and a requested explanation is the coverage the holdout
# is for. A holdout of four short questions would pass every rule edit that
# compresses by cutting a warning.
hsafety=$(grep -l '"grading": "safety"' "$ROOT"/evals/holdout/*/expect.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$hsafety" -ge 2 ]; then
  ok "holdout covers at least 2 never-cut cases (found $hsafety)"
else
  fail "holdout covers at least 2 never-cut cases (found $hsafety)"
fi

printf '\n%d failure(s)\n' "$fails"
[ "$fails" -eq 0 ]
