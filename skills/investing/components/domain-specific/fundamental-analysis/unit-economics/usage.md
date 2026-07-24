# unit-economics

_Authoring guidance for the `unit-economics` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

What one customer costs to acquire, what one customer is worth, and how long
the money is out. For any subscription, marketplace or lending business this
decides whether growth creates value or destroys it — a company can grow
revenue at 60% a year and be worth less each year if the payback period is
longer than the customer's life.

```jinja
{{ c.unit_economics(
    caption="Unit economics — FY2025 cohort",
    headline=[("LTV / CAC", "3.4x"), ("CAC payback", "17 months"), ("Gross margin", "78%")],
    tone="good", benchmark_label="SaaS median",
    verdict="Economics work, but the margin is thinner than the headline ratio suggests: at a 17-month payback, growth is cash-consuming for at least six quarters.",
    note="LTV uses gross profit, not revenue, and caps customer life at 5 years. CAC is fully loaded, including sales salaries and brand marketing.",
    rows=[
        ("Customer acquisition cost (CAC)", "$14,200", "$12,000", "Fully loaded; up 22% y/y as the channel mix shifted to paid."),
        ("Annual contract value",           "$18,600", "$16,400", "Up 9% on price, flat on seats."),
        ("Gross margin",                    "78%",     "76%",     "Hosting scales; support does not."),
        ("Annual gross profit per customer", "$14,500", "$12,500", "The real numerator for LTV."),
        ("Annual churn",                    "9%",      "12%",     "Better than median; enterprise mix helps."),
        ("Implied customer life",           "5 years (capped)", "6 years", "Capped rather than 1/churn — an 11-year life is not evidenced."),
        ("Lifetime value (LTV)",            "$48,300", "$45,000", "Gross profit basis, 5-year cap, undiscounted."),
    ]) }}
```

Rules: compute LTV on GROSS PROFIT, never on revenue — the revenue version
overstates value by the whole cost base and is the most common abuse of this
table. CAC is fully loaded (all sales and marketing, not just paid
acquisition). Cap customer life at a defensible horizon rather than using
1/churn, which produces absurd lives at low churn rates; say that you capped it.
State whether LTV is discounted. Payback period matters more than the LTV/CAC
ratio for a cash-constrained business, so lead with it in `headline`. Where the
figures are your estimates rather than disclosure, mark them — most companies do
not publish CAC, and a reconstructed number needs its method in `note`.
