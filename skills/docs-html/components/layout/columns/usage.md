# columns

_Authoring guidance for the `columns` component — when to use it, how, and the rules._

Styled by: `css/layout.css`

A responsive row that places its child [[column]] cells side by side. Cells are
equal width by default; they **wrap and stack** when the row gets narrow, and
collapse to one column in print. `columns` holds only `column` cells — put the
real components inside those.

## Markup

```html
{% raw %}{% call c.columns() %}
  {% call c.column() %}{{ c.chart_echarts(...) }}{% endcall %}
  {% call c.column() %}{% call c.callout("note") %}Reading of the chart…{% endcall %}{% endcall %}
{% endcall %}{% endraw %}
```

For an asymmetric split, give a cell a `span` (see [[column]]):
`{% raw %}{% call c.column(span=2) %}…{% endcall %}{% endraw %}` makes it twice as wide as a `span=1` neighbour.

## Rules

- **Cells are [[column]] only.** Never drop a component straight into `columns` —
  it must sit in a `column`.
- **Two or three cells.** Four is the ceiling; more equal tiles → use [[grid]].
- **Layout is an enhancement.** It stacks on phones and in print, so the document
  must still read correctly in one column. Don't hide meaning in the arrangement.
- **No nested `columns` inside a `column`** — split the section instead; nesting
  fights the stack-to-one-column rule.
