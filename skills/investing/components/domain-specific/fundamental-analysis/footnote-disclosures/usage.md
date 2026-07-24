# footnote-disclosures

_Authoring guidance for the `footnote-disclosures` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The numbered notes to the accounts, each anchored at `id="note-<num>"` so that
`note=` on any line of `income_statement`, `balance_sheet` or
`cash_flow_statement` links straight to it. The `watch` flag is the analytical
act: most disclosures are boilerplate, and marking the two or three that change
what the statements mean is the reason to reproduce them at all.

```jinja
{{ c.footnote_disclosures(caption="Notes cited in the statements above", items=[
    (2, "Revenue recognition",
     "Services revenue is recognised over the contract term. Deferred revenue of $9.1B at year end is disclosed separately and is not in the Services line above.",
     ""),
    (5, "Income taxes",
     "The FY2024 provision includes a one-off $10.2B charge from the European Commission State Aid decision. The FY2025 effective rate of 17.0% is the run rate; FY2024 net income is not comparable without adjusting for it.",
     "watch"),
    (8, "Share-based compensation",
     "$12.6B was expensed in FY2025 and added back in operating cash flow. Dilution is offset by buybacks, so the cost is real but does not appear in the share count.",
     "watch"),
    (12, "Debt and commitments",
     "Term debt of $82.3B has a weighted average rate of 3.1% and a maturity wall of $18.4B in FY2027. Operating lease commitments of $14.2B are not included in term debt.",
     ""),
]) }}
```

Rules: reproduce only the notes a statement line actually cites — a full note
set belongs in the filing, not in your document. Every note is SUMMARISED in
your own words with the figures kept exact; never paste the filing's language
and never paraphrase a number. `watch` means the note changes how a statement
line should be read, and each flagged note says what it changes, in the note
body. Note numbers must match the source filing's numbering — renumbering them
to be contiguous breaks the reader's ability to check you. Notes appear after
the statements they annotate, in ascending order.

Distinct from `footnotes` (front-back-matter), which is scholarly apparatus for
citing sources anywhere in a document. This component is the accounting
disclosure set, and its anchors are a statement's cross-reference target.
