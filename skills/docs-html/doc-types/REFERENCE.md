# doc-types/ — reference

The curated taxonomy of document types. The authoritative, always-current list
is generated — `../CATALOG.md` (names + purposes, grouped by domain) or
`python builder.py --list` (names by domain). This file is the human map: the
same types organized into meaningful groups, with notes the flat list can't
carry.

Each type is a folder `doc-types/<domain>/<name>/` holding a `usage.md` and a
`document.html.j2`. The type's identity is its own folder name (unique across
all domains) — commands take the type name alone, never the domain. Types marked
† are universal patterns whose recipes are still software-flavored — reusable in
other fields with judgment (each carries a "Beyond software" note in its
`usage.md`).

**general/** — any field

| Group | Types |
|---|---|
| Initiation & Planning | business-case, project-charter, feasibility-study, statement-of-work, proposal, project-management-plan, roadmap, risk-register |
| Governance & Operations | decision-record, policy, standard-operating-procedure, change-request, incident-postmortem, service-level-agreement, user-guide |
| Communication | status-report, meeting-minutes, presentation |

**software/** — SDLC

| Stage | Types |
|---|---|
| Requirements | product-requirements-document †, software-requirements-specification, use-case-specification †, user-story-backlog, requirements-traceability-matrix † |
| Design | architecture-decision-record †, software-architecture, software-design-document, api-specification, database-design-document, user-interface-design-specification, threat-model |
| Implementation | coding-standards, developer-setup-guide, technical-specification † |
| Testing | test-plan, test-case-specification, test-summary-report, performance-test-report, defect-report † |
| Deployment & Operations | release-notes †, deployment-runbook †, rollback-plan, operations-runbook †, data-migration-plan, disaster-recovery-plan |
| Process | sprint-retrospective †, project-closure |

**finance/** — budget, cash-flow-forecast, management-report,
net-worth-statement, valuation-report

**investing/** — investment-thesis, due-diligence-report, portfolio-review,
trade-journal, investment-policy-statement, market-outlook,
strategy-specification, backtest-report, watchlist, earnings-note

**accounting/** — financial-statements, invoice, credit-note, expense-report,
reconciliation-report

**research/** — research-report, data-analysis-report, literature-review,
white-paper, experiment-log

**economics/** — economic-analysis, policy-brief, industry-analysis

**engineering/** — design-calculation-note, equipment-specification,
inspection-report, failure-analysis, bill-of-materials, risk-assessment,
maintenance-plan, commissioning-report

**tools/** — diagram-editor (one Mermaid diagram, nothing else — a workspace for
the built-in ✎ editor)

**fallback/** — generic-document

## Abbreviations

When the user gives an abbreviation, translate it to the full type name (the
builder accepts only full names): ADR → architecture-decision-record, SRS →
software-requirements-specification, PRD → product-requirements-document, SOW →
statement-of-work, SDD → software-design-document, RTM →
requirements-traceability-matrix, API spec → api-specification, SLA →
service-level-agreement, postmortem → incident-postmortem, CR → change-request,
runbook → deployment-runbook or operations-runbook (ask which if ambiguous),
retro → sprint-retrospective, changelog → release-notes.

## Adding a doc-type

Add `doc-types/<domain>/<name>/{usage.md, document.html.j2}` (pick the domain
folder from above; a genuinely new domain gets a new folder — the builder
discovers recursively). See `../SKILL.md` → "new type" for the template shape,
and run `python builder.py catalog` afterward.
