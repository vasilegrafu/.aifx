"""Test - `financial-profile` for AMD, with NVDA and INTC as peers.

    python .claude/skills/finance-reports/reports/report_test_runner.py financial-profile
    python .claude/skills/finance-reports/reports/company/financial-profile/report_test.py
        # ... or run it alone

Exercises the skill END TO END: environment resolution, the FMP client, the
arithmetic assertions in `_build_context`, the view's `READS` contract,
`StrictUndefined`, and the full component render. Then it checks the FILE, which
is the half no amount of build-time validation can reach. Exits 0 or 1.

FOUR DECLARATIONS AND THE CHECKS ONLY THIS PAGE CAN ANSWER. The ten checks
themselves live in `reports/_report_checks.py`, because every one of them is
generic over "a page this skill generated" - copied here they would be one
report's private reading of `no_blank_epidemic`'s threshold, free to disagree
with the next report's the moment either learned something. That is the
`components/_contracts.py` argument, one level up.

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
that is simply not the number. Every one of those is a fact about the RENDERED
page, and nothing in this skill renders one. **Open the page.**

COST: ~13 network calls and roughly ten seconds, against the dev key, every
time. Nothing is cached on purpose - a report's claim is that it describes the
world at a stated moment, and a cache reproduces a stale figure perfectly and
silently. Numbers therefore differ between runs: never diff two outputs.
"""

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

from reports import _report_checks as checks                       # noqa: E402

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

#: The seven universal checks, plus the three whose expectation is this report's
#: own. Two tiers run inside `_report_checks`, because they answer two different
#: questions and the second is the one people actually mean: WELL-FORMED asks
#: whether the page is valid, CARRIES DATA asks whether there is anything in it
#: - a page can be flawless and empty, and every check in the first tier passes
#: it.
#:
#: `fa-` because this is a company report and its exhibits are the
#: fundamental-analysis family; a portfolio report names `portfolio-` here.
CHECKS = checks.UNIVERSAL + (
    checks.sections_are_populated(SECTIONS),
    checks.symbols_present([ARGV[0], *ARGV[-1].split(",")]),
    checks.markup_is_current("fa-"),
)


if __name__ == "__main__":
    raise SystemExit(checks.run(REPORT, ARGV, OUT, CHECKS))
