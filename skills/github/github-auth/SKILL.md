---
name: github-auth
description: Authenticate gh CLI for GitHub operations (token, SSH key setup).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, auth]
---

# GitHub Authentication

Set up and verify authentication for the `gh` CLI and git operations.

## Quick Setup

```bash
# Using PAT (Personal Access Token) — recommended
gh auth login --with-token < token.txt
gh auth status   # verify

# Using SSH — already configured on this machine
ssh -T git@github.com  # verify
git config --global credential.helper store  # cache credentials
```

## Creating a Fine-Grained PAT (recommended over classic)

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Set minimum scopes based on need:
   - **Read-only** (browse, issues view): `repo (read-only)`
   - **Full control** (PRs, issues, manage): `repo` full scope
   - **Org admin**: add `admin:org`, `admin:org_hook`

## Troubleshooting

- `Permission denied (publickey)` → Verify SSH key in ~/.ssh/ and registered on GitHub
- `gh: command not found` → Install at https://cli.github.com/
- Expired token → Re-run `gh auth login`
