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
python $S/reports/report_test_runner.py --list        # tests, and what they cost
python $S/reports/report_test_runner.py --all         # each builds for REAL
python $S/reports/catalog_builder.py                  # -> reports/CATALOG.md
python $S/components/showcase_builder.py charts/bar
python $S/components/showcase_builder.py --all        # rebuild every showcase
python $S/components/showcase_builder.py --check      # verify each is current
python $S/components/showcase_builder.py --missing    # components with none yet
python $S/components/showcase_audit.py                # the page that checks them
python $S/components/catalog_builder.py               # -> components/CATALOG.md
python $S/usage_audit.py                              # every usage.md vs the skeleton
```

**Only the script path is relative to where you stand.** Everything inside the
tools derives from `__file__` — which component, which report, where the output
goes — so no argument and no result depends on the working directory.

**`showcase_audit.py` generates a page, it does not print a verdict.** Serve the
repo **root** and open it — the script prints both lines when it runs:

```bash
python -m http.server 8000
# http://localhost:8000/.claude/skills/finance-reports/components/showcase_audit.html
```

**It has to be `http://`, not the file.** The page checks each showcase in an
iframe, and a browser blocks cross-document access over `file://` — so opening
it by double-clicking shows an empty audit that reads as a pass. What it can and
cannot see is under **What guards the output** below, and in full in
`components/REFERENCE.md`.

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
holds `showcase_controller.py` and `showcase.html.j2` **has** a showcase, and a
report directory that also holds `report_test.py` **has** a test. Nothing is
listed anywhere, so adding any of the four means adding files and nothing else.

`ShowcaseBuilder.build("charts/bar")` therefore does no lookup: check the three
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
controller and in a report controller — `charts/bar/showcase_controller.py` and
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
`ShowcaseController`, a report imports `ReportController` from
`reports._report_controller`, and a report test imports `_report_checks`. The
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
  charts/                      engine-backed charts (Apache ECharts)
  domain-specific/             one discipline owns each; prefixed after it
    fundamental-analysis/        `fa-`         the company under the lens
    portfolio/                   `portfolio-`  a book you hold
    macro/                       `macro-`      the economy, no security in view
  foundational/                any document may use these; NO prefix
  diagrams/  math/             the two other rendering subsystems

reports/
  _report_controller.py        ReportController; borrows env() AND the asset pair
  _report.master.html.j2       the shell every report view extends
  report_builder.py            ReportBuilder.build(name, argv, out) + the CLI
  report_test_runner.py        finds report_test.py, totals the cost, runs them
  company/                     a domain, holding its reports
    financial-profile/         one report — view, controller, usage, report_test
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
LAYOUT facts that exist only once the CSS has been applied.
`components/showcase_audit.py` is the pass that looks for them, and even it
cannot see a chart that is merely wrong.

### When a build fails, and what NOT to do about it

Every one of these has a wrong response that looks like progress. A build spends
~13 live calls with nothing cached, so a retry is a decision, not a reflex.

- **Credentials unresolved** — say which two places were checked, by the full
  paths the error prints, and stop. Never write a key into a file, never pass
  one on a command line, never retry with a guess.
- **A ticker returns nothing** — say so and ask. Substituting a similar symbol
  produces a report about a company nobody asked about, and it looks fine.
- **An endpoint 200s with an empty body** — the build SUCCEEDS. Zeros satisfy
  every identity, so the page renders flat and empty; `report_test_runner.py
  <name>` and its per-section blank check are the only things that see it.
  Re-running the build cannot clear it and costs another ~13 calls.
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

**Nothing catches this.** The `assets_resolve` check in a report test builds its
expectation *from* the local `version.json`, so a copy that kept the original
value agrees with itself and passes. The check catches a stale *version*, never
a wrong *repository*. Set `cdn` to wherever the copy is actually published, at
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
4. **`python $S/reports/catalog_builder.py`** — nothing calls it for you. This
   is not registration: the catalogue is derived from the header, the `TITLE`
   and the parser you already wrote, and regenerating it only publishes what the
   tree already says. Skip it and `reports/CATALOG.md` is short by one, which
   means the next session choosing a report cannot see yours.
5. `python $S/reports/report_builder.py <name> … --out DIR`
6. `reports/<domain>/<name>/report_test.py` — **four declarations and a `CHECKS`
   tuple**, not a copied test. `REPORT`, `ARGV`, `CALLS` and `OUT`, then
   `checks.UNIVERSAL` from `reports/_report_checks.py` plus the three that take
   this report's own answer — its `SECTIONS`, its symbols, its domain prefix —
   and any check only THIS finished page can answer. The build asserts its own
   arithmetic; what it cannot see is an empty page, since `0 + 0 == 0` satisfies
   `cost + gross == revenue`. Add a `report_test_output/` folder beside it
   holding a `.gitkeep` — that is where it writes, `.gitignore` already covers
   the contents of every one of them, and the destination is not free to move
   (`reports/REFERENCE.md` says why).

   **Never copy a check body into a leaf.** Ten reports carrying their own
   reading of the blank-cell threshold are ten claims about one number, free to
   disagree the moment one of them learns something — the argument
   `components/_contracts.py` already settled for components. A check that
   applies to any generated page belongs in `_report_checks.py`, where adding it
   reaches every report on its next run.

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
3. `python $S/components/showcase_builder.py <cat>/<name>`
4. **`python $S/components/catalog_builder.py`** — nothing calls it for you. A
   showcase is a **column in the catalogue**, not just a page: the row for a
   component with both `showcase_controller.py` and `showcase.html.j2` carries a
   `[showcase]` link and the row for one without carries nothing. So this step
   is needed when you give an EXISTING component its first showcase, not only
   when you add a component.

**Follow the skeleton in `components/REFERENCE.md`** — there is one showcase per
component, and a hundred-odd written freehand is a hundred-odd dialects.

There is no step registering it — step 4 included, which derives a link from the
two files you just wrote rather than recording them anywhere. `showcase.html` is
a build artifact — the
controller and the view are the source — but it is **tracked**, so a showcase
is viewable straight from the CDN without cloning anything. Regenerate it
whenever you change the component or its controller, or the committed page
describes a version of the component that no longer exists.

Start the controller with the `sys.path` preamble under **The preamble every
leaf starts with** above — every leaf needs it, reports included, and it is the
same four lines on both sides.

## The shape of a usage.md

Every component has one and every report has one — no exceptions, and they are
the only per-item documentation there is (`usage_audit.py` counts them and
names any that is missing). **Follow this skeleton.** They are read
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

`usage_audit.py` is the exit code behind this section — it asserts the three
things SKILL.md actually mandates (a `usage.md` exists, it opens with an H1, it
carries `## Rules`) and nothing softer:

```bash
python $S/usage_audit.py           # name every file that does not conform
python $S/usage_audit.py --check   # exit 1 if any does
```

It deliberately does **not** check `## Markup` or `## Build it`, because the
paragraph above lets those names vary and an audit that fails correct files
earns an ignore rule rather than a fix. This was the last convention here
enforced by nothing, and it is the one that drifted: 62 of 110 files had no
`## Rules` when the audit was written. That is what an unenforced convention
converges to, not a fact about those authors.

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
- A chart never sets its own title; captions and units go through the shared
  chart frame so every exhibit is labelled the same way.
- **Every component declares `{# purpose: … #}`. A component declares
  `{# data: … #}` if and only if its input IS data** — most do; the rest take
  a `{% call %}` block and have nothing to declare. That is the test, not a
  matter of how much effort the component looks like it deserves: a data
  contract nobody can see is the one a showcase or a report gets wrong.
