# cohort-table

_Authoring guidance for the `cohort-table` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Cohorts down the side, periods since acquisition across the top, forming the
characteristic triangle — recent cohorts have fewer observations, so their rows
are shorter. The definitive shape for subscription retention, net revenue
retention, and loan loss curves by vintage. It separates a business that is
growing from one that is churning and replacing.

```jinja
{{ c.cohort_table(
    caption="Net revenue retention by signup cohort (%)",
    size_label="Accounts", periods=["M0", "M6", "M12", "M18", "M24", "M30"],
    note="Levels: 5 above 120%, 4 is 105–120%, 3 is 95–105%, 2 is 80–95%, 1 below 80%. Cohorts from FY2025 retain materially worse at M12 — the mix shifted to self-serve.",
    rows=[
        ("FY2023 H1", "1,240", [("100", 3), ("104", 4), ("118", 4), ("126", 5), ("131", 5), ("138", 5)]),
        ("FY2023 H2", "1,510", [("100", 3), ("102", 3), ("115", 4), ("121", 5), ("128", 5)]),
        ("FY2024 H1", "1,880", [("100", 3), ("101", 3), ("110", 4), ("114", 4)]),
        ("FY2024 H2", "2,240", [("100", 3), ("98",  3), ("104", 3)]),
        ("FY2025 H1", "2,910", [("100", 3), ("94",  2)]),
        ("FY2025 H2", "3,400", [("100", 3)]),
    ]) }}
```

Rules: state the level thresholds in `note` — the colours are your buckets and
mean nothing without them. Every cohort starts at 100 in M0 (or at its own
starting count); a table where cohorts start at different bases cannot be
compared down a column. Read DOWN the columns, not across the rows: comparing
M12 across cohorts is the test of whether the business is getting better or
worse, and that comparison is the reason for the shape. Short rows are correct
for young cohorts — never extrapolate to fill the triangle. Say what changed
when a column deteriorates, since the cause (mix, pricing, product) determines
whether it recovers.
