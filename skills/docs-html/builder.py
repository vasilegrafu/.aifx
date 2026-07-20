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

# Showcases: living reference pages in showcases/. Each showcases/<name>.html.j2
# composes to showcases/<name>.html — the component gallery is component.html.j2,
# and more showcases can be dropped in the same folder.
SHOWCASES_DIR = SKILL_DIR / "showcases"

# CATALOG.md — the generated quick-reference: every component's call signature
# and every doc-type's purpose, pulled straight from source so it can't drift.
CATALOG_OUTPUT = SKILL_DIR / "CATALOG.md"

TYPE_NAME_RE = re.compile(r"\{#\s*type-name:\s*(.*?)#\}")       # {# type-name: X #}
TITLE_RE = re.compile(r"\{#\s*title:\s*(.*?)#\}")              # {# title: X #}
BODY_CLASS_RE = re.compile(r"\{#\s*body-class:\s*(.*?)#\}")     # {# body-class: presentation #}
PURPOSE_RE = re.compile(r"\{#\s*purpose:\s*(.*?)\s*#\}")        # {# purpose: X #}
MACRO_SIG_RE = re.compile(r"\{%\s*macro\s+\w+\s*\((.*?)\)\s*%\}", re.S)

# Presentation order for CATALOG.md (unknown keys append alphabetically).
CATEGORY_ORDER = ["structure", "content", "lists", "callouts", "blocks",
                  "business", "front-back-matter", "diagrams", "math"]
DOMAIN_ORDER = ["general", "software", "finance", "investing", "accounting",
                "research", "economics", "engineering", "tools", "fallback"]

# --------------------------------------------------------------------------
# component catalog — loaded once, exposes every macro on the `c` namespace
# --------------------------------------------------------------------------


class Component(NamedTuple):
    """One entry of components/<name>/component.html.j2."""
    name: str        # directory name, e.g. "kpi-tiles"
    macro: str       # macro/callable name, e.g. "kpi_tiles"
    path: Path       # the component.html.j2 file


def load_components() -> list[Component]:
    """Scan components/ once, recursively.

    components/ is organized in CATEGORY folders (structure/, lists/, blocks/,
    business/, …) that exist purely for humans — a component's identity stays
    its own folder name (macro = name with - -> _), so category moves never
    touch templates. Names must be unique across categories."""
    components, seen = [], {}
    for markup in sorted(COMPONENTS_DIR.rglob("component.html.j2")):
        name = markup.parent.name
        if name in seen:
            raise SystemExit(f"duplicate component name: {name!r} "
                             f"({seen[name]} and {markup.parent})")
        seen[name] = markup.parent
        components.append(Component(name=name,
                                    macro=name.replace("-", "_"),
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
            component.path.relative_to(SKILL_DIR).as_posix()).module
        if hasattr(module, component.macro):
            setattr(c, component.macro, getattr(module, component.macro))
    env.globals["c"] = c        # templates call {{ c.<macro>(...) }} — no imports
    return env


# --------------------------------------------------------------------------
# doc-type catalog
# --------------------------------------------------------------------------


def doc_type_dirs() -> dict[str, Path]:
    """Every doc-type folder, discovered recursively: name -> directory.

    doc-types/ is organized in DOMAIN folders (general/, software/, finance/,
    …) that exist purely for humans — the type's identity stays its own folder
    name, so `new investment-thesis` works regardless of which domain holds
    it. Names must therefore be unique across all domains."""
    dirs: dict[str, Path] = {}
    for template in sorted(DOCTYPES_DIR.rglob("document.html.j2")):
        name = template.parent.name
        if name in dirs:
            raise SystemExit(f"duplicate doc-type name: {name!r} "
                             f"({dirs[name]} and {template.parent})")
        dirs[name] = template.parent
    return dirs


def doc_types() -> list[str]:
    """All doc-type names that have a Jinja template."""
    return sorted(doc_type_dirs())


def resolve_type(name: str) -> str:
    """Validate a doc-type name; fail with a hint otherwise."""
    name = name.strip().lower()
    if name not in doc_type_dirs():
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
    directory = doc_type_dirs()[type_name]
    template_rel = (directory.relative_to(SKILL_DIR) / "document.html.j2").as_posix()
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


def showcase_templates() -> list[Path]:
    """Every showcase source: showcases/<name>.html.j2."""
    return sorted(SHOWCASES_DIR.glob("*.html.j2"))


def compose_showcase(template: Path) -> str:
    """Render one showcase (showcases/<name>.html.j2). A showcase is the skill's
    own reference page — it exercises real macros against local assets, never a
    user document. Title/type-name come from `{# title #}` / `{# type-name #}`
    headers (falling back to the file stem)."""
    text = template.read_text(encoding="utf-8")
    stem = template.name[:-len(".html.j2")]
    tn = TYPE_NAME_RE.search(text)
    ti = TITLE_RE.search(text)
    type_name = tn.group(1).strip() if tn else stem
    title = ti.group(1).strip() if ti else type_name
    rel = template.relative_to(SKILL_DIR).as_posix()
    return make_env(load_components()).get_template(rel).render(
        title=title,
        type_name=type_name,
        author="docs-html",
        date=datetime.date.today().isoformat(),
        version="",
        skill_href=skill_href(SHOWCASES_DIR),   # showcases live one level deep
        cdn_href="",   # skill-internal page: ALWAYS local relative refs
        cat_blurb=category_blurbs(),   # single source: the category usage.md blurbs
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
    """`--list` — the live doc-type catalog, grouped by domain folder."""
    by_domain: dict[str, list[str]] = {}
    for name, directory in doc_type_dirs().items():
        domain = directory.parent.name if directory.parent != DOCTYPES_DIR else "(root)"
        by_domain.setdefault(domain, []).append(name)
    for domain in sorted(by_domain):
        print(f"{domain}:")
        for name in sorted(by_domain[domain]):
            print(f"  {name}")
    return 0


def cmd_showcase() -> int:
    """`showcase` — regenerate every showcases/<name>.html from its template."""
    templates = showcase_templates()
    if not templates:
        print(f"no showcases found in {SHOWCASES_DIR}")
        return 1
    for template in templates:
        output = template.with_suffix("")          # <name>.html.j2 -> <name>.html
        output.write_text(compose_showcase(template), encoding="utf-8")
        print(f"composed showcase -> {output}")
    return 0


# --------------------------------------------------------------------------
# CATALOG.md — the generated quick-reference
# --------------------------------------------------------------------------


def _param_names(signature: str) -> str:
    """A macro's parameter NAMES only — defaults dropped for a clean reference:
    `id="REQ-1", given=[]` -> `id, given`. (No current default holds a comma.)"""
    names = [p.split("=", 1)[0].strip()
             for p in signature.split(",") if p.strip()]
    return ", ".join(names)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _purpose(text: str) -> str:
    m = PURPOSE_RE.search(text)
    return m.group(1).strip() if m else ""


def _ordered(keys, order: list[str]) -> list[str]:
    """`order` first (those present), then any remaining keys alphabetically."""
    present = set(keys)
    return [k for k in order if k in present] + sorted(present - set(order))


def _blurb(text: str) -> str:
    """The one-line blurb of a category/domain usage.md: the first content
    paragraph — first non-blank line that is not a Markdown heading."""
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def category_blurbs() -> dict[str, str]:
    """category folder name -> blurb, from components/<category>/usage.md."""
    return {p.parent.name: _blurb(_read(p))
            for p in COMPONENTS_DIR.glob("*/usage.md")}


def domain_blurbs() -> dict[str, str]:
    """domain folder name -> blurb, from doc-types/<domain>/usage.md."""
    return {p.parent.name: _blurb(_read(p))
            for p in DOCTYPES_DIR.glob("*/usage.md")}


def _component_call(comp: Component) -> str:
    """The exact call form for a component: `{{ c.x(...) }}` for a leaf,
    `{% call c.x(...) %}…{% endcall %}` for a container (detected via caller())."""
    text = _read(comp.path)
    m = MACRO_SIG_RE.search(text)
    params = _param_names(m.group(1)) if m else ""
    if "caller()" in text:
        return f"{{% call c.{comp.macro}({params}) %}}…{{% endcall %}}"
    return f"{{{{ c.{comp.macro}({params}) }}}}"


def compose_catalog() -> str:
    """Render CATALOG.md from source: component call signatures + doc-type
    purposes, both grouped and pulled from the templates themselves so the file
    can never drift from what actually exists."""
    components = load_components()
    cat_blurb, dom_blurb = category_blurbs(), domain_blurbs()
    by_cat: dict[str, list[tuple[str, str]]] = {}
    for comp in components:
        category = comp.path.parent.parent.name
        by_cat.setdefault(category, []).append(
            (_component_call(comp), _purpose(_read(comp.path))))

    types = doc_type_dirs()
    by_dom: dict[str, list[tuple[str, str]]] = {}
    for name, directory in types.items():
        domain = directory.parent.name if directory.parent != DOCTYPES_DIR else "(root)"
        purpose = _purpose(_read(directory / "document.html.j2"))
        by_dom.setdefault(domain, []).append((name, purpose))

    out: list[str] = []
    out.append("# docs-html — catalog")
    out.append("")
    out.append("Auto-generated by `python builder.py catalog` — **do not "
               "hand-edit**. The one file to read before authoring: every "
               "component's call form and every doc-type's purpose, pulled "
               "straight from source so it never drifts.")
    out.append("")
    out.append(f"**{len(components)} components · {len(types)} doc-types.**")
    out.append("")

    out.append("## Components")
    out.append("")
    out.append("Call on the `c` namespace inside a doc-type body. Leaves are "
               "shown as `{{ c.x(...) }}`; containers that wrap content as "
               "`{% call c.x(...) %}…{% endcall %}`.")
    for cat in _ordered(by_cat, CATEGORY_ORDER):
        out.append("")
        out.append(f"### {cat}")
        if cat_blurb.get(cat):
            out.append(f"*{cat_blurb[cat]}*")
        out.append("")
        for call, purpose in sorted(by_cat[cat]):
            out.append(f"- `{call}`" + (f" — {purpose}" if purpose else ""))

    out.append("")
    out.append("## Doc-types")
    out.append("")
    out.append('Compose with `python builder.py new <type> "<title>"`.')
    for dom in _ordered(by_dom, DOMAIN_ORDER):
        out.append("")
        out.append(f"### {dom}")
        if dom_blurb.get(dom):
            out.append(f"*{dom_blurb[dom]}*")
        out.append("")
        for name, purpose in sorted(by_dom[dom]):
            out.append(f"- `{name}`" + (f" — {purpose}" if purpose else ""))

    out.append("")
    return "\n".join(out)


def cmd_catalog() -> int:
    """`catalog` — regenerate CATALOG.md from the templates."""
    CATALOG_OUTPUT.write_text(compose_catalog(), encoding="utf-8")
    print(f"composed catalog -> {CATALOG_OUTPUT}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """`show <name>` — everything about ONE component or doc-type in a single
    call: its call form / purpose (or type-name + which components it uses) and
    its full usage.md — so a lookup costs one command, not several file reads."""
    name = args.name

    comp = next((c for c in load_components() if c.name == name), None)
    if comp is not None:
        text = _read(comp.path)
        print(f"COMPONENT  {name}   (category: {comp.path.parent.parent.name})")
        print(f"  call:    {_component_call(comp)}")
        print(f"  purpose: {_purpose(text) or '(none)'}")
        print(f"\n--- usage.md ({comp.path.parent / 'usage.md'}) ---")
        print(_read(comp.path.parent / "usage.md").rstrip())
        return 0

    types = doc_type_dirs()
    if name in types:
        directory = types[name]
        text = _read(directory / "document.html.j2")
        tn = TYPE_NAME_RE.search(text)
        used = list(dict.fromkeys(re.findall(r"\bc\.(\w+)\(", text)))  # order-preserving
        print(f"DOC-TYPE   {name}   (domain: {directory.parent.name})")
        print(f"  type-name: {tn.group(1).strip() if tn else '(none)'}")
        print(f"  purpose:   {_purpose(text) or '(none)'}")
        print(f"  uses:      {', '.join(used) or '(none)'}")
        print(f"\n--- usage.md ({directory / 'usage.md'}) ---")
        print(_read(directory / "usage.md").rstrip())
        return 0

    print(f"no component or doc-type named {name!r}. "
          f"See CATALOG.md or `python builder.py --list`.")
    return 1


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
    sub.add_parser("showcase", help="regenerate every showcases/<name>.html")
    sub.add_parser("catalog", help="regenerate CATALOG.md (quick-reference)")
    show = sub.add_parser("show", help="print one component/doc-type: signature + usage.md")
    show.add_argument("name", help="a component or doc-type name")

    args = parser.parse_args(argv)
    if args.list:
        return cmd_list()
    if args.cmd == "new":
        return cmd_new(args)
    if args.cmd == "showcase":
        return cmd_showcase()
    if args.cmd == "catalog":
        return cmd_catalog()
    if args.cmd == "show":
        return cmd_show(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
