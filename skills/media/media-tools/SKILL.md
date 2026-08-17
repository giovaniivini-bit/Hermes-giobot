---
name: media-tools
description: "Fetch, transform, and reformat media content from web APIs — YouTube transcripts, Tenor GIFs, and other media sources."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [media, youtube, gif, transcript, tenor, content]
---

# Media Tools

Fetch and transform media from web APIs. Each subsection covers one media source.

---

## GIF Search (Tenor API)

Search and download GIFs via the Tenor API. Requires `TENOR_API_KEY` env var.

### Setup

```bash
# Get free API key at https://developers.google.com/tenor/guides/quickstart
# Add to ~/.hermes/.env:
TENOR_API_KEY=your_key_here
```

### Search for GIFs

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

### Download a GIF

```bash
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

### API Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `key` | API key (from `$TENOR_API_KEY`) |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |
| `media_filter` | Filter formats: `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |

### Available Media Formats

Each result has formats under `.media_formats`: `gif` (full quality), `tinygif` (preview), `mp4` (video), `tinymp4`, `webm`, `nanogif`.

---

## YouTube Content (Transcripts)

Extract YouTube transcripts and reformat them into summaries, threads, chapters, or blog posts.

### Setup

```bash
pip install youtube-transcript-api
```

### Helper Script

The script accepts any YouTube URL format (youtu.be, shorts, embeds, live links) or raw 11-char video ID:

```bash
# JSON with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

### Output Formats

| Format | Use |
|--------|-----|
| **Chapters** | Timestamped chapter list grouped by topic shifts |
| **Summary** | Concise 5-10 sentence overview |
| **Chapter summaries** | Chapters with short paragraph per section |
| **Thread** | X/Twitter thread format — numbered posts, each under 280 chars |
| **Blog post** | Full article with title, sections, key takeaways |
| **Quotes** | Notable quotes with timestamps |

### Workflow

1. Fetch with `--text-only --timestamps`
2. Validate non-empty output in expected language
3. Chunk if transcript exceeds ~50K chars (overlapping ~40K with 2K overlap)
4. Transform into requested format (default: summary)
5. Verify coherence, correct timestamps, completeness before presenting

### Error Handling

- **Transcript disabled** → tell user to check subtitle availability
- **Private/unavailable video** → relay error, ask user to verify URL
- **No matching language** → retry without `--language` to get any available transcript
- **Missing dependency** → `pip install youtube-transcript-api`

## Pitfalls

- Tenor: GIF URLs can be used directly in markdown: `![alt](url)`
- YouTube: Script path is `SKILL_DIR/scripts/fetch_transcript.py` — use absolute path for reliability
