# developer-setup-guide

_Authoring guidance for the `developer-setup-guide` document type — audience, depth, and rules._

How a new developer gets the project running locally: prerequisites, setup,
running, common tasks, troubleshooting. Onboarding in one page.

- Audience: new developers. Altitude: concrete, step-by-step, copy-pasteable.
- Filename: `docs/developer-setup-guide.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` — ground every command in the real repo (scripts, README,
  package/manifest files, config).

## Research guidance
- Real prerequisites (versions), real setup commands, real run commands.
- Actual config files and environment variables the project needs.

## Rules
- Setup and run are `ol.steps` with copy-pasteable commands in `<code>`.
- Every command is real and ordered — a step that fails mid-way is a bug.
- Troubleshooting pairs a symptom with a fix; grow it from real friction.
