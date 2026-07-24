# heatmap

_Authoring guidance for the `heatmap` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

A grid of values with colour carrying the magnitude. Three canonical uses:
monthly returns by year (the standard track-record table), correlation
matrices, and performance grids of sector against region. The author assigns
each cell a level from −3 to +3 — the component never computes buckets, so the
thresholds are yours, stated, and consistent across documents.

```jinja
{{ c.heatmap(
    caption="Monthly total return (%)", corner="Year",
    legend="Levels: ±1 under 2%, ±2 two to five percent, ±3 above 5%.",
    cols=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "YTD"],
    rows=[
        ("2024", [("2.1", 2), ("-1.4", -1), ("3.8", 2), ("-5.9", -3), ("4.2", 2), ("1.1", 1), ("3.5", 2)]),
        ("2025", [("-0.8", -1), ("2.9", 2), ("1.2", 1), ("6.4", 3), ("-2.2", -2), ("0.4", 0), ("7.9", 3)]),
        ("2026", [("1.8", 1), ("3.1", 2), ("-0.6", 0), ("2.4", 2), ("1.9", 1), ("2.1", 2)]),
    ]) }}
```

Rules: state the level thresholds in `legend` — an unexplained gradient is
decoration, and the same number must get the same colour in every document in a
project. Level 0 is genuinely neutral, not "small positive". Rows shorter than
the column list pad with blanks, which is how a part-year row or the empty half
of a correlation matrix renders. Keep cell text to four characters or fewer;
this is a shape to scan, and the exact figures belong in a `table` if they
matter individually. For a correlation matrix, show one triangle only — a
mirrored matrix doubles the ink for no information.
