"""investing — builder: generate a report from live data through Jinja.

Usage:
    python builder.py build <report> <args...> [--out DIR]
    python builder.py check
    python builder.py list
    python builder.py show <name>

The pieces (all inside this skill directory):

    data_providers/<provider>/           the client — the ONLY thing doing I/O
    reports/base.html.j2                 the shared shell ({% block content %})
    reports/<name>/report.builder.py     fetch() + shape() + sample()
    reports/<name>/report.html.j2        the RECIPE: which components, in what
                                         order, in what layout
    components/<cat>/<name>/component.html.j2   {% macro <name>(...) %}

THE SEPARATION THAT MATTERS. The builder never emits markup; the template never
fetches; a component never knows which report called it. Break any one of those
and the other two stop being replaceable.

HOW THIS DIFFERS FROM docs-html. There, a doc-type is a SKELETON a human fills:
component calls carrying literal placeholder text, and the output is edited by
hand. Here a report is a PROGRAM: the same component calls carry `d.*`, and the
output is regenerated. The consequence is `StrictUndefined` in `make_env` — see
the note there, it is the single most important line in this file.

Jinja runs ONLY here, at build time. The written file is standalone HTML with
no Jinja left, linking the two version-pinned CDN assets and nothing else.

MAP — the whole engine is five small things; everything else is a guard or a
comment explaining WHY. Read these five and you have read the builder:

    1. FIND FILES       load_components() · report_dirs()   rglob for *.html.j2;
                        found, never registered.
    2. MAKE THE ENV     make_env()   number filters, macros hung on `c`, and
                        StrictUndefined (the one line that matters most).
    3. RENDER A REPORT  compose_report()   data on `d`, macros on `c`, CDN links
                        baked in.
    4. build            cmd_build()   fetch() -> shape() -> render -> write.
    5. check            cmd_check()   the same render from sample(), offline —
                        no network, no key — plus every showcase.py.

The rest earns its keep but is not the spine:
    - filters + boxstats()          the one place a number becomes a string
    - chart_audit() · data_audit()  static rules rendering cannot catch
    - showcase machinery            per-component proof: showcase.py -> .html
    - _blame() · _family_tally()    nicer failure and summary output
"""

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import NamedTuple

from jinja2 import Environment, FileSystemLoader, StrictUndefined

# --------------------------------------------------------------------------
# paths and constants
# --------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = SKILL_DIR / "components"
REPORTS_DIR = SKILL_DIR / "reports"

REPORT_NAME_RE = re.compile(r"\{#\s*report-name:\s*(.+?)\s*#\}")


class Component(NamedTuple):
    """One entry of components/<cat>/<name>/component.html.j2."""
    name: str        # directory name, e.g. "metric-trend"
    macro: str       # macro/callable name, e.g. "metric_trend"
    path: Path       # the component.html.j2 file


def load_components() -> list[Component]:
    """Scan components/ once, recursively.

    components/ is organized in CATEGORY folders that exist purely for humans —
    a component's identity stays its own folder name (macro = name with
    - -> _), so category moves never touch templates. Names must be unique
    across categories."""
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
# formatting — the one place a number becomes a string
# --------------------------------------------------------------------------
#
# Components receive RAW NUMBERS and format them here. In docs-html the author
# passed pre-formatted strings, which meant every generator re-implemented
# money()/pct()/signed() and two documents could disagree about what a thousands
# separator looks like. One definition, applied by the component.
#
# Every filter passes STRINGS THROUGH UNCHANGED. A builder legitimately needs to
# emit "n/m" where a ratio has no meaning (a CAGR from a negative base, say),
# and forcing that through a numeric format would either crash or invent a
# number. Passing it through is the honest behaviour.

def _passthrough(fn):
    def wrapped(value, *a, **kw):
        if isinstance(value, str) or value is None:
            return "" if value is None else value
        return fn(value, *a, **kw)
    return wrapped


@_passthrough
def f_money(v, digits=0):
    return f"{v:,.{digits}f}"


@_passthrough
def f_pct(v, digits=1):
    return f"{v:.{digits}f}%"


@_passthrough
def f_signed(v, digits=0):
    return f"{v:+,.{digits}f}"


@_passthrough
def f_bps(v):
    return f"{v:+,.0f} bps"


@_passthrough
def f_num(v, digits=2):
    return f"{v:,.{digits}f}"


FORMATS = {"money": f_money, "pct": f_pct, "signed": f_signed,
           "bps": f_bps, "num": f_num, "raw": lambda v: v}


def f_fmt(value, spec="num", *a, **kw):
    """Dispatch by name, so a component can take `fmt="money"` as an argument.

    Named `fmt` rather than `format` because Jinja already ships a `format`
    filter (printf-style) and shadowing it would break any template using it."""
    if spec not in FORMATS:
        raise ValueError(f"unknown format {spec!r} — one of {', '.join(FORMATS)}")
    return FORMATS[spec](value, *a, **kw)


def boxstats(values: list) -> dict:
    """Five-number summary + Tukey outliers, for the box-plot preset.

    A Jinja filter rather than template arithmetic: quartiles need sorting and
    interpolation, which Jinja can express only badly. It still runs at build
    time, so the rendered spec carries the derived numbers and a reader can
    check them.

    Quartiles use linear interpolation between order statistics (R's type 7 /
    numpy's `percentile` default). Whiskers are Tukey's: the furthest point
    within 1.5 x IQR of the box, NOT the extremes — points beyond come back
    separately so they draw as outliers rather than silently stretching the
    whisker, which is how a fat tail disappears."""
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


# --------------------------------------------------------------------------
# jinja environment — every component macro exposed on the `c` namespace
# --------------------------------------------------------------------------

def make_env(components: list[Component]) -> Environment:
    """Build the Jinja environment used for building reports.

    StrictUndefined IS THE POINT. A report reading `d.revenue` when its builder
    produced `d.total_revenue` would, by default, render an empty string — a
    tidy blank cell in an otherwise perfect table, which nobody notices. That is
    the same failure class as an unbalanced sankey: it draws beautifully and
    lies. With StrictUndefined it raises at build time instead, and since Jinja
    runs only here the failure costs nothing and reaches no reader.

    docs-html cannot do this: its skeletons are meant to come out with holes.
    This skill's output is meant to come out finished."""
    env = Environment(loader=FileSystemLoader(str(SKILL_DIR)),
                      trim_blocks=True, lstrip_blocks=True,
                      keep_trailing_newline=True, autoescape=False,
                      undefined=StrictUndefined)
    for name, fn in [("money", f_money), ("pct", f_pct), ("signed", f_signed),
                     ("bps", f_bps), ("num", f_num), ("fmt", f_fmt),
                     ("boxstats", boxstats)]:
        env.filters[name] = fn

    c = SimpleNamespace()
    for component in components:
        module = env.get_template(
            component.path.relative_to(SKILL_DIR).as_posix()).module
        if hasattr(module, component.macro):
            setattr(c, component.macro, getattr(module, component.macro))
    env.globals["c"] = c        # templates call {{ c.<macro>(...) }} — no imports
    return env


# --------------------------------------------------------------------------
# report discovery — same rule as components: found, never registered
# --------------------------------------------------------------------------

def report_dirs() -> dict[str, Path]:
    """Every report folder, discovered recursively: name -> directory."""
    dirs: dict[str, Path] = {}
    for template in sorted(REPORTS_DIR.rglob("report.html.j2")):
        name = template.parent.name
        if name in dirs:
            raise SystemExit(f"duplicate report name: {name!r} "
                             f"({dirs[name]} and {template.parent})")
        dirs[name] = template.parent
    return dirs


def resolve_report(name: str) -> str:
    names = report_dirs()
    if name in names:
        return name
    matches = [n for n in names if n.startswith(name)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"unknown report: {name!r}\nknown: {', '.join(sorted(names))}")
    raise SystemExit(f"ambiguous report {name!r}: {', '.join(sorted(matches))}")


def load_report_module(name: str):
    """Import reports/<name>/report.builder.py by path.

    By path rather than by package, so a report folder needs no __init__.py and
    the discovery rule stays 'a directory containing report.html.j2'."""
    directory = report_dirs()[name]
    path = directory / "report.builder.py"
    if not path.exists():
        raise SystemExit(f"{name}: no report.builder.py beside report.html.j2")
    spec = importlib.util.spec_from_file_location(f"report_{name.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for required in ("shape", "sample"):
        if not hasattr(module, required):
            raise SystemExit(f"{name}: report.builder.py defines no {required}()")
    return module


def cdn_href() -> str:
    """CDN prefix (version-pinned) baked into the head's asset URLs.

    Read from version.json at build time, so every generated file is pinned to
    the design-system version it was built against. Published tags are
    immutable, so an old report keeps rendering exactly as it did."""
    info = json.loads((SKILL_DIR.parent.parent / "version.json").read_text(encoding="utf-8"))
    cdn, version = info.get("cdn"), info["version"]
    if not cdn:
        sys.exit('version.json has no "cdn" — every report links it; set it first.')
    return cdn.replace("{version}", version).replace("{skill}", SKILL_DIR.name)


# --------------------------------------------------------------------------
# build — the heart
# --------------------------------------------------------------------------

def compose_report(name: str, d: dict, title: str = "") -> str:
    """Render one report's recipe with the data its builder produced."""
    directory = report_dirs()[name]
    rel = (directory.relative_to(SKILL_DIR) / "report.html.j2").as_posix()
    src = (SKILL_DIR / rel).read_text(encoding="utf-8")
    match = REPORT_NAME_RE.search(src)
    display = match.group(1).strip() if match else name.replace("-", " ").title()

    return make_env(load_components()).get_template(rel).render(
        d=SimpleNamespace(**d) if isinstance(d, dict) else d,
        title=title or d.get("title", display),
        report_name=display,
        cdn_href=cdn_href())


def load_showcase_cases(component: Component) -> list[tuple[str, dict]]:
    """Import components/<cat>/<name>/showcase.py and return its cases().

    By path, like report modules, so a component folder needs no __init__.py and
    the discovery rule stays 'a directory containing component.html.j2'. The
    contract is one function, cases() -> list[(label, kwargs)]; each kwargs dict
    is fed straight to the macro."""
    path = component.path.parent / "showcase.py"
    spec = importlib.util.spec_from_file_location(
        f"showcase_{component.macro}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "cases"):
        raise SystemExit(f"{component.name}: showcase.py defines no cases()")
    cases = module.cases()
    if not cases:
        raise SystemExit(f"{component.name}: cases() returned nothing")
    return cases


def components_with_showcase() -> list[Component]:
    """Every component that ships a showcase.py beside its markup."""
    return [c for c in load_components()
            if (c.path.parent / "showcase.py").exists()]


def compose_component_showcase(env: Environment, component: Component) -> str:
    """Render every case of one component into its standalone showcase page.

    Each case is rendered by CALLING the macro from Python — the same macro the
    reports call through `c.<macro>` — so the showcase exercises the exact code
    path a report does, not a re-implementation of it. A macro that renders here
    renders there."""
    macro = getattr(env.globals["c"], component.macro, None)
    if macro is None:
        raise SystemExit(f"{component.name}: no macro {component.macro!r} to show")

    src = component.path.read_text(encoding="utf-8")
    sig = re.search(r"\{% macro (\w+\(.*?\)) %\}", src, re.S)
    rendered = [{"label": label, "body": macro(**kwargs)}
                for label, kwargs in load_showcase_cases(component)]

    css = (SKILL_DIR / "css" / "_showcase.css").read_text(encoding="utf-8")
    return env.get_template("components/_showcase.html.j2").render(
        title=f"{component.name} — showcase",
        component_name=component.name,
        macro_sig=sig.group(1) if sig else component.macro,
        cases=rendered,
        showcase_css=css,
        cdn_href=cdn_href())


def _blame(exc: BaseException) -> str:
    """Which TEMPLATE actually raised — the part of a Jinja traceback worth
    printing. Jinja rewrites tracebacks so template frames appear as real
    frames whose filename is the .j2 path; the DEEPEST one is the culprit."""
    import traceback
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if f.filename.endswith(".j2")]
    if not frames:
        return ""
    deepest = frames[-1]
    return f" [{Path(deepest.filename).parent.name}:{deepest.lineno}]"


# --------------------------------------------------------------------------
# chart audit — structural rules no amount of rendering can catch
# --------------------------------------------------------------------------

UNIT_RE = re.compile(r"\{#\s*unit:\s*(\w+)")

UNIT_FAMILIES = {
    "required": "must accept `unit`",
    "axis": "must accept `y_name` or `x_name`",
    "multi": "must accept both `x_name` and `y_name`",
    "none": "nothing required",
}

DATA_RE = re.compile(r"\{#\s*data:\s*(.+?)\s*#\}", re.S)


def chart_audit() -> list[str]:
    """Where a unit has to be written depends on the chart's SHAPE — on where
    the reader's eye lands on the number — not on the chart's name. Each
    component declares its family in a `{# unit: … #}` header, so a new chart
    states what it is and nothing here needs editing.

    A chart that states no unit draws perfectly and leaves the reader guessing
    whether a bar means dollars or percent. A chart that sets its own title
    draws it wherever the engine likes — which is how `sankey` came to print
    its caption straight through the ribbons."""
    problems = []
    charts = COMPONENTS_DIR / "charts"
    if not charts.exists():
        return problems

    for path in sorted(charts.glob("*/component.html.j2")):
        name = path.parent.name
        if name == "apache-echarts":             # the engine, not a chart
            continue
        src = path.read_text(encoding="utf-8")
        match = re.search(r"\{% macro (\w+)\((.*?)\) %\}", src, re.S)
        if not match:
            problems.append(f"{name}: no macro signature")
            continue
        params = match.group(2)

        if '"title"' in src:
            problems.append(f"{name}: sets its own title — use r.out(…, caption, unit)")
        if "caption=" not in params:
            problems.append(f"{name}: macro takes no `caption`")

        declared = UNIT_RE.search(src)
        family = declared.group(1) if declared else None
        if family not in UNIT_FAMILIES:
            problems.append(f"{name}: {'unknown' if family else 'missing'} "
                            f"`{{# unit: … #}}` header — one of {', '.join(UNIT_FAMILIES)}")
            continue
        if family == "required" and "unit=" not in params:
            problems.append(f"{name}: declared `required` but takes no `unit`")
        if family == "axis" and not ("y_name=" in params or "x_name=" in params):
            problems.append(f"{name}: declared `axis` but names no axis")
        if family == "multi" and not ("y_name=" in params and "x_name=" in params):
            problems.append(f"{name}: declared `multi` but does not name both axes")
    return problems


# Key names that are also dict METHODS. Jinja resolves `r.values` with getattr
# before getitem, so a row dict keyed "values" hands the template a bound method
# and the render dies with "'builtin_function_or_method' object is not
# iterable" — pointing at the component, which is not where the mistake is.
# Table rows carry `cells`; chart series carry `points`.
DICT_METHODS = {"values", "keys", "items", "copy", "update", "pop", "clear",
                "setdefault", "popitem", "fromkeys"}

ATTR_RE = re.compile(r"\b[a-z_]\w*\.(\w+)\b")


def data_audit() -> list[str]:
    """Every component must declare the shape it expects, and must not name a
    field after a dict method.

    A builder and a component agreeing by accident is the failure this skill
    exists to prevent; StrictUndefined catches a MISSING key at build time, but
    only a declared shape tells a human what the key should CONTAIN — and only
    this check stops a field name from being silently shadowed."""
    problems = []
    for component in load_components():
        src = component.path.read_text(encoding="utf-8")

        declared = DATA_RE.search(src)
        if not declared and re.search(r"\b(rows|series|nodes|links|steps|items|inputs)=\[\]", src):
            problems.append(f"{component.name}: takes structured data but "
                            f"declares no `{{# data: … #}}` header")

        # `.get(` is the deliberate way to read an OPTIONAL field, so exempt it.
        for attr in set(ATTR_RE.findall(src)) & DICT_METHODS:
            if f".{attr}(" in src:
                continue
            problems.append(f"{component.name}: reads `.{attr}`, which is a dict "
                            f"method — Jinja returns the method, not the field. "
                            f"Rename it (rows carry `cells`, series carry `points`)")
        if declared:
            for field in re.findall(r"(\w+):", declared.group(1)):
                if field in DICT_METHODS:
                    problems.append(f"{component.name}: declares field {field!r}, "
                                    f"which is a dict method — rename it")
    return problems


def _family_tally() -> str:
    tally = {}
    charts = COMPONENTS_DIR / "charts"
    if charts.exists():
        for path in charts.glob("*/component.html.j2"):
            if path.parent.name == "apache-echarts":
                continue
            found = UNIT_RE.search(path.read_text(encoding="utf-8"))
            key = found.group(1) if found else "?"
            tally[key] = tally.get(key, 0) + 1
    return " · ".join(f"{k} {v}" for k, v in sorted(tally.items()))


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_list() -> int:
    reports = report_dirs()
    print(f"{len(reports)} report(s):\n")
    for name, directory in sorted(reports.items()):
        src = (directory / "report.html.j2").read_text(encoding="utf-8")
        match = REPORT_NAME_RE.search(src)
        print(f"  {name:<28} {match.group(1).strip() if match else ''}")
    print(f"\n{len(load_components())} component(s) available.")
    return 0


def cmd_build(name: str, rest: list[str], out_dir: str, force: bool) -> int:
    name = resolve_report(name)
    module = load_report_module(name)

    parser = argparse.ArgumentParser(prog=f"builder.py build {name}")
    if hasattr(module, "add_args"):
        module.add_args(parser)
    args = parser.parse_args(rest)

    if not hasattr(module, "fetch"):
        raise SystemExit(f"{name}: report.builder.py defines no fetch()")

    print(f"fetching …", flush=True)
    payloads = module.fetch(**vars(args))
    print(f"shaping and asserting …", flush=True)
    d = module.shape(payloads)

    html = compose_report(name, d)

    stem = d.get("slug") or name
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{stem}-{name}.html" if not stem.endswith(name) else out / f"{stem}.html"
    if target.exists() and not force:
        print(f"refusing to overwrite {target.name} (pass --force)")
        return 1
    target.write_text(html, encoding="utf-8")

    left = re.findall(r"\{\{[^{}]{0,60}", html)
    print(f"built: {target}")
    if left:
        print(f"  {len(left)} prose slot(s) left to fill by hand")
    return 0


def cmd_check() -> int:
    """Build every report from its own sample() and confirm nothing is unrendered.

    sample() rather than fetch() so the check needs NO network and NO
    credential — the moment a guard needs a secret to run, it stops being run.
    It also exercises shape(), which is where every arithmetic invariant lives,
    so the ties are re-asserted on every check."""
    start = time.perf_counter()
    try:
        make_env(load_components())              # parses every component template
    except Exception as e:                       # noqa: BLE001 — report, don't crash
        print(f"component templates failed to load: {type(e).__name__}: {e}")
        return 1

    failures = 0
    reports = report_dirs()

    for name in sorted(reports):
        try:
            module = load_report_module(name)
            out = compose_report(name, module.shape(module.sample()))
        except Exception as e:                   # noqa: BLE001 — report, don't crash
            print(f"  {name:<30} FAILED{_blame(e)}: {type(e).__name__}: {e}")
            failures += 1
            continue
        left = re.search(r"\{%.{0,60}", out, re.S)
        if left:
            print(f"  {name:<30} UNRENDERED: {left.group(0)!r}")
            failures += 1

    # Per-component showcases — the render-coverage net. Only financial-profile
    # calls components, and it calls a fraction of them; every other component
    # would ship with nothing proving it renders. showcase.py fixes that: each
    # is rendered here, in memory, offline. A component with NO showcase.py is
    # reported as uncovered so the gap is visible rather than silent.
    env = make_env(load_components())
    shown = components_with_showcase()
    shown_names = {c.name for c in shown}
    for component in shown:
        try:
            out = compose_component_showcase(env, component)
        except Exception as e:                   # noqa: BLE001 — report, don't crash
            print(f"  {component.name:<30} FAILED{_blame(e)}: {type(e).__name__}: {e}")
            failures += 1
            continue
        left = re.search(r"\{%.{0,60}", out, re.S)
        if left:
            print(f"  {component.name:<30} UNRENDERED: {left.group(0)!r}")
            failures += 1

    uncovered = [c.name for c in load_components() if c.name not in shown_names]

    problems = chart_audit() + data_audit()
    for problem in problems:
        print(f"  {problem}")

    elapsed = time.perf_counter() - start
    total = len(load_components())
    print()
    if failures or problems:
        if failures:
            print(f"{failures} template(s) failed")
        if problems:
            print(f"{len(problems)} rule(s) broken")
        return 1
    print(f"{total} components: {len(shown)} shown via showcase.py, "
          f"{len(reports)} report(s), all clean ({elapsed:.1f}s)")
    if uncovered:
        print(f"  {len(uncovered)} without a showcase.py yet: "
              f"{', '.join(uncovered[:8])}{' …' if len(uncovered) > 8 else ''}")
    if _family_tally():
        print(f"charts: {_family_tally()}, none titles itself")
    return 0


def cmd_show(name: str) -> int:
    for component in load_components():
        if component.name == name or component.macro == name:
            src = component.path.read_text(encoding="utf-8")
            print(f"--- {component.path.relative_to(SKILL_DIR)} ---\n")
            for line in src.splitlines():
                if line.startswith("{#") or line.startswith("{% macro"):
                    print(line)
            usage = component.path.parent / "usage.md"
            if usage.exists():
                print(f"\n--- usage.md ---\n{usage.read_text(encoding='utf-8')}")
            return 0
    print(f"unknown component: {name!r}")
    return 1


def cmd_showcase(name: str | None = None) -> int:
    """Write showcase.html beside every component that ships a showcase.py.

    The output is a build artifact, gitignored (see .gitignore): this is a
    PUBLIC repo and 110 generated pages have no business being served by the
    CDN. Regenerate them locally to browse; the showcase.py is the source."""
    components = components_with_showcase()
    if name:
        components = [c for c in components if c.name == name or c.macro == name]
        if not components:
            print(f"no component with a showcase.py named {name!r}")
            return 1
    if not components:
        print("no showcase.py files yet — add one beside a component.html.j2")
        return 0

    env = make_env(load_components())
    for component in components:
        out = component.path.parent / "showcase.html"
        try:
            out.write_text(compose_component_showcase(env, component),
                           encoding="utf-8")
        except Exception as e:                   # noqa: BLE001 — report, don't crash
            print(f"  {component.name:<30} FAILED{_blame(e)}: {type(e).__name__}: {e}")
            return 1
        print(f"composed: {out.relative_to(SKILL_DIR)}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="builder.py", description="generate investing reports from live data")
    sub = parser.add_subparsers(dest="cmd")

    build = sub.add_parser("build", help="build a report from live data")
    build.add_argument("report", help="report name")
    build.add_argument("--out", default="docs", help="output directory (default: ./docs)")
    build.add_argument("--force", action="store_true", help="overwrite an existing file")

    sub.add_parser("check", help="build every report from sample(); fail on anything unrendered")
    sub.add_parser("list", help="list reports and components")
    showcase = sub.add_parser("showcase",
        help="write showcase.html beside each component that has a showcase.py")
    showcase.add_argument("name", nargs="?", help="only this component (optional)")
    show = sub.add_parser("show", help="print one component: signature + usage.md")
    show.add_argument("name")

    args, rest = parser.parse_known_args(argv)
    if args.cmd == "build":
        return cmd_build(args.report, rest, args.out, args.force)
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "list":
        return cmd_list()
    if args.cmd == "showcase":
        return cmd_showcase(args.name)
    if args.cmd == "show":
        return cmd_show(args.name)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
