"""Generate CATALOG.md — the index that lets a reader CHOOSE a report.

    CatalogBuilder().build()  ->  Path to reports/CATALOG.md

    python reports/catalog_builder.py

The twin of components/catalog_builder.py, and it answers the same question one
level up: usage.md tells you whether to run THIS report, once you have a
candidate; nothing told you which of them to consider. With one report that is
not yet a real question — it becomes one the moment two reports could plausibly
answer the same request, and a report costs ~13 network calls, so choosing
wrong is more expensive here than picking the wrong component.

Built now rather than later on purpose: the conventions it depends on hold
while there is one report to keep honest, and every report from here on inherits
them. An index that arrives after a dozen reports is an index someone has to
backfill, which is the same reason the components catalogue is generated rather
than written.

READ FROM THE SOURCE, so it cannot drift:

    purpose      the {# purpose: … #} header of report.html.j2, via
                 ReportBuilder.purpose() — the same accessor the build checks
    title        TITLE on the controller class
    arguments    the parser the controller itself declares in _add_args

Nothing here is restated by hand, so a report that changes what it takes
changes this file on the next build.

The output is a BUILD ARTIFACT. Regenerate it; do not edit it.
"""

import argparse
import sys
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPORTS_DIR.parent

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from reports.report_builder import ReportBuilder                # noqa: E402

PAGE = "CATALOG.md"
USAGE = "usage.md"


class CatalogBuilder:

    def build(self, check: bool = False) -> Path:
        """Write CATALOG.md — or, with check=True, verify it is current.

        THE CHECK IS THE POINT. Generating the catalogue stops its CONTENT
        drifting from the source, but nothing stops the FILE going stale: add a
        report, forget the command, and the index is quietly short by one.
        `--check` turns that silence into a non-zero exit a hook or a reviewer
        can act on.

        Raises rather than returning a code: a report that cannot be described
        is a report nobody can choose, and that is worth stopping for."""
        content = self._render()
        output = REPORTS_DIR / PAGE
        if check:
            current = output.read_text(encoding="utf-8") if output.exists() else ""
            if current != content:
                raise SystemExit(f"{PAGE} is out of date. Run: python "
                                 f"reports/catalog_builder.py")
            return output
        output.write_text(content, encoding="utf-8")
        return output

    def _render(self) -> str:
        """The whole file as a string, so build() can either write or compare."""
        reports = ReportBuilder()
        found = reports.all()
        if not found:
            raise SystemExit(f"no report.html.j2 under {REPORTS_DIR}")

        lines = [
            "# Reports — catalogue",
            "",
            "_Every report, by what it argues. **Generated** from each report's "
            "own_",
            "_declarations — do not edit; run `python reports/catalog_builder.py`._",
            "",
            f"{len(found)} report{'' if len(found) == 1 else 's'}. Narrow to a "
            "candidate here, then read its `usage.md` for what",
            "it fetches, what that costs, and what its assertions guarantee.",
            "",
            "```bash",
            "python reports/report_builder.py <report> <args...> --out DIR",
            "```",
            "",
            "| report | title | what it argues | arguments | docs |",
            "|---|---|---|---|---|",
        ]

        for name in sorted(found):
            row = self._row(reports, name, found[name])
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------ read
    @staticmethod
    def _row(reports: ReportBuilder, name: str, directory: Path) -> list[str]:
        """One report, described entirely from what it declares itself."""
        purpose = reports.purpose(directory)        # raises if the header is gone
        controller, parser = reports.parser_for(name)

        docs = (f"[usage]({name}/{USAGE})" if (directory / USAGE).exists()
                else "**no usage.md**")
        return [f"`{name}`",
                controller.TITLE or "—",
                purpose.replace("|", "\\|"),
                f"`{CatalogBuilder._arguments(parser)}`",
                docs]

    @staticmethod
    def _arguments(parser: argparse.ArgumentParser) -> str:
        """What the report accepts, taken from the parser IT declared.

        format_usage() rather than reaching into parser internals, then the
        prog and the always-present -h dropped: what is left is exactly the
        part that differs between reports, which is the only part worth putting
        in a table."""
        usage = " ".join(parser.format_usage().split())
        usage = usage.removeprefix("usage: ").removeprefix(parser.prog).strip()
        return usage.replace("[-h] ", "").strip() or "none"


def main(argv: list[str] | None = None) -> int:
    """The terminal entry point.

    Plain hyphens in anything printed: stdout is cp1252 on Windows, where an
    em dash shows as a replacement character."""
    parser = argparse.ArgumentParser(
        prog="catalog_builder.py",
        description="regenerate reports/CATALOG.md from what each report declares",
        epilog="example: python reports/catalog_builder.py")
    parser.add_argument("--check", action="store_true",
                        help="do not write; exit 1 if CATALOG.md is out of date")
    args = parser.parse_args(argv)

    print(CatalogBuilder().build(check=args.check))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
