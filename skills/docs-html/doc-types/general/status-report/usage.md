# status-report

_Authoring guidance for the `status-report` document type — audience, depth, and rules._

A periodic project update: headline metrics, progress since last report,
what's next, risks and blockers.

- Audience: stakeholders, sponsors, team. Altitude: concise, scannable.
- Filename: `docs/status-report-<period>.html` (e.g. `-2026-w29`).
- Template: `document.html.j2` (in this folder)
- Depth: `full` — short by design; ground it in real progress (git, board).

## Rules
- Metrics first ([[kpi-tiles]]) — a reader gets the state in 5 seconds.
- Progress is outcomes, not activity ("shipped X", not "worked on X").
- Blockers name what is needed and from whom.
- Short: a status report is not a project plan — no front/back matter.
