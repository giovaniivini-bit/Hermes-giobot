---
name: cron-management
description: "Manage Hermes cron jobs — list, create, test, remove, monitor, and debug scheduled tasks."
version: 1.0
author: CleitonBot
tags: [cron, scheduler, automation, hermes]
---

## Overview
Hermes includes a cron scheduler for recurring tasks (scripts, prompts, agent runs). Use the `cronjob` tool or `/cron` slash commands to manage jobs.

**CLI:**
```bash
hermes cron list              # list all jobs with IDs
hermes cron create SCHED [prompt]  # positional: schedule, then optional prompt
hermes cron edit ID           # interactive edit of schedule/prompt/delivery
hermes cron remove ID         # delete a job (use the hex ID, not the name)
hermes cron pause ID          # stop scheduling
hermes cron resume ID         # resume scheduling
hermes cron run ID            # trigger immediate execution
hermes cron status            # scheduler health
```

**Key difference from the `cronjob` tool:** The CLI uses `remove` (not `delete`), and `create` takes positional args — `schedule` first, then optional `prompt`. Flags like `--name`, `--skill`, `--script`, `--no-agent`, `--deliver`, `--workdir`, `--profile` follow after.
- Jobs can be LLM-driven (`no_agent: false`) or script-only (`no_agent: true`).
- Script-only jobs deliver stdout verbatim; empty stdout = silent.
- Schedules: `"30m"`, `"every 2h"`, `"0 9 * * *"` (cron), ISO timestamp for one-shot.
- Delivery target: `origin` (current chat), `all`, or explicit platform:chat_id:thread_id.
- Job state: `scheduled`, `running`, `paused`, `error`.

## Commands (via `cronjob` tool)

### List all jobs
```python
cronjob(action="list")
```
Returns array with `job_id`, `name`, `schedule`, `last_status`, `next_run_at`.

**Interpretation:**
- `last_status: "error"` → job failed last run; check logs.
- `last_run_at: null` → never executed.
- `enabled: false` → job paused.

### Remove a job
```python
cronjob(action="remove", job_id="<id>")
# CLI: hermes cron remove <job_id>
```
Always call `cronjob(action="list")` first to get the correct `job_id`.

### Create a script‑only job (no_agent)
For recurring scripts that produce static output (e.g., API pollers, watchdog alerts):
```python
cronjob(
    action="create",
    name="Log uso 12:00 BRT",
    schedule="0 15 * * *",   # 15:00 UTC = 12:00 BRT
    script="log_usage.py",   # relative to ~/.hermes/scripts/
    no_agent=True,
    deliver="origin"
)
```
- Script path: relative to `~/.hermes/scripts/` or absolute.
- `no_agent=True` means the script’s stdout is delivered raw; no LLM reasoning.
- Ensure script is executable and has appropriate shebang.

### Create an LLM‑driven job
For tasks requiring reasoning (summaries, conditional logic):
```python
cronjob(
    action="create",
    name="Daily briefing",
    schedule="30m",
    prompt="Fetch top 3 Hacker News stories and summarize each in one line.",
    skills=["web-scraping"],   # optional skill preload
    deliver="origin"
)
```
- Skills are loaded in order before the prompt runs.
- Model/provider can be overridden per‑job via `model` field.

**CLI equivalent (notice: schedule and prompt are positional, `--name`/`--skill` are flags):**
```bash
# Positional: schedule first, then prompt
hermes cron create "0 6 * * *" "Your prompt text here" --name "job_name" --skill "skill-name"

# Script-only (no_agent):
hermes cron create "0 15 * * *" --name "Log uso" --script "log_usage.py" --no-agent --deliver origin
```
Full positional signature: `hermes cron create <schedule> [prompt]` — the prompt is optional for script-only jobs.

### Test a job immediately
```python
cronjob(action="run", job_id="<id>")
```
Triggers a manual run; does not affect the schedule. Useful for validation.

### Pause/resume
```python
cronjob(action="pause", job_id="<id>")
cronjob(action="resume", job_id="<id>")
```
Paused jobs stay in the list but skip scheduled ticks.

## Monitoring & Debugging

### Check script output
For `no_agent=True` jobs, test the script directly:
```bash
cd /opt/data && python3 ~/.hermes/scripts/log_usage.py
```

### Verify delivery
After a run, check if the message arrived in the target chat. If not:
- Confirm `deliver` target matches current chat (`origin`).
- Ensure the script stdout is non‑empty (empty = silent).
- Check `last_status` for errors.

### Inspect logs
Cron logs are written to the gateway log (`~/.hermes/logs/gateway.log`). Search for `cron` or the job name.

### Common issues
1. **Script not found** – ensure path is relative to `~/.hermes/scripts/` or absolute.
2. **Permission denied** – script must be executable (`chmod +x`).
3. **Schedule syntax** – test with `hermes cron list` (CLI) to validate.
4. **Silent job** – `no_agent=True` with empty stdout sends nothing; add a diagnostic echo.
5. **OpenRouter API failures** – check API key, network.

## Example: OpenRouter usage logger
Reference script: `~/.hermes/scripts/log_usage.py`
- Reads OpenRouter API key from base64‑encoded file.
- Fetches daily usage and remaining limit.
- Appends a row to Google Sheets (spreadsheet ID hardcoded).
- Designed for BRT timezone.

To adapt:
1. Set `OR_KEY_FILE` path (base64‑encoded OpenRouter key).
2. Update `SID` (Google Sheets ID).
3. Ensure `google_token.json` exists and has Sheets scope.

## Integration with memory
Cron jobs are profile‑specific (`~/.hermes/profiles/<name>/cron/`). Changing profiles changes the job list.

## Pitfalls
- **Don’t guess job_id** – always list first.
- **`no_agent=True` jobs can’t ask questions** – script must be self‑contained.
- **Schedule uses UTC** – convert local time accordingly.
- **Cron runs are isolated** – no session context, no memory injection.