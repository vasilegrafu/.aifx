# test-case-specification

The concrete test cases: id, preconditions, steps, expected result, and the
requirement each verifies.

- Audience: QA, engineers. Altitude: executable detail.
- Filename: `docs/test-case-specification-<area>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` for structure; `ask` if cases must be derived from real
  requirements/code.

## Rules
- Each case has a `TC-` id and traces to the `REQ-` id(s) it verifies.
- Steps are an `ol.steps`; the expected result is explicit and checkable.
- One behaviour per case — a case that tests two things is two cases.
- The summary counts cases by state ([[kpi-tiles]]) if execution status is
  tracked here.
