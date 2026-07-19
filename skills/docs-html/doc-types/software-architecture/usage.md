# software-architecture

The system's structure: context, containers, components, data, deployment,
decisions, risks. C4-inspired.

- Audience: developers, architects. Altitude: structural — what exists and
  why, not code walkthroughs.
- Filename: `docs/software-architecture.html` (one per system; per-subsystem
  variants get the subsystem in the slug: `software-architecture-<subsystem>.html`)
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the whole solution structure (typically
  20–40 files). State the scope and offer draft first.

## Research guidance
- Solution layout: projects/packages, their dependency directions.
- Entry points, external systems touched (APIs, DBs, brokers, files).
- Data: main entities, where stored, how they flow.
- Deployment reality: what runs where (check configs, docker files, scripts).
- Existing ADRs → the Decisions section links them, never restates them.

## Rules
- Every structural claim must be diagrammed or cited — no prose-only architecture.
- Mermaid: `flowchart` for context/containers, `erDiagram` for data where
  useful; keep each diagram readable, split rather than cram.
- The Decisions section is a table linking ADRs — content lives in the ADRs.
- Risks use `<aside class="risk">` so audit can collect them.
