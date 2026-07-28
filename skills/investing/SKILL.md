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
| `components/CATALOG.md` | **all 109 by what they are for** — start here to choose one, generated |
| `components/REFERENCE.md` | the library and its showcase engine: `env()`, the `c` namespace, filters, path-loading |
| `reports/CATALOG.md` | **every report by what it argues** — start here to choose one, generated |
| `reports/REFERENCE.md` | the report engine: the four stages, the controller contract, where the guarantees come from |
| `css/REFERENCE.md` | the stylesheet: `@layer` order, module map, theming |
| `js/REFERENCE.md` | the runtime: modules, chart frame, the failure states |
| `data_providers/REFERENCE.md` | the only code doing I/O: the client, credentials, why it raises and never caches |
| `data_providers/fmp/endpoints.md` | which FMP endpoints exist, and which the plan allows |
| `components/<cat>/<name>/usage.md` | one per component: when to use it, and the rules |
| `reports/<name>/usage.md` | one per report: what it argues, what it fetches, what it guarantees |

**Every directory that owns an engine owns a `REFERENCE.md`**, so it can be
read on its own — the documentation form of the rule the code already follows.
This file holds the contracts and how the two sides relate; each `REFERENCE.md`
holds the internals of one. Where they overlap, they overlap on purpose:
`components/` and `reports/` load controllers by the same mechanism, and each
states it in its own terms rather than pointing at the other.

**Read the `usage.md` before building or changing the thing it describes.** For
a report that means before running it — it is the only place that says what the
arguments mean editorially (a peer group is chosen, not screened), what the
build costs (~13 calls, no cache), and which of its numbers are asserted rather
than merely computed. None of that is inferable from the controller quickly
enough to be worth re-deriving each time.

## CLI

```bash
python reports/report_builder.py financial-profile INTC --peers AMD,NVDA --out DIR
python components/showcase_builder.py charts/bar
```

There is **no top-level dispatcher**. Each directory owns the engine that
builds what lives in it, and neither knows the other exists as a command.

A showcase is addressed by its **directory path**, a report by its **name** —
the same idea at two depths, since components nest two to four levels and
reports are flat. Neither is a registry lookup: the address IS where the
controller, the view and the output live. Every path derives from `__file__`,
so both commands work from any working directory.

`--out` is required and has no default. The page's local asset href is computed
relative to it, so a report built without naming its destination would link its
CSS and JS relative to a directory nobody chose. A showcase needs no such flag:
it lands beside the component it shows.

### ASK where the report goes. Never choose for the reader.

**If you have not been told the output directory, stop and ask for it.** Do not
invent one, do not default to the current directory, and do not reuse a path
from an earlier build. A report is a deliverable someone asked for; where it
lands is their decision, not a detail to be filled in.

The flag has no default for exactly this reason — the CLI cannot guess, so
neither should whoever is driving it. Two things follow from getting it wrong,
and neither announces itself:

- **The file is somewhere nobody looks.** It is not an error; it is a report
  that quietly does not exist where it was wanted.
- **The asset href is computed from that directory**, so a report written to
  the wrong place links its CSS and JS along a relative path that may not
  resolve — and it still renders from the CDN fallback, looking almost right.

Ask once, plainly: *"Where should the report be written?"* One question costs a
sentence; a report in the wrong place costs ~13 API calls and a file the reader
has to be told to delete.

The same applies to every other argument, and the CLI is built to force the
question rather than let it pass. **No argument has a default.** `--peers` is
required, because naming peers the reader did not ask for puts companies into a
comparison on your authority — and *not* naming any is equally a judgement, so
it must be said out loud as `--peers none` rather than happening by silence.

That is the rule the whole CLI follows: **an editorial decision must never be
the shape of an unset flag.**

Each engine prints the arguments its own reports declare:

```bash
python reports/report_builder.py financial-profile --help   # symbol, --peers
```

## The shape — both sides are the same three files

```
                shell                     controller              view
reports/        _report.master.html.j2    report_controller.py    report.html.j2
components/     _showcase.master.html.j2  showcase_controller.py  showcase.html.j2
```

**Python files use underscores so they can be imported; templates keep the
dots.** A **leading underscore** marks the library half of `components/` —
`_showcase_controller.py`, `_showcase.master.html.j2`, `charts/_render.html.j2`
— the files that serve components without being one. It also disambiguates:
`_showcase_controller.py` is the base class, `showcase_controller.py` is a
component's own.

### A controller builds data. A view emits markup.

The controller returns a plain dict; it reaches the view as `d`; **the view is
the only thing that calls a macro.** Three rules follow, and breaking any one
makes the other two stop being replaceable:

- the controller never emits markup
- the view never fetches
- a component never knows which report called it

### Both controllers are classes, and the same class

```python
class ChartBarShowcaseController(ShowcaseController):
    def _build_context(self) -> dict: ...            # required
    def _validate_context(self, d) -> None: ...      # optional

class FinancialProfileReportController(ReportController):
    TITLE = "Financial Profile"
    def _add_args(self, parser) -> None: ...         # optional
    def _fetch(self, **args) -> dict: ...            # required — the ONLY I/O
    def _build_context(self, payloads) -> dict: ...  # required — pure
    def _validate_context(self, d) -> None: ...      # optional
    def _filename(self, d) -> str: ...               # optional
```

`build()` does the rest on both sides, and a subclass is **told nothing** — the
base reads the directory off the subclass's own `_build_context` code object,
and the name off that directory.

**Everything the report side has extra follows from one sentence:** a
showcase's inputs are literal and its destination is implied; a report's inputs
are fetched and its destination is chosen. Fetched inputs give you `_fetch` and
`_add_args` (what to fetch); a chosen destination gives you `out_dir`,
`_filename` and `TITLE`. Nothing else differs.

Both outputs are **build artifacts** and both are overwritten without asking.
The controller and the view are the source; a report regenerated from the same
symbol is the same report with newer numbers.

`_fetch` and `_build_context` never touch each other. One place does I/O; the
derivation is a pure `payloads -> dict`, which is what lets its 13 identity
assertions be read on their own with no request in the middle.

### Which way the arrow points

`components/_showcase_controller.py` owns everything a page needs to render:
the macros' Jinja environment, the `c` namespace that exposes them, the number
filters they format with, and the asset pair every page links. `reports/`
**borrows** them — `env()` is module-level and `@cache`d, because it belongs to
the library rather than to whoever is rendering. So a macro that draws on a
showcase page draws identically in a report: it is the same env, not two
configurations that happen to match.

Building that env parses all 109 component templates. Cached once it costs
~0.5s on the first call and nothing after; built per controller it would cost
that 109 times.

**Reports depend on components, never the reverse.** That is why `components/`
builds its own showcases without knowing reports exist — and it now imports
**nothing** from outside itself, not even `sys.path` manipulation.

### Nothing is registered — components, reports and showcases are all found

A directory containing `component.html.j2` **is** a component. A directory
containing `report.html.j2` **is** a report. A component directory that also
holds `showcase_controller.py` and `showcase.html.j2` **has** a showcase.
Nothing is listed anywhere, so adding any of the three means adding files and
nothing else.

`ShowcaseBuilder.build("charts/bar")` therefore does no lookup: check the three
files are present, path-load the controller, find the `ShowcaseController`
subclass in it, call `build()`. It **raises** rather than returning a code,
because a showcase asked for by name and not built is a mistake worth stopping
for.

**It finds the class rather than deriving its name.** `charts/bar` holding
`ChartBarShowcaseController` is a convention worth keeping, but computing one
from the other would make the convention load-bearing — and a category that
pluralizes (`charts` → `Chart`) already shows how that goes wrong. A subclass
of `ShowcaseController` in the module is unambiguous.

**Path-loading is what removed the old hyphen constraint.** An `import`
statement cannot name a folder with a hyphen, which once disqualified 72 of the
109 components — `domain-specific/fundamental-analysis/*` is blocked twice
before you reach the component at all. Loading by path has no such rule, so
every component is reachable by the same one notation.

Two things the loader must get right, both verified:

- the module is registered in `sys.modules` before it executes. Plain
  `importlib` path-loading skips this, and then a class cannot be resolved back
  to its file.
- the base is imported **package-qualified** — `from components._showcase_controller
  import …` — by the builder and by every leaf. Reached under two names it
  would be two module objects: `issubclass` would fail against the wrong one,
  and each copy would build its own env.

## Layout

```
version.json  (repo root)      the CDN pin every generated page carries

components/                    the library: macros, filters, env, assets, showcases
  _showcase_controller.py      ShowcaseController + env() + FILTERS + the asset pair
  _showcase.master.html.j2     the shell every showcase view extends
  showcase_builder.py          ShowcaseBuilder.build(path) + the CLI
  charts/            21        engine-backed charts (Apache ECharts)
  domain-specific/   45        investing- and business-namespaced
  foundational/      41        any document may use these
  diagrams/  math/    2        the two other rendering subsystems

reports/
  _report_controller.py        ReportController + its own copy of the asset pair
  _report.master.html.j2       the shell every report view extends
  report_builder.py            ReportBuilder.build(name, argv, out) + the CLI
  financial-profile/           one report

css/  css.loader.html.j2       the <link>   + its CDN fallback
js/   js.loader.html.j2        the <script> + its CDN fallback
data_providers/fmp/            the client — the ONLY thing doing I/O
```

`_showcase_controller.py` is one file because each part of it has exactly one
consumer inside the others: a filter nothing hangs on a template is
unreachable, and the asset hrefs exist only to be passed to a render. It has no
imports outside the standard library and Jinja.

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
API key, so `_build_context`'s assertions and `StrictUndefined` fire during a real
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

**`_validate_context(d)` is the other half, and both sides have it.** Optional,
called by `build()` between the controller and the render, and it catches what
`StrictUndefined` cannot: a key that is present and **wrong**.

The two are not the same job. `_build_context` asserts the **arithmetic** —
that a sankey conserves, that a bridge reaches its endpoint — and lives with
the derivation that produces it. `_validate_context` asserts the **contract
with the view**, which the arithmetic knows nothing about. `financial-profile`
carries both: 13 identities in the derivation, and a `READS` tuple of the 47
`d.*` names its recipe touches.

The checks worth writing are about agreement between values, not presence:

- **length** — a series pairs to categories BY INDEX, and ECharts complains
  about neither a short list nor a long one. The chart draws; the difference is
  simply not there to see.
- **finiteness** — `NaN` and the infinities are `float` instances, so they pass
  every type check and reach `| tojson`, which writes them into the `<pre>`
  unquoted. That is not JSON, so the browser's `JSON.parse` throws and the page
  shows **no chart at all**.
- **collisions** — a repeated category is two ticks a reader cannot tell apart;
  two series sharing a name collapse into one legend key. Names must be unique
  *within one call*, not globally: `bar` legitimately draws two different
  single-series charts both named `FY24`.
- **drift** — anything in the context that no section draws is data left behind
  by a view that changed.

`showcase` is the only thing that renders without an API key, and it covers
components, not reports.

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

1. `reports/<name>/report_controller.py` — subclass `ReportController`, set
   `TITLE`, write `_fetch(**args)` and `_build_context(payloads)`. Declare the
   endpoints in one table at the top; assert every identity in
   `_build_context`. Add `_add_args(parser)` if it takes arguments and
   `_filename(d)` if the data names the file.
2. `reports/<name>/report.html.j2` — `{% extends "reports/_report.master.html.j2" %}`,
   fill `{% block content %}` with `c.<macro>(...)` calls carrying `d.*`.
3. `reports/<name>/usage.md` — what it argues, what it fetches and what that
   costs, the exhibits in order, and what the assertions guarantee. Same
   obligation a component has, and for the same reason: the next person to run
   it needs the editorial rules, not the code.
4. `python reports/report_builder.py <name> … --out DIR`

There is no step registering it, and no `{# report-name: … #}` header any more —
the title is `TITLE` on the class. Jinja discards comments before rendering, so
reading one meant regex-parsing the template you were about to render.

## Adding a component showcase

1. `components/<cat>/<name>/showcase_controller.py` — subclass
   `ShowcaseController` and write `_build_context() -> dict`, line by line. No
   markup, no macro calls. Optionally add `_validate_context(d)`.
2. `components/<cat>/<name>/showcase.html.j2` —
   `{% extends "_showcase.master.html.j2" %}`, one `<section>` per state worth
   seeing: the default, and the ones where the component has to make a decision
   (a legend appears past one series, an axis name widens the margin).
3. `python components/showcase_builder.py <cat>/<name>`

There is no step registering it. `showcase.html` is a build artifact — the
controller and the view are the source, and the generated pages are gitignored
because this is a public repo and 109 of them have no business on the CDN.

Copy `charts/bar/showcase_controller.py` for the four-line preamble that puts
the skill root on `sys.path`. A leaf needs it to import the base
package-qualified, and it walks up to the `components` folder rather than
counting parents, because components sit two to four levels deep.

## The shape of a usage.md

Every component has one and every report has one — 110 files, and they are the
only per-item documentation there is. **Follow this skeleton.** They are read
selectively, one at a time, so a reader who cannot predict where "the rules"
live has to read the whole file to find out there were none:

```markdown
# <name>

_One italic line: what this is, and that this file is authoring guidance._

What it is in two or three sentences. **Use when** … — and, where it earns its
place, **not** for … .

## Markup            (a component: the macro call and its parameters)
## Build it          (a report: the command, the arguments, what they cost)

## Rules
- The things a reader cannot infer from the code, each with its reason.
```

The heading names may vary where the item genuinely differs — a report has no
markup and a component has no fetch — but **`## Rules` is not optional**. It is
the section that carries what the code cannot say: that a bar's axis starts at
zero because length IS the value, that a peer group is chosen rather than
screened. A `usage.md` without it is a description, and the code was already
that.

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
