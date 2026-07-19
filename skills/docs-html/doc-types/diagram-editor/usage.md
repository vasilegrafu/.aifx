# diagram-editor

A diagram workspace: one Mermaid diagram and nothing else. The document IS the
diagram — open it in a browser and use the viewport's own tools (✎ edit with
live preview, pan/zoom, fit, fullscreen, resize grip, download SVG, copy
source) to work on it.

- Audience: whoever is authoring or reviewing a single diagram — this is a
  working document, not a report.
- Filename: `docs/diagram-editor.html`, or `docs/diagram-editor-<topic>.html`
  when a project keeps several.
- Depth: none — the skeleton ships a minimal starter diagram; the content IS
  whatever the diagram becomes.

## Workflow
1. `python builder.py new diagram-editor "<title>"` — composes the document
   with a starter `flowchart`.
2. Open it, press ✎, edit the source with live preview.
3. Edits are session-only: press the copy button, then paste the source over
   the `<pre class="mermaid">` content in the file to keep it.

## Rules
- Exactly one `diagram-mermaid` component in the body — no TOC, no sections,
  no prose. If the diagram needs explanation, it belongs in a real document
  type that embeds a diagram.
- Metadata header stays (title/author/date/version identify the workspace).
