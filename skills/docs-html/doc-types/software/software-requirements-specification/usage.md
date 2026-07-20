# software-requirements-specification (SRS)

_Authoring guidance for the `software-requirements-specification` document type — audience, depth, and rules._

The definitive statement of what the software must do — ISO/IEC/IEEE 29148
style. Functional and non-functional requirements, interfaces, constraints,
with full front/back matter.

- Audience: engineering, QA, product, stakeholders. Altitude: complete and
  precise — the contract for what gets built and tested.
- Filename: `docs/software-requirements-specification-<system>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full is a large effort (read the domain, existing code,
  interfaces). State scope and offer a draft skeleton first.

## Research guidance
- Existing behaviour in code (if the system exists) grounds requirements.
- External interfaces: real APIs, files, brokers, DBs the system touches.
- Non-functional targets: real latency/throughput/availability numbers.

## Rules
- Carries ISO front/back matter ([[front-back-matter]]): Purpose & Scope,
  Executive summary, then body, then References, Glossary, Appendices.
- Every requirement is a [[requirement]] card with a `REQ-` id, MoSCoW
  priority, and a measurable fit criterion. Never a bullet.
- Functional and non-functional requirements are separate sections.
- A requirements-traceability-matrix references these REQ- ids — keep them
  stable once Approved.
