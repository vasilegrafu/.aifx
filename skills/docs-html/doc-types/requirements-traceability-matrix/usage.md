# requirements-traceability-matrix (RTM)

The grid that proves coverage: each requirement traced to its design element,
implementation, and the test(s) that verify it.

- Audience: QA, engineering leads, auditors. Altitude: cross-reference.
- Filename: `docs/requirements-traceability-matrix.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reconciling the real SRS, design, and test docs.

## Rules
- The matrix is a `table.wide` (it scrolls, the page does not).
- Columns: REQ- id → design ref → code/module → TC- id(s) → status.
- Every `REQ-` from the SRS appears exactly once; a requirement with no test
  is a coverage gap — flag it with `<mark class="todo">` or a risk.
- Cells reference real ids from the other documents ([[trace-id]]); this doc
  links them, it does not restate their content.
- The coverage summary ([[kpi-tiles]]) counts covered vs total.
