# radar

_Authoring guidance for the `radar` component — when to use it, how, and the rules._

Several attributes of a few entities at once — profile shape, not precise values. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** you are comparing the SHAPE of two or three profiles across the same attributes — a scorecard across candidates.

## Markup

```html
{% raw %}{{ c.radar(indicators=…, series=…, caption=…) }}{% endraw %}
```

Parameters: `indicators, series, caption, height, note`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Axis order changes the shape.** The same data in a different order draws a
  different polygon, and neither is more true. Fix the order deliberately and
  keep it across figures.
- **Area is not meaningful** — it scales with the square of the values and with
  axis order. Read vertices, never area.
- Maxima are derived from the data unless you pass them (`(name, max)`). Ad-hoc
  per-axis maxima let you draw any shape you like.
- Three series maximum. Beyond that it is a web.
- **A table is usually better.** Use [[scorecard]] when the numbers matter more
  than the silhouette.
