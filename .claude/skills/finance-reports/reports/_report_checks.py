"""The checks every report test makes, and the run that makes them.

WHAT A `report_test.py` IS, once this file exists: four declarations and the
checks only THAT report's finished page can answer. Everything here is generic
over "a page this skill generated" - it names no report, no endpoint and no
company - so a second report inherits ten checks instead of copying four
hundred lines of them.

THE ARGUMENT IS `components/_contracts.py`, one level up. Ten charts share one
series/categories contract there, and copying it into ten files would have been
ten claims about one contract, free to disagree the moment one of them learned
something. The same is true of `no_blank_epidemic`'s threshold, of the two
halves of `assets_resolve`, and of what counts as a blank cell: each is one
fact, and a fact wants one home. `reports/REFERENCE.md` refuses a mirrored tree
of test directories for this reason - a mirror is a second copy free to drift -
and check bodies copied per report are that mirror at a smaller scale.

WHAT STAYS IN THE LEAF. Three of the ten cannot be universal, because their
EXPECTATION is the report's own: which sections it declares, which symbols it
was asked for, which domain prefix its components carry. Those are factories
here - called with the report's answer, returning a check of the usual shape -
so the leaf declares a fact rather than reimplementing a loop.

EVERY CHECK IS `(html, out) -> list[str]`, returning complaints rather than
asserting, so one run reports EVERY fault it found: a test that stops at the
first tells you nothing about the second, and the second is the one that was
going to cost you a rebuild. `out` is the directory the page was written to and
only `assets_resolve` uses it - uniform anyway, because the alternative is a
runner that has to know which checks want which arguments, and that knowledge
would live nowhere the checks themselves can see.

A GREEN RUN MEANS THE PAGE IS VALID, NOT THAT IT IS RIGHT. Charts draw at view
time. Nothing in this file has seen one. Open the page.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Skill root on sys.path by MARKER, so the base imports PACKAGE-QUALIFIED -
# character for character what a leaf does, and for the same reason. Not a
# parent count: leaves sit two to four folders deep and a count is wrong at the
# next depth.
SKILL = next(p for p in [HERE, *HERE.parents] if (p / "_paths.py").exists())
if str(SKILL) not in sys.path:
    sys.path.insert(0, str(SKILL))

from _paths import VERSION_FILE                                    # noqa: E402

#: The engine's own selector, from js/modules/charts-apache-echarts.js. Any
#: attribute may follow the class - `hidden` always does, `data-height`
#: sometimes.
CHART = re.compile(r'<pre class="chart apache-echarts"[^>]*>(.*?)</pre>', re.S)

#: How much of a section may be blank before it stops being a section.
#:
#: MEASURED, not guessed. Swept across the 36 built showcase pages that carry a
#: real table, the legitimate high-water marks are `approval-block` at 50% and
#: `cohort-table` at 36% - both correct pages that are simply sparse. So 25%
#: would have failed known-good markup, and the number has to sit above the
#: densest honest page rather than wherever it feels strict. A section whose
#: endpoint returned nothing goes to ~100%, so there is room for both.
#:
#: ONE NUMBER FOR EVERY REPORT, which is the point of it living here: it was
#: measured once against the library, not against `financial-profile`, and a
#: per-report copy would be a second reading of the same sweep.
BLANK_LIMIT = 0.55

#: What a cell holds when it holds nothing. `n/m` is deliberate - `_convert_to_str`
#: emits it where a ratio has no meaning - so these are only damning in bulk.
BLANK_CELLS = ("", "-", "—", "n/m", "n/a", "$0", "0", "0.0%", "0.00")


# ------------------------------------------------------------------ helpers
def _reject_constant(name):
    """Make `json.loads` as strict as the browser, which is the entire point.

    Python accepts bare `NaN`, `Infinity` and `-Infinity` - JSON does not, and
    `JSON.parse` throws on them. `| tojson` writes them unquoted from any float
    that got there, so without this hook a test would cheerfully parse a page
    on which NOT ONE CHART RENDERS."""
    raise ValueError(f"{name} is not valid JSON")


def _numbers(node):
    """Every numeric leaf under an ECharts `data`/`links` value, whatever its shape.

    Twenty-one chart types put their numbers in six different places - a bare
    list for the axis charts, `[x, y]` pairs for scatter, `[o, c, l, h]` for
    candlestick, `{name, value}` for pie and funnel, `{value}` for gauge, and a
    separate `links[].value` for sankey. Walking for numbers costs one function
    and works for the twenty-second."""
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


# ------------------------------------------------- universal - is it well-formed
def charts_parse(html, out):
    """Every chart spec must survive `JSON.parse`.

    This is the failure the documentation calls invisible: the markup is valid,
    the build exits 0, and the browser shows a page of error cards because one
    number was non-finite. It is invisible to a READER of the HTML, not to a
    parser of it."""
    specs = CHART.findall(html)
    if not specs:
        return ["no chart specs in the page at all"]
    problems = []
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

    CDN is pinned at BUILD time, so a page built before `version.json` was
    bumped pins the previous tag and serves the previous behaviour to everyone
    who opens it outside this tree. That is the ordering trap in CLAUDE.md,
    caught here as a string comparison.

    THE CDN PATTERN COMES FROM `version.json`, not from a repository name
    written into this file. A copied skill points its `cdn` at whoever will
    publish its pages, and a check that hard-coded the original owner would
    quietly stop testing the CDN half in every project but this one - passing,
    because the half it could not find was never required."""
    info = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    # {version} is the one variable part; everything else is escaped, so the
    # pattern is whatever this project actually publishes to.
    pinned = re.escape(info["cdn"]).replace(
        re.escape("{version}"), r"([0-9][0-9.]*)")

    problems = []
    for kind, bundle in (("css", "css/bundle.css"), ("js", "js/bundle.js")):
        # `[^":]*` so a URL can never match: the local href is a RELATIVE path,
        # and without excluding the colon this matched the CDN fallback and
        # then reported it as a local file that does not exist. A page with no
        # local half at all looked identical to a page with a broken one.
        local = re.search(rf'(?:href|src)="([^":]*?/{re.escape(bundle)})"', html)
        if not local:
            problems.append(f"{kind}: no local link to {bundle} - the page "
                            f"links the CDN alone and renders unstyled until "
                            f"that tag is pushed")
        elif not (out / local.group(1)).resolve().is_file():
            problems.append(f"{kind}: local href does not resolve to a file - "
                            f"{local.group(1)!r} from {out}")
        cdn = re.search(rf"{pinned}/[^'\"]*?{re.escape(bundle)}", html)
        if not cdn:
            problems.append(f"{kind}: no CDN fallback for {bundle} matching "
                            f"{info['cdn']!r} from {VERSION_FILE}")
        elif cdn.group(1) != info["version"]:
            problems.append(f"{kind}: CDN pins {cdn.group(1)}, version.json says "
                            f"{info['version']} - the page was built before "
                            f"the bump, or not rebuilt after it")
    return problems


def toc_resolves(html, out):
    """Every in-page link must land on an id, and no id may be ambiguous.

    `toc/component.html.j2` claims the contents and the document "cannot
    disagree" because the recipe passes the same list it renders from. It writes
    the two lists SEPARATELY, so today they can - this is what turns that claim
    into an exit code."""
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


# ------------------------------------------------- universal - does it carry data
def charts_have_data(html, out):
    """A chart may be perfectly valid and perfectly EMPTY.

    This is the check the arithmetic cannot make. If an endpoint returns a 200
    with an empty list, `_build_context` derives zeros - and its identities
    still hold, because `0 + 0 == 0` satisfies `cost + gross == revenue`. Every
    `READS` name is present, `StrictUndefined` is satisfied, every spec is valid
    JSON containing `[0, 0, 0, 0]`, and the page renders beautifully with flat
    lines and nothing in it.

    Free to run: `charts_parse` has already parsed these. This only looks."""
    problems = []
    for i, spec in enumerate(CHART.findall(html), 1):
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
    """A `<tbody>` with no `<tr>` is a header over an empty page.

    Checked on every table rather than on the ones a given report happens to
    draw: `peer_comparison`, `balance_sheet`, `roll_forward` and
    `segment_reporting` all emit the same shape, and so will the fifth."""
    bodies = re.findall(r"<tbody>(.*?)</tbody>", html, re.S)
    if not bodies:
        return ["no <tbody> in the page - no table rendered"]
    empty = [i for i, body in enumerate(bodies, 1) if "<tr" not in body]
    return [f"table {i} of {len(bodies)}: <tbody> has no rows" for i in empty]


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
    its own, and the complaint names which one - which is also the difference
    between "something is wrong" and a place to look."""
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


#: The seven that need nothing from the report to be useful. A leaf adds them
#: whole rather than naming them one at a time, so a check added here reaches
#: every report on its next run - which is the entire reason this file exists.
UNIVERSAL = (
    # is it well-formed?
    charts_parse, assets_resolve, toc_resolves, no_residue,
    # does it carry data?
    charts_have_data, tables_have_rows, no_blank_epidemic,
)


# ----------------------------------------------------- configured by the report
# Three checks whose LOGIC is universal and whose EXPECTATION is the report's
# own. Factories, so what the leaf writes is the fact and not the loop, and so
# the thing it appends to CHECKS has the same (html, out) shape as everything
# else.

def sections_are_populated(sections):
    """Every declared section present, and carrying something.

    A section that renders as a heading with nothing under it is what a macro
    handed an empty list looks like: no error, no gap in the contents, just a
    title and white space that a reader scrolls straight past.

    "Carrying something" means a table, a chart, or visible prose - not a byte
    count, which a wrapper div would satisfy on its own.

    `sections` is written out in the leaf rather than read from the view: a test
    that derives its expectation from the thing it is testing agrees with it by
    construction, including when both are wrong. A deleted section should fail
    here and be deliberately removed from that list."""
    def check(html, out):
        problems = []
        found = _sections(html)
        for wanted in sections:
            if wanted not in found:
                problems.append(f"section {wanted!r} is missing entirely")
                continue
            body = found[wanted]
            text = re.sub(r"<[^>]+>", " ",
                          re.sub(r"<h2>.*?</h2>", "", body, flags=re.S))
            if not ("<table" in body or "chart apache-echarts" in body
                    or len(text.split()) >= 12):
                problems.append(f"section {wanted!r} rendered as a heading with "
                                f"no table, no chart and no prose beneath it")
        return problems
    return check


def symbols_present(symbols):
    """The subject and every peer must actually appear in the page.

    The single strongest signal that the fetch worked. A peer whose payload came
    back empty still gets its column - labelled, present, and blank - so the
    table looks complete while comparing the subject against nothing.

    The leaf passes the list because only the leaf knows its report's argument
    shape: `financial-profile` reads a symbol and a comma-separated `--peers`,
    and the next report need not take either."""
    def check(html, out):
        return [f"{s!r} was requested but appears nowhere in the page"
                for s in symbols if s not in html]
    return check


def markup_is_current(prefix):
    """No pre-6.0.0 prefix, and this report's own domain prefix present.

    `investing-` was the domain prefix before 6.0.0 and is universal: an
    occurrence anywhere means something in the render path still emits old
    markup against new CSS, which degrades SILENTLY - the page loads and simply
    loses that component's styling.

    The positive half is the report's, and matters as much: zero `fa-` in a
    company report means the fundamental-analysis components did not render at
    all. A portfolio report asks the same question of `portfolio-`, which is why
    the prefix is an argument and not a constant."""
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


# ----------------------------------------------------------------------- the run
def run(report, argv, out, checks) -> int:
    """Build the report for REAL, then check the file. 0 or 1.

    The build is the expensive half and the point of the exercise: ~13 live
    calls, nothing cached, no fixture and no offline mode. What comes back is a
    page on disk, which is the half no amount of build-time validation reaches.

    Plain hyphens in anything printed: stdout is cp1252 on Windows."""
    from reports.report_builder import ReportBuilder
    from service_providers.config import config_file
    from service_providers.fmp.credentials import describe, resolve

    # Said out loud BEFORE the calls, exactly as report_builder.main does.
    # Worth reading rather than skipping past: `from $ENVIRONMENT` means a shell
    # variable is overriding environment.json, and `key from $FMP_API_KEY` means
    # a stale one is overriding secrets.dev.json. Both are legal, neither is
    # usually intended, and the only other record of which key paid is a quota.
    name, source = resolve()
    print(f"environment: {name} (from {source})   "
          f"{config_file().name}, {describe()}", flush=True)
    print(f"building {report} {' '.join(argv)} -> {out}", flush=True)

    # No try/except. A build that raises has already said which stage failed and
    # named the template or the identity; catching it here would replace a
    # useful traceback with the word "failed".
    page = ReportBuilder().build(report, argv, out)
    html = page.read_text(encoding="utf-8")
    print(f"{page}  ({len(html):,} bytes)\n", flush=True)

    failures = 0
    for check in checks:
        problems = check(html, out)
        failures += len(problems)
        # A factory's closure is named `check`; the factory is what the reader
        # recognises, so name it from the qualified name rather than __name__.
        label = getattr(check, "__qualname__", check.__name__).split(".")[0]
        print(f"{'FAIL' if problems else 'ok  '}  {label}")
        for problem in problems:
            print(f"        {problem}")

    print()
    if failures:
        print(f"FAILED - {failures} problem(s). The page was still written; "
              f"open it and see.")
        return 1
    print("PASSED - and a passing run does not mean the page is RIGHT. "
          "Charts draw at view time; open it.")
    return 0
