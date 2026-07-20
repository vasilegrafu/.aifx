---
name: docs-html
description: Generate, maintain, and audit professional documents as clean,
  manually-editable HTML. Domains built out - general business (charter,
  business case, risk register, minutes, status), software/SDLC (ADR, SRS,
  architecture, test plan, runbook), finance & investing (investment thesis,
  portfolio review, trade journal, IPS), accounting (budget, statements,
  invoice), research & economics (research report, data analysis, white
  paper), and engineering (calc note, specification, inspection). Use when
  the user asks to create, modify, update, or audit any such document.
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

## Documentation map

Five kinds of doc file, each with one job — read the next level only when you
need it:

| file | for | answers |
|---|---|---|
| `README.md` | users / evaluators | what this is, why use it, how to start |
| `SKILL.md` (this file) | the agent | what to do, and the rules |
| `CATALOG.md` (generated) | authoring | every component call form + doc-type purpose |
| `<item>/usage.md` | authoring | how &amp; when to use one component / doc-type |
| `<subsystem>/REFERENCE.md` | maintaining | how css / js / components / doc-types work, and how to extend them |

Reading path: `README` → `SKILL` → `CATALOG` → `usage.md` (to author a document)
or `REFERENCE.md` (to extend the system).

## The two assets

**`css/docs-html.css`** — the single stylesheet. It sets the cascade order once
with `@layer`, then `@import`s the modules in `css/modules/`. A document links
only this file.

`@layer` makes the cascade order explicit and independent of import order, so
modules can be added or reordered without specificity surprises; a document
links the whole stylesheet (no tree-shaking — one cached file beats a
per-document set). **The CSS architecture — the `@layer` order, the full module
map, page-local CSS, and rebranding — is in `css/REFERENCE.md`.**

**`js/docs-html.js`** — the single script a document links; like the CSS entry,
it only loads the real code from `js/modules/` (classic `<script>` injection in
list order — ES modules are blocked on `file://`). The modules form a tree on
the one `docsHtml` namespace: `core` (registry) · `util` · `icons` ·
`layout-toggle` · `highlight` (Prism) · `math` (KaTeX) · `diagrams` (Mermaid +
Panzoom) · `chart` (ECharts) · `main`. **Module roles, the feature-author guide,
and the diagrams engine/editor internals are in `js/REFERENCE.md`.**

**Extending**: new behaviour = new `js/modules/<name>.js` that calls
`docsHtml.register(...)` + its name in the `MODULES` list in `docs-html.js`.
`core.js`/`main.js`/other features stay untouched — `js/REFERENCE.md` is the
feature-author guide (contract, skeleton, rules) and the full JS internals. Features read per-document
options from `data-` attributes on their own markup via
`docsHtml.data(el, "option-name", fallback)` (e.g.
`<pre class="mermaid" data-max-scale="10">` raises that diagram's zoom cap) —
there is **no per-document JavaScript**, ever; every behaviour keys off markup
the author already writes:

- `.doc-toolbar [data-w]` → the page / full-width **layout toggle** (adds/removes
  `class="wide"` on `<body>`; which button looks active is decided in CSS).
- `pre.mermaid` → a **diagram**: rendered, then made **pan/zoomable**.
- `pre.chart` → a **data chart**: a JSON ECharts `option` rendered to SVG with
  the built-in validated `docs-html` palette (bar/line/pie/scatter/candlestick…).

It loads the heavy engines from CDN **only when a document actually contains a
diagram or chart** — a plain document fetches nothing extra. Mermaid renders each
diagram at natural size in a bounded pan/zoom viewport with an icon toolbar
(fit · fullscreen · ✎ source editor · download SVG · copy source); ECharts renders
each chart as SVG. If the CDN is unreachable the Mermaid/chart **source stays
visible as a readable code box** — nothing breaks. **Engine pins, the toolbar,
the ✎-editor, and the chart theme/palette are in `js/REFERENCE.md` (charts) and
`css/REFERENCE.md`.**

**Where the two hrefs point — documents are CDN-ONLY.** `builder.py` bakes
the version-pinned CDN URLs into every composed document's head:
`https://cdn.jsdelivr.net/gh/vasilegrafu/.aifx@X.Y.Z/skills/docs-html/…`
(the version read from `version.json` at compose time — a document is forever
pinned to the design system it was authored against, and works anywhere on
the internet with zero local setup). Local paths never appear in any generated
file — the skill's own showcases (`showcases/*.html`) link the same
version-pinned CDN as documents, so every output is shareable as-is. `cdn` is
the only asset path the builder emits; a missing `cdn` in `version.json` is a
hard error, not a silent local fallback.

**Versioning.** The design-system version lives in exactly two files at the
skill root and NOWHERE else (not in the CSS, not in the JS): `version.json`
(machine-readable source of truth: `version`, `date`, `cdn` base URL) and
`version.md` (the human changelog, one entry per release, semver contract
documented at its top). On a CDN the version is carried by the URL path
(`…/docs-html@X.Y.Z/css/docs-html.css`) — relative `@import`s and the JS
loader's self-resolved base pin the whole asset tree to one version
automatically. See the `release` command below.

**Developing against a document.** Every generated file — documents and the
showcase alike — pins the CDN version from `version.json`, so previewing local
CSS/JS edits means bumping `cdn` to the version you're about to release (or
serving the working tree yourself). A document picks up improvements by a
deliberate head edit to a newer `@X.Y.Z` — never silently. The `cdn` field in
`version.json` is the URL template with `{version}`.

## How documents are composed

`builder.py` (a Jinja2 driver) composes three kinds of *template* — never viewed
directly — into a finished document:

```
SKILL.md
CATALOG.md     ← generated quick-reference (component call forms + doc-type purposes); `builder.py catalog`
builder.py     ← Jinja compose: base + doc-type template + component macros → docs/<name>.html
css/
    docs-html.css    ← the single stylesheet (@layer + @import)
    modules/*.css    ← the modules it imports
    REFERENCE.md     ← CSS architecture: @layer order, module map, page-local CSS, rebranding
js/
    docs-html.js     ← the single script: entry/loader (MODULES list)
    modules/*.js     ← the modules it loads (core, util, icons, features, main)
    REFERENCE.md     ← JS internals: module roles, feature-author guide, diagrams engine/editor
components/
    REFERENCE.md      ← the component model (how components are organized + called)
    <category>/       structure | lists | content | callouts | blocks |
                      front-back-matter | business | diagrams | math
        usage.md           category orientation: blurb + when to use
        <name>/
            usage.md           guidance for the author: when + how, and the rules
            component.html.j2  a Jinja macro {% macro <name>(...) %} — the callable markup
showcases/
    <name>.html.j2    source template for a showcase (edit this)
    <name>.html       generated showcase — run `python builder.py showcase`
                      (components.html.j2 = the category-driven component gallery)
doc-types/
    REFERENCE.md      ← curated type taxonomy (groupings, † markers, abbreviations)
    base.html.j2      the shared shell: head (the two links + {% block head %}) + toolbar + <main> + {% block content %}
    <domain>/         general | software | finance | investing | accounting |
                      research | economics | engineering | tools | fallback
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

## CATALOG.md — read this first

`CATALOG.md` (skill root) is the generated quick-reference: every component's
exact call form (`{{ c.x(...) }}` for leaves, `{% call c.x(...) %}…{% endcall %}`
for containers) and every doc-type's one-line purpose, grouped by category /
domain, each group introduced by its blurb. **Read it once before authoring
instead of opening component and doc-type files** — it is built from the
templates themselves (macro signatures + the `{# purpose: … #}` headers +
category/domain blurbs), so it can never drift. Regenerate with
`python builder.py catalog` after adding or changing any component or doc-type.

**For one item, don't read files — ask the builder:**
`python builder.py show <name>` prints, for a component, its call form +
purpose + full `usage.md`; for a doc-type, its domain, type-name, purpose, the
components it uses, and its `usage.md`. One command instead of several reads.

**Category / domain orientation.** Each `components/<category>/usage.md` and
`doc-types/<domain>/usage.md` opens with a one-line **blurb** (the first
content paragraph) then a `**Use when**` line — the fast way to pick the right
category. That blurb is the SINGLE SOURCE: the builder reads it into both
`CATALOG.md` (the group intro) and the showcase category bands, so the copy is
written once. Keep the blurb as the first non-heading line.

## Document type catalog

Each type is a folder `doc-types/<domain>/<name>/` holding a `usage.md` and a
`document.html.j2`. The type's identity is its own folder name (unique across
all domains) — commands take the type name alone, never the domain.

The ten domains: **general** (any field), **software** (SDLC), **finance**,
**investing**, **accounting**, **research**, **economics**, **engineering**,
**tools**, **fallback**. For the live list read `CATALOG.md` (names + purposes)
or run `python builder.py --list`. For the curated taxonomy — types grouped by
SDLC stage / theme, the † universal-pattern markers, and the abbreviation map —
see `doc-types/REFERENCE.md`.

## Commands

### `new <type> "<title>"` — create a document
Pick the type from the catalog (`CATALOG.md`, or `python builder.py --list`).
The builder accepts only full type names — when the user gives an abbreviation
(ADR, SRS, PRD, SOW, RTM, SLA, retro, changelog…), translate it to the full name
first; the abbreviation map is in `doc-types/REFERENCE.md`. If no dedicated type
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
   `docs-html.js`), the two version-pinned CDN head links present, no leftover
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
Extend the skill: add `doc-types/<domain>/<full-name>/usage.md` +
`document.html.j2` (pick the domain folder from the catalog; a genuinely new
domain gets a new folder — the builder discovers recursively).
The template is a Jinja file:
```jinja
{# type-name: Full Type Name #}
{# purpose: one line — what this document is for (feeds CATALOG.md) #}
{% extends "doc-types/base.html.j2" %}
{% block content %}
  {{ c.toc([("id", "Heading"), ...]) }}
  {% call c.section("id", "Heading") %}
    {{ c.requirement(id="REQ-001", priority="must", label="Must") }}
  {% endcall %}
{% endblock %}
```
The `{# purpose: … #}` line is required — `python builder.py catalog` reads it
into CATALOG.md. Its body is **only** component-macro calls —
`{{ c.<name>(...) }}` for leaves, `{% call c.<name>(...) %}…{% endcall %}` for
containers. Every component is a macro on the `c` namespace (no imports). Base
shell, cover, and the two asset links come from `base.html.j2` + the builder.
If a needed component is missing, add it as
`components/<category>/<new>/{usage.md, component.html.j2}` (pick the category
folder; the builder discovers recursively) — the macro file's FIRST line is
`{# purpose: … #}`. After adding either, run `python builder.py catalog` to
regenerate CATALOG.md.

### `release [major|minor|patch]` — publish a design-system version
This skill lives in `github.com/vasilegrafu/.aifx` — a standalone public
repo, checked out ONCE as a shared clone that solutions consume via
junctions/symlinks into their `.claude/skills/`; the same repo is ALSO the CDN
origin (jsDelivr serves its tags). There is no sync step: releasing IS tagging
this repo. The version lives ONLY in `version.json` + `version.md` (skill root).
When the user asks for a release:
1. Read `version.json`; bump per semver (`version.md` documents the contract:
   patch = visual fix, minor = additive, major = markup contract change —
   infer the level from what changed since the last entry if not stated).
2. Write the new `version.json` (version + ISO date, keep the `cdn` template)
   and prepend a `version.md` entry summarizing the changes.
3. In the `.aifx` repo: commit all changes; `git tag vX.Y.Z`;
   `git push origin main --tags`. A published tag is IMMUTABLE — never move or
   re-tag; any fix is a new version. Verify with a HEAD request to
   `https://cdn.jsdelivr.net/gh/vasilegrafu/.aifx@X.Y.Z/skills/docs-html/css/docs-html.css`.
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
   from the linked `docs-html.js`. The head links exactly the two
   version-pinned CDN assets (`…@X.Y.Z/skills/docs-html/css/docs-html.css`
   and `…/js/docs-html.js`) and nothing else.
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
valid. See `components/content/code-block/usage.md`.

**Content**
- Uncertain content is always `<mark class="todo">` — never silently invented,
  never an empty section.
- Diagrams are Mermaid text, editable — never exported images of diagrams.
- Formulas are LaTeX text in `.math` elements (`c.formula()` block /
  hand-written `<span class="math">` inline), rendered at view time — never
  images of equations.
- Charts are data, not pictures: a JSON ECharts `option` in `c.chart_echarts()`
  (`pre.chart`), rendered to SVG at view time — never a screenshot of a chart.
  Never restyle the theme per chart (the palette is validated); one y-axis only.
  Prefer it over a Mermaid `xychart-beta` whenever the chart carries analysis.
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

## Page-specific CSS

Shared `css/modules/` are for styles used across MANY documents; CSS that styles
ONE page lives in that page, in a `{% block head %}` `<style>` (the base shell
exposes `{% block head %}` just before `</head>`, after the design-system link,
so the page reads the same tokens). Worked example + mechanics:
`css/REFERENCE.md`.

## Showcases &amp; the maintenance rule
Showcases are the skill's own generated reference pages: `showcases/<name>.html.j2`
→ `showcases/<name>.html`. `components.html` is the **category-driven component
gallery** — structured by the nine `components/<category>/` folders. Add more
showcases by dropping another `<name>.html.j2` in `showcases/`. Never hand-edit
a generated `showcases/*.html`.

Two gallery-only macros in `components.html.j2` (documents never use them):
`cat(dir, kicker, name)` opens each category with a separator band — the folder
name in parentheses after the title, and the blurb pulled from
`components/<dir>/usage.md`; `spec(title, name)` heads each component's demo,
pairing a human title with its macro/folder name. Every catalog component has a
demo under a `spec` header. After changing anything in `css/` or any component,
edit `showcases/components.html.j2` (add a `spec` + demo in the right category
when you add a component), then regenerate with `python builder.py showcase`
and open the result in a browser
— **CSS and JS changes hit ALL documents in ALL projects retroactively**
(documents reference the shared assets, not copies). When changing a
component's markup, edit its `component.html.j2` macro (the source the builder
composes); the `usage.md` is guidance only. `builder.py` needs `jinja2`;
viewing does not.
