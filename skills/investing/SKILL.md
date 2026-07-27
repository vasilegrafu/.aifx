---
name: investing
description: Generate data-driven investing reports as standalone HTML, built
  from live market and fundamentals data rather than hand-filled templates. A
  report is a program - a controller fetches and asserts, a view chooses which
  of 109 components appear - and the output is regenerated, never edited. Use
  when the user asks to build, extend, or audit a company or portfolio report,
  add a report type, or work on the component library behind them.
---

# investing — reports as programs, not documents

Every report here is **generated end to end**. A controller fetches live data
and does the arithmetic; a view says which components appear and in what order;
the output is a standalone HTML file with no placeholders to fill and nothing
to edit by hand. Regenerate it and you get the same file with newer numbers.

That is the whole difference from `docs-html`, the sibling skill. There a
doc-type is a **skeleton a human fills** — component calls carrying literal
placeholder text, edited after generation. Here a report is a **program**: the
same component calls carry `d.*`, and editing the output would be editing a
build artifact.

## Documentation map

| where | what |
|---|---|
| **this file** | the shape, the contracts, how to add things |
| `css/REFERENCE.md` | the stylesheet: `@layer` order, module map, theming |
| `js/REFERENCE.md` | the runtime: modules, chart frame, the failure states |
| `data_providers/fmp/endpoints.md` | which FMP endpoints exist, and which the plan allows |
| `components/<cat>/<name>/usage.md` | one per component: when to use it, and the rules |

## CLI

```bash
python builder.py build <report> <args...> --out DIR
python builder.py showcase [<component>]
```

`builder.py` **dispatches and nothing else**. Each directory owns the code that
builds what lives in it, and each runs on its own:

```bash
python reports/report_builder.py financial-profile INTC --peers AMD,NVDA --out DIR
python components/showcase_builder.py bar
```

`--out` is required and has no default: the head's local asset href is computed
relative to it, so a report composed without naming its destination would link
assets relative to a directory nobody chose.

Names resolve by prefix or by macro name — `build financial` reaches
`financial-profile`, `showcase bar_negative` reaches `bar-negative`.

## The shape — both sides are the same three files

```
                shell                    controller              view
reports/        report.master.html.j2    report_controller.py    report.html.j2
components/     showcase.master.html.j2  showcase_controller.py  showcase.html.j2
```

**Python files use underscores so they can be imported; templates keep the
dots.**

### A controller builds data. A view emits markup.

The controller returns a plain dict; it reaches the view as `d`; **the view is
the only thing that calls a macro.** Three rules follow, and breaking any one
makes the other two stop being replaceable:

- the controller never emits markup
- the view never fetches
- a component never knows which report called it

### Which way the arrow points

`components/` owns the macros, the number filters they use, and the Jinja
environment that exposes them as `c`. `reports/` **borrows** that environment —
so a macro that draws on a showcase page draws identically in a report, because
it is the same env, not two configurations that happen to match.

**Reports depend on components, never the reverse.** That is why `components/`
builds its own showcases without knowing reports exist.

### Discovery is by presence, never by registration

A directory containing `component.html.j2` **is** a component. A directory
containing `report.html.j2` **is** a report. Nothing is listed in a registry,
so adding either means adding files and nothing else. Controllers are
path-loaded for the same reason — an `import` line somewhere would be a
registry by another name.

## Layout

```
builder.py                     dispatch only
version.json  (repo root)      the CDN pin every generated page carries

components/                    SELF-CONTAINED: macros, filters, env, showcases
  showcase_builder.py          the engine — discovery, env, compose, write
  filters.py                   the one place a number becomes a string
  showcase.master.html.j2      the shell every showcase view extends
  charts/            21        engine-backed charts (Apache ECharts)
  domain-specific/   45        investing- and business-namespaced
  foundational/      41        any document may use these
  diagrams/  math/    2        the two other rendering subsystems

reports/
  report_builder.py            the engine — discovery, controller, compose, write
  report.master.html.j2        the shell every report view extends
  financial-profile/           one report

css/  css.loader.html.j2       the <link>   + its CDN fallback
js/   js.loader.html.j2        the <script> + its CDN fallback
data_providers/fmp/            the client — the ONLY thing doing I/O
```

## Assets — local first, CDN second

Every generated page links the bundle **twice over**: the local copy, relative
to wherever the file was written, and the version-pinned CDN as an `onerror`
fallback. Local first, so a page previews the current tree the moment it is
generated. CDN second, so the same file still renders once it leaves the tree —
copied elsewhere, emailed, opened from a download folder.

The two halves fail differently, which is why they are two files. A `<link>`
retargets its own `href`. A `<script>` **cannot** — once it has failed the
browser will not re-fetch on a new `src`, so the handler appends a fresh
element. Getting that wrong looks like it works; the page simply has no
JavaScript.

**Editing a bundle means bumping `version.json`.** Until you do, anything
falling back to the CDN serves the previous behaviour from the pinned tag.

## What guards the output

There is **no offline check**. Building a report requires the network and an
API key, so `shape()`'s assertions and `StrictUndefined` fire during a real
build and nowhere else.

**`StrictUndefined` is the point.** A view reading a key its controller never
produced would, by default, render an empty string — a tidy blank cell in an
otherwise perfect table, which nobody notices. It raises at build time instead,
and since Jinja runs only at build time the failure costs nothing and reaches
no reader.

**Assertions live in the controller** because that is the only place with the
arithmetic. `financial-profile` carries 14: cost + gross == revenue,
liabilities + equity == assets, each sankey summing to its own table, the
segment bridge reaching its endpoint. They exist because **a diagram that does
not conserve draws perfectly and lies** — a sankey scales each node's ribbons
independently, so an unbalanced one is a confident, wrong picture that no
template and no reader can catch.

`showcase` is the only command that renders anything without a key, and it
covers components, not reports.

## Credentials

This repository is **public**, and jsDelivr's `/gh/` path publishes it — a key
committed anywhere under this directory is fetchable at a URL by anyone who
guesses the path.

```
1. FMP_API_KEY                  environment variable — preferred
2. credentials.local.json       beside data_providers/fmp/, gitignored
3. hard error naming both
```

There is deliberately no third place it looks. Read a key **into the
environment** rather than copying it into a file that might be committed.

## Adding a report

1. `reports/<name>/report_controller.py` — `fetch(**args)`, `shape(payloads) -> dict`,
   optionally `add_args(parser)` for CLI arguments. Declare the endpoints in one
   table at the top; assert every identity in `shape()`.
2. `reports/<name>/report.html.j2` — `{% extends "reports/report.master.html.j2" %}`,
   fill `{% block content %}` with `c.<macro>(...)` calls carrying `d.*`. Add a
   `{# report-name: … #}` header; it becomes the title a reader sees.
3. `python builder.py build <name> … --out DIR`

## Adding a component showcase

1. `components/<cat>/<name>/showcase_controller.py` — one function,
   `context() -> dict`, built line by line. No markup, no macro calls.
2. `components/<cat>/<name>/showcase.html.j2` —
   `{% extends "showcase.master.html.j2" %}`, one `<section>` per state worth
   seeing: the default, and the ones where the component has to make a decision
   (a legend appears past one series, an axis name widens the margin).
3. `python builder.py showcase <name>`

A component with one half and not the other is reported as **half-written**
rather than skipped, so it does not stay that way. `showcase.html` is a build
artifact — the controller and the view are the source.

## House rules for components

- **No `style=` and no `<style>` in generated documents.** Geometry comes from
  `data-` attributes read by typed `attr()`, with `js/modules/attr-fallback.js`
  covering engines that do not support it yet.
- **No component sets its own colour.** Every colour in the system is a custom
  property in `css/foundational/theme.css`; charts read the chart tokens once at
  load. `--accent` is the rebranding knob.
- **No animations.**
- Domain CSS classes carry their domain's prefix — `investing-`, `business-`. A
  class that resists the prefix is telling you it is foundational.
- A chart never sets its own title; captions and units go through the shared
  chart frame so every exhibit is labelled the same way.
