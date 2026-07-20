# database-design-document

_Authoring guidance for the `database-design-document` document type — audience, depth, and rules._

The data layer: entity-relationship model, tables/columns, keys, indexes,
constraints, migrations, retention.

- Audience: engineering, DBAs. Altitude: schema-level.
- Filename: `docs/database-design-document-<db>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the real models/migrations/DDL.

## Research guidance
- Entities and relations from the actual models (an `erDiagram`).
- Real table and column names, types, keys, indexes.
- Migration strategy and any partitioning/retention policy.

## Rules
- The ER model is a Mermaid `erDiagram`, not an image.
- Tables documented with real column names and types; DDL uses the framed
  [[code-block]] (`sql`) with tokens.
- Note keys, indexes, and constraints — they are design, not incidental.
