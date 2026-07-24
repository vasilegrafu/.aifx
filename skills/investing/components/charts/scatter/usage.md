# scatter

_Authoring guidance for the `scatter` component — when to use it, how, and the rules._

Two measures per entity — where the relationship between them is the finding. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** each thing has two numbers and the question is how they relate — volatility against return, valuation against growth, size against margin.

## Markup

```html
{% raw %}{{ c.scatter(series=…, caption=…, x_name=…, y_name=…) }}{% endraw %}
```

Parameters: `series, caption, height, note, x_name, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Label the points that carry the argument.** Pass a third element in the
  tuple `(x, y, label)`. An unlabelled cloud is a shape, not an analysis.
- **Four series maximum**, and prefer one. Scatter markers are small, and the
  palette slots past the third need relief the markers cannot give.
- **Both axes named, both with units.** A scatter with bare numbers is
  unreadable.
- Correlation is not causation, and a fitted line is a claim — if you add one,
  defend it in `note`.
