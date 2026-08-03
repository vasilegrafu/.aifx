"""Audit every usage.md against the skeleton in SKILL.md. Exit 0 or 1.

    python .claude/skills/finance-reports/usage_audit.py           # the report
    python .claude/skills/finance-reports/usage_audit.py --check   # exit 1 if any fail

WHY THIS EXISTS. Three conventions in this skill are enforced by an exit code:
a stale showcase fails `showcase_builder.py --check`, a short catalogue fails
`catalog_builder.py --check`, and a malformed page fails its report test. The
usage.md skeleton was the fourth convention and the only one enforced by
nothing -- and it is the only one that drifted. When this file was written, 62
of 110 usage.md carried no `## Rules` heading, which SKILL.md calls not
optional. That is not a coincidence about those 62 authors; it is what an
unenforced convention converges to. A rule with no exit code is a preference.

WHAT IT CHECKS, and deliberately no more than SKILL.md actually mandates:

  1. every component and every report HAS a usage.md
  2. it opens with an H1
  3. it carries `## Rules`

SKILL.md says the heading names "may vary where the item genuinely differs -- a
report has no markup and a component has no fetch", so `## Markup` and
`## Build it` are NOT asserted; only `## Rules`, which the same paragraph calls
not optional. Checking the soft ones would fail files that are right, and an
audit that cries wolf gets an ignore rule rather than a fix.

Nor is the H1 required to equal the folder name. Two files deliberately differ
(`apache-echarts` titles itself `chart-apache-echarts`), naming the reader's
term rather than the directory's, and forcing those two would be churn no
reader benefits from. What matters is that the file opens by saying what it is.

WHY IT SITS AT THE SKILL ROOT rather than as twins under components/ and
reports/. "There is no top-level dispatcher" is a real rule here and this does
not break it: a dispatcher routes work to the engine that owns it, and this
builds nothing, writes nothing and owns nothing. The convention itself is
documented ONCE, in one section of SKILL.md, as a statement about all 110 files
on both sides -- so the check that enforces it is one file for the same reason
`_report_validation.py` is one file. Two copies of these three assertions would be
two claims about one skeleton, free to disagree the moment either side learned
something.

The discovery rule is the same one everything else here uses: a directory
holding `component.html.j2` IS a component and a directory holding
`report.html.j2` IS a report, so nothing is registered and a new item is
audited the day it appears, without this file being told.
"""

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from _paths import CDN_SUFFIX                                        # noqa: E402

#: How to invoke this from the PROJECT ROOT, where a session starts. Derived
#: from where the skill actually sits, so a copy under another name still
#: prints a command that runs.
COMMAND = f"python {CDN_SUFFIX}/usage_audit.py"

USAGE = "usage.md"

#: What makes a directory an item, per side. The marker IS the definition --
#: the same rule `catalog_builder.py` and `showcase_builder.py` discover by.
MARKERS = {
    "component": ("components", "component.html.j2"),
    "report": ("reports", "report.html.j2"),
}

RULES = "## Rules"


def items() -> list[tuple[str, Path]]:
    """Every component and report in the tree, sorted, as (kind, directory)."""
    found = []
    for kind, (subdir, marker) in MARKERS.items():
        for path in sorted((SKILL_DIR / subdir).rglob(marker)):
            found.append((kind, path.parent))
    return found


def failures(directory: Path) -> list[str]:
    """What is wrong with this item's usage.md, as a list of reasons.

    Empty means it conforms. Each reason is phrased as the thing to DO, since
    the reader of this output is about to fix it."""
    usage = directory / USAGE
    if not usage.exists():
        return [f"no {USAGE} at all -- every component and every report has one"]

    text = usage.read_text(encoding="utf-8")
    reasons = []

    first = next((line for line in text.splitlines() if line.strip()), "")
    if not first.startswith("# "):
        reasons.append("does not open with an H1 naming what this is")

    if RULES not in text:
        extra = ""
        if "Rules:" in text:
            extra = (" -- the content is already there under a prose 'Rules:'"
                     " lead-in, so this is a heading, not a rewrite")
        reasons.append(f"no `{RULES}` heading{extra}")

    return reasons


def audit() -> tuple[int, list[str]]:
    """Audit the tree. Returns (items checked, lines to print)."""
    lines, broken = [], 0
    for kind, directory in items():
        reasons = failures(directory)
        if not reasons:
            continue
        broken += 1
        relative = directory.relative_to(SKILL_DIR).as_posix()
        lines.append(f"{relative}  ({kind})")
        lines.extend(f"    {reason}" for reason in reasons)

    total = len(items())
    lines.append("")
    lines.append(f"{total - broken} of {total} usage.md conform, {broken} do not.")
    return broken, lines


def main(argv: list[str] | None = None) -> int:
    """The terminal entry point.

    Plain hyphens in anything printed: stdout is cp1252 on Windows, where an
    em dash shows as a replacement character."""
    parser = argparse.ArgumentParser(
        prog="usage_audit.py",
        description="check every usage.md against the skeleton in SKILL.md",
        epilog=f"example: {COMMAND} --check")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if any usage.md fails (for a hook or CI)")
    args = parser.parse_args(argv)

    broken, lines = audit()
    print("\n".join(lines))
    return 1 if (broken and args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())
