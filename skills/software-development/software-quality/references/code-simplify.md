# Code Simplify — Parallel 3-Agent Cleanup

Condensed from the former `simplify-code` skill.

Review recent code changes with three focused reviewers running in parallel,
aggregate findings, and apply fixes.

## When to Use

Trigger when the user says: "simplify", "review my code", "clean up my changes"

Optional modifiers: `focus on efficiency` (run only one reviewer), `dry run`
(report only, don't apply), `scope` (last commit, staged, specific file).

## The Process

### Phase 1 — Identify changes

```bash
# Default: uncommitted working tree changes
git diff
# Or: staged changes
git diff --staged
# Last commit
git diff HEAD~1
```

### Phase 2 — Launch three reviewers in parallel

Use `delegate_task` batch mode — all three run concurrently.

**Reviewer 1 — Code Reuse:** Finds functionality that duplicates existing
codebase utilities. Must provide file:line evidence of the existing utility.

**Reviewer 2 — Code Quality:** Finds redundant state, parameter sprawl,
copy-paste-with-variation, leaky abstractions, stringly-typed code.

**Reviewer 3 — Efficiency:** Finds unnecessary work, missed concurrency,
hot-path bloat, TOCTOU anti-patterns, memory issues, overly broad reads.

Each reviewer gets the complete diff plus repo path. Toolsets: terminal, file, search.

### Phase 3 — Aggregate and apply

1. Merge findings, dedupe
2. Discard false positives
3. Resolve conflicts (correctness > stated focus > readability > micro-perf)
4. Apply fixes with `patch` / `write_file`
5. Verify: run targeted tests + linter for touched files
6. Summarize what changed

## Pitfalls

- Max ~3 reviewers — more doesn't add coverage
- Give the WHOLE diff to each reviewer
- Require `file:line` evidence — drop unsupported claims
- Apply ≠ rewrite. Scope edits to what the diff touched
- Large diffs (>2000 lines): warn user, offer to scope down
