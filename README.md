# aifx-finance

**A versioned toolbox for Claude Code — skills and agents in one public repo,
dropped into any project.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Installation

### Option A — copy (simplest)

Grab any skill folder and paste it into your project. The MIT license allows
exactly this — take it, keep it, modify it.

```
<your-project>/.claude/skills/<skill-name>/   ← copied from aifx-finance/skills/<skill-name>/
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
mklink /J <project>\.claude\skills\<skill-name> <path-to>\aifx-finance\skills\<skill-name>
```

```bash
# macOS / Linux (symlink)
ln -s <path-to>/aifx-finance/skills/<skill-name> <project>/.claude/skills/<skill-name>
```

**3. Verify** — open Claude Code in the project: the skill appears in its
skills list.

**Update later** — one pull updates every project at once:

```bash
git -C <path-to>/aifx-finance pull            # latest
git -C <path-to>/aifx-finance checkout v1.1.0 # or pin a released version
```

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

`config/config.dev.json` and `config/config.prod.json` are already in the repo.
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
every time someone adds a field. An `api_key` in `config/` is rejected at build
time for that reason.

In CI, set `FMP_API_KEY` instead — it wins over the file and needs no file at
all.

### 4. Run

```powershell
python skills/finance-reports/reports/report_builder.py `
    financial-profile AMD --peers NVDA,INTC --env dev --out ./some/directory
```

**`--env` and `--out` are both required and neither has a default.** `--env`
picks `config.<env>.json` *and* `secrets.<env>.json` together, so a run cannot
read dev settings against a prod key; `--out` has no default because the page's
local asset links are computed relative to wherever it is written. Every build
says what it resolved before spending ~13 API calls:

```
environment: dev   (config.dev.json, key from secrets.dev.json)
fetching ...
deriving and asserting ...
<path to the written file>
```

Runnable scenarios live in `skills_testing_scenarios/`, each stating its
command, what must be true of the output, and what each failure mode points at.

```powershell
python skills/finance-reports/reports/report_builder.py financial-profile --help
```

## License

[MIT](LICENSE) — use it, copy it, ship it.
