# width

_Authoring guidance for the `width` component — when to use it, how, and the rules._

Styled by: `css/layout.css`

Constrains any component(s) to a **fixed width** instead of filling the column.
Every other component is full-width by design (the container owns geometry); wrap
one in `width` when a fixed size reads better — a narrow chart, a small figure, a
compact table. It never overflows: on a narrow screen or in print it shrinks to
fit (`max-width: 100%`).

## Markup

```html
{% raw %}{% call c.width("18rem") %}{{ c.apache_echarts(...) }}{% endcall %}

{% call c.width("30rem", align="center") %}
  {{ c.figure(...) }}
{% endcall %}{% endraw %}
```

- `w` (default `"24rem"`) — the width. Any CSS length: `"320px"`, `"18rem"`, `"40%"`.
- `align` (default `"left"`) — `left`, `center`, or `right` within the column.

## Rules

- **Wrap, don't widen.** Never add a width to a component's own macro — geometry
  lives in this wrapper so components stay portable (the [[base]] contract).
- Prefer `rem`/`%` over `px` so it scales with the reader's font size.
- Don't use it to force two things side by side — that's [[columns]]. `width` is
  about one block being narrower than the column.
- It caps width; it never forces overflow. A wide table still scrolls inside its
  own component, not the page.
