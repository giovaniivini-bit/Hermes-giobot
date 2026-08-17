---
name: github
description: GitHub operations including auth, issues, PRs, repo management, and code review.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, auth, issues, pull-requests, repo-management, code-review]
---

# GitHub Operations

This skill covers various GitHub operations via the CLI and API.

## Authentication

See the `github-auth` skill for setting up GitHub authentication (HTTPS tokens, SSH keys, gh CLI login).

## Issues

See the `github-issues` skill for creating, triaging, labeling, and assigning GitHub issues.

## Pull Requests

See the `github-pr-workflow` skill for the full GitHub PR lifecycle: branch, commit, open, CI, merge.

## Code Review

See the `github-code-review` skill for reviewing PRs: diffs, inline comments via gh or REST.

## Repository Management

See the `github-repo-management` skill for cloning, creating, forking repos; managing remotes and releases.

## Reference

- GitHub CLI: https://cli.github.com/
- GitHub REST API: https://docs.github.com/en/rest

## Pitfalls

### Verify sub-skill refs before claiming completeness
This SKILL.md references 5 sub-skills (`github-auth`, `github-issues`, `github-pr-workflow`, `github-code-review`, `github-repo-management`). When editing or loading this skill, ALWAYS verify each referenced sub-skill loads successfully with `skill_view(name=<ref>)`. If any return "not found", report the gap to the user — do not assume they exist on disk. A common failure mode: SKILL.md is updated to reference new sub-skills but the actual files are never created.
