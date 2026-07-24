# segment-reporting

_Authoring guidance for the `segment-reporting` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Each segment's revenue and profit with TWO share bars — share of revenue and
share of profit — because the gap between them is usually the whole analysis.
A segment at 26% of revenue and 41% of profit is a different company from the
one the headline revenue split describes, and no single-bar chart shows it.

```jinja
{{ c.segment_reporting(
    caption="Revenue and gross profit by category, FY2025", unit="$M",
    revenue_label="Revenue", profit_label="Gross profit",
    source="Segment note, FY2025 Form 10-K page 41.",
    rows=[
        ("iPhone",            "205,600", 49.4, "76,100", 38.7, "37.0%", "+2.1%"),
        ("Services",          "109,200", 26.2, "80,800", 41.1, "74.0%", "+13.6%"),
        ("Wearables & Home",   "41,300",  9.9, "18,100",  9.2, "43.8%", "-1.2%"),
        ("Mac",                "31,200",  7.5, "11,500",  5.9, "36.9%", "+4.0%"),
        ("iPad",               "28,900",  6.9, "10,100",  5.1, "34.9%", "+5.1%"),
    ],
    total_row=("Total", ["416,200", "100.0%", "196,600", "100.0%", "47.2%", "+6.4%"])) }}
```

Rules: use the company's OWN reported segments — a re-cut of the disclosure is
your estimate and must be labelled as one. Both share columns sum to 100%;
if the company does not disclose profit by segment, say so in the caption and
leave the profit columns empty rather than allocating costs yourself. Name the
profit measure exactly (`gross profit`, `operating income`, `segment adjusted
EBITDA`) — "profit" alone is not a defined term. Corporate and unallocated
costs get their own row; hiding them inflates every segment's margin. Segments
sort by revenue descending. When a segment's share of profit exceeds its share
of revenue by more than about ten points, that segment IS the thesis — link it
to a pillar in `thesis_pillars`.
