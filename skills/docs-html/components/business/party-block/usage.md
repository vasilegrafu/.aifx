# party-block

_Authoring guidance for the `party-block` component — when to use it, how, and the rules._

Styled by: `css/modules/business.css`

Two-party identity block side by side (From/To, Issuer/Client,
Contractor/Customer) — for invoices, proposals, statements of work,
agreements.

`{{ c.party_block(from_lines=["Name", "Address", "Tax id"], to_lines=[...]) }}`

Rules: line one is the legal name; include what the document type legally
requires (tax ids on invoices); titles adjustable via `from_title`/`to_title`.
