---
name: exploration-prototyping
description: "Exploration and prototyping: spike code ideas, sketch UI variants — validate before building."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spike, sketch, prototype, exploration, feasibility, mockup, ui, experiment, throwaway, proof-of-concept]
---

# Exploration & Prototyping

Two sides of the same coin: **validate an idea before committing to a build.**

- **Spike** — code/technical feasibility experiments (\"can this work?\")
- **Sketch** — UI/design direction mockups (\"how should this look?\")

Both create **disposable artifacts**. Throw them away once they've paid their debt.

| Question | Use | Tool |
|---|---|---|
| "Is this technically possible?" | Code spike | `references/spike.md` |
| "What should this UI look like?" | Design sketch | `references/sketch.md` |
| "Which approach is better?" | Comparison spike | `references/spike.md` |
| "Show me 2-3 design directions" | Variant sketch | `references/sketch.md` |

## Quick Decision

Ask: **Is the question about feasibility or appearance?**

- Technical feasibility (API latency, library compatibility, algorithm X) → **Spike**
- Visual/UX direction (layout, color, layout variants, flow) → **Sketch**
- Don't know → start with a spike; if it works, then sketch the UI

Both workflows produce `spikes/` or `sketches/` directories of disposable files
and a verdict/comparison. Neither produces production code.

## Loading the References

```bash
# Code feasibility experiments
skill_view(name="exploration-prototyping", file_path="references/spike.md")

# UI design mockups
skill_view(name="exploration-prototyping", file_path="references/sketch.md")
```

## Attribution

Both workflows adapted from the GSD (Get Shit Done) project
([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done), MIT).
