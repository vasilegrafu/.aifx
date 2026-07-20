# journal-entry

_Authoring guidance for the `journal-entry` component — when to use it, how, and the rules._

Styled by: `css/modules/business.css`

An accounting journal entry: debit/credit lines under an Account | Debit |
Credit header, with date, optional entry id, and a memo line. Credit-line
accounts are automatically indented (the bookkeeping convention).

```jinja
{{ c.journal_entry(id="JE-042", date="2026-07-19",
    memo="Broker commission on IBKR trade #18841",
    lines=[
      ("Trading commissions expense", "12.50", ""),
      ("Cash — broker account", "", "12.50"),
    ]) }}
```

Rules: debits before credits; every entry balances (state totals in the memo
when many lines); amounts as formatted strings, one currency per entry.
