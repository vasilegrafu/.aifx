# defect-report

_Authoring guidance for the `defect-report` document type — audience, depth, and rules._

One defect, documented so anyone can reproduce and fix it: environment,
steps, expected vs actual, evidence, root cause, fix.

- Audience: engineers, QA. Altitude: precise and reproducible.
- Filename: `docs/defect-report-NNN-<slug>.html` (NNN = next defect number).
- Template: `document.html.j2` (in this folder)
- Depth: `full`.

## Rules
- Give it a `DEF-` id; link the `TC-`/`REQ-` it violates.
- Steps to reproduce are an `ol.steps` — deterministic, numbered.
- Expected vs actual are stated side by side, unambiguously.
- Severity and priority are separate fields (impact vs urgency).
- Evidence (logs, payloads) uses `<details>` or framed [[code-block]];
  screenshots use [[figure]] with alt text.

## Beyond software

This pattern is universal — the examples above are software-flavored, but the
same structure serves other fields (finance, engineering, operations,
research). Reuse it with domain judgment: keep the mechanics, swap the
vocabulary.
