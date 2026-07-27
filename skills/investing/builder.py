"""investing — the skill's front door. Two commands, two engines.

    python builder.py build <report> <args...> --out DIR
    python builder.py showcase [<component>]

DISPATCH AND NOTHING ELSE. Each directory owns the code that builds what lives
in it, and each runs perfectly well on its own:

    python reports/report_builder.py financial-profile INTC --out DIR
    python components/showcase_builder.py bar

So this file exists to be the single place that says what the skill can do.
Delete it and both engines still work — you would only lose the list.

`components` and `reports` are namespace packages, no __init__.py: ordinary
directories Python can import because the skill root is on sys.path. Both names
are generic, so in a process that put this skill on the path beside some other
`components`, they would shadow one another. Fine for a CLI; it would matter if
anything imported this skill into a larger application.

The architecture — the shell/controller/view shape, which way the dependency
arrow points, what guards the output — is in SKILL.md.
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
