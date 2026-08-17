---
name: github-code-review
description: Review PRs with diffs, inline comments, and automated checks via gh CLI or REST API.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, review, code-review]
---

# Code Review Operations

Review pull requests programmatically using `gh` CLI or the GitHub REST API.

## Viewing Changes

```bash
# Full diff for a PR
gh pr diff 137

# Patch file-specific diff
gh pr diff 137 -- filepath/to/file.py

# File contents at PR HEAD vs base
gh api repos/{owner}/{repo}/pulls/137/files --jq '.[].filename'
```

## Automated Checks

```bash
# View CI status
gh pr checks 137

# Wait for CI to pass before reviewing further
gh pr checks 137 --watch

# View individual check logs
gh api repos/{owner}/{repo}/check-runs --jq '.check_runs[] | select(.status=="in_progress") | .name'
```

## Inline Comments (via REST)

```bash
# Single comment on specific line
gh api repos/{owner}/{repo}/pulls/137/comments \
  -X POST \
  -F 'body="Consider extracting this into a constant"' \
  -F 'path="src/utils.ts"' \
  -F 'line=42' \
  -F 'side=RIGHT'

# Suggestion (code snippet)
curl -s https://api.github.com/repos/{owner}/{repo}/pulls/137/comments \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"body":"Try using array.map() here","path":"file.js","line":15}'
```

## Submitting Reviews

```bash
# Approve
gh pr review 137 --approve --body "LGTM ✅"

# Request changes
gh pr review 137 --request-changes --body "Needs fix: edge case in error handler"

# Comment only (no approval/changes)
gh pr review 137 --comment --body "Interesting approach — worth benchmarking against X"
```

## Review Script Pattern

```bash
# Auto-check CI, then open browser for human review
gh pr checks 137 && echo "CI passing" && gh pr view 137 &
```

## Best Practices

- Always check `gh pr checks` before deep-diving into code
- Use `--json` output for machine processing
- Group related inline comments into a single review thread when possible
- Prefer constructive feedback: suggest alternatives, not just complaints
