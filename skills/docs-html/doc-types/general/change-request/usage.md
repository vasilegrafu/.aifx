# change-request

_Authoring guidance for the `change-request` document type — audience, depth, and rules._

A proposed change to a controlled system, for review and approval: what,
why, impact, rollout, rollback, sign-off. ITIL change-management style.

- Audience: change advisory board, owners. Altitude: decision-grade.
- Filename: `docs/change-request-NNN-<slug>.html` (NNN = next CR number).
- Template: `document.html.j2` (in this folder)
- Depth: `full`.

## Rules
- Give it a `CR-` id. Impact analysis covers affected systems, users, and
  risk — not just the happy path.
- Rollout and rollback are both concrete (`ol.steps`).
- Ends with the [[approval-block]].
- A change with no rollback is a risk to call out explicitly.
