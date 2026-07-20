# threat-model

_Authoring guidance for the `threat-model` document type — audience, depth, and rules._

- Audience: whoever must decide which attacks are worth defending against.
- Filename: `docs/threat-model-<system>.html`.
- Depth: ask — full means walking the real architecture.
- Rules: threats phrased attacker-first (who, does what, to which asset);
  every threat gets THR- id, probability and impact (the matrix visualizes
  the register); a threat without a mitigation OR an explicit acceptance is
  unfinished; revisit on architecture changes.
