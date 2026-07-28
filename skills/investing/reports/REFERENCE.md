# reports/ — reference

Deep reference for the report engine: the four stages a report runs, the
controller contract, how one is loaded and rendered, and where the guarantees
come from. The authoring contract lives in `../SKILL.md`; what a specific report
argues and costs lives in its own `usage.md`. This is the on-demand detail.

```
reports/
  _report_controller.py     ReportController + its own copy of the asset pair
  _report.master.html.j2    the shell every report view extends
  report_builder.py         ReportBuilder.build(name, argv, out) + the CLI
  catalog_builder.py        CatalogBuilder.build() -> CATALOG.md
  CATALOG.md                every report by what it argues — generated
  financial-profile/        one report
```

**A leading underscore marks the library half.** `_report_controller.py` is the
base class, `report_controller.py` is a report's own.

## What makes a report

A directory containing `report.html.j2`. Nothing is registered anywhere.

```
reports/<name>/
  report_controller.py   a ReportController subclass
  report.html.j2         the recipe: which exhibits, in what order
  usage.md               what it argues, what it costs        (required)
```

## Four stages that fail differently

```
arguments  ->  fetch (I/O)  ->  derive (pure)  ->  render  ->  write
```

The whole design follows from keeping them apart. `_fetch` is the only thing
that touches the network. `_build_context` is a pure `payloads -> dict`, which
is what makes the identities it asserts readable on their own: everything they
check is in front of you, with no request in the middle.

## The contract

```python
class FinancialProfileReportController(ReportController):
    TITLE = "Financial Profile"

    def _add_args(self, parser): ...          # optional — this report's CLI
    def _fetch(self, **args): ...             # required — the ONLY I/O
    def _build_context(self, payloads): ...   # required — pure, asserts identities
    def _validate_context(self, d): ...       # optional — the view's contract
    def _filename(self, d): ...               # optional — defaults to <name>.html
```

`ReportController.build(out_dir, **args) -> Path` runs the stages and returns
the file. It **raises** rather than returning a code; `main()` owns the exit
code.

### Why the title is a class attribute

`TITLE` is what a reader sees as the document type, above the heading;
`d["title"]` overrides it when the report computes one from the data
(`"Micron Technology, Inc. — Financial Profile"`).

It is not read from the template. The previous engine regex-scraped a
`{# report-name: … #}` comment out of the view's **source**, because Jinja
discards comments before rendering — parsing a file you are about to render, as
text, to recover something you could have declared.

### Why the destination has no default

`--out` is required. The page's local asset href is computed **relative to where
the file is written**, so a report composed without naming its destination would
link its CSS and JS relative to a directory nobody chose. A showcase needs no
such flag: it lands beside the component it shows.

**The absent default is a question, not a gap.** Whoever drives the CLI must
supply the destination, and if they were not told it they must **ask** rather
than pick one — see the rule in `../SKILL.md`. The engine deliberately cannot
help here: it has no sensible default to fall back on, and a report written to
an invented path fails silently in two ways at once, landing where nobody looks
and computing its asset links against the wrong root.

`_filename(d)` defaults to `<name>.html`; `financial-profile` overrides it to
`<slug>-financial-profile.html`, because the report is *about* a company and two
symbols must not land on the same file.

### Why there is no --force

The output is a **build artifact**, exactly like a showcase page. The controller
and the view are the source, and a report regenerated from the same symbol is
the same report with newer numbers. There is nothing hand-edited to protect, so
it overwrites without asking.

## Where the environment comes from

`_report_controller.py` **borrows** `env()` from
`components._showcase_controller`. Reports depend on components, never the
reverse, and one env means a macro drawn on a showcase page draws identically in
a report — it is the same environment, not two configurations that happen to
match.

It carries **its own copy** of `cdn_href` / `local_href` so this directory stays
readable on its own. That is a deliberate duplication: the asset pair is 45
lines with no dependencies, while `env()` has behaviour that must not be
duplicated (two `@cache`d copies would parse the 109-template tree twice and
could disagree about what a thousands separator looks like).

The view is named to the env as `reports/<name>/report.html.j2` — relative to
the **skill root**, the loader's second search path.

## The engine

```bash
python reports/report_builder.py financial-profile MU --peers none --out DIR
python reports/report_builder.py financial-profile MU --peers INTC,WDC --out DIR
python reports/report_builder.py financial-profile --help    # the REPORT's args
```

Addressed by **name**, not path: reports are flat one level, so the name is the
path. (`components/showcase_builder.py` takes `charts/bar` because components
nest two to four levels — same idea at two depths.)

### Two levels of CLI, and why

The arguments after the report name belong to **the report**. The engine cannot
know what a symbol is and should not have to, so the controller declares them
through `_add_args(parser)` and `main()` uses `parse_known_args` to hand over
what it did not claim.

That creates one wrinkle worth knowing: argparse fires the *engine's* `-h`
during `parse_known_args`, so `report_builder.py <report> --help` would never
reach the report's parser. `main()` checks for it **before parsing** and
delegates to `ReportBuilder.help(name)`.

### Two traps in path-loading

Identical to the showcase side, and load-bearing for the same reasons:

1. **Register in `sys.modules` before executing.** Plain `importlib` path-loading
   skips this, and then nothing can resolve a class back to its file.
2. **Import the base package-qualified** — `from reports._report_controller
   import …` — in the builder and in every leaf. Reached under two names it
   becomes two module objects and `issubclass` fails against the wrong one.

`ReportController.directory` reads the filename off the **subclass's own
`_build_context` code object** (`own.__code__.co_filename`), not `__file__` and
not `inspect.getfile(cls)` — the latter resolves through `sys.modules` and
raises *"is a built-in class"* for a path-loaded controller.

### Naming the template that failed

`blame(exc)` returns the **deepest `.j2` frame** in a Jinja traceback — Jinja
rewrites tracebacks so template frames appear as real frames whose filename is
the `.j2` path. A report view calls 25 macros across 15 components, so *"the
render failed"* is not an answer anyone can act on. `build()` wraps the render
and re-raises with `<component>:<line>` attached.

## Where the guarantees come from

Two kinds of assertion, in two places, and the split is deliberate.

**`_build_context` asserts the arithmetic.** `financial-profile` carries 13:
cost + gross == revenue, liabilities + equity == assets, each sankey summing to
its own table, the segment bridge reaching its endpoint. They live with the
derivation because that is the only place with the arithmetic, and they exist
because **a diagram that does not conserve draws perfectly and lies** — a sankey
scales each node's ribbons independently, so an unbalanced one is a confident,
wrong picture that no template and no reader can catch.

**`_validate_context` asserts the contract with the view**, which the arithmetic
knows nothing about. `financial-profile` carries 2: every one of the 47 `d.*`
names its recipe reads is present, and no `NaN` or infinity survives anywhere in
the nested structure. Non-finite numbers pass every type check, reach
`| tojson` unquoted, and make the browser's `JSON.parse` throw — the exhibit
renders as nothing at all. The check is recursive because a report's numbers
live inside rows, nodes, links and series, never at the top level.

A build that violates either **stops**. It does not warn.

`StrictUndefined` covers the third case: a key the view reads and the controller
never wrote raises at render.

## The catalogue

```bash
python reports/catalog_builder.py       # -> reports/CATALOG.md
```

`usage.md` answers *"should I run THIS one?"* once you have a candidate. The
catalogue is the step before: name, title, what it argues, what it accepts.

**Nothing in it is written by hand** — the purpose comes from the view's
`{# purpose: … #}` header through `ReportBuilder.purpose()`, the title from
`TITLE` on the class, and the argument column from `format_usage()` on the
parser the controller itself declared in `_add_args`. A report that changes what
it takes changes the catalogue on the next build.

With one report this is not yet a real question. It becomes one the moment two
reports could plausibly answer the same request — and a report costs ~13
network calls, so choosing wrong is more expensive here than picking the wrong
component. Built now because the conventions it depends on are cheap to hold
with one report and expensive to backfill across a dozen.

## Adding a report

1. `reports/<name>/report_controller.py` — subclass `ReportController`, set
   `TITLE`, write `_fetch(**args)` and `_build_context(payloads)`. Declare the
   endpoints in one table at the top; assert every identity.
2. `reports/<name>/report.html.j2` — `{% extends "reports/_report.master.html.j2" %}`,
   `c.<macro>(...)` calls carrying `d.*`. No arithmetic, no I/O. **The
   `{# purpose: … #}` header is required** — the build checks it.
3. `reports/<name>/usage.md` — see the skeleton in `../SKILL.md`.
4. **`python reports/catalog_builder.py`** — nothing calls it for you.
5. `python reports/report_builder.py <name> … --out DIR`

Nothing to register. Building requires the network and `FMP_API_KEY` — see
`../data_providers/REFERENCE.md` for the client and the credential order.

**Nothing runs the catalogue automatically.** There is no CI and no git hook
here, so a report added without step 4 leaves `CATALOG.md` short by one.
`--check` makes that loud:

```bash
python reports/catalog_builder.py --check      # exit 1 if stale, writes nothing
```
