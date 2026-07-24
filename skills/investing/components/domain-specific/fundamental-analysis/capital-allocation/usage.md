# capital-allocation

_Authoring guidance for the `capital-allocation` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Where the cash went, over several years, as a share of the cash that came in.
No filing presents this table — you build it — and it is the single most direct
evidence about management. A company that has spent 70% of a decade's operating
cash on buybacks at rising multiples has told you what it thinks about its own
reinvestment opportunities.

```jinja
{{ c.capital_allocation(
    caption="Uses of operating cash, FY2021–FY2025", unit="$M",
    periods=["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"],
    source_line=("Operating cash flow", ["104,038", "122,151", "110,543", "118,254", "128,900"], "583,886"),
    note="Buybacks were executed at an average of 27x trailing earnings.",
    rows=[
        ("Capital expenditure", ["(11,085)", "(10,708)", "(10,959)", "(9,447)",  "(12,100)"], "(54,299)",  9.3),
        ("Acquisitions",        ["(33)",     "(306)",    "(1,445)",  "(620)",    "(800)"],    "(3,204)",   0.5),
        ("Dividends",           ["(14,467)", "(14,841)", "(15,025)", "(15,234)", "(15,900)"], "(75,467)",  12.9),
        ("Buybacks",            ["(85,971)", "(89,402)", "(77,550)", "(94,949)", "(95,000)"], "(442,872)", 75.8),
        ("Net debt repayment",  ["(7,500)",  "(9,543)",  "(11,151)", "(9,958)",  "(8,000)"],  "(46,152)",  7.9),
    ]) }}
```

Rules: five years minimum — capital allocation is a decade-scale question and a
two-year window shows nothing. The `source_line` is the denominator and must be
stated; percentages that sum past 100% mean the company funded uses with debt or
cash reserves, which is itself the finding, so do not scale them to fit. Use the
company's cash flow statement figures unadjusted. For buybacks, state the average
multiple paid in `note` — buying back stock is an investment decision and is
judged like one. Where a use is lumpy (one large acquisition), call it out rather
than letting the average hide it.
