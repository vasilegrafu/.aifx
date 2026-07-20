# js/ — internals reference

Deep reference for the docs-html script: the module tree, module roles, how to
add a feature, and the diagrams engine/editor internals. The authoring contract
and the "what to do" live in `../SKILL.md`; this file is the on-demand detail.

Every document links exactly one script, `docs-html.js`. Like the CSS entry, it
holds no logic — it loads `modules/` in list order (classic `<script>`
injection; ES modules are blocked on `file://`, where documents open). The
modules form a tree on the one `docsHtml` namespace.

```
docs-html.js          entry/loader: the MODULES list + injector — order IS dependency order
└── modules/
    ├── core.js       the trunk: docsHtml namespace — register(), init(), data()
    ├── util.js       leaf helpers: loadScript (deduped), copyText, downloadBlob
    ├── icons.js      the shared SVG icon set (Lucide-style strokes, currentColor)
    ├── layout-toggle.js   feature — ▯/▭ width switch   (selector: .doc-toolbar)
    ├── highlight.js       feature — runtime code coloring (selector: code[data-lang]; Prism, lazy)
    ├── math.js            feature — LaTeX formulas (selector: .math; KaTeX, lazy)
    ├── diagrams.js        feature — everything diagrams (selector: pre.mermaid)
    ├── chart.js           feature — declarative charts (selector: pre.chart; ECharts, lazy, SVG)
    └── main.js       docsHtml.init() on DOM-ready — final, never edited
```

## Module roles

| module | role |
|---|---|
| `core.js` | the trunk: `docsHtml.register(feature)` + `init()`. A feature = `{name, selector, init}`; markup absent → dormant; a failing feature degrades itself only. Also `docsHtml.data(el, name, fallback)` |
| `util.js` | leaf helpers: `loadScript` (deduped), `loadStyle` (deduped), `copyText`, `downloadBlob`, `drag(handle, {start, move})` |
| `icons.js` | the inline SVG icon set (Lucide-style strokes, `currentColor`) |
| `layout-toggle.js` | feature on `.doc-toolbar`: the ▯/▭ width switch |
| `highlight.js` | feature on `code[data-lang]`: runtime syntax coloring (Prism core + autoloader, lazy; grammars on demand). Exposes `docsHtml.highlight.ensure()/element()` for other features |
| `math.js` | feature on `.math`: LaTeX rendered by KaTeX `0.16.11` (lazy CDN, script + stylesheet). `<div class="math">` = display, `<span class="math">` = inline; CDN down → the LaTeX source stays readable (math.css) |
| `diagrams.js` | feature on `pre.mermaid`: everything diagrams — CDN pins, `DiagramViewer` class (pan/zoom + toolbar from a declarative `BUTTONS` spec); the source editor reuses `highlight` for a colored overlay |
| `chart.js` | feature on `pre.chart`: declarative data charts. Parses a JSON ECharts `option`, lazy-loads ECharts `5.5.1` (pinned CDN), renders **SVG** with the built-in validated `docs-html` theme; auto-fills `aria`/`tooltip`/`legend` only when unset; reflows on resize. Invalid JSON or CDN down → the spec stays a readable code box (chart.css). Rebrand the palette here, never per chart |
| `main.js` | `docsHtml.init()` on DOM-ready — final, never edited |

Features read per-document options from `data-` attributes on their own markup
via `docsHtml.data(el, "option-name", fallback)` (e.g.
`<pre class="mermaid" data-max-scale="10">` raises that diagram's zoom cap).
There is **no per-document JavaScript**, ever; every behaviour keys off markup
the author already writes.

## Adding a feature

Create `modules/<name>.js` and add `<name>` to `MODULES` in `docs-html.js`
(before `main`). Nothing else changes — not `core.js`, not `main.js`, not any
other feature. Skeleton:

```js
/* docs-html/<name> — one sentence: what it does, what markup activates it. */

"use strict";

docsHtml.register({
  name: "<name>",
  selector: "<the markup hook>",     // no match in the document → feature dormant

  init(targets) {                    // the matched NodeList, once, on DOM-ready
    for (const el of targets) {
      // read options from the element's own data- attributes:
      // const depth = docsHtml.data(el, "depth", 2);
      // wire behaviour…
    }
  },
});
```

## The rules

1. **Self-contained.** Everything the feature needs — constants, CDN pins,
   classes, state — lives in its one file. It never reaches into another
   feature.
2. **Markup activates, never configures in JS.** A document opts in by writing
   markup; per-document tuning is `data-` attributes on that markup, read via
   `docsHtml.data(el, "option-name", fallback)`. There is no per-document
   JavaScript, ever.
3. **Own your engines.** A heavy library loads from a pinned CDN URL inside the
   feature's `init` via `docsHtml.util.loadScript(...)` (deduplicated — shared
   engines load once). A document without the feature's markup fetches nothing.
4. **Degrade gracefully.** `core.init()` isolates each feature in try/catch —
   but design the CSS-only fallback too (like `pre.mermaid` staying a readable
   code box when the CDN is unreachable).
5. **Declarative internals.** Repetitive UI (toolbars, button rows) is a data
   spec walked by a generic builder — see `DiagramViewer.BUTTONS` in
   `diagrams.js`, the reference example.

## Diagrams — engine & editor internals

`diagrams.js` loads its heavy engines from pinned CDNs **only when a document
actually contains a diagram** — a diagram-free document fetches nothing extra:

- **Mermaid `11.4.1`** — renders every `<pre class="mermaid">` with
  `useMaxWidth:false` (natural pixel size; a node's box is the same across every
  diagram regardless of node count).
- **Panzoom `@panzoom/panzoom@4.6.0`** — wraps each rendered diagram in a
  bounded viewport with **drag-to-pan**, **Ctrl+wheel zoom**, and an icon
  toolbar (inline SVG icons, Lucide-style strokes, no icon files): zoom out ·
  live zoom-% · zoom in │ fit-to-view · reset-100% │ fullscreen │ ✎ edit-source │
  download-SVG · copy-Mermaid-source.

The viewport opens at the diagram's natural height capped at `70vh` (diagrams
that fit show in full; larger ones are panned/zoomed, never shrunk), and a
**grip pill on the bottom edge resizes it vertically** — drag to grow or shrink,
double-click to reset. Plain mouse-wheel still scrolls the page.

The **✎ editor** opens a **side panel** left of the diagram — its own column;
the diagram is never covered (the SVG lives in a `.mermaid-canvas` pane that
shrinks beside it; drag the panel's right-edge grip to resize, 256px minimum,
double-click resets). It re-renders after a typing pause while **preserving the
current pan/zoom** (so you can stay zoomed into the region you are editing);
parse errors show under the textarea and the last good render stays. Edits are
**session-only** (a `file://` page cannot save itself): the copy button carries
the edited source back into the document.

If the CDN is unreachable, `diagrams.css` leaves the Mermaid source visible as a
readable code box — the page still works, just without rendered diagrams.

---

When the modules become real ES modules (`register` → `export`, the loader →
`import` list), the tree is already the right shape for that split.
