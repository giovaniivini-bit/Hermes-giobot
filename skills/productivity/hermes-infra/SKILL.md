---
name: hermes-infra
description: Manage Hermes Agent installation and configuration across multiple deployments. Covers skills, memory, crons, scripts, plugins, config.yaml, and Git-based brain sync strategy.
version: 1.0.0
author: Hermes Agent + Giovani
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, infrastructure, sync, config, skills-management]
---

# Hermes Infrastructure Management

This skill covers configuring and maintaining the Hermes Agent brain: skills, memory, cron jobs, scripts, plugins, config.yaml, SOUL.md, and SKILL.md files across multiple deployments.

## Key Directories (in /opt/data)

| Path | Content |
|------|---------|
| `skills/` | All SKILL.md files organized by category |
| `memory/` | Saved persistent memories |
| `cron/` | Scheduled cron job definitions |
| `plugins/` | Plugin configurations |
| `scripts/` | Custom bash/python scripts |
| `config.yaml` | Main Hermes configuration |
| `SOUL.md` / `SKILL.md` | Personality and base skill |

## Pitfalls

### Sub-skill references must be verified before declaring complete
When a SKILL.md references sub-skills (e.g., github-auth, github-issues), you MUST verify each referenced skill loads successfully with skill_view(name=<ref>). If any return not found, report the gap to the user - do not assume they exist. Common cause: SKILL.md was updated to point to new sub-skills but the actual files were not yet created on disk.

Action pattern: run skill_view for every sub-skill ref; if failure, list all missing names so the user can create them.

### Multiple deployment sync workflow
When syncing brain files between deployments (server ↔ desktop):
1. Verify repo exists with correct .gitignore (exclude secrets, DBs, cache, venvs).
2. Include explicitly: skills/, memory/, cron/, plugins/, scripts/, config.yaml, SOUL.md, SKILL.md.
3. Push initial commit.
4. On target machine: clone, symlink or adjust config paths to point to shared repo.
5. Establish sync direction rule (last-push-wins recommended).

### Skills vs Memory distinction
- Save durable facts (who user is, environment quirks, conventions) to memory only.
- Save procedural knowledge (how to do recurring tasks, pitfalls, workflows) to skills.
- Never save task progress, session outcomes, PR numbers, commit SHAs, or temporary state.

## References
See references/sync-patterns.md for detailed sync workflow examples.