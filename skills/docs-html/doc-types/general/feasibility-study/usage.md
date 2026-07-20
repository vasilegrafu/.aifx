# feasibility-study

_Authoring guidance for the `feasibility-study` document type — audience, depth, and rules._

Can this be done, and should it? Technical, economic, and operational
feasibility of options, ending in a recommendation.

- Audience: decision-makers, sponsors. Altitude: analytical.
- Filename: `docs/feasibility-study-<subject>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means real investigation of options and costs.

## Rules
- At least two options plus the do-nothing baseline.
- Each feasibility dimension (technical / economic / operational) is assessed
  per option — no hand-waving.
- The recommendation is one `<aside class="decision">` with the reasoning
  after it; it must follow from the analysis above, not precede it.
