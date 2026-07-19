# generic-document

Fallback for any document without a dedicated doc-type yet. If the same
kind is requested twice, propose promoting it: `new type <name>` adds a
dedicated doc-type + template to the skill.

- Audience/altitude: per request — ask if unclear.
- Filename: `docs/<slug>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` unless the scope is obviously small.

## Rules
- Compose only from `components/` components.
- Structure the sections yourself to fit the content — the template's
  sections are placeholders, replace them freely.
- Adjust the head to the components you use: add `callouts.css` /
  `diagrams.css` / `lists.css` links as needed, and the Mermaid script
  before `</body>` if the document has diagrams.
