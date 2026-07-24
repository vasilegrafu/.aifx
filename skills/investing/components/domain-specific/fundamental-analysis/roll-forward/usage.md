# roll-forward

_Authoring guidance for the `roll-forward` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Opening balance, every movement, closing balance. The universal shape of a note
to the accounts — property and equipment, goodwill, provisions, deferred
revenue, loan loss reserves, share count, shareholders' equity — and the fastest
way to see whether a balance moved because of trading or because of an
accounting choice.

```jinja
{{ c.roll_forward(
    caption="Share count roll-forward (millions of diluted shares)",
    periods=["FY2023", "FY2024", "FY2025"],
    note="Buybacks retired 3.0% of shares a year; issuance is settled RSUs.",
    rows=[
        ("Opening balance",              ["16,326", "15,813", "15,408"], "opening"),
        ("Shares issued on settlement",  ["92",     "88",     "84"],     "movement"),
        ("Shares repurchased",           ["(605)",  "(493)",  "(544)"],  "movement"),
        ("Closing balance",              ["15,813", "15,408", "14,948"], "closing"),
    ]) }}
```

Rules: opening plus movements must equal closing in every column — verify each
column by hand, because a roll-forward that does not foot is the single most
embarrassing error in a financial document. Each movement is a CAUSE, not a
category: "shares repurchased" not "other changes"; a movement line called
"other" that exceeds about 5% of the opening balance must be broken out. Signs
follow the balance's own direction, in accounting parentheses. Use the same
periods and order as the statements in the same document. One balance per
table — a combined roll-forward of three different balances cannot be checked.
