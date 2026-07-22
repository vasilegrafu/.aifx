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
    ├── attr-fallback.js   polyfill — typed attr() bar geometry off Chromium; delete when it lands
    ├── layout-toggle.js   feature — ▯/▭ width switch   (selector: .doc-toolbar)
    ├── highlight.js       feature — runtime code coloring (selector: code[data-lang]; Prism, lazy)
    ├── math.js            feature — LaTeX formulas (selector: .math; KaTeX, lazy)
    ├── diagrams.js        SHARED diagram viewport — docsHtml.diagram.Viewer (no feature, no engine)
    ├── diagram-mermaid.js feature — Mermaid (selector: pre.mermaid; lazy) + the ✎ source editor
    │                      …one diagram-<engine>.js per engine; add more beside it
    ├── charts.js          SHARED chart frame — docsHtml.chart (no feature, no engine)
    ├── chart-apache-echarts.js  feature — Apache ECharts (selector: pre.chart.apache-echarts; lazy, SVG)
    │                      …one chart-<engine>.js per engine; add more beside it
    └── main.js       docsHtml.init() on DOM-ready — final, never edited
```

## Module roles

| module | role |
|---|---|
| `core.js` | the trunk: `docsHtml.register(feature)` + `init()`. A feature = `{name, selector, init}`; markup absent → dormant; a failing feature degrades itself only. Also `docsHtml.data(el, name, fallback)` |
| `util.js` | leaf helpers: `loadScript` (deduped), `loadStyle` (deduped), `copyText`, `downloadBlob`, `drag(handle, {start, move})` |
| `icons.js` | the inline SVG icon set (Lucide-style strokes, `currentColor`) |
| `attr-fallback.js` | **polyfill, not a feature.** The 14 bar/plot components carry their geometry in `data-pct` / `data-lo` / `data-span` / `data-at` / `data-x` / `data-y` and CSS reads it with typed `attr()` — Chromium 133+ only. Elsewhere the whole declaration is dropped (`width: auto` → **every bar full width**, wrong data rather than missing data), so this sets the equivalent inline style. Selects on the *attribute*, relying on the invariant that the attribute name determines the property system-wide. Delete this file when Firefox and Safari ship typed `attr()` |
| `layout-toggle.js` | feature on `.doc-toolbar`: the ▯/▭ width switch |
| `highlight.js` | feature on `code[data-lang]`: runtime syntax coloring (Prism core + autoloader, lazy; grammars on demand). Exposes `docsHtml.highlight.ensure()/element()` for other features |
| `math.js` | feature on `.math`: LaTeX rendered by KaTeX `0.16.11` (lazy CDN, script + stylesheet). `<div class="math">` = display, `<span class="math">` = inline; CDN down → the LaTeX source stays readable (math.css) |
| `diagrams.js` | **Not a feature** — the shared, engine-agnostic diagram viewport, exposed as `docsHtml.diagram.Viewer`. Owns `.diagram-figure` (bounded box), `.diagram-canvas` (pan surface), the toolbar from a declarative `BUTTONS` spec, the zoom-% readout, fit/reset/fullscreen/download-SVG/copy-source, the resize grip, and pan/zoom (a small self-contained transform — deliberately **not** an external pan library, so no engine bundle can clobber it with a global of its own). Knows nothing about any engine |
| `diagram-mermaid.js` | feature on `pre.mermaid`: pins Mermaid `11.4.1` (lazy), renders with `useMaxWidth:false` (natural pixel size, so 100% = natural), hands the SVG to `diagram.Viewer`, and adds the ✎ **live source editor** (its only engine-specific tool — re-renders into the same SVG node so the view survives; reuses `highlight` for the colored overlay) |
| `charts.js` | **Not a feature** — the shared, engine-agnostic chart frame, exposed as `docsHtml.chart`. Owns `PALETTE` (the 8-slot categorical palette — Okabe-Ito, ordered by contrast, ink substituted for pure black), `RAMP` (sequential, for continuous encodings) and `TOKENS` (ink/axis/grid/surface/font plus the semantic `positive`/`negative`/`caution` direction tones) as **plain data, in no engine's format**, so every engine inherits the same checked colors; `resolveColors(spec)`, which substitutes `"palette:3"` / `"token:positive"` / `"ramp:2"` references so a preset never writes a hex into a document; `Frame` (the `.chart-figure` card, the `.chart-canvas` an engine draws into, `data-height`, hiding the source `<pre>`, and the toolbar from a declarative `BUTTONS` spec: download-SVG · copy-source); one debounced resize dispatch for the whole page via `frame.onResize(fn)`; and `markError(pre)`. Knows nothing about any engine. **Rebrand the dataviz palette here**, then run `python builder.py dataviz` — it verifies contrast, colour-blind separation and ramp monotonicity, and fails on a confusable pair |
| `chart-apache-echarts.js` | feature on `pre.chart.apache-echarts`: declarative data charts. Parses every JSON `option` **first** (an all-invalid page never fetches the ~900 KB engine), lazy-loads ECharts `5.5.1` (pinned CDN), translates `chart.PALETTE`/`TOKENS` into an ECharts theme, and renders **SVG** into `frame.canvas`; auto-fills `aria`/`tooltip`/`legend` only when unset. Invalid JSON or CDN down → the spec stays a readable code box (charts.css) |
| `main.js` | `docsHtml.init()` on DOM-ready — final, never edited |

**Adding a diagram engine.** Mermaid is the only engine today, but the split is
deliberate — `diagrams.js` is the viewport, `diagram-mermaid.js` is *one* engine
beside it. A second engine is five mechanical steps, and touches nothing that
exists:

1. `js/modules/diagram-<name>.js` — `docsHtml.register({name, selector:
   "pre.<name>", init})`; turn each block's source into an `<svg>` (offscreen if
   the engine needs a host element) and call `new docsHtml.diagram.Viewer({ pre,
   svg, index, source, copyTitle, extraButtons })`. Load the engine lazily with
   `docsHtml.util.loadScript(<pinned CDN url>)`, inside `init`.
2. `css/modules/diagram-<name>.css` — style `pre.<name>` as a readable code box
   (the CDN-down fallback) and `pre.<name>[hidden] { display: none }`.
3. Add `"diagram-<name>"` to `MODULES` in `js/docs-html.js`, after `"diagrams"`.
4. Add `@import url("modules/diagram-<name>.css") layer(diagrams);` to
   `css/docs-html.css`.
5. `components/diagrams/diagram-<name>/` (`component.html.j2` + `usage.md`) so
   the builder and the catalog know about it.

The viewport, toolbar, pan/zoom, fullscreen, download and copy come free; an
engine-specific tool goes in via `extraButtons` (Mermaid's ✎ editor is the
worked example). If the SVG carries a `viewBox` instead of natural pixel
dimensions, 100% means fit-to-column-width rather than natural size — both are
supported, the engine chooses.

**Adding a chart engine.** The same split, one level over: `charts.js` is the
frame, `chart-apache-echarts.js` is *one* engine beside it. Five mechanical
steps, touching nothing that exists:

1. `js/modules/chart-<name>.js` — `docsHtml.register({name, selector:
   "pre.chart.<name>", init})`; parse each block's spec, then
   `const frame = new docsHtml.chart.Frame({ pre, index, source })`, draw into
   `frame.canvas`, and register a redraw with `frame.onResize(...)`. Load the
   engine lazily with `docsHtml.util.loadScript(<pinned CDN url>)`, inside
   `init`. Build the engine's theme from `docsHtml.chart.PALETTE` / `.TOKENS` —
   never re-pick colors.
2. `css/modules/chart-<name>.css` — engine specifics ONLY. The card, the
   toolbar, and the `pre.chart` fallback box are already shared, selected by the
   `chart` marker class every engine wears.
3. Add `"chart-<name>"` to `MODULES` in `js/docs-html.js`, after `"charts"`.
4. Add `@import url("modules/chart-<name>.css") layer(charts);` to
   `css/docs-html.css`.
5. `components/charts/<name>/` (`component.html.j2` + `usage.md`) — the
   macro emits `<pre class="chart <name>">` — so the builder and catalog know
   about it. (The component drops the `chart-` prefix that the JS/CSS modules
   carry: inside the `charts` category it would only repeat the category name.
   `diagrams` does the same — `mermaid`, not `diagram-mermaid`.)

**Adding a chart KIND (a preset) — the far more common job.** A kind is not an
engine: it is a macro that writes a spec for an engine that already exists.
`components/charts/{sankey,price-history,drawdown-curve,return-distribution,correlation-matrix}`
are the models.

1. `components/charts/<kind>/component.html.j2`. Import the engine macro and
   delegate to it, so the engine name is written in ONE place per preset:
   ```jinja
   {% import "components/charts/apache-echarts/component.html.j2" as engine %}
   {% call engine.apache_echarts(height=height) %}{{ option | tojson(indent=2) }}{% endcall %}
   ```
2. **Build the spec as a data structure, then serialise it.** Never hand-write
   JSON in the template. Manual comma bookkeeping (`{{ "," if not loop.last }}`)
   fails silently: a malformed spec is not an error, the engine just leaves the
   source visible as a code box, which looks exactly like an unreachable CDN.
3. Colours by reference, never by hex — `"palette:1"`, `"token:positive"`,
   `"ramp:2"` (`docsHtml.chart.resolveColors` substitutes them). A preset that
   colours by role rather than by item is why a 15-node sankey does not run out
   of colours; see `components/charts/sankey/usage.md`.
4. Add a `{# sample: <kwargs> #}` header — real enough to exercise every loop.
   `python builder.py charts` renders every preset with its sample and fails if
   the spec is not valid JSON. A preset without a sample is not checked.
5. Compute at compose time what the reader should be able to audit
   (`drawdown-curve` derives the running peak in the macro, so the document
   carries the input series and the arithmetic is inspectable).
6. List the kind in `components/charts/usage.md` — the approved-kinds catalogue
   — and say there whether it is a preset or a recipe. A preset earns its place
   only by computing something, enforcing a rule, or preventing a known
   mistake; otherwise document a recipe and let the author write the spec.

The card, the toolbar, download-SVG, copy-source, `data-height` and the resize
dispatch come free.

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
   spec walked by a generic builder — see `Viewer.BUTTONS` in `diagrams.js`,
   the reference example.

## Diagrams — engine & editor internals

An engine loads from a pinned CDN **only when a document actually contains that
kind of diagram** — a diagram-free document fetches nothing extra:

- **Mermaid `11.4.1`** (`diagram-mermaid.js`) — renders every
  `<pre class="mermaid">` with `useMaxWidth:false` (natural pixel size; a node's
  box is the same across every diagram regardless of node count), so 100% is
  natural size.

It hands its SVG to the shared `docsHtml.diagram.Viewer`, which supplies the
bounded viewport with **drag-to-pan**, **Ctrl+wheel zoom**, and one icon toolbar
(inline SVG icons, Lucide-style strokes, no icon files): zoom out · live zoom-% ·
zoom in │ fit-to-view · reset-100% │ fullscreen │ *engine tools* │ download-SVG ·
copy-source. Mermaid contributes the one engine tool, ✎ edit-source.

The viewport opens at the diagram's natural height capped at `70vh` (diagrams
that fit show in full; larger ones are panned/zoomed, never shrunk), and a
**grip pill on the bottom edge resizes it vertically** — drag to grow or shrink,
double-click to reset. Plain mouse-wheel still scrolls the page.

The **✎ editor** opens a **side panel** left of the diagram — its own column;
the diagram is never covered (the SVG lives in a `.diagram-canvas` pane that
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
