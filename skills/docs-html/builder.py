"""docs-html — builder: compose a document from Jinja templates.

Usage:
    python builder.py new <type> "<title>" [--docs DIR] [--force]
    python builder.py --list
    python builder.py --help

The pieces it composes (all Jinja, all inside this skill directory):

    doc-types/base.html.j2               the shared shell ({% block content %})
    doc-types/<type>/document.html.j2    {% extends base %}; body is ONLY
                                         component-macro calls
    components/<name>/component.html.j2   {% macro <name>(...) %} — the markup

Every component macro is exposed on a single `c` namespace, so templates call
`{{ c.requirement(...) }}` or `{% call c.section(...) %}...{% endcall %}`
without any import lines.

Jinja runs ONLY here, at compose time. The output written to
`<docs>/<slug>.html` is fully rendered, standalone, hand-editable HTML with no
Jinja syntax left.

Single-include design system: every document links exactly one stylesheet
(`css/docs-html.css`) and one script (`js/docs-html.js`) back to this skill;
`base.html.j2` writes both from the resolved `skill_href`. There is no
per-document CSS selection and no publish step — documents reference the shared
assets directly.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import NamedTuple

from jinja2 import Environment, FileSystemLoader

# --------------------------------------------------------------------------
# paths and constants
# --------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = SKILL_DIR / "components"
DOCTYPES_DIR = SKILL_DIR / "doc-types"

# The component gallery: a template that calls every macro, composed into a
# viewable page so it can never drift from the fragments.
SHOWCASE_TEMPLATE = "components/showcase.html.j2"
SHOWCASE_OUTPUT = COMPONENTS_DIR / "showcase.html"

TYPE_NAME_RE = re.compile(r"\{#\s*type-name:\s*(.*?)#\}")       # {# type-name: X #}
BODY_CLASS_RE = re.compile(r"\{#\s*body-class:\s*(.*?)#\}")     # {# body-class: presentation #}

# --------------------------------------------------------------------------
# component catalog — loaded once, exposes every macro on the `c` namespace
# --------------------------------------------------------------------------


class Component(NamedTuple):
    """One entry of components/<name>/component.html.j2."""
    name: str        # directory name, e.g. "kpi-tiles"
    macro: str       # macro/callable name, e.g. "kpi_tiles"
    path: Path       # the component.html.j2 file


def load_components() -> list[Component]:
    """Scan components/ once."""
    components = []
    for directory in sorted(COMPONENTS_DIR.iterdir()):
        markup = directory / "component.html.j2"
        if not (directory.is_dir() and markup.is_file()):
            continue
        components.append(Component(name=directory.name,
                                    macro=directory.name.replace("-", "_"),
                                    path=markup))
    return components


# --------------------------------------------------------------------------
# jinja environment — every component macro exposed on the `c` namespace
# --------------------------------------------------------------------------


def make_env(components: list[Component]) -> Environment:
    """Build the Jinja environment used for composing documents."""
    env = Environment(loader=FileSystemLoader(str(SKILL_DIR)),
                      trim_blocks=True, lstrip_blocks=True,   # tidy whitespace
                      keep_trailing_newline=True, autoescape=False)
    c = SimpleNamespace()
    for component in components:
        module = env.get_template(
            f"components/{component.name}/component.html.j2").module
        if hasattr(module, component.macro):
            setattr(c, component.macro, getattr(module, component.macro))
    env.globals["c"] = c        # templates call {{ c.<macro>(...) }} — no imports
    return env


# --------------------------------------------------------------------------
# doc-type catalog
# --------------------------------------------------------------------------


def doc_types() -> list[str]:
    """All doc-types that have a Jinja template."""
    return sorted(path.name for path in DOCTYPES_DIR.iterdir()
                  if path.is_dir() and (path / "document.html.j2").is_file())


def resolve_type(name: str) -> str:
    """Validate a doc-type name; fail with a hint otherwise."""
    name = name.strip().lower()
    if name not in doc_types():
        raise SystemExit(f"unknown doc-type: {name!r}\n"
                         f"run  python builder.py --list")
    return name


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------


def slug(title: str) -> str:
    """Deterministic filename slug: lowercase, hyphen-separated."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "document"


def git_user() -> str:
    """Document author defaults to git config user.name (empty if no git)."""
    try:
        result = subprocess.run(["git", "config", "user.name"],
                                capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else ""
    except OSError:
        return ""


def cdn_href() -> str:
    """CDN prefix (version-pinned) baked into the head's fallback URLs.

    Read from version.json (the single source of truth) at compose time, so a
    document's fallback is pinned to the design-system version it was authored
    against. The cdn field is a template containing "{version}" (the version
    sits mid-URL when the assets live in a repo subfolder, e.g.
    …/gh/<user>/<repo>@{version}/skills/docs-html); a plain base URL gets
    "@version" appended. Empty while no CDN is configured — the head then
    carries plain local links with no fallback."""
    info = json.loads((SKILL_DIR / "version.json").read_text(encoding="utf-8"))
    cdn, version = info.get("cdn"), info["version"]
    if not cdn:
        return ""
    return cdn.replace("{version}", version) if "{version}" in cdn else f"{cdn}@{version}"


def skill_href(out_dir: Path) -> str:
    """How the composed document links back to this skill's css/ and js/.

    Preferred: THROUGH the consuming project's `.claude/skills/docs-html`
    junction/symlink (out_dir is `<project>/docs`, so `../.claude/...`) — the
    path stays inside the project and is identical on every machine, wherever
    the shared .claudefx clone lives. Otherwise: relative path to the skill
    itself (same drive), or an absolute file:// URL (cross-drive).
    """
    junction = out_dir.parent / ".claude" / "skills" / "docs-html"
    if (junction / "SKILL.md").is_file():
        return "../.claude/skills/docs-html"
    try:
        return os.path.relpath(SKILL_DIR, out_dir).replace(os.sep, "/")
    except ValueError:
        return SKILL_DIR.as_uri()


# --------------------------------------------------------------------------
# compose — the heart of the builder
# --------------------------------------------------------------------------


def compose(type_name: str, title: str, out_dir: Path) -> str:
    """Render one doc-type template into standalone, hand-editable HTML."""
    template_rel = f"doc-types/{type_name}/document.html.j2"
    template_src = (SKILL_DIR / template_rel).read_text(encoding="utf-8")

    # Display name from the template's {# type-name: ... #} comment.
    match = TYPE_NAME_RE.search(template_src)
    display_name = (match.group(1).strip() if match
                    else type_name.replace("-", " ").title())

    # Optional {# body-class: ... #} — presentations set "presentation".
    match = BODY_CLASS_RE.search(template_src)
    body_class = match.group(1).strip() if match else ""

    components = load_components()
    return make_env(components).get_template(template_rel).render(
        title=title,
        type_name=display_name,
        author=git_user(),
        date=datetime.date.today().isoformat(),
        version="0.1",
        skill_href=skill_href(out_dir),
        cdn_href=cdn_href(),
        body_class=body_class)


def compose_showcase() -> str:
    """Render the component gallery from components/showcase.html.j2.

    The gallery calls nearly every macro, so it exercises the whole design
    system on one page. Metadata is fixed (it is the skill's own reference page,
    not a user document)."""
    components = load_components()
    return make_env(components).get_template(SHOWCASE_TEMPLATE).render(
        title="The Design System, Exercised",
        type_name="Component Showcase",
        author="docs-html",
        date=datetime.date.today().isoformat(),
        version="10.0",
        skill_href=skill_href(COMPONENTS_DIR),   # gallery lives in components/
        cdn_href=cdn_href(),
        body_class="")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> int:
    """`new <type> <title>` — compose and write docs/<slug>.html."""
    type_name = resolve_type(args.type)
    out_dir = Path(args.docs).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / f"{slug(args.title)}.html"
    if out.exists() and not args.force:     # never clobber a hand-edited doc
        print(f"refusing to overwrite {out.name} (pass --force)")
        return 1

    out.write_text(compose(type_name, args.title, out_dir), encoding="utf-8")
    print(f"composed: {type_name} -> {out}")
    print("next: fill the placeholders")
    return 0


def cmd_list() -> int:
    """`--list` — the live doc-type catalog."""
    print("doc-types (document.html.j2 present):")
    for name in doc_types():
        print(f"  {name}")
    return 0


def cmd_showcase() -> int:
    """`showcase` — regenerate components/showcase.html from its template."""
    SHOWCASE_OUTPUT.write_text(compose_showcase(), encoding="utf-8")
    print(f"composed showcase -> {SHOWCASE_OUTPUT}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="builder.py",
                                     description="compose docs-html documents (Jinja)")
    parser.add_argument("--list", action="store_true", help="list doc-types")
    sub = parser.add_subparsers(dest="cmd")
    new = sub.add_parser("new", help="compose a new document")
    new.add_argument("type", help="doc-type name")
    new.add_argument("title", help="document title (quote it)")
    new.add_argument("--docs", default="docs", help="output directory (default: ./docs)")
    new.add_argument("--force", action="store_true", help="overwrite an existing document")
    sub.add_parser("showcase", help="regenerate components/showcase.html")

    args = parser.parse_args(argv)
    if args.list:
        return cmd_list()
    if args.cmd == "new":
        return cmd_new(args)
    if args.cmd == "showcase":
        return cmd_showcase()
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
