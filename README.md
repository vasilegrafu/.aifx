# .claudefx

Personal Claude Code skills, tracked as their own repository and mounted as a
git submodule by the solutions that use them.

- `skills/docs-html/` — a design system for professional documents as clean,
  hand-editable HTML: one CSS + one JS, component catalog, SDLC doc-types,
  Mermaid diagrams with pan/zoom and a live source editor. See its README
  and SKILL.md.

This repository is also the CDN origin: versioned tags are served by jsDelivr,
e.g. `https://cdn.jsdelivr.net/gh/vasilegrafu/.claudefx@1.0.0/skills/docs-html/css/docs-html.css`.
Version source of truth: `skills/docs-html/version.json` + `version.md`.
Published tags are immutable.
