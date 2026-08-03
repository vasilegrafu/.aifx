# aifx-finance

**A versioned toolbox for Claude Code — skills in one public repo, dropped into
any project.**

Today that is one skill, `finance-reports`: a component library — every
component with a built showcase page — and the report engine that builds
documents out of them. `components/CATALOG.md` is the current index and states
the count; it is generated, so it cannot fall behind the tree. `.claude/agents/` exists and is empty — the shelf is
declared, nothing is on it yet.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Installation

### Option A — copy (simplest)

Grab any skill folder and paste it into your project. The MIT license allows
exactly this — take it, keep it, modify it.

```
<your-project>/.claude/skills/<skill-name>/   ← copied from aifx-finance/.claude/skills/<skill-name>/
```

Done. Claude Code discovers it next session. Your copy is frozen — it never
changes unless you update it yourself.

### Option B — clone once, link everywhere (always updatable)

One shared clone on your machine serves ALL your projects through links.
Nothing you already have is touched — your own skills stay beside the links.

**1. Clone** once, anywhere (a good spot: next to your projects):

```bash
git clone https://github.com/vasilegrafu/aifx-finance.git
```

**2. Link each skill you want** into every project's `.claude/skills`,
next to your own:

```bat
:: Windows (junction — no admin rights needed)
mklink /J <project>\.claude\skills\<skill-name> <path-to>\aifx-finance\.claude\skills\<skill-name>
```

```bash
# macOS / Linux (symlink)
ln -s <path-to>/aifx-finance/.claude/skills/<skill-name> <project>/.claude/skills/<skill-name>
```

**3. Verify** — open Claude Code in the project: the skill appears in its
skills list.

**Linking is the better option if you intend to run the builders.** A linked
skill resolves back through the junction into this clone, so it reads the
clone's `environment.json`, `config.<env>.json` and `secrets.<env>.json`: one
set of credentials on the machine, and **nothing lands in your project**. A
copied skill is a real file tree and needs its own beside `.claude/` — in which
case add `secrets.*.json` to that project's `.gitignore` yourself, since this
repo's cannot reach it.

**Update later** — one pull updates every project at once:

```bash
git -C <path-to>/aifx-finance pull            # latest
git -C <path-to>/aifx-finance checkout v8.0.0 # or pin a released version
```

What a version number promises is in [Versioning](#versioning) below — worth
reading before you pull across a major.

### Check the install — `status.py`

Appearing in the skills list means Claude Code found it. It does not mean it can
build anything. One command says what is actually there, for either install:

```bash
python .claude/skills/finance-reports/status.py
```

```
finance-reports  <path>\aifx-finance\.claude\skills\finance-reports

components  …
  charts-apache-echarts                   …
  diagrams-mermaid                        …
  …
reports     …
version     …        every generated page pins this at BUILD time

checks
  usage.md skeleton                     ok
  class prefixes own their directory    ok
  every class in markup is reachable    ok
  components/CATALOG.md                 ok
  reports/CATALOG.md                    ok
  showcase pages                        ok
  bundles load every module             ok
```

The counts are elided above on purpose: `status.py` reads them off the tree, so
printing them here would only record what was true the day this was typed.

Two things to read there. **The path on the first line tells you which install
you got** — it resolves through a junction, so a *linked* skill prints the
clone's path and a *copied* one prints your project's. **The version line is the
copy path's usual failure**: a copied skill needs its own `version.json` beside
`.claude/`, and without one it cannot render a single page. `status.py` says so
in a sentence instead of a traceback.

The checks that regenerate something to compare against it — both catalogues and
every showcase page — render templates, so they need Jinja: run it with the venv
from [Environment](#1-environment) below. On an interpreter without it they
report `NOT RUN` and name the missing library rather than claiming anything is
stale, because being sent to regenerate a catalogue that was already current is
worse than being told nothing. The rest are pure file reading and always run.

`--check` exits 1 if any of them fails — a stale catalogue or showcase page, a
`usage.md` off the skeleton, a class whose prefix does not match the directory
it lives in or that no stylesheet can reach, or a `css/bundle.css` or
`js/bundle.js` that has stopped loading a file beside it. Useful in a pre-commit
hook if you intend to *modify* the skill; not needed to use it.

---

## Building a report

The `finance-reports` skill generates standalone HTML from live market data.
Installing the skill (above) is enough for Claude Code to *use* it; running the
builders yourself needs four things.

### 1. Environment

```powershell
python -m venv .venv
.venv\Scripts\activate                    # PowerShell
# source .venv/bin/activate               # macOS / Linux
pip install -r requirements.txt
```

Two libraries: Jinja renders every template, httpx is the only thing that
touches the network. Nothing here builds the published CSS or JS — those are
served raw from the git tag.

### 2. Config — tracked

`config.dev.json` and `config.prod.json` are already in the repo.
They hold what is not secret:

```json
{
  "service_providers": {
    "fmp": {
      "api_url": "https://financialmodelingprep.com/stable"
    }
  }
}
```

### 3. Secrets — never tracked

Create `secrets.dev.json` at the repo root by hand:

```json
{
  "fmp": {
    "api_key": "<your-fmp-api-key>"
  }
}
```

Add `secrets.prod.json` in the same shape if you use a separate production key.

**There is deliberately no `secrets.example.json` to copy.** `.gitignore`
matches `secrets.*.json` with **no exception**, so nothing by that name can
ever be staged. A tracked template would need a negation in `.gitignore`, and a
negation is one mis-ordered line away from publishing a key — in a repository
that is public *and* served by jsDelivr, where anything committed is fetchable
at a URL by anyone who guesses the path. Writing four lines of JSON is cheaper
than that risk.

The split is per **file**, not per field: config is tracked, secrets are not,
so "is this safe to commit?" is decided once for the file rather than judged
every time someone adds a field. An `api_key` in `config.<env>.json` is
rejected at build time for that reason.

In CI, set `FMP_API_KEY` instead — it wins over the file and needs no file at
all.

### 4. Run

```powershell
python .claude/skills/finance-reports/reports/report_builder.py `
    financial-profile AMD --peers NVDA,INTC --out ./some/directory
```

`--out` is required and has no default: the page's local asset links are
computed relative to wherever it is written, so the destination is a decision.

`--asset-bundles` says which bundle the page links, and **defaults to `cdn`** —
the pinned version, so the page renders anywhere: copied, mailed, opened from a
download folder. Pass `local` to point it at this tree relative to `--out`
instead, which is live against whatever you have just edited and broken the
moment the file is moved. The default goes to the portable one because `cdn`
works everywhere `local` does and more, so it cannot be silently wrong.

**The environment is declared, not passed.** `environment.json` sits at the
repo root and is tracked, so a fresh clone starts somewhere:

```json
{ "environment": "dev" }
```

Or set `ENVIRONMENT` in the shell, which wins over the file. There is **no
flag and no default**: a flag would reach only builds driven through
`report_builder.py` while anything importing the client directly still needs
the declaration, and it cannot be inherited by a shell another tool spawned —
which is where builds usually run.

It is deliberately **not** called `.env`. That name is where every tutorial
tells you to put an API key, and this file is tracked; a name nobody reaches
for by reflex is a name that can be committed safely.

One declaration picks `config.<env>.json` *and* `secrets.<env>.json` together,
so a run cannot read dev settings against a prod key. Every build says what it
resolved, and from where, before spending ~13 API calls:

```
environment: dev (from D:\...\environment.json)   config.dev.json, key from D:\...\secrets.dev.json
fetching ...
deriving and asserting ...
<path to the written file>
```

```powershell
python .claude/skills/finance-reports/reports/report_builder.py financial-profile --help
```

### Every report validates itself

There is no separate test to remember to run. `build()` checks the page it just
rendered and **writes what it found into the top of the document**, above the
cover — so the findings arrive where you already have to look, since charts draw
at view time and the page has to be opened anyway.

A report that left this tree therefore carries its own warning. That matters
more than the developer case: a reader cannot otherwise tell a healthy page from
one whose endpoint returned nothing, because `0 + 0 == 0` satisfies every
identity the controller asserts.

- **errors** — the page is broken: a chart spec that will not parse, an asset
  half that does not resolve, a link to an id nothing carries, unrendered
  template syntax. Independent of which company was asked for.
- **warnings** — the page rendered and its content is thin: an empty chart, a
  table with no rows, a section mostly blank, a requested symbol appearing
  nowhere. Usually a sparse subject, so they are shown and fail nothing.

Neither raises. The page has already cost ~13 live calls and is written either
way — a page you can open beats an exception. A clean build carries the
all-clear as an HTML comment rather than a box, so *"validated and clean"* is
never confused with *"validation never ran"*.

The checks live in `reports/_report_validation.py`, one home for all reports.
What each report expects of itself — its sections, its domain class prefix, the
symbols the request named — is declared on its controller beside `TITLE`.

That is why the warnings exist at all: an endpoint returning 200 with an empty
body passes every structural check, and the report renders beautifully with flat
lines and no numbers. The warnings are what measure that.

**A clean report is valid, not correct.** Charts draw at view time and nothing
in the build has seen one, so **open it**.

---

## Versioning

**One version governs the whole repository** — every skill under
`.claude/skills/`, the CSS, the JS, all of it. The single source of truth is
`version.json` at the root; no version number lives anywhere else. A skill that
versioned itself would let two skills in one clone disagree about which CSS
they were written against, and every generated page links that CSS by tag.

Each release is the git tag `v<version>`, and jsDelivr serves it at
`…/aifx-finance@<version>/.claude/skills/<skill>/…`.

**A published version is immutable.** Any change, however small, is a new
version — never a re-tag. Documents that have left this tree link their assets
by tag, so moving one would silently restyle pages nobody can find any more.

| bump | what changed | what it costs you |
|---|---|---|
| **PATCH** | a visual fix, no markup contract change | nothing — safe for every existing document |
| **MINOR** | additive: a new component, style, JS feature, or skill | nothing — old documents render unchanged |
| **MAJOR** | a markup contract changed, a skill was removed, **or a published command changed shape** | documents must opt in; a linked directory can vanish; a command from the previous release may stop working |

The MAJOR clause covers three different kinds of breakage because each one
arrived and found the contract silent about it. A removed skill did, before
5.0.0. A changed CLI did, at 8.0.0 — `--env`, required since 6.0.0, was dropped;
no document was affected at all, and it was still a break for anyone with the
old command in a script. **A release is major if a thing that worked stops
working**, whether the thing is a page, a link, or a line someone typed.

**Upgrading across a major is opt-in by construction.** An existing page keeps
pointing at the tag it was built against and keeps rendering; it moves only
when you regenerate it. Read the tag message — `git show v8.0.0` — for what
broke and what to do about it.

---

## License

[MIT](LICENSE) — use it, copy it, ship it.
