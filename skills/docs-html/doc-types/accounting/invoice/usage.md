# invoice

_Authoring guidance for the `invoice` document type — audience, depth, and rules._

- Audience: the client and both parties' bookkeeping.
- Filename: `docs/invoice-<number>.html` (numbers sequential, never reused).
- Depth: none — pure data entry.
- Rules: an issued invoice is IMMUTABLE — corrections happen via credit note
  (a new invoice with negative amounts), never by editing; check local legal
  requirements for mandatory fields (tax ids, VAT breakdown); Ctrl+P gives
  the PDF to send (print.css).
