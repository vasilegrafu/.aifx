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
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from _paths import CDN_SUFFIX, SKILL_DIR, VERSION_FILE, owning_directory

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
# onerror fallback. THIS IS THE ONLY COPY — reports/ imports both.

def cdn_href() -> str:
    """CDN prefix (version-pinned) — the FALLBACK half of the asset pair.

    THE OBLIGATION THIS CREATES: change anything under css/ or js/ and the
    version has to be bumped and tagged, or pages falling back to the CDN keep
    getting the previous behaviour while local ones move on."""
    # A COPIED skill lands in a project that has none of the four root files,
    # and this is the first one any build touches -- so it is where an install
    # that skipped them gets caught. Unhandled, it is a FileNotFoundError
    # naming a path the reader has never heard of.
    if not VERSION_FILE.exists():
        sys.exit(f'{VERSION_FILE} not found -- every generated page pins its '
                 f'assets to it. Create it beside .claude/:\n'
                 f'  {{"version": "1.0.0", "cdn": '
                 f'"https://cdn.jsdelivr.net/gh/<owner>/<repo>@{{version}}"}}')
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


#: Pixels per tick-label character, and the smallest gap worth reserving.
#: Measured against the chart font rather than calculated: the axis font is
#: ~11px and its digits are tabular, so 7px a character is close and errs wide.
_AXIS_CHAR_PX = 7
_AXIS_GAP_FLOOR = 46


def f_axis_gap(values, stacked=False, floor=_AXIS_GAP_FLOOR):
    """Left margin for a ROTATED Y-AXIS NAME, in pixels.

    THE BUG THIS EXISTS FOR. ECharts' `containLabel` reserves room for tick
    LABELS but not for the axis NAME, which sits at a fixed `nameGap` from the
    axis. A hardcoded 46 is right for "12.1" and draws straight through
    "60,000" — the chart renders, nothing raises, and the two texts simply
    overlap. `waterfall` hit it first; ten other charts carried the same
    constant against data that had not yet grown wide enough.

    It is a FUNCTION rather than ten copies of the arithmetic because the
    Jinja to express it is fiddly (a stacked axis reaches the column TOTAL,
    not the largest point) and ten copies of fiddly arithmetic is ten chances
    to get it subtly different.

    `values` is either a flat list of numbers or the `series` list itself —
    [{"name": …, "points": [...]}, …]. With `stacked=True` the magnitude is
    the per-category sum, because that is where the axis actually reaches.
    Mixed signs sum as absolutes, which OVER-estimates: erring wide costs a
    few pixels of margin, erring narrow costs a collision.
    """
    rows = [row["points"] if isinstance(row, dict) else row for row in values]
    if not rows:
        return floor

    def numbers(row):
        return [v for v in row if isinstance(v, (int, float))
                and not isinstance(v, bool)]

    if not isinstance(rows[0], (list, tuple)):
        magnitudes = [abs(v) for v in numbers(rows)]
    elif stacked:
        width = max(len(row) for row in rows)
        magnitudes = [sum(abs(v) for row in rows
                          for v in numbers(row[i:i + 1]))
                      for i in range(width)]
    else:
        magnitudes = [abs(v) for row in rows for v in numbers(row)]

    if not magnitudes:
        return floor
    # The widest tick as it is PRINTED: its digits, plus one character for
    # each thousands separator the formatter will insert.
    digits = len(str(int(max(magnitudes)))) or 1
    characters = digits + (digits - 1) // 3
    return max(floor, 24 + characters * _AXIS_CHAR_PX)


#: What the env exposes. Derived from FORMATS rather than restated, so the two
#: cannot drift — `fmt` dispatches over exactly the names available directly.
#: `raw` comes along as the identity filter, which is what it already meant.
FILTERS = {**FORMATS, "fmt": f_fmt, "axis_gap": f_axis_gap}


@cache
def env() -> Environment:
    """The Jinja environment, built ONCE for the whole process.

    Building it parses every component template in the tree, so a per-instance
    env would reparse the whole library once per controller. Cached at module
    level because the environment belongs to the library, not to whoever is
    rendering — which is what lets reports/ borrow this exact one.

    TWO ROOTS, components/ FIRST. A view extends _showcase.master.html.j2 and a
    component.html.j2 imports charts-apache-echarts/_render.html.j2 — both named from here.
    The master then includes css/css.loader.html.j2 and js/js.loader.html.j2,
    which live at the skill root. One root cannot resolve both.

    StrictUndefined IS THE POINT. A key the view reads and the controller never
    wrote would otherwise render as an empty string — a tidy blank cell nobody
    notices. It raises at build time instead, where the failure reaches no
    reader.
    """
    environment = Environment(
        loader=FileSystemLoader([str(COMPONENTS_DIR), str(SKILL_DIR)]),
        trim_blocks=True, lstrip_blocks=True,
        keep_trailing_newline=True, autoescape=False,
        undefined=StrictUndefined)
    environment.filters.update(FILTERS)

    # `c` — every component's macro on one namespace, so a view calls
    # {{ c.charts_apache_echarts_bar(...) }} with no import of its own. The
    # WHOLE tree, not just the component being shown: _showcase.master.html.j2 reaches for
    # c.metadata_header, which lives in foundational/structure/.
    #
    # ONE FLAT NAMESPACE, so the tree's category folders buy no room: two
    # components anywhere in it whose folder names reach the same macro would
    # land on the same attribute, and the second would silently replace the
    # first in every view that calls it. That failure renders — valid markup,
    # wrong exhibit — which is the one kind this library cannot afford, so the
    # collision is refused here rather than resolved by sort order. Keyed on the
    # MACRO rather than the folder because the mapping is not injective:
    # `cash-flow` and `cash_flow` are two directories and one attribute.
    c = SimpleNamespace()
    source: dict[str, Path] = {}
    for markup in sorted(COMPONENTS_DIR.rglob(MARKUP)):
        macro = macro_name(markup.parent.relative_to(COMPONENTS_DIR).as_posix())
        if macro in source:
            raise SystemExit(
                f"duplicate component name: {macro!r} is claimed by both "
                f"{source[macro]} and {markup.parent}.\n"
                f"A component's folder name IS its macro on the shared `c` "
                f"namespace, so two cannot coexist under any categories. "
                f"Rename one for what it is, not for where it lives.")
        source[macro] = markup.parent
        module = environment.get_template(
            markup.relative_to(COMPONENTS_DIR).as_posix()).module
        if hasattr(module, macro):
            setattr(c, macro, getattr(module, macro))
    environment.globals["c"] = c
    return environment


#: Top-level directories that NAMESPACE their members. Every chart engine has a
#: `bar` and every diagram engine a `diagram`, so a kind's leaf name identifies
#: it only WITHIN its engine -- `charts-apache-echarts/bar` and
#: `charts-plotly/bar` are two macros writing two different specs, and one flat
#: attribute cannot hold both. Nowhere else needs this: `foundational/` and
#: `domain-specific/` nest for the benefit of whoever edits the tree, and their
#: leaf names are unique library-wide, so `c.badge` stays `c.badge`.
NAMESPACED = ("charts-", "diagrams-")


def macro_name(relative) -> str:
    """The attribute a view calls, from a component's path under components/.

    `foundational/blocks/metric-trend` -> `metric_trend`: the leaf, because it
    is unique. `charts-apache-echarts/bar` -> `charts_apache_echarts_bar`:
    qualified by its engine, because the leaf alone is not.

    Takes the path rather than the folder name so the two callers -- the `c`
    namespace and the catalogue -- cannot disagree about what a view types.
    """
    parts = PurePosixPath(relative).parts
    if len(parts) > 1 and parts[0].startswith(NAMESPACED):
        return f"{parts[0]}_{parts[-1]}".replace("-", "_")
    return parts[-1].replace("-", "_")


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

        OPTIONAL, and it does the half StrictUndefined cannot: a key present
        and WRONG. Five points against four categories draws a chart that looks
        finished and is silently missing a bar — so the checks worth writing
        are about agreement between values, not presence."""

    # ---------------------------------------------------------------- where
    @property
    def directory(self) -> Path:
        """The component's folder, taken from the SUBCLASS's own file."""
        return owning_directory(self, ShowcaseController)

    @property
    def name(self) -> str:
        """The component's identity IS its folder name — categories above it
        exist for humans, so moving one between them touches no template."""
        return self.directory.name

    # ---------------------------------------------------------------- build
    def render(self) -> str:
        """The page as a string. Everything build() does except writing.

        Split out so `--check` can compare a page against what it WOULD be
        without touching the tree: a check that writes is a build."""
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

        return env().get_template(view).render(
            d=SimpleNamespace(**d),
            title=f"{self.name} — showcase",
            component_name=self.name,
            local_href=local_href(directory),
            cdn_href=cdn_href())

    def build(self) -> Path:
        """Render the view with the controller's data; write the page beside
        the component.

        A showcase always lands next to what it shows, so unlike a report it
        has no destination to be told. Raises rather than returning a code —
        the caller owns the reporting."""
        output_file = self.directory / PAGE
        output_file.write_text(self.render(), encoding="utf-8")
        return output_file
