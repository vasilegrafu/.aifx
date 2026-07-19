# use-case-specification

One use case in full: actors, preconditions, the main flow, alternate and
exception flows, postconditions. Cockburn style.

- Audience: engineering, QA, product. Altitude: behavioural — interaction
  steps, not implementation.
- Filename: `docs/use-case-specification-<name>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` (one use case — structure and write it).

## Rules
- The main flow is an `ol.steps` — numbered actor/system interactions.
- Alternate and exception flows reference the main-flow step they branch from
  (e.g. "3a. If the password is wrong...").
- Preconditions and postconditions are checkable states, not prose.
- Give the use case a `UC-` id in the title; trace it to `REQ-` ids it
  realises.
