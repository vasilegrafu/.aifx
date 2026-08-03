# reports/ — reference

Deep reference for the report engine: the four stages a report runs, the
controller contract, how one is loaded and rendered, and where the guarantees
come from. The authoring contract lives in `../SKILL.md`; what a specific report
argues and costs lives in its own `usage.md`. This is the on-demand detail.

```
reports/
  _report_controller.py     ReportController + its own copy of the asset pair
  _report.master.html.j2    the shell every report view extends
  _report_checks.py         the checks every report test makes + run()
  report_builder.py         ReportBuilder.build(name, argv, out) + the CLI
  catalog_builder.py        CatalogBuilder.build() -> CATALOG.md
  CATALOG.md                every report by what it argues — generated
  company/                  a domain, holding its reports
    financial-profile/      one report
  portfolio/                empty — a .gitkeep holds the shelf
  market/                     ”
  economy/                    ”
```

**A report is filed by its SUBJECT — the thing it is about.** Not by method,
and that is the whole point: a good company report already draws on
fundamental, macro and quantitative work at once, so a method-shaped shelf
would make every filing decision a judgement call. The subject does not blend.

| domain | the report is about | typical |
|---|---|---|
| `company/` | one business | financial profile, thesis, earnings note |
| `portfolio/` | a book you hold | review, attribution, risk, drawdown |
| `market/` | many securities compared, or a sector | screens, peer tables, breadth |
| `economy/` | no security at all | macro dashboard, cycle position |

**Where `company/` ends and `market/` begins:** one company under the lens,
with others present only as context, is `company/` — `financial-profile` takes
`--peers` and stays a company report. A set compared as a set, with no single
subject, is `market/`.

The domains are a taxonomy for a reader choosing a report, not a namespace: a
report is still addressed by its own name, and the name must be unique across
all of them. The empty ones are declared rather than created on demand so the
taxonomy is visible — what belongs where is a decision, and an empty shelf
states it.

**A leading underscore marks the library half.** `_report_controller.py` is the
base class, `report_controller.py` is a report's own.

## What makes a report

A directory containing `report.html.j2`. Nothing is registered anywhere.

```
reports/<domain>/<name>/
  report_controller.py   a ReportController subclass
  report.html.j2         the recipe: which exhibits, in what order
  usage.md               what it argues, what it costs        (required)
```

Discovery is `rglob`, so the domain level costs the engine nothing — but it
does mean two domains cannot both hold a `financial-profile`. `all()` raises on
a duplicate name rather than picking one.

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

There is deliberately **no conventional destination either** — no `output/`
shelf to fall into by habit. A real deliverable goes wherever the reader asked
for it.

The one place the question is already answered is a test — see below.

## Testing a report

```bash
S=.claude/skills/finance-reports        # from the PROJECT ROOT — see ../SKILL.md

python $S/reports/report_test_runner.py --list      # what exists, and the cost
python $S/reports/report_test_runner.py financial-profile
python $S/reports/report_test_runner.py --all
```

**The test sits beside the report**, as `report_test.py` — four declarations and
a `CHECKS` tuple. A directory holding `report.html.j2` **is** a report; one that
also holds `report_test.py` **has** a test — the same rule a component follows
with `showcase_controller.py`, and nothing is registered either way.

**The checks themselves live once, in `_report_checks.py`.** Seven are universal
— they are generic over "a page this skill generated" and a leaf takes them
whole as `checks.UNIVERSAL`, so a check added there reaches every report on its
next run. Three have universal logic and a per-report *expectation*, so they are
factories called with the report's own answer:

```python
CHECKS = checks.UNIVERSAL + (
    checks.sections_are_populated(SECTIONS),        # the sections it declares
    checks.symbols_present([ARGV[0], *ARGV[-1].split(",")]),
    checks.markup_is_current("fa-"),                # `portfolio-` for a book
)
```

`run(REPORT, ARGV, OUT, CHECKS)` builds for real, echoes the resolved
credentials before spending a call, runs every check, and owns the exit code.

**A check body is never copied into a leaf.** Ten reports carrying their own
reading of `BLANK_LIMIT` are ten claims about one measured number, free to
disagree the moment one of them learns something — which is the argument
`components/_contracts.py` already settled one level down, and the same reason
this directory refuses a mirrored tree of test folders below. The alternative was a mirrored tree of test
directories, and a mirror is a second copy of the taxonomy free to drift from
the first; this repository already deleted a hand-maintained catalogue for that
reason.

Being inside the skill means it travels with it: a skill **linked** into another
project can be tested there, which is the fastest way to learn whether that
project's `environment.json` and `secrets.<env>.json` resolve — the failure a
fresh install actually has.

**The page lands in `report_test_output/`, beside the report**, and stays there
to be opened. Every report has one:

```
company/financial-profile/
  report.html.j2  report_controller.py  report_test.py  usage.md
  report_test_output/
    .gitkeep                       tracked — the folder exists in a fresh clone
    amd-financial-profile.html     ignored — never committed, never published
```

**Tracked as an empty directory.** `.gitignore` carries one pair of rules for
all of them:

```
**/report_test_output/*
!**/report_test_output/.gitkeep
```

The leading `**/` is load-bearing — a pattern containing a slash is anchored to
the `.gitignore`'s own directory, so plain `report_test_output/*` matches only at
the repo root and silently ignores nothing four levels down. With it, **a new
report needs no new rule.**

That is what makes writing inside a published tree safe: jsDelivr serves what is
committed, and this repo is committed with a blanket `git add .` — so the
`.gitignore` rule is the only thing standing between a built page and a public
URL, and a page that is never committed is never swept up and never served. A skill **copied** into another
project needs the same two lines in that project's `.gitignore`, exactly as
`secrets.*.json` does.

**Written at all, rather than held in memory**, because the destination is part
of what is under test. `build()` renders, writes and returns a path — that *is*
its contract, and a test that rebuilt the four stages in-process to avoid the
disk would have stopped testing the thing it is named after. Concretely,
`local_href` is computed **from** the destination, so with no destination
`assets_resolve` loses the half that catches a wrong `../` depth.

**Not the system temp directory**, which was tried and is wrong on Windows: it
is on `C:` while a project usually is not, and `local_href` is empty when no
relative path exists between two drives — so the page would link the CDN alone,
render unstyled against a tag that may not be pushed, and leave the local half
of `assets_resolve` testing nothing. Beside the report is the same volume by
construction.

That destination is declared in the test rather than asked for, and it is not an
exception being smuggled in: `--out` has no default because **a report is a
deliverable somebody asked for**, and a scratch artifact nobody receives is not
one.

### What it checks, and why the build cannot

`_build_context` asserts the arithmetic and `_validate_context` asserts the view
contract, but **neither has seen the file**. Two tiers:

- **is it well-formed** — every chart spec survives `JSON.parse`, both asset
  halves resolve and the CDN half pins the *current* `version.json`, every
  `href="#x"` finds an `id="x"`, no half-rendered markup, no pre-6.0.0 prefix
- **does it carry data** — no chart is an empty frame, no `<tbody>` is a header
  over nothing, every declared section has content, every requested symbol
  appears, and no section is mostly blanks

The second tier exists because the first cannot fail on an empty page. An
endpoint returning 200 with an empty body yields zeros, and **`0 + 0 == 0`
satisfies `cost + gross == revenue`** — the identities hold, all 48 `READS`
names are present, every spec is valid JSON, and the report renders beautifully
with flat lines and nothing in it.

Blanks are measured **per section**. A real build is 19% blank against a limit
that must sit above 50% to clear known-good markup, so one dead endpoint would
move a seven-section page to ~26% and never fire; measured where the failure
lands, that section reads 100% and the complaint names it.

### Cost, and why `--all` is explicit

Each test builds its report for real: ~13 calls, nothing cached, no offline
mode. Ten reports is ~130 calls of live quota, so **a bare invocation runs
nothing** — it lists what exists and totals what it would spend. Each test
declares `CALLS = <n>`, which the runner reads out of the source with `ast`
rather than by importing, since importing is where the expense begins.

Each test runs as **its own process**: every one puts the skill on `sys.path`
and path-loads controllers into `sys.modules` under aliases of its own, and the
exit code is already the contract. Sharing an interpreter would trade that
isolation for ~0.5s of cached Jinja environment against a test that spends ten
seconds on the network.

**A green run means the page is valid, not that it is right.** Charts draw at
view time. Open it.

### The environment is DECLARED, not passed — and there is no flag

It comes from `ENVIRONMENT`, or from `environment.json` beside `.claude/`, and
nowhere else:

```
1. ENVIRONMENT        the variable — a shell, CI, or setx
2. environment.json   {"environment": "dev"}, tracked, this checkout
3. hard error
```

It selects **two** files — `config.<env>.json` for the API URL and
`secrets.<env>.json` for the key — so one declaration cannot put them out of
step.

**A `--env` flag existed in 6.0.0 and was removed.** Two reasons, and the
second is the one that killed it:

- It could only reach builds driven through `report_builder.py`. Anything
  importing `FmpClient` directly still needed the declaration, so the same fact
  had two homes and they were free to disagree.
- **A flag cannot be inherited.** An editor's terminal settings do not reach a
  shell spawned by another tool, and that is where builds actually run — so the
  flag had to be retyped by whoever was driving, every time.

The file is not a default in the sense that matters: the build prints both the
value and where it read it, in full paths, before it spends a call.

```
environment: dev (from D:\...\environment.json)   config.dev.json, key from ...
```

That line is the safety property the required flag was reaching for. What it
prevents is not "unstated" but "unnoticed" — including a stale `ENVIRONMENT` in
some shell silently overriding this checkout's own file, which it names. See
`service_providers/REFERENCE.md` for why the file is not called `.env`.

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
duplicated (two `@cache`d copies would parse the whole component tree twice and
could disagree about what a thousands separator looks like).

The view is named to the env as `reports/<domain>/<name>/report.html.j2` —
relative to the **skill root**, the loader's second search path. It is computed
as `(directory / VIEW).relative_to(SKILL_DIR)`, so the depth of the tree is
never restated in code.

## The engine

```bash
python $S/reports/report_builder.py financial-profile MU --peers none --out DIR
python $S/reports/report_builder.py financial-profile MU --peers INTC,WDC --out DIR
python $S/reports/report_builder.py financial-profile --help    # the REPORT's args
```

Addressed by **name**, not path — and the two no longer coincide, since a
report sits under its domain. The name stays the address because the domain is
shelving for a reader, and making it part of the address would force whoever
runs a report to know how it was filed. (`components/showcase_builder.py` takes
`charts/bar` because components nest two to four levels — same idea at two
depths.)

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
knows nothing about. `financial-profile` carries 2: every one of the 48 `d.*`
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
python $S/reports/catalog_builder.py    # -> reports/CATALOG.md
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

0. **Choose the domain by SUBJECT** — `company`, `portfolio`, `market`,
   `economy`. What the report is about, not the method it uses or the
   endpoints it happens to call. A new domain is a new directory; nothing
   registers one.
1. `reports/<domain>/<name>/report_controller.py` — subclass `ReportController`,
   set `TITLE`, write `_fetch(**args)` and `_build_context(payloads)`. Declare
   the endpoints in one table at the top; assert every identity.
2. `reports/<domain>/<name>/report.html.j2` — `{% extends "reports/_report.master.html.j2" %}`,
   `c.<macro>(...)` calls carrying `d.*`. No arithmetic, no I/O. **The
   `{# purpose: … #}` header is required** — the build checks it.
3. `reports/<domain>/<name>/usage.md` — see the skeleton in `../SKILL.md`.
4. **`python $S/reports/catalog_builder.py`** — nothing calls it for you.
5. `python $S/reports/report_builder.py <name> … --out DIR`

Nothing to register. Building requires the network and `FMP_API_KEY` — see
`../service_providers/REFERENCE.md` for the client and the credential order.

**Nothing runs the catalogue automatically.** There is no CI and no git hook
here, so a report added without step 4 leaves `CATALOG.md` short by one.
`--check` makes that loud:

```bash
python $S/reports/catalog_builder.py --check   # exit 1 if stale, writes nothing
```
