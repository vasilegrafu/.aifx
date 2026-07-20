# sprint-retrospective

_Authoring guidance for the `sprint-retrospective` document type — audience, depth, and rules._

A team's reflection on an iteration: what went well, what didn't, and the
improvements to try next. Blameless and action-oriented.

- Audience: the delivery team. Altitude: honest, internal.
- Filename: `docs/sprint-retrospective-<sprint>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full`.

## Rules
- Blameless: focus on process and systems, never individuals.
- Every retro produces action items (`ul.checklist`) with owners — a retro
  with no actions changed nothing.
- Optional headline metrics ([[kpi-tiles]]): velocity, carryover, etc.
- Carry last retro's actions forward and mark whether they were done.

## Beyond software

This pattern is universal — the examples above are software-flavored, but the
same structure serves other fields (finance, engineering, operations,
research). Reuse it with domain judgment: keep the mechanics, swap the
vocabulary.
