"""Generate CATALOG.md — the index that lets a reader CHOOSE a component.

    CatalogBuilder().build()  ->  Path to components/CATALOG.md

    python components/catalog_builder.py

WHY THIS IS GENERATED. An index of 109 items maintained by hand is an index
that is wrong, and a previous one was deleted for exactly that reason — a
dangling reference to it outlived the file. Every component already declares
what it is in the `{# purpose: … #}` header of its own markup, so the catalogue
is READ FROM THE SOURCE and cannot drift: a component that changes its purpose
changes this file on the next build, and one that ships without a purpose fails
the build rather than appearing blank.

WHAT IT IS FOR, and what it is not. usage.md answers "should I use THIS?" —
one file per component, opened once you have a candidate. Nothing answered
"which of the 109?", so choosing meant grepping the tree. This is that missing
step and nothing more: a name, what it is for, and where to read the rules. It
carries no parameters and no examples, because those would be a second copy of
usage.md and would rot.

The output is a BUILD ARTIFACT like every other page here. Regenerate it; do
not edit it.
"""

import argparse
import re
import sys
from pathlib import Path

COMPONENTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = COMPONENTS_DIR.parent

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from components._showcase_controller import MARKUP, VIEW, macro_name   # noqa: E402

PAGE = "CATALOG.md"
USAGE = "usage.md"
CONTROLLER = "showcase_controller.py"

PURPOSE = re.compile(r"\{#\s*purpose:\s*(.+?)\s*#\}", re.S)

#: Category folders in the order a reader meets them, with the one line that
#: says what the group is FOR. Anything not listed still appears, under its own
#: name — the catalogue never silently drops a component because a category was
#: added and this map was not.
CATEGORIES = {
    "foundational": "Any document may use these. Nothing here knows a discipline.",
    "charts": "Engine-backed charts (Apache ECharts). A chart is data; a table is the same data you can read.",
    "domain-specific": "One analysis discipline owns these — fundamental-analysis, portfolio, macro. Classes are namespaced after the directory that owns them (`fa-`, `portfolio-`, `macro-`).",
    "diagrams": "The diagram subsystem: a shared viewport and one engine.",
    "math": "The formula subsystem: KaTeX, with a readable-LaTeX fallback.",
}


class CatalogBuilder:

    def build(self, check: bool = False) -> Path:
        """Write CATALOG.md — or, with check=True, verify it is current.

        THE CHECK IS THE POINT. Generating the catalogue stops its CONTENT
        drifting from the source, but nothing stops the FILE going stale: add a
        component, forget the command, and the index is quietly short by one.
        That is how the previous catalogue died. `--check` turns that silence
        into a non-zero exit a hook or a reviewer can act on.

        Raises rather than returning a code: a component with no purpose is a
        component nobody can choose, and that is worth stopping for."""
        content = self._render()
        output = COMPONENTS_DIR / PAGE
        if check:
            current = output.read_text(encoding="utf-8") if output.exists() else ""
            if current != content:
                raise SystemExit(
                    f"{PAGE} is out of date. Run: python "
                    f"components/catalog_builder.py")
            return output
        output.write_text(content, encoding="utf-8")
        return output

    def _render(self) -> str:
        """The whole file as a string, so build() can either write or compare."""
        found = self._components()
        if not found:
            raise SystemExit(f"no {MARKUP} under {COMPONENTS_DIR}")
        total = sum(len(members) for members in found.values())

        lines = [
            "# Components — catalogue",
            "",
            "_Every component, by what it is for. **Generated** from the "
            "`{# purpose: … #}`_",
            "_header of each `component.html.j2` — do not edit; run "
            "`python components/catalog_builder.py`._",
            "",
            f"{total} components in {len(found)} categories. Narrow to a "
            "candidate here, then read its `usage.md`",
            "for the rules and its parameters. The macro name is the folder "
            "name with hyphens",
            "turned to underscores; a view calls it as `c.<macro>(...)`.",
            "",
        ]
        lines += self._contents(found)

        for category, members in found.items():
            lines += ["", f"## {category}", ""]
            if category in CATEGORIES:
                lines += [CATEGORIES[category], ""]
            lines += ["| component | macro | what it is for | docs |",
                      "|---|---|---|---|"]
            for item in members:
                lines.append(
                    f"| `{item['name']}` | `{item['macro']}` | {item['purpose']} "
                    f"| {item['docs']} |")

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------ read
    def _components(self) -> dict[str, list[dict]]:
        """category -> [component, …], each with its purpose read from source.

        Grouped by TOP-LEVEL folder, which is the grouping a chooser thinks in;
        the deeper nesting under foundational/ and domain-specific/ organizes
        the tree for humans editing it, not for someone picking a component."""
        by_category: dict[str, list[dict]] = {}
        for markup in sorted(COMPONENTS_DIR.rglob(MARKUP)):
            directory = markup.parent
            relative = directory.relative_to(COMPONENTS_DIR)
            category = relative.parts[0]

            match = PURPOSE.search(markup.read_text(encoding="utf-8"))
            if not match:
                raise SystemExit(
                    f"{relative.as_posix()}/{MARKUP} has no "
                    f"{{# purpose: ... #}} header, so it cannot be catalogued")
            purpose = " ".join(match.group(1).split())

            by_category.setdefault(category, []).append({
                "name": directory.name,
                "macro": macro_name(directory.name),
                "purpose": purpose.replace("|", "\\|"),
                "docs": self._docs(directory, relative),
            })

        # Listed categories first, in CATEGORIES order; any others after, so a
        # new category appears rather than vanishing.
        order = [c for c in CATEGORIES if c in by_category]
        order += [c for c in sorted(by_category) if c not in CATEGORIES]
        return {c: sorted(by_category[c], key=lambda i: i["name"]) for c in order}

    @staticmethod
    def _docs(directory: Path, relative: Path) -> str:
        """Links to what a reader reads NEXT, and a marker for what is missing.

        A component with no usage.md is the one case worth showing in the
        catalogue itself: it is choosable and undocumented, which is the state
        this file exists to make visible."""
        links = []
        if (directory / USAGE).exists():
            links.append(f"[usage]({relative.as_posix()}/{USAGE})")
        else:
            links.append("**no usage.md**")
        if (directory / VIEW).exists() and (directory / CONTROLLER).exists():
            links.append(f"[showcase]({relative.as_posix()}/showcase.html)")
        return " · ".join(links)

    @staticmethod
    def _contents(found: dict[str, list[dict]]) -> list[str]:
        counts = " · ".join(f"[{c}](#{c}) {len(m)}" for c, m in found.items())
        return [counts, ""]


def main(argv: list[str] | None = None) -> int:
    """The terminal entry point.

    Plain hyphens in anything printed: stdout is cp1252 on Windows, where an
    em dash shows as a replacement character."""
    parser = argparse.ArgumentParser(
        prog="catalog_builder.py",
        description="regenerate components/CATALOG.md from the purpose headers",
        epilog="example: python components/catalog_builder.py")
    parser.add_argument("--check", action="store_true",
                        help="do not write; exit 1 if CATALOG.md is out of date")
    args = parser.parse_args(argv)

    print(CatalogBuilder().build(check=args.check))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
