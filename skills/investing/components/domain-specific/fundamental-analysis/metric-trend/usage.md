# metric-trend

_Authoring guidance for the `metric-trend` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The operating history in one table: a metric per row, a reporting period per
column, then the compound growth rate and a direction glyph. Use it for the
five-year picture that precedes any valuation work — revenue, margins,
returns on capital, cash conversion, share count.

```jinja
{{ c.metric_trend(
    caption="Apple — five-year operating record ($B unless noted)",
    periods=["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"],
    rows=[
        ("Revenue",            ["365.8", "394.3", "383.3", "391.0", "416.2"], "+3.3%",  "up"),
        ("Gross margin",       ["41.8%", "43.3%", "44.1%", "46.2%", "46.9%"], "+2.9pp", "up"),
        ("Operating income",   ["108.9", "119.4", "114.3", "123.2", "133.0"], "+5.1%",  "up"),
        ("Diluted shares (M)", ["16,865", "16,326", "15,813", "15,408", "14,948"], "-3.0%", "down"),
    ]) }}
```

Rules: label the unit once in the caption, never per cell. Periods run oldest
to newest, left to right — never reversed. `dir` describes the METRIC, not
whether it is good news: a falling share count is `down` and that is fine;
the reader judges. CAGR states its own basis (%, or pp for margins). Restated
figures carry the restatement in a footnote, not a silent overwrite. For more
than about seven periods use `apache_echarts` — a table stops being readable.
