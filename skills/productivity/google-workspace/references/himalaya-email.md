# Himalaya Email CLI Reference

Himalaya (`himalaya`) is a CLI email client for IMAP/SMTP from terminal. Use this
as an alternative to Google Workspace Gmail when the user only needs email or uses
a non-Google provider.

## Prerequisites

```bash
# Install
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
# Or via Homebrew
brew install himalaya
```

## Configuration

Create `~/.config/himalaya/config.toml`:

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"

# Gmail folder aliases (v1.2.0+ syntax — plural dotted keys, NOT section aliases)
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

## Common Operations

```bash
# List inbox
himalaya envelope list

# Search
himalaya envelope list from john@example.com

# Read
himalaya message read 42

# Send (pipe stdin)
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Hello

Message body here.
EOF

# Reply from template
himalaya template reply 42 | sed 's/^$/\nYour reply here\n/' | himalaya template send

# Attachments
himalaya attachment download 42 --dir ~/Downloads

# JSON output
himalaya envelope list --output json
```

## Gmail App Password Setup (quick alternative to OAuth)

1. Enable 2FA in Google Account → Security
2. Generate App Password at https://myaccount.google.com/apppasswords
3. Use app password as IMAP/SMTP password
4. IMAP: imap.gmail.com:993 (TLS)
5. SMTP: smtp.gmail.com:587 (STARTTLS)

## Gmail Folder Aliases (v1.2.0+ critical syntax)

Pre-v1.2.0 docs used `[accounts.NAME.folder.alias]` sub-section (singular `alias`).
v1.2.0 silently ignores that form. Use **plural dotted keys**:

```toml
# WRONG (v1.2.0 silently ignores):
[accounts.personal.folder.alias]
inbox = "INBOX"

# RIGHT (v1.2.0+):
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
```

Without correct aliases, save-to-Sent fails AFTER SMTP delivery succeeds,
and the agent may retry the entire send — creating duplicate emails.

## Tips

- Use `--output json` for structured output
- `himalaya account configure` needs PTY mode: `terminal(command="himalaya account configure", pty=true)`
- For compose/forward/reply, pipe stdin via heredoc — more reliable than editor mode
