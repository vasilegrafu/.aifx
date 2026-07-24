# css/ — reference

Deep reference for the stylesheet: the single-file architecture, the `@layer`
cascade order, the module map, page-local CSS, and rebranding. The authoring
contract lives in `../SKILL.md`; this is the on-demand detail.

## The single stylesheet

Every document links exactly one file, `css/docs-html.css`. It carries no rules
of its own — it declares the cascade order once with `@layer`, then `@import`s
the modules:

```css
@layer theme, base, metadata, layout, toc, content, callouts, lists, blocks, business, investing,
       code, math, diagrams, charts;
```

`@layer` makes the cascade order explicit and independent of import order, so
modules can be added or reordered without specificity surprises. A document
links the whole stylesheet — there is no tree-shaking; the CSS is small and one
cached file beats a per-document set.

## The five groups

Modules are grouped by **scope**, one directory each, so the layout says what a
file is for before you open it:

| directory | what lives there |
|---|---|
| `foundational/` | any document may use it; nothing here knows a domain |
| `domain-specific/` | one business domain owns it; its classes carry that domain's name |
| `math/` | the formula subsystem: KaTeX |
| `diagrams/` | the diagram subsystem: engine-agnostic viewport + one engine |
| `charts/` | the chart subsystem: engine-agnostic frame + one engine |

The last three are **rendering subsystems**: each pairs its CSS with a lazy CDN
engine in `js/modules/`, and a document using none of them fetches none of them.
They are separate from one another because the thing rendered differs — a
formula, a drawn relationship, data — and each carries its own engine.

`components/` is grouped the same way, so a component and the CSS that styles it
sit in matching places.

## Module map

| module | styles |
|---|---|
| `theme.css` | **every colour in the system**, as `:root` custom properties — including `--accent`, the brand colour. THE file to edit to retheme or rebrand; no other module may hardcode a colour |
| `base.css` | fonts (Inter + JetBrains Mono via CDN), non-colour tokens, typography, layout, the layout-toggle toolbar, opt-in numbering — always. **No colour lives here** |
| `metadata.css` | metadata-header (cover title block), change-history, approval-block |
| `layout.css` | spatial primitives: `columns`/`column` (responsive flex row), `grid` (auto-fit tiles), `card` (titled surface). Collapses to one column on narrow width + print |
| `toc.css` | the static TOC |
| `content.css` | table, plain code, figure, collapsible, quote, comparison-table |
| `code.css` | framed code blocks (`figure.code` title bar) + the runtime syntax palette (`.token.*`, applied by docs-html.js/Prism) |
| `callouts.css` | callout, todo-marker |
| `lists.css` | facts, steps, checklist, trace-id |
| `blocks.css` | requirement card, acceptance-criteria (Given/When/Then), kpi-tiles, timeline, glossary, revision-note, meter, risk-matrix, footnotes, ISO front/back matter |
| `business.css` | **domain-specific**, classes namespaced `business-`: financial-table, journal-entry, scenarios, pros-cons, swot-grid, party-block |
| `investing.css` | **domain-specific**, classes namespaced `investing-`. The investing category (44 components) and the largest module. Opens with ONE shared numeric-table skin selected by an `investing-fin` marker class (`<table class="investing-fin investing-multiples">`), so a new table component inherits alignment, tabular figures and micro-headers for free and the skin is defined once. Three further shared skins follow: `.statement` (income-statement, balance-sheet, cash-flow-statement, dcf-summary — they differ only in which lines are mandatory, which is guidance, not styling), the labelled-bar figure row (bridge, debt-maturity, funnel), and the level-graded cell grid (heatmap, cohort-table, sensitivity-table). Every bar width, bar offset and plot position comes from a `data-` attribute via typed `attr()` — never `style=`; that syntax is Chromium-only today, so `js/modules/attr-fallback.js` applies the same geometry on other engines. It no longer borrows anything from `business` — `.badge` moved to `foundational/blocks.css` when the domains were namespaced. |
| `math.css` | formula blocks (`.math`) — spacing, overflow, and the readable-LaTeX fallback before/without KaTeX |
| `diagrams.css` | **shared, engine-agnostic**: the `.diagram-figure` viewport, `.diagram-canvas` pan surface, `.diagram-tools` glyph toolbar, `.diagram-resize` grip, fullscreen + print |
| `diagram-mermaid.css` | Mermaid-only: the `pre.mermaid` source-box fallback and the ✎ editor panel (surface, overlay, scrollbars). One `diagram-<engine>.css` per engine — a new engine adds a file here, it never edits `diagrams.css` |
| `charts.css` | **shared, engine-agnostic**: the `.chart-figure` card (the validated `bg-soft` surface), the `.chart-canvas` an engine draws into, the `.chart-tools` toolbar, and the `pre.chart` readable-spec fallback — one definition for every engine, selected by the shared `chart` marker class. The categorical palette is data, not CSS: it lives in `js/modules/charts.js` (with the sequential ramp and the semantic direction tones). Also `.chart-note`, the one-line reading under a chart |
| `chart-apache-echarts.css` | Apache ECharts only: containment for the wrapper div the engine generates. Deliberately small — anything a second engine would also need belongs in `charts.css`. One `chart-<engine>.css` per engine, exactly as `diagram-<engine>.css` |

## Namespacing the domain modules

Every class in `domain-specific/` starts with its domain: `.investing-bridge-bar`,
`.business-swot`. The markup then says who owns a class, and the two domains
cannot reach into each other's names.

The rule has a useful side effect: **a class that resists the prefix is telling
you it isn't domain-specific.** Two failed the test when this was applied and
moved to `foundational/` instead:

- **`.badge`** — business.css's own comment called it "a generic status/rating
  pill", and three investing components used it. A shared name across two
  domains is the definition of foundational.
- **`.neg`** — "this number is negative" is arithmetic, not a domain concept.
  It was the system's only genuine class collision (both domain modules defined
  it), and it is hand-written in doc-type markup across accounting, finance and
  general documents.

Where a class name arrives as a **macro argument** — `financial_table` takes
rows of `("subtotal", …)` from 11 doc-types — the macro adds the prefix, so
authoring keeps its plain vocabulary and only the emitted markup is namespaced.

## The exhibit title

A table's `<caption>`, a figure's **leading** `<figcaption>` and the title a
chart engine draws all do one job: they name the exhibit. They are styled once,
in `foundational/content.css`:

```css
caption, figcaption:first-child { font-size: .95rem; font-weight: 700; color: var(--fg); }
```

`:first-child` carries the whole distinction: **a figcaption that leads its
figure is a title; one that follows is a caption**, and the softer `.85rem`
rule above it still styles the latter. A component gets the treatment by
emitting the right element — nothing opts in, and nothing may restate it.

That rule matters because the treatment used to be restated in every domain
file: the same four declarations appeared **15 times**, at `.72rem` uppercase
soft-grey — within `.02rem` and `.02em` of the column-header row directly
beneath them. The title had no rank of its own and read as a second header row.
Since `content` sits before `business` and `investing` in the layer order,
those copies won; deleting them was the fix, not adding a rule.

Two exceptions are deliberate: `figure.code > figcaption` is a code header with
a language badge rather than a title (and its `code` layer sits after
`content`), and `.investing-disclosures-caption` / `.investing-forces-caption`
sit on a `<p>`, which no element selector can reach — they share one rule in
`investing.css` that mirrors this one.

## Page-specific CSS

Shared modules are for styles used across MANY documents. CSS that styles
ONE page only does **not** belong there — it lives in that page, in a
`{% block head %}` `<style>` (the base shell exposes `{% block head %}` just
before `</head>`, after the design-system link, so the page reads the same
tokens). The component gallery is the worked example: all its `gx-*` chrome is a
`<style>` inside `../showcases/components.html.j2`, not a shared module — so a
document never downloads a byte of showcase styling.

## Theme and rebranding

**`css/foundational/theme.css` holds every colour in the system** — one `:root`
block of custom properties, first in the `@layer` order so every later layer
consumes it. Retheming and rebranding are the same act: edit that file. There
is no second theme file, no separate brand file, no `data-theme` attribute and
no switcher.

To rebrand, `--accent` is the knob — headings rule, links, kickers, step
numbers and the chart ramp's dark end all derive from it. Identity is carried
by colour alone; the organization line that printed above every title was
removed in 4.0.0.

The rule that makes it work: **no other module may hardcode a colour.** Not the
components, not the syntax palette, not the data ramps. Verify with

```bash
grep -rE "#[0-9a-fA-F]{3,8}|rgba?\(" css --include="*.css" \
  | grep -v "theme.css"
```

which should return nothing.

Charts are the exception that proves it: an ECharts theme object cannot hold
`var()`, so `js/modules/charts.js` reads `--chart-palette-N`, `--chart-ramp-N`
and `--chart-*` with `getComputedStyle` once at load, each with a fallback.
Edit the values here and charts follow on the next load.

Going **dark** is a real edit, not an inversion. Three things need re-deciding:
`--bg-soft` becomes *lighter* than `--bg` (a recess on white is a raise on
black); `--accent` needs a lighter brand tone and `--on-accent` must flip dark,
or a filled badge becomes illegible; and the chart palette keeps the same eight
Okabe-Ito hues but **reorders** them — colours are handed out in sequence, so
the early slots must be the legible ones, and `#0072b2` leads well on white
while being nearly the worst choice on near-black.

## Print

There is **no print stylesheet**. Ctrl+P uses the browser's own defaults —
paper size, margins and pagination come from the print dialog, not from CSS.

What remains is the `@media print` block each module keeps for itself:
`base.css` hides the floating toolbar, `diagrams.css` and
`diagram-mermaid.css` freeze diagrams to static fully-visible images,
`layout.css` collapses columns to one, `charts.css` and `investing.css` adjust
their own blocks. Those exist to stop screen-only UI reaching paper; they
impose no layout of their own. A new module that needs print behaviour adds its
own `@media print` block rather than a shared file.

One limit, whatever the theme: charts cannot follow it in print. An engine
reads the chart tokens once at init and bakes them into the SVG.

## Adding a module

New styles for a new component category go in `css/<group>/<name>.css` — pick
the group by asking who may use it: `foundational/` if any document might,
`domain-specific/` if exactly one domain owns it (and then namespace every class
with that domain's name). Add its `@import` and its layer name to the `@layer`
list in `css/docs-html.css`. Because layer order is declared up front, where you
put the `@import` does not matter — only the layer list does.

Put the matching component under the same group in `components/`, so the pair
stays findable from either side.
