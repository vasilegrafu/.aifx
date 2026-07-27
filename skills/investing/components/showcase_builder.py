import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import NamedTuple

from jinja2 import Environment, FileSystemLoader, StrictUndefined

COMPONENTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = COMPONENTS_DIR.parent

SHELL = "showcase.master.html.j2"
CONTROLLER = "showcase_controller.py"
VIEW = "showcase.html.j2"


# --------------------------------------------------------------------------
# formatting — the one place a number becomes a string
# --------------------------------------------------------------------------
#
# These live in components/ because only components use them: 20 call sites
# across components/*.j2 and none in reports/*.j2. A report's builder does
# arithmetic and hands over NUMBERS; the macro it calls turns them into
# strings. That is why this directory does not reach outside itself.
#
# In docs-html the author passed pre-formatted strings, which meant every
# generator re-implemented money()/pct()/signed() and two documents could
# disagree about what a thousands separator looks like. One definition,
# applied by the component.
#
# Every filter passes STRINGS THROUGH UNCHANGED. A builder legitimately needs
# to emit "n/m" where a ratio has no meaning (a CAGR from a negative base,
# say), and forcing that through a numeric format would either crash or invent
# a number. Passing it through is the honest behaviour.

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


FILTERS = {"money": f_money, "pct": f_pct, "signed": f_signed, "bps": f_bps,
           "num": f_num, "fmt": f_fmt}


# --------------------------------------------------------------------------
# the component library
# --------------------------------------------------------------------------

class Component(NamedTuple):
    """One entry of components/<cat>/<name>/component.html.j2."""
    name: str        # directory name, e.g. "metric-trend"
    macro: str       # macro/callable name, e.g. "metric_trend"
    path: Path       # the component.html.j2 file


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


def cdn_href() -> str:
    """CDN prefix (version-pinned) — the FALLBACK half of the asset pair.

    Read from version.json at build time, so every generated file is pinned to
    the design-system version it was built against. Published tags are
    immutable, so a page that has left the tree keeps rendering as it did."""
    info = json.loads((SKILL_DIR.parent.parent / "version.json")
                      .read_text(encoding="utf-8"))
    cdn, version = info.get("cdn"), info["version"]
    if not cdn:
        sys.exit('version.json has no "cdn" — every page links it; set it first.')
    return cdn.replace("{version}", version).replace("{skill}", SKILL_DIR.name)


def local_href(out_dir: Path) -> str:
    """Path back to the skill FROM WHERE THE PAGE IS WRITTEN — the local half
    of the asset pair (css/css.loader.html.j2 and js/js.loader.html.j2).

    A showcase lands beside its component, three or four folders deep, and the
    page cannot know how deep that is. Whoever is about to write it does.

    Empty when no relative path exists — a different Windows drive — and the
    template then links the CDN alone rather than an href that cannot resolve."""
    try:
        return Path(os.path.relpath(SKILL_DIR, Path(out_dir).resolve())).as_posix()
    except ValueError:
        return ""


class Showcases:
    """The component library, and everything needed to show it.

    Holds the Jinja environment so it is built ONCE. That matters: building it
    parses every component template in the tree, and the old free-function form
    rebuilt it on each render because nothing owned it."""

    def __init__(self, root: Path = COMPONENTS_DIR):
        self.root = Path(root).resolve()
        self._env: Environment | None = None

    # ---------------------------------------------------------------- find
    def all(self) -> list[Component]:
        """Scan components/ once, recursively.

        components/ is organized in CATEGORY folders that exist purely for
        humans — a component's identity stays its own folder name (macro = name
        with - -> _), so category moves never touch templates. Names must be
        unique across categories."""
        components, seen = [], {}
        for markup in sorted(self.root.rglob("component.html.j2")):
            name = markup.parent.name
            if name in seen:
                raise SystemExit(f"duplicate component name: {name!r} "
                                 f"({seen[name]} and {markup.parent})")
            seen[name] = markup.parent
            components.append(Component(name=name,
                                        macro=name.replace("-", "_"),
                                        path=markup))
        return components

    def find(self, name: str) -> Component | None:
        """By folder name or by macro name — `metric-trend` and `metric_trend`
        both reach the same component, because a view writes one and the
        directory is called the other."""
        for component in self.all():
            if name in (component.name, component.macro):
                return component
        return None

    def showable(self) -> tuple[list[Component], list[str]]:
        """Components that ship BOTH halves, and complaints about the rest.

        A component with a controller and no view (or the reverse) is half
        written. Skipping it silently is how it stays half written, so it comes
        back as a complaint the caller prints."""
        ready, half = [], []
        for c in self.all():
            has_controller = (c.path.parent / CONTROLLER).exists()
            has_view = (c.path.parent / VIEW).exists()
            if has_controller and has_view:
                ready.append(c)
            elif has_controller:
                half.append(f"{c.name}: has {CONTROLLER} but no {VIEW}")
            elif has_view:
                half.append(f"{c.name}: has {VIEW} but no {CONTROLLER}")
        return ready, half

    # ----------------------------------------------------------------- env
    def env(self) -> Environment:
        """Built once, then reused.

        StrictUndefined IS THE POINT. A view reading a key its controller never
        produced would, by default, render an empty string — a tidy blank cell
        in an otherwise perfect table, which nobody notices. That is the same
        failure class as an unbalanced sankey: it draws beautifully and lies.
        With StrictUndefined it raises at build time instead, and since Jinja
        runs only at build time the failure costs nothing and reaches no
        reader.

        Both roots are search paths, components/ FIRST — see the module note."""
        if self._env is not None:
            return self._env
        env = Environment(
            loader=FileSystemLoader([str(self.root), str(SKILL_DIR)]),
            trim_blocks=True, lstrip_blocks=True,
            keep_trailing_newline=True, autoescape=False,
            undefined=StrictUndefined)
        env.filters.update(FILTERS)

        c = SimpleNamespace()
        for component in self.all():
            module = env.get_template(
                component.path.relative_to(self.root).as_posix()).module
            if hasattr(module, component.macro):
                setattr(c, component.macro, getattr(module, component.macro))
        env.globals["c"] = c    # templates call {{ c.<macro>(…) }} — no imports
        self._env = env
        return env

    # -------------------------------------------------------------- render
    def context(self, component: Component) -> dict:
        """Import <name>/showcase_controller.py and return its context().

        By path, so a component folder needs no __init__.py and the discovery
        rule stays 'a directory containing component.html.j2'. The contract is
        one function, context() -> dict; the dict reaches the view as `d`."""
        path = component.path.parent / CONTROLLER
        spec = importlib.util.spec_from_file_location(
            f"showcase_{component.macro}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "context"):
            raise SystemExit(f"{component.name}: {CONTROLLER} defines no context()")
        d = module.context()
        if not isinstance(d, dict):
            raise SystemExit(f"{component.name}: context() returned "
                             f"{type(d).__name__}, expected dict")
        return d

    def compose(self, component: Component,
                local: str | None = None, cdn: str | None = None) -> str:
        """Render one component's view with the data its controller produced.

        Nothing here calls a macro. The view does, through the same `c`
        namespace and the same env a report uses."""
        env = self.env()
        d = self.context(component)
        view = (component.path.parent / VIEW).relative_to(self.root).as_posix()

        return env.get_template(view).render(
            d=SimpleNamespace(**d),
            title=f"{component.name} — showcase",
            component_name=component.name,
            local_href=local if local is not None
            else local_href(component.path.parent),
            cdn_href=cdn if cdn is not None else cdn_href())

    def write(self, name: str | None = None) -> int:
        """Write showcase.html beside every component that ships both halves.

        The output is a build artifact: this is a PUBLIC repo and 110 generated
        pages have no business being served by the CDN. Regenerate them locally
        to browse; the controller and the view are the source."""
        components, half = self.showable()
        if name:
            components = [c for c in components if name in (c.name, c.macro)]
            if not components:
                print(f"no component with a {CONTROLLER} + {VIEW} named {name!r}")
                for complaint in half:
                    print(f"  {complaint}")
                return 1

        for component in components:
            out = component.path.parent / "showcase.html"
            try:
                out.write_text(self.compose(component), encoding="utf-8")
            except Exception as e:          # noqa: BLE001 — report, don't crash
                print(f"  {component.name:<30} FAILED{_blame(e)}: "
                      f"{type(e).__name__}: {e}")
                return 1
            print(f"composed: {out.relative_to(SKILL_DIR)}")

        if not components and not name:
            print(f"no showcases yet — add {CONTROLLER} + {VIEW} "
                  f"beside a component.html.j2")
        for complaint in half:
            print(f"  half-written — {complaint}")
        return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="showcase_builder.py",
        description="render each component's showcase.html from its controller + view")
    parser.add_argument("name", nargs="?",
                        help="only this component (folder or macro name)")
    args = parser.parse_args(argv)
    return Showcases().write(args.name)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
