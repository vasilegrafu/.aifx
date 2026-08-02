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
- `git.commit&push.bat` runs `git add .`, so no file holding a key may ever be
  trackable — not even briefly.

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
./.venv/Scripts/python.exe .claude/skills/finance-reports/components/showcase_audit.py
```

Rebuild first and the pages pin the old version. **Any edit under `css/` or
`js/` invalidates every one of the 109 pages at once** — `--check` is what turns
"did I remember?" into an exit code.

The semver rule is in `README.md`: a release is MAJOR if **a thing that worked
stops working**, whether the thing is a page, a link, or a line someone typed.

## Before saying a page is fine

A clean build proves the markup is valid. It does not prove the page is right —
three defects have shipped past one. Two checks catch different things and
neither replaces the other:

- **`showcase_audit.py`** — generates a page; serve the repo and open it. Finds
  overflow, out-of-track percentages, clipping, glued text. Cannot see a chart
  that is merely wrong.
- **Look at it.** Charts draw at view time, so a malformed spec is invisible in
  the HTML. ECharts here uses the **SVG renderer** — counting `<canvas>`
  elements proves nothing.

## Report output

Reports need the network and a real key; there is no offline mode and nothing
is cached. `--out` and `--peers` have **no defaults on purpose** — ask rather
than choose. Output under `.claude_testing_scenarios/` is gitignored: it
carries live market data and differs on every run.
