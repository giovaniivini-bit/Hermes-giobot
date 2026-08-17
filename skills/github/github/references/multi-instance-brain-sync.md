# Multi-Instance Brain Sync Pattern

## Problem
Multiple Hermes Agent instances (Telegram bot, desktop PC at home, PC at office) need to share a single "brain" — skills, memories, SOUL, config, cron, scripts — stored in one shared GitHub repository.

## Components
- **Repo**: Private GitHub repo (e.g., `hermes-giobot`)
- **Sync script**: `scripts/sync_brain.sh` — pulls/pushes via git
- **Files synced**: `.gitignore`, `SOUL.md`, `soul.md`, `memories/`, `skills/`, `plugins/`, `cron/`, `scripts/`, `reports/`, `config.yaml`
- **Git root**: `/opt/data` (may vary per deployment)

## Pitfalls

### 1. SSH Host Key Verification Fails
```
Host key verification failed.
fatal: Could not read from remote repository.
```
**Fix:** On the new machine, run first:
```bash
ssh -T git@github.com   # accept host key interactively
```
Or use a PAT (Personal Access Token) instead of SSH keys.

### 2. Script Path Mismatch
Sync scripts may hardcode a wrong base directory (e.g., `/home/ubuntu/hermes/data` instead of actual data path). Always verify `cd <base>` works before running.

### 3. Git Owner/Ownership Issues
If repo was created by another user or permissions changed:
```bash
git config --global --add safe.directory /path/to/repo
```

### 4. Sensitive Files Leak
Always verify `.gitignore` excludes: `.env*`, `auth.json`, `google_token.json`, `state.db*`, caches, `venv_*/`.

## Setup Steps (New Machine)
1. Clone the shared repo into the correct directory
2. Add SSH key to GitHub or configure PAT-based remote
3. Verify `safe.directory` if needed
4. Run sync once to confirm bidirectional flow
5. Set up periodic sync (cron job or systemd timer)
