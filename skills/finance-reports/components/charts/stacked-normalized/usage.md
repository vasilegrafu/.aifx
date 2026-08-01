# stacked-normalized

_Authoring guidance for the `stacked-normalized` component — when to use it, how, and the rules._

Each category as 100% — composition when the shares matter and the totals do not. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** you are comparing MIX across categories whose totals differ wildly. Normalising removes the size difference so the composition can be compared.

## Markup

```html
{% raw %}{{ c.stacked_normalized(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **The totals disappear.** That is the trade: a category worth $2M and one
  worth $2B become the same height. If size matters, pair this with a [[bar]]
  of the totals, or say the sizes in `note`.
- Values are converted to percentages of each column total **at compose time** —
  pass raw amounts, not pre-computed shares.
- Segments carry labels automatically, because a percentage nobody can read off
  a moving baseline is not information.
