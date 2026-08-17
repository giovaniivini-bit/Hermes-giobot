---
name: google-workspace
description: "Gmail, Calendar, Drive, Docs, Sheets, and Tasks via gws CLI or Python."
version: 1.2.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, Docs, and Tasks — through Hermes-managed OAuth and a thin CLI wrapper. When `gws` is installed, the skill uses it as the execution backend for broader Google Workspace coverage; otherwise it falls back to the bundled Python client implementation.

## References

- `references/cron-usage-logging.md` — Cron job logging token usage to Sheets (no_agent pattern)
- `references/log-usage-openrouter.py` — Script funcional para logging via OpenRouter API (produção)
- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)
- `references/tasks-api.md` — Google Tasks API reference (create, list, complete, due dates)

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — compatibility wrapper CLI. It prefers `gws` for operations when available, while preserving Hermes' existing JSON output contract.

## First-Time Setup

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

### Quick Setup (concise)

1. Run `python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```ython /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```
### Step 1: Triage — ask the user what they need

Before starting OAuth setup, ask the user TWO questions:

**Question 1: "What Google services do you need? Just email, or also
Calendar/Drive/Sheets/Docs/Tasks?"**

- **Email only** → They don't need this skill at all. Use the `himalaya` skill
  instead — it works with a Gmail App Password (Settings → Security → App
  Passwords) and takes 2 minutes to set up. No Google Cloud project needed.
  Load the himalaya skill and follow its setup instructions.

- **Email + Calendar** → Continue with this skill, but add `tasks` to the scope by editing `setup.py`'s `SCOPES` list so the consent screen only asks for the scopes they actually need.

- **Calendar/Drive/Sheets/Docs only** → Continue with this skill. Narrow `setup.py`'s `SCOPES` list to the needed services before running `--auth-url`.

- **Full Workspace access** → Continue with this skill. The default SCOPES in `setup.py` cover Gmail, Calendar, Drive, Contacts, Sheets, Docs, and Tasks.

**Question 2: "Does your Google account use Advanced Protection (hardware
security keys required to sign in)? If you're not sure, you probably don't
— it's something you would have explicitly enrolled in."**

- **No / Not sure** → Normal setup. Continue below.
- **Yes** → Their Workspace admin must add the OAuth client ID to the org's
  allowed apps list before Step 4 will work. Let them know upfront.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> You need a Google Cloud OAuth client. This is a one-time setup:
>
> 1. Create or select a project:
>    https://console.cloud.google.com/projectselector2/home/dashboard
> 2. Enable the required APIs from the API Library:
>    https://console.cloud.google.com/apis/library
>    Enable: Gmail API, Google Calendar API, Google Drive API,
>    Google Sheets API, Google Docs API, People API
>    **If using Tasks**: also enable Google Tasks API
>    https://console.developers.google.com/apis/api/tasks.googleapis.com/overview
> 3. Create the OAuth client here:
>    https://console.cloud.google.com/apis/credentials
>    Credentials → Create Credentials → OAuth 2.0 Client ID
> 4. Application type: "Desktop app" → Create
> 5. If the app is still in Testing, add the user's Google account as a test user here:
>    https://console.cloud.google.com/auth/audience
>    Audience → Test users → Add users
> 6. Download the JSON file and tell me the file path
>
> Important Hermes CLI note: if the file path starts with `/`, do NOT send only the bare path as its own message in the CLI, because it can be mistaken for a slash command. Send it in a sentence instead, like:
> `The JSON file path is: /home/user/Downloads/client_secret_....json`

### Quick Setup (concise)

1. Run `python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```
explicit (for example `~/Downloads/hermes-google-client-secret.json`), then run
`--client-secret` against that file.

### Step 3: Get authorization URL

The script uses the `SCOPES` list hardcoded at the top of `setup.py`.
To narrow or widen services, edit the `SCOPES` list in `setup.py` before
running `--auth-url`.

```bash
# Default (Gmail, Calendar, Drive, Contacts, Sheets, Docs, Tasks)
python /opt/data/skills/productivity/google-workspace/scripts/setup.py --auth-url
```

This prints the OAuth URL to stdout. No `--services` or `--format` flags
are supported — scope changes must be done by editing the `SCOPES` list in
`setup.py` directly.

**IMPORTANT**: `setup.py` uses `SCOPES = [...]` at module level (line ~46).
Add/remove entries as needed before generating the URL. After auth completes,
restore the full scope list for future use — the token only stores granted
scopes.

Agent rules for this step:
- Send the URL to the user as a single line.
- Tell the user that the browser will likely fail on `http://localhost:1` after approval, and that this is expected.
- Tell them to copy the ENTIRE redirected URL from the browser address bar.
- If the user gets `Error 403: access_denied`, send them directly to `https://console.cloud.google.com/auth/audience` to add themselves as a test user.

### Step 4: Exchange the code

The user will paste back either a URL like `http://localhost:1/?code=4/0A...&scope=...`
or just the code string. Either works. The `--auth-url` step stores a temporary
pending OAuth session locally so `--auth-code` can complete the PKCE exchange
### Quick Setup (concise)

1. Run `python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```
immediately send the new URL to the user and have them retry with the newest
browser redirect only.

### Quick Setup (concise)

1. Run `python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```
### Notes

- Token is stored at `~/.hermes/google_token.json` and auto-refreshes.
- Pending OAuth session state/verifier are stored temporarily at `~/.hermes/google_oauth_pending.json` until exchange completes.
- If `gws` is installed, `google_api.py` points it at the same `~/.hermes/google_token.json` credentials file. Users do not need to run a separate `gws auth login` flow.
- To revoke: `$GSETUP --revoke`
- **Adding new services later**: If you upgrade scopes (e.g., add Tasks after initial setup), edit `setup.py`'s `SCOPES` list to include the new scope, then `--revoke` and re-run `--auth-url` → `--auth-code`. The old token does not gain new scopes automatically.

## Usage

### Quick Setup (concise)

1. Run `python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```
```bash
# Search (returns JSON array with id, from, subject, date, snippet)
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# Read full message (returns JSON with body text)
$GAPI gmail get MESSAGE_ID

# Send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html
$GAPI gmail send --to user@example.com --subject "Hello" --from '"Research Agent" <user@example.com>' --body "Message text"

# Reply (automatically threads and sets In-Reply-To)
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
$GAPI gmail reply MESSAGE_ID --from '"Support Bot" <user@example.com>' --body "Thanks"

# Labels
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### Calendar

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (ISO 8601 with timezone required)
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# Delete event
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
# Search existing files
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# Get metadata for a single file
$GAPI drive get FILE_ID

# Upload a local file (auto-detects MIME type)
$GAPI drive upload /path/to/report.pdf
$GAPI drive upload /path/to/image.png --name "Logo.png" --parent FOLDER_ID

# Download (binary files download as-is; Google-native files export to a
# sensible default — Docs→pdf, Sheets→csv, Slides→pdf, Drawings→png)
$GAPI drive download FILE_ID
$GAPI drive download DOC_ID --output ~/doc.pdf
$GAPI drive download DOC_ID --export-mime text/plain --output ~/doc.txt

# Create a folder
$GAPI drive create-folder "Reports"
$GAPI drive create-folder "Q4" --parent FOLDER_ID

# Share
$GAPI drive share FILE_ID --email alice@example.com --role reader
$GAPI drive share FILE_ID --email alice@example.com --role writer --notify
$GAPI drive share FILE_ID --type anyone --role reader        # anyone with link
$GAPI drive share FILE_ID --type domain --domain example.com --role reader

# Delete — defaults to trash (reversible). Use --permanent to skip the trash.
$GAPI drive delete FILE_ID
$GAPI drive delete FILE_ID --permanent
```

### Quick Setup (concise)

1. Run `python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`.  
   - If output is `AUTHENTICATED`, you’re ready to use the skill.  
   - If not, proceed to step 2.

2. Provide the absolute path to your `client_secret.json` (e.g., `/opt/data/client_secret.json`).

3. Complete the OAuth flow:  
   - The script will output an `auth_url`. Open it in a browser, approve, and copy the returned code.  
   - Paste the code back to finish authentication.

4. Verify with `--check` again; it should now print `AUTHENTICATED`.
```
```bash
# Create a new spreadsheet
$GAPI sheets create --title "Q4 Budget"
$GAPI sheets create --title "Inventory" --sheet-name "Stock"

# Read
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# Write
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'

#### Preparing data from images

If your source data is in images (e.g., photos of tables, receipts), perform OCR first to extract text. You can use tools like Tesseract OCR or EasyOCR (via Python) to convert images to CSV format, then import the CSV into Google Sheets using the `sheets update` or `sheets append` commands.

Example workflow:
1. Install OCR dependencies: `apt-get install -y tesseract-ocr` or `uv pip install easyocr torch`.
2. Run OCR to generate CSV text.
3. Use `$GAPI sheets update SHEET_ID "Sheet1!A1" --values '<csv_as_array>'` or append rows.

```

### Docs

```bash
# Read
$GAPI docs get DOC_ID

# Create a new Doc (optionally seeded with body text)
$GAPI docs create --title "Meeting Notes"
$GAPI docs create --title "Draft" --body "First paragraph..."

# Append text to the end of an existing Doc
$GAPI docs append DOC_ID --text "Additional content to append"
```

### Tasks (via direct API)

`google_api.py` does not include a Tasks CLI. Use the Python API directly:

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('/path/to/google_token.json')
service = build('tasks', 'v1', credentials=creds)

# List task lists
lists = service.tasklists().list().execute()

# Create task
task = {'title': 'My Task', 'notes': 'Details', 'due': '2026-06-16T05:00:00Z'}
result = service.tasks().insert(tasklist='@default', body=task).execute()

# List tasks from default list
tasks = service.tasks().list(tasklist='@default').execute()

# Mark complete
service.tasks().patch(tasklist='@default', task=TASK_ID, body={'status': 'completed'}).execute()
```

## Output Format

All commands return JSON. Parse with `jq` or read directly. Key fields:

- **Gmail search**: `[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**: `{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**: `{status: "sent", id, threadId}`
- **Calendar list**: `[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**: `{status: "created", id, summary, htmlLink}`
- **Drive search**: `[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Drive get**: `{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`
- **Drive upload**: `{status: "uploaded", id, name, mimeType, webViewLink}`
- **Drive download**: `{status: "downloaded", id, name, path, mimeType}`
- **Drive create-folder**: `{status: "created", id, name, webViewLink}`
- **Drive share**: `{status: "shared", permissionId, fileId, role, type}`
- **Drive delete**: `{status: "trashed" | "deleted", fileId, permanent}`
- **Contacts list**: `[{name, emails: [...], phones: [...]}]`
- **Sheets get**: `[[cell, cell, ...], ...]`
- **Sheets create**: `{status: "created", spreadsheetId, title, spreadsheetUrl}`
- **Docs create**: `{status: "created", documentId, title, url}`
- **Docs append**: `{status: "appended", documentId, inserted_at, characters}`
- **Tasks create/list**: `{id, title, due, status, notes}` (via direct API)

## Rules

1. **Never send email, create/delete calendar events, delete Drive files, share files, or modify Docs/Sheets without confirming with the user first.** Show what will be done (recipients, file IDs, content, share role) and ask for approval. For `drive delete`, prefer the default trash (reversible) over `--permanent`.
2. **Check auth before first use** — run `setup.py --check`. If it fails, guide the user through setup.
3. **Use the Gmail search syntax reference** for complex queries — load it with `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")`.
4. **Calendar times must include timezone** — always use ISO 8601 with offset (e.g., `2026-03-01T10:00:00-06:00`) or UTC (`Z`).
5. **Respect rate limits** — avoid rapid-fire sequential API calls. Batch reads when possible.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 above |
| `REFRESH_FAILED` | Token revoked or expired — redo Steps 3-5 |
| `HttpError 403: Insufficient Permission` | Missing API scope — `$GSETUP --revoke` then redo Steps 3-5 |
| `AUTHENTICATED (partial)` or "Token missing scopes" | New write capabilities (Drive write/delete, Docs create/edit) require re-authorization. `$GSETUP --revoke` then redo Steps 3-5 to grant the upgraded scopes. |
| `HttpError 403: Access Not Configured` | API not enabled — user needs to enable it in Google Cloud Console |
| `Google Tasks API has not been used` | User must enable Google Tasks API at https://console.developers.google.com/apis/api/tasks.googleapis.com/overview?project=PROJECT_ID |
| `ModuleNotFoundError` | Run `$GSETUP --install-deps` |
| Advanced Protection blocks auth | Workspace admin must allowlist the OAuth client ID |

## Alternative: Himalaya Email CLI (non-Google email)

If the user only needs email (no Calendar/Drive/Sheets), the **Himalaya CLI** (`himalaya`) is a simpler alternative: IMAP/SMTP from terminal, no Google Cloud project needed. Use it for Gmail App Password auth or any IMAP mailbox.

See `references/himalaya-email.md` for setup and common operations.

### Quick comparison

| Feature | Google Workspace (Gmail) | Himalaya CLI |
|---------|-------------------------|--------------|
| Setup | Google Cloud OAuth (~5 min) | App password or IMAP creds (~2 min) |
| Services | Gmail, Calendar, Drive, Sheets, Docs, Tasks | Email only |
| Backend | Gmail API | IMAP/SMTP (any provider) |
| Auth | OAuth 2.0 with auto-refresh | App password / password command |
| Platform | Any (via gws CLI or curl) | Linux/macOS/Windows (CLI) |

## Revoking Access

```bash
$GSETUP --revoke
```
