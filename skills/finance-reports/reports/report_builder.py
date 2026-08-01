"""Build a report from live data, addressed by NAME.

    ReportBuilder().build("financial-profile", ["INTC", "--peers", "none"], out)

    python reports/report_builder.py financial-profile INTC --peers none --out DIR
    python reports/report_builder.py financial-profile INTC --peers AMD,NVDA --out DIR

A name rather than a path, and no longer because they coincide: a report sits
under its SUBJECT (`company/financial-profile`), so the name is the leaf, not
the path. It stays the address because the domain is a taxonomy for READERS —
it says what the report is about — and asking whoever runs one to know which
folder it was filed under would make that shelving load-bearing. Discovery is
recursive and the name must therefore be unique across every domain; `all()`
refuses a duplicate rather than picking one.

(`components/showcase_builder.py` takes `charts/bar` instead, because
components nest two to four levels — same idea at two depths.)

Nothing is registered. A directory holding report.html.j2 IS a report, so
adding one means adding files and nothing else, and the builder does no lookup:
find the directory, path-load the controller, find the ReportController
subclass, hand it the arguments and the destination.

The builder finds the CLASS rather than being told its name. `financial-profile`
holding FinancialProfileReportController is a convention worth keeping, but
deriving one from the other would make the convention load-bearing. A subclass
of ReportController in the module is unambiguous.

The class does the finding; ReportController.build() does the four stages, and
this file never touches Jinja or the network.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPORTS_DIR.parent

# PACKAGE-QUALIFIED, and the skill root on the path to make it resolve. It has
# to match how a leaf controller imports the base: reached under two different
# names the base would be two module objects, and `issubclass` below would fail
# against the wrong one.
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from reports._report_controller import VIEW, ReportController      # noqa: E402

CONTROLLER = "report_controller.py"

#: The one-line `{# purpose: … #}` header every report view declares, matching
#: the convention components/ already follows. Read as TEXT rather than through
#: Jinja: it is a comment, so rendering the template discards it.
PURPOSE = re.compile(r"\{#\s*purpose:\s*(.+?)\s*#\}", re.S)


class ReportBuilder:

    def all(self) -> dict[str, Path]:
        """Every report, discovered recursively: name -> directory.

        Found, never registered — the same rule components use, with
        report.html.j2 in place of component.html.j2."""
        found: dict[str, Path] = {}
        for view in sorted(REPORTS_DIR.rglob(VIEW)):
            name = view.parent.name
            if name in found:
                raise SystemExit(f"duplicate report name: {name!r} "
                                 f"({found[name]} and {view.parent})")
            found[name] = view.parent
        return found

    def parser_for(self, name: str):
        """The controller, and the parser IT declared.

        Public because three callers need the pair: build(), help(), and
        catalog_builder.py, which tabulates what each report accepts."""
        reports = self.all()
        if name not in reports:
            known = ", ".join(sorted(reports)) or "none"
            raise SystemExit(f"unknown report: {name!r}\nknown: {known}")
        directory = reports[name]
        if not (directory / CONTROLLER).exists():
            raise SystemExit(f"{name}: no {CONTROLLER}")

        controller = self._controller(directory)()
        parser = argparse.ArgumentParser(
            prog=f"report_builder.py {name}",
            description=controller.TITLE or name)
        controller._add_args(parser)
        return controller, parser

    def build(self, name: str, argv: list[str], out_dir) -> Path:
        """Build report `name` with `argv` as its own arguments.

        `argv` is whatever the CLI did not claim: the report declares what it
        accepts through _add_args, so the engine never knows what a symbol is.

        Raises rather than returning a code: a report asked for by name and
        not built is a mistake worth stopping for."""
        controller, parser = self.parser_for(name)
        # Before the arguments are parsed and long before ~13 network calls: a
        # malformed report should cost nothing to discover.
        self.purpose(self.all()[name])
        args = parser.parse_args(argv)
        return controller.build(out_dir, **vars(args))

    @staticmethod
    def purpose(directory: Path) -> str:
        """The report's one line, from the `{# purpose: … #}` header of its view.

        REQUIRED, and checked on every build rather than merely conventional.
        components/ enforces the same header — catalog_builder.py fails without
        it — and a report that ships without one is a report nobody can choose
        from a list. Checking it while the convention still holds is what keeps
        a reports catalogue free to write later; discovering it across a dozen
        reports is what makes such a catalogue never get written.

        Returned rather than merely asserted, because the accessor and the
        check are the same operation: whatever lists reports needs this string,
        and nothing else should re-implement reading it."""
        view = directory / VIEW
        match = PURPOSE.search(view.read_text(encoding="utf-8"))
        if not match:
            raise SystemExit(
                f"{directory.name}: {VIEW} has no {{# purpose: ... #}} header. "
                f"One line saying what the report is for, as components do.")
        return " ".join(match.group(1).split())

    def help(self, name: str) -> None:
        """Print what THIS report accepts."""
        self.parser_for(name)[1].print_help()

    @staticmethod
    def _controller(directory: Path) -> type[ReportController]:
        """Path-load <directory>/report_controller.py and return the class.

        By path rather than by import, so a report folder needs no
        __init__.py and the rule stays "a directory containing the view".
        Registered in sys.modules under its own name because a module that
        path-loads without one is invisible to anything resolving a class back
        to its file."""
        source = directory / CONTROLLER
        alias = f"report_{directory.name}".replace("-", "_")

        spec = importlib.util.spec_from_file_location(alias, source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[alias] = module
        spec.loader.exec_module(module)

        found = [value for value in vars(module).values()
                 if isinstance(value, type)
                 and issubclass(value, ReportController)
                 and value is not ReportController]
        if not found:
            raise SystemExit(f"{directory.name}: {CONTROLLER} defines no "
                             f"ReportController subclass")
        if len(found) > 1:
            raise SystemExit(f"{directory.name}: {CONTROLLER} defines "
                             f"{len(found)} controllers: "
                             f"{', '.join(c.__name__ for c in found)}")
        return found[0]


def main(argv: list[str] | None = None) -> int:
    """The terminal entry point.

    parse_known_args, because the arguments after the report name belong to
    the REPORT, not to this parser: it cannot know what a symbol is, and
    should not have to.

    Plain hyphens in anything printed: stdout is cp1252 on Windows, where an
    em dash shows as a replacement character."""
    parser = argparse.ArgumentParser(
        prog="report_builder.py",
        description="build a report from live data",
        epilog="example: python reports/report_builder.py financial-profile "
               "INTC --peers AMD,NVDA --out ./out")
    parser.add_argument("report", help="report name, e.g. financial-profile")
    parser.add_argument("--out", required=True,
                        help="output directory. Required and with no default: "
                             "the page's local asset links are relative to it")
    # `report_builder.py <report> --help` has to reach the REPORT's parser.
    # The arguments after the name belong to it, and argparse fires this
    # parser's own -h during parse_known_args, so the report's would never be
    # seen. Checked before parsing rather than after, for that reason.
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and not argv[0].startswith("-") and {"-h", "--help"} & set(argv[1:]):
        ReportBuilder().help(argv[0])
        return 0

    args, rest = parser.parse_known_args(argv)
    print(ReportBuilder().build(args.report, rest, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
