---
name: creative-tools
description: Umbrella skill for creative AI-assisted tools and workflows (diagrams, art, music, video, design, etc.).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, tools, diagram, ascii, infographic, comfyui, design, excalidraw, humanizer, manim, p5js, web-design, pretext, sketch, songwriting, touchdesigner]
---

# Creative Tools

This skill provides a unified interface for various creative AI-assisted tools integrated with Hermes, covering diagram generation, ASCII art, infographics, image/video generation, design systems, music, and more.

## Subtools

- **Architecture Diagram** (`architecture-diagram`) – Dark-themed SVG architecture/cloud/infra diagrams as HTML. See `references/architecture-diagram.md`.
- **ASCII Art** (`ascii`) – Create ASCII art and video from text, images, and audio. See `references/ascii.md`.
- **Baoyu Infographic** (`baoyu-infographic`) – 21 layouts × 21 styles for Chinese-style infographics. See `references/baoyu-infographic.md`.
- **ComfyUI** (`comfyui`) – Generate images, video, and audio with ComfyUI via comfy-cli and REST/WebSocket API. See `references/comfyui.md`.
- **Design.md** (`design-md`) – Author/validate/export Google's DESIGN.md token spec files. See `references/design-md.md`.
- **Excalidraw** (`excalidraw`) – Hand-drawn Excalidraw JSON diagrams (architecture, flow, sequence). See `references/excalidraw.md`.
- **Humanizer** (`humanizer`) – Humanize text: strip AI-isms and add natural voice. See `references/humanizer.md`.
- **Manim Video** (`manim-video`) – Manim CE animations for 3Blue1Brown style math/algo videos. See `references/manim-video.md`.
- **p5.js** (`p5js`) – p5.js sketches for generative art, shaders, interactive, 3D. See `references/p5js.md`.
- **Popular Web Designs** (`popular-web-designs`) – 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. See `references/popular-web-designs.md`.
- **Pretext** (`pretext`) – DOM-free text layout for ASCII art, typographic flow, kinetic typography, etc. See `references/pretext.md`.
- **Sketch** (`sketch`) – Throwaway HTML mockups: 2-3 design variants to compare. See `references/sketch.md`.
- **Songwriting & AI Music** (`songwriting-and-ai-music`) – Songwriting craft and Suno AI music prompts. See `references/songwriting-and-ai-music.md`.
- **TouchDesigner MCP** (`touchdesigner-mcp`) – Control a running TouchDesigner instance via twozero MCP. See `references/touchdesigner-mcp.md`.

## Usage

To load a specific creative tool's subskill:

```
/skill architecture-diagram
```

Or enable the whole umbrella:

```
hermes skills enable creative-tools
```

## References

Detailed guides for each tool are stored in the `references/` directory.

## Related Skills

- `delegate_task` – For spawning subagents to work on creative tasks.
- `cronjob` – For scheduling regular creative generation.
- `kanban` – For creative project collaboration boards.