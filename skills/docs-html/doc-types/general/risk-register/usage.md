# risk-register

_Authoring guidance for the `risk-register` document type — audience, depth, and rules._

A living catalogue of project/product risks: likelihood, impact, owner,
mitigation, status. Reviewed on a cadence.

- Audience: project lead, team, sponsors. Altitude: managerial.
- Filename: `docs/risk-register.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` for the structure; `ask` if risks must be mined from code /
  incident history.

## Rules
- Each risk carries a `RISK-` trace-id (identity, referable from other docs).
- Score = likelihood x impact; keep the scale consistent and stated.
- Every open risk has a named owner and a mitigation — no orphan risks.
- Closed risks stay in the register with status `Closed`, not deleted
  (audit trail).
