# components/ — reference

Deep reference for the component library and its showcase engine: what a
component is, how the Jinja environment is built, how a showcase is loaded and
rendered, and the traps in doing that. The authoring contract lives in
`../SKILL.md`; this is the on-demand detail, and this directory is
self-contained — it imports nothing from outside itself.

```
components/
  _showcase_controller.py   ShowcaseController + env() + FILTERS + the asset pair
  _showcase.master.html.j2  the shell every showcase view extends
  showcase_builder.py       ShowcaseBuilder.build(path) + the CLI
  catalog_builder.py        CatalogBuilder.build() -> CATALOG.md
  CATALOG.md                every component by purpose — generated, do not edit
  domain-specific/          one analysis discipline owns it
  foundational/             any document may use these
  math/                     the formula subsystem (KaTeX)

  ONE DIRECTORY PER ENGINE, holding that engine's kinds. The engine is part of
  every macro inside it, because another engine's `bar` is a different macro:
  charts-apache-echarts/    c.charts_apache_echarts_<kind>(...)
    _render.html.j2           ECharts-specific tail, shared by the kinds here
    chart/                    the generic one — a raw spec, for what the
                              named kinds do not cover
    bar/ line/ pie/ …         one folder per kind
  charts-plotly/            reserved, empty (.gitkeep)
  charts-bokeh/             reserved, empty (.gitkeep)
  diagrams-mermaid/         c.diagrams_mermaid_<kind>(...)
    diagram/                  the generic one — Mermaid source directly
```

**A leading underscore marks the library half** — the files that serve
components without being one. It also disambiguates: `_showcase_controller.py`
is the base class, `showcase_controller.py` is a component's own.

## What makes a component

A directory containing `component.html.j2`. That is the whole rule — nothing is
registered anywhere, so adding one means adding files.

```
components/<category>/<name>/
  component.html.j2   the macro. {# purpose #} always; {# data #}, {# unit #} when they apply
  usage.md            when to use it, and the rules            (required)
  showcase_controller.py   _build_context() -> dict            (optional)
  showcase.html.j2         the states worth seeing             (optional)
  showcase.html            build artifact, but TRACKED — see below
```

**`showcase.html` is a build artifact that is nonetheless committed.** It is
generated, never edited by hand, and regenerated whenever the component or its
controller changes — but it is **tracked**, because jsDelivr serves what is
committed and a showcase is meant to be viewable from the CDN without cloning
anything. Every one is in the index; `git check-ignore` exits 1 for all of them.

Do not "fix" this by adding a `.gitignore` rule. That would un-publish every
showcase link in `CATALOG.md` at the next tag, and the pages are the only
rendered evidence of what a component actually looks like.

**Most category folders exist for humans.** `foundational/` and
`domain-specific/` nest to organise the tree; a component's identity is its own
folder name, so moving one between them touches no template. Those names must be
unique across the whole tree — the builder raises on a duplicate.

**An engine folder is different: it NAMESPACES its members.** Every chart engine
has a `bar` and every diagram engine a `diagram`, so a kind's leaf name
identifies it only within its engine. `macro_name()` takes the path, not the
leaf, and qualifies anything under a `charts-` or `diagrams-` directory:

| path under `components/` | macro a view calls |
|---|---|
| `foundational/content/metric-trend` | `c.metric_trend(...)` |
| `charts-apache-echarts/bar` | `c.charts_apache_echarts_bar(...)` |
| `charts-plotly/bar` | `c.charts_plotly_bar(...)` |
| `diagrams-mermaid/diagram` | `c.diagrams_mermaid_diagram(...)` |

The two `bar`s are different macros writing different specs, and one flat
attribute cannot hold both — which is why the engine is in the name rather than
being resolved by whichever sorted first. The qualified form is verbose on
purpose: a view that says `charts_apache_echarts_bar` cannot be silently
repointed at another engine by a change somewhere else.

`NAMESPACED` in `_showcase_controller.py` is the list of prefixes this applies
to. Everything outside it keys on the leaf, so `c.badge` stays `c.badge`.

## The environment

`env()` in `_showcase_controller.py`, module-level and `@cache`d. **Built once
per process**: ~0.5s cold, ~0.001ms after, because building it parses every
component template in the tree. Per-controller it would cost that once per
component.

It is cached at module level rather than on an instance because **it belongs to
the library, not to whoever is rendering** — which is also what lets `reports/`
borrow this exact one instead of a second configuration that happens to match.

### Two roots, components/ first

```python
FileSystemLoader([str(COMPONENTS_DIR), str(SKILL_DIR)])
```

One root cannot resolve everything. A view extends `_showcase.master.html.j2`
and `charts-apache-echarts/bar/component.html.j2` imports `charts-apache-echarts/_render.html.j2` — both named
from `components/`. The master then includes `css/css.loader.html.j2` and
`js/js.loader.html.j2`, which live at the **skill root**.

### The `c` namespace

Every component's macro on one object, so a view calls `{{ c.charts_apache_echarts_bar(...) }}` with
no import of its own:

```python
c = SimpleNamespace()
for markup in sorted(COMPONENTS_DIR.rglob("component.html.j2")):
    macro = macro_name(markup.parent.relative_to(COMPONENTS_DIR).as_posix())
    module = environment.get_template(...).module
    if hasattr(module, macro):
        setattr(c, macro, getattr(module, macro))
environment.globals["c"] = c
```

**The whole tree, not just the component being rendered** — the master shell
reaches for `c.metadata_header`, which lives in `foundational/structure/`. That
is why one showcase costs the full parse.

**A file that defines no macro matching its computed name is skipped silently** —
no error, the component simply never reaches `c`, and the first sign is
`StrictUndefined` firing in whatever view called it. So the `{% macro %}` inside
must match what `macro_name()` produces, qualifier included:
`charts-apache-echarts/bar/component.html.j2` declares
`{% macro charts_apache_echarts_bar(...) %}`.

A file not named `component.html.j2` is never seen at all — which is what
`charts-apache-echarts/_render.html.j2` relies on.

### Filters

`FILTERS` — `money`, `pct`, `signed`, `bps`, `num`, `raw`, and the `fmt`
dispatcher — live in `_showcase_controller.py` because `env()` is the only thing
that ever consumed them: a filter nothing hangs on a template is unreachable.

Ten templates under `domain-specific/` use them, and **Jinja resolves filters at
compile time**, so the env cannot be built at all without them.

`_convert_to_str` makes each format **total**: every input yields a string, none
raise. Text passes through unchanged and `None` becomes `""`, because a
controller legitimately emits `"n/m"` where a ratio has no meaning, and a
missing value is not a zero. `raw` is the one format left unwrapped, which is
why it is the one that can return a non-string.

### StrictUndefined

A view reading a key its controller never produced would, by default, render an
empty string — a tidy blank cell in an otherwise perfect table, which nobody
notices. It raises at build time instead, and since Jinja runs only at build
time the failure costs nothing and reaches no reader.

## The showcase engine

```bash
S=.claude/skills/finance-reports        # from the PROJECT ROOT — see ../SKILL.md

python $S/components/showcase_builder.py charts-apache-echarts/bar
python $S/components/charts-apache-echarts/bar/showcase_controller.py   # a leaf runs alone
(cd $S && python -m components.showcase_builder charts-apache-echarts/bar)
```

The `-m` form is the only one that needs a working directory: it names a
*package*, so it must run from the skill root. The other two name a file.

Addressed by **directory path**, because components nest two to four levels and
the path is the whole address: where the controller is, where the view is, where
the page goes.

`ShowcaseBuilder.build(path)` does no lookup — check the three files exist,
path-load the controller, find the `ShowcaseController` subclass, call `build()`.
It **raises** rather than returning a code; `main()` owns the exit code.

### It finds the class, not the name

`charts-apache-echarts/bar` holding `ChartBarShowcaseController` is a convention worth keeping,
but computing one from the other would make the convention load-bearing — and a
category that pluralizes (`charts` → `Chart`) shows how that goes wrong. A
subclass of `ShowcaseController` in the module is unambiguous. Zero matches and
more than one are both errors that name what they found.

### Two traps in path-loading

Both are load-bearing and both were verified the hard way:

1. **Register in `sys.modules` before executing.** Plain `importlib` path-loading
   skips this, and then nothing can resolve a class back to its file.
2. **Import the base package-qualified** — `from components._showcase_controller
   import …` — in the builder *and* in every leaf. Reached under two names it
   becomes two module objects: `issubclass` fails against the wrong one, and each
   copy builds its own cached env.

The leaf's four-line `sys.path` preamble exists for (2). It walks up to the
`components` folder rather than counting parents, because components sit two to
four levels deep.

**Path-loading removed the old hyphen constraint.** An `import` statement cannot
name a folder with a hyphen, which disqualifies **the majority of the tree** —
`status.py` counts how many carry one. Loading by path has no such rule.

### How a controller knows where it is

`ShowcaseController.directory` reads the filename off the **subclass's own
`_build_context` code object**:

```python
Path(own.__code__.co_filename).resolve().parent
```

Not `__file__` — that names the base module and would put every showcase in
`components/`. Not `inspect.getfile(cls)` — that resolves through
`sys.modules[cls.__module__]` and raises *"is a built-in class"* for a
path-loaded controller. A code object carries its filename with it and needs no
lookup, so a controller reached by import, by path, or run directly all land in
the same place.

## The shape of a showcase

A showcase is two files and they divide the same way a report does: the
controller holds data and calls no macro, the view calls macros and holds no
data. **Follow this skeleton** — there is one per component, and a hundred-odd
written freehand is a hundred-odd dialects.

```python
# showcase_controller.py — NAMED DATA, never per-state bundles.
class ChartBarShowcaseController(ShowcaseController):
    def _build_context(self) -> dict:
        return {"quarters": [...], "revenue": {...}, "by_segment": {...}}
```

```jinja
{# showcase.html.j2 — one <section> per state, <hr> between. #}
{% extends "_showcase.master.html.j2" %}
{% block content %}
    <section>
      <h3>two series — a legend appears, colour is never the only cue</h3>
      {{ c.charts_apache_echarts_bar(series=[d.fy24, d.fy23], categories=d.quarters, ...) }}
    </section>
{% endblock %}
```

Three rules carry the weight:

- **Show the states where the component DECIDES something** — a legend appears
  past one series, an axis name widens the margin, a negative flips the tone,
  an empty list has to say so. A second state that exercises no decision is a
  second copy of the first.
- **The `<h3>` names the decision, not the data.** "two series — a legend
  appears" tells a reader what to look at; "another example" does not.
- **Context keys read as what the data IS**, not which section uses it —
  `by_segment`, not `example_3`. The view is then free to recombine them, and
  a new state costs no controller change.

Demo data is chosen, not invented: it should be the kind of thing the component
exists for, at a plausible magnitude. A `bar` of `[1, 2, 3]` proves the macro
runs and nothing else.

## Validating a context

`_validate_context(d)` is optional and called by `build()` between the
controller and the render. It does the half `StrictUndefined` cannot: a key
present and **wrong**. The checks worth writing are about agreement between
values.

`charts-apache-echarts/bar` is the worked example. Its `CALLS` map is one entry per `<section>`
of the view — per section rather than grouped by axis, because both checks that
matter are relative:

- **length** — a series pairs to categories by index and ECharts complains about
  neither a short nor a long list. The chart draws; the difference is not there
  to see.
- **finiteness** — `NaN` and the infinities are `float` instances, so they pass
  every type check and reach `| tojson`, which writes them into the `<pre>`
  unquoted. That is not JSON, so `JSON.parse` in
  `js/modules/charts-apache-echarts.js` throws and **no chart renders at all**.
- **collisions** — a repeated category is two ticks a reader cannot tell apart;
  two series sharing a name collapse into one legend key. Per call, not global:
  `bar` legitimately draws two single-series charts both named `FY24`.
- **drift** — anything in the context no section draws is data left behind.

### `_contracts.py` — the checks, written once

Those four are the same relation whatever component is asking, and ten of the
charts share one contract exactly:

```
series[] {name:str, points:num[]}   categories: str[]
```

Copied into ten files that would be ten claims about one contract, free to
disagree the moment one of them learned something. `_contracts.py` holds them
instead — `assert_series_categories`, `assert_numbers`, `assert_labels`,
`assert_enum`, `assert_rows`, `assert_all_drawn` — so a lesson is learned once.

Two that are not obvious from their names:

- `assert_numbers` rejects `bool` as well as non-finite values. `bool` is an
  `int` in Python, so `True` would draw as 1; and an integer past
  `Number.MAX_SAFE_INTEGER` arrives rounded, because the page parses its data
  with `JSON.parse` where every number is a float64.
- `assert_all_drawn` runs BACKWARDS, from the context to the calls. Every other
  check runs from the calls to the context, which is why this is the one that
  notices a section the view renamed or data orphaned by one it deleted.

A component still writes the checks only IT can make — `area` capping
overlapping fills at two, `sankey` conserving flow, `bridge` reaching its own
endpoint — beside a call to these.

### What none of them can see

All of the above runs before a browser does. A page whose markup is valid and
whose numbers agree can still be **wrong on screen**: bars past their track, a
unit welded to a number, clipped labels, an axis name over its own ticks.
**Nothing in this skill looks for any of them** — they are layout facts that
exist only once the CSS has been applied, so serving the page and opening it is
the only pass that sees them. The last of the four is not detectable from the
DOM at all — both texts are SVG inside the chart and nothing overflows
anything — so it is handled at render time by the `axis_gap` filter instead.

## The catalogue

```bash
python $S/components/catalog_builder.py    # -> components/CATALOG.md
```

`usage.md` answers *"should I use THIS?"* once you have a candidate. Nothing
answered *"which one?"*, so choosing meant grepping the tree. `CATALOG.md`
is that missing step: name, macro, what it is for, and where to read the rules.

**Generated from the `{# purpose: … #}` header of each `component.html.j2`**, so
it cannot drift — a component that changes its purpose changes the catalogue on
the next build, and one that ships without a purpose **fails the build** rather
than appearing blank. An index of a hundred-odd items maintained by hand is an
index that is wrong; the previous one was deleted for exactly that reason.

It carries no parameters and no examples on purpose. Those would be a second
copy of `usage.md`, and the second copy is the one that rots. A component with
no `usage.md` is shown as **no usage.md** rather than omitted — choosable and
undocumented is the state the catalogue exists to make visible.

## Adding a component

**The procedure is in `../SKILL.md`, under "Adding a component" — all of it,
including the parts this file used to leave out.** It is not repeated here.

That is the split this file already declares in its own first paragraph: the
authoring contract lives in `SKILL.md` and this is the on-demand detail. The
procedure was written down twice anyway, and the report side shows what that
costs — the two copies of "Adding a report" drifted, and the shorter one omitted
the step that declares what a report validates about itself, so a report written
from it passed a validation that was checking almost nothing.

What the procedure needs from this file it names directly: the showcase skeleton
under **The shape of a showcase**, and the checks under **`_contracts.py`**.

**Nothing runs the catalogue automatically.** There is no CI and no git hook in
this repository, so a component added without regenerating it leaves
`CATALOG.md` quietly short by one — the exact way the previous catalogue died.
`--check` makes that loud, on its own or through `status.py`:

```bash
python $S/components/catalog_builder.py --check   # exit 1 if stale, writes nothing
python $S/status.py --check                       # this and the three others
```

Wire either into a pre-commit hook if you want it enforced rather than
remembered.
