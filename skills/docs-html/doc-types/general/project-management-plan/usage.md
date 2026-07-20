# project-management-plan

_Authoring guidance for the `project-management-plan` document type — audience, depth, and rules._

How a project will be run: scope, schedule, team, milestones, risks,
communication. The PMBOK-style baseline the team commits to.

- Audience: sponsors, team, stakeholders. Altitude: managerial — commitments
  and boundaries, not implementation.
- Filename: `docs/project-management-plan.html` (one per project; variants
  carry the scope in the slug).
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the repo, backlog, and git history to
  ground schedule/scope in reality. Offer a draft skeleton first.

## Research guidance
- Scope in vs out — be explicit about exclusions.
- Milestones with real dates or quarters; use a [[timeline]].
- Team roles: who owns what. Risks use `<aside class="risk">` (audit collects).

## Rules
- Every commitment is measurable or dated — no "soon", no "TBD" without a
  `<mark class="todo">`.
- Scope exclusions are as important as inclusions; list both.
- Milestones in the timeline match the schedule section — keep them in sync.
