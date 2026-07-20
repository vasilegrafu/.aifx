# css/ — reference

Deep reference for the stylesheet: the single-file architecture, the `@layer`
cascade order, the module map, page-local CSS, and rebranding. The authoring
contract lives in `../SKILL.md`; this is the on-demand detail.

## The single stylesheet

Every document links exactly one file, `css/docs-html.css`. It carries no rules
of its own — it declares the cascade order once with `@layer`, then `@import`s
the modules in `css/modules/`:

```css
@layer base, metadata, toc, content, callouts, lists, blocks, business, code,
       math, diagrams, presentation, print;
```

`@layer` makes the cascade order explicit and independent of import order, so
modules can be added or reordered without specificity surprises. A document
links the whole stylesheet — there is no tree-shaking; the CSS is small and one
cached file beats a per-document set. (`brand.css` is `@import`ed by `base.css`,
not by the entry file — it is identity, not a cascade layer.)

## Module map

Which `css/modules/` file styles which components:

| module (css/modules/) | styles |
|---|---|
| `brand.css` | organization identity: `--brand-name`, `--brand-accent`. Imported by base.css — never referenced by documents. THE file a corporation edits to rebrand everything |
| `base.css` | fonts (Inter + JetBrains Mono via CDN), tokens, typography, layout, the layout-toggle toolbar, opt-in numbering — always |
| `metadata.css` | metadata-header (cover title block), change-history, approval-block |
| `toc.css` | the static TOC (regular documents; not presentations) |
| `content.css` | table, plain code, figure, collapsible, quote, comparison-table |
| `code.css` | framed code blocks (`figure.code` title bar) + the runtime syntax palette (`.token.*`, applied by docs-html.js/Prism) |
| `callouts.css` | callout, todo-marker |
| `lists.css` | facts, steps, checklist, trace-id |
| `blocks.css` | requirement card, acceptance-criteria (Given/When/Then), kpi-tiles, timeline, glossary, revision-note, meter, risk-matrix, footnotes, ISO front/back matter |
| `business.css` | finance & decision components: financial-table, journal-entry, scenarios, pros-cons, swot-grid, badge, party-block |
| `math.css` | formula blocks (`.math`) — spacing, overflow, and the readable-LaTeX fallback before/without KaTeX |
| `diagrams.css` | diagram-mermaid: the pan/zoom viewport + glyph toolbar |
| `presentation.css` | presentation pages (`<body class="presentation">`) |
| `print.css` | Ctrl+P → cover page, page breaks — layered LAST |

## Page-specific CSS

Shared `css/modules/` are for styles used across MANY documents. CSS that styles
ONE page only does **not** belong there — it lives in that page, in a
`{% block head %}` `<style>` (the base shell exposes `{% block head %}` just
before `</head>`, after the design-system link, so the page reads the same
tokens). The component gallery is the worked example: all its `gx-*` chrome is a
`<style>` inside `../showcases/components.html.j2`, not a shared module — so a
document never downloads a byte of showcase styling.

## Rebranding

Edit `css/modules/brand.css` (`--brand-name`, `--brand-accent`); it cascades to
every document. `base.css` `@import`s it, so nothing else references it — one
file restyles the whole system.

## Adding a module

New styles for a new component category go in a `css/modules/<name>.css` file;
add its `@import` (and its layer name to the `@layer` list) in
`css/docs-html.css`. Because layer order is declared up front, where you put the
`@import` does not matter — only the layer list does.
