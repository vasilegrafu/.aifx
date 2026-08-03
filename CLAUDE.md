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

Each report has a `report_test.py` **beside it** that builds it for real and
then checks the file:

```bash
R=.claude/skills/finance-reports/reports/report_test_runner.py
./.venv/Scripts/python.exe $R --list          # costs nothing
./.venv/Scripts/python.exe $R financial-profile
./.venv/Scripts/python.exe $R --all
```

**A bare run does nothing on purpose** — it lists what exists and totals the
quota it would spend. Tests are found, not registered: a directory holding
`report_test.py` has a test, and its `CALLS = <n>` is what the runner adds up
without importing anything.

**The page lands in `report_test_output/` beside the report** and stays there —
open it, because a chart draws at view time and no check here can see one.

That folder is **tracked but always empty**: a `.gitkeep`, plus one pair of
rules in `.gitignore` covering every report present and future.

```
**/report_test_output/*
!**/report_test_output/.gitkeep
```

The `**/` is load-bearing — without it the pattern anchors to the repo root and
silently ignores nothing four levels down. **Verify with `git check-ignore`, not
by eye**, whenever these lines are touched: a published page is a page that was
committed, and this is the rule standing between the two. A copied skill needs
the same lines in the consuming project.

**Not temp**, which was tried: it is on `C:` while this repo is on `D:`, and
with no relative path between drives `local_href` comes out empty — so the page
links the CDN alone and renders unstyled against a tag that may not be pushed.

**It spends ~13 live API calls every time** — there is nothing to cache and no
fixture, so don't run it in a loop while iterating. Its ten checks answer two
questions the build cannot:

- **well-formed** — chart specs survive `JSON.parse`, both asset halves resolve,
  the CDN half pins the *current* `version.json` (which is how the
  bump-before-rebuild rule above gets enforced rather than remembered), in-page
  links land on real ids, no half-rendered markup
- **carries data** — no empty chart, no header-over-nothing table, no bare
  section, every requested symbol present, no section mostly blank

**Assertions passing does not mean data arrived.** An endpoint that returns a
200 with an empty body yields zeros, and `0 + 0 == 0` satisfies `cost + gross ==
revenue` — so the arithmetic holds, all 48 `READS` names exist, and the page
renders flat and empty. That is what the second tier is for, and it measures
per SECTION: one dead endpoint out of seven moves the whole page only to ~26%
blank, which no page-level threshold can catch without failing good markup.

It is the same story as the showcase audit: green means the page is valid, not
that it is correct. **Open it.**
