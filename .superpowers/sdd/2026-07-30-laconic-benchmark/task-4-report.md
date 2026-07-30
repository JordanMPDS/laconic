# Task 4 Report: Generation Harness

**Status:** DONE

**Commit:** c947f30ceab9f5f7dcf945a80f97ddb9b61e8a1c

**Test Summary:** All 25 unit tests pass (original 17 + 8 new). Resume check (4→0 runs) and failure recording (recorded: 1 usable: 0) both verified.

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
