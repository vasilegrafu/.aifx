# user-story-backlog

An agile backlog: epics and user stories with acceptance criteria and
priority. A living, ordered list.

- Audience: product, engineering. Altitude: increments of value.
- Filename: `docs/user-story-backlog.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` if stories must be derived from a real codebase/roadmap;
  otherwise `full`.

## Rules
- Stories follow "As a {role}, I want {goal}, so that {benefit}".
- Each story has explicit acceptance criteria (a `ul.checklist`) and a
  `STORY-` id.
- Ordering is priority — top of the backlog is next. Use MoSCoW
  (`req-priority`) or an explicit order column, not both.
- Epics group stories; a story belongs to exactly one epic.
