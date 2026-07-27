"""investing — the skill's front door. Two commands, two engines.

Usage:
    python builder.py build <report> <args...> --out DIR
    python builder.py showcase [<component>]

THIS FILE DISPATCHES AND NOTHING ELSE. Each directory owns the code that builds
what lives in it, and each runs perfectly well on its own:

    reports/report_builder.py        the report engine
    components/showcase_builder.py   the showcase engine

    python reports/report_builder.py financial-profile INTC --out DIR
    python components/showcase_builder.py bar

NAMESPACE PACKAGES, NO __init__.py. `components` and `reports` are ordinary
directories that Python treats as namespace packages because the skill root is
on sys.path. Both names are generic: in a process that put this skill on the
path alongside some other `components` package, they would shadow one another.
That is fine for a CLI and would matter if anything ever imported this skill
into a larger application.

So this exists for one reason: to be the single place that says what this skill
can do. Delete it and both engines still work — you would only lose the list.

THE PIECES. Both sides are the same three files, deliberately:

                    shell                    controller              view
    reports/        report.master.html.j2    report_controller.py    report.html.j2
    components/     showcase.master.html.j2  showcase_controller.py  showcase.html.j2

Python files use underscores so they can be imported; templates keep the dots.

A CONTROLLER BUILDS DATA. A VIEW EMITS MARKUP. The controller returns a plain
dict, handed to the view as `d`, and the view is the only thing that calls a
macro. The builder never emits markup; the template never fetches; a component
never knows which report called it. Break any one of those and the other two
stop being replaceable.

WHICH WAY THE ARROW POINTS. components/ owns the macros, the number filters
they use, and the Jinja environment that exposes them as `c`. reports/ borrows
that environment. Reports depend on components, never the reverse — which is
why components/ builds its showcases without knowing reports exist.

WHAT GUARDS THE OUTPUT. Building a report requires the network and a key, so
there is no offline check: shape()'s assertions and StrictUndefined fire during
a real build, and nowhere else. `showcase` is the only command that renders
anything without a key, and it covers components, not reports.
"""

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))          # so both engines resolve by name

from components.showcase_builder import Showcases        # noqa: E402
from reports.report_builder import Reports               # noqa: E402


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="builder.py",
        description="generate investing reports and component showcases")
    sub = parser.add_subparsers(dest="cmd")

    build = sub.add_parser("build", help="build a report from live data")
    build.add_argument("report", help="report name (or a unique prefix)")
    build.add_argument("--out", required=True,
                       help="output directory — required: the report's local "
                            "asset links are relative to it")
    build.add_argument("--force", action="store_true",
                       help="overwrite an existing file")

    showcase = sub.add_parser(
        "showcase",
        help="write showcase.html beside each component that has a controller + view")
    showcase.add_argument("name", nargs="?", help="only this component (optional)")

    args, rest = parser.parse_known_args(argv)
    if args.cmd == "build":
        return Reports().write(args.report, rest, args.out, args.force)
    if args.cmd == "showcase":
        return Showcases().write(args.name)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
