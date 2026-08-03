# js/ — internals reference

Deep reference for the bundled script: the module tree, module roles, how to
add a feature, and the diagrams engine/editor internals. The authoring contract
and the "what to do" live in `../SKILL.md`; this file is the on-demand detail.

Every document links exactly one script, `bundle.js`. Like the CSS entry, it
holds no logic — it loads `modules/` in list order (classic `<script>`
injection; ES modules are blocked on `file://`, where documents open). The
modules form a tree on the one `docsHtml` namespace.

```
bundle.js          entry/loader: the MODULES list + injector — order IS dependency order
└── modules/
    ├── core.js       the trunk: docsHtml namespace — register(), init(), data()
    ├── util.js       leaf helpers: loadScript (deduped), copyText, downloadBlob
    ├── icons.js      the shared SVG icon set (Lucide-style strokes, currentColor)
    ├── attr-fallback.js   polyfill — typed attr() bar geometry off Chromium; delete when it lands
    ├── layout-toggle.js   feature — ▯/▭ width switch   (selector: .doc-toolbar)
    ├── highlight.js       feature — runtime code coloring (selector: code[data-lang]; Prism, lazy)
    ├── math.js            feature — LaTeX formulas (selector: .math; KaTeX, lazy)
    ├── diagrams.js        SHARED diagram viewport — docsHtml.diagram.Viewer (no feature, no engine)
    ├── diagrams-mermaid.js feature — Mermaid (selector: pre.mermaid; lazy) + the ✎ source editor
    │                      …one diagrams-<engine>.js per engine; add more beside it
    ├── charts.js          SHARED chart frame — docsHtml.chart (no feature, no engine)
    ├── charts-apache-echarts.js  feature — Apache ECharts (selector: pre.chart.apache-echarts; lazy, SVG)
    │                      …one charts-<engine>.js per engine; add more beside it
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
| `diagrams-mermaid.js` | feature on `pre.mermaid`: pins Mermaid `11.4.1` (lazy), renders with `useMaxWidth:false` (natural pixel size, so 100% = natural), hands the SVG to `diagram.Viewer`, and adds the ✎ **live source editor** (its only engine-specific tool — re-renders into the same SVG node so the view survives; reuses `highlight` for the colored overlay) |
| `charts.js` | **Not a feature** — the shared, engine-agnostic chart frame, exposed as `docsHtml.chart`. Owns `PALETTE` (the 8-slot categorical palette — Okabe-Ito, ordered by contrast, ink substituted for pure black), `RAMP` (sequential, for continuous encodings) and `TOKENS` (ink/axis/grid/surface/font plus the semantic `positive`/`negative`/`caution` direction tones) as **plain data, in no engine's format**, so every engine inherits the same checked colors. Since 4.0.0 those values are **read from `css/foundational/theme.css`'s custom properties** (`--chart-palette-N`, `--chart-ramp-N`, `--chart-*`) once at load via `getComputedStyle`, each with a hardcoded fallback — an engine theme object cannot hold `var()`, and the palette is fixed for the life of the page, so one read is enough and nothing re-renders. Also `resolveColors(spec)`, which substitutes `"palette:3"` / `"token:positive"` / `"ramp:2"` references so a preset never writes a hex into a document — which is what lets a retheme reach every existing chart; `Frame` (the `.chart-figure` card, the `.chart-canvas` an engine draws into, `data-height`, hiding the source `<pre>`, and the toolbar from a declarative `BUTTONS` spec: download-SVG · copy-source); one debounced resize dispatch for the whole page via `frame.onResize(fn)`; and `fail(pre, message)` — the stated failure that takes a chart's place, since the spec now ships hidden and a broken chart would otherwise leave a silent gap. Knows nothing about any engine. **Rebrand the palette in `css/foundational/theme.css`, not here** — and take a published colour-blind-safe reference set rather than hand-picking, since nothing checks it |
| `charts-apache-echarts.js` | feature on `pre.chart.apache-echarts`: declarative data charts. Parses every JSON `option` **first** (an all-invalid page never fetches the ~900 KB engine), lazy-loads ECharts `5.5.1` (pinned CDN), translates `chart.PALETTE`/`TOKENS` into an ECharts theme, and renders **SVG** into `frame.canvas`; auto-fills `aria`/`tooltip`/`legend` only when unset. Invalid JSON, an option the engine refuses, or the CDN down → `chart.fail()` puts one line saying so where the chart would have been, with the spec behind a `show source` button |
| `main.js` | `docsHtml.init()` on DOM-ready — final, never edited |

**Adding a diagram engine.** Mermaid is the only engine today, but the split is
deliberate — `diagrams.js` is the viewport, `diagrams-mermaid.js` is *one* engine
beside it. A second engine is five mechanical steps, and touches nothing that
exists:

1. `js/modules/diagrams-<name>.js` — `docsHtml.register({name, selector:
   "pre.<name>", init})`; turn each block's source into an `<svg>` (offscreen if
   the engine needs a host element) and call `new docsHtml.diagram.Viewer({ pre,
   svg, index, source, copyTitle, extraButtons })`. Load the engine lazily with
   `docsHtml.util.loadScript(<pinned CDN url>)`, inside `init`.
2. `css/diagrams/diagrams-<name>.css` — style `pre.<name>` as a readable code box
   (the CDN-down fallback) and `pre.<name>[hidden] { display: none }`.
3. Add `"diagrams-<name>"` to `MODULES` in `js/bundle.js`, after `"diagrams"`.
   That string is also the `name` the module passes to `docsHtml.register` —
   they are the same identifier and must stay equal.
4. Add `@import url("diagrams/diagrams-<name>.css") layer(diagrams);` to
   `css/bundle.css`.
5. `components/diagrams-<name>/` (`component.html.j2` + `usage.md`) so
   the builder and the catalog know about it. **Flat, and carrying the prefix**
   — there is no `components/diagrams/` category folder. The folder name is the
   macro key, so the `{% macro %}` inside must be `diagrams_<name>` to match;
   a mismatch is not an error, it just never lands on `c`.

The viewport, toolbar, pan/zoom, fullscreen, download and copy come free; an
engine-specific tool goes in via `extraButtons` (Mermaid's ✎ editor is the
worked example). If the SVG carries a `viewBox` instead of natural pixel
dimensions, 100% means fit-to-column-width rather than natural size — both are
supported, the engine chooses.

**Adding a chart engine.** The same split, one level over: `charts.js` is the
frame, `charts-apache-echarts.js` is *one* engine beside it. Five mechanical
steps, touching nothing that exists:

1. `js/modules/charts-<name>.js` — `docsHtml.register({name, selector:
   "pre.chart.<name>", init})`; parse each block's spec, then
   `const frame = new docsHtml.chart.Frame({ pre, index, source })`, draw into
   `frame.canvas`, and register a redraw with `frame.onResize(...)`. Load the
   engine lazily with `docsHtml.util.loadScript(<pinned CDN url>)`, inside
   `init`. Build the engine's theme from `docsHtml.chart.PALETTE` / `.TOKENS` —
   never re-pick colors.
2. `css/charts/charts-<name>.css` — engine specifics ONLY. The card, the
   toolbar, and the `pre.chart` fallback box are already shared, selected by the
   `chart` marker class every engine wears.
3. Add `"charts-<name>"` to `MODULES` in `js/bundle.js`, after `"charts"`.
4. Add `@import url("charts/charts-<name>.css") layer(charts);` to
   `css/bundle.css`.
5. `components/charts-<name>/` — the engine's own directory, holding its kinds.
   Start it with `chart/` (`component.html.j2` + `usage.md`), the generic kind
   that takes a raw spec and emits `<pre class="chart <name>">`, so the builder
   and catalog know about it.
6. `components/charts-<name>/_render.html.j2` — the shared tail for THIS
   engine's kinds, importing `chart/` and holding whatever clearance and title
   arithmetic the engine's spec format needs. The ECharts one is the model, and
   it is engine-specific by nature: it reads `option.grid`, `option.radar`,
   `option.legend`. There is nothing to reuse across engines here.

**ONE DIRECTORY PER ENGINE, holding that engine's kinds.**

```
components/
  charts-apache-echarts/     c.charts_apache_echarts_<kind>(...)
    _render.html.j2          this engine's shared tail
    chart/                   the generic kind — a raw spec
    bar/ line/ pie/ …        one folder per kind
  charts-plotly/             reserved, empty
  diagrams-mermaid/          c.diagrams_mermaid_<kind>(...)
    diagram/                 the generic kind — Mermaid source
```

**The engine is part of every macro under it**, because a kind's leaf name
identifies it only within its engine: `charts-apache-echarts/bar` and
`charts-plotly/bar` are two macros writing two different specs, and the flat `c`
namespace cannot hold both under one name. `NAMESPACED` in
`_showcase_controller.py` is what turns a path into that qualified name — see
`components/REFERENCE.md`.

**Three different names are in play, and the steps above use all three.** A
MODULE file is named for its directory (`charts-<name>`, matching
`js/modules/` and `css/charts/`); a COMPONENT folder is the macro key; a CLASS
carries the singular namespace (`chart-…`). They are not meant to converge, and
each is checked by something different — `js/bundle.js` and `css/bundle.css`
fail loudly on a wrong module name, `status.py` owns the class prefixes, and the
component folder IS its own registration.

**Adding a chart KIND — the far more common job.** A kind is not an engine: it
is a macro that writes a spec for an engine that already exists. They fill
`components/charts-apache-echarts/`; `bar` is the simplest model and `waterfall` the most
involved.

1. `components/charts-apache-echarts/<kind>/component.html.j2` — one self-contained macro that
   builds its own option and hands it to `r.out`. It never writes the `<pre>`
   itself:
   ```jinja
   {# purpose: one line — read by builder.py catalog #}
   {# sample: series=[("A",[1,2])], categories=["x","y"], caption="s" #}
   {% import "charts-apache-echarts/_render.html.j2" as r %}

   {% macro charts_apache_echarts_bar(series=[], categories=[], caption="",
                                      height=340, note="", y_name="") %}
   {% set built = [] %}
   {% for name, values in series %}
   {%   set _ = built.append({"type": "bar", "name": name, "data": values}) %}
   {% endfor %}
   {% set option = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 8, "right": 16, "top": (52 if caption else 16),
                 "bottom": 8, "containLabel": true},
        "xAxis": {"type": "category", "data": categories},
        "yAxis": {"type": "value"},
        "series": built,
      } %}
   {% if caption %}
   {%   set _ = option.update({"title": {"text": caption}}) %}
   {% endif %}
   {{ r.out(option, height, note) }}
   {% endmacro %}
   ```
   The macro name carries the engine because `macro_name()` derives it from the
   PATH — `charts-apache-echarts/bar` → `charts_apache_echarts_bar`. Get it
   wrong and nothing raises; the kind simply never reaches `c`.

   Template paths are named from `components/`, which is a loader root — so it
   is `"charts-apache-echarts/_render.html.j2"`, with no `components/` prefix.

   `_render.html.j2` owns the engine call, so the engine is named in ONE place
   for the whole family rather than once per kind. It is `_`-prefixed because it
   is not a component — see `../components/REFERENCE.md`.
2. **Build the spec as a data structure, then serialise it.** Never hand-write
   JSON in a template. Manual comma bookkeeping (`{{ "," if not loop.last }}`)
   fails silently: a malformed spec is not an error, the engine just leaves the
   source visible as a code box, which looks exactly like an unreachable CDN.

   Each kind builds its own option **in its own file** — there is no shared
   option builder, and a Jinja macro could not be one anyway (a macro returns
   output, not data). Copy the nearest existing kind and change what differs.
   The cost is that the grid/axis block repeats; the check in step 4 is what
   catches the copies drifting apart. Two details are easy to lose in a copy:
   the left margin must widen to `46` when the y axis carries a `name`
   (`containLabel` reserves room for tick labels but not for the name, so it
   renders off the card), and a horizontal chart's category axis needs
   `"inverse": true` or the ranking reads bottom-up.
3. Colours by reference, never by hex — `"palette:1"`, `"token:positive"`,
   `"ramp:2"` (`docsHtml.chart.resolveColors` substitutes them). Colouring by
   ROLE rather than by item is why a 15-node sankey does not run out of colours;
   see `components/charts-apache-echarts/sankey/usage.md`.
4. Add a `{# sample: <kwargs> #}` header — a real call, real enough to exercise
   every loop. Nothing executes it; it is the worked example the next author
   copies, and the arguments you would use to try the kind yourself.
   **Then compose a document with the kind and open it.** A malformed spec does
   not raise — the engine leaves the source visible as a code box, which is
   indistinguishable from an unreachable CDN, so the only way to find out is to
   look.
5. Compute at compose time what the reader should be able to audit
   (`drawdown-curve` derives the running peak, `waterfall` the cumulative
   placeholder, `stacked-normalized` the column shares — so the document carries
   the inputs and the arithmetic is inspectable).
6. Write `components/charts-apache-echarts/<name>/usage.md` — the question the kind answers,
   and its CSS twin if one exists (`waterfall`/`bridge`, `funnel-chart`/`funnel`,
   `gauge`/`meter`). A twin that needs no engine and prints is often the better
   answer, and its own usage.md is the only place that can say so.

The card, the toolbar, download-SVG, copy-source, `data-height` and the resize
dispatch come free.

Features read per-document options from `data-` attributes on their own markup
via `docsHtml.data(el, "option-name", fallback)` (e.g.
`<pre class="mermaid" data-max-scale="10">` raises that diagram's zoom cap).
There is **no per-document JavaScript**, ever; every behaviour keys off markup
the author already writes.

## Adding a feature

Create `modules/<name>.js` and add `<name>` to `MODULES` in `bundle.js`
(before `main`). Nothing else changes — not `core.js`, not `main.js`, not any
other feature. Skeleton:

```js
/* bundle/<name> — one sentence: what it does, what markup activates it. */

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

- **Mermaid `11.4.1`** (`diagrams-mermaid.js`) — renders every
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
