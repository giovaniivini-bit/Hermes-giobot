---
name: github-repo-management
description: Clone, create, fork repos; manage remotes, releases, branches, and repository settings via gh CLI.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, repo, management, clone, fork, release]
---

# Repository Management

Common operations for managing GitHub repositories via `gh` CLI and git.

## Cloning & Setup

```bash
# Clone from URL
gh repo clone owner/repo ./local-path

# Secure clone (HTTPS with credential helper)
git clone https://github.com/owner/repo.git

# Fork & clone
gh repo fork owner/repo --clone --remote
```

## Creating Repositories

```bash
# Private repo in current org
gh repo create my-project --private --description "Short description" --source=. --push

# With topics and default branch
gh repo create new-service --private --topic microservice --default-branch main

# From template
gh repo create my-org/project --template template-repo
```

## Branch Management

```bash
# List all branches
gh branch list --repo owner/repo

# Delete remote branch
gh branch delete feature/old-work -r

# Protect branch (admin)
gh api repos/owner/repo/branches/main/protection \
  -X PUT \
  -F 'required_status_checks={"strict":true,"contexts":["ci"]}'

# Set protected branch rules
gh api repos/owner/repo/branches/main/protection \
  -X PUT -F 'required_pull_request_reviews={"dismissal_restrictions":{"users":[]},"bypass_pull_request_allowances":{"repos":[],"users":[],"teams":[]}}'
```

## Releases

```bash
# Create a release
gh release create v1.2.3 \
  --title "Release 1.2.3" \
  --notes "Bug fixes and performance improvements." \
  --draft

# Upload artifacts
gh release upload v1.2.3 dist/app.tar.gz dist/checksum.sha256

# List latest releases
gh release list --limit 5 --json tagName,publishedAt,draft,isPrerelease
```

## Remote Management

```bash
# Add upstream remote (after fork)
gh repo add upstream git@github.com:original-owner/repo.git

# Sync with upstream
git fetch upstream && git merge upstream/main

# Remove remote
git remote remove origin
```

## Common Patterns

| Action | Command |
|--------|---------|
| View repo info | `gh repo view owner/repo` |
| List issues by priority | `gh issue list --sort created --label critical --state open` |
| Archive a repo | `gh repo archive owner/repo` |
| Un-archive | `gh repo unarchive owner/repo` |
| Change visibility | `gh repo edit owner/repo --visibility public/private` |
