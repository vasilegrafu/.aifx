# gauge

_Authoring guidance for the `gauge` component — when to use it, how, and the rules._

One value against a range — a dial, for a single bounded measure. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** a single value is genuinely bounded and the position within its range is the message — utilisation against capacity, a covenant against its limit.

## Markup

```html
{% raw %}{{ c.gauge(value=…, minimum=…, maximum=…, caption=…, unit=…) }}{% endraw %}
```

Parameters: `value, minimum, maximum, caption, height, note, unit`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Read this before using it.** A gauge spends a great deal of ink on one
  number. The design system's own rule is that a single headline number is a
  [[kpi-tiles]] tile; a gauge is that tile with a dial drawn around it. It
  earns its place only when the RANGE is as important as the value.
- **The range must be real.** A gauge from 0 to 100 on an unbounded measure
  invents the ceiling, and the needle's position is then meaningless.
- **No danger bands.** Deliberately not offered: colouring the arc adds a
  judgement the number does not carry. Put the threshold in `note`, or use
  [[meter]], which states value and target as text.
- One gauge, never a wall of them. A row of dials is a table.
