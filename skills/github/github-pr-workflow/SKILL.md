---
name: github-pr-workflow
description: Full PR lifecycle: branch, commit, push, open review, merge via gh CLI.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, pr, pull-requests]
---

# Pull Request Workflow

End-to-end PR management using `gh`.

## Branch & Commit

```bash
# Create feature branch
git checkout -b feat/inventory-cache
git add . && git commit -m "feat: add Redis caching to inventory API"

# Push and track
git push -u origin feat/inventory-cache
```

## Opening a PR

```bash
# Simple PR linked to issue #42
gh pr create \
  --base main \
  --title "feat: add Redis caching to inventory API" \
  --body "Addresses #42 — improves response time from 800ms to <50ms." \
  --label enhancement

# With reviewers and assignees
gh pr create \
  --reviewer alice,bob \
  --assignee @me \
  --draft \
  --title "WIP: auth refactor" \
  --body "Draft — needs security review before merging."
```

## Managing PRs

```bash
# List my PRs
gh pr list --state open --assignee @me

# View details
gh pr view 137 --json number,title,state,mergeable,statusCheckRollup

# Update description/comment
gh pr edit 137 --body "Updated with benchmarks"
gh pr comment 137 --body "Rebased onto main ✅"

# Merge (when CI passes)
gh pr merge 137 --squash --delete-branch

# Or rebase merge (keeps individual commits)
gh pr merge 137 --rebase --delete-branch
```

## Review Flow

```bash
# Check out PR locally
gh pr checkout 137

# View diffs
gh pr diff 137 | head -100
gh pr views 137  # inline comments in browser

# Approve / request changes
gh pr review 137 --approve --body "Looks good, minor nits noted"
gh pr review 137 --request-changes --body "Needs fix in error handling"
```

## Common Patterns

| Scenario | Command |
|----------|---------|
| Cancel merge | `gh pr cancel-merge 137` |
| Add label to PR | `gh pr edit 137 --add-label blocked` |
| Link to issue | `gh pr close 137 --closing-ref-closes 42` |
| Draft PR ready | `gh pr ready 137` |
| Sync fork | `gh repo sync <owner>/<repo>` |
