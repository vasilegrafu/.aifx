# kpi-tiles

_Authoring guidance for the `kpi-tiles` component — when to use it, how, and the rules._

Styled by: `css/blocks.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

A row of headline metrics — the dashboard strip at the top of a status
report, test summary, or release note. Big number, label, optional trend.

## Markup
```html
<div class="kpi-tiles">
  <div class="kpi">
    <span class="kpi-value">99.2%</span>
    <span class="kpi-label">Test pass rate</span>
    <span class="kpi-trend up">▲ 1.4 pts</span>
  </div>
  <div class="kpi">
    <span class="kpi-value">3</span>
    <span class="kpi-label">Open blockers</span>
    <span class="kpi-trend down">▼ 2</span>
  </div>
  <div class="kpi">
    <span class="kpi-value">142</span>
    <span class="kpi-label">Commits this sprint</span>
    <span class="kpi-trend flat">—</span>
  </div>
</div>
```

## Trend
`up` = green, `down` = red, `flat` = grey. Direction is about the metric's
*health*, not its arithmetic: fewer open blockers is `down` and good — pick
the arrow to match the number, the colour to match the meaning if they
disagree, and say so in surrounding prose.

## Rules
- 2–5 tiles per row; the grid wraps on narrow screens.
- `kpi-value` is a single figure — no sentences. Units belong in the value
  (`500 ms`, `99.2%`) or the label.
- The trend span is optional; omit it when there is no prior period.
