# operations-runbook

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
