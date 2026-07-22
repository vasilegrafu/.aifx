# Charts — charts

Declarative data charts — a spec in the document, rendered to SVG at view time, never a screenshot.

**Use when** the shape of the numbers carries the argument.

---

## The approved chart kinds

This is the list. A chart in a docs-html document is one of these forms, and
picking the form is the first decision — before the data, before the colours.
Anything not here is either a [[mermaid]] (a relationship, not a
measurement) or not a chart at all (see *When it is not a chart* below).

Two ways to reach them. A **preset** is a macro: you pass data, it writes the
spec. A **recipe** is a documented `option` you write directly through
[[apache-echarts]]. The split is deliberate — a preset exists only where
it computes something, enforces a rule, or prevents a known mistake. Everywhere
else a preset would just be indirection over JSON you can already read.

### Presets

| kind | call | what it is for |
|---|---|---|
| flow | `{{ c.sankey(...) }}` | how a total splits, merges or converts across stages — revenue to net income, cash sources to uses |
| price action | `{{ c.price_history(...) }}` | candlestick with volume beneath, one shared time axis |
| drawdown | `{{ c.drawdown_curve(...) }}` | peak-to-trough decline over time — the shape of the losing periods |
| distribution | `{{ c.return_distribution(...) }}` | the spread of an outcome rather than its average — box plot with outliers drawn, not absorbed |
| correlation | `{{ c.correlation_matrix(...) }}` | pairwise relationships across a set, on the sequential ramp |

### Recipes

| kind | series type | what it is for |
|---|---|---|
| trend | `line` | a measure over time; the default for anything with a date axis |
| comparison | `bar` | a measure across categories, ranked |
| composition | `bar` stacked | parts of a whole across time or category — prefer over `pie` past three slices |
| risk/return | `scatter` | two measures per entity — volatility against return, valuation against growth |

`risk-return` stays a recipe: its ECharts `option` is already about as short and
as readable as the data it carries, so a macro would hide the chart without
simplifying it. It is written out in full in [[apache-echarts]].

Distribution and correlation went the other way once it was clear what each had
to compute — Tukey fences and quartiles for one, a correctly wired sequential
`visualMap` for the other. That is the test: a preset earns its place by
computing something, enforcing a rule, or preventing a known mistake.

## Colour is not yours to choose

Every kind above takes its colours from the design system — the categorical
palette for series identity, the sequential ramp for ordered quantities, and
the semantic tones only for *direction*. All three live in
`js/modules/charts.js` and are checked by `python builder.py dataviz`.

A spec that genuinely needs to name one references it rather than writing a hex:
`"palette:3"`, `"token:positive"`, `"ramp:2"`. The presets above use exactly
this, which is why a fifteen-node sankey does not run out of colours and start
repeating them.

## When it is NOT a chart

A single headline number is a [[kpi-tiles]] tile, not a one-bar chart. A 2×2
positioning grid is [[risk-matrix]] or [[quadrant-map]]. A waterfall showing
how one total became another is [[bridge]] — it is a table with bars, needs no
engine, and prints. A schedule of amounts by year is [[debt-maturity]]. Reach
for a chart when the *shape* of the data is the argument; reach for an
investing component when the numbers are.
