---
name: github-issues
description: Create, triage, label, assign, and close GitHub issues programmatically.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, issues]
---

# GitHub Issues Operations

Manage issues via `gh` CLI or GitHub REST API.

## Creating Issues

```bash
# Basic issue
gh issue create --title "Fix login timeout" --body "Users report 502 errors after midnight" --label "bug"

# With assignee, milestone, project
gh issue create \
  --title "Add caching layer to inventory API" \
  --body "Performance degraded with >10k SKUs. Proposed: Redis cache + invalidation strategy." \
  --assignee @me \
  --label "enhancement,performance" \
  --milestone "Q3 Optimizations"

# Multiple labels at once
gh issue create --title "Bug" --label "bug,critical,p0"
```

## Listing & Filtering

```bash
# My open issues
gh issue list --state open --assignee @me --limit 50

# Unassigned critical bugs
gh issue list --state open --label critical --label bug --json title,number,assignees,labels

# Search across repo
gh search issues "timeout" --state all --sort created --order desc --limit 20
```

## Triage Workflow

```bash
# Label new issues by category
gh issue edit 42 --add-label "needs-triage"
gh issue edit 42 --remove-label "needs-triage" --add-label "bug,severity-high" --assignee userX

# Close stale/duplicate
gh issue close 42 --comment "Duplicate of #38" --close-reason duplicate
```

## Automation Tips

- Use `--json` flag for structured output (machine-readable)
- Combine `gh issue list` with `jq` for scripting
- Set default labels in repo settings (`Issues → Manage labels`)
