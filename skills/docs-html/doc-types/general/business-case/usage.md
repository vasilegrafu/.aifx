# business-case

_Authoring guidance for the `business-case` document type — audience, depth, and rules._

Why the organisation should invest in this work: the problem, the options, the
money, and the recommendation. Answers "should we fund this?" — distinct from
`feasibility-study` (can it be done?) and `statement-of-work` (what will be
delivered, for whom).

- Audience: sponsors, budget owners, steering group. Altitude: financial and
  strategic — outcomes and cost, not implementation.
- Filename: `docs/business-case-<subject>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means real numbers (costs, benefits, payback), not
  placeholders.

## Rules
- Always include the **do-nothing** baseline as one of the options — the case
  is only meaningful relative to not acting.
- Costs and benefits are quantified in a table; soft benefits are listed
  separately and labelled as non-quantified.
- The financial summary (ROI, payback period, NPV where relevant) is stated as
  KPI tiles, and every figure traces to the costs/benefits table above it.
- The recommendation is one `<aside class="decision">` that follows from the
  analysis, with the funding ask and the reasoning after it.
- Close with an approval block — a business case is a decision artefact.
