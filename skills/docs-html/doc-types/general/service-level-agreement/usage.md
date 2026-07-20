# service-level-agreement (SLA)

_Authoring guidance for the `service-level-agreement` document type — audience, depth, and rules._

The commitment between a service provider and its consumers: services,
measurable service levels, responsibilities, reporting, and remedies.

- Audience: provider + consumer signatories. Altitude: contractual, measurable.
- Filename: `docs/service-level-agreement-<service>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` (a structured agreement — fill the terms).

## Rules
- Service levels are a table of metric → target → measurement window
  (e.g. "Availability → 99.9% → monthly"). Each target is measurable.
- Headline targets can also show as [[kpi-tiles]].
- Responsibilities of both parties are explicit.
- Remedies/penalties for breach are stated, not implied.
- Ends with the [[approval-block]].
