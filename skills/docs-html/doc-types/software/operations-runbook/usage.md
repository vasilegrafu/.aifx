# operations-runbook

_Authoring guidance for the `operations-runbook` document type — audience, depth, and rules._

How to run and keep a service healthy day to day: overview, routine tasks,
alerts and their responses, escalation, recovery procedures.

- Audience: on-call and operations. Altitude: operational, exact.
- Filename: `docs/operations-runbook-<service>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the real deployment, alerts, and
  recovery scripts.

## Rules
- Alerts map to responses in a table: alert → what it means → what to do.
- Routine and recovery procedures are `ol.steps` with real commands.
- An architecture diagram (Mermaid) orients the reader; delete if trivial.
- Escalation path names roles/rotations, not individuals where possible.

## Beyond software

This pattern is universal — the examples above are software-flavored, but the
same structure serves other fields (finance, engineering, operations,
research). Reuse it with domain judgment: keep the mechanics, swap the
vocabulary.
