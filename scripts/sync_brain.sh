#!/usr/bin/env bash
# Sync Hermes Agent brain (memories, skills, SOUL, plans) with GitHub

if [ -d "/opt/data" ]; then
    cd /opt/data || exit 1
elif [ -d "/home/ubuntu/hermes/data" ]; then
    cd /home/ubuntu/hermes/data || exit 1
else
    exit 1
fi

git config --global --add safe.directory "$PWD"
git pull origin main --rebase --quiet 2>/dev/null
git add .gitignore SOUL.md soul.md memories/ skills/ plugins/ cron/ scripts/ reports/ config.yaml 2>/dev/null

if ! git diff --cached --quiet; then
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    git commit -m "Auto-sync Hermes brain: $TIMESTAMP" --quiet
    git push origin main --quiet 2>/dev/null
fi
