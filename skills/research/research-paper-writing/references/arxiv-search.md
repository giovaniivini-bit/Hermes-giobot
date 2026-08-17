# Paper Discovery via arXiv API

Use the arXiv REST API to search for academic papers. No API key needed.

## Quick Reference

```bash
# Search papers
curl -s "https://export.arxiv.org/api/query?search_query=all:YOUR+QUERY&max_results=5"

# Get specific paper
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"

# Read abstract
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Read full paper (PDF)
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
```

## Search Prefixes

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:transformer+attention` |
| `ti:` | Title | `ti:large+language+models` |
| `au:` | Author | `au:vaswani` |
| `abs:` | Abstract | `abs:reinforcement+learning` |
| `cat:` | Category | `cat:cs.AI` |

## Sort and Pagination

| Parameter | Options |
|-----------|---------|
| `sortBy` | `relevance`, `lastUpdatedDate`, `submittedDate` |
| `sortOrder` | `ascending`, `descending` |
| `start` | Result offset (0-based) |
| `max_results` | Number of results (default 10, max 30000) |

## Semantic Scholar (Citations, Related Papers)

Free API, no key needed for basic use:

```bash
# Paper details + citations
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount,referenceCount"

# Search
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=GRPO+reinforcement+learning&limit=5&fields=title,authors,year,citationCount,externalIds"
```

## Complete Research Workflow

1. **Discover**: `python scripts/search_arxiv.py "your topic" --sort date --max 10`
2. **Assess impact**: Semantic Scholar citation count
3. **Read abstract**: `web_extract(urls=["https://arxiv.org/abs/ID"])`
4. **Read full paper**: `web_extract(urls=["https://arxiv.org/pdf/ID"])`
5. **Find related work**: Semantic Scholar references endpoint
6. **Track authors**: Semantic Scholar author search

## Helper Script

Path: `scripts/search_arxiv.py` (previously in the `arxiv` skill, now archived under `research-paper-writing`). No dependencies — Python stdlib only.

## Rate Limits

- arXiv: ~1 req / 3 seconds
- Semantic Scholar: 1 req / second (100/sec with API key)

## Common Categories

| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `cs.LG` | Machine Learning |
| `stat.ML` | Machine Learning (Statistics) |