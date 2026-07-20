# project-charter

_Authoring guidance for the `project-charter` document type — audience, depth, and rules._

The document that formally authorises a project and names its manager: purpose,
objectives, scope boundary, stakeholders, high-level milestones and budget, and
the sponsor's sign-off. It is the *mandate to start* — short, signed, and
stable. Distinct from `project-management-plan` (the detailed *how*), which the
charter authorises.

- Audience: sponsor, project manager, stakeholders. Altitude: authorising —
  boundaries and accountability, not execution detail.
- Filename: `docs/project-charter-<project>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` (one project — structure and write it).

## Rules
- Scope is stated as two explicit lists: **in scope** and **out of scope**. An
  empty out-of-scope list is a red flag, not a convenience.
- Objectives are measurable (SMART) — each is a checkable outcome, not an
  aspiration.
- Name a single accountable project manager and the sponsor; list other
  stakeholders with their interest/role.
- Milestones are high-level dates on a timeline, not a work breakdown.
- Assumptions and constraints are recorded — the charter is the reference when
  they later change.
- Ends with the sponsor's authorisation (approval block); the charter has no
  force until signed.
