---
name: finance-reports
description: Generate data-driven investing reports as standalone HTML, built
  from live market and fundamentals data rather than hand-filled templates. A
  report is a program - a controller fetches and asserts, a view chooses which
  components appear - and the output is regenerated, never edited. Use when
  asked to build, extend, or audit a company, portfolio, market or economy
  report, or to add a report type; when working on the component library behind
  them - adding or restyling a component, writing its usage.md, or building a
  showcase page; and when a generated page comes out wrong - a chart draws
  blank or misshapen, CSS and JS fail to load, a showcase looks stale, or
  version.json was bumped and every page needs rebuilding against it. Not for
  hand-editing a generated report, which is a build artifact to be regenerated,
  and not for charts outside this component library.
---

# finance-reports — reports as programs, not documents

Every report here is **generated end to end**. A controller fetches live data
and does the arithmetic; a view says which components appear and in what order;
the output is a standalone HTML file with no placeholders to fill and nothing
to edit by hand. Regenerate it and you get the same file with newer numbers.

**The contrast worth holding onto** is with the ordinary way a component
library gets used: a template is a **skeleton a human fills** — component calls
carrying literal placeholder text, edited after generation. Here the same
component calls carry `d.*`, so the document is a **program**, and editing the
output would be editing a build artifact.

## Documentation map

| where | read it when |
|---|---|
| **this file** | always — the shape, the contracts, how to add things |
| `components/CATALOG.md` | **choosing a component** — all of them by what they are for, generated |
| `reports/CATALOG.md` | **choosing a report** — every one by what it argues, generated |
| `components/<cat>/<name>/usage.md` | **before using or changing that component** — its rules |
| `reports/<domain>/<name>/usage.md` | **before running that report** — what it argues, fetches and costs |
| `components/REFERENCE.md` | writing a showcase, or a macro/filter/`c`-namespace question |
| `reports/REFERENCE.md` | writing a report controller, or asking where a guarantee comes from |
| `css/REFERENCE.md` | before touching any `.css` — the `@layer` order decides what wins |
| `js/REFERENCE.md` | a chart renders blank, a page has no JS, or a module needs adding |
| `service_providers/REFERENCE.md` | credentials will not resolve, or a fetch is behaving oddly |
| `service_providers/fmp/endpoints.md` | you need an endpoint no report uses yet — check the plan allows it |

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

## Requirements

Python 3.11+ and two libraries: Jinja renders every template, httpx is the only
thing that touches the network. Nothing here builds the published CSS or JS —
those are served raw from the git tag.

```bash
python -m venv .venv
.venv/Scripts/pip install "jinja2>=3.1.4" "httpx>=0.27.0"   # .venv/bin/pip elsewhere
```

A **linked** skill reads its configuration from the clone it was linked from. A
**copied** one is a real file tree in someone else's project: it needs those two
libraries installed there, and the four root files listed under **Credentials**
below created there, because nothing above `.claude/skills/<name>/` travels
with a copy.

## CLI

**Every command below is written from the PROJECT ROOT** — the directory holding
`.claude/`, which is where a session starts. `python` means the project venv's
interpreter (`.venv/Scripts/python.exe` on Windows, `.venv/bin/python`
elsewhere); a system interpreter has no Jinja and fails on the first import.

```bash
S=.claude/skills/finance-reports

python $S/reports/report_builder.py financial-profile INTC --peers AMD,NVDA --out DIR
python $S/reports/catalog_builder.py                  # -> reports/CATALOG.md
python $S/components/showcase_builder.py charts-apache-echarts/bar
python $S/components/showcase_builder.py --all        # rebuild every showcase
python $S/components/showcase_builder.py --check      # verify each is current
python $S/components/showcase_builder.py --missing    # components with none yet
python $S/components/catalog_builder.py               # -> components/CATALOG.md
python $S/status.py                                   # what is in the tree, and every check
```

**Only the script path is relative to where you stand.** Everything inside the
tools derives from `__file__` — which component, which report, where the output
goes — so no argument and no result depends on the working directory.

**No tool here renders a page.** Everything above reads markup, so what a
browser does with it — layout, overflow, whether a chart actually draws — is
checked by opening the page and looking. Serve the repo **root** over `http://`
rather than opening the file, since a showcase links its assets relatively:

```bash
python -m http.server 8000
# http://localhost:8000/.claude/skills/finance-reports/components/charts-apache-echarts/bar/showcase.html
```

There is **no top-level dispatcher**. Each directory owns the engine that
builds what lives in it, and neither knows the other exists as a command.

**`--all` is not a convenience.** A showcase page is tracked and pins the asset
version it was built against, so one edit under `css/` or `js/` invalidates
every page in the tree at once. `--check` writes nothing and names every stale
page, so the answer to "did I regenerate them?" is an exit code rather than a
memory.

**Nothing regenerates a catalogue for you either.** Both `CATALOG.md` files are
derived — from the `{# purpose: … #}` headers, and for reports also from `TITLE`
and the parser the controller declares — but there is no CI and no git hook in
this repository, so anything added without its `catalog_builder.py` run leaves
the catalogue quietly short by one. That is exactly how the previous
hand-maintained index died. Both builders take `--check`: exit 1 if stale,
writes nothing.

A showcase is addressed by its **directory path** (components nest two to four
levels), a report by its **name** alone — its domain is shelving for a reader,
not part of the address, so a name must be unique across every domain. Neither
is a registry lookup: the address IS where the controller, the view and the
output live.

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
python $S/reports/report_builder.py financial-profile --help   # symbol, --peers
```

## The shape — both sides are the same three files

```
                shell                     controller              view
reports/        _report.master.html.j2    report_controller.py    report.html.j2
components/     _showcase.master.html.j2  showcase_controller.py  showcase.html.j2
```

**Python files use underscores so they can be imported; templates keep the
dots.** A **leading underscore** marks the library half of `components/` —
`_showcase_controller.py`, `_showcase.master.html.j2`, `charts-apache-echarts/_render.html.j2`
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

`_fetch` and `_build_context` never touch each other — one place does I/O, and
the derivation is a pure `payloads -> dict`, which is what lets its identity
assertions be read on their own with no request in the middle.

### Which way the arrow points

`components/_showcase_controller.py` owns everything a page needs to render:
the macros' Jinja environment, the `c` namespace that exposes them, the number
filters they format with, and the asset pair every page links. `reports/`
**borrows** them — `env()` is module-level and `@cache`d, because it belongs to
the library rather than to whoever is rendering. So a macro that draws on a
showcase page draws identically in a report: it is the same env, not two
configurations that happen to match. What that caching costs and why it is
module-level is in `components/REFERENCE.md`.

**Reports depend on components, never the reverse.** That is why `components/`
builds its own showcases without knowing reports exist. It imports exactly one
thing from outside itself — `_paths`, at the skill root, which answers *where
is this skill* — and manipulates `sys.path` not at all. That one import is
shared with `reports/` and `service_providers/` on purpose: a layout question
with three answers is a layout question with two wrong ones.

### Nothing is registered — components, reports and showcases are all found

A directory containing `component.html.j2` **is** a component. A directory
containing `report.html.j2` **is** a report. A component directory that also
holds `showcase_controller.py` and `showcase.html.j2` **has** a showcase.
Nothing is listed anywhere, so adding any of the three means adding files and
nothing else.

`ShowcaseBuilder.build("charts-apache-echarts/bar")` therefore does no lookup: check the three
files are present, path-load the controller, find the `ShowcaseController`
subclass in it, call `build()`. It **raises** rather than returning a code,
because a showcase asked for by name and not built is a mistake worth stopping
for.

**It finds the class rather than deriving its name**, and it **path-loads**
rather than importing — the first so a naming convention never becomes
load-bearing, the second because an `import` statement cannot name a folder
with a hyphen and most of this tree has one. `components/REFERENCE.md` has both
in full.

Two things the loader must get right — register the module in `sys.modules`
*before* executing it, and import the base **package-qualified** — and both are
load-bearing enough that `components/REFERENCE.md` writes up the failure each
one produces.

### The preamble every leaf starts with

Copy this rather than reconstructing it. It is the same four lines in a showcase
controller and in a report controller — `charts-apache-echarts/bar/showcase_controller.py` and
`company/financial-profile/report_controller.py` carry it character for
character, and a new leaf on either side is a copy of those four lines and
nothing else:

```python
import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._showcase_controller import ShowcaseController    # noqa: E402
```

**The marker is `_paths.py`, and the search is an ascent, not a count.** Leaves
sit two to four folders deep, so any fixed number of `.parent` calls is correct
at one depth and silently wrong at the next — and wrong here means the base gets
imported under a second name, which is failure (2) above.

The last line is what differs per side: a showcase imports
`ShowcaseController`, and a report imports `ReportController` from
`reports._report_controller`. The
`# noqa: E402` is required on each — the import is deliberately below the
`sys.path` edit that makes it resolvable, and every linter reads that as a
mistake.

## Layout

```
../../../version.json          the CDN pin every generated page carries, at the
                               project root beside config/secrets/environment
_paths.py                      the ONE ascent: find .claude/, derive the rest

components/                    the library: macros, filters, env, assets, showcases
  _showcase_controller.py      ShowcaseController + env() + FILTERS + the asset pair
  _showcase.master.html.j2     the shell every showcase view extends
  showcase_builder.py          ShowcaseBuilder.build(path) + the CLI
  domain-specific/             one discipline owns each; prefixed after it
    fundamental-analysis/        `fa-`         the company under the lens
    portfolio/                   `portfolio-`  a book you hold
    macro/                       `macro-`      the economy, no security in view
  foundational/                any document may use these; NO prefix
  math/                        the formula subsystem (KaTeX)

  ONE DIRECTORY PER ENGINE, holding that engine's kinds. The engine is part of
  every macro inside it, because another engine's `bar` is a different macro:
  charts-apache-echarts/       c.charts_apache_echarts_<kind>(...)
    _render.html.j2              ECharts-specific tail, shared by the kinds here
    chart/                       the generic one — a raw spec, for what the
                                 named kinds do not cover
    bar/ line/ pie/ …            one folder per kind
  charts-plotly/               reserved, empty (.gitkeep)
  charts-bokeh/                reserved, empty (.gitkeep)
  diagrams-mermaid/            c.diagrams_mermaid_<kind>(...)
    diagram/                     the generic one — Mermaid source directly

reports/
  _report_controller.py        ReportController; borrows env() AND the asset pair
  _report_validation.py        what build() checks the rendered page for
  _report.master.html.j2       the shell every report view extends
  report_builder.py            ReportBuilder.build(name, argv, out) + the CLI
  company/                     a domain, holding its reports
    financial-profile/         one report — view, controller, usage
  portfolio/  market/  economy/
                               declared and empty — the taxonomy, stated

css/  css.loader.html.j2       the <link>   + its CDN fallback
js/   js.loader.html.j2        the <script> + its CDN fallback
service_providers/fmp/            the client — the ONLY thing doing I/O
```

`_showcase_controller.py` is one file because each part of it has exactly one
consumer inside the others — a filter nothing hangs on a template is
unreachable. It imports nothing outside the standard library and Jinja.

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
produced would otherwise render an empty string — a tidy blank cell in an
otherwise perfect table, which nobody notices. It raises at build time instead.

**Assertions live in the controller** because that is the only place with the
arithmetic. `financial-profile` carries 13: cost + gross == revenue,
liabilities + equity == assets, each sankey summing to its own table, the
segment bridge reaching its endpoint. They exist because **a diagram that does
not conserve draws perfectly and lies** — a sankey scales each node's ribbons
independently, so an unbalanced one is a confident, wrong picture that no
template and no reader can catch.

**`_validate_context(d)` is the other half, and both sides have it.** Optional,
called by `build()` between the controller and the render, and it catches what
`StrictUndefined` cannot: a key that is present and **wrong**.

The two are not the same job. `_build_context` asserts the **arithmetic** — a
sankey conserving, a bridge reaching its endpoint — beside the derivation that
produces it. `_validate_context` asserts the **contract with the view**, which
the arithmetic knows nothing about. `financial-profile` carries both: 13
identities, and a `READS` tuple of the 48 `d.*` names its recipe touches.

**The checks worth writing are about agreement between values, not presence** —
length against its own categories, finiteness, name collisions, and data no
section draws. All four live once in `components/_contracts.py`, which
`components/REFERENCE.md` documents; a component writes only its own.

`showcase` is the only thing that renders without an API key, and it covers
components, not reports.

**A CLEAN BUILD IS NOT A CORRECT PAGE.** Everything above runs before the
browser does, and three defects have shipped past all of it — bars running out
of their track, a unit welded to a number, clipped axis labels. Those are
LAYOUT facts that exist only once the CSS has been applied, so **nothing in
this skill can see them**. Open the page.

### Report validation — the page says what is wrong with it

`build()` checks the report it just rendered and **renders the findings into the
top of the document**, above the cover. The checks are in
`reports/_report_validation.py`, one home for every report.

**On the page rather than on stdout**, because a chart draws at view time and
the page has to be opened anyway — so the findings arrive where the eye already
is, instead of in output nobody is obliged to read. A report that leaves this
tree then carries its own warning, which is the case that matters most: a reader
cannot otherwise tell a healthy page from one whose endpoint returned nothing.

| | means | fails the build? |
|---|---|---|
| **error** | the page is broken — a spec that will not parse, an asset half that does not resolve, a dangling in-page link, unrendered template syntax, a declared section that never rendered, the pre-6.0.0 `investing-` prefix | no |
| **warning** | it rendered and its content is thin — an empty chart, a table with no rows, a section mostly blank, a requested symbol appearing nowhere | no |

The split exists because the second kind depends on **what was asked for**.
Against a fixed input, a mostly-blank section meant the code broke; against
whatever symbol you named today it usually means that company has little data.
Failing on it would fail a legitimately sparse company's own report.

**Nothing raises and nothing is withheld.** By the time validation runs the page
has cost ~13 live calls, so it is written whatever was found — a page you can
open beats an exception. The findings also print on the way out.

**A clean build leaves an HTML comment**, not an empty box: an absent banner
cannot distinguish *"validated and clean"* from *"validation never ran"*.

**What it checks is the document, never the banner.** The page is rendered, that
string is validated, and only then is it rendered again carrying the findings —
including when there are none, so the all-clear can state how many checks
actually ran.

### When a build fails, and what NOT to do about it

Every one of these has a wrong response that looks like progress. A build spends
~13 live calls with nothing cached, so a retry is a decision, not a reflex.

- **Credentials unresolved** — say which two places were checked, by the full
  paths the error prints, and stop. Never write a key into a file, never pass
  one on a command line, never retry with a guess.
- **A ticker returns nothing** — say so and ask. Substituting a similar symbol
  produces a report about a company nobody asked about, and it looks fine.
- **An endpoint 200s with an empty body** — the build SUCCEEDS. Zeros satisfy
  every identity, so the page renders flat and empty; the per-section blank
  warning at the top of the page is the only thing that sees it. Re-running the
  build cannot clear it and costs another ~13 calls.
- **Anything raised mid-`_fetch`** — the calls already spent are gone. Report
  how many before retrying.
- **`StrictUndefined` or an assertion** — the report is wrong, not the engine.
  Fix the controller or the view; never loosen the check that caught it.

## Credentials

This repository is **public**, and jsDelivr's `/gh/` path publishes it — a key
committed anywhere under this directory is fetchable at a URL by anyone who
guesses the path.

**Four files beside `.claude/`, never inside it.** A skill is copied or linked
as `.claude/skills/<name>/` and nothing above it, so a credential kept outside
that subtree cannot travel with a copy of the skill — and neither can the other
three, which is why a **copied** skill needs all four created in the consuming
project before anything builds:

```
<project>/
  version.json         TRACKED     {"version": …, "cdn": …} — the pin every page carries
  environment.json     TRACKED     {"environment": "dev"} — which env this is
  config.<env>.json    TRACKED     api_url, and anything else not secret
  secrets.<env>.json   GITIGNORED  api_key, and nothing else
  .claude/skills/<name>/
```

`version.json` is on that list because **every generated page links its assets
to it** — `cdn_href()` reads it on every build, so a project without one cannot
render a single showcase, let alone a report.

**A copied skill must REPOINT `cdn`, not just copy the file.** Left at
`…/gh/vasilegrafu/aifx-finance@{version}`, every page the consuming project
builds will fall back to *this* repository's CSS and JS, pinned to a version
number that means something else there — and it will look like it works, because
those assets exist and resolve. What it actually means is that another project's
tag now controls your documents' appearance, and a version you never published
is what they name.

**Nothing catches this.** The asset check in `reports/_report_validation.py`
builds its expectation *from* the local `version.json`, so a copy that kept the
original value agrees with itself and passes. It catches a stale *version*,
never a wrong *repository*. Set `cdn` to wherever the copy is actually published, at
the same time you create the file — a **linked** skill has no such problem,
since `resolve()` walks the junction back to this clone and reads this
`version.json`.

**Two resolutions, both first-hit-wins, both with NO default:**

```
key:  $FMP_API_KEY   ->  secrets.<env>.json   ->  hard error naming both
env:  $ENVIRONMENT   ->  environment.json     ->  hard error
```

One declaration selects both `config.<env>.json` and `secrets.<env>.json`, so a
run cannot read dev settings against a prod key. There is **no `--env` flag**
and no third place either looks. Every build prints what it resolved and from
where, in full paths, before the ~13 calls.

**There is no template for `secrets.<env>.json`** — write the two lines by hand,
`{ "fmp": { "api_key": "<your-fmp-api-key>" } }`. `.gitignore` matches
`secrets.*.json` with **no exception**, so nothing by that name is trackable; a
shipped template would need a negation, and this repo is committed with a
blanket `git add .` against a public, CDN-served tree. For the same reason the environment file
is **not** called `.env`: that is where every tutorial says to put a key, and it
is tracked.

Why declared rather than passed, why two environments, why per-FILE rather than
per-field — **`service_providers/REFERENCE.md`**. It is written down once.

## Adding a component

A component is a directory holding `component.html.j2`. **Nothing is
registered**, so every step below either writes a file or runs something that
reads one — there is no list anywhere to append to.

1. `components/<cat>/<name>/component.html.j2` — one macro named for the folder
   (`name.replace("-", "_")`), opening with `{# purpose: … #}`. **That header is
   required** — `catalog_builder.py` refuses a component without one. Add
   `{# data: … #}` if and only if the input IS data — most components, but one
   taking a `{% call %}` block has nothing to declare — and `{# unit: … #}` only
   where the component displays a quantity whose unit is not obvious from the
   value. Only `purpose` is universal; the other two answer a question the
   component may not raise.
2. `components/<cat>/<name>/usage.md` — skeleton under **The shape of a
   usage.md** below. `## Rules` is not optional.
3. **Style it in the matching `css/` directory**, under the prefix that names
   that directory. No `style=`, no `<style>`, no component sets its own colour.
   A category with no stylesheet yet needs a new file **and one `@import` in
   `css/bundle.css`**; a new JS feature needs its name in `js/bundle.js`. Both
   bundles are hand-maintained manifests on purpose, so a file nothing loads is
   a component that renders unstyled — which reads as a CSS bug and is a missing
   line in a list. `status.py` is what notices.
4. `showcase_controller.py` + `showcase.html.j2` — one `<section>` per state
   where the component **decides** something. Nominally optional; in practice
   every component in the tree has one, and a component without one is
   choosable with no rendered evidence of what it looks like. Follow the
   skeleton in `components/REFERENCE.md` — a hundred-odd written freehand is a
   hundred-odd dialects. **This step is also how an EXISTING component gets its
   first showcase**, which is a catalogue change (step 6) and not only a page.
5. **Bump `version.json` BEFORE rebuilding anything.** A new component is
   additive — MINOR, by the table in `README.md`. Every generated page pins its
   asset version **at build time**, so a rebuild that runs first pins the old
   one and `--check` will say so.
6. Rebuild, then check — in this order:

```bash
python $S/components/showcase_builder.py --all   # step 3 touched css/: EVERY page is stale
python $S/components/catalog_builder.py          # nothing calls it for you
python $S/status.py --check                      # the four exit codes, one command
```

7. **Serve the repo root over `http://` and open the showcase.** Nothing above
   renders a page, so overflow, clipping, bars out of their track and glued
   text are invisible to all of it. This is not optional and it is not covered
   by a green `--check`.
8. **Leave it uncommitted** unless you were asked to commit. A push is a
   separate go-ahead: a published tag is immutable.

Step 6 is not registration. Both catalogues are **derived** — from the purpose
header you already wrote, and from the two files step 4 created — so running
them publishes what the tree already says. Skip them and the index is quietly
short by one, which is exactly how the previous hand-maintained one died.

## Adding a report

0. **Choose the domain by SUBJECT** — `company` (one business), `portfolio` (a
   book you hold), `market` (many securities, or a sector), `economy` (no
   security at all). What it is *about*, never the method or the endpoints:
   one company under the lens with peers as context is `company/`, a set
   compared as a set is `market/`. The name still has to be unique across all
   of them, since a report is addressed by name alone.
1. `reports/<domain>/<name>/report_controller.py` — subclass `ReportController`,
   set `TITLE`, write `_fetch(**args)` and `_build_context(payloads)`. Declare
   the endpoints in one table at the top; assert every identity in
   `_build_context`. Add `_add_args(parser)` if it takes arguments and
   `_filename(d)` if the data names the file.
2. `reports/<domain>/<name>/report.html.j2` — open with a one-line
   `{# purpose: … #}` header, then `{% extends "reports/_report.master.html.j2" %}`
   and fill `{% block content %}` with `c.<macro>(...)` calls carrying `d.*`.
   **The header is required** — `reports/CATALOG.md` is generated from it, and
   the builder refuses a report without one. Components follow the same rule.
3. `reports/<domain>/<name>/usage.md` — what it argues, what it fetches and what that
   costs, the exhibits in order, and what the assertions guarantee. Same
   obligation a component has, and for the same reason: the next person to run
   it needs the editorial rules, not the code.
4. **Declare what the page must contain**, on the controller beside `TITLE` —
   `SECTIONS` (what the view lays out, written by hand so a section that stops
   rendering is a finding rather than an expectation quietly agreeing with it),
   `PREFIX` (the domain class family: `fa-`, `portfolio-`, `macro-`), and
   `_expected_text(**args)` if the request names things that must appear, such
   as a symbol and its peers. Each is optional; declaring nothing **skips** that
   check rather than inventing an expectation — which is why a report written
   without this step passes its own validation while checking almost nothing.

   **There is no test to write.** `build()` validates the page it rendered and
   puts what it found at the top of the document — see **Report validation**
   above. A check that applies to any generated page belongs in
   `reports/_report_validation.py`, never copied into a report: ten reports
   carrying their own reading of the blank-cell threshold are ten claims about
   one number, free to disagree the moment one of them learns something. That is
   the argument `components/_contracts.py` already settled.
5. **`python $S/reports/catalog_builder.py`** — nothing calls it for you. This
   is not registration: the catalogue is derived from the header, the `TITLE`
   and the parser you already wrote, and regenerating it only publishes what the
   tree already says. Skip it and `reports/CATALOG.md` is short by one, which
   means the next session choosing a report cannot see yours.
6. **Bump `version.json`** — a new report is additive, so MINOR. Nothing under
   `css/` or `js/` changed, so no showcase is invalidated and there is nothing
   to rebuild; the bump is what publishes the report at a tag someone can pin.
7. `python $S/status.py --check` — the four exit codes in one command.
8. **Run it**, and ask for both arguments rather than choosing either:

```bash
python $S/reports/report_builder.py <name> … --peers … --out DIR
```

9. **Open the page.** It costs ~13 live calls and validates itself, but a clean
   validation means the markup is valid, not that the page is right — charts
   draw at view time and nothing here has seen one.
10. **Never commit the output.** A built report carries live market data and
    differs on every run; it is an artifact, wherever it was written. The source
    (controller, view, `usage.md`) is what gets committed, and only when asked.

There is no step registering it, and no `{# report-name: … #}` header any more —
the title is `TITLE` on the class. Jinja discards comments before rendering, so
reading one meant regex-parsing the template you were about to render.

Start every controller — both sides — with the `sys.path` preamble under **The
preamble every leaf starts with** above.

## Knowing what is in here, without counting it in prose

```bash
python $S/status.py           # components per category, reports per domain, version, checks
python $S/status.py --check   # exit 1 if any generated file is stale
```

`--check` covers five things. Three have an engine that already decides them —
both `catalog_builder.py` and `showcase_builder.py --all --check` — so it runs
those commands and reports their exit codes rather than forming a second opinion
about what "stale" means. Two have no engine and are computed there: the
`usage.md` skeleton, and whether `css/bundle.css` imports every stylesheet and
`js/bundle.js` lists every module.

**No document here states a count of the tree.** A sentence saying how many
components carry a hyphen, or how many a stylesheet namespaces, is true when it
is typed and cannot announce that it stopped being — `CATALOG.md` may state one
because it is generated, and a REFERENCE may not. A number describing the tree
**now** is read from `status.py`; a number arguing that something happened at a
moment stays in prose and dates itself.

## The shape of a usage.md

Every component has one and every report has one — no exceptions, and they are
the only per-item documentation there is (`status.py` names any that is
missing). **Follow this skeleton.** They are read
selectively, one at a time, so a reader who cannot predict where "the rules"
live has to read the whole file to find out there were none:

```markdown
# <name>

_One italic line: what this is, and that this file is authoring guidance._

What it is in two or three sentences. **Use when** … — and, where it earns its
place, **not** for … .

### Markup          (a component: the macro call and its parameters)
### Build it        (a report: the command, the arguments, what they cost)

### Rules
- The things a reader cannot infer from the code, each with its reason.
```

*(Those are `##` in the real file — shown a level down here so they do not read
as sections of THIS document.)*

The heading names may vary where the item genuinely differs — a report has no
markup and a component has no fetch — but **`## Rules` is not optional**. It is
the section that carries what the code cannot say: that a bar's axis starts at
zero because length IS the value, that a peer group is chosen rather than
screened. A `usage.md` without it is a description, and the code was already
that.

**Rules are bullets, each led by its claim in bold, then the reason.** All the
conforming files do this and it is what makes them skimmable one-handed; a
paragraph beginning "Rules:" packs four rules into four sentences and is read
as none.

**`status.py` is the exit code behind this section** — it asserts the three
things SKILL.md actually mandates (a `usage.md` exists, it opens with an H1, it
carries `## Rules`) and nothing softer:

```bash
python $S/status.py           # name every file that does not conform
python $S/status.py --check   # exit 1 if any does
```

It deliberately does **not** check `## Markup` or `## Build it`, because the
paragraph above lets those names vary and a check that fails correct files
earns an ignore rule rather than a fix. This was the last convention here
enforced by nothing, and it is the one that drifted: 62 of 110 files had no
`## Rules` when it was first measured. That is what an unenforced convention
converges to, not a fact about those authors.

It is one of the two checks `status.py` performs itself rather than delegating,
and for a reason worth keeping: the catalogues and the showcase pages each have
a builder that can say whether they are current, and this has no engine behind
it at all. A check with a possible owner belongs to that owner; only a check
with none is written into `status.py`.

## House rules for components

- **No `style=` and no `<style>` in generated documents.** Geometry comes from
  `data-` attributes read by typed `attr()`, with `js/modules/attr-fallback.js`
  covering engines that do not support it yet.
- **No component sets its own colour.** Every colour in the system is a custom
  property in `css/foundational/theme.css`; charts read the chart tokens once at
  load. `--accent` is the rebranding knob.
- **No animations.**
- **A class is unprefixed ONLY in `foundational/`.** Anywhere else it carries
  the name of the directory it lives in — `fa-`, `portfolio-`, `macro-`,
  `chart-`, `diagram-`. A class that resists its prefix is telling you it is
  foundational. The prefix names the DIRECTORY, never the skill.
  **`status.py --check` enforces this**, in both directions and including
  doubled prefixes. It is not a tidiness preference: `domain` is a later
  `@layer` than `content` and `blocks`, so a foundational component that
  borrows a domain class cannot restyle it, and a discipline that restyles its
  own class silently restyles every foundational borrower. Six classes had
  crossed the line before 11.0.0 and one rendered visibly wrong for it — see
  `css/REFERENCE.md`, **Which direction dependencies run**.
- A chart never sets its own title; captions and units go through the shared
  chart frame so every exhibit is labelled the same way.
- **Every component declares `{# purpose: … #}`. A component declares
  `{# data: … #}` if and only if its input IS data** — most do; the rest take
  a `{% call %}` block and have nothing to declare. That is the test, not a
  matter of how much effort the component looks like it deserves: a data
  contract nobody can see is the one a showcase or a report gets wrong.
