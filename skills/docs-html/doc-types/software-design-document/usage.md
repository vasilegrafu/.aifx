# software-design-document (SDD)

How the software is built to meet the SRS: components, their responsibilities,
data design, interfaces, and the decisions behind them.

- Audience: engineering. Altitude: design — module boundaries and contracts,
  not line-by-line code.
- Filename: `docs/software-design-document-<system>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the codebase's structure and data model.

## Research guidance
- Component decomposition and dependency directions (a `flowchart`).
- Data model (an `erDiagram`) grounded in the real schema.
- Interfaces between components: what each exposes and consumes.
- Existing ADRs → the design references them, never restates them.

## Rules
- Every structural claim is diagrammed or cited — no prose-only design.
- Trace design elements back to `REQ-` ids they satisfy.
- Code samples use the framed [[code-block]] with generation-time tokens.
- Design decisions link ADRs; do not duplicate their content here.
