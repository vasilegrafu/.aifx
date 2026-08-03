# CLAUDE.md

Operational context for this repository. The **design** of the skill is in
`.claude/skills/finance-reports/SKILL.md` and its REFERENCEs — this file is
only what a session needs before touching anything, and it deliberately does
not repeat them.

## Run things with the venv

```bash
./.venv/Scripts/python.exe <script>          # NOT bare `python`
```

Bare `python` on this machine has no `jinja2` and fails on the first import.

## This repository is PUBLIC and served by a CDN

jsDelivr publishes every tag at `cdn.jsdelivr.net/gh/vasilegrafu/aifx-finance@<version>/…`,
**including dot-directories** — `.claude/skills/…` resolves. Anything committed
is fetchable by anyone who guesses the path.

- `secrets.*.json` is gitignored with **no exception and no negation**, and
  there is deliberately no `secrets.example.json` template.
- `config.<env>.json` is **tracked** and must never hold an `api_key`.
- The environment file is deliberately **not** `.env`, because that is where
  every tutorial says to put a key and this one is tracked.
- This repo is committed with a blanket `git add .`, so no file holding a key
  may ever be trackable — not even briefly.

## Ask before committing, and again before pushing

Do the work and leave it uncommitted unless asked. A push is separate from a
commit and needs its own go-ahead: **a published tag is immutable**, because
documents that have left this tree link their assets by tag.

## Version discipline — bump BEFORE you rebuild

Every generated page pins its asset version **at build time**. So the order is:

```bash
# 1. edit version.json
./.venv/Scripts/python.exe .claude/skills/finance-reports/components/showcase_builder.py --all
./.venv/Scripts/python.exe .claude/skills/finance-reports/components/catalog_builder.py
./.venv/Scripts/python.exe .claude/skills/finance-reports/components/showcase_builder.py --check
```

Rebuild first and the pages pin the old version. **Any edit under `css/` or
`js/` invalidates every showcase page at once** — `--check` is what turns
"did I remember?" into an exit code.

The semver rule is in `README.md`: a release is MAJOR if **a thing that worked
stops working**, whether the thing is a page, a link, or a line someone typed.

## Before saying a page is fine

A clean build proves the markup is valid. It does not prove the page is right —
three defects have shipped past one, and **nothing here renders a page**, so
overflow, out-of-track bars, clipping and glued text are found only by looking:

- **Serve it over `http://`** — `python -m http.server 8000`, then open the
  page. Not `file://`: a showcase links its assets relatively and a report
  links them relative to where it was written.
- **Look at it.** Charts draw at view time, so a malformed spec is invisible in
  the HTML. ECharts here uses the **SVG renderer** — counting `<canvas>`
  elements proves nothing.

## Report output

Reports need the network and a real key; there is no offline mode and nothing
is cached. `--out` and `--peers` have **no defaults on purpose** — ask rather
than choose. A built report carries live market data and differs on every run,
so it is an artifact: never commit one, wherever it was written.

## Every report validates itself, and says so on its own first screen

There is **no report test and no test runner**. `build()` checks the page it
just rendered, in `reports/_report_validation.py`, and renders what it found
into the top of the document — above the cover, before anything else.

That costs nothing. The test this replaced built a report *of its own* to check,
so confidence in a report you wanted cost twice the quota and validated the
wrong page. Now the page that gets checked is the page you are holding, every
time, for every symbol.

**Two severities, and the line matters:**

- **error** — the page is BROKEN: a spec that will not `JSON.parse`, an asset
  half that does not resolve, a link to an id nothing carries, a Jinja
  delimiter that reached the file, a declared section that never rendered, the
  pre-6.0.0 `investing-` prefix. None of these depend on the company asked for.
- **warning** — the page rendered and its CONTENT is thin: an empty chart, a
  table with no rows, a section mostly blank, a requested symbol that appears
  nowhere. Against arbitrary input these usually mean the data is sparse, so
  they are said loudly and fail nothing.

Without that split a legitimately sparse company would fail its own report.

**Validation never raises and never withholds the page.** By the time it runs,
the file has cost ~13 live calls; it is written whatever was found. Errors and
warnings also print on the way out, so a caller building several does not have
to open each one.

**A clean build leaves an HTML comment, not a box** — `<!-- validated: N
check(s), 0 error(s) … -->`. An absent banner cannot tell *"validated and
clean"* from *"validation never ran"*.

**Assertions passing does not mean data arrived.** An endpoint returning a 200
with an empty body yields zeros, and `0 + 0 == 0` satisfies `cost + gross ==
revenue` — the arithmetic holds, all 48 `READS` names exist, and the page
renders flat and empty. That is what the warnings measure, and they measure per
SECTION: one dead endpoint out of seven moves the whole page only to ~26% blank,
which no page-level threshold catches without failing good markup.

Green still means the page is valid, not that it is correct. Charts draw at view
time and nothing here has seen one. **Open it.**
