# decision-record

_Authoring guidance for the `decision-record` document type — audience, depth, and rules._

- Audience: anyone later asking "why is it like this?" — the domain-neutral
  sibling of architecture-decision-record: same mechanics, any field
  (equipment choice, policy change, provider selection, investment process).
- Filename: `docs/decision-record-NNN-<slug>.html` (NNN sequential, like ADRs).
- Depth: full — a decision record is written when the decision is made.
- Rules: a decided record's Decision section is IMMUTABLE — supersede with a
  new record linked both ways; rejected options stay in the document (they
  are the value); consequences include the bad ones.
