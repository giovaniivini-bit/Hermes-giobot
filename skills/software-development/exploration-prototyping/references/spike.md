# Spike — Code Feasibility Experiments

Condensed from the former `spike` skill.

Use when the user wants to **feel out an idea** before committing: validating
feasibility, comparing approaches, surfacing unknowns.

## Core Method

```
decompose → research → build → verdict
```

### 1. Decompose

Break the idea into 2-5 independent feasibility questions. Present as a table:

| # | Spike | Validates | Risk |
|---|---|---|---|
| 001 | websocket-streaming | Given a WS connection, when LLM streams tokens, then client receives chunks < 100ms | High |

**Order by risk.** The spike most likely to kill the idea runs first.

### 2. Research (per spike)

1. Brief the question (2-3 sentences)
2. Surface competing approaches if there's choice
3. Pick one approach and state why

### 3. Build

One directory per spike under `spikes/`:

```
spikes/
 001-websocket-streaming/README.md
 001-websocket-streaming/main.py
 002a-pdf-parse-pdfjs/README.md
 002b-pdf-parse-camelot/README.md
```

**Bias toward something the user can interact with.** Prefer: runnable CLI,
minimal HTML page, small web server, or unit test.

**Depth over speed.** Never declare "it works" after one happy-path run.

### 4. Verdict

Each `README.md` closes with:

```markdown
## Verdict: VALIDATED | PARTIAL | INVALIDATED

### What worked
### What didn't
### Surprises
### Recommendation
```

## Comparison Spikes

Build two approaches back-to-back, then write a head-to-head table:

| Dimension | pdfjs | camelot |
|---|---|---|
| Quality | 9/10 | 7/10 |
| Perf | 3s | 18s |

## Pitfalls

- Skip decomposition only if the user already knows what they want
- **Depth over speed** — test edge cases, follow surprising findings
- Avoid Docker, complex package management, build tools unless required
- A spike that takes 2 days to "clean up" was a bad spike — it's disposable
