# product-requirements-document (PRD)

_Authoring guidance for the `product-requirements-document` document type — audience, depth, and rules._

What to build and why, from the product side: problem, users, goals,
requirements, success metrics. The bridge between a business need and an SRS.

- Audience: product, engineering, design, stakeholders. Altitude: what and
  why — not how.
- Filename: `docs/product-requirements-document-<product>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means grounding requirements and metrics in the real
  product/codebase.

## Research guidance
- The problem, stated as a user problem, not a solution.
- Goals AND explicit non-goals.
- Requirements as [[requirement]] cards with MoSCoW priority and trace-ids.
- Success metrics as [[kpi-tiles]] with targets.

## Rules
- Non-goals are mandatory — they scope the product as much as goals.
- Every requirement is a `requirement` card with a `REQ-` id, never a bullet.
- Success metrics are measurable with a target value, not aspirations.

## Beyond software

This pattern is universal — the examples above are software-flavored, but the
same structure serves other fields (finance, engineering, operations,
research). Reuse it with domain judgment: keep the mechanics, swap the
vocabulary.
