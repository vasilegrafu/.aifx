# rollback-plan

_Authoring guidance for the `rollback-plan` document type — audience, depth, and rules._

How to safely revert a release or change: trigger conditions, impact, exact
rollback steps, verification, and data considerations.

- Audience: operators, release managers. Altitude: exact and reversible.
- Filename: `docs/rollback-plan-<release>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full`.

## Rules
- Trigger conditions are objective ("error rate > 2% for 5 min"), not "if it
  looks bad".
- Data considerations are explicit: is the migration reversible? what about
  data written since deploy? This is the part that bites — do not skip it.
- Rollback steps are `ol.steps` with real commands; verification is a
  checklist.
- Often embedded in a deployment-runbook; use this standalone type for
  high-risk changes that need a dedicated plan.
