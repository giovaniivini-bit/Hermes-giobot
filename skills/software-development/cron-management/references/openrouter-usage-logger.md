# OpenRouter Usage Logger Script

Location: `~/.hermes/scripts/log_usage.py`

## Purpose
Log daily OpenRouter API usage (cost, remaining limit) to a Google Sheets spreadsheet every 12h and 18h BRT.

## Dependencies
- Python 3.x
- Google Sheets API enabled (`sheets.googleapis.com`)
- Google OAuth token with Sheets scope (`/opt/data/google_token.json`)
- OpenRouter API key stored as base64‑encoded file (`/opt/data/.or_key_b64`)

## Script overview
```python
#!/opt/data/venv_google/bin/python3
# -*- coding: utf-8 -*-
"""Cron: log OpenRouter usage to Sheets via API key (Brasilia time)."""

import base64, subprocess, sys
from datetime import datetime, timezone, timedelta
import urllib.request, json

SID = "18KZeG6S8pODXEu580CX-UJogSLNrkjjH7DwSL18b86k"
TOK = "/opt/data/google_token.json"
OR_KEY_FILE = "/opt/data/.or_key_b64"
BRT = timezone(timedelta(hours=-3))
```

## Data flow
1. **Read OpenRouter key** – decode base64 file.
2. **Call OpenRouter auth/key endpoint** – `GET https://openrouter.ai/api/v1/auth/key`
3. **Extract** `usage_daily`, `limit_remaining`, `limit`.
4. **Read previous row** from Sheets to compute delta.
5. **Append new row** with columns:
   - `A`: date (YYYY-MM-DD)
   - `B`: time (HH:MM)
   - `C`: daily usage (float)
   - `D`: delta since previous entry (float)
   - `E`: remaining limit (float)
   - `F`: formatted daily usage as currency string (`$1.2345`)

## Google Sheets layout
```
A              B      C         D         E               F
Data           Hora   Gasto Hoje($) Periodo($) Limite Restante($) Total Gasto($)
2026‑06‑14     23:37  1.720650  1.720650  6.279350        $1.7207
```

## Timezone handling
Script uses BRT (UTC‑3) for timestamps. Cron schedule must be in UTC:
- 12:00 BRT → 15:00 UTC (`0 15 * * *`)
- 18:00 BRT → 21:00 UTC (`0 21 * * *`)

## Cron job definition
```python
cronjob(
    action="create",
    name="Log uso 12:00 BRT",
    schedule="0 15 * * *",
    script="log_usage.py",
    no_agent=True,
    deliver="origin"
)
```

## Testing
1. **Manual run**:
   ```bash
   cd /opt/data && /opt/data/venv_google/bin/python3 ~/.hermes/scripts/log_usage.py
   ```
2. **Check output** – should print:
   ```
   LOG 2026‑06‑14 23:37 BRT
     Gasto hoje:  $1.720650
     Período:     $1.720650
     Restante:    $6.279350 de $8.00
   ```
3. **Verify Sheets** – new row appears at bottom.

## Troubleshooting
- **403 / authentication error** – Google token expired or missing `https://www.googleapis.com/auth/spreadsheets` scope.
- **OpenRouter key invalid** – ensure base64 file contains the raw API key (not a JSON).
- **Delta negative** – script resets to `usage_daily` when delta < 0 (new day).
- **Silent cron** – `no_agent=True` with empty stdout delivers nothing; add a print for debugging.
- **Duplicate rows** – manual `cronjob(action="run")` can double‑append; script does not deduplicate.