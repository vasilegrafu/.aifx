# stacked-area

_Authoring guidance for the `stacked-area` component — when to use it, how, and the rules._

Parts summing to a whole over time — composition and total in one figure. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** the total and its composition both matter over time — revenue by segment, assets by class.

## Markup

```html
{% raw %}{{ c.stacked_area(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Only stack additive quantities.** The stack asserts the parts sum to the
  total.
- **Only the bottom band is measurable.** Bands above sit on a moving baseline,
  so a reader can judge their share but not their trend. Put the series you
  most want compared at the bottom.
- Past ~5 bands nobody can track a band across the chart.
- If shares matter more than totals, use [[stacked-normalized]].
