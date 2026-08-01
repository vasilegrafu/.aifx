# bar-negative

_Authoring guidance for the `bar-negative` component — when to use it, how, and the rules._

A measure that crosses zero — variance, surprise, contribution. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** the sign is the story: budget variance, earnings surprise, attribution by contributor.

## Markup

```html
{% raw %}{{ c.bar_negative(series=…, categories=…, caption=…, y_name=…) }}{% endraw %}
```

Parameters: `series, categories, caption, height, note, y_name`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- Bars are coloured by **sign, not by series** — the positive and negative
  direction tones. That is the documented exception to *status colours are
  reserved*: direction is not identity.
- **Colour is never the only cue** — the bar's side of the zero line says the
  same thing, which matters because the two tones are exactly the pair that
  collapses under deuteranopia.
- One series. Two series of signed bars in one figure cannot be read.
