---
name: software-quality
description: "Code quality processes: TDD, systematic debugging, pre-commit code review, and developer productivity workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [testing, tdd, debugging, code-review, quality, verification]
---

# Software Quality Workflows

Three complementary methodologies for producing quality code: TDD (write tests first), Systematic Debugging (find root cause before fixing), and Pre-Commit Code Review (security + correctness gate before commit).

---

## 1. Test-Driven Development (TDD)

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing. Write the test FIRST, watch it fail, then write minimal code to pass.

### RED — Write Failing Test

One behavior per test, clear descriptive name, real code over mocks:

```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'
    result = retry_operation(operation)
    assert result == 'success'
    assert attempts == 3
```

### Verify RED — Watch It Fail (mandatory)

```bash
pytest tests/test_feature.py::test_specific_behavior -v
```

Confirm: test fails for expected reason (feature missing), not from typos.

### GREEN — Minimal Code

Write simplest code to pass. Cheating is OK (hardcode, copy-paste, skip edge cases). Refactor after green.

```bash
pytest tests/test_feature.py::test_specific_behavior -v  # verify green
pytest tests/ -q  # check regressions
```

### REFACTOR — Clean Up

Remove duplication, improve names, extract helpers. Keep tests green throughout.

### Common Rationalizations (all wrong)

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests-after prove nothing — they pass immediately. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Unverified code is debt. |

### Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

---

## 2. Systematic Debugging

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure. NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

### Phase 1: Root Cause Investigation

1. **Read error messages carefully** — use `read_file` on source, `search_files` for strings
2. **Reproduce consistently** — if not reproducible, gather data, don't guess
3. **Check recent changes:** `git log --oneline -10`, `git diff`
4. **Gather evidence in multi-component systems** — log data at each component boundary
5. **Trace data flow** — where does the bad value originate? Fix at the source.

### Phase 2: Pattern Analysis

1. Find similar working code in the same codebase
2. Compare against references — read the reference implementation completely
3. Identify differences between working and broken
4. Understand dependencies

### Phase 3: Hypothesis and Testing

1. Form single hypothesis: "I think X is the root cause because Y"
2. Test minimally — smallest possible change, one variable at a time
3. Verify before continuing

### Phase 4: Implementation

1. Create failing test case (simplest reproduction)
2. Implement single fix addressing root cause
3. Verify fix, check no regressions
4. If fix doesn't work — STOP after 3 attempts and question the architecture

### The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

### Language-Specific References

See `references/python-debugging.md` (pdb, debugpy, remote-pdb) and `references/node-debugging.md` (node inspect, chrome-remote-interface/CDP).

---

## 3. Pre-Commit Code Review

**Core principle:** No agent should verify its own work. Fresh context finds what you miss.

### Step 1: Get the diff

```bash
git diff --cached  # staged changes
git diff HEAD~1 HEAD  # last commit
```

### Step 2: Static security scan

```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"

# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"

# Dangerous eval/exec
git diff --cached | grep "^+" | grep -E "\beval\(|\bexec\("

# SQL injection
git diff --cached | grep "^+" | grep -E "execute\(f\"|\.format\(.*SELECT"
```

### Step 3: Baseline tests and linting

Detect project language, run tools against baseline (stash → run → pop). Only NEW failures block the commit.

### Step 4: Self-review checklist

- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Input validation on user-provided data
- [ ] SQL queries use parameterized statements
- [ ] File operations validate paths (no traversal)
- [ ] External calls have error handling (try/catch)
- [ ] No debug print/console.log left behind
- [ ] No commented-out code

### Step 5: Independent reviewer subagent

Use `delegate_task` with the diff + static scan results. Fail-closed: non-empty security_concerns/logic_errors → passed=false.

### Step 6-7: Evaluate results + auto-fix loop

Max 2 fix-and-reverify cycles. If still failing after 2, escalate to user.

### Step 8: Commit

```bash
git add -A && git commit -m "[verified] <description>"
```

### Additional reviews

See `references/code-simplify.md` (parallel 3-agent code cleanup) and `references/codebase-inspection.md` (pygount LOC analysis).

---

## Pitfalls (all sections)

- **Empty diff** — check `git status`, tell user nothing to verify
- **No test framework found** — skip regression check, reviewer still runs
- **Auto-fix introduces new issues** — counts as new failure, cycle continues
- **pdb under pytest-xdist hangs** — always use `-p no:xdist`
- **`breakpoint()` in CI non-TTY hangs** — never commit it
- **Don't guess job_id** for cron jobs — always list first