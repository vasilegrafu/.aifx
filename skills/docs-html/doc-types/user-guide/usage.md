# user-guide

End-user documentation: how a person uses the product to get their work done.
Task-oriented and written for the reader's goals, not the system's internals.
Distinct from `developer-setup-guide` (engineers building the software) and
`operations-runbook` (operators running it in production).

- Audience: end users, non-technical. Altitude: task — steps a user follows,
  in the user's vocabulary.
- Filename: `docs/user-guide-<product>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means every core task written out with real steps.

## Rules
- Organise by **what the user wants to do**, one task per subsection, each a
  numbered `ol.steps` the reader can follow start to finish.
- Second person, imperative ("Select…", "Enter…"). No implementation detail,
  no internal component names the user never sees.
- Illustrate with figures (screenshots) where a picture removes ambiguity;
  every figure has a caption and alt text.
- Troubleshooting is a symptom → cause → fix table, phrased from what the user
  observes.
- Define any unavoidable jargon in the glossary; prefer plain words in the body.
