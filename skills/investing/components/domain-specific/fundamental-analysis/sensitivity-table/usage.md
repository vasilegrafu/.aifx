# sensitivity-table

_Authoring guidance for the `sensitivity-table` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The two-way grid: one output across two assumptions, colour-graded, with the
base case outlined. The standard output of any discounted cash flow — value per
share across discount rate and terminal growth — and equally the right shape for
earnings across price and volume, or LBO returns across entry and exit multiple.
It is the honest form: it shows the answer is a range governed by two numbers.

```jinja
{{ c.sensitivity_table(
    caption="Value per share ($) — DCF sensitivity",
    row_label="WACC", col_label="Terminal growth",
    cols=["2.0%", "2.5%", "3.0%", "3.5%", "4.0%"],
    note="Spot $232. The base case assumes WACC 8.5% and terminal growth 3.0%.",
    rows=[
        ("7.5%", [("268", "high", False), ("284", "high", False), ("305", "high", False), ("332", "high", False), ("368", "high", False)]),
        ("8.0%", [("246", "high", False), ("259", "high", False), ("275", "high", False), ("296", "high", False), ("322", "high", False)]),
        ("8.5%", [("227", "mid",  False), ("238", "mid",  False), ("251", "mid",  True),  ("267", "high", False), ("287", "high", False)]),
        ("9.0%", [("211", "low",  False), ("219", "low",  False), ("230", "mid",  False), ("243", "mid",  False), ("259", "high", False)]),
        ("9.5%", [("196", "low",  False), ("203", "low",  False), ("212", "low",  False), ("222", "low",  False), ("234", "mid",  False)]),
    ]) }}
```

Rules: exactly ONE cell carries `base=True` — the assumption set you actually
believe, so the reader can see how much of your conclusion survives moving one
step in either direction. Tones are assigned against a stated reference (here,
spot price): `low` below it, `mid` near it, `high` comfortably above. Say what
the reference is in `note` — an unexplained colour gradient is decoration.
Five by five is the readable maximum. Step the assumptions evenly. If the sign
of your conclusion flips inside the grid, that IS the finding and belongs in the
text, not just in a colour. Never tune the grid bounds until the base case sits
in a comfortable colour.
