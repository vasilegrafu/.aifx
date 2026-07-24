# balance-sheet

_Authoring guidance for the `balance-sheet` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The balance sheet across periods, using the same line kinds as
`income_statement`, plus one thing the income statement does not need: an
explicit balance check. The `check` string states the identity in words and the
component marks it as balancing or not — a balance sheet published without that
arithmetic done is a balance sheet nobody checked.

```jinja
{{ c.balance_sheet(
    caption="Consolidated balance sheets", unit="$M",
    source="FY2025 Form 10-K, page 33.",
    periods=["FY2023", "FY2024", "FY2025"],
    check="Total assets $377,300M = total liabilities $306,000M + shareholders' equity $71,300M.",
    balanced=true,
    rows=[
        ("Assets",                        [],                                  "section",  ""),
        ("Cash and cash equivalents",     ["29,965", "29,943", "32,400"],      "detail",   ""),
        ("Accounts receivable, net",      ["29,508", "33,410", "35,900"],      "detail",   ""),
        ("Total current assets",          ["143,566", "152,987", "162,500"],   "subtotal", ""),
        ("Total non-current assets",      ["209,017", "211,993", "214,800"],   "subtotal", ""),
        ("Total assets",                  ["352,583", "364,980", "377,300"],   "total",    ""),
        ("Liabilities and equity",        [],                                  "section",  ""),
        ("Total current liabilities",     ["145,308", "176,392", "176,600"],   "subtotal", ""),
        ("Term debt",                     ["95,281", "85,750", "82,300"],      "detail",   "12"),
        ("Total liabilities",             ["290,437", "308,030", "306,000"],   "subtotal", ""),
        ("Total shareholders' equity",    ["62,146", "56,950", "71,300"],      "subtotal", ""),
        ("Total liabilities and equity",  ["352,583", "364,980", "377,300"],   "total",    ""),
    ]) }}
```

Rules: the check is written out and verified by hand — set `balanced=false` and
say why in the text if the figures you have do not tie, rather than quietly
adjusting a number. Order is assets, then liabilities, then equity; current
before non-current within each. Contra-equity lines (accumulated deficit,
treasury stock, accumulated other comprehensive loss) stay negative in
parentheses — never flip their sign to make the section read tidily. Cite the
note on debt, leases, pensions and anything with an off-balance-sheet
component. Same periods, in the same order, as the `income_statement` and
`cash_flow_statement` in the same document.
