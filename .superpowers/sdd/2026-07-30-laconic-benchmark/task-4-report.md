# Task 4 Report: Generation Harness

**Status:** DONE (round 4)

**Commit:** cd2db0ee3d31a741fa56c842d17b458beffc912d (round 3); see "Round 4" section below for the final fix and its commit.

**Test Summary:** 34 unit tests pass. Resume check (4→0 runs) and failure recording (recorded: 1 usable: 0) both verified. Guard is now covered by an extracted predicate plus a subprocess end-to-end test; loose-guard reintroduction now fails the suite (see Round 4).

## Fixes Applied

### 1. CRITICAL: Path Resolution (breaks all real runs)
**Problem:** `Path("claude").resolve()` returns `<repo>/claude` (nonexistent), causing every call to return `{"ok": false}`. A 320-call run would produce all failures.

**Solution:** Added `resolve_claude_bin(arg)` that distinguishes bare command names (resolved via `shutil.which()`) from paths (resolved to absolute). Falls back to bare name if not found in PATH, letting subprocess raise OSError naturally.

**Proof the fix works:** Test assertion `resolve_claude_bin("claude") != str(ROOT / "claude")` would fail against old code. Verified:
```
Old broken resolve('claude'): /home/jordan/projects/laconic/claude
Does it exist? False
```

### 2. IMPORTANT: Snapshot Atomicity
**Problem:** Non-atomic writes to snapshot file across 320+ saves in multi-hour run. Interrupt mid-write truncates file, destroying all results.

**Solution:** Write to `.tmp`, then atomic `os.replace()` ensures snapshot either fully updates or stays unchanged.

### 3. IMPORTANT: Snapshot Schema
**Problem:** Missing `source` field in laconic arm. Reader cannot tell which level/hook produced the data.

**Solution:** Added `"source": "hooks/laconic.sh start @ {level}"` to laconic arm. Verified in snapshot:
```json
"laconic": {
  "source": "hooks/laconic.sh start @ full",
  "system_prompt": "..."
}
```

### 4. IMPORTANT: Test Coverage
**Added assertions:**
- `resolve_claude_bin("claude")` doesn't return nonexistent `<repo>/claude` 
- `resolve_claude_bin("tests/stubs/claude-stub.sh")` returns absolute existing path
- `call()` with resolved stub path succeeds and extracts text
- Snapshot laconic arm has `source` field containing level

## End-to-End Verification

**Resume check (4→0 runs):**
```
First run:  [1/4] ... [2/4] ... [3/4] ... [4/4] ... → 4 runs
Second run: (no output, all resumed)
Snapshot:   runs: 4, all ok: True
```

**Failure recording (recorded: 1 usable: 0):**
```
STUB_FAIL=1 → [1/1] FAILED
Snapshot:   recorded: 1, usable: 0
```

Both verified with fixed code.

---

## Re-Review Fixes

### 5. Fail-Fast Binary Validation (residual gap in Finding 1)
**Problem:** When `shutil.which()` returns None for an unresolvable binary, `resolve_claude_bin` falls back to the bare name. The call then fails silently, recording all 320 calls as failures. Same outcome as the original Critical, reached by a different path.

**Solution:** Added guard in `main()` right after resolving:
```python
if not (shutil.which(claude_bin) or Path(claude_bin).exists()):
    sys.exit("claude binary not found: %s (set --claude-bin or fix PATH)" % args.claude_bin)
```

**Verification:** Tested with restricted PATH to confirm guard triggers:
```bash
PATH=/usr/bin:/bin python3 evals/bench/run.py --claude-bin claude --models haiku --reps 1 --cases floor
# Output: claude binary not found: claude (set --claude-bin or fix PATH)
```

Confirmed guard does NOT fire when binary is resolvable, so normal runs are unaffected.

### 6. Complete Bare-Name Test Coverage (Finding 4 - partial coverage)
**Problem:** Previous test only exercised path-like arguments (relative paths → absolute). The `shutil.which()` branch was never tested end-to-end, leaving the residual gap in Finding 1 undetected.

**Solution:** Added bare-name test that:
1. Creates temp dir with copy of stub executable
2. Modifies PATH to include that dir
3. Tests `resolve_claude_bin(bare_name)` finds it via `shutil.which()`
4. Tests `call(bare_name, ...)` succeeds end-to-end
5. Restores PATH even if assertion fails

**Added tests (4 new):**
- `resolve bare name finds it in PATH`
- `call with bare-name resolution succeeds`
- `unresolvable name doesn't exist as path`
- `resolve returns bare name when not in PATH`

All assertions exercised both success and failure paths. Verified that the new fail-fast guard catches the unresolvable case before it reaches `call()`.

## Final Verification Summary

All 29 tests pass. Both Step 6 end-to-end verifications confirmed:

**Resume (4→0):**
```
$ rm -f /tmp/snap.json
$ python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh --models haiku --reps 1 --cases floor --snapshot /tmp/snap.json
[1/4] floor baseline haiku rep0 ok
[2/4] floor terse-control haiku rep0 ok
[3/4] floor word-compression haiku rep0 ok
[4/4] floor laconic haiku rep0 ok
wrote /tmp/snap.json (4 runs, 0 failed)
$ python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh --models haiku --reps 1 --cases floor --snapshot /tmp/snap.json
wrote /tmp/snap.json (4 runs, 0 failed)
$ python3 -c "import json; s=json.load(open('/tmp/snap.json')); print('runs:', len(s['runs']), 'all ok:', all(r['ok'] for r in s['runs']))"
runs: 4 all ok: True
```

**Failure (recorded: 1, usable: 0):**
```
$ rm -f /tmp/snapfail.json
$ STUB_FAIL=1 python3 evals/bench/run.py --claude-bin tests/stubs/claude-stub.sh --models haiku --reps 1 --cases floor --arms baseline --snapshot /tmp/snapfail.json
[1/1] floor baseline haiku rep0 FAILED
wrote /tmp/snapfail.json (1 runs, 1 failed)
$ python3 -c "import json,sys; sys.path.insert(0,'evals/bench'); import run; s=json.load(open('/tmp/snapfail.json')); print('recorded:', len(s['runs']), 'usable:', len(run.usable(s['runs'])))"
recorded: 1 usable: 0
```

---

## Final Re-Review Fix

### 7. Tighten Guard: Reject Non-Executable Files and Directories
**Problem:** The guard `if not (shutil.which(claude_bin) or Path(claude_bin).exists())` was too loose. It admitted:
- Non-executable files: `Path.exists()` returns True, but file can't execute
- Directories: `Path.exists()` returns True, but directory can't execute

Both then fail with `PermissionError`/`IsADirectoryError`, caught as `OSError` in `call()`, recorded as `ok: false`. Same silent-100%-failure symptom.

**Solution:** Drop the `Path.exists()` fallback and use only `shutil.which()`:
```python
if not shutil.which(claude_bin):
    sys.exit("claude binary not found or not executable: %s "
             "(set --claude-bin or fix PATH)" % args.claude_bin)
```

`shutil.which()` already rejects both non-executable files and directories; it only accepts genuinely executable files or bare commands found in PATH.

**Proof old guard was loose:**
```python
# Old guard with Path.exists() fallback
non_exec_file = Path("/tmp/file")  # exists but not executable
non_exec_file.write_text("#!/bin/sh\necho hi")
shutil.which(str(non_exec_file))    # None (rejects it)
Path(non_exec_file).exists()         # True (old guard allows it!)

directory = Path("/tmp/dir")
directory.mkdir()
shutil.which(str(directory))         # None (rejects it)
Path(directory).exists()             # True (old guard allows it!)
```

**Assertions added (2 new):**
- `shutil.which rejects non-executable file` — verifies the guard catches this
- `shutil.which rejects directory` — verifies the guard catches this

**Test coverage:** Both assertions pass with strict guard, would fail with loose guard.

**Final verification:** All 31 tests pass. Both Step 6 end-to-end checks confirmed:
- Resume (4→0): ✓
- Failure (recorded: 1, usable: 0): ✓

---

## Round 4: Genuine Guard Coverage

**Problem:** The two assertions added in round 3 ("shutil.which rejects non-executable file", "shutil.which rejects directory") tested `shutil.which` directly — a stdlib function, not the guard in `main()`. Restoring the old loose guard (`if not (shutil.which(claude_bin) or Path(claude_bin).exists())`) and re-running the suite gave 0 failures: every assertion still passed against the reintroduced defect. No test exercised `main()`'s guard branch at all.

**Fix, two parts:**

1. **Extracted the guard's condition** into a named predicate in `run.py` so the test and the guard cannot diverge:
   ```python
   def claude_bin_usable(claude_bin):
       """The fail-fast guard's condition, factored out so tests exercise the
       real thing instead of re-deriving it. Rejects missing paths, directories,
       and non-executable files - shutil.which() already handles all three."""
       return bool(shutil.which(claude_bin))
   ```
   `main()` now calls `claude_bin_usable(claude_bin)` instead of inlining the check. The two hollow `shutil.which(...)` assertions in `tests/test_bench.py` were replaced with assertions against `claude_bin_usable` itself: non-executable file → False, directory → False, the resolved stub → True.

2. **Added an end-to-end subprocess test**, immune to refactoring games: invokes `evals/bench/run.py` via `sys.executable` with `--claude-bin` pointing at a non-executable temp file and a fresh temp `--snapshot` path, then asserts the exit code is non-zero and the snapshot file was never created (the guard runs before any work, so this is fast — no live model calls).

**Acceptance-bar check (per instructions):** temporarily restored the loose guard in `run.py`:
```python
def claude_bin_usable(claude_bin):
    """LOOSE GUARD FOR ACCEPTANCE-BAR TEST ONLY."""
    return bool(shutil.which(claude_bin) or Path(claude_bin).exists())
```
Ran the full suite — **4 failures, exit code 1**:
```
ok   claude_bin_usable accepts a real executable
FAIL claude_bin_usable rejects non-executable file
FAIL claude_bin_usable rejects directory
FAIL subprocess: guard exits non-zero for non-executable claude-bin
FAIL subprocess: guard runs before any work, no snapshot written
...
4 failure(s)
EXIT CODE: 1
```
Restored the correct guard, re-ran — **0 failures, exit code 0**, all 34 assertions pass (31 original + 3 net new: one added `claude_bin_usable accepts a real executable` check plus the two subprocess checks; the two hollow `shutil.which` checks were replaced in place, not added to).

**Final verification, all still hold:**
- Full suite: 34/34 pass, `0 failure(s)`, exit code 0.
- Resume (4→0):
  ```
  wrote /tmp/snap.json (4 runs, 0 failed)   [first run]
  wrote /tmp/snap.json (4 runs, 0 failed)   [second run, no new output lines]
  runs: 4
  all ok: True
  ```
- Forced failure:
  ```
  [1/1] floor          baseline         haiku   rep0 FAILED
  wrote /tmp/snapfail.json (1 runs, 1 failed)
  recorded: 1 usable: 0
  ```

**Status:** DONE.
