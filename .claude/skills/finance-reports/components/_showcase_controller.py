"""The base every component's showcase controller extends.

CONTRACT — a subclass writes one method:

    class ChartBarShowcaseController(ShowcaseController):
        def _build_context(self) -> dict: ...

    ChartBarShowcaseController().build()  ->  Path to showcase.html

A controller assembles a view model and hands it over. It emits NO markup and
calls NO macro; the view does both, so a showcase exercises the same path a
report does.

Everything else the base works out from the SUBCLASS's own file — which
component this is, what its view is called, where the page goes. That is why a
leaf controller stays what `bar` is: a dict, built line by line.

Show the states that matter — the default, and the ones where the component has
to make a decision (a legend appears past one series, an axis name widens the
margin). Keys should read as what the data IS, not as which case uses it, so
the view can recombine them.

Around that base sits everything a page needs to render: the Jinja env, the `c`
macro namespace, the number filters the macros format with, and the asset pair
every generated page links. reports/ borrows them rather than building a second
set, which is what makes a macro draw identically on both sides.
"""

import json
import os
import sys
from functools import cache
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from _paths import CDN_SUFFIX, SKILL_DIR, VERSION_FILE

COMPONENTS_DIR = Path(__file__).resolve().parent

MARKUP = "component.html.j2"        # what makes a directory a component
VIEW = "showcase.html.j2"
PAGE = "showcase.html"              # the build artifact


# --------------------------------------------------------------------------
# assets — where a generated page's CSS and JS come from
# --------------------------------------------------------------------------
#
# Two hrefs, read by css/css.loader.html.j2 and js/js.loader.html.j2 at the
# skill root. Every page links the bundle LOCAL-FIRST with the pinned CDN as an
# onerror fallback, so a file inside the tree renders from the working copy and
# the same file emailed to someone renders from jsDelivr.
#
# THIS IS THE ONLY COPY. reports/ imports both, the same way it imports env().

def cdn_href() -> str:
    """CDN prefix (version-pinned) — the FALLBACK half of the asset pair.

    Read at build time, so every generated file is pinned to the version it was
    built against; published tags are immutable, so a page that has left the
    tree keeps rendering as it did.

    THE OBLIGATION THIS CREATES: change anything under css/ or js/ and the
    version has to be bumped and tagged, or pages falling back to the CDN keep
    getting the previous behaviour while local ones move on."""
    info = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    cdn, version = info.get("cdn"), info["version"]
    if not cdn:
        sys.exit(f'{VERSION_FILE} has no "cdn" — every page links it; set it first.')
    # A config left half-migrated would otherwise put a literal "{skill}" in
    # every URL on the page — a 404 that only shows up once a file has left
    # the tree, which is the one place nobody is looking.
    if "{skill}" in cdn:
        sys.exit(f'{VERSION_FILE} still carries "{{skill}}"; the skill path is '
                 f'derived from the tree now, so drop it from the template.')
    return cdn.replace("{version}", version).rstrip("/") + "/" + CDN_SUFFIX


def local_href(out_dir: Path) -> str:
    """Path back to the skill FROM WHERE THE PAGE IS WRITTEN — the local half
    of the asset pair.

    A showcase lands beside its component, three or four folders deep, and the
    page cannot know how deep that is. Whoever is about to write it does, which
    is why a report's --out is required and has no default.

    Empty when no relative path exists — a different Windows drive — and the
    loaders then link the CDN alone rather than an href that cannot resolve."""
    try:
        return Path(os.path.relpath(SKILL_DIR, Path(out_dir).resolve())).as_posix()
    except ValueError:
        return ""


# --------------------------------------------------------------------------
# formatting — the one place a number becomes a string
# --------------------------------------------------------------------------

def _convert_to_str(fn):
    def wrapped(value, *args, **kwargs):
        if isinstance(value, str) or value is None:
            return "" if value is None else value
        return fn(value, *args, **kwargs)
    return wrapped


@_convert_to_str
def f_money(v, digits=0):
    return f"{v:,.{digits}f}"


@_convert_to_str
def f_pct(v, digits=1):
    return f"{v:.{digits}f}%"


@_convert_to_str
def f_signed(v, digits=0):
    return f"{v:+,.{digits}f}"


@_convert_to_str
def f_bps(v):
    return f"{v:+,.0f} bps"


@_convert_to_str
def f_num(v, digits=2):
    return f"{v:,.{digits}f}"


FORMATS = {"money": f_money, "pct": f_pct, "signed": f_signed,
           "bps": f_bps, "num": f_num, "raw": lambda v: v}


def f_fmt(value, spec="num", *a, **kw):
    """Dispatch by name, so a component can take `fmt="money"` as an argument.

    Named `fmt` rather than `format` because Jinja already ships a `format`
    filter (printf-style) and shadowing it would break any template using it."""
    if spec not in FORMATS:
        raise ValueError(f"unknown format {spec!r}: one of {', '.join(FORMATS)}")
    return FORMATS[spec](value, *a, **kw)


#: What the env exposes. Derived from FORMATS rather than restated, so the two
#: cannot drift — `fmt` dispatches over exactly the names available directly.
#: `raw` comes along as the identity filter, which is what it already meant.
FILTERS = {**FORMATS, "fmt": f_fmt}


@cache
def env() -> Environment:
    """The Jinja environment, built ONCE for the whole process.

    Building it parses every component template in the tree, so 109
    controllers each making their own would parse the tree 109 times. Cached
    at module level rather than on the instance because the environment
    belongs to the library, not to whoever is rendering — which is also what
    lets reports/ borrow this exact one instead of a second configuration that
    happens to match.

    TWO ROOTS, components/ FIRST. A view extends _showcase.master.html.j2 and a
    component.html.j2 imports charts/_render.html.j2 — both named from here.
    The master then includes css/css.loader.html.j2 and js/js.loader.html.j2,
    which live at the skill root. One root cannot resolve both.

    StrictUndefined IS THE POINT. A view reading a key its controller never
    produced would, by default, render an empty string — a tidy blank cell in
    an otherwise perfect table, which nobody notices. It raises at build time
    instead, and since Jinja runs only at build time that failure costs
    nothing and reaches no reader.
    """
    environment = Environment(
        loader=FileSystemLoader([str(COMPONENTS_DIR), str(SKILL_DIR)]),
        trim_blocks=True, lstrip_blocks=True,
        keep_trailing_newline=True, autoescape=False,
        undefined=StrictUndefined)
    environment.filters.update(FILTERS)

    # `c` — every component's macro on one namespace, so a view calls
    # {{ c.bar(...) }} with no import of its own. The WHOLE tree, not just the
    # component being shown: _showcase.master.html.j2 reaches for
    # c.metadata_header, which lives in foundational/structure/.
    c = SimpleNamespace()
    for markup in sorted(COMPONENTS_DIR.rglob(MARKUP)):
        macro = macro_name(markup.parent.name)
        module = environment.get_template(
            markup.relative_to(COMPONENTS_DIR).as_posix()).module
        if hasattr(module, macro):
            setattr(c, macro, getattr(module, macro))
    environment.globals["c"] = c
    return environment


def macro_name(name: str) -> str:
    """`metric-trend` is the folder; `metric_trend` is what a view calls."""
    return name.replace("-", "_")


class ShowcaseController:
    """Build one component's showcase page.

    Subclass, write _build_context(), call build(). Nothing else is required —
    and nothing here is component-specific, so nothing here needs overriding.
    """

    # ------------------------------------------------------------- subclass
    def _build_context(self) -> dict:
        """The view model. Reaches showcase.html.j2 as `d`."""
        raise NotImplementedError(
            f"{type(self).__name__} defines no _build_context()")

    def _validate_context(self, d: dict) -> None:
        """Assert the context matches the {# data: … #} contract of the macro
        the view calls. Raise on anything wrong; return nothing.

        OPTIONAL, and it does the half StrictUndefined cannot. A key the view
        reads and the controller never wrote already raises at render. What
        does not is a key present and WRONG — a series carrying five points
        against four categories draws a chart that looks finished and is
        silently missing a bar. Same failure class as an unbalanced sankey: it
        renders beautifully and lies.

        So the checks worth writing are the ones about agreement between
        values, not about presence."""

    # ---------------------------------------------------------------- where
    @property
    def directory(self) -> Path:
        """The component's folder, taken from the SUBCLASS's own file.

        Read off the function that subclass wrote — not __file__, which names
        this base module and would put every showcase in components/, and not
        inspect.getfile(cls), which resolves a class through
        sys.modules[cls.__module__] and so raises "is a built-in class" for a
        controller loaded BY PATH, since importlib registers nothing. A code
        object carries its filename with it and needs no such lookup, so a
        controller reached by import and one reached by path land in the same
        place."""
        for klass in type(self).__mro__:
            if klass is ShowcaseController:
                break               # reached the base without finding one
            own = klass.__dict__.get("_build_context")
            if own is not None:
                return Path(own.__code__.co_filename).resolve().parent
        raise NotImplementedError(
            f"{type(self).__name__} defines no _build_context()")

    @property
    def name(self) -> str:
        """The component's identity IS its folder name — categories above it
        exist for humans, so moving one between them touches no template."""
        return self.directory.name

    # ---------------------------------------------------------------- build
    def build(self) -> Path:
        """Render the view with the controller's data; write the page beside
        the component.

        A showcase always lands next to what it shows, so unlike a report it
        has no destination to be told — the asset hrefs follow from where it
        goes.

        Raises rather than returning a code: a showcase that cannot be built
        is a mistake worth stopping for, and the caller owns the reporting."""
        directory = self.directory
        try:
            view = (directory / VIEW).relative_to(COMPONENTS_DIR).as_posix()
        except ValueError:
            raise SystemExit(
                f"{type(self).__name__}: {directory} is not under "
                f"{COMPONENTS_DIR}") from None
        if not (directory / VIEW).exists():
            raise SystemExit(f"{self.name}: no {VIEW} beside the controller")

        d = self._build_context()
        if not isinstance(d, dict):
            raise SystemExit(f"{self.name}: _build_context() returned "
                             f"{type(d).__name__}, expected dict")
        self._validate_context(d)

        html = env().get_template(view).render(
            d=SimpleNamespace(**d),
            title=f"{self.name} — showcase",
            component_name=self.name,
            local_href=local_href(directory),
            cdn_href=cdn_href())

        output_file = directory / PAGE
        output_file.write_text(html, encoding="utf-8")
        return output_file
