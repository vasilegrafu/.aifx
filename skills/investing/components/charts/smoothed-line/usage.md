# smoothed-line

_Authoring guidance for the `smoothed-line` component — when to use it, how, and the rules._

A measure over time drawn as a smooth curve — trend over tick-by-tick detail. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** the shape of the trend is the point and the individual observations are not. Smoothing is a claim that the wiggles are noise.

## Markup

```html
{% raw %}{{ c.smoothed_line(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Smoothing invents values between your points.** The curve passes through
  your data but the path between is interpolation, not measurement. Never
  smooth a series a reader might read intermediate values off.
- Never smooth sparse data — with six points the curve is mostly invention.
- If the volatility IS the finding, use [[line]].
