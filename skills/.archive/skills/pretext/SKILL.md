---
name: pretext
description: "Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative-coding, typography, pretext, ascii-art, canvas, generative, text-layout, kinetic-typography]
    related_skills: [p5js, claude-design, excalidraw, architecture-diagram]
---

# Pretext Creative Demos

## Overview

[`@chenglou/pretext`](https://github.com/chenglou/pretext) is a 15KB zero-dependency TypeScript library by Cheng Lou (React core, ReasonML, Midjourney) for **DOM-free multiline text measurement and layout**. It does one thing: given `(text, font, width)`, return the line breaks, per-line widths, per-grapheme positions, and total height — all via canvas measurement, no reflow.

That sounds like plumbing. It is not. Because it is fast and geometric, it is a **creative primitive**: you can reflow paragraphs around a moving sprite at 60fps, build games whose level geometry is made of real words, drive ASCII logos through prose, shatter text into particles with exact per-grapheme starting positions, or pack shrink-wrapped multiline UI without any `getBoundingClientRect` thrash.

**Archived into p5js.** The full content of this skill (patterns, examples, pitfalls, font stacks) has been consolidated into `p5js` as a reference file at `references/text-layout-pretext.md`. When someone asks for pretext demos, load the `p5js` skill and refer to that reference.

## Source

Library: [`@chenglou/pretext`](https://github.com/chenglou/pretext) (MIT)
Community demos: [pretext.cool](https://www.pretext.cool/)
p5js reference: `skill_view(name="p5js", file_path="references/text-layout-pretext.md")`
