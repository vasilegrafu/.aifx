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
(`css/docs-html.css`) and one script (`js/docs-html.js`), both from the
version-pinned CDN (`cdn_href`, read from version.json). There is no
per-document CSS selection and no publish step — every generated file,
documents and the showcase alike, references the shared CDN assets so it is
shareable as-is.
"""

import argparse
import json
import re
import sys
import time
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
PURPOSE_RE = re.compile(r"\{#\s*purpose:\s*(.*?)\s*#\}")        # {# purpose: X #}
MACRO_SIG_RE = re.compile(r"\{%\s*macro\s+\w+\s*\((.*?)\)\s*%\}", re.S)

# Presentation order for CATALOG.md (unknown keys append alphabetically).
# Categories are listed GROUP BY GROUP: the catalog bands by group, so a
# category out of its group's run would split that band in two.
CATEGORY_ORDER = ["structure", "layout", "content", "lists", "callouts",
                  "blocks", "front-back-matter",               # foundational
                  "business", "investing",                     # domain-specific
                  "math", "diagrams", "charts"]                # subsystems

# The first folder under components/ — what a component's scope is, stated by
# where it lives. `math`, `diagrams` and `charts` are each their own group AND
# their own category: single-category subsystems that need no extra level.
GROUP_BLURBS = {
    "foundational": "Domain-neutral — any document may use these, and nothing "
                    "here knows what the document is about.",
    "domain-specific": "Owned by one business domain. Their CSS classes carry "
                       "the domain name, so markup says who owns it.",
    "math": "The formula subsystem: LaTeX in the document, rendered by KaTeX "
            "at view time.",
    "diagrams": "The diagram subsystem: an engine-agnostic viewport plus one "
                "engine.",
    "charts": "The chart subsystem: an engine-agnostic frame plus one engine. "
              "A chart is data, not a picture.",
}

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


def boxstats(values: list[float]) -> dict:
    """Five-number summary + Tukey outliers, for the box-plot preset.

    A Jinja filter rather than template arithmetic: quartiles need sorting and
    interpolation, which Jinja can express only badly. It still runs at compose
    time, so the rendered spec carries the derived numbers and a reader can
    check them.

    Quartiles use linear interpolation between order statistics (the default of
    R's type 7 and numpy's `percentile`). Whiskers are Tukey's: the furthest
    point within 1.5 x IQR of the box, NOT the extremes — points beyond are
    returned separately so they can be drawn as outliers rather than silently
    stretching the whisker."""
    data = sorted(float(v) for v in values)
    if not data:
        return {"box": [0, 0, 0, 0, 0], "outliers": []}

    def q(p: float) -> float:
        if len(data) == 1:
            return data[0]
        pos = p * (len(data) - 1)
        lo = int(pos)
        hi = min(lo + 1, len(data) - 1)
        return data[lo] + (pos - lo) * (data[hi] - data[lo])

    q1, med, q3 = q(.25), q(.5), q(.75)
    iqr = q3 - q1
    lo_fence, hi_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    inside = [v for v in data if lo_fence <= v <= hi_fence] or data
    return {
        "box": [round(v, 4) for v in (inside[0], q1, med, q3, inside[-1])],
        "outliers": [round(v, 4) for v in data if v < lo_fence or v > hi_fence],
    }


def make_env(components: list[Component]) -> Environment:
    """Build the Jinja environment used for composing documents."""
    env = Environment(loader=FileSystemLoader(str(SKILL_DIR)),
                      trim_blocks=True, lstrip_blocks=True,   # tidy whitespace
                      keep_trailing_newline=True, autoescape=False)
    env.filters["boxstats"] = boxstats
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


def cdn_href() -> str:
    """CDN prefix (version-pinned) baked into the head's fallback URLs.

    Read from version.json (the single source of truth) at compose time, so
    every generated file is pinned to the design-system version it was authored
    against. The cdn field is a template containing "{version}" (the version
    sits mid-URL when the assets live in a repo subfolder, e.g.
    …/gh/<user>/<repo>@{version}/skills/docs-html); a plain base URL gets
    "@version" appended. It is the only asset path the builder emits, so a
    missing cdn is a hard error rather than a silent broken link."""
    info = json.loads((SKILL_DIR.parent.parent / "version.json").read_text(encoding="utf-8"))
    cdn, version = info.get("cdn"), info["version"]
    if not cdn:
        sys.exit("version.json has no \"cdn\" — every document links the CDN; set it first.")
    return cdn.replace("{version}", version).replace("{skill}", SKILL_DIR.name)


# --------------------------------------------------------------------------
# compose — the heart of the builder
# --------------------------------------------------------------------------


def compose(type_name: str, title: str) -> str:
    """Render one doc-type template into standalone, hand-editable HTML."""
    directory = doc_type_dirs()[type_name]
    template_rel = (directory.relative_to(SKILL_DIR) / "document.html.j2").as_posix()
    template_src = (SKILL_DIR / template_rel).read_text(encoding="utf-8")

    # Display name from the template's {# type-name: ... #} comment.
    match = TYPE_NAME_RE.search(template_src)
    display_name = (match.group(1).strip() if match
                    else type_name.replace("-", " ").title())

    components = load_components()
    return make_env(components).get_template(template_rel).render(
        title=title,
        type_name=display_name,
        cdn_href=cdn_href())


def showcase_templates() -> list[Path]:
    """Every showcase source: showcases/<name>.html.j2."""
    return sorted(SHOWCASES_DIR.glob("*.html.j2"))


def compose_showcase(template: Path) -> str:
    """Render one showcase (showcases/<name>.html.j2). A showcase is the skill's
    own reference page — it exercises real macros, never a user document. Unlike
    a document (CDN-only), base.html.j2 links the showcase to the LOCAL working
    tree (`cdn_href="..", so `../css`/`../js`) so the gallery always previews the
    current tree; the template's own `{% block head %}` adds a CDN fallback
    (`cdn_fallback`) for when those local assets are absent. Title/type-name come
    from `{# title #}` / `{# type-name #}` headers (falling back to the stem)."""
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
        cdn_href="..",              # base links the LOCAL tree (../css, ../js) — previews the current tree
        cdn_fallback=cdn_href(),    # …and the page's own block head falls back to this pinned CDN if local is absent
        cat_blurb=category_blurbs())   # single source: the category usage.md blurbs


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> int:
    """`new <type> <title>` — compose and write docs/<subject>-<type>.html.

    The SUBJECT leads and the report kind follows: `amd-investment-thesis.html`.
    One subject's reports then sort together, which is what you want when a
    folder holds several reports about the same thing.

    `--slug` sets the subject independently of the title, because the two want
    different things: the title is prose the reader sees ("AMD — Advanced Micro
    Devices"), the subject is an identifier ("amd"). Without it the filename
    inherits the whole title and grows unreadable. Defaults to the title's slug.

    The kind of report is in the filename because a rule in each doc-type's
    usage.md was not enough — nothing applied it, and two investment theses
    ended up named after their subject alone."""
    type_name = resolve_type(args.type)
    out_dir = Path(args.docs).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = slug(args.slug) if args.slug else slug(args.title)
    # Do not repeat the type when the subject already ends with it.
    if not stem.endswith(type_name):
        stem = f"{stem}-{type_name}"
    out = out_dir / f"{stem}.html"
    if out.exists() and not args.force:     # never clobber a hand-edited doc
        print(f"refusing to overwrite {out.name} (pass --force)")
        return 1

    out.write_text(compose(type_name, args.title), encoding="utf-8")
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


def _blame(exc: BaseException) -> str:
    """Which TEMPLATE actually raised — the part of a Jinja traceback worth
    printing.

    Jinja rewrites tracebacks so template frames appear as real frames whose
    filename is the .j2 path. The failure surfaces at the top-level template
    being rendered (a showcase calls 115 components), so without this the
    report names `components.html.j2` and leaves the reader to find which of
    the 115 broke. The DEEPEST .j2 frame is the culprit."""
    import traceback
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if f.filename.endswith(".j2")]
    if not frames:
        return ""
    deepest = frames[-1]
    name = Path(deepest.filename).parent.name          # the component's folder
    return f" [{name}:{deepest.lineno}]"


UNIT_RE = re.compile(r"\{#\s*unit:\s*(\w+)")

# Where a unit has to be written depends on the chart's SHAPE — on where the
# reader's eye lands on the number — not on the chart's name. Each component
# declares its family in a `{# unit: … #}` header, so a new chart states what it
# is and nothing here needs editing.
UNIT_FAMILIES = {
    # one quantity and no axis: the subtext is the only place a unit can go, so
    # without it the reader has a bare number and nothing to interpret it with.
    "required": "must accept `unit`, and the showcase demo must pass one",
    # one measured axis: the axis name sits right next to the numbers, which is
    # a better home than a subtext. `unit` stays allowed, just not required.
    "axis": "must accept `y_name` or `x_name`",
    # two measured dimensions: a single subtext for two different units would
    # be a lie, so each axis must be nameable independently.
    "multi": "must accept both `x_name` and `y_name`",
    # fixed by construction — a correlation coefficient, a 100% column. Nagging
    # for a unit here would train authors to write something meaningless.
    "none": "nothing required",
}


def chart_audit() -> list[str]:
    """Structural rules every chart component must obey. Returns the breaches.

    Rendering cannot catch these. A chart that states no unit draws perfectly
    and leaves the reader guessing whether a bar means dollars or percent; a
    chart that sets its own title draws it wherever the engine likes, which is
    how `sankey` came to print its caption straight through the ribbons while
    sixteen other charts each repeated the same clearance literal.

    The rules guard the COMPONENTS rather than the authors, with one exception:
    for a `required` chart the SHOWCASE demo must also state a unit, because
    the showcase is the reference example and a canonical demo that omits it
    teaches every copy to omit it.

    An absent or unknown `{# unit: … #}` is itself a failure — a new chart
    cannot skip the decision by saying nothing."""
    problems = []
    showcase_src = "\n".join(_read(t) for t in showcase_templates())

    for path in sorted((COMPONENTS_DIR / "charts").glob("*/component.html.j2")):
        name = path.parent.name
        if name == "apache-echarts":             # the engine, not a chart
            continue
        src = _read(path)
        match = re.search(r"\{% macro (\w+)\((.*?)\) %\}", src, re.S)
        if not match:
            problems.append(f"{name}: no macro signature")
            continue
        macro, params = match.group(1), match.group(2)

        # universal: the shared tail owns the whole title area
        if '"title"' in src:
            problems.append(f"{name}: sets its own title — use r.out(…, caption, unit)")
        if "caption=" not in params:
            problems.append(f"{name}: macro takes no `caption`")

        declared = UNIT_RE.search(src)
        family = declared.group(1) if declared else None
        if family not in UNIT_FAMILIES:
            problems.append(f"{name}: {'unknown' if family else 'missing'} "
                            f"`{{# unit: … #}}` header{f' ({family})' if family else ''}"
                            f" — one of {', '.join(UNIT_FAMILIES)}")
            continue

        if family == "required":
            if "unit=" not in params:
                problems.append(f"{name}: declared `required` but takes no `unit`")
            # the demo call in the showcase, up to its closing paren
            demo = re.search(rf"c\.{macro}\((?:[^()]|\([^()]*\))*\)", showcase_src)
            if not demo:
                problems.append(f"{name}: declared `required` but has no showcase demo")
            elif not re.search(r'\bunit\s*=\s*"[^"]+"', demo.group(0)):
                problems.append(f"{name}: showcase demo states no unit")
        elif family == "axis":
            if "y_name=" not in params and "x_name=" not in params:
                problems.append(f"{name}: declared `axis` but names no axis")
        elif family == "multi":
            missing = [p for p in ("x_name=", "y_name=") if p not in params]
            if missing:
                problems.append(f"{name}: declared `multi` but takes no "
                                f"{', '.join(p.rstrip('=') for p in missing)}")
    return problems


def cmd_check() -> int:
    """`check` — compose every doc-type and confirm nothing is left unrendered.

    The skill's one automated guard, and it exists because the failures it
    catches are SILENT. A component whose template no longer parses, or a
    doc-type calling a macro that has changed shape, is not discovered at
    compose time by anything else — it is discovered by the next person who
    runs `new` and gets a broken document, or worse, does not notice.

    Three things are checked, and between them they EXECUTE every component:

    1. `make_env` parses EVERY component template to expose its macro, so a
       syntax error anywhere in components/ fails here before a doc-type is
       touched.
    2. Every doc-type is rendered through the same context `compose()` uses,
       then searched for a surviving `{% ... %}`.
    3. Every showcase is rendered the same way. This is what makes the check
       complete rather than merely broad: doc-types call well under half the
       components, because the rest are a library an author reaches for by
       hand, and the showcase calls the rest. Together they run every one, so
       a RUNTIME fault — bad tuple arity, a wrong unpack, `loop.parent` — is
       caught in a component no doc-type happens to use. Parsing alone would
       not find it.

    4. `chart_audit()` — structural rules the charts must obey, which no
       amount of rendering can catch. See its docstring.

    Only `{% %}` counts as a defect. `{{ ... }}` in the output is BY DESIGN —
    a composed skeleton carries content placeholders for the author to fill,
    and treating those as failures makes the check cry wolf on every one."""
    start = time.perf_counter()
    try:
        env = make_env(load_components())
    except Exception as e:                       # noqa: BLE001 — report, don't crash
        print(f"component templates failed to load: {type(e).__name__}: {e}")
        return 1

    types = doc_type_dirs()
    failures = 0

    for name, directory in sorted(types.items()):
        rel = (directory.relative_to(SKILL_DIR) / "document.html.j2").as_posix()
        try:
            src = (SKILL_DIR / rel).read_text(encoding="utf-8")
            match = TYPE_NAME_RE.search(src)
            out = env.get_template(rel).render(
                title="Check Probe",
                type_name=(match.group(1).strip() if match
                           else name.replace("-", " ").title()),
                cdn_href=cdn_href())
        except Exception as e:                   # noqa: BLE001 — report, don't crash
            print(f"  {name:<30} FAILED{_blame(e)}: {type(e).__name__}: {e}")
            failures += 1
            continue

        left = re.search(r"\{%.{0,60}", out, re.S)
        if left:
            print(f"  {name:<38} UNRENDERED: {left.group(0)!r}")
            failures += 1

    # The showcases, through the same function `showcase` uses — so the check
    # exercises the real code path rather than a copy of it. Nothing is written.
    shows = showcase_templates()
    for template in shows:
        try:
            out = compose_showcase(template)
        except Exception as e:                   # noqa: BLE001 — report, don't crash
            print(f"  {template.name:<30} FAILED{_blame(e)}: {type(e).__name__}: {e}")
            failures += 1
            continue
        left = re.search(r"\{%.{0,60}", out, re.S)
        if left:
            print(f"  {template.name:<38} UNRENDERED: {left.group(0)!r}")
            failures += 1

    charts = chart_audit()
    for problem in charts:
        print(f"  {problem}")

    elapsed = time.perf_counter() - start
    print()
    if failures or charts:
        if failures:
            print(f"{failures} template(s) failed")
        if charts:
            print(f"{len(charts)} chart rule(s) broken")
        return 1
    print(f"{len(load_components())} components executed via {len(types)} doc-types "
          f"+ {len(shows)} showcase(s), all clean ({elapsed:.1f}s)")
    print(f"charts: {_family_tally()}, none titles itself")
    return 0


def _family_tally() -> str:
    """`required 5 · axis 11 · multi 1 · none 4` — what the audit just checked."""
    counts = dict.fromkeys(UNIT_FAMILIES, 0)
    for path in (COMPONENTS_DIR / "charts").glob("*/component.html.j2"):
        found = UNIT_RE.search(_read(path))
        if found and found.group(1) in counts:
            counts[found.group(1)] += 1
    return " · ".join(f"{k} {v}" for k, v in counts.items())


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
    """category folder name -> blurb, from the category's own usage.md.

    Derived from the loaded components rather than globbed at a fixed depth,
    because the categories do not all sit at the same depth: `charts` and
    `diagrams` are top-level groups holding components directly, while
    `foundational` and `domain-specific` hold a category level first. Walking
    up from each component finds the category wherever it is, and cannot drift
    from what `load_components` actually discovered."""
    blurbs = {}
    for comp in load_components():
        category_dir = comp.path.parent.parent
        if category_dir.name not in blurbs:
            usage = category_dir / "usage.md"
            if usage.exists():
                blurbs[category_dir.name] = _blurb(_read(usage))
    return blurbs


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
    cat_group: dict[str, str] = {}
    for comp in components:
        category = comp.path.parent.parent.name
        by_cat.setdefault(category, []).append(
            (_component_call(comp), _purpose(_read(comp.path))))
        # The group is the first folder under components/. For `charts` and
        # `diagrams` that is the category itself — they are single-category
        # subsystems and need no extra level.
        cat_group[category] = comp.path.relative_to(COMPONENTS_DIR).parts[0]

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
    shown_group = None
    for cat in _ordered(by_cat, CATEGORY_ORDER):
        group = cat_group.get(cat, "")
        if group != shown_group:
            shown_group = group
            out.append("")
            out.append(f"### {group}")
            out.append("")
            out.append(f"*{GROUP_BLURBS.get(group, '')}*")
        out.append("")
        out.append(f"#### {cat}")
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
    new.add_argument("--slug", default="",
                     help="subject for the filename (e.g. a ticker); "
                          "defaults to the title's slug")
    new.add_argument("--force", action="store_true", help="overwrite an existing document")
    sub.add_parser("showcase", help="regenerate every showcases/<name>.html")
    sub.add_parser("catalog", help="regenerate CATALOG.md (quick-reference)")
    sub.add_parser("check", help="compose every doc-type; fail on unrendered Jinja")
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
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "show":
        return cmd_show(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
