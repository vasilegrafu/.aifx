# chart-apache-echarts

_Authoring guidance for the `chart-apache-echarts` component — when to use it, how, and the rules._

Styled by: `css/charts/charts.css` (the shared frame) +
`css/charts/chart-apache-echarts.css` (engine specifics)
Rendered by: the pinned Apache ECharts CDN script, loaded by the
`chart-apache-echarts` feature only when the document holds a matching element
(see SKILL.md). No `<script>` tag in the document — the feature self-loads the
engine, exactly like `math` (KaTeX). Renders **SVG** (crisp in print, one
`<main>` column).

For real data — bar, line, area, pie, scatter, heatmap, **candlestick/OHLC**,
boxplot. Prefer this over a Mermaid `xychart-beta` whenever the chart carries
analysis (multi-series, stacked, a legend, tooltips). Keep Mermaid for
*diagrams* (flow, sequence, ER); see [[mermaid]].

## Markup

The block wears two classes: `chart` is the marker every chart engine shares
(it selects the shared frame and the readable-source fallback), and
`apache-echarts` selects this engine. The macro writes both.

The body is a JSON ECharts `option` — data and encoding as plain, editable
text. Use a `{% raw %}{% call %}{% endraw %}` block so the JSON reads cleanly:

```html
{% raw %}{% call c.apache_echarts(height=320) %}{% endraw %}
{
  "xAxis": { "type": "category", "data": ["Q1", "Q2", "Q3", "Q4"] },
  "yAxis": { "type": "value" },
  "series": [{ "type": "bar", "name": "Revenue", "data": [120, 145, 132, 168] }]
}
{% raw %}{% endcall %}{% endraw %}
```

- `height` (default `340`) sets the card height in px; width is the column.
- The palette, ink, axes, grid, legend, and tooltip come from the built-in
  **docs-html theme** — do NOT set `color`/`textStyle` per chart. Just describe
  the data.

Every rendered chart carries a small toolbar (top-right of the card): **download
as SVG** and **copy the spec**. Both come from the shared frame, so any future
chart engine has them too.

## What the feature fills in for you

Applied only when you did not set them, so an explicit author always wins:

- `aria.enabled: true` — screen-reader description of the chart.
- `tooltip: {}` — hover layer on by default. For line/bar add
  `"tooltip": { "trigger": "axis" }`; pie/scatter keep the item default.
- `legend: {}` — added automatically when there are **≥ 2 series** (identity is
  never color-alone).

## Degradation (pure CSS + JS, automatic)

Until ECharts renders — or forever, if the CDN is unreachable, or the JSON is
invalid — the spec shows as a readable code box (`charts.css`). Invalid JSON
also gets a red border, and a page whose specs are *all* invalid never downloads
the engine at all. So write the `option` clean enough to read as text.

## Rules

- **Never restyle the theme.** No per-chart `color`, fonts, or axis colors — the
  palette is the Okabe-Ito reference set, colorblind-safe on the light surface;
  overriding it breaks that guarantee. Rebrand once, in `PALETTE`/`TOKENS`/`RAMP`
  in `js/modules/charts.js` — the shared layer, so every engine follows.
- **A spec may NAME a design colour** rather than write a hex: `"palette:3"`,
  `"token:positive"`, `"ramp:2"`. Use this when a mark genuinely needs a
  specific tone (a target `markLine`, a role-coloured node); never to
  hand-pick a series colour.
- **One y-axis.** No dual-axis charts (two value scales) — the #1 charting
  mistake. Two measures of different scale → two charts, or index to a common
  base. (ECharts will let you; don't.)
- **Legend for ≥ 2 series; direct-label ≤ 4.** Four palette slots sit below 3:1
  on the light surface — **4** (reddish purple), **5** (sky blue), **6**
  (orange) and **8** (yellow): when you use them, add visible data labels
  (`"label": { "show": true }`) or a table view so the series is legible, not
  color-alone (the *relief rule*). Slots 1-3 and 7 need no relief. Nothing
  enforces this — count the automatically-coloured series yourself.
- **Categorical series cap 8**, and only the first 4 for scatter/bubble/maps;
  past that, fold to "Other", facet, or small-multiple.
- **Charts are never images** — screenshots use [[figure]]. A chart is data.
- **Status colors are reserved** — never reuse good/warning/critical hues for a
  series (see the [[badge]]/callout tokens).

## When it is NOT a chart

A single headline number is a [[kpi-tiles]] tile, not a one-bar chart. A 2×2
positioning grid is [[risk-matrix]] or [[quadrant-map]]. Composition of a whole
may be a stacked bar rather than a pie. Pick the form for the data's job first.
