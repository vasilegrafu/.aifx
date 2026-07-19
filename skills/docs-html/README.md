# docs-html

A skill for producing professional documents as clean, hand-editable HTML.
Every document wires up the whole design system with **two lines** — one
stylesheet and one script — a light theme, no framework at view time. Documents
live in `<project>/docs/` as the single source of truth and are git-versioned.

Documents are **composed** by `builder.py` (a Jinja2 driver). Jinja runs only at
compose time; the output is standalone, hand-editable HTML with no template
syntax left. There is **no publish step and no build step** — the document you
compose is the document you ship.

## The two assets

Every document links exactly these, resolved back to this skill:

```html
<link rel="stylesheet" href="<skill>/css/docs-html.css">
<script src="<skill>/js/docs-html.js" defer></script>
```

- **`css/docs-html.css`** — one stylesheet. Sets cascade order with `@layer`,
  then `@import`s the modules in `css/modules/`. Documents link only this file.
- **`js/docs-html.js`** — one script, and like the CSS it is only an entry: it
  loads `js/modules/` in order (classic script injection — ES modules don't
  work on `file://`). `core.js` is a tiny feature registry; each feature is a
  self-contained module activated by its markup (`layout-toggle.js` on
  `.doc-toolbar`, `diagrams.js` on `pre.mermaid` — Mermaid + Panzoom from CDN,
  pan/zoom, SVG-icon toolbar: zoom ± with live %, fit, reset, fullscreen,
  download SVG, copy source). New behaviour = new module + one entry in the
  `MODULES` list; no per-document JS ever.

## Layout

```
docs-html/
├── SKILL.md            authoring contract + command recipes
├── builder.py          compose base + doc-type template + component macros → docs/<name>.html
├── css/
│   ├── docs-html.css   the single stylesheet (@layer + @import)
│   └── modules/*.css   the modules it imports
├── js/
│   ├── docs-html.js    the single script: entry/loader (MODULES list)
│   └── modules/*.js    core (registry) · util · icons · layout-toggle · diagrams · main
├── components/
│   ├── <name>/
│   │   ├── usage.md           guidance: when + how to use, and the rules
│   │   └── component.html.j2  a Jinja macro — the callable markup
│   └── showcase.html          curated live gallery of every component
└── doc-types/
    ├── base.html.j2          the shared shell (head + toolbar + <main> + {% block content %})
    └── <name>/
        ├── usage.md          audience, depth, research, rules
        └── document.html.j2  {% extends base %}; body is ONLY macro calls
```

## Workflow

Run from the project root. Prefix with `!` in the Claude prompt to run
in-session, or type them in a terminal — same commands.

1. **Compose** — `python builder.py new <type> "<title>"` writes a standalone
   `docs/<slug>.html` (base shell + the type's macro calls + component macros;
   the two asset links, author, and date resolved automatically). It won't
   overwrite an existing document without `--force`.
2. **Fill** the `{{...}}` placeholders with real content; keep the TOC in sync
   with the sections.

That's it — open the file in a browser to view; there is no export.

Other commands:

```
python builder.py --list        # doc-types
python builder.py showcase      # regenerate components/showcase.html
```

PDF: open a document and Ctrl+P → Save as PDF (`print.css` handles pagination).

## How templates work

A doc-type `document.html.j2` contains **only component-macro calls** — no raw
HTML:

```jinja
{# type-name: Software Requirements Specification #}
{% extends "doc-types/base.html.j2" %}
{% block content %}
  {{ c.toc([("purpose", "Purpose & scope"), ("functional", "Functional requirements")]) }}

  {% call c.section("purpose", "Purpose & scope") %}
    {% call c.prose() %}{% raw %}{{what this covers}}{% endraw %}{% endcall %}
  {% endcall %}

  {% call c.section("functional", "Functional requirements") %}
    {{ c.requirement(id="REQ-001", priority="must", label="Must") }}
  {% endcall %}
{% endblock %}
```

Every component is a macro on the `c` namespace (no imports). Leaves use
`{{ c.name(...) }}`; containers use `{% call c.name(...) %}…{% endcall %}`. The
base shell writes the two asset links; the body is pure component calls.

## Extending

- **New doc-type** — add `doc-types/<name>/usage.md` + `document.html.j2`
  (`{% extends "doc-types/base.html.j2" %}` with a body of only macro calls).
- **New component** — add `components/<name>/usage.md` (guidance) +
  `component.html.j2` (a `{% macro %}`), style it in a `css/modules/` file (add
  its `@import` to `css/docs-html.css`), and add it to the showcase.
- **Rebrand** — edit `css/modules/brand.css` (`--brand-name`, accent colour); it
  cascades to every document.

`builder.py` needs `jinja2`; viewing does not. See `SKILL.md` for the full
authoring contract and the complete doc-type catalog.

## Versioning

The design-system version lives ONLY in `version.json` (source of truth) +
`version.md` (changelog + semver contract) at the skill root — never in the
CSS or JS. On a CDN the URL path carries it (`…/docs-html@X.Y.Z/…`); relative
imports pin the whole asset tree to one version. Releases via the `release`
command in SKILL.md; published versions are immutable.

## Local-first, CDN fallback

Documents always try the local skill assets first; when `version.json` carries
a `cdn` base URL, the builder adds an `onerror` fallback to both head tags —
a document opened where the skill doesn't exist heals itself from the
version-pinned CDN copy (pinned at compose time). While `cdn` is empty, heads
carry plain local links.

## CDN (live)

This skill's repo — `github.com/vasilegrafu/.claudefx`, mounted as a git
submodule by consuming solutions — is also the CDN origin: jsDelivr serves its
tags at `https://cdn.jsdelivr.net/gh/vasilegrafu/.claudefx@X.Y.Z/skills/docs-html/…`.
Releasing = tagging (see SKILL.md `release`); published tags are immutable.
