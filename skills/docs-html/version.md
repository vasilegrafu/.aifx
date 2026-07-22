# docs-html — version history

The SINGLE source of truth for the design-system version is `version.json`
(machine-readable); this file is its human ledger — newest release first, one
entry per version, written when the version is bumped. No version number lives
anywhere else (not in the CSS, not in the JS, not in documents).

Semver contract:
- **PATCH** — visual fix, no markup contract change. Safe for every document.
- **MINOR** — additive: new component, new style, new JS feature.
- **MAJOR** — the markup contract changed; documents must opt in to upgrade.

A published version is immutable: any change, however small, is a new version.

---

## 3.2.0 — 2026-07-22

Additive: two more chart kinds, and the relief rule becomes enforceable instead
of merely documented. No markup contract change.

### New — two chart presets

- **`c.return_distribution(series, …)`** — a box plot built from **raw
  observations**. Quartiles (type-7 interpolation) and **Tukey whiskers**
  (1.5 × IQR) are derived at compose time by a new `boxstats` filter, so the
  rendered spec carries the numbers and a reader can check them. Points beyond
  the fences are drawn as **outliers rather than absorbed into the whisker** —
  an outlier quietly extending a whisker is how a fat tail disappears from a
  chart, and that is the reason this is a component rather than a recipe.
- **`c.correlation_matrix(labels, matrix, …)`** — pairwise relationships on the
  sequential `RAMP`. The categorical palette would imply unrelated categories,
  and ECharts' stock blue-to-red `visualMap` reads as good-to-bad on a number
  carrying no such judgement: a −0.8 correlation is not "bad", it is the point
  of a diversifier. Values are printed as well as coloured.

`risk-return` deliberately stays a **recipe** — its spec is already as short and
readable as the data it carries, so a macro would hide the chart without
simplifying it. The test a preset must pass is unchanged: compute something,
enforce a rule, or prevent a known mistake.

### New — the relief rule is checked

`python builder.py charts` now validates two things about every chart spec, the
presets' and the showcase's alike: that it is valid JSON, and that it satisfies
the dataviz **relief rule** — more than three automatically-coloured series
reaches a palette slot below 3:1 on the chart surface, so it needs visible data
labels rather than colour alone.

Only **automatic** colours count. A series or item that sets its own colour is
not drawing from the rotating palette, which is why a fifteen-node role-coloured
sankey passes and a four-series bar chart does not. Pie, funnel and treemap
label by default, so for those the violation is switching labels *off*.

### `c.sankey` gained layout control

`label_room` (default 150) reserves right margin for terminal nodes, whose
labels sit outside the node and otherwise clip. Node width, gap, alignment and a
white label text-border are now sensible defaults rather than something every
call site re-specifies. This came out of migrating a real sixteen-node document,
which is the only way that gap was going to surface.

---

## 3.1.0 — 2026-07-22

Additive: the chart layer grows a checked colour system, three chart presets,
and two build-time checks. **No markup contract change** — a document's HTML is
byte-identical whichever version composed it, so nothing published needs
re-composing. Two things below are nevertheless worth reading before upgrading:
the palette changes colour, and two authoring macros are renamed.

### The categorical palette is replaced — charts will look different

The old palette's comments claimed it was "validated" and colourblind-safe. The
new `python builder.py dataviz` check proves it was not: slots 6 and 8 (orange
and red) collapsed to a CIEDE2000 distance of **4.8** under deuteranopia, and
only the first **three** slots were safe. Any chart with four or more series had
confusable colours.

It is now the **Okabe-Ito** reference set — the published standard for
categorical colour under colour vision deficiency — with pure black replaced by
the document's own ink (`#182338`), since a pure-black series reads as an axis.
Slots are ordered by contrast on the chart surface, because the early slots are
used most and must be the legible ones:

```
1 #0072b2 blue   2 #d55e00 vermillion  3 #009e73 bluish green  4 #cc79a7 purple
5 #56b4e9 sky    6 #e69f00 orange      7 #182338 ink           8 #f0e442 yellow
```

Worst pair is now **11.1** and it holds at every prefix length, so four series
are as safe as eight. Slots 4, 5, 6 and 8 sit below 3:1 and still need the
relief rule (data labels or a table view); slots 1-3 and 7 do not.

Upgrading a document changes its chart colours. That is the point, but it is
visible — check any chart whose colours were chosen around the old palette.

### Renamed authoring macros

Component names dropped a prefix that only repeated their category:

```jinja
c.chart_apache_echarts(...)   ->  c.apache_echarts(...)
c.diagram_mermaid(...)        ->  c.mermaid(...)
```

This is **not** a markup change — both emit exactly the markup they did before
(`pre.chart.apache-echarts`, `pre.mermaid`), and no composed document contains a
macro name. Only templates calling these macros need editing, and every
in-repo caller was updated. The JS/CSS module filenames keep their
`chart-`/`diagram-` prefix: that prefix is the engine convention, not a
category echo.

### New — colour system

- **`RAMP`**, a sequential light-to-dark scale for continuous encodings
  (heatmap, `visualMap`). The categorical palette implied categories where the
  data had an order, and ECharts' stock blue-to-red default read as good/bad.
- **`TOKENS.positive` / `.negative` / `.caution`** — semantic *direction* tones,
  the documented exception to "status colours are reserved". Direction is not
  identity: a candlestick's up/down, a flow's cost/retained. Never assign one to
  a series, and never as the sole cue — positive/negative fail deuteranopia
  separation by construction, so candlestick bodies are hollow/filled too.
- **`docsHtml.chart.resolveColors`** — a spec may now NAME a design colour
  instead of writing a hex: `"palette:1"`, `"token:positive"`, `"ramp:2"`. It
  lives in the shared layer, so every engine resolves the same references and no
  hex is ever forked into a document.

### New — theme coverage

`buildTheme()` styled only `line` and `bar`; everything else fell through to
ECharts' stock colours, which collide with the reserved status hues. It now
covers `pie`, `scatter`, `boxplot`, `candlestick`, `sankey`, `funnel`,
`heatmap`, `radar`, `graph`, plus `visualMap`, `dataZoom`, `markPoint` and
`markLine`.

### New — chart presets

Three macros that compute something, enforce a rule, or prevent a known mistake:

- **`c.sankey(nodes, links, …)`** — colours nodes by ROLE (`source` / `stage` /
  `cost` / `retained`), not by identity, so the colour count never depends on
  the node count. Left to itself ECharts cycles the palette and a fifteen-node
  flow gives two unrelated nodes the same hue.
- **`c.price_history(bars, …)`** — candlestick plus volume as two stacked grids
  sharing an axis pointer, never a dual y-axis (the charting mistake the rules
  already forbid). Takes OHLCV as a human reads it and reorders internally.
- **`c.drawdown_curve(series, …)`** — derives the running peak and each drawdown
  at compose time from a level series, so the document carries the input and the
  arithmetic is auditable.

`components/charts/usage.md` is now the **approved chart-kind catalogue** —
which kinds exist, which are presets and which are hand-written recipes
(`risk-return`, `return-distribution`), and why. Also new: `.chart-note`, the
one-line reading beneath a chart.

### New — two checks

- **`python builder.py dataviz`** — contrast on the chart surface, pairwise
  separation under protanopia / deuteranopia / tritanopia (CIEDE2000, floor
  10.0, calibrated just under Okabe-Ito's own 11.1), and monotonic ramp
  luminance. Fails the build on a confusable pair. Colour science lives in
  `dataviz.py`, out of the composer.
- **`python builder.py charts`** — renders every preset from a `{# sample: … #}`
  header and validates the emitted spec is JSON. This exists because the failure
  is silent by design: a malformed spec does not raise, the engine simply leaves
  the source visible as a code box, indistinguishable from an unreachable CDN.

Presets accordingly build a data structure and serialise it once rather than
hand-writing JSON, and delegate the markup to the engine macro. Both rules, and
the six steps for adding a chart kind, are in `js/REFERENCE.md`.

---

## 3.0.2 — 2026-07-22

Bug fix. No markup contract change — safe for every document; upgrade by
changing the version in the two hrefs. **Recommended for anyone whose readers
are not all on Chromium or Edge.**

- **Bar geometry now renders correctly in Firefox and Safari.** Fourteen
  components carry their geometry in `data-` attributes that CSS reads with
  typed `attr()` — `width: attr(data-pct type(<percentage>), 0%)`. That syntax
  is CSS Values 5 and today ships only in Chromium 133+. Elsewhere the engine
  cannot parse the declaration and **drops it whole**: the `0%` fallback is
  inside the syntax it could not parse, so `width` reverts to `auto` and the
  bar fills its track. Every bar rendered full width — a `bridge` showed
  `+13,031` and `+4,200` as the same size. Wrong data, not missing data.

  New `js/modules/attr-fallback.js` detects the gap once
  (`CSS.supports("width", "attr(...)")`) and, only where it exists, applies the
  same geometry as an inline style. Chromium never enters that path and its
  rendering is byte-for-byte unchanged.

  Affected: `blocks/meter`, and in `investing` — `aging-schedule`, `bridge`,
  `capital-allocation`, `debt-maturity`, `exposure-bars`, `funnel`,
  `holdings-table`, `ownership-table`, `quadrant-map`, `scorecard`,
  `segment-reporting`, `stress-test`, `valuation-range`.

  Verified in Firefox 153: typed `attr()` absent, all 79 geometry elements
  corrected, 89 of 90 rendered measurements within 2% of their declared
  percentage — the one outlier being `funnel-bar`'s deliberate `min-width:
  11rem` legibility floor, which behaves identically in Chromium.

- **Documentation corrected.** Nine `usage.md` files, `css/modules/blocks.css`
  and `css/modules/investing.css` claimed these components "degrade to an empty
  track" with the numbers staying readable. That was false in the dangerous
  direction — the tracks came out full, contradicting the numbers printed
  beside them. `SKILL.md`, `js/REFERENCE.md` and `css/REFERENCE.md` updated too.

The polyfill is deliberately deletable: when Firefox and Safari ship typed
`attr()`, remove the file and the line in `js/docs-html.js`. Nothing else
references it.

---

## 3.0.1 — 2026-07-22

Visual fix. No markup contract change — safe for every document; upgrade by
changing the version in the two hrefs.

- **`kpi-tiles` values are smaller**: `1.5rem` -> `1.25rem` (24px -> 20px), with
  line-height at `1.2`. They were reading as poster numbers rather than headline
  metrics; the weight (800) and tight tracking carry the emphasis instead of the
  size. A long value like `$1,001,000` now also fits one line in a 9rem tile.
- **Component gallery: more air between specimens.** `.gx-spec-head` gained a
  `2.5rem` top margin, so consecutive demos are separated by 40px instead of
  16px and it is obvious where one component ends and the next begins. A spec
  header directly after a category band keeps the tighter `1.2rem`, since the
  band already supplies its own space. This is page-local chrome in
  `showcases/components.html.j2`, not a shared module — documents download none
  of it.

---

## 3.0.0 — 2026-07-22

**Charts changed their markup hook, and gained a whole component category for
investing.** The breaking change is the first one; the second is purely
additive.

### Breaking — charts name their engine

`pre.chart` alone is no longer a recognised markup hook. A chart block now wears
two classes: `chart`, the marker every chart engine shares, and a second class
selecting the engine.

```html
<pre class="chart">…</pre>                   <!-- 2.x -->
<pre class="chart apache-echarts">…</pre>    <!-- 3.0 -->
```

The macro is renamed to match: `c.chart_echarts()` → `c.chart_apache_echarts()`.

Why: charts had no engine seam. Everything lived in one `chart.js` — the
validated categorical palette written directly into an **ECharts theme object**,
the card, the source fallback, `data-height`, the resize reflow — so a second
engine could not have reused the palette the dataviz method validated, and had
nowhere to hook. Diagrams solved this in 1.8.0 with a shared viewport plus one
engine file beside it; charts now use the same split.

- Added: `js/modules/charts.js` — the shared, engine-agnostic chart frame,
  `docsHtml.chart`. Owns `PALETTE` and `TOKENS` **as plain data in no engine's
  format**, `Frame` (card, canvas, `data-height`, source hiding, toolbar), one
  debounced resize dispatch for the whole page, and `markError`.
- Added: `js/modules/chart-apache-echarts.js` — the engine. Owns the pinned
  `echarts@5.5.1` CDN and *translates* the shared tokens into an ECharts theme.
- Renamed: CSS layer `chart` → `charts`. `css/modules/chart.css` becomes
  `charts.css` (frame, toolbar, and the `pre.chart` readable-source fallback —
  one definition for every engine) plus `chart-apache-echarts.css`.
- Moved: the component leaves `components/diagrams/` for a new twelfth category,
  `components/charts/`. A chart is data; a diagram is a drawn relationship.
- **New: a chart toolbar.** Every rendered chart now carries download-as-SVG and
  copy-source, top-right of the card — from the shared layer, so any future
  engine inherits them.
- Rebrand the dataviz palette in `js/modules/charts.js` now, not in the engine.

Adding a chart engine is documented in `js/REFERENCE.md` as the same five
mechanical steps as a diagram engine.

### Added — the `investing` component category (45 components)

An eleventh component category for documents that must support an allocation
decision: buy, hold, sell, size, or wait. Nothing in it is a prettier table —
each component encodes a rule its `usage.md` enforces.

- The security and the call: `security-header`, `recommendation`.
- Company analysis: `thesis-pillars` (claim + evidence + **falsifier**),
  `scorecard`, `metric-trend`, `valuation-multiples`, `peer-comparison`,
  `earnings-surprise`, `valuation-range` (football field), `catalyst-timeline`,
  `expected-value`.
- Statements: `income-statement`, `balance-sheet` (with an explicit
  assets = liabilities + equity check), `cash-flow-statement` (with the free
  cash flow derivation), `dcf-summary`, `segment-reporting` (revenue share vs
  profit share), `footnote-disclosures`. Statement lines cross-reference notes
  via `note=` → `id="note-N"`.
- Decomposition and valuation: `bridge` (waterfall, cumulative maths done at
  compose time), `sensitivity-table`, `roll-forward`, `dupont`,
  `capital-allocation`, `composite-score`, `debt-maturity`, `working-capital`.
- Portfolio and market: `holdings-table`, `performance-table`, `exposure-bars`,
  `risk-metrics`, `trade-log`, `attribution`, `drawdown-table`, `stress-test`.
- Economy and strategy: `macro-indicators`, `cycle-position`, `heatmap`,
  `five-forces`, `quadrant-map`, `funnel`, `cohort-table`, `unit-economics`,
  `ownership-table`, `variance-analysis`, `aging-schedule`, `covenant-table`.

**No new JavaScript.** Every bar width, bar offset and plot position is computed
at compose time and carried as a `data-` attribute read by CSS `attr()`, so the
authoring contract's ban on `style=` holds throughout; each component also
prints its own values, so nothing becomes unreadable without `attr()`.

`css/modules/investing.css` defines four shared skins rather than 45 bespoke
ones: `table.fin` (a marker class every numeric table opts into), `.statement`,
the labelled-bar figure row, and the level-graded cell grid. It is layered after
`business` so `valuation-multiples` and `covenant-table` can reuse `.badge`.

**Migration.** Only charts need action. In each document, change
`<pre class="chart">` to `<pre class="chart apache-echarts">`; the JSON spec
inside is untouched, as is every other component. A document with no chart in it
upgrades to 3.0.0 by changing the version in its two hrefs, nothing else.

Documents already published against `@1.x` or `@2.x` need no action at all: each
pins an immutable tag and loads the assets of that tag, so it keeps its old
markup *and* the code that understands it. Verified against
`data-analysis-report-apple-income-fy2025.html` (pinned `@2.0.0`), which still
renders unchanged.

---

## 2.0.0 — 2026-07-21

**draw.io / diagrams.net support is removed.** `pre.drawio` is no longer a
recognised markup hook — this is the breaking change. Mermaid is now the only
diagram engine.

Why: draw.io diagrams are mxGraph XML with **no auto-layout** — every box needs
an explicit `x`/`y` and every connector a hand-picked exit/entry side and a
routed corridor. Authoring or editing one by hand (or by assistant) means
solving a layout problem before saying anything about the system, and the
results collide and overlap as soon as the diagram changes. Mermaid's dagre
layout removes that entire class of work: you write relationships, it places
them. The 3.6 MB diagrams.net bundle goes with it.

- Removed: `js/modules/diagram-drawio.js`, `css/modules/diagram-drawio.css`,
  `components/diagrams/diagram-drawio/` (`c.diagram_drawio()`), and the pinned
  `jgraph/drawio@24.7.17` CDN dependency.
- **Unchanged: everything else.** `pre.mermaid`, `pre.chart`, and every other
  component keep their exact markup. A document that has no `pre.drawio` in it
  upgrades to 2.0.0 by changing the version in its two hrefs, nothing else.
- **The multi-engine architecture stays** — deliberately. `diagrams.js` remains
  the shared, engine-agnostic viewport and `diagram-mermaid.js` remains *one*
  engine beside it, not merged into it. Adding a future engine is still a new
  `diagram-<name>.js` + `diagram-<name>.css` + two list entries and touches no
  existing code; `js/REFERENCE.md` documents the five steps.

**Migration.** Replace each `<pre class="drawio">` with a `<pre class="mermaid">`
holding the equivalent `flowchart` — nodes become ids with shapes
(`[box]`, `([stadium])`, `{diamond}`, `[(store)]`), connectors become
`a --> b` / `a -. label .-> b`, draw.io groups become `subgraph`, and fill/stroke
colours become `classDef` + `class`. Drop every coordinate.

---

## 1.8.0 — 2026-07-21

Diagram subsystem split into shared core + per-engine files. No authored-markup
change (`pre.mermaid` / `pre.drawio` are unchanged), so documents are unaffected.

- JS: `diagrams.js` is now the **engine-agnostic viewport** (`docsHtml.diagram.Viewer`
  — bounded box, pan/zoom, toolbar, fit/reset/fullscreen/download/copy, resize
  grip); `diagram-mermaid.js` and `diagram-drawio.js` only turn source into an
  `<svg>` and hand it over. Mermaid keeps the ✎ editor as its one engine tool.
- CSS: `diagrams.css` (shared chrome) + `diagram-mermaid.css` + `diagram-drawio.css`.
  Runtime classes renamed to neutral `.diagram-figure` / `.diagram-canvas` /
  `.diagram-tools` / `.diagram-resize`.
- draw.io gains the **reset-to-100%** button it was missing, and both engines now
  share one identical toolbar.
- `@panzoom` is gone: pan/zoom is self-contained for both engines (the
  diagrams.net bundle ships a global `Panzoom` that clobbered it).

---

## 1.7.0 — 2026-07-21

- `diagram-drawio` now renders into the same bounded viewport as Mermaid, with
  the on-brand toolbar (zoom % · fit · fullscreen · download SVG · copy XML,
  drag to pan, Ctrl+wheel to zoom) instead of the diagrams.net chrome. The SVG
  carries a `viewBox`, so 100% **fits the column width** with proportional
  height. Pan/zoom is self-contained — the diagrams.net bundle ships a global
  `Panzoom` that clobbered `@panzoom`, so draw.io no longer loads it.

---

## 1.6.0 — 2026-07-20

- New `drawio` feature + `diagram-drawio` component: freeform draw.io /
  diagrams.net diagrams authored as mxGraph XML (`c.diagram_drawio()`,
  `pre.drawio`), rendered to SVG at view time by the pinned diagrams.net viewer
  (`jgraph/drawio@24.7.17`, lazy). For architecture/network/infra with explicit
  layout — complements Mermaid (auto-laid-out). Styled by `diagrams.css`;
  degrades to the XML source if the viewer CDN is unreachable. Additive.

---

## 1.5.0 — 2026-07-20

- New `layout/width` component: wrap any component to give it a fixed width
  (`w`, default `24rem`) with optional `align` (left/center/right). Caps width,
  never overflows. Additive.

---

## 1.4.0 — 2026-07-20

Layout primitives. Additive — existing documents keep working unchanged.

- New `layout` component category (the 10th) with four composable primitives,
  styled by new `css/layout.css` (layer `layout`):
  - `columns` + `column` — a responsive side-by-side row; `column(span=N)` for
    asymmetric splits. Wraps/stacks when narrow.
  - `grid` — an auto-fit grid of equal tiles (`min` sets the smallest tile).
  - `card` — a titled, bordered surface; the natural cell for grid/columns, or
    standalone.
- The single-column reading model is preserved: every layout **collapses to one
  column on narrow screens and in print** (`break-inside: avoid` on cells), so
  layout is an enhancement, never a dependency.
- Showcase gains a Layout band (now ten category bands); `CATALOG.md`
  regenerated.

---

## 1.3.0 — 2026-07-20

Declarative charts. Additive — existing documents keep working unchanged.

- New `chart` feature: `<pre class="chart">` holding a JSON ECharts `option`,
  rendered to **SVG** at view time by Apache ECharts `5.5.1` (lazy, pinned CDN).
  Component `chart-echarts` (`c.chart_echarts()`), styled by new `css/chart.css`
  (layer `chart`). Covers bar/line/area/pie/scatter/heatmap/candlestick — real
  analytical charts, not just Mermaid's `xychart-beta` illustrations.
- Built-in validated `docs-html` theme: the 8-slot categorical palette (fixed
  order, colorblind-checked against the light surface via the dataviz method),
  ink/axis/grid from the base tokens. Never restyle per chart — rebrand once in
  `js/modules/chart.js`.
- Accessible by default: `aria`, hover tooltip, and a legend for ≥ 2 series are
  auto-filled when the author leaves them unset; one y-axis only (documented).
- Degradation: invalid JSON or an unreachable CDN leaves the spec visible as a
  readable code box — nothing breaks.

---

## 1.2.1 — 2026-07-20

Visual patch — no markup change, safe for every document.

- `kpi-tiles`: smaller headline number (`.kpi-value` 2rem → 1.5rem) so tiles
  read as metrics, not banners.

Tooling (unversioned assets, noted for the record): every generated file now
links the version-pinned CDN — the showcase joined documents in dropping local
refs, so all output is shareable as-is; a missing `cdn` in `version.json` is now
a hard error.

---

## 1.2.0 — 2026-07-20

Catalog completion, generated reference, and internal reorganization. Additive —
existing documents keep working unchanged.

- Catalog grows 59 → 84 doc-types; components reorganized into nine category
  folders (structure, content, lists, callouts, blocks, business,
  front-back-matter, diagrams, math). New components: comparison-table, quote,
  meter, risk-matrix, party-block, footnotes.
- New generated `CATALOG.md` (every component call form + doc-type purpose,
  built from source via `builder.py catalog`), backed by a required
  `{# purpose: … #}` header on every template. `builder.py show <name>` prints
  one item's signature/purpose + usage.md.
- Category/domain `usage.md` blurbs are the single source feeding both
  `CATALOG.md` and the showcase category bands.
- Showcase rebuilt as a category-driven gallery and moved to
  `showcases/components.html` (the builder discovers `showcases/*.html.j2`).
- Page-local CSS via a `{% block head %}` hook; showcase-only chrome left the
  shared stylesheet (`gallery.css` removed).
- Docs restructured: a per-subsystem `REFERENCE.md` (css, js, components,
  doc-types) and a "Documentation map"; SKILL.md slimmed to point at them; every
  per-item `usage.md` opens with a role line.

---

## 1.1.0 — 2026-07-19

Multi-domain expansion + CDN-only documents.

- Catalog grows 38 → 59 doc-types across ten domain folders
  (`doc-types/<domain>/<name>/`): general, software, finance, investing,
  accounting, research, economics, engineering, tools, fallback; the builder
  discovers recursively and `--list` groups by domain.
- New components: financial-table, journal-entry, scenarios, pros-cons,
  swot-grid, badge (`business.css`) and formula (`math.css`).
- New `math` feature: LaTeX rendered at view time by KaTeX 0.16.11 (lazy CDN);
  formulas are LaTeX text, never images.
- Charts documented: mermaid `xychart-beta` / `pie` through the standard
  diagram viewport.
- MINOR head-generation change: composed documents now carry version-pinned
  CDN hrefs ONLY (no local paths, no onerror fallback) — fully portable;
  the gallery keeps local refs. Existing documents keep working unchanged.

---

## 1.0.0 — 2026-07-19

First versioned release of the two-asset, single-include design system.

- One stylesheet: `css/docs-html.css` (`@layer` + `@import` of `css/modules/`),
  one script: `js/docs-html.js` (loader for `js/modules/`: core registry, util,
  icons, layout-toggle, highlight, diagrams, main).
- Layout invariants: single `<main>` column, components flush-left,
  `--block-gap` external spacing.
- Diagrams: Mermaid at natural size in a bounded viewport — pan/zoom
  (Panzoom), icon toolbar with live zoom-%, fit, fullscreen, download SVG,
  copy source; vertical resize grip; ✎ source editor as a resizable side
  panel with live re-render and Prism-colored overlay.
- Code: documents hold plain text + `data-lang`; view-time coloring (Prism,
  lazy) with the palette in `code.css`.
