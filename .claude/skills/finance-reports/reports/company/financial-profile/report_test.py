"""Test - `financial-profile` for AMD, with NVDA and INTC as peers.

    python .claude/skills/finance-reports/reports/report_test_runner.py financial-profile
    python .claude/skills/finance-reports/reports/company/financial-profile/report_test.py
        # ... or run it alone

Exercises the skill END TO END: environment resolution, the FMP client, the
arithmetic assertions in `_build_context`, the view's `READS` contract,
`StrictUndefined`, and the full component render. Then it checks the FILE, which
is the half no amount of build-time validation can reach. Exits 0 or 1.

BESIDE THE REPORT IT TESTS, which is the whole point of where it sits. A
directory holding `report.html.j2` IS a report; one that also holds
`report_test.py` HAS a test - the same rule a component follows with
`showcase_controller.py`, and nothing is registered either way. The alternative
was a mirrored tree of test directories, and a mirror is a second copy of the
taxonomy that is free to drift from the first; this repo already deleted a
hand-maintained catalogue for that reason.

Being inside the skill means it travels with it. A skill LINKED into another
project can be tested there, which is the fastest way to find out whether that
project's `environment.json` and `secrets.<env>.json` resolve - the failure a
fresh install actually has.

THE PAGE LANDS IN `report_test_output/`, beside this file, and stays there. Every
report has one. It is tracked as an EMPTY directory - a `.gitkeep`, and a
`.gitignore` rule for everything else in it - so a fresh clone has the folder and
no clone ever has a built page in it.

That is what makes writing inside a published tree safe. jsDelivr serves what is
committed and `git.commit&push.bat` runs `git add .`; a page that is never
committed is never swept up and never served. A skill COPIED into another
project needs the same two lines in that project's `.gitignore`, exactly as
`secrets.*.json` does.

WRITTEN AT ALL, rather than held in memory, because the destination is part of
what is under test. `build()` renders, writes and returns a path - that IS its
contract, and a test that rebuilt the four stages in-process to avoid the disk
would have stopped testing the thing it is named after. Concretely, `local_href`
is computed FROM the destination, so with no destination `assets_resolve` loses
the half that catches a wrong `../` depth.

NOT the system temp directory, which was tried and is wrong on Windows: temp is
on C: while a project usually is not, and `local_href` is empty when no relative
path exists between two drives - so the page would link the CDN alone and render
unstyled against a tag that may not be pushed. Beside the report is the same
volume by construction.

WHY AMD WITH NVDA AND INTC, rather than three names picked for being famous. All
three are semiconductor designers with genuinely different shapes: AMD is
fabless with heavy R&D, INTC carries the capex of its own fabs, NVDA runs
margins several times theirs. That makes `peer-comparison`,
`valuation-multiples` and the segment exhibits show real spread instead of three
near-identical columns - and a rendering fault is only visible where there is
something to render. `--peers none` is the faster smoke test and still exercises
every single-company exhibit; it is not what this file runs.

WHAT IT CANNOT SEE, stated so nobody trusts a green run further than it goes. A
chart whose spec is valid JSON and draws perfectly can still be WRONG - bars
past their track, a clipped label, an axis name over its own ticks, a number
that is simply not the number. `components/showcase_audit.py` catches the first
three for showcases and nothing catches them here yet. **Open the page.**

COST: ~13 network calls and roughly ten seconds, against the dev key, every
time. Nothing is cached on purpose - a report's claim is that it describes the
world at a stated moment, and a cache reproduces a stale figure perfectly and
silently. Numbers therefore differ between runs: never diff two outputs.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Skill root on sys.path by MARKER, so the base imports PACKAGE-QUALIFIED -
# character for character what report_controller.py does beside this file, and
# for the same reason. Not a parent count: this file has already been moved
# once, and the count would have been wrong twice.
SKILL = next(p for p in HERE.parents if (p / "_paths.py").exists())
if str(SKILL) not in sys.path:
    sys.path.insert(0, str(SKILL))

# The version pin every page carries, from the one place that answers where it
# lives - shared with components/, reports/ and service_providers/, because a
# layout question with four answers has three wrong ones.
from _paths import VERSION_FILE                                    # noqa: E402

#: The report, and the arguments it is worth testing with. Both live here rather
#: than on the command line: a test whose inputs are typed each time is a test
#: that was run differently the last time somebody ran it.
REPORT = "financial-profile"
ARGV = ["AMD", "--peers", "NVDA,INTC"]

#: What one run spends. Declared so `reports/report_test_runner.py` can total it
#: up and say so BEFORE running anything - it reads this literal out of the
#: source without importing the module, because importing is where the expense
#: starts.
CALLS = 13

#: Where the page lands: BESIDE THE REPORT, in a directory of its own, which
#: every report has one of. The page stays there to be opened - charts draw at
#: view time, so looking at it is the only check no code here can make.
#:
#: TRACKED BUT EMPTY. `.gitignore` ignores the contents and keeps the `.gitkeep`,
#: so the directory exists in a fresh clone and nothing built in it is ever
#: committed. That is what makes writing inside a PUBLISHED tree safe: jsDelivr
#: serves what is committed, and a page that is never committed is never served.
#: A copied skill needs the same two lines in the consuming project's
#: `.gitignore`, exactly as `secrets.*.json` does - see README.
#:
#: WRITTEN AT ALL, rather than checked in memory, because the destination is
#: part of what is under test. `build()` renders, writes and returns a path -
#: that IS its contract, and a test that rebuilt the four stages in-process to
#: avoid the disk would have stopped testing the thing it is named after. More
#: concretely, `local_href` is computed FROM the destination, so with no
#: destination `assets_resolve` loses the half that catches a wrong `../` depth.
#:
#: NOT the system temp directory, which was tried and is wrong on Windows. Temp
#: is on C: and a project is usually not, and `local_href` is EMPTY when no
#: relative path exists between two drives - so the page would link the CDN
#: alone, render unstyled against a tag that may not be pushed, and leave the
#: local half of `assets_resolve` testing nothing. Beside the report is the same
#: volume by construction, and the shortest honest path back to the assets.
OUT = HERE / "report_test_output"

#: The sections `report.html.j2` declares, in its order. Written out rather than
#: read from the view: a test that derives its expectation from the thing it is
#: testing agrees with it by construction, including when both are wrong. A
#: deleted section should fail here and be deliberately removed from this list.
SECTIONS = ("snapshot", "income", "cash", "position", "per-share",
            "evolution", "peers")

#: How much of a page may be blank before it stops being a page.
#:
#: MEASURED, not guessed. Swept across the 36 built showcase pages that carry a
#: real table, the legitimate high-water marks are `approval-block` at 50% and
#: `cohort-table` at 36% - both correct pages that are simply sparse. So 25%
#: would have failed known-good markup, and the number has to sit above the
#: densest honest page rather than wherever it feels strict. A section whose
#: endpoint returned nothing goes to ~100%, so there is room for both.
BLANK_LIMIT = 0.55


# --------------------------------------------------------------- the checks
# Each takes `(html, out)` and returns a list of complaints. Returning rather
# than asserting, so one run reports EVERY fault it found: a test that stops at
# the first tells you nothing about the second, and the second is the one that
# was going to cost you a rebuild.
#
# `out` is the directory the page was written to, and only `assets_resolve` uses
# it. Uniform anyway, because the alternative is a runner that has to know which
# checks want which arguments - and that knowledge would live nowhere the checks
# themselves can see.

#: The engine's own selector, from js/modules/charts-apache-echarts.js. Any
#: attribute may follow the class - `hidden` always does, `data-height`
#: sometimes.
CHART = re.compile(r'<pre class="chart apache-echarts"[^>]*>(.*?)</pre>', re.S)


def _reject_constant(name):
    """Make `json.loads` as strict as the browser, which is the entire point.

    Python accepts bare `NaN`, `Infinity` and `-Infinity` - JSON does not, and
    `JSON.parse` throws on them. `| tojson` writes them unquoted from any float
    that got there, so without this hook the test would cheerfully parse a page
    on which NOT ONE CHART RENDERS."""
    raise ValueError(f"{name} is not valid JSON")


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


def charts_have_data(html, out):
    """A chart may be perfectly valid and perfectly EMPTY.

    This is the check the arithmetic cannot make. If an endpoint returns a 200
    with an empty list, `_build_context` derives zeros - and its identities
    still hold, because `0 + 0 == 0` satisfies `cost + gross == revenue`. All 48
    `READS` names are present, `StrictUndefined` is satisfied, every spec is
    valid JSON containing `[0, 0, 0, 0]`, and the page renders beautifully with
    flat lines and nothing in it.

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

    Checked on every table rather than on the four this report happens to draw:
    `peer_comparison`, `balance_sheet`, `roll_forward` and `segment_reporting`
    all emit the same shape, and so will the fifth."""
    bodies = re.findall(r"<tbody>(.*?)</tbody>", html, re.S)
    if not bodies:
        return ["no <tbody> in the page - no table rendered"]
    empty = [i for i, body in enumerate(bodies, 1) if "<tr" not in body]
    return [f"table {i} of {len(bodies)}: <tbody> has no rows" for i in empty]


def sections_are_populated(html, out):
    """Every declared section present, and carrying something.

    A section that renders as a heading with nothing under it is what a macro
    handed an empty list looks like: no error, no gap in the contents, just a
    title and white space that a reader scrolls straight past.

    "Carrying something" means a table, a chart, or visible prose - not a byte
    count, which a wrapper div would satisfy on its own. Sections are compared
    to the NEXT one rather than parsed, which is sound here because this report
    nests none inside another; a view that starts using `c.subsection` needs
    this to become a parse."""
    problems = []
    spans = re.split(r'<section id="([^"]+)">', html)
    found = dict(zip(spans[1::2], spans[2::2]))
    for wanted in SECTIONS:
        if wanted not in found:
            problems.append(f"section {wanted!r} is missing entirely")
            continue
        body = found[wanted]
        text = re.sub(r"<[^>]+>", " ", re.sub(r"<h2>.*?</h2>", "", body, flags=re.S))
        if not ("<table" in body or "chart apache-echarts" in body
                or len(text.split()) >= 12):
            problems.append(f"section {wanted!r} rendered as a heading with "
                            f"no table, no chart and no prose beneath it")
    return problems


def symbols_present(html, out):
    """The subject and every peer must actually appear in the page.

    The single strongest signal that the fetch worked. A peer whose payload came
    back empty still gets its column - labelled, present, and blank - so the
    table looks complete while comparing the subject against nothing."""
    wanted = [ARGV[0]] + [p for p in ARGV[-1].split(",") if p.lower() != "none"]
    return [f"{s!r} was requested but appears nowhere in the page"
            for s in wanted if s not in html]


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
    spans = re.split(r'<section id="([^"]+)">', html)
    for name, body in zip(spans[1::2], spans[2::2]):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", body, re.S)
        # Below a handful of cells the ratio is noise: two blanks out of three
        # is 67% and means nothing at all.
        if len(cells) < 6:
            continue
        blank = [c for c in cells
                 if re.sub(r"<[^>]+>", "", c).strip()
                 in ("", "-", "—", "n/m", "n/a", "$0", "0", "0.0%", "0.00")]
        share = len(blank) / len(cells)
        if share > BLANK_LIMIT:
            problems.append(f"section {name!r}: {len(blank)} of {len(cells)} "
                            f"cells ({share:.0%}) are blank, zero or n/m - "
                            f"above the {BLANK_LIMIT:.0%} limit. One is a ratio "
                            f"with no meaning; this many is an endpoint that "
                            f"returned nothing.")
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
    caught here as a string comparison."""
    version = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
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
        cdn = re.search(rf"aifx-finance@([0-9.]+)/[^'\"]*?{re.escape(bundle)}",
                        html)
        if not cdn:
            problems.append(f"{kind}: no CDN fallback for {bundle}")
        elif cdn.group(1) != version["version"]:
            problems.append(f"{kind}: CDN pins {cdn.group(1)}, version.json says "
                            f"{version['version']} - the page was built before "
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


def markup_is_current(html, out):
    """No pre-6.0.0 prefix, and the post-6.0.0 one present.

    `investing-` was the domain prefix before 6.0.0. An occurrence means
    something in the render path still emits old markup against new CSS, which
    degrades SILENTLY: the page loads and simply loses that component's
    styling. The positive half matters as much - zero `fa-` would mean the
    fundamental-analysis components did not render at all."""
    problems = []
    if (stale := html.count("investing-")):
        problems.append(f"{stale} occurrence(s) of the pre-6.0.0 "
                        f"`investing-` prefix")
    if not re.search(r'class="[^"]*\bfa-', html):
        problems.append("no `fa-` class anywhere - "
                        "no fundamental-analysis component rendered")
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


#: Two tiers, because they answer two different questions and the second is the
#: one people actually mean. WELL-FORMED asks whether the page is valid: does it
#: parse, do its links land, is its markup current. CARRIES DATA asks whether
#: there is anything in it - a page can be flawless and empty, and every check
#: in the first tier will pass it.
CHECKS = (
    # is it well-formed?
    charts_parse, assets_resolve, toc_resolves, markup_is_current, no_residue,
    # does it carry data?
    charts_have_data, tables_have_rows, sections_are_populated,
    symbols_present, no_blank_epidemic,
)


# ----------------------------------------------------------------- the run
def main() -> int:
    """Build for real, then check the page. cp1252: plain hyphens in output."""
    from reports.report_builder import ReportBuilder
    from service_providers.config import config_file
    from service_providers.fmp.credentials import describe, resolve

    # Said out loud BEFORE the ~13 calls, exactly as report_builder.main does.
    # Worth reading rather than skipping past: `from $ENVIRONMENT` means a shell
    # variable is overriding environment.json, and `key from $FMP_API_KEY` means
    # a stale one is overriding secrets.dev.json. Both are legal, neither is
    # usually intended, and the only other record of which key paid is a quota.
    name, source = resolve()
    print(f"environment: {name} (from {source})   "
          f"{config_file().name}, {describe()}", flush=True)
    print(f"building {REPORT} {' '.join(ARGV)} -> {OUT}", flush=True)

    # No try/except. A build that raises has already said which stage failed and
    # named the template or the identity; catching it here would replace a
    # useful traceback with the word "failed".
    page = ReportBuilder().build(REPORT, ARGV, OUT)
    html = page.read_text(encoding="utf-8")
    print(f"{page}  ({len(html):,} bytes)\n", flush=True)

    failures = 0
    for check in CHECKS:
        problems = check(html, OUT)
        failures += len(problems)
        print(f"{'FAIL' if problems else 'ok  '}  {check.__name__}")
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


if __name__ == "__main__":
    raise SystemExit(main())
