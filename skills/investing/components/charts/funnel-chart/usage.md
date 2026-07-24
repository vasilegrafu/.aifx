# funnel-chart

_Authoring guidance for the `funnel-chart` component — when to use it, how, and the rules._

Stage-to-stage narrowing — a rendered funnel with proportional bands. Rendered by [[apache-echarts]] through the
shared chart frame, so it carries the same toolbar, the same validated palette
and the same readable-source fallback.

**Use when** a population narrows through ordered stages and the drop between stages is the point.

## Markup

```html
{% raw %}{{ c.funnel_chart(stages=…, caption=…) }}{% endraw %}
```

Parameters: `stages, caption, height, note`.

Colours come from the design system — never set them per chart. `caption` is the
figure title, `note` the one-line reading beneath it. Say what the shape MEANS
in `note`; the chart shows it, the sentence argues it.

## Rules

- **Stages must be nested**, each a subset of the one above. A funnel of
  unrelated categories is a sorted bar chart wearing a costume.
- **Say WHY each stage is smaller** in `note`. An unexplained drop is a
  question, not a finding.
- **Consider [[funnel]] instead** — the CSS component needs no engine, prints,
  and keeps its numbers as selectable text.
