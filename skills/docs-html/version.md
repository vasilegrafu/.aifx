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
