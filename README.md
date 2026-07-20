# .claudefx

**A versioned toolbox for Claude Code — skills and agents in one public repo,
dropped into any project.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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

### Option B — clone once, link everywhere (always updatable)

One shared clone on your machine serves ALL your projects through links.
Nothing you already have is touched — your own skills stay beside the links.

**1. Clone** once, anywhere (a good spot: next to your projects):

```bash
git clone https://github.com/vasilegrafu/.claudefx.git
```

**2. Link each skill you want** into every project's `.claude/skills`,
next to your own:

```bat
:: Windows (junction — no admin rights needed)
mklink /J <project>\.claude\skills\<skill-name> <path-to>\.claudefx\skills\<skill-name>
```

```bash
# macOS / Linux (symlink)
ln -s <path-to>/.claudefx/skills/<skill-name> <project>/.claude/skills/<skill-name>
```

**3. Verify** — open Claude Code in the project: the skill appears in its
skills list.

**Update later** — one pull updates every project at once:

```bash
git -C <path-to>/.claudefx pull            # latest
git -C <path-to>/.claudefx checkout v1.1.0 # or pin a released version
```

## License

[MIT](LICENSE) — use it, copy it, ship it.
