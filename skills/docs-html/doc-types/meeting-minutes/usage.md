# meeting-minutes

The record of a meeting: attendees, agenda, discussion, decisions, and action
items with owners.

- Audience: attendees + absent stakeholders. Altitude: factual record.
- Filename: `docs/meeting-minutes-<date>-<topic>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full`.

## Rules
- Decisions are captured as `<aside class="decision">` — findable later.
- Action items are a `ul.checklist`, each with an owner and (ideally) a due
  date. An action with no owner will not happen.
- Discussion is summarised, not transcribed — capture conclusions and the
  reasoning that mattered, not every remark.
