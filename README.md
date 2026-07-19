# .claudefx

**A versioned toolbox for Claude Code — skills and agents in one public repo,
dropped or mounted into any project.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tag](https://img.shields.io/github/v/tag/vasilegrafu/.claudefx?label=version)](https://github.com/vasilegrafu/.claudefx/tags)

---

## Installation

### Option A — copy (simplest)

Grab any skill folder and paste it into your project. The MIT license allows
exactly this — take it, keep it, modify it.

```
<your-project>/.claude/skills/<skill-name>/   ← copied from .claudefx/skills/<skill-name>/
```

Done. Claude Code discovers it next session. Your copy is frozen — it never
changes unless you update it yourself.

### Option B — mount (tracked, always updatable)

Mount the repo once, then *link* the assets you want beside your own skills.
Nothing you already have is touched.

**1. Mount** (inside a git project; a plain `git clone` works too):

```bash
git submodule add https://github.com/vasilegrafu/.claudefx.git .claudefx
```

**2. Link each skill you want** into `.claude/skills`, next to your own:

```bat
:: Windows (junction — no admin rights needed)
mklink /J .claude\skills\<skill-name> .claudefx\skills\<skill-name>
```

```bash
# macOS / Linux (symlink)
ln -s ../../.claudefx/skills/<skill-name> .claude/skills/<skill-name>
```

**3. Verify** — open Claude Code in the project: the skill appears in its
skills list.

**Update later**:

```bash
git -C .claudefx pull            # latest
git -C .claudefx checkout v1.0.0 # or pin a released version
```

## Requirements

What you need depends on how much you use — from nothing extra at all, up to a
small Python toolchain for the generator-based skills.

### 1. Claude Code — always

The host: skills and agents are instructions *for* Claude Code, so without it
this repository is just text.

```bash
npm install -g @anthropic-ai/claude-code
```

Or use the desktop app / IDE extension — any form works the same.

### 2. git — for Option B (and updates)

Why: mounting the repo as a submodule, pulling new versions, and pinning a
release are all git operations. (Option A — plain copying — technically needs
no git at all.)

- **Windows**: `winget install Git.Git` or [git-scm.com](https://git-scm.com)
- **macOS**: `xcode-select --install` or `brew install git`
- **Linux**: `sudo apt install git` (or your distro's package manager)

### 3. Python 3.10+ and Jinja2 — for generator-based skills

Why: some skills don't just instruct Claude — they ship a small **builder**
that composes files from templates (Jinja2 is the template engine). The
builder runs only at *creation* time; the generated output needs no Python
ever again.

- **Windows**: `winget install Python.Python.3.12` or [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python`
- **Linux**: `sudo apt install python3 python3-pip`

Then the one library:

```bash
pip install jinja2
```

### 4. A browser + internet — for web-rendered output

Why: skills that produce HTML (documents, diagrams) render in any modern
browser and load their engines (diagram rendering, syntax coloring) from
pinned CDNs at view time. Nothing to install — but fully offline viewing
shows content without those enhancements.

### Summary

| You want to… | Claude Code | git | Python + Jinja2 | Browser |
|---|:-:|:-:|:-:|:-:|
| Copy a skill and use it (Option A) | ✓ | — | — | — |
| Mount + link, stay updatable (Option B) | ✓ | ✓ | — | — |
| Run a skill's generator/builder | ✓ | — | ✓ | — |
| View generated HTML output | — | — | — | ✓ |

Each skill states its exact needs in its own folder — the list above is the
worst case.

## License

[MIT](LICENSE) — use it, copy it, ship it.
