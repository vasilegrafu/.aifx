# incident-postmortem

A blameless account of an incident: what happened, the timeline, root cause,
impact, and the action items that prevent recurrence.

- Audience: engineering, ops, leadership. Altitude: honest and factual.
- Filename: `docs/incident-postmortem-NNN-<slug>.html` (NNN = incident number).
- Template: `document.html.j2` (in this folder)
- Depth: `full`.

## Rules
- Blameless: describe systems and decisions, never blame a person.
- The timeline ([[timeline]]) uses real timestamps from detection to
  resolution.
- Root cause reaches the real cause (the "5 whys"), not the first symptom.
- Action items are a `ul.checklist` with an owner each; a postmortem with no
  action items failed.
- Severity, duration, and user impact are quantified in the summary.
