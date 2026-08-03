"""What a built report is checked for, and how the page says so on its face.

    validate(html, out, sections=…, prefix=…, expected=…)  ->  Validation

RUN AT BUILD TIME, NOT BY A TEST, and the difference is quota. The test this
replaced built a report OF ITS OWN - a fixed AMD/NVDA/INTC, ~13 live calls - and
checked that. So confidence in a report you actually wanted cost twenty-six
calls and validated the wrong page: the one the test built, never the one you
were about to send. Checking the render in `build()` costs nothing, happens
every time, and the page that gets checked is the page you are holding.

THE RESULT IS RENDERED INTO THE DOCUMENT, at the top, before the cover. Printing
to stdout was the other option and it repeats the mistake this repository keeps
finding: a signal nobody is obliged to read. Charts draw at view time, so a
human has to open the page anyway - putting the findings there means the
feedback arrives where the eye already is. It also means a report that left this
tree carries its own warning, which matters more than the developer case: a
reader cannot tell a healthy page from one whose endpoint returned nothing,
because `0 + 0 == 0` satisfies every identity a controller asserts.

TWO SEVERITIES, and the line between them is what the finding depends on.

    ERROR    the page is BROKEN. A spec that will not parse, an asset half that
             does not resolve, a link to an id nothing carries, a Jinja
             delimiter that reached the file. None of these depend on which
             company was asked for - they are defects in the render path, and
             they are defects for every input.

    WARNING  the page renders, and its CONTENT is thin. An empty chart, a table
             with no rows, a section that is mostly blank. Against the fixed
             input of a test these meant "the code broke". Against arbitrary
             input they usually mean "this symbol has little data", which is a
             fact about the world and not a fault - so they are said loudly and
             they do not fail the build.

Without that split a legitimately sparse company would fail its own report.

THE BANNER IS NOT ITSELF VALIDATED. `build()` renders, validates that string,
and only then renders again carrying the findings - so what these checks measure
is the document, never the notice about the document. The second render happens
even on a clean page, so the all-clear can say how many checks actually ran: an
ABSENT banner cannot distinguish "validated and clean" from "validation never
ran", and neither can one claiming zero checks.
"""

import json
import re
import sys
from collections import namedtuple
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Skill root on sys.path by MARKER, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "The preamble every leaf
# starts with".
SKILL = next(p for p in [HERE, *HERE.parents] if (p / "_paths.py").exists())
if str(SKILL) not in sys.path:
    sys.path.insert(0, str(SKILL))

from _paths import VERSION_FILE                                    # noqa: E402

#: One finding. `check` is what the reader recognises, `message` is where to
#: look - both reach the page, because "something is wrong" is not actionable.
Problem = namedtuple("Problem", "check message")

#: What `build()` hands the template. `ok` is a convenience for the common case;
#: `checked` exists so the all-clear comment can say how much was actually run.
Validation = namedtuple("Validation", "errors warnings checked at ok")

#: The engine's own selector, from js/modules/charts-apache-echarts.js. Any
#: attribute may follow the class - `hidden` always does, `data-height`
#: sometimes.
CHART = re.compile(r'<pre class="chart apache-echarts"[^>]*>(.*?)</pre>', re.S)

#: How much of a section may be blank before it stops being a section.
#:
#: MEASURED, not guessed. Swept across the built showcase pages that carry a
#: real table, the legitimate high-water marks are `approval-block` at 50% and
#: `cohort-table` at 36% - both correct pages that are simply sparse. So 25%
#: would have failed known-good markup, and the number has to sit above the
#: densest honest page rather than wherever it feels strict. A section whose
#: endpoint returned nothing goes to ~100%, so there is room for both.
BLANK_LIMIT = 0.55

#: What a cell holds when it holds nothing. `n/m` is deliberate - `_convert_to_str`
#: emits it where a ratio has no meaning - so these are only damning in bulk.
BLANK_CELLS = ("", "-", "—", "n/m", "n/a", "$0", "0", "0.0%", "0.00")


# ------------------------------------------------------------------ helpers
def _reject_constant(name):
    """Make `json.loads` as strict as the browser, which is the entire point.

    Python accepts bare `NaN`, `Infinity` and `-Infinity` - JSON does not, and
    `JSON.parse` throws on them. `| tojson` writes them unquoted from any float
    that got there, so without this hook validation would cheerfully pass a page
    on which NOT ONE CHART RENDERS."""
    raise ValueError(f"{name} is not valid JSON")


def _numbers(node):
    """Every numeric leaf under an ECharts `data`/`links` value, whatever its shape.

    Chart types put their numbers in six different places - a bare list for the
    axis charts, `[x, y]` pairs for scatter, `[o, c, l, h]` for candlestick,
    `{name, value}` for pie and funnel, `{value}` for gauge, and a separate
    `links[].value` for sankey. Walking for numbers costs one function and works
    for the next one."""
    if isinstance(node, bool):
        return                          # a bool is an int in Python; not data
    if isinstance(node, (int, float)):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _numbers(value)
    elif isinstance(node, (list, tuple)):
        for value in node:
            yield from _numbers(value)


def _sections(html):
    """`id -> body` for every `<section>` in the page, in document order.

    Split rather than parsed, which is sound while no report nests a section
    inside another; a view that starts using `c.subsection` needs this to
    become a parse, and both checks that call it will be wrong until it does."""
    spans = re.split(r'<section id="([^"]+)">', html)
    return dict(zip(spans[1::2], spans[2::2]))


# --------------------------------------------------------------- ERROR checks
# Broken regardless of what was asked for. Every one of these is a defect in the
# render path, so none of them can be explained away by a thin data set.

def charts_parse(html, out):
    """Every chart spec that EXISTS must survive `JSON.parse`.

    The failure this catches is the one the documentation calls invisible: the
    markup is valid, the build exits 0, and the browser shows a page of error
    cards because one number was non-finite. It is invisible to a READER of the
    HTML, not to a parser of it.

    Absence is not an error here - a report with no chart is a warning, below,
    because whether it should have had one is a question about its data."""
    problems = []
    specs = CHART.findall(html)
    for i, spec in enumerate(specs, 1):
        try:
            json.loads(spec, parse_constant=_reject_constant)
        except ValueError as e:
            problems.append(f"chart {i} of {len(specs)}: spec is not JSON - {e}")
    return problems


def assets_resolve(html, out):
    """Both halves of the asset pair, and both ways they break.

    LOCAL is computed relative to wherever the file was written, so it is
    exactly what moving the destination breaks - resolved against the real
    filesystem rather than pattern-matched, because a path with the right SHAPE
    and the wrong depth looks identical.

    THE CDN PATTERN COMES FROM `version.json`, not from a repository name
    written into this file. A copied skill points its `cdn` at whoever will
    publish its pages, and a check that hard-coded the original owner would
    quietly stop testing the CDN half in every project but this one - passing,
    because the half it could not find was never required."""
    info = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    pinned = re.escape(info["cdn"]).replace(
        re.escape("{version}"), r"([0-9][0-9.]*)")

    problems = []
    for kind, bundle in (("css", "css/bundle.css"), ("js", "js/bundle.js")):
        # `[^":]*` so a URL can never match: the local href is a RELATIVE path,
        # and without excluding the colon this matched the CDN fallback and
        # then reported it as a local file that does not exist.
        local = re.search(rf'(?:href|src)="([^":]*?/{re.escape(bundle)})"', html)
        if not local:
            problems.append(f"{kind}: no local link to {bundle} - the page "
                            f"links the CDN alone and renders unstyled until "
                            f"that tag is pushed")
        elif not (out / local.group(1)).resolve().is_file():
            problems.append(f"{kind}: local href does not resolve to a file - "
                            f"{local.group(1)!r} from {out}")
        if not re.search(rf"{pinned}/[^'\"]*?{re.escape(bundle)}", html):
            problems.append(f"{kind}: no CDN fallback for {bundle} matching "
                            f"{info['cdn']!r} from {VERSION_FILE}")
    return problems


def toc_resolves(html, out):
    """Every in-page link must land on an id, and no id may be ambiguous.

    `toc/component.html.j2` claims the contents and the document "cannot
    disagree" because the recipe passes the same list it renders from. It writes
    the two lists SEPARATELY, so today they can - this is what turns that claim
    into a finding on the page."""
    ids = re.findall(r'\sid="([^"]+)"', html)
    problems = [f"duplicate id: {i!r}" for i in sorted(set(ids))
                if ids.count(i) > 1]
    targets = set(ids)
    for href in sorted(set(re.findall(r'href="#([^"]+)"', html))):
        if href not in targets:
            problems.append(f"link to #{href} - no section carries that id")
    return problems


def no_residue(html, out):
    """Nothing half-rendered reached the file.

    `StrictUndefined` catches a key the controller never wrote. It does not
    catch a template that emitted its own delimiters, or a `None` that survived
    a filter and printed as the word."""
    problems = []
    for token in ("{{", "{%", "{#"):
        if token in html:
            problems.append(f"unrendered Jinja delimiter {token!r} in the output")
    for token in (">None<", ">Undefined<", ">nan<", ">NaN<"):
        if token in html:
            problems.append(f"{token!r} rendered as visible text")
    return problems


def sections_present(sections):
    """Every section the report DECLARES actually rendered.

    Missing entirely is structural: the view names a section the render did not
    produce, which is a fault in the page whatever the data was. Present but
    empty is a different question and is a warning.

    `sections` is declared on the controller rather than read back from the
    view: a check that derives its expectation from the thing it is checking
    agrees with it by construction, including when both are wrong."""
    def check(html, out):
        found = _sections(html)
        return [f"section {s!r} is missing entirely" for s in sections
                if s not in found]
    return check


def markup_is_current(prefix):
    """No pre-6.0.0 prefix, and this report's own domain prefix present.

    `investing-` was the domain prefix before 6.0.0: an occurrence anywhere
    means something in the render path still emits old markup against new CSS,
    which degrades SILENTLY - the page loads and simply loses that component's
    styling.

    The positive half matters as much: zero `fa-` in a company report means the
    fundamental-analysis components did not render at all. Neither half depends
    on the data, which is why both are errors."""
    def check(html, out):
        problems = []
        if (stale := html.count("investing-")):
            problems.append(f"{stale} occurrence(s) of the pre-6.0.0 "
                            f"`investing-` prefix")
        if not re.search(rf'class="[^"]*\b{re.escape(prefix)}', html):
            problems.append(f"no `{prefix}` class anywhere - no component from "
                            f"that family rendered")
        return problems
    return check


# ------------------------------------------------------------- WARNING checks
# The page renders; what is in it is thin. Against a fixed test input these
# meant the code broke. Against whatever was asked for today they usually mean
# the data is sparse - so they are said loudly and they do not fail anything.

def charts_have_data(html, out):
    """A chart may be perfectly valid and perfectly EMPTY.

    This is the check the arithmetic cannot make. If an endpoint returns a 200
    with an empty list, `_build_context` derives zeros - and its identities
    still hold, because `0 + 0 == 0` satisfies `cost + gross == revenue`. Every
    `READS` name is present, `StrictUndefined` is satisfied, every spec is valid
    JSON containing `[0, 0, 0, 0]`, and the page renders beautifully with flat
    lines and nothing in it."""
    specs = CHART.findall(html)
    if not specs:
        return ["no chart specs in the page at all"]
    problems = []
    for i, spec in enumerate(specs, 1):
        try:
            option = json.loads(spec, parse_constant=_reject_constant)
        except ValueError:
            continue                    # charts_parse owns that complaint
        series = option.get("series") or []
        if not series:
            problems.append(f"chart {i}: no series - it will draw an empty frame")
            continue
        for j, one in enumerate(series, 1):
            where = f"chart {i}" + (f" series {j}" if len(series) > 1 else "")
            payload = [one.get("data"), one.get("links")]
            if not any(p for p in payload):
                problems.append(f"{where}: no data points")
                continue
            values = list(_numbers(payload))
            if not values:
                problems.append(f"{where}: data carries no numbers at all")
            elif not any(values):
                problems.append(f"{where}: every one of its {len(values)} "
                                f"values is zero - an endpoint returned nothing")
    return problems


def tables_have_rows(html, out):
    """A `<tbody>` with no `<tr>` is a header over an empty page."""
    bodies = re.findall(r"<tbody>(.*?)</tbody>", html, re.S)
    if not bodies:
        return ["no <tbody> in the page - no table rendered"]
    return [f"table {i} of {len(bodies)}: <tbody> has no rows"
            for i, body in enumerate(bodies, 1) if "<tr" not in body]


def no_blank_epidemic(html, out):
    """Blanks are legitimate one at a time and damning in bulk.

    `_convert_to_str` emits "n/m" deliberately where a ratio has no meaning, and
    a missing value is not a zero - so a handful of these is the design working,
    not a fault. What is a fault is a SECTION of them.

    PER SECTION, not per page, and the difference is the whole check. A real
    build measures 19% blank across the page against a limit that has to sit
    above 50% to clear known-good markup - so one dead endpoint, taking its
    section to ~100%, would move a seven-section page to about 33% and never
    fire. Measured where the failure actually lands, that same section trips on
    its own, and the complaint names which one."""
    problems = []
    for name, body in _sections(html).items():
        cells = re.findall(r"<td[^>]*>(.*?)</td>", body, re.S)
        # Below a handful of cells the ratio is noise: two blanks out of three
        # is 67% and means nothing at all.
        if len(cells) < 6:
            continue
        blank = [c for c in cells
                 if re.sub(r"<[^>]+>", "", c).strip() in BLANK_CELLS]
        share = len(blank) / len(cells)
        if share > BLANK_LIMIT:
            problems.append(f"section {name!r}: {len(blank)} of {len(cells)} "
                            f"cells ({share:.0%}) are blank, zero or n/m - "
                            f"above the {BLANK_LIMIT:.0%} limit. One is a ratio "
                            f"with no meaning; this many is an endpoint that "
                            f"returned nothing.")
    return problems


def sections_are_populated(sections):
    """A declared section that rendered as a heading over nothing.

    What a macro handed an empty list looks like: no error, no gap in the
    contents, just a title and white space a reader scrolls straight past.

    "Carrying something" means a table, a chart, or visible prose - not a byte
    count, which a wrapper div would satisfy on its own."""
    def check(html, out):
        problems = []
        found = _sections(html)
        for wanted in sections:
            if wanted not in found:
                continue                # sections_present owns that complaint
            body = found[wanted]
            text = re.sub(r"<[^>]+>", " ",
                          re.sub(r"<h2>.*?</h2>", "", body, flags=re.S))
            if not ("<table" in body or "chart apache-echarts" in body
                    or len(text.split()) >= 12):
                problems.append(f"section {wanted!r} rendered as a heading with "
                                f"no table, no chart and no prose beneath it")
        return problems
    return check


def text_present(expected):
    """Everything the request named must actually appear in the page.

    The single strongest signal that the fetch worked. A peer whose payload came
    back empty still gets its column - labelled, present, and blank - so the
    table looks complete while comparing the subject against nothing.

    The controller supplies the list, because only it knows its own argument
    shape: `financial-profile` reads a symbol and a comma-separated `--peers`,
    and the next report need not take either."""
    def check(html, out):
        return [f"{s!r} was requested but appears nowhere in the page"
                for s in expected if s not in html]
    return check


# ---------------------------------------------------------------- the run
def validate(html, out, sections=(), prefix="", expected=()) -> Validation:
    """Check a rendered report. Never raises, never writes, returns findings.

    The three configured checks are skipped rather than failed when the
    controller declares nothing for them: a report with no `SECTIONS` is a
    report that has not made that promise, and inventing an expectation for it
    would be a check agreeing with itself."""
    errors_run = [charts_parse, assets_resolve, toc_resolves, no_residue]
    warnings_run = [charts_have_data, tables_have_rows, no_blank_epidemic]

    if prefix:
        errors_run.append(markup_is_current(prefix))
    if sections:
        errors_run.append(sections_present(sections))
        warnings_run.append(sections_are_populated(sections))
    if expected:
        warnings_run.append(text_present(expected))

    def gather(checks):
        found = []
        for check in checks:
            # A factory's closure is named `check`; the factory is what the
            # reader recognises, so name it from the qualified name.
            label = getattr(check, "__qualname__", check.__name__).split(".")[0]
            found.extend(Problem(label, m) for m in check(html, out))
        return found

    errors, warnings = gather(errors_run), gather(warnings_run)
    return Validation(
        errors=errors, warnings=warnings,
        checked=len(errors_run) + len(warnings_run),
        at=datetime.now().isoformat(timespec="seconds"),
        ok=not (errors or warnings))


#: What the FIRST render is handed, before anything has been checked. The
#: environment runs with `StrictUndefined`, so the name has to exist even on the
#: pass whose whole purpose is to produce the string that gets validated.
NOT_YET = Validation(errors=(), warnings=(), checked=0, at="", ok=True)
