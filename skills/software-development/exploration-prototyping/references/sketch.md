# Sketch — UI Design Mockups

Condensed from the former `sketch` skill.

Use when the user wants to **see a design direction before committing** —
exploring a UI/UX idea as disposable HTML mockups.

## Core Method

```
intake → variants → head-to-head → pick winner
```

### 1. Intake

Get three things (one at a time):
1. **Feel** — what should this feel like? (adjectives, emotions)
2. **References** — what apps/sites capture the feel?
3. **Core action** — what's the single most important user action?

### 2. Variants (2-3)

Each variant is a **standalone HTML file**. Each takes a different design stance:

- **Density:** compact / airy
- **Emphasis:** content-first / action-first
- **Layout:** single-column / sidebar / split-pane

Naming: `001-calm-editorial/index.html`, `001-utilitarian-dense/index.html`

### 3. Make them real HTML

- Single self-contained file (inline CSS, no build step)
- Tailwind via CDN is fine
- Realistic fake content — no lorem ipsum
- **Interactive**: at least one state transition (open/close, filter, toggle)

Verify with browser tools:
```bash
browser_navigate(url="file:///path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="Does this look right? Any visual bugs?")
```

### 4. Head-to-Head

Present as a comparison table with opinions:

| Dimension | Calm editorial | Utilitarian dense |
|---|---|---|
| Density | Low | High |
| Primary action visibility | Low | High |

**My take:** [opinionated recommendation]

## Interactivity Bar

A sketch is interactive enough when the user can:
1. Click a primary action and something visible happens
2. See one meaningful state transition
3. Hover recognizable affordances

## Pitfalls

- Don't use this for production work — use `claude-design` instead
- Two variants differing only in accent color are wasted effort
- Keep sketches disposable — don't curate them as assets
- Verify visually in the browser before presenting
