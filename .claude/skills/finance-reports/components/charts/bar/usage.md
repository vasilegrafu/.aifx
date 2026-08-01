# bar

_Authoring guidance for the `bar` component — when to use it, how, and the rules._

A measure across categories — the workhorse comparison. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** you are comparing discrete things. Length from a common baseline is the most accurately read encoding there is, which is why this should be the default before anything cleverer.

## Markup

```html
{% raw %}{{ c.bar(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **The axis starts at zero.** Non-negotiable for bars: length IS the value, so
  a truncated axis multiplies differences.
- **Sort by value** unless the categories carry their own order (time, ratings,
  maturity buckets).
- Long category names? Use [[stacked-horizontal-bar]] or its unstacked form —
  rotated labels are a workaround, not a fix.
