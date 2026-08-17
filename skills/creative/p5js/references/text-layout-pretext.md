# Text-as-Geometry: Pretext Creative Layout

Pretext (`@chenglou/pretext`) is a 15KB zero-dependency TypeScript library for
**DOM-free multiline text measurement and layout** — given (text, font, width),
it returns line breaks, per-line widths, per-grapheme positions, and total
height. Because it is fast and geometric, it is a **creative primitive**: you
can reflow paragraphs around a moving sprite at 60fps, build games whose level
geometry is real words, drive ASCII logos through prose, or shatter text into
particles with exact per-glyph starting positions.

## When to Use

Reach for this pattern when building p5.js sketches that involve:

- Text flowing around a moving shape (hero sections, editorial layouts)
- ASCII-art effects using **real words or prose**, not monospace rasters
- Games where obstacles are made of text words
- Kinetic typography with per-glyph physics (shatter, scatter, flock)
- Multiline "shrink-wrap" layout (tightest container width)
- Typographic generative art with non-Latin scripts

Use p5.js's `createGraphics()` / canvas 2D as the renderer. Pretext provides
measurements; p5.js draws the result.

## Quick Reference

Import from esm.sh:

```html
<script type="module">
import {
  prepare, layout,                   // use-case 1: simple height
  prepareWithSegments, layoutWithLines,  // use-case 2a: fixed-width lines
  layoutNextLineRange, materializeLineRange, // use-case 2b: streaming / variable width
  measureLineStats, walkLineRanges,  // stats without string allocation
} from "https://esm.sh/@chenglou/pretext@0.0.6";
</script>
```

Pin the version. Check [npm](https://www.npmjs.com/package/@chenglou/pretext) for latest.

## Patterns (copy-paste ready)

### 1. Flow around an obstacle (variable-width column)

The signature pretext move. Row-by-row: "how wide is the corridor here?" — pretext
breaks lines accordingly. Use in p5.js `draw()` with an animated obstacle.

```js
// p5.js sketch integration
let prepared;

function preload() {
  // In p5.js 2.x: prepared = await prepareWithSegments(TEXT, FONT);
}

function setup() {
  createCanvas(800, 600);
  prepared = prepareWithSegments(TEXT, "16px Inter");
}

function draw() {
  background(10);
  const obstacle = { x: mouseX, y: mouseY, r: 80 };
  drawFlow(obstacle);
}

function drawFlow(obstacle) {
  const COL_X = 40, COL_W = width - 80, LINE_H = 24;
  let cursor = { segmentIndex: 0, graphemeIndex: 0 };
  let y = 40;
  while (y < height - 40) {
    const dy = y - obstacle.y;
    const inBand = Math.abs(dy) < obstacle.r;
    let x = COL_X, w = COL_W;
    if (inBand) {
      const half = Math.sqrt(obstacle.r ** 2 - dy ** 2);
      const leftW  = max(0, (obstacle.x - half) - COL_X);
      const rightW = max(0, (COL_X + COL_W) - (obstacle.x + half));
      if (leftW >= rightW) { x = COL_X;                 w = leftW - 12; }
      else                 { x = obstacle.x + half + 12; w = rightW - 12; }
      if (w < 40) { y += LINE_H; continue; } // skip narrow gaps
    }
    const range = layoutNextLineRange(prepared, cursor, w);
    if (!range) break;
    const line = materializeLineRange(prepared, range);
    fill(220); textAlign(LEFT, TOP); text(line.text, x, y);
    cursor = range.end;
    y += LINE_H;
  }
  // Draw the obstacle
  fill(100, 40, 40, 200); noStroke();
  ellipse(obstacle.x, obstacle.y, obstacle.r * 2);
}
```

**Obstacle variants:** rectangles, multiple obstacles (sort segments, emit wider
lane), morphing obstacles (tween collision field alongside rendered shape).

### 2. Text-as-geometry game (word bricks with collision)

Use `layoutWithLines` to get stable line rects, then treat each word as an
axis-aligned box for physics (e.g., Breakout where bricks are real words).

```js
const prepared = prepareWithSegments(WORDS.join(" "), FONT);
const { lines } = layoutWithLines(prepared, FIELD_W, 28);

// Build brick rects per word
const bricks = [];
let y = 50;
for (const line of lines) {
  let x = 10;
  for (const word of line.text.split(" ")) {
    const wPx = textWidth(word); // p5.js convenience
    bricks.push({ x, y, w: wPx, h: 24, text: word, hp: 1 });
    x += wPx + textWidth(" ");
  }
  y += 28;
}
```

### 3. Shatter / explode typography

Use `walkLineRanges` + a grapheme walk to get (x, y) for every glyph, then
spawn particles that scatter on click and return home.

```js
const prepared = prepareWithSegments(TEXT, FONT);
const particles = [];
let y = 100;
walkLineRanges(prepared, COL_W, (line) => {
  const range = materializeLineRange(prepared, line);
  const seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  let x = COL_X;
  for (const { segment } of seg.segment(range.text)) {
    const w = textWidth(segment);
    particles.push({ ch: segment, x, y, vx: 0, vy: 0, homeX: x, homeY: y });
    x += w;
  }
  y += LINE_H;
});

function mousePressed() {
  for (const p of particles) {
    const dx = p.x - mouseX, dy = p.y - mouseY;
    const d = dist(p.x, p.y, mouseX, mouseY) || 1;
    const force = 400 / (d * 0.2 + 1);
    p.vx += (dx / d) * force;
    p.vy += (dy / d) * force;
  }
}

function updateParticles() {
  for (const p of particles) {
    p.vx *= 0.92; p.vy *= 0.92;
    p.vx += (p.homeX - p.x) * 0.06;
    p.vy += (p.homeY - p.y) * 0.06;
    p.x += p.vx * deltaTime * 0.06;
    p.y += p.vy * deltaTime * 0.06;
  }
}
```

### 4. ASCII mask as moving obstacle

Rasterize an ASCII logo or bitmap into a cell buffer, convert occupied cells
into per-row obstacle spans, feed into `layoutNextLineRange`. The text opens
around the moving ASCII object.

```js
const CELL_W = 12, CELL_H = 15;
const cols = ceil(W / CELL_W), rows = ceil(H / CELL_H);
const obstacleRows = Array.from({ length: rows }, () => []);

function rasterizeLogo(time) {
  for (const r of obstacleRows) r.length = 0;
  for (const block of logoBlocks(time)) {
    const r0 = floor(block.y0 / CELL_H);
    const r1 = ceil(block.y1 / CELL_H);
    for (let r = r0; r <= r1; r++)
      obstacleRows[r]?.push([block.x0 - 18, block.x1 + 22]);
  }
  mergeRowSpans(obstacleRows); // sort & merge overlapping spans
}
```

### 5. Editorial multi-column with shared cursor

```js
const prepared = prepareWithSegments(ARTICLE, FONT);
let cursor = { segmentIndex: 0, graphemeIndex: 0 };

for (const col of [col1, col2, col3]) {
  let y = col.y;
  while (y < col.y + col.h) {
    const range = layoutNextLineRange(prepared, cursor, col.w);
    if (!range) return;
    const line = materializeLineRange(prepared, range);
    fill(220); text(line.text, col.x, y);
    cursor = range.end;
    y += LINE_H;
  }
}
```

### 6. Multiline shrink-wrap

Find the container width that still fits all lines:

```js
const { lineCount, maxLineWidth } = measureLineStats(prepared, MAX_W);
// card width = maxLineWidth + padding; card height = lineCount * LINE_H + padding
```

### 7. Kinetic typography

Animate per-line transforms using `layoutWithLines`:

```js
const { lines } = layoutWithLines(prepared, W - 80, 40);
function draw() {
  const t = millis();
  for (let i = 0; i < lines.length; i++) {
    const phase = t * 0.001 - i * 0.15;
    const yOff = 100 + i * 40 + sin(phase) * 12;
    const opacity = map(sin(phase), -1, 1, 0.3, 1);
    fill(220, opacity * 255);
    text(lines[i].text, 40, yOff);
  }
}
```

## Key API Reference

| Function | Purpose | Use Case |
|----------|---------|----------|
| `prepare(text, font)` | Measure, return prepared handle | Simple height-only (CSS rendering) |
| `layout(prepared, width, lineHeight)` | Get height + line count | Virtualized lists, masonry |
| `prepareWithSegments(text, font)` | Measure with grapheme segmentation | Creative rendering (cases 1-7) |
| `layoutWithLines(prepared, width, lineHeight)` | Get line objects with text + width | Fixed-width creative layout |
| `layoutNextLineRange(prepared, cursor, width)` | Stream one line from cursor | Variable-width (case 1, 4, 5) |
| `materializeLineRange(prepared, range)` | Get {text} for a range | After nextLineRange |
| `measureLineStats(prepared, maxWidth)` | Get lineCount + maxLineWidth | Shrink-wrap (case 6) |
| `walkLineRanges(prepared, maxWidth, cb)` | Iterate without string alloc | Stats, physics over graphemes |

## Performance Notes

- `prepare()` / `prepareWithSegments()` is the expensive call — call **once** per
  text+font pair. Cache the handle.
- On resize, only re-run `layout*()` — never re-prepare.
- `layoutNextLineRange` in a tight loop is cheap enough for 60fps on normal
  paragraph lengths.
- Canvas `ctx.font` is slow — set once per frame, not per `fillText` call.

## Common Pitfalls

1. **Drifting font strings** — `ctx.font = "16px Inter"` must match the CSS
   `font-family`. If the font 404s, CSS falls back and measurements drift.
2. **Re-preparing in draw loop** — only `layout*` is cheap. Keep handle in
   module scope.
3. **Forgetting `Intl.Segmenter`** — `"é".split("")` gives 2 chars. Use
   `new Intl.Segmenter(undefined, { granularity: "grapheme" })` for glyphs.
4. **Monospace fallback erases the point** — pretext's whole vibe is
   non-monospaced. Verify font loaded via DevTools.
5. **Skipping rows vs adjusting width** — if corridor is too narrow, **skip**
   (`y += lineHeight; continue;`) rather than pass tiny width and get
   one-grapheme lines.
6. **Shipping a cold demo** — always add: vignette, subtle scanline, idle
   auto-motion, one interactive response. Without these, it's an API repro.

## Font Stack Patterns

| Vibe | Font string | Palette hint |
|------|-------------|--------------|
| Editorial | `17px/1.4 "Iowan Old Style", Georgia, serif` | bone `#e8e6df` on charcoal `#0c0d10` |
| CRT / terminal | `600 13px "JetBrains Mono", ui-monospace` | amber `hsl(38 60% 62%)` on `#07070a` |
| Humanist | `500 17px Inter, ui-sans-serif` | off-white `#f3efe6` on deep-navy `#0b1020` |
| Display | `700 64px "Playfair Display", serif` | hot-red `#ff4130` on cream `#f0ebe0` |
| Engineering | `14px "IBM Plex Mono", monospace` | neon-green `#7cff7c` on near-black `#0a0a0c` |

## Source

Library: [`@chenglou/pretext`](https://github.com/chenglou/pretext) (MIT)
Inspiration: [pretext.cool](https://www.pretext.cool/)