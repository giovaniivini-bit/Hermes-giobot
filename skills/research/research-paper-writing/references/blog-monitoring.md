# RSS/Atom Feed Monitoring via blogwatcher-cli

Track blog and RSS/Atom feed updates with `blogwatcher-cli`. Supports automatic feed discovery, HTML scraping fallback, OPML import, and read/unread article management.

## Installation

```bash
# Go (recommended)
go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest

# Binary (Linux amd64)
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli
```

## Common Commands

### Managing blogs

- Add a blog: `blogwatcher-cli add "My Blog" https://example.com`
- Add with explicit feed: `blogwatcher-cli add "My Blog" https://example.com --feed-url https://example.com/feed.xml`
- Add with HTML scraping: `blogwatcher-cli add "My Blog" https://example.com --scrape-selector "article h2 a"`
- List tracked blogs: `blogwatcher-cli blogs`
- Remove a blog: `blogwatcher-cli remove "My Blog" --yes`
- Import from OPML: `blogwatcher-cli import subscriptions.opml`

### Scanning and reading

- Scan all blogs: `blogwatcher-cli scan`
- Scan one blog: `blogwatcher-cli scan "My Blog"`
- List unread articles: `blogwatcher-cli articles`
- List all articles: `blogwatcher-cli articles --all`
- Filter by blog: `blogwatcher-cli articles --blog "My Blog"`
- Mark article read: `blogwatcher-cli read 1`
- Mark all read: `blogwatcher-cli read-all --yes`

## Environment Variables

| Variable | Description |
|---|---|
| `BLOGWATCHER_DB` | Path to SQLite database file |
| `BLOGWATCHER_WORKERS` | Number of concurrent scan workers (default: 8) |
| `BLOGWATCHER_SILENT` | Only output "scan done" when scanning |
| `BLOGWATCHER_YES` | Skip confirmation prompts |

## Tips

- Auto-discovers RSS/Atom feeds from blog homepages
- Falls back to HTML scraping if RSS fails and `--scrape-selector` is configured
- Database stored at `~/.blogwatcher-cli/blogwatcher-cli.db` by default
- Import blogs in bulk from OPML files exported by Feedly, Inoreader, NewsBlur