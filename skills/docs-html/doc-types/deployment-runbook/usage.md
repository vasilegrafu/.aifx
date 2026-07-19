# deployment-runbook

The exact procedure to deploy a release: prerequisites, pre-checks, deploy
steps, verification, rollback, contacts. Followed under pressure, so it is
unambiguous.

- Audience: whoever runs the deploy (possibly at 3am). Altitude: exact,
  copy-pasteable, no assumed knowledge.
- Filename: `docs/deployment-runbook-<system>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` — ground every command/step in the real pipeline and infra.

## Rules
- Deploy, verification, and rollback are `ol.steps` / `ul.checklist` with real
  commands — no "deploy as usual".
- Rollback is a first-class section, as detailed as the deploy — not an
  afterthought.
- Pre-checks and post-deploy verification are objective checklists.
- Emergency contacts and escalation are included.
