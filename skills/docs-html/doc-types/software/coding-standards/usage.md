# coding-standards

_Authoring guidance for the `coding-standards` document type — audience, depth, and rules._

The team's rules for writing code: naming, formatting, patterns to use and
avoid, testing expectations, tooling. The reference a reviewer cites.

- Audience: developers. Altitude: prescriptive and concrete.
- Filename: `docs/coding-standards.html` (or `-<language>` per language).
- Template: `document.html.j2` (in this folder)
- Depth: `full` (write the rules; ground examples in the real codebase's
  conventions where one exists).

## Rules
- Every rule pairs a "do" with a "don't" using the framed [[code-block]]
  (good vs bad), not prose alone.
- Rules are enforceable — say which are automated (linter/formatter) vs
  reviewer-judged.
- No rule without a reason; a rule nobody can justify is deleted.
