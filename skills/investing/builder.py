"""investing — the skill's front door. Two commands, two engines.

Usage:
    python builder.py build <report> <args...> --out DIR
    python builder.py showcase [<component>]

THIS FILE DISPATCHES AND NOTHING ELSE. Each directory owns the code that builds
what lives in it, and each runs perfectly well on its own:

    reports/report.builder.py        the report engine
    components/showcase.builder.py   the showcase engine

    python reports/report.builder.py financial-profile INTC --out DIR
    python components/showcase.builder.py bar

So this exists for one reason: to be the single place that says what this skill
can do. Delete it and both engines still work — you would only lose the list.

THE PIECES. Both sides are the same three files, deliberately:

                    shell                    controller          view
    reports/        report.master.html.j2    report.controller.py    report.html.j2
    components/     showcase.master.html.j2  showcase.controller.py  showcase.html.j2

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
import importlib.util
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent


def _engine(relative: str, alias: str):
    """Load one of the two engines BY PATH.

    Their filenames carry dots — report.builder.py, showcase.builder.py — so
    neither can be reached by `import`. Path-loading is this skill's idiom
    anyway: controllers on both sides are loaded the same way, and no folder
    here is a package or wants an __init__.py."""
    spec = importlib.util.spec_from_file_location(alias, SKILL_DIR / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        reports = _engine("reports/report.builder.py", "report_engine")
        return reports.Reports().build(args.report, rest, args.out, args.force)
    if args.cmd == "showcase":
        showcases = _engine("components/showcase.builder.py", "showcase_engine")
        return showcases.Showcases().write(args.name)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
