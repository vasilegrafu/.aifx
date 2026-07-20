# docs-html

**Professional documents as clean, hand-editable HTML.** One design system, no
proprietary format, no build step — the file you compose is the file you ship,
and it opens in any browser, on any machine.

docs-html turns a document type and a title into a finished, standalone HTML
page that wires up the whole design system with two lines. Ask Claude for it in
a sentence, or run one command yourself. Then edit it like any HTML — it's
yours, and it will read the same next year as it does today.

- **Standalone HTML, zero lock-in** — no Word, no LaTeX, no export step. Open
  it, edit it, send it, print it.
- **One system, consistent everywhere** — 84 document types and 45 components
  that already look right together; restyle every document by editing one file.
- **Renders what real documents need** — interactive diagrams, proper math,
  syntax-highlighted code, tables, KPIs, timelines, callouts.
- **Two-line include** — a document links one stylesheet and one script from a
  version-pinned CDN, so it stays portable and pinned to the exact look it was
  authored against.
- **Prints to PDF** — Ctrl+P, done. Pagination is handled.

## What you can do with it

Compose any of **84 document types** across **10 domains**, each built from
**45 reusable components**:

| Domain | A few of the types |
|---|---|
| **general** | business case · proposal · decision record · status report · SOP · roadmap |
| **software** | requirements spec · architecture · ADR · test plan · runbook · release notes |
| **finance** | budget · cash-flow forecast · valuation report · net-worth statement |
| **investing** | investment thesis · due diligence · backtest · portfolio review · watchlist |
| **accounting** | invoice · credit note · expense report · financial statements |
| **research** | research report · literature review · data-analysis report · white paper |
| **economics** | economic analysis · industry analysis · policy brief |
| **engineering** | equipment spec · inspection report · maintenance plan · risk assessment |
| **tools · fallback** | diagram editor · generic document |

The components are the building blocks — requirement cards, KPI tiles,
timelines, risk matrices, financial tables, SWOT grids, callouts, interactive
Mermaid diagrams, KaTeX formulas, and more. See every one rendered live in the
gallery (below), or read `CATALOG.md` for the full list with a one-line purpose
for each.

## How to use it

### The easy way — ask Claude

docs-html is a Claude skill. Describe the document you want and Claude does the
rest — it picks the right type, composes it, and fills in real content:

> “Create a software requirements specification for the payments service.”
>
> “Draft an investment thesis for ACME with a bull / base / bear scenario table.”

Behind the scenes Claude reads the generated `CATALOG.md` and runs
`python builder.py show <name>` to see exactly how each component is called, so
it composes quickly and hands you a finished document you can open and tweak.
You never have to learn the internals.

### The direct way — one command

Prefer to drive it yourself? Three steps, no server and no build:

```bash
python builder.py new invoice "ACME Invoice 0042"   # -> docs/acme-invoice-0042.html
# fill in the placeholders
# open the file in a browser — that's it
```

Browse the catalog any time with `python builder.py --list`.

**Requirements.** Authoring needs **Python 3 + Jinja2** (`pip install jinja2`) —
the only dependency, and it runs once at compose time. *Viewing* a document
needs nothing but a browser.

## See it in action

The gallery renders every component through its real code, grouped by category,
with each demo sitting next to the exact call you would write:

```bash
python builder.py showcase     # regenerate the gallery
# then open showcases/components.html
```

It is the fastest way to see what is available and what it looks like — and
because it is generated from the same components your documents use, it can
never fall out of date.

## Sharing documents

A composed document is **self-contained and portable**. Its two asset links
point at a **version-pinned CDN** (jsDelivr), which means:

- hand someone the `.html` file and it renders correctly on their machine — no
  setup, no attachments, no shared folder to keep in sync;
- it is pinned to the exact design-system version it was authored against, so
  it looks the same for them as it did for you;
- need a fixed page for print or email? Open it and **Ctrl+P → Save as PDF**.

There is no publish or export step. The document you compose *is* the artifact.

## Extending it

It is just Jinja and CSS — growing it is easy:

- **New component** — add `components/<category>/<name>/component.html.j2`
  (a Jinja macro) plus a short `usage.md`, style it in a `css/modules/` file,
  and add a demo to the gallery.
- **New document type** — add `doc-types/<domain>/<name>/document.html.j2`
  (a body of component calls) plus a `usage.md`.
- **Rebrand everything** — edit `css/modules/brand.css` (name + accent colour);
  it cascades to every document.

Then refresh the reference with `python builder.py catalog` and the gallery
with `python builder.py showcase`. See `SKILL.md` for the full authoring
contract.

## Versioning

The design-system version lives in exactly two files — `version.json`
(machine-readable) and `version.md` (the changelog and semver contract). On the
CDN the version is carried in the URL, and **published versions are
immutable**: a document pinned to `@X.Y.Z` never changes underneath you.
Upgrading a document to a newer look is a deliberate one-line edit, never a
surprise.

## How it's organized

```
docs-html/
├── SKILL.md            the authoring contract + full catalog
├── CATALOG.md          generated quick-reference: every component + doc-type
├── builder.py          composes documents  (new · --list · catalog · show · showcase)
├── version.json        the design-system version   (+ version.md changelog)
├── css/
│   ├── docs-html.css   the single stylesheet every document links
│   └── modules/*.css   the modules it imports
├── js/
│   ├── docs-html.js    the single script every document links
│   └── modules/*.js    features: syntax highlighting, math, diagrams, layout
├── components/
│   └── <category>/     45 building blocks, grouped by category
├── doc-types/
│   └── <domain>/       84 document types, grouped by domain
└── showcases/
    └── components.html  the live component gallery
```

Every document references exactly one stylesheet and one script back to this
system, so a change made here updates every document that points at that
version — no copies to chase.

## License

MIT — use it, copy it, ship it.
