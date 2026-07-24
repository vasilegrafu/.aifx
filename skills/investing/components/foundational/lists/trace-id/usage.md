# trace-id

_Authoring guidance for the `trace-id` component — when to use it, how, and the rules._

Styled by: `css/lists.css`

Markup skeleton: `component.html.j2` in this folder — the canonical source the builder composes (parameters, if any, declared at its top). The example(s) below are filled illustrations.

Traceability anchors and links: a requirement defined once, referenced
from design docs, test cases, and risk registers — the raw material for a
traceability matrix.

## Markup
```html
<!-- definition (once, in the owning document) -->
<span class="req" id="REQ-042">REQ-042</span>

<!-- reference (anywhere else) -->
<a href="software-requirements-specification.html#REQ-042"
   data-trace="REQ-042">REQ-042</a>
```

## Rules
- IDs are unique across the whole workspace.
- Prefix by kind: `REQ-` requirements, `RISK-` risks, `TC-` test cases.
- References always link to the definition; `audit` checks the targets
  resolve.
