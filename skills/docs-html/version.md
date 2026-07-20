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
