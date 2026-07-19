# table

Styled by: `css/content.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Tabular data: comparisons, matrices, inventories.

## Markup
```html
<table>
  <thead><tr><th>Option</th><th>Pros</th><th>Cons</th></tr></thead>
  <tbody>
    <tr><td>PostgreSQL</td><td>mature, SQL</td><td>ops overhead</td></tr>
  </tbody>
</table>
```

## Variants
- `class="wide"` — for many columns: the table scrolls horizontally inside
  itself (pure CSS) instead of overflowing the page.

## Rules
- Always a `<thead>`; header cells are `<th>`.
- Zebra striping and borders come from CSS — never add styling attributes.
