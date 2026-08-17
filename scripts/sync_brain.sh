#!/usr/bin/env bash
# Sync Hermes Agent brain (memories, skills, SOUL, plans) with GitHub
cd /home/ubuntu/hermes/data || exit 1

git config --global --add safe.directory /home/ubuntu/hermes/data
git pull origin main --rebase --quiet 2>/dev/null
git add .gitignore SOUL.md soul.md memories/ skills/ plugins/ cron/ scripts/ reports/ config.yaml 2>/dev/null

if ! git diff --cached --quiet; then
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    git commit -m "Auto-sync Hermes brain: $TIMESTAMP" --quiet
    git push origin main --quiet 2>/dev/null
fi
