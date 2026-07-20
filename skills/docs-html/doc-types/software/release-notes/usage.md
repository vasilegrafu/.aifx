# release-notes

_Authoring guidance for the `release-notes` document type — audience, depth, and rules._

What changed in a release, for the people who consume it: added, changed,
fixed, deprecated, removed, plus upgrade notes and known issues. Keep a
Changelog style.

- Audience: users, operators, downstream developers. Altitude: outcomes, not
  implementation.
- Filename: `docs/release-notes-<version>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` — mine the real change set (git log, merged PRs, closed
  issues since the last release).

## Rules
- Group changes under Added / Changed / Fixed / Deprecated / Removed.
- User-facing language: what changed for them, not the commit message.
- Breaking changes are called out with upgrade steps — never buried.
- Known issues link to defect-report ids where they exist.

## Beyond software

This pattern is universal — the examples above are software-flavored, but the
same structure serves other fields (finance, engineering, operations,
research). Reuse it with domain judgment: keep the mechanics, swap the
vocabulary.
