# technical-specification

_Authoring guidance for the `technical-specification` document type — audience, depth, and rules._

A focused engineering design for one feature or change: the problem, the
proposed approach, the detailed design, alternatives, rollout, and testing.
The "tech spec" / design-doc engineers write before building.

- Audience: engineering reviewers. Altitude: enough detail to review and
  build without re-deriving decisions.
- Filename: `docs/technical-specification-<feature>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the affected code and constraints.

## Rules
- Summary first: a reader gets the gist in the `.lead` paragraph.
- Alternatives considered are documented with why they were rejected (like an
  ADR, but broader scope).
- Rollout covers flags, migration, and backward compatibility.
- Diagrams for structure/flow; framed [[code-block]] for interfaces.

## Beyond software

This pattern is universal — the examples above are software-flavored, but the
same structure serves other fields (finance, engineering, operations,
research). Reuse it with domain judgment: keep the mechanics, swap the
vocabulary.
