# financial-table

_Authoring guidance for the `financial-table` component — when to use it, how, and the rules._

Styled by: `css/modules/business.css`

THE numeric report table: first column left-aligned (labels), all others
right-aligned with tabular numerals. Row kinds: `""` normal, `"subtotal"`
(bold, rule above), `"total"` (bold, double rule above).

```jinja
{{ c.financial_table(
    caption="Income statement — FY2026 (EUR)",
    headers=["", "FY2025", "FY2026"],
    rows=[
      ("", ["Revenue", "1,200", "1,450"]),
      ("", ["Cost of sales", '<span class="neg">(700)</span>', '<span class="neg">(810)</span>']),
      ("subtotal", ["Gross profit", "500", "640"]),
      ("", ["Operating expenses", '<span class="neg">(320)</span>', '<span class="neg">(355)</span>']),
      ("total", ["Operating profit", "180", "285"]),
    ]) }}
```

Rules: format numbers as strings (thousands separators, currency in the
caption or header — not per cell); negatives in parentheses wrapped in
`<span class="neg">` (renders red); never mix units in one column.
