# aifx-finance

**A versioned toolbox for Claude Code — skills in one public repo, dropped into
any project.**

Today that is one skill, `finance-reports`: a component library of 109
components, each with a built showcase page, and the report engine that builds
documents out of them. `.claude/agents/` exists and is empty — the shelf is
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

### Testing a report

Each report has a `report_test.py` **beside it** — it builds the report for real
and then checks the file:

```powershell
python .claude/skills/finance-reports/reports/report_test_runner.py --list
python .claude/skills/finance-reports/reports/report_test_runner.py financial-profile
python .claude/skills/finance-reports/reports/report_test_runner.py --all
```

Tests are **found, not registered** — a directory holding `report.html.j2` is a
report, and one that also holds `report_test.py` has a test — so adding one
means adding a file. Because the test ships with the skill, a **linked** install
can be tested in place, which is the quickest way to find out whether that
project's `environment.json` and `secrets.<env>.json` resolve.

**A bare run does nothing**: it prints what exists and totals what it would
cost, because every test builds against the live API and nothing is cached. Ten
reports is ~130 calls of real quota, so the selection has to be said out loud.
The built page lands in **`report_test_output/` beside the report** and stays
there — open it, since charts draw at view time and no check can judge one. That
folder is tracked but always empty: a `.gitkeep`, and a `.gitignore` pair that
covers every report, so nothing built is ever committed or published.

It is written to disk rather than held in memory because the destination is part
of what is tested — the page's local asset links are computed relative to it.
Beside the report rather than the system temp directory for the same reason: on
Windows temp is on another drive, no relative path exists between them, and the
page would silently fall back to linking the CDN alone.

If you **copy** the skill into your own project, add those two lines to that
project's `.gitignore` yourself, exactly as you would for `secrets.*.json`.

It exits 0 or 1 and needs no arguments: the symbol and the peer group are
declared in the file, because a test whose inputs are typed each time is a test
that was run differently the last time somebody ran it.

The build already asserts its own arithmetic, so the test adds what only the
finished page can show, in two tiers:

- **is it well-formed** — every chart spec survives `JSON.parse`, both asset
  halves resolve and the CDN half pins the *current* version, every in-page link
  lands on a real section id, no half-rendered markup reached the file
- **does it carry data** — no chart is an empty frame, no table is a header over
  nothing, every declared section has content, every requested symbol appears,
  and no section is mostly blanks

The second tier exists because the first cannot fail on an empty page. If an
endpoint returns a 200 with nothing in it, the derivation produces zeros — and
its identities still hold, since `0 + 0 == 0` satisfies `cost + gross ==
revenue`. Every structural check passes and the report renders beautifully with
flat lines and no numbers.

Tests live beside `.claude/` rather than inside it for the same reason the
config does: they belong to this project, not to a skill copied out of it. A
passing run still does not mean the page is right — charts draw at view time, so
**open it**.

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
5.0.0. A changed CLI did, at 7.0.0 — `--env` was dropped, no document was
affected at all, and it was still a break for anyone with the old command in a
script. **A release is major if a thing that worked stops working**, whether
the thing is a page, a link, or a line someone typed.

**Upgrading across a major is opt-in by construction.** An existing page keeps
pointing at the tag it was built against and keeps rendering; it moves only
when you regenerate it. Read the tag message — `git show v8.0.0` — for what
broke and what to do about it.

---

## License

[MIT](LICENSE) — use it, copy it, ship it.
