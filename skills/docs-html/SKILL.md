---
name: docs-html
description: Generate, maintain, and audit professional documents as clean,
  manually-editable HTML. Covers software / SDLC documents (ADR, SRS,
  architecture, test plan, release notes, runbook, status report, meeting
  minutes, presentation) and extends to other domains (management, corporate,
  finance, economics). Use when the user asks to create, modify, update, or
  audit any such document.
---

# docs-html — professional documents in HTML, one CSS + one JS

A design system and component catalog for authoring professional documents as
hand-editable HTML. The **software / SDLC** family is built out (see the
catalog below); the same components, CSS, and JS host further domains
(management, corporate, finance, economics) as they are added — each new domain
contributes `doc-types/` recipes, reusing the shared `components/`, `css/`, and
`js/`.

An HTML document is the single source of truth. It contains only semantic HTML
composed from the component catalog, and wires up the whole design system with
**exactly two lines**: one stylesheet and one script.

```html
<link rel="stylesheet" href="<skill>/css/docs-html.css">
<script src="<skill>/js/docs-html.js" defer></script>
```

There is **no publish step and no build step.** A document references the shared
`css/` and `js/` assets directly; there is no per-document CSS selection, no
inlining, no generated export. The document you compose is the document you ship.

Paths below are relative to this skill directory.

## The two assets

**`css/docs-html.css`** — the single stylesheet. It sets the cascade order once
with `@layer`, then `@import`s the modules in `css/modules/`. A document links
only this file.

| module (css/modules/) | styles |
|---|---|
| `brand.css` | organization identity: `--brand-name`, `--brand-accent`. Imported by base.css — never referenced by documents. THE file a corporation edits to rebrand everything |
| `base.css` | fonts (Inter + JetBrains Mono via CDN), tokens, typography, layout, the layout-toggle toolbar, opt-in numbering — always |
| `metadata.css` | metadata-header (cover title block), change-history, approval-block |
| `toc.css` | the static TOC (regular documents; not presentations) |
| `content.css` | table, plain code, figure, collapsible |
| `code.css` | framed code blocks (`figure.code` title bar) + the runtime syntax palette (`.token.*`, applied by docs-html.js/Prism) |
| `callouts.css` | callout, todo-marker |
| `lists.css` | facts, steps, checklist, trace-id |
| `blocks.css` | requirement card, acceptance-criteria (Given/When/Then), kpi-tiles, timeline, glossary, revision-note, ISO front/back matter |
| `diagrams.css` | diagram-mermaid: the pan/zoom viewport + glyph toolbar |
| `presentation.css` | presentation pages (`<body class="presentation">`) |
| `print.css` | Ctrl+P → cover page, page breaks — layered LAST |

Every document links the whole stylesheet; there is no tree-shaking. The CSS is
small and a single cached file beats a per-document set. `@layer` makes the
cascade order explicit and independent of import order, so modules can be added
or reordered without specificity surprises.

**`js/docs-html.js`** — the single script a document links; like the CSS entry,
it only loads the real code from `js/modules/` (classic `<script>` injection in
list order — ES modules are blocked on `file://`). The modules form a tree on
the one `docsHtml` namespace:

| module (js/modules/) | role |
|---|---|
| `core.js` | the trunk: `docsHtml.register(feature)` + `init()`. A feature = `{name, selector, init}`; markup absent → dormant; a failing feature degrades itself only |
| `util.js` | leaf helpers: `loadScript`, `copyText`, `downloadBlob` |
| `icons.js` | the inline SVG icon set (Lucide-style strokes, currentColor) |
| `layout-toggle.js` | feature on `.doc-toolbar`: the ▯/▭ width switch |
| `highlight.js` | feature on `code[data-lang]`: runtime syntax coloring (Prism core + autoloader, lazy; grammars on demand). Exposes `docsHtml.highlight.ensure()/element()` for other features |
| `diagrams.js` | feature on `pre.mermaid`: everything diagrams — CDN pins, `DiagramViewer` class (pan/zoom + toolbar from a declarative `BUTTONS` spec); the source editor reuses `highlight` for a colored overlay |
| `main.js` | `docsHtml.init()` on DOM-ready — final, never edited |

**Extending**: new behaviour = new `js/modules/<name>.js` that calls
`docsHtml.register(...)` + its name in the `MODULES` list in `docs-html.js`.
`core.js`/`main.js`/other features stay untouched — `js/README.md` is the
feature-author guide (contract, skeleton, rules). Features read per-document
options from `data-` attributes on their own markup via
`docsHtml.data(el, "option-name", fallback)` (e.g.
`<pre class="mermaid" data-max-scale="10">` raises that diagram's zoom cap) —
there is **no per-document JavaScript**, ever; every behaviour keys off markup
the author already writes:

- `.doc-toolbar [data-w]` → the page / full-width **layout toggle** (adds/removes
  `class="wide"` on `<body>`; which button looks active is decided in CSS).
- `pre.mermaid` → a **diagram**: rendered, then made **pan/zoomable**.

It loads the heavy engines from CDN **only when a document actually contains a
diagram** — a diagram-free document fetches nothing extra:

- Mermaid `11.4.1` — renders every `<pre class="mermaid">` with
  `useMaxWidth:false` (natural pixel size; a node's box is the same across every
  diagram regardless of node count).
- Panzoom `@panzoom/panzoom@4.6.0` — wraps each rendered diagram in a bounded
  viewport with **drag-to-pan**, **Ctrl+wheel zoom**, and an icon toolbar
  (inline SVG icons, Lucide-style strokes, no icon files): zoom out · live
  zoom-% · zoom in │ fit-to-view · reset-100% │ fullscreen │ ✎ edit-source │
  download-SVG · copy-Mermaid-source. The **✎ editor** opens a **side panel**
  left of the diagram — its own column, the diagram is never covered (the SVG
  lives in a `.mermaid-canvas` pane that shrinks beside it; drag the panel's
  right-edge grip to resize, 256px minimum, double-click resets) — re-rendering
  after a typing pause while **preserving the current pan/zoom** (so you can
  stay zoomed into the region you are editing); parse errors show under the
  textarea and the last good render stays. Edits are **session-only** (a
  `file://` page cannot save itself): the copy button carries the edited
  source back into the document. The viewport opens at the diagram's natural height
  capped at `70vh` (diagrams that fit show in full; larger ones are
  panned/zoomed, never shrunk), and a **grip pill on the bottom edge resizes it
  vertically** — drag to grow or shrink, double-click to reset. Plain
  mouse-wheel still scrolls the page.

If the CDN is unreachable, `diagrams.css` leaves the Mermaid source visible as a
readable code box — the page still works, just without rendered diagrams.

**The href to the skill** is resolved by `builder.py` at compose time and used
for both lines:
- Document on the SAME drive as this skill → the relative path from `docs/`,
  i.e. `../.claude/skills/docs-html` — portable for everyone who clones.
- A DIFFERENT drive → the absolute `file:///` URL of this skill directory. If
  the skill moves, sweep the documents' heads.

**Versioning.** The design-system version lives in exactly two files at the
skill root and NOWHERE else (not in the CSS, not in the JS): `version.json`
(machine-readable source of truth: `version`, `date`, `cdn` base URL) and
`version.md` (the human changelog, one entry per release, semver contract
documented at its top). On a CDN the version is carried by the URL path
(`…/docs-html@X.Y.Z/css/docs-html.css`) — relative `@import`s and the JS
loader's self-resolved base pin the whole asset tree to one version
automatically. See the `release` command below.

**Local-first, CDN fallback.** Documents always try the LOCAL skill assets
first (instant dev feedback); when `version.json` has a `cdn` base, the
builder adds an `onerror` fallback to both head tags so a document opened
where the skill doesn't exist heals itself from the version-pinned CDN copy
(the version is baked at compose time — a document falls back to the design
system it was authored against). The CDN is LIVE:
`https://cdn.jsdelivr.net/gh/vasilegrafu/.claudefx@X.Y.Z/skills/docs-html/…`
(the `cdn` field in `version.json` is that template with `{version}`).

## How documents are composed

`builder.py` (a Jinja2 driver) composes three kinds of *template* — never viewed
directly — into a finished document:

```
SKILL.md
builder.py     ← Jinja compose: base + doc-type template + component macros → docs/<name>.html
css/
    docs-html.css    ← the single stylesheet (@layer + @import)
    modules/*.css    ← the modules it imports
js/
    docs-html.js     ← the single script: entry/loader (MODULES list)
    modules/*.js     ← the modules it loads (core, util, icons, features, main)
components/
    <name>/
        usage.md           guidance for the author: when + how, and the rules
        component.html.j2  a Jinja macro {% macro <name>(...) %} — the callable markup
    showcase.html.j2       source template for the gallery (edit this)
    showcase.html          generated gallery — run `python builder.py showcase`
doc-types/
    base.html.j2      the shared shell: head (the two links) + toolbar + <main> + {% block content %}
    <name>/
        usage.md          audience, depth, research, type rules
        document.html.j2  {% extends base %}; body is ONLY component-macro calls
```

**Jinja runs only at compose time.** `builder.py` renders a doc-type template to
a fully-rendered, standalone `docs/<name>.html` with **no `{% %}` left** — plain
hand-editable HTML. `jinja2` is a dependency of the builder only; viewing needs
nothing.

## Workspace layout (per project)

```
<project>/docs/
└── <name>.html    ← the document — hand-edited source AND what you ship, flat, no subfolders
```

`<name>.html` is the single source of truth. No index/portal, no init step — the
first `new` creates `docs/` if missing.

## View modes — the layout toggle

Every non-presentation document carries a small fixed toolbar top-right with two
glyph buttons, injected by `base.html.j2`:

- **▯ Page width** (default) — content sits in a centered 1024px column
  (the `<main>` wrapper carries the geometry; see Layout invariants below).
- **▭ Full width** — `docs-html.js` adds `class="wide"` to `<body>`; `base.css`
  drops the column cap so content fills the viewport.

The buttons carry only `data-w="page"|"wide"` — no inline handler.
`docs-html.js` attaches one click listener; which button looks active is decided
purely in CSS from the body class. The toolbar is excluded from the reading
column, hidden in print, and omitted from presentations.

## Document type catalog

Each type is a folder `doc-types/<name>/` holding a `usage.md` and a
`document.html.j2`. `doc-types/` is the authoritative list; this table is the
map. Run `python builder.py --list` for the live catalog.

| Stage | Types |
|---|---|
| Initiation | business-case, project-charter, feasibility-study, statement-of-work |
| Planning | project-management-plan, product-requirements-document, risk-register |
| Requirements | software-requirements-specification, use-case-specification, user-story-backlog, requirements-traceability-matrix |
| Design | architecture-decision-record, software-architecture, software-design-document, api-specification, database-design-document, user-interface-design-specification |
| Implementation | coding-standards, developer-setup-guide, technical-specification |
| Testing | test-plan, test-case-specification, test-summary-report, defect-report |
| Deployment | release-notes, deployment-runbook, rollback-plan, user-guide |
| Maintenance | incident-postmortem, change-request, operations-runbook, service-level-agreement |
| Communication | status-report, meeting-minutes, sprint-retrospective, presentation |
| Tools | diagram-editor (one Mermaid diagram, nothing else — a workspace for the built-in ✎ editor) |
| Fallback | generic-document |

## Commands

### `new <type> "<title>"` — create a document
Pick the type from the catalog (`doc-types/` is the live list). The builder
accepts only full type names — when the user says an abbreviation, translate it
yourself: ADR → architecture-decision-record, SRS →
software-requirements-specification, PRD → product-requirements-document, SOW →
statement-of-work, SDD → software-design-document, RTM →
requirements-traceability-matrix, API spec → api-specification, SLA →
service-level-agreement, postmortem → incident-postmortem, CR → change-request,
runbook → deployment-runbook or operations-runbook (ask which if ambiguous),
retro → sprint-retrospective, changelog → release-notes. If no dedicated type
fits, use `generic-document` and offer to promote it via `new type`.

1. Read `doc-types/<full-type-name>/usage.md` → audience, filename rule, depth
   policy, research guidance, type rules.
2. **Compose** the skeleton — run the builder (you or the user):
   `python builder.py new <type> "<title>"` → writes a standalone
   `docs/<slug>.html` (base shell + the type's sections + component fragments;
   the two asset links, author, and date all resolved). It won't overwrite an
   existing document without `--force`.
3. **Depth**: if the doc-type says `depth: full`, proceed. If `depth: ask`,
   state the research scope and cost first ("full means reading ~N files / a few
   minutes — or draft skeleton now?") and let the user choose:
   - `draft`: fill metadata + cheap recon only (folder listing, README, git
     log). Every substantive section gets a targeted
     `<mark class="todo">what belongs here + candidates spotted</mark>`.
   - `full`: research per the doc-type's guidance; write true content;
     todo-marks only where genuinely uncertain.
4. **Fill** the composed file: replace the `{{...}}` content placeholders;
   delete skeleton rows/sections that don't apply. Keep the TOC in sync with the
   final sections.
5. **Self-check**: no `style=` attributes, no `<style>` blocks, no `<script>`
   blocks and no inline event handlers (all behaviour comes from
   `docs-html.js`; the builder-generated `onerror` CDN fallback on the two
   head tags is the one exception), the two head links present and resolving, no leftover
   `{{...}}` placeholders, TOC entries match sections exactly, metadata complete.
   Fix before reporting done.

To grow a document later, copy the markup pattern from the component's `usage.md`
(or render it once via a scratch compose) — the composed file is plain HTML;
edits are hand edits.

Later section-by-section filling: "fill the X section" → research only what that
section needs, replace its todo-mark, report remaining todo count.

### `modify <doc> …`
Read the current file FIRST (manual edits are part of the truth — merge, never
regenerate). Targeted edits using only catalog components. Section changes update
the TOC in the same edit. Bump version, update date, append a change-history row
(add the table if missing). Renames: update every referring link in other
documents — never rename without the sweep.

### `update <doc>`
Re-read the code/state the document describes; propose refresh edits as targeted
changes; version bump + change-history row.

### `new type <name>`
Extend the skill: add `doc-types/<full-name>/usage.md` + `document.html.j2`.
The template is a Jinja file:
```jinja
{# type-name: Full Type Name #}
{% extends "doc-types/base.html.j2" %}
{% block content %}
  {{ c.toc([("id", "Heading"), ...]) }}
  {% call c.section("id", "Heading") %}
    {{ c.requirement(id="REQ-001", priority="must", label="Must") }}
  {% endcall %}
{% endblock %}
```
Its body is **only** component-macro calls — `{{ c.<name>(...) }}` for leaves,
`{% call c.<name>(...) %}…{% endcall %}` for containers. Every component is a
macro on the `c` namespace (no imports). Base shell, cover, and the two asset
links come from `base.html.j2` + the builder. If a needed component is missing,
add it as `components/<new>/{usage.md, component.html.j2}`.

### `release [major|minor|patch]` — publish a design-system version
This skill lives in `github.com/vasilegrafu/.claudefx` — a standalone public
repo, checked out ONCE as a shared clone (on this machine:
`D:\Dev.Work\.claudefx`) that solutions consume via junctions/symlinks into
their `.claude/skills/`; the same repo is ALSO the CDN origin (jsDelivr
serves its tags). There is no sync step: releasing IS
tagging this repo. The version lives ONLY in `version.json` + `version.md`
(skill root). When the user asks for a release:
1. Read `version.json`; bump per semver (`version.md` documents the contract:
   patch = visual fix, minor = additive, major = markup contract change —
   infer the level from what changed since the last entry if not stated).
2. Write the new `version.json` (version + ISO date, keep the `cdn` template)
   and prepend a `version.md` entry summarizing the changes.
3. In the `.claudefx` repo: commit all changes; `git tag vX.Y.Z`;
   `git push origin main --tags`. A published tag is IMMUTABLE — never move or
   re-tag; any fix is a new version. Verify with a HEAD request to
   `https://cdn.jsdelivr.net/gh/vasilegrafu/.claudefx@X.Y.Z/skills/docs-html/css/docs-html.css`.
4. Report the new version and the two CDN URLs.
Never bump the version as a side effect of other work — only on an explicit
release. Day-to-day skill commits to `main` are fine without a release; tags
pin what documents fall back to.

### PDF
Open the document and Ctrl+P → Save as PDF — `print.css` produces clean
paginated output (diagrams freeze to static, fully-visible images; the toolbar
and diagram tools are hidden); presentations print one page per sheet.

### `audit`
Grep/Read over the `*.html` documents in `docs/`:
- contract violations (see Authoring contract), leftover `{{...}}` placeholders;
- TOC entries match the document's sections exactly (ids and titles);
- the two head links present and resolving;
- metadata headers complete; internal links between documents resolve;
- unresolved `<mark class="todo">` counts per document;
- change-history vs git: file changed after last recorded row → offer to
  backfill;
- staleness vs code: docs describing code areas with many commits since the
  doc's last change.
Report findings; offer fixes.

## Authoring contract

**Layout invariants (alignment + spacing)**
1. All document content lives inside the single `<main>` wrapper (written by
   `base.html.j2`); `<main>` alone carries the column geometry (64rem cap,
   centering, 1.5rem gutters). Only the `.doc-toolbar` sits outside it.
2. Every component sits flush on the column's left edge. A component NEVER sets
   horizontal margins, horizontal offsets, or root-level horizontal padding that
   would shift it off that edge (internal padding inside cards/frames is fine).
3. A component's external spacing is exactly `margin: var(--block-gap) 0`
   (1rem, defined in base.css) — never more, never hard-coded. Heading margins
   (h2/h3/h4) are typography rhythm, not component spacing, and keep their own
   scale.

**Files**
1. A document is one `.html` file in `docs/` (flat) containing only semantic HTML
   composed from the components in `components/`.
2. No `style=` attributes, no `<style>` blocks, no `<script>` blocks, no inline
   event handlers. All behaviour (layout toggle, diagram render, pan/zoom) comes
   from the linked `docs-html.js`. The head links exactly the two skill assets
   (`css/docs-html.css`, `js/docs-html.js`) and nothing else. ONE sanctioned
   exception, generated by the builder and never authored: when a CDN is
   configured in `version.json`, the two head tags carry an `onerror` fallback
   attribute (local asset missing → load the version-pinned CDN copy).
3. The TOC is a static component maintained by hand: any edit that adds, renames,
   or removes a section updates the TOC in the same change.

**Naming (slug algorithm — deterministic)**
1. Lowercase the title; replace every run of non-alphanumerics with one hyphen;
   trim edge hyphens. No stopword removal, no abbreviations.
2. Filename = `<slug>.html`. Same title → same filename, always.
3. ADRs only: `architecture-decision-record-NNN-<slug>.html`, NNN = zero-padded
   next number (scan existing ADRs in `docs/`). The number is identity, not
   ordering.
4. Template and doc-type names are full words, never abbreviations.

**Metadata**
Every document starts with the metadata-header: doc-type kicker
(`<p class="doc-type">` — the document type in full words), title, author, ISO
date, and version. A document type may add fields it needs (Owner, Reviewers,
Release, Sponsor, Severity, etc.). The organization line is injected by
brand.css, never written into documents. Documents past v0.x carry a
change-history table; every modification appends a row.

**Code**
Documents hold code as **plain text** — never token `<span>`s, never
`language-*` classes. Declare the language with `data-lang` on the `<code>`
(the `c.code(lang=…)` / `c.code_block(lang=…, path=…)` macros set it);
`docs-html.js` colors it at view time (Prism from CDN, lazy — CDN down means
plain but readable code). The `language-*` ban applies to *authored markup*;
the runtime adds those classes internally. Use the framed form (`figure.code`
with title bar) for developer-facing documents; plain `<pre><code>` is always
valid. See `components/code-block/usage.md`.

**Content**
- Uncertain content is always `<mark class="todo">` — never silently invented,
  never an empty section.
- Diagrams are Mermaid text, editable — never exported images of diagrams.
- Requirements and traceable items carry trace-ids (`REQ-`, `RISK-`, `TC-`); a
  requirement is a `requirement` card, not a bullet.
- Formal documents (SRS, architecture, standards, test plans) carry ISO-style
  front/back matter per `components/front-back-matter/`: Purpose & Scope,
  Executive summary, then the body, then References, Glossary, Appendices. Short
  documents (status report, minutes) do not — never pad with empty scaffolding.
- An Approved ADR's Decision is immutable — supersede with a new ADR, linked both
  ways.
- Documents approaching ~60 KB split into a parent linking child documents.

**Writing style** (applies to all generated and modified content)
- Active voice, present tense: "the importer writes X", not "X will be written
  by the importer".
- One idea per sentence; short sentences over subordinate-clause chains.
- Define every acronym at first use: "Software Requirements Specification (SRS)".
- Numbers over adjectives: "3× slower under load", not "much slower"; cite real
  files, real values, real limits.
- Say who does what — name the component, never "the system" when a specific
  module is meant.
- No filler ("it should be noted that", "in order to"), no marketing adjectives.
  A sentence that adds no information is deleted.

## Maintenance rule
The gallery is generated: never hand-edit `components/showcase.html`. Every
catalog component has a demo, and every demo sits under a labeled divider
naming its component (the gallery-only `mark(...)` macro in showcase.html.j2,
styled by `css/modules/gallery.css` — documents never use it). After changing
anything in `css/` or any component, edit `components/showcase.html.j2`
(add a demo + its `mark` label when you add a component), then regenerate with
`python builder.py showcase` and open the result in a browser — **CSS and JS
changes hit ALL documents in ALL projects retroactively** (documents reference
the shared assets, not copies). When changing a component's markup, edit its
`component.html.j2` macro (the source the builder composes); the `usage.md` is
guidance only. `builder.py` needs `jinja2`; viewing does not.
