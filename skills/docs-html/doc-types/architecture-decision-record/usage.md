# architecture-decision-record (ADR)

One significant technical decision: context, options, decision, consequences.

- Audience: developers, future maintainers. Altitude: technical, terse, honest.
- Filename: `docs/architecture-decision-record-NNN-<slug>.html` — NNN =
  zero-padded next number (scan existing ADRs in `docs/`).
- Template: `document.html.j2` (in this folder)
- Depth: `full` (small scope — one decision, one code area; just do it)

## Research guidance
Read the code area the decision concerns: current implementation, its
dependencies, pain points visible in code/git history. Cite real files,
real constraints, real numbers. Check existing ADRs for related/conflicting
decisions and link them.

## Rules
- Exactly one `<aside class="decision">` in the Decision section.
- Minimum 2 options in Options Considered; rejected options get honest pros.
- A published ADR's Decision is immutable — a new ADR supersedes it;
  both metadata headers get Supersedes / Superseded-by rows linking each other,
  and the change-history records the supersession.
