# test-plan

_Authoring guidance for the `test-plan` document type — audience, depth, and rules._

How testing will be done: scope, approach, what to test, environment,
schedule, entry/exit criteria, risks. IEEE 829 style.

- Audience: QA, engineering, leads. Altitude: strategy, not individual cases.
- Filename: `docs/test-plan-<system>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means grounding scope/environment in the real system.

## Rules
- Entry and exit criteria are checklists — objective, checkable conditions.
- Features to test trace to `REQ-` ids; out-of-scope features are listed too.
- Individual test cases live in a test-case-specification, not here — this is
  the strategy.
- Test risks use `<aside class="risk">`.
