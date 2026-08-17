# Git-Based Brain Sync Patterns

Session context: Giovani (17/2026) — syncing Hermes brain between Linux server (Oracle Cloud) and Windows desktop.

## Server Setup (/opt/data)

The agent home at `/opt/data` is already a Git repo (no remote yet). Contains:

**To version:**
- `skills/` — all SKILL.md files (66+ files across categories)
- `memory/` — persistent memory files
- `cron/` — cron job definitions
- `plugins/` — plugin configurations
- `scripts/` — custom scripts
- `config.yaml` — main config
- `SOUL.md` — personality definition

**Already excluded by .gitignore:**
`.env*`, secrets (*.json except needed), state.db, kanban.db, cache/, logs/, audio_cache/, image_cache/, venv_google/, bin/, sandboxes/, *.lock, *.pid, process files, model caches.

## Commands for Initial Setup

```bash
cd /opt/data
# Add untracked but wanted files
git add skills/ memory/ cron/ plugins/ scripts/ config.yaml SOUL.md SKILL.md
# Verify what's staged
git status
# Commit
git commit -m "Initial brain snapshot"
# Add remote (after creating private GitHub repo)
git remote add origin git@github.com:<user>/hermes-brain.git
git push -u origin main
```

## Desktop Sync

On Windows desktop where Hermes Agent runs:

```powershell
# Clone to desired location
git clone git@github.com:<user>/hermes-brain.git %USERPROFILE%\hermes-brain

# Option A: Symlink skills directory (Linux only, use junction on Windows)
mklink /J "%APPDATA%\hermes\skills" "%USERPROFILE%\hermes-brain\skills"

# Option B: Set HERMES_SKILLS_DIR env var in profile/config
# Export HERMES_SKILLS_DIR=C:\Users\<you>\hermes-brain\skills

# When brain changes on either side:
cd hermes-brain
git pull
```

Note: symlinks/junctions require admin privileges on Windows. If unavailable, consider setting up Herme's config to point to the cloned path directly via an environment variable or config override.

## Merge Conflicts Strategy

When both sides edit simultaneously:
1. **Skills**: last-push-wins (manual review before merge if both touched same file)
2. **Memory**: keep latest non-conflicting entries, manually reconcile duplicates
3. **Config**: always review diffs carefully — conflicts here can break deployment

Quick conflict check:
```bash
git fetch origin
git diff --name-only HEAD origin/main | grep -E '\.(yaml|md|json)$'
```
