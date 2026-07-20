# risk-assessment

_Authoring guidance for the `risk-assessment` document type — audience, depth, and rules._

- Audience: whoever accepts the residual risk — the FMEA/HAZOP-style
  engineering assessment (risk-register is its general-management sibling).
- Filename: `docs/risk-assessment-<subject>.html`.
- Depth: full — done with the people who know the failure modes.
- Rules: cause and effect separated (one failure, many causes = many rows);
  scores use the declared scales; every risk above the acceptance threshold
  gets a control with owner and RESIDUAL score — a control that doesn't move
  the score is decoration.
