# Laconic Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the n=1, two-arm, human-read eval with a four-arm benchmark across two models at n=5 that measures compression *and* readability, and publishes numbers regenerable offline from a committed snapshot.

**Architecture:** Generation (`run.py`) shells out to `claude -p --output-format json` and appends to a resumable snapshot. Scoring splits in two: `metrics.py` is deterministic and offline, `judge.py` is a blind LLM pass over the same snapshot. `report.py` turns both into markdown tables and enforces gates by exit code.

**Tech Stack:** Python 3 (stdlib only), bash 3.2, the `claude` CLI.

**Spec:** `docs/superpowers/specs/2026-07-30-laconic-benchmark-design.md`

## Global Constraints

- **Zero third-party Python packages.** `json`, `re`, `statistics`, `subprocess`, `argparse`, `pathlib` only. No pytest, no tiktoken, no pandas, no requests.
- **Tests are framework-free**, mirror `tests/test_rules.sh` (print `ok`/`FAIL` per assertion, count failures, exit non-zero if any). Python tests run as `python3 tests/test_x.py`.
- **Any shell touched stays bash 3.2-safe** — no `mapfile`, no associative arrays, no `${var,,}`. No `jq` anywhere.
- **The laconic arm's rules come from `hooks/laconic.sh`**, never a copy. The benchmark must not be able to drift from what ships.
- **All prose detection runs on code-stripped text.** `->` in Rust and `impl` in a command are correct usage.
- **A failed call is recorded as `ok: false` and excluded from every statistic.** A failure scored as a short answer reads as excellent compression.
- **The judge is blind:** arm names never appear in its prompt.
- Python target is 3.9+ syntax (no `match`, no PEP 604 `X | Y` in annotations) so the harness runs on stock system Pythons.

## File Structure

| File | Responsibility |
| --- | --- |
| `evals/cases/<name>/prompt.md` | The question. 8 cases. |
| `evals/cases/<name>/fixture/` | Files staged into the run cwd. Only where the prompt names project artifacts. |
| `evals/cases/<name>/expect.json` | Machine-readable never-cut keywords + trap text for the judge. |
| `evals/bench/metrics.py` | Deterministic scoring. Pure functions, no I/O, no network. |
| `evals/bench/run.py` | Generation and snapshot management. |
| `evals/bench/judge.py` | Blind trap grading. |
| `evals/bench/report.py` | Stats, tables, gates. |
| `evals/snapshots/results.json` | Committed generation data. |
| `evals/snapshots/judgments.json` | Committed judge verdicts. |
| `tests/test_metrics.py` | Validates the detectors against known-good/known-bad/code fixtures. |
| `tests/test_bench.py` | Validates run/judge/report logic against stubs and synthetic snapshots. |
| `tests/stubs/claude-stub.sh` | Fake CLI emitting canned JSON, so run/judge are testable offline. |

**Plan decision, deviating from the spec:** the spec put per-case never-cut keyword lists in `CRITERIA.md`. Parsing prose markdown for machine use is fragile, so the lists live in `evals/cases/<name>/expect.json` and `CRITERIA.md` documents the mechanism in prose without duplicating the keywords. Single source of truth, no drift.

---

### Task 1: Restructure the evals layout

**Files:**
- Move: `evals/{decision,walkthrough,destructive,badnews}/` → `evals/cases/`
- Modify: `evals/run.sh` (case glob, output dir)
- Modify: `.gitignore`
- Test: `tests/test_evals_layout.sh` (create)

**Interfaces:**
- Produces: every case lives at `evals/cases/<name>/prompt.md`; `run.sh` writes to `evals/scratch/<level>/`; `evals/results/` is committed.

- [ ] **Step 1: Write the failing test**

Create `tests/test_evals_layout.sh`:

```bash
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

printf '\n%d failure(s)\n' "$fails"
[ "$fails" -eq 0 ]
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `bash tests/test_evals_layout.sh`
Expected: FAIL on all four case assertions plus the run.sh and gitignore assertions.

- [ ] **Step 3: Move the case directories**

```bash
mkdir -p evals/cases
git mv evals/decision evals/walkthrough evals/destructive evals/badnews evals/cases/
```

- [ ] **Step 4: Point run.sh at the new layout**

In `evals/run.sh`, change the output directory:

```bash
OUT="$ROOT/evals/scratch/$LEVEL"
```

and the case loop:

```bash
for dir in "$ROOT"/evals/cases/$GLOB/; do
```

Update the final message to name the new path:

```bash
printf '\nwrote %s\nGrade against evals/CRITERIA.md.\n' "$OUT"
```

- [ ] **Step 5: Update .gitignore**

Replace the `evals/results/` line with `evals/scratch/`. The file becomes:

```
evals/scratch/
.superpowers/
*.tmp
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `bash tests/test_evals_layout.sh`
Expected: PASS, 0 failures.

- [ ] **Step 7: Verify run.sh still resolves cases**

Run: `bash -n evals/run.sh && ls evals/cases/*/prompt.md | wc -l`
Expected: syntax OK, prints `4`.

- [ ] **Step 8: Commit**

```bash
git add -A evals .gitignore tests/test_evals_layout.sh
git commit -m "refactor: move eval cases under evals/cases, free evals/results for committed writeups"
```

---

### Task 2: Deterministic metrics and their validation suite

**Files:**
- Create: `evals/bench/metrics.py`
- Test: `tests/test_metrics.py`

**Interfaces:**
- Produces, consumed by Tasks 5 and 6:
  - `split_text(text) -> (prose, sentences_src)` — `prose` has fenced blocks, inline code and URLs removed; `sentences_src` keeps inline code so sentence-initial checks can see backticks.
  - `score(text) -> dict` with keys `words` (int), `article_rate` (float), `aux_verb_rate` (float), `symbol_connectors` (int), `abbreviated_prose` (int), `sentence_initial_lowercase` (int), `violations` (int, the sum of the three counts), `spans` (list of str, the offending text).
  - `never_cut_missing(text, keywords) -> list` — keywords (case-insensitive substrings) absent from `text`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_metrics.py`. The three fixtures are the point of this task: known-good, known-bad carrying *the same content*, and a code-heavy paragraph that must not fire.

```python
#!/usr/bin/env python3
"""Validates the readability detectors themselves.

If these fail, the metric is broken - not the plugin. A detector that cannot
separate fixture GOOD from fixture BAD measures nothing, and one that fires on
CODE would score correct prose as degraded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals" / "bench"))
import metrics  # noqa: E402

fails = 0


def check(label, cond):
    global fails
    if cond:
        print("ok   %s" % label)
    else:
        print("FAIL %s" % label)
        fails += 1


GOOD = """The deploy failed because the worker ran out of memory. If the usage
sits at a steady ceiling, raise the limit; if it is climbing, you have a leak and
a bigger limit only delays the next kill.

Check these in order:

- run `kubectl top pod` for a few minutes
- compare the peak against the configured limit
- look at the restart count
"""

BAD = """Deploy failed -> worker OOM. Usage steady ceiling -> raise limit.
Usage climbing -> leak, bigger limit just delays next kill.

check kubectl top pod few min. compare peak vs configured limit. check restart
count. impl detail: req handler leaks obj refs, err path never frees.
"""

CODE = """The parser returns an error value rather than raising, so the caller
decides what to do with it.

```rust
impl Parser {
    fn parse(&self) -> Result<Ast, Err> { self.inner() }
}
```

Run `make test -> out.log` to capture the output, and read `impl.rs` for the
detail. The `err` variant is described at https://example.com/docs in section 4.
"""

g = metrics.score(GOOD)
b = metrics.score(BAD)
c = metrics.score(CODE)

check("good prose has no violations", g["violations"] == 0)
check("good prose keeps a normal article rate", g["article_rate"] >= 0.05)
check("good prose bullets do not trip lowercase-start",
      g["sentence_initial_lowercase"] == 0)

check("bad prose is flagged", b["violations"] >= 5)
check("bad prose arrows counted", b["symbol_connectors"] >= 3)
check("bad prose abbreviations counted", b["abbreviated_prose"] >= 3)
check("bad prose lowercase starts counted", b["sentence_initial_lowercase"] >= 2)
check("bad prose article rate collapses", b["article_rate"] < 0.03)
check("detectors separate good from bad", g["violations"] < b["violations"])
check("article rate separates good from bad by >2x",
      g["article_rate"] > 2 * b["article_rate"])

check("code blocks do not trip detectors", c["violations"] == 0)
check("inline code does not trip detectors", c["symbol_connectors"] == 0)
check("code-block identifiers are not counted as abbreviations",
      c["abbreviated_prose"] == 0)

check("violations are auditable", len(b["spans"]) == b["violations"])

check("never_cut_missing finds absent keywords",
      metrics.never_cut_missing("the sessions cascade", ["cascade", "invoices"])
      == ["invoices"])
check("never_cut_missing is case-insensitive",
      metrics.never_cut_missing("CASCADE deletes rows", ["cascade"]) == [])

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 tests/test_metrics.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'metrics'`.

- [ ] **Step 3: Implement metrics.py**

Create `evals/bench/metrics.py`:

```python
#!/usr/bin/env python3
"""Deterministic response scoring. No I/O, no network, no dependencies.

Two axes are measured here. Compression comes from the CLI's own token counts
and never touches this module. Readability is measured with the heuristics
below, which are validated by tests/test_metrics.py - they are proxies for
degraded grammar, not a parser.

Every detector runs on code-stripped prose: `->` in Rust and `impl` in a
command are correct usage, and counting them would make the metric worthless.
"""
import re

FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
ARTICLES = {"the", "a", "an"}
AUX = {
    "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did",
    "will", "would", "can", "could", "should", "may", "might", "must",
}

SYMBOLS = re.compile(r"(->|=>|→)")
# Deliberately tight. config, repo, auth, env and db are normal developer
# English; including them would fire on correct prose in every arm.
ABBREV = re.compile(
    r"\b(impl|req|resp|func|val|obj|arg|msg|err)\b|\bw/|\bb/c\b", re.I
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
# Lines that are structural markdown, not paragraph flow. Bullets legitimately
# start lowercase, so checking them would fire on correct writing.
STRUCTURAL = re.compile(r"^\s*([-*+>|#]|\d+[.)])")


def _paragraph_prose(sentences_src):
    """Structural lines dropped; hard-wrapped lines rejoined into paragraphs.

    Iterating raw lines would flag the continuation of every wrapped sentence
    as a lowercase start. Verified: that bug fired twice on the known-good
    fixture before this was paragraph-aware.
    """
    paras, cur = [], []
    for line in sentences_src.splitlines():
        if not line.strip() or STRUCTURAL.match(line):
            if cur:
                paras.append(" ".join(cur))
                cur = []
            continue
        cur.append(line.strip())
    if cur:
        paras.append(" ".join(cur))
    return paras


def split_text(text):
    """Return (prose, sentences_src).

    prose: fenced blocks, inline code and URLs removed - for word and rate
    counts. sentences_src: fenced blocks removed but inline code kept, so a
    sentence opening with a code span is still recognizable as such.
    """
    no_fence = FENCE.sub(" ", text)
    sentences_src = URL.sub(" ", no_fence)
    prose = URL.sub(" ", INLINE.sub(" ", no_fence))
    return prose, sentences_src


def _lowercase_starts(sentences_src):
    hits = []
    for para in _paragraph_prose(sentences_src):
        for sentence in SENTENCE_SPLIT.split(para):
            s = sentence.strip()
            if not s or s.startswith("`"):
                continue
            if s[0].islower():
                hits.append(s[:40])
    return hits


def score(text):
    prose, sentences_src = split_text(text)
    words = WORD.findall(prose)
    total = len(words)
    lowered = [w.lower() for w in words]

    symbols = SYMBOLS.findall(prose)
    abbrevs = [m.group(0) for m in ABBREV.finditer(prose)]
    lows = _lowercase_starts(sentences_src)

    spans = symbols + abbrevs + lows
    return {
        "words": total,
        "article_rate": (sum(1 for w in lowered if w in ARTICLES) / total) if total else 0.0,
        "aux_verb_rate": (sum(1 for w in lowered if w in AUX) / total) if total else 0.0,
        "symbol_connectors": len(symbols),
        "abbreviated_prose": len(abbrevs),
        "sentence_initial_lowercase": len(lows),
        "violations": len(symbols) + len(abbrevs) + len(lows),
        "spans": spans,
    }


def never_cut_missing(text, keywords):
    low = text.lower()
    return [k for k in keywords if k.lower() not in low]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 tests/test_metrics.py`
Expected: PASS, `0 failure(s)`.

- [ ] **Step 5: Prove each detector can actually fail**

Negative check — a detector that always returns 0 would pass the CODE assertions for the wrong reason. Confirm each fires in isolation:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "evals/bench")
import metrics
for probe in ["Deploy failed -> restart.", "the impl is broken.", "check the pod."]:
    print(repr(probe), metrics.score(probe)["violations"])
PY
```

Expected: `1`, `2`, `1`. The middle probe scores two because it trips both the
abbreviation and the lowercase-start detector — verified, not a defect.

- [ ] **Step 6: Commit**

```bash
git add evals/bench/metrics.py tests/test_metrics.py
git commit -m "feat: readability detectors with a validation suite

Heuristics are acceptable only because the suite proves they separate
known-good from known-bad prose and do not fire on code blocks."
```

---

### Task 3: Four new cases and the machine-readable expectations

**Files:**
- Create: `evals/cases/{conditional,ordered-steps,floor,code-fidelity}/prompt.md`
- Create: `evals/cases/conditional/fixture/{pool.log,db.js}`
- Create: `evals/cases/<name>/expect.json` for all 8 cases
- Modify: `evals/CRITERIA.md`
- Test: `tests/test_evals_layout.sh` (extend)

**Interfaces:**
- Consumes: layout from Task 1.
- Produces: `expect.json` per case, shape `{"never_cut": [str, ...], "trap": str}`. Consumed by `judge.py` (Task 5) and `report.py` (Task 6).

- [ ] **Step 1: Extend the layout test**

Append to `tests/test_evals_layout.sh`, before the final `printf`:

```bash
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tests/test_evals_layout.sh`
Expected: FAIL — 4 cases found, no `expect.json` anywhere.

- [ ] **Step 3: Write the four new prompts**

`evals/cases/conditional/prompt.md`:

```
Our Postgres connection pool keeps hitting max — pool.log has the last hour and
db.js is where it's configured. Should I raise the pool size?
```

`evals/cases/ordered-steps/prompt.md`:

```
How do I rotate our JWT signing key without logging every user out?
```

`evals/cases/floor/prompt.md`:

```
What does `git restore --staged` do?
```

`evals/cases/code-fidelity/prompt.md`:

```
Give me a one-liner to find files over 100MB modified in the last week, and
explain what each flag does.
```

- [ ] **Step 4: Write the conditional fixture**

`evals/cases/conditional/fixture/db.js`:

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.PGHOST,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Callers check out a client and are responsible for releasing it.
async function withClient(fn) {
  const client = await pool.connect();
  const result = await fn(client);
  client.release();
  return result;
}

module.exports = { pool, withClient };
```

`evals/cases/conditional/fixture/pool.log`:

```
14:02:11 pool: total=20 idle=0 waiting=7
14:02:41 pool: total=20 idle=0 waiting=11
14:03:11 pool: total=20 idle=0 waiting=14
14:03:41 pool: total=20 idle=0 waiting=19
14:04:11 error: timeout exceeded when trying to connect
14:04:12 pool: total=20 idle=0 waiting=23
14:04:42 pool: total=20 idle=0 waiting=28
```

The fixture is deliberately ambiguous between the two diagnoses: `idle=0` with a
monotonically climbing wait queue fits both a genuinely saturated pool and a leak,
and `withClient` leaks a client whenever `fn` throws, because `release()` is not in
a `finally`. A correct answer is therefore conditional, which is exactly what this
case measures.

- [ ] **Step 5: Write expect.json for all eight cases**

```bash
cat > evals/cases/decision/expect.json <<'JSON'
{
  "never_cut": [],
  "trap": "Passes when the answer commits to one recommendation with at most a clause of justification. Fails when it surveys both options evenhandedly, adds an unrequested migration lecture, or ends with an offer to do more work."
}
JSON

cat > evals/cases/walkthrough/expect.json <<'JSON'
{
  "never_cut": ["401", "refresh"],
  "trap": "Passes when it covers the whole flow the user asked for, including both the 401 path and what happens when two requests refresh at once. Fails when it is compressed to a summary, or when either of the two named branches is silently dropped."
}
JSON

cat > evals/cases/destructive/expect.json <<'JSON'
{
  "never_cut": ["cascade", "invoices"],
  "trap": "Passes when it names the blast radius before acting: sessions cascade-delete, and the invoices foreign key references users. Fails when either is unmentioned or the warning is trimmed to a fragment. Mentioning the fixture row count is a bonus, not a requirement."
}
JSON

cat > evals/cases/badnews/expect.json <<'JSON'
{
  "never_cut": ["3 failed", "test_billing"],
  "trap": "Passes when it states plainly that three tests still fail and names them. Fails when it reports the rounding fix as a success, omits the failures, or buries them under the passing count."
}
JSON

cat > evals/cases/conditional/expect.json <<'JSON'
{
  "never_cut": ["if"],
  "trap": "Passes when the advice stays conditional in readable English: raise the pool only if the connections are genuinely concurrent, and note that a leak - withClient never releases on throw - means a bigger pool just delays the same failure. Fails when the condition is dropped, when only one branch is given as unqualified advice, or when the conditional is collapsed into a symbol such as 'waiting climbing -> raise max'."
}
JSON

cat > evals/cases/ordered-steps/expect.json <<'JSON'
{
  "never_cut": ["verif", "sign"],
  "trap": "Passes when all four steps are present and their order is unmistakable: publish the new key to the verifier set first, then start signing with it, then wait out the old tokens' lifetime, and only then retire the old key. Fails when any step is missing or the ordering words are cut, because this procedure is wrong in any other order."
}
JSON

cat > evals/cases/floor/expect.json <<'JSON'
{
  "never_cut": ["stag"],
  "trap": "Passes when it answers the question correctly and briefly - this case has no padding to remove. Fails when the answer is wrong about what the command does, or when it is padded out with unrequested material about related commands."
}
JSON

cat > evals/cases/code-fidelity/expect.json <<'JSON'
{
  "never_cut": ["find", "-size", "-mtime"],
  "trap": "Passes when the command is complete and runnable and every flag in it is explained, since the explanation was explicitly requested. Fails when the command is truncated or abbreviated, or when the flag explanation is dropped as if it were unrequested padding."
}
JSON
```

- [ ] **Step 6: Document the new cases in CRITERIA.md**

Add to the per-case trap table in `evals/CRITERIA.md`:

```markdown
| `conditional` | The advice stays conditional in readable English, and the leak in `withClient` is named as the other branch | The condition is dropped, one branch is given as unqualified advice, or the conditional collapses into an arrow |
| `ordered-steps` | All four rotation steps present, order unmistakable | A step is missing, or the ordering words are cut — the procedure is wrong in any other order |
| `floor` | Correct and brief; nothing here should be cut | Wrong about the command, or padded with unrequested related material |
| `code-fidelity` | Command complete and runnable, every flag explained | Command truncated or abbreviated, or the requested explanation dropped |
```

Then add a section explaining where the machine-readable half lives:

```markdown
## Where the machine-readable criteria live

Each case carries an `expect.json` with two keys: `never_cut` (case-insensitive
substrings that must survive in the response, checked deterministically) and
`trap` (prose handed to the blind judge). The tables above are the human
narrative; `expect.json` is what the harness actually enforces. Keywords are
not duplicated here, so the two cannot drift.
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `bash tests/test_evals_layout.sh`
Expected: PASS, 0 failures, 8 cases.

- [ ] **Step 8: Verify every expect.json parses and every fixture-naming prompt has a fixture**

```bash
python3 - <<'PY'
import json, pathlib
for d in sorted(pathlib.Path("evals/cases").iterdir()):
    e = json.load(open(d / "expect.json"))
    has_fix = (d / "fixture").is_dir()
    print("%-14s never_cut=%-28s fixture=%s" % (d.name, e["never_cut"], has_fix))
PY
```

Expected: 8 rows; `conditional`, `walkthrough`, `destructive`, `badnews` show `fixture=True`; `decision`, `ordered-steps`, `floor`, `code-fidelity` show `fixture=False`.

- [ ] **Step 9: Commit**

```bash
git add evals/cases evals/CRITERIA.md tests/test_evals_layout.sh
git commit -m "feat: four new eval cases with machine-readable expectations

conditional is the case the README's central claim needs: correct advice
here is conditional, so a dropped conjunction makes it wrong half the time."
```

---

### Task 4: Generation harness

**Files:**
- Create: `evals/bench/run.py`
- Create: `tests/stubs/claude-stub.sh`
- Test: `tests/test_bench.py`

**Interfaces:**
- Consumes: `evals/cases/*/prompt.md`, `hooks/laconic.sh`.
- Produces, consumed by Tasks 5 and 6:
  - `ARMS` dict: name → system prompt (`None` for baseline; the laconic entry is filled at runtime from the hook).
  - `load_snapshot(path) -> dict`, `save_snapshot(path, snap)`.
  - `run_key(case, arm, model, rep) -> tuple` for resume checks.
  - `parse_cli_json(raw) -> dict` returning `{ok, text, output_tokens, input_tokens, cache_creation_input_tokens, cache_read_input_tokens, total_cost_usd, duration_ms, num_turns}`; `ok` is False on unparseable input.
  - Snapshot shape exactly as in the spec's "Snapshot schema" section.

- [ ] **Step 1: Write the failing test**

Create `tests/test_bench.py`:

```python
#!/usr/bin/env python3
"""Validates harness logic against stubs - no live model calls."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import run as bench_run  # noqa: E402

fails = 0


def check(label, cond):
    global fails
    if cond:
        print("ok   %s" % label)
    else:
        print("FAIL %s" % label)
        fails += 1


GOOD_JSON = json.dumps({
    "is_error": False, "result": "the answer", "num_turns": 1,
    "total_cost_usd": 0.0096, "duration_ms": 2089,
    "usage": {"input_tokens": 10, "output_tokens": 33,
              "cache_creation_input_tokens": 3573,
              "cache_read_input_tokens": 17615},
})

parsed = bench_run.parse_cli_json(GOOD_JSON)
check("parses text", parsed["text"] == "the answer")
check("parses output tokens", parsed["output_tokens"] == 33)
check("parses cache fields", parsed["cache_read_input_tokens"] == 17615)
check("parses cost", parsed["total_cost_usd"] == 0.0096)
check("good json is ok", parsed["ok"] is True)

check("garbage is not ok", bench_run.parse_cli_json("not json")["ok"] is False)
check("empty is not ok", bench_run.parse_cli_json("")["ok"] is False)
check("is_error payload is not ok",
      bench_run.parse_cli_json(json.dumps({"is_error": True, "result": "x"}))["ok"] is False)

check("arms include all four",
      sorted(bench_run.ARMS) == ["baseline", "laconic", "terse-control", "word-compression"])
check("baseline has no system prompt", bench_run.ARMS["baseline"] is None)
check("terse control is exactly the control instruction",
      bench_run.ARMS["terse-control"] == "Answer concisely.")

rules = bench_run.laconic_rules(ROOT, "full")
check("laconic rules come from the hook and are non-empty", len(rules) > 200)
check("laconic rules carry the thesis sentinel", "fewer claims" in rules)

with tempfile.TemporaryDirectory() as td:
    snap_path = Path(td) / "results.json"
    snap = bench_run.new_snapshot(reps=1, models=["haiku"], level="full",
                                  rules_cksum="123", arms=bench_run.ARMS)
    snap["runs"].append({"case": "decision", "arm": "baseline",
                         "model": "haiku", "rep": 0, "ok": True, "text": "x"})
    bench_run.save_snapshot(snap_path, snap)
    reloaded = bench_run.load_snapshot(snap_path)
    check("snapshot round-trips", len(reloaded["runs"]) == 1)
    done = bench_run.completed_keys(reloaded)
    check("completed key recognized",
          bench_run.run_key("decision", "baseline", "haiku", 0) in done)
    check("other key not recognized",
          bench_run.run_key("decision", "laconic", "haiku", 0) not in done)

    failed = {"case": "c", "arm": "a", "model": "haiku", "rep": 0, "ok": False}
    check("failed runs are excluded from stats input",
          bench_run.usable([failed, {"case": "c", "arm": "a", "model": "haiku",
                                     "rep": 1, "ok": True, "text": "y"}]) ==
          [{"case": "c", "arm": "a", "model": "haiku", "rep": 1, "ok": True, "text": "y"}])

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 tests/test_bench.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'run'`.

- [ ] **Step 3: Write the stub CLI**

Create `tests/stubs/claude-stub.sh` (used in Step 7 and by Task 5):

```bash
#!/usr/bin/env bash
# Fake `claude` for offline harness tests. Emits one canned CLI JSON object.
# STUB_TEXT overrides the answer; STUB_FAIL=1 exits non-zero.
[ "${STUB_FAIL:-0}" = "1" ] && exit 3
cat <<JSON
{"is_error":false,"result":"${STUB_TEXT:-stub answer}","num_turns":1,
"total_cost_usd":0.001,"duration_ms":1234,
"usage":{"input_tokens":10,"output_tokens":7,
"cache_creation_input_tokens":100,"cache_read_input_tokens":200}}
JSON
```

Make it executable: `chmod +x tests/stubs/claude-stub.sh`

- [ ] **Step 4: Implement run.py**

Create `evals/bench/run.py`:

```python
#!/usr/bin/env python3
"""Generation pass: run every (case, arm, model, rep) and append to a snapshot.

Resumable: a key already in the snapshot is skipped, so an interrupted
two-hour run continues instead of restarting. Failures are recorded with
ok=False and excluded from every statistic - a failed call silently scored as
a very short answer would read as excellent compression.
"""
import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
SNAPSHOT = ROOT / "evals" / "snapshots" / "results.json"

WORD_COMPRESSION = (
    "Answer concisely. Drop articles and filler words, abbreviate common "
    "terms, and use arrows instead of conjunctions."
)

# The laconic entry is a placeholder here and is replaced at runtime with the
# real hook output, so the benchmark cannot drift from what ships.
ARMS = {
    "baseline": None,
    "terse-control": "Answer concisely.",
    "word-compression": WORD_COMPRESSION,
    "laconic": "",
}


def laconic_rules(root, level):
    """Build the treatment arm from the real hook, never from a copy."""
    tmp = tempfile.mkdtemp()
    try:
        (Path(tmp) / ".laconic-level").write_text(level)
        env = dict(os.environ, CLAUDE_CONFIG_DIR=tmp)
        env.pop("LACONIC_DEFAULT", None)
        out = subprocess.run(
            ["bash", str(root / "hooks" / "laconic.sh"), "start"],
            capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL,
        )
        return out.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def parse_cli_json(raw):
    blank = {"ok": False, "text": "", "output_tokens": 0, "input_tokens": 0,
             "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
             "total_cost_usd": 0.0, "duration_ms": 0, "num_turns": 0}
    try:
        d = json.loads(raw)
    except (ValueError, TypeError):
        return blank
    if not isinstance(d, dict) or d.get("is_error"):
        return blank
    u = d.get("usage") or {}
    return {
        "ok": True,
        "text": d.get("result", ""),
        "output_tokens": u.get("output_tokens", 0),
        "input_tokens": u.get("input_tokens", 0),
        "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
        "total_cost_usd": d.get("total_cost_usd", 0.0),
        "duration_ms": d.get("duration_ms", 0),
        "num_turns": d.get("num_turns", 0),
    }


def run_key(case, arm, model, rep):
    return (case, arm, model, rep)


def completed_keys(snap):
    return set(run_key(r["case"], r["arm"], r["model"], r["rep"])
               for r in snap.get("runs", []) if r.get("ok"))


def usable(runs):
    return [r for r in runs if r.get("ok")]


def new_snapshot(reps, models, level, rules_cksum, arms):
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "claude_cli_version": _cli_version(),
            "git_commit": _git_commit(),
            "laconic_level": level,
            "rules_cksum": rules_cksum,
            "reps": reps,
            "models": models,
        },
        "arms": {k: {"system_prompt": v} for k, v in arms.items()},
        "runs": [],
    }


def _cli_version():
    try:
        return subprocess.run(["claude", "--version"], capture_output=True,
                              text=True).stdout.strip()
    except OSError:
        return "unknown"


def _git_commit():
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return "unknown"


def load_snapshot(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None


def save_snapshot(path, snap):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n")


def call(claude_bin, model, prompt, system_prompt, cwd):
    cmd = [claude_bin, "-p", "--model", model, "--output-format", "json"]
    if system_prompt:
        cmd += ["--append-system-prompt", system_prompt]
    env = dict(os.environ, CLAUDE_CODE_SAFE_MODE="1")
    env.pop("LACONIC_DEFAULT", None)
    try:
        out = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                             cwd=cwd, env=env, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return {"ok": False}
    if out.returncode != 0:
        return {"ok": False}
    return parse_cli_json(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="full")
    ap.add_argument("--models", default="haiku,sonnet")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--cases", default="*")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--claude-bin", default="claude")
    args = ap.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    arm_names = [a.strip() for a in args.arms.split(",") if a.strip()]
    cases = sorted(d for d in CASES.iterdir()
                   if (d / "prompt.md").exists() and fnmatch.fnmatch(d.name, args.cases))
    if not cases:
        sys.exit("no cases matched: %s" % args.cases)

    arms = dict(ARMS)
    arms["laconic"] = laconic_rules(ROOT, args.level)
    if not arms["laconic"].strip():
        sys.exit("hook produced no rules for level %s" % args.level)
    cksum = str(zlib.crc32(arms["laconic"].encode()))

    snap = load_snapshot(args.snapshot)
    if snap is None:
        snap = new_snapshot(args.reps, models, args.level, cksum, arms)
    elif snap["metadata"].get("rules_cksum") != cksum:
        sys.exit("snapshot was generated from different rules (cksum %s vs %s); "
                 "move it aside before regenerating"
                 % (snap["metadata"].get("rules_cksum"), cksum))
    done = completed_keys(snap)

    total = len(cases) * len(arm_names) * len(models) * args.reps
    n = 0
    for rep in range(args.reps):
        for case_dir in cases:
            case = case_dir.name
            prompt = (case_dir / "prompt.md").read_text()
            for model in models:
                for arm in arm_names:  # innermost: arms sampled at adjacent moments
                    n += 1
                    if run_key(case, arm, model, rep) in done:
                        continue
                    scratch = tempfile.mkdtemp()
                    fixture = case_dir / "fixture"
                    if fixture.is_dir():
                        shutil.copytree(fixture, scratch, dirs_exist_ok=True)
                    res = call(args.claude_bin, model, prompt, arms[arm], scratch)
                    shutil.rmtree(scratch, ignore_errors=True)
                    if not res.get("ok"):  # one retry before recording a failure
                        scratch = tempfile.mkdtemp()
                        if fixture.is_dir():
                            shutil.copytree(fixture, scratch, dirs_exist_ok=True)
                        res = call(args.claude_bin, model, prompt, arms[arm], scratch)
                        shutil.rmtree(scratch, ignore_errors=True)
                    res.update({"case": case, "arm": arm, "model": model, "rep": rep})
                    snap["runs"].append(res)
                    save_snapshot(args.snapshot, snap)
                    print("[%d/%d] %-14s %-16s %-7s rep%d %s"
                          % (n, total, case, arm, model, rep,
                             "ok" if res.get("ok") else "FAILED"))

    bad = len([r for r in snap["runs"] if not r.get("ok")])
    print("\nwrote %s (%d runs, %d failed)" % (args.snapshot, len(snap["runs"]), bad))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python3 tests/test_bench.py`
Expected: PASS, `0 failure(s)`.

- [ ] **Step 6: Verify resume and failure recording end to end against the stub**

```bash
rm -f /tmp/snap.json
python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh \
  --models haiku --reps 1 --cases floor --snapshot /tmp/snap.json
python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh \
  --models haiku --reps 1 --cases floor --snapshot /tmp/snap.json
python3 -c "
import json; s=json.load(open('/tmp/snap.json'))
print('runs:', len(s['runs']))
print('all ok:', all(r['ok'] for r in s['runs']))
"
```

Expected: the first run prints 4 `ok` lines (one per arm); the second prints none (all resumed); `runs: 4`, `all ok: True`.

Then force failures:

```bash
rm -f /tmp/snapfail.json
STUB_FAIL=1 python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh \
  --models haiku --reps 1 --cases floor --arms baseline --snapshot /tmp/snapfail.json
python3 -c "
import json,sys; sys.path.insert(0,'evals/bench'); import run
s=json.load(open('/tmp/snapfail.json'))
print('recorded:', len(s['runs']), 'usable:', len(run.usable(s['runs'])))
"
```

Expected: `recorded: 1 usable: 0` — the failure is stored but excluded.

- [ ] **Step 7: Commit**

```bash
git add evals/bench/run.py tests/test_bench.py tests/stubs/claude-stub.sh
git commit -m "feat: resumable generation harness with failure exclusion

Arms are sampled innermost so temporal drift hits them evenly, and the
laconic arm is built from hooks/laconic.sh so it cannot drift from ship."
```

---

### Task 5: Blind judge

**Files:**
- Create: `evals/bench/judge.py`
- Test: `tests/test_bench.py` (extend)

**Interfaces:**
- Consumes: `evals/snapshots/results.json`, `evals/cases/*/expect.json`, `parse_cli_json` from `run.py`.
- Produces, consumed by Task 6: `evals/snapshots/judgments.json`, shape
  `{"metadata": {...}, "judgments": [{"case","arm","model","rep","verdict","quote","reason"}]}`
  where `verdict` is one of `pass`, `fail`, `not_exercised`.
- Produces: `build_judge_prompt(case_prompt, trap, response) -> str` and
  `parse_verdict(raw) -> dict`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_bench.py`, before the final `print`:

```python
import judge as bench_judge  # noqa: E402

v = bench_judge.parse_verdict('{"verdict":"pass","quote":"q","reason":"r"}')
check("parses a clean verdict", v["verdict"] == "pass")
v = bench_judge.parse_verdict('here you go:\n{"verdict":"fail","quote":"q","reason":"r"}\nthanks')
check("parses a verdict wrapped in prose", v["verdict"] == "fail")
v = bench_judge.parse_verdict('{"verdict":"maybe","quote":"q","reason":"r"}')
check("rejects an out-of-range verdict", v["verdict"] == "not_exercised")
check("rejects garbage", bench_judge.parse_verdict("nope")["verdict"] == "not_exercised")
check("not_exercised is a supported verdict",
      bench_judge.parse_verdict('{"verdict":"not_exercised","quote":"","reason":"r"}')["verdict"]
      == "not_exercised")

p = bench_judge.build_judge_prompt("the question", "the trap", "the response")
check("judge prompt carries the trap", "the trap" in p)
check("judge prompt carries the response", "the response" in p)
for arm in ["laconic", "baseline", "terse-control", "word-compression"]:
    check("judge prompt is blind to arm %s" % arm, arm not in p)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 tests/test_bench.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'judge'`.

- [ ] **Step 3: Implement judge.py**

Create `evals/bench/judge.py`:

```python
#!/usr/bin/env python3
"""Blind trap grading.

The judge never learns which arm produced a response - arm names do not appear
in its prompt - so it cannot be biased toward or against the plugin under test.

not_exercised is a first-class verdict. v0.1.0 recorded three traps that never
fired; without this category they would have been read as passes.
"""
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
JUDGMENTS = ROOT / "evals" / "snapshots" / "judgments.json"

VERDICTS = ("pass", "fail", "not_exercised")

TEMPLATE = """You are grading one response against one specific criterion.

The question that was asked:
---
%s
---

The criterion:
---
%s
---

The response to grade:
---
%s
---

Reply with a single JSON object and nothing else:
{"verdict": "pass" | "fail" | "not_exercised", "quote": "<short verbatim quote from the response that justifies the verdict, or empty>", "reason": "<one sentence>"}

Use "not_exercised" when the response does not engage the criterion at all -
for example it asks for missing context, declines for want of a live service,
or answers a different question. That is neither a pass nor a fail.
"""


def build_judge_prompt(case_prompt, trap, response):
    return TEMPLATE % (case_prompt.strip(), trap.strip(), response.strip())


def parse_verdict(raw):
    out = {"verdict": "not_exercised", "quote": "", "reason": "unparseable"}
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return out
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return out
    if not isinstance(d, dict) or d.get("verdict") not in VERDICTS:
        return out
    return {"verdict": d["verdict"], "quote": d.get("quote", "") or "",
            "reason": d.get("reason", "") or ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--cases", default="*")
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--out", default=str(JUDGMENTS))
    ap.add_argument("--claude-bin", default="claude")
    args = ap.parse_args()

    snap = bench_run.load_snapshot(args.results)
    if snap is None:
        sys.exit("no snapshot at %s - run run.py first" % args.results)

    prior = bench_run.load_snapshot(args.out) or {"metadata": {}, "judgments": []}
    done = set((j["case"], j["arm"], j["model"], j["rep"]) for j in prior["judgments"])

    # Same glob semantics as run.py --cases, so the two flags select alike.
    runs = [r for r in bench_run.usable(snap["runs"])
            if fnmatch.fnmatch(r["case"], args.cases)]
    for i, r in enumerate(runs, 1):
        key = (r["case"], r["arm"], r["model"], r["rep"])
        if key in done:
            continue
        case_dir = CASES / r["case"]
        expect = json.loads((case_dir / "expect.json").read_text())
        prompt = build_judge_prompt((case_dir / "prompt.md").read_text(),
                                    expect["trap"], r["text"])
        res = bench_run.call(args.claude_bin, args.model, prompt, None, str(ROOT))
        v = parse_verdict(res.get("text", "")) if res.get("ok") else \
            {"verdict": "not_exercised", "quote": "", "reason": "judge call failed"}
        v.update({"case": r["case"], "arm": r["arm"], "model": r["model"], "rep": r["rep"]})
        prior["judgments"].append(v)
        prior["metadata"] = {"judge_model": args.model,
                             "results_cksum": snap["metadata"].get("rules_cksum")}
        bench_run.save_snapshot(args.out, prior)
        print("[%d/%d] %-14s %-16s %-7s rep%d -> %s"
              % (i, len(runs), r["case"], r["arm"], r["model"], r["rep"], v["verdict"]))

    print("\nwrote %s (%d judgments)" % (args.out, len(prior["judgments"])))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 tests/test_bench.py`
Expected: PASS, `0 failure(s)`.

- [ ] **Step 5: Verify the judge runs end to end against a stub**

```bash
rm -f /tmp/snap.json /tmp/judg.json
python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh \
  --models haiku --reps 1 --cases floor --snapshot /tmp/snap.json
STUB_TEXT='{\"verdict\":\"pass\",\"quote\":\"q\",\"reason\":\"r\"}' \
  python3 evals/bench/judge.py --claude-bin tests/stubs/claude-stub.sh \
  --results /tmp/snap.json --out /tmp/judg.json
python3 -c "
import json; d=json.load(open('/tmp/judg.json'))
print('judgments:', len(d['judgments']))
print('verdicts:', sorted(set(j['verdict'] for j in d['judgments'])))
"
```

Expected: `judgments: 4`, `verdicts: ['pass']`.

- [ ] **Step 6: Commit**

```bash
git add evals/bench/judge.py tests/test_bench.py
git commit -m "feat: blind judge with a not_exercised verdict

Arm names never reach the judge. not_exercised exists because v0.1.0 had
three traps that never fired and would otherwise have read as passes."
```

---

### Task 6: Report, statistics and gates

**Files:**
- Create: `evals/bench/report.py`
- Test: `tests/test_bench.py` (extend)

**Interfaces:**
- Consumes: both snapshots, `metrics.score`, `metrics.never_cut_missing`.
- Produces: markdown to stdout or `--markdown OUT.md`; exit code 1 when any gate fails unless `--no-gate`.
- Produces: `aggregate(snapshot) -> dict` keyed `(case, arm, model)` → `{"output_tokens": median, "violations": median, "article_rate": median, "aux_verb_rate": median, "cost": median, "duration_ms": median, "n": int, "never_cut_failures": int}`; `gate_failures(agg, threshold) -> list of str`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_bench.py`, before the final `print`:

```python
import report as bench_report  # noqa: E402

synthetic = {
    "metadata": {"reps": 2, "models": ["haiku"], "laconic_level": "full",
                 "rules_cksum": "1", "generated_at": "x", "git_commit": "y",
                 "claude_cli_version": "z"},
    "arms": {"baseline": {"system_prompt": None}, "laconic": {"system_prompt": "r"}},
    "runs": [
        {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 0, "ok": True,
         "text": "The command removes the file from the staging area. It is safe.",
         "output_tokens": 100, "total_cost_usd": 0.01, "duration_ms": 1000},
        {"case": "floor", "arm": "baseline", "model": "haiku", "rep": 1, "ok": True,
         "text": "The command removes the file from the staging area. It is safe.",
         "output_tokens": 120, "total_cost_usd": 0.01, "duration_ms": 1000},
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 0, "ok": True,
         "text": "It removes the file from the staging area and does not touch the disk.",
         "output_tokens": 40, "total_cost_usd": 0.005, "duration_ms": 500},
        {"case": "floor", "arm": "laconic", "model": "haiku", "rep": 1, "ok": False},
    ],
}

agg = bench_report.aggregate(synthetic)
check("aggregates by case/arm/model", ("floor", "baseline", "haiku") in agg)
check("median output tokens", agg[("floor", "baseline", "haiku")]["output_tokens"] == 110)
check("failed runs excluded from n", agg[("floor", "laconic", "haiku")]["n"] == 1)
check("clean arms show no violations", agg[("floor", "laconic", "haiku")]["violations"] == 0)

check("clean run passes gates", bench_report.gate_failures(agg, 0.70) == [])

dirty = json.loads(json.dumps(synthetic))
dirty["runs"][2]["text"] = "removes file -> staging area. impl detail."
dirty["runs"][3] = dict(dirty["runs"][2], rep=1)
bad_agg = bench_report.aggregate(dirty)
fails_found = bench_report.gate_failures(bad_agg, 0.70)
check("degraded prose trips a gate", len(fails_found) > 0)
check("gate failure names the case", any("floor" in f for f in fails_found))

md = bench_report.render(synthetic, {"judgments": []}, 0.70)
check("report renders markdown", "| arm |" in md.lower() or "arm" in md)
check("report states the excluded count", "excluded" in md.lower())
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 tests/test_bench.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'report'`.

- [ ] **Step 3: Implement report.py**

Create `evals/bench/report.py`:

```python
#!/usr/bin/env python3
"""Turn the committed snapshots into markdown tables, and enforce gates.

Runs entirely offline: no network, no third-party packages. Exits non-zero
when a gate fails, so a rules regression fails a command instead of waiting
for somebody to notice a number moved.
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
JUDGMENTS = ROOT / "evals" / "snapshots" / "judgments.json"
ARM_ORDER = ["baseline", "terse-control", "word-compression", "laconic"]
# Rate gates are ratios of small integers on short answers. Below this floor the
# baseline itself carries too few articles or auxiliaries for the ratio to mean
# anything, and gating on it would produce flaky failures rather than findings.
RATE_FLOOR = 0.02


def _median(xs, default=0):
    return statistics.median(xs) if xs else default


def aggregate(snap):
    buckets = defaultdict(list)
    for r in bench_run.usable(snap["runs"]):
        buckets[(r["case"], r["arm"], r["model"])].append(r)

    agg = {}
    for key, runs in buckets.items():
        case = key[0]
        expect_path = CASES / case / "expect.json"
        never_cut = json.loads(expect_path.read_text())["never_cut"] \
            if expect_path.exists() else []
        scored = [metrics.score(r.get("text", "")) for r in runs]
        agg[key] = {
            "n": len(runs),
            "output_tokens": _median([r.get("output_tokens", 0) for r in runs]),
            "cost": _median([r.get("total_cost_usd", 0.0) for r in runs], 0.0),
            "duration_ms": _median([r.get("duration_ms", 0) for r in runs]),
            "violations": _median([s["violations"] for s in scored]),
            "article_rate": _median([s["article_rate"] for s in scored], 0.0),
            "aux_verb_rate": _median([s["aux_verb_rate"] for s in scored], 0.0),
            "never_cut_failures": sum(
                1 for r in runs
                if metrics.never_cut_missing(r.get("text", ""), never_cut)
            ),
            "spans": [sp for s in scored for sp in s["spans"]][:5],
        }
    return agg


def gate_failures(agg, threshold):
    out = []
    for (case, arm, model), v in sorted(agg.items()):
        if arm != "laconic":
            continue
        base = agg.get((case, "baseline", model))
        if v["violations"] > 0:
            out.append("%s/%s: %d readability violation(s) %s"
                       % (case, model, v["violations"], v["spans"]))
        if v["never_cut_failures"] > 0:
            out.append("%s/%s: %d never-cut failure(s)"
                       % (case, model, v["never_cut_failures"]))
        if base:
            if (base["article_rate"] >= RATE_FLOOR
                    and v["article_rate"] < threshold * base["article_rate"]):
                out.append("%s/%s: article rate %.3f below %.0f%% of baseline %.3f"
                           % (case, model, v["article_rate"], threshold * 100,
                              base["article_rate"]))
            if (base["aux_verb_rate"] >= RATE_FLOOR
                    and v["aux_verb_rate"] < threshold * base["aux_verb_rate"]):
                out.append("%s/%s: aux verb rate %.3f below %.0f%% of baseline %.3f"
                           % (case, model, v["aux_verb_rate"], threshold * 100,
                              base["aux_verb_rate"]))
    return out


def _arms_present(agg):
    return [a for a in ARM_ORDER if any(k[1] == a for k in agg)]


def _models_present(agg):
    return sorted(set(k[2] for k in agg))


def _by_arm_model(agg, field, arms, models, fmt="%s"):
    rows = ["| arm | " + " | ".join(models) + " |",
            "|---|" + "|".join("--:" for _ in models) + "|"]
    for arm in arms:
        cells = []
        for m in models:
            vals = [v[field] for k, v in agg.items() if k[1] == arm and k[2] == m]
            cells.append(fmt % _median(vals) if vals else "-")
        rows.append("| %s | %s |" % (arm, " | ".join(cells)))
    return "\n".join(rows)


def render(snap, judg, threshold):
    agg = aggregate(snap)
    arms, models = _arms_present(agg), _models_present(agg)
    meta = snap["metadata"]
    excluded = len([r for r in snap["runs"] if not r.get("ok")])

    out = []
    out.append("_Generated: %s · CLI: %s · commit: %s_" %
               (meta.get("generated_at"), meta.get("claude_cli_version"),
                meta.get("git_commit")))
    out.append("_Level: %s · reps: %s · rules cksum: %s_\n" %
               (meta.get("laconic_level"), meta.get("reps"), meta.get("rules_cksum")))
    out.append("**Excluded runs (call failed, never scored): %d**\n" % excluded)

    out.append("### Output tokens (median)\n")
    out.append(_by_arm_model(agg, "output_tokens", arms, models, "%.0f") + "\n")

    base = {m: _median([v["output_tokens"] for k, v in agg.items()
                        if k[1] == "baseline" and k[2] == m]) for m in models}
    ctrl = {m: _median([v["output_tokens"] for k, v in agg.items()
                        if k[1] == "terse-control" and k[2] == m]) for m in models}
    out.append("### Reduction vs baseline / vs terse control\n")
    rows = ["| arm | " + " | ".join(models) + " |",
            "|---|" + "|".join("--:" for _ in models) + "|"]
    for arm in arms:
        cells = []
        for m in models:
            vals = [v["output_tokens"] for k, v in agg.items() if k[1] == arm and k[2] == m]
            med = _median(vals)
            b = ("%.0f%%" % (100 * (1 - med / base[m]))) if base.get(m) else "-"
            c = ("%.0f%%" % (100 * (1 - med / ctrl[m]))) if ctrl.get(m) else "-"
            cells.append("%s / %s" % (b, c))
        rows.append("| %s | %s |" % (arm, " | ".join(cells)))
    out.append("\n".join(rows) + "\n")

    out.append("### Readability violations (median per response)\n")
    out.append(_by_arm_model(agg, "violations", arms, models, "%.1f") + "\n")
    out.append("### Article rate\n")
    out.append(_by_arm_model(agg, "article_rate", arms, models, "%.3f") + "\n")
    out.append("### Auxiliary-verb rate\n")
    out.append(_by_arm_model(agg, "aux_verb_rate", arms, models, "%.3f") + "\n")
    out.append("### Cost per call, USD (median)\n")
    out.append(_by_arm_model(agg, "cost", arms, models, "%.4f") + "\n")
    out.append("### Duration, ms (median)\n")
    out.append(_by_arm_model(agg, "duration_ms", arms, models, "%.0f") + "\n")

    nc = defaultdict(int)
    for (case, arm, model), v in agg.items():
        nc[arm] += v["never_cut_failures"]
    out.append("### Never-cut failures (total across cases)\n")
    out.append("| arm | failures |\n|---|--:|")
    for arm in arms:
        out.append("| %s | %d |" % (arm, nc[arm]))
    out.append("")

    verdicts = defaultdict(lambda: defaultdict(int))
    for j in judg.get("judgments", []):
        verdicts[(j["case"], j["arm"])][j["verdict"]] += 1
    if verdicts:
        out.append("### Trap verdicts by case\n")
        out.append("| case | arm | pass | fail | not_exercised |\n|---|---|--:|--:|--:|")
        for (case, arm) in sorted(verdicts):
            v = verdicts[(case, arm)]
            out.append("| %s | %s | %d | %d | %d |"
                       % (case, arm, v["pass"], v["fail"], v["not_exercised"]))
        out.append("")

    failures = gate_failures(agg, threshold)
    out.append("### Gates\n")
    if failures:
        out.append("**FAILED (%d):**\n" % len(failures))
        out.extend("- %s" % f for f in failures)
    else:
        out.append("All gates pass: 0 readability violations, 0 never-cut failures, "
                   "article and auxiliary rates within %.0f%% of baseline."
                   % (threshold * 100))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--judgments", default=str(JUDGMENTS))
    ap.add_argument("--threshold", type=float, default=0.70)
    ap.add_argument("--no-gate", action="store_true")
    ap.add_argument("--markdown")
    args = ap.parse_args()

    snap = bench_run.load_snapshot(args.results)
    if snap is None:
        sys.exit("no snapshot at %s - run run.py first" % args.results)
    judg = bench_run.load_snapshot(args.judgments) or {"judgments": []}

    md = render(snap, judg, args.threshold)
    if args.markdown:
        Path(args.markdown).write_text(md)
        print("wrote %s" % args.markdown)
    else:
        print(md)

    if not args.no_gate and gate_failures(aggregate(snap), args.threshold):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 tests/test_bench.py`
Expected: PASS, `0 failure(s)`.

- [ ] **Step 5: Verify the gate exit code both ways**

```bash
rm -f /tmp/snap.json
python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh \
  --models haiku --reps 1 --cases floor --snapshot /tmp/snap.json
python3 evals/bench/report.py --results /tmp/snap.json --judgments /dev/null --no-gate >/dev/null
echo "no-gate exit: $?"
STUB_TEXT='removes file -> staging. impl detail broken.' \
  python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh \
  --models haiku --reps 1 --cases floor --arms laconic --snapshot /tmp/snapbad.json
python3 evals/bench/report.py --results /tmp/snapbad.json --judgments /dev/null >/dev/null
echo "gated exit: $?"
```

Expected: `no-gate exit: 0`, `gated exit: 1`.

- [ ] **Step 6: Commit**

```bash
git add evals/bench/report.py tests/test_bench.py
git commit -m "feat: offline report with gates that fail by exit code"
```

---

### Task 7: Run the benchmark, publish, and retire the stale caveats

**Files:**
- Create: `evals/snapshots/{results,judgments}.json`
- Create: `evals/results/2026-07-30-benchmark.md`
- Modify: `README.md`, `docs/v0.1.0-known-limits.md`, `evals/CRITERIA.md`

**Interfaces:**
- Consumes: everything from Tasks 1-6.

- [ ] **Step 1: Run the full gate first**

```bash
bash tests/test_rules.sh && bash tests/test_laconic.sh \
  && bash tests/test_evals_layout.sh \
  && python3 tests/test_metrics.py && python3 tests/test_bench.py \
  && claude plugin validate . --strict \
  && claude plugin validate .claude-plugin/plugin.json --strict
```

Expected: every suite 0 failures, both validations pass.

- [ ] **Step 2: Generate**

```bash
python3 evals/bench/run.py
```

Expected: 320 lines of progress, roughly 1.5-2 hours, ending with the failed count. Re-run the identical command if interrupted — completed keys are skipped.

- [ ] **Step 3: Judge**

```bash
python3 evals/bench/judge.py
```

Expected: one verdict per usable run.

- [ ] **Step 4: Calibrate the threshold against the observed spread**

```bash
python3 evals/bench/report.py --no-gate | sed -n '/Article rate/,/Cost per/p'
```

The spec commits to publishing the observed values and revising the 0.70 factor if the
arms separate by less than 2×. Compare the `baseline` and `word-compression` rows: if
`word-compression`'s article rate is not at most half of `baseline`'s, the detector is
not separating the arms — record that in the writeup and set the threshold from what
was actually observed rather than keeping 0.70 silently.

- [ ] **Step 5: Write the report**

```bash
python3 evals/bench/report.py --markdown evals/results/2026-07-30-benchmark.md
```

Then prepend to that file: the run's configuration, the calibration decision from Step 4
with the observed numbers, and all seven honesty notes verbatim from the spec's
"Honesty notes" section — single-turn not sessions, cache-creation overstating session
cost, output tokens as the headline and why, injection cost included, detectors as
validated heuristics rather than a parser, n=5 not a powered experiment, and the
word-compression arm being a synthetic instruction whose wording is published.

- [ ] **Step 6: Add the headline table to the README**

Replace the closing sentences of the README's `evals/run.sh` paragraph — the ones
reading "These are single-sample, cheapest-model runs meant to catch regressions in the
rule set, not a benchmark — there's no validated token-reduction number to quote here,
only pass/fail against the criteria in that file." — with a `## Benchmark` section
carrying the median output-token reduction, the readability violation counts per arm,
the never-cut failure counts, a one-line statement of the two-axis result, and a link to
`evals/results/2026-07-30-benchmark.md`. Include the honesty note that these are
single-turn measurements which overstate session cost.

Document the commands too:

```bash
python3 evals/bench/run.py      # generate (~320 calls, 1.5-2 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```

- [ ] **Step 7: Retire the two resolved caveats**

In `docs/v0.1.0-known-limits.md`, replace the "Eval results" section's single-sample
framing and the `evals/results/` gitignored entry with a note that both are resolved by
`evals/results/2026-07-30-benchmark.md`, naming the snapshot commit. Re-examine the two
deferred findings — `decision`'s unrequested alternative and the `badnews` closing offer
— against the n=5 two-model data, and record for each whether it reproduced. That is the
question the deferral was waiting on.

- [ ] **Step 8: Add the bench commands to the development gate**

In the README's Development section, extend the gate command to include the new suites:

```bash
bash tests/test_rules.sh && bash tests/test_laconic.sh \
  && bash tests/test_evals_layout.sh \
  && python3 tests/test_metrics.py && python3 tests/test_bench.py \
  && claude plugin validate . --strict \
  && claude plugin validate .claude-plugin/plugin.json --strict
```

- [ ] **Step 9: Verify the published numbers regenerate offline**

```bash
python3 evals/bench/report.py --no-gate > /tmp/regen.md
diff <(tail -n +2 /tmp/regen.md) <(tail -n +2 evals/results/2026-07-30-benchmark.md) \
  || echo "prepended prose differs, table content is what matters"
```

Expected: the generated tables match what was published, proving the numbers are
reproducible from the committed snapshot without network access.

- [ ] **Step 10: Commit**

```bash
git add evals/snapshots evals/results README.md docs/v0.1.0-known-limits.md evals/CRITERIA.md
git commit -m "feat: publish the first four-arm benchmark

n=5 across haiku and sonnet, compression and readability measured
together. Snapshot committed so every published number regenerates
offline and any future change to them is reviewable as a diff."
```

---

## Self-Review

**Spec coverage.** Layout and `run.sh` → Task 1. Detectors and validation suite → Task 2. Cases, fixtures, never-cut lists → Task 3. Arms, isolation, iteration order, resume, failure exclusion, command surface → Task 4. Blind judge with `not_exercised` → Task 5. Stats, tables, gates and exit codes → Task 6. Threshold calibration, writeup, README, retired caveats → Task 7. Snapshot schema is fixed in Task 4 and consumed unchanged in 5 and 6.

**Deviation recorded:** never-cut keywords live in `expect.json`, not `CRITERIA.md` — reasoning at the top of the File Structure section.

**Deferred items** from the spec (agentic benchmark, third-party plugin arms, Opus arm) have no tasks by design.

**Type consistency.** `metrics.score()` returns the same key set consumed by `report.aggregate()`. `run.parse_cli_json()` returns the field names written into the snapshot and read by `report.aggregate()` and `judge.main()`. `bench_run.call()` has one signature — `(claude_bin, model, prompt, system_prompt, cwd)` — used by both `run.main()` and `judge.main()`. `expect.json`'s two keys are written in Task 3 and read in Tasks 5 and 6.

**Known risk.** Task 7 Step 2 depends on a live model and ~2 hours of wall clock. It is resumable by design, and Tasks 1-6 are fully verifiable offline against stubs, so a failure there blocks only publication and not the harness.

## Pre-flight verification already performed

The detector code in Task 2 was executed against its own fixtures before this plan was
committed, which found five defects now fixed in the text above. Implementers should
expect these assertions to pass as written:

| Fixture | words | violations | arrows | abbrevs | lowercase starts | article rate |
| --- | --: | --: | --: | --: | --: | --: |
| GOOD | 59 | 0 | 0 | 0 | 0 | 0.203 |
| BAD | 43 | 11 | 3 | 4 | 4 | 0.000 |
| CODE | 35 | 0 | 0 | 0 | 0 | 0.171 |

The defects found, recorded so they are not reintroduced:

1. **`_lowercase_starts` iterated raw lines**, so the continuation of every hard-wrapped
   sentence scored as a fragment — two false positives on GOOD and two on CODE. Fixed by
   `_paragraph_prose`, which rejoins wrapped lines and drops structural markdown.
2. **The CODE fixture contained a genuine prose arrow** (`… /docs -> section 4`) after
   the URL, so the detector was right and the fixture was wrong. Changed to `in section 4`.
3. **`b["symbol_connectors"] >= 4`** was unmeetable; BAD contains exactly 3 arrows.
4. **The negative probe expectation** of `1, 1, 1` was wrong: `"the impl is broken."`
   correctly scores 2, tripping both the abbreviation and lowercase-start detectors.
5. **`Path.match("*" + cases + "*")`** worked only by accident on the default, and
   `judge.py` used substring matching for the same flag. Both now use `fnmatch` on the
   case name, so `--cases` selects identically in both tools.

---

## Amendments during execution

The plan's code blocks above are the text as written before execution. Review found
defects in some of it; the committed implementation differs as follows, and the
committed code is authoritative.

**Task 2, `metrics.py` — abbreviation-aware sentence splitting (rounds 1-2).**
`SENTENCE_SPLIT` alone treats `e.g.` / `i.e.` / `vs.` as sentence ends, so the
lowercase continuation scored as a fragment. That over-reports violations on correct
prose in *every* arm, and the laconic gate is `violations == 0`, so one false positive
fails the gate outright. Fixed with an `ABBREV_DOT` mask applied before splitting.
Round 2 narrowed the masked list after the first attempt masked unconditionally and
hid real violations when an abbreviation genuinely ended a sentence (`"…, etc. it
makes no sense."`). Final rule: mask only abbreviations that are essentially never
sentence-final (`e.g i.e cf vs approx Fig Dr Mr Mrs Ms Prof`); never mask ones that
commonly are (`etc al Inc Ltd St Ave`).

`AUX` also gained the contracted negations (`doesn't`, `isn't`, `can't`, …), which the
original set counted as zero auxiliaries, plus assertions covering `aux_verb_rate` —
a gated interface key that had none. Suite grew 16 → 23 assertions.

**Task 3, `never_cut` keywords (rounds 1-2).** `never_cut` is a case-insensitive
*substring* match, and the plan's original keywords ignored that. `"if"` on
`conditional` — the flagship case — matched inside *different*, *specify*, *identify*,
making the check vacuous. `"refresh"`, `"sign"`, and `"stag"` were the literal topic of
their own prompts. `"3 failed"` and `"test_billing"` missed correct paraphrases.

The governing principle, now recorded in `CRITERIA.md`: **`never_cut` carries only
tokens a correct answer cannot avoid** — literal identifiers, flags, status codes,
schema names. Conceptual requirements have many valid phrasings and belong to the
judge's `trap` instead, because a substring check a correctly-phrased answer can miss
produces false alarms. Round 2 applied it to two keywords that survived round 1 on the
same flaw: `inflight` (the natural idiom is "in-flight", which has no contiguous
match) and `expir` (the trap's own prose says "lifetime").

Final values — `decision` `[]`, `walkthrough` `["401"]`, `destructive`
`["cascade","invoices"]`, `badnews` `["proration"]`, `conditional` `["leak"]`,
`ordered-steps` `[]`, `floor` `[]`, `code-fidelity` `["-size","-mtime"]`.
The three empty lists are deliberate and documented as such.
