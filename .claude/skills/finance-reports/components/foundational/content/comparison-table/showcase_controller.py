"""Showcase controller for the `comparison-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    headers: str[]   rows: cell[][] -- positional matrix; "yes"|"no"|"part" render as marks, anything else as text

THE ROWS ARE A POSITIONAL MATRIX, which is the one shape in this
library with no key to check itself against. A row one cell short does not
raise -- it renders a short row, and every heading after the gap now sits
above the wrong column. The validator enforces the width the headers declare.

"yes", "no" and "part" become marks; ANY other string is printed as text. That
is deliberate, and it is also how a typo becomes a cell reading "Yes".
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import (                                # noqa: E402
    assert_all_drawn, assert_enum, assert_labels, assert_numbers, assert_rows)
from components._showcase_controller import ShowcaseController     # noqa: E402


class ComparisonTableShowcaseController(ShowcaseController):

    def _build_context(self):
        headers = ["", "This library", "Hand-built HTML", "Notebook export"]
        # Column 0 is the row label; the rest are marks or text.
        rows = [
            ["Regenerated from source data", "yes", "no", "yes"],
            ["Assets pinned to a version", "yes", "part", "no"],
            ["Renders without a server", "yes", "yes", "part"],
            ["Component library", "yes", "no", "no"],
            ["Setup cost", "moderate", "none", "low"],
        ]
        return {"headers": headers, "rows": rows}

    def _validate_context(self, d):
        """Every row is exactly as wide as the headers, and every mark-like
        cell is spelled the way the macro recognises.

        Width is the check that matters: the matrix has no keys, so a short
        row silently shifts every cell after it under the wrong heading."""
        assert_all_drawn("comparison-table", d, [("headers", ("rows",))])
        headers = d["headers"]
        assert len(headers) >= 2, "comparison-table: needs something to compare"
        assert_labels("comparison-table", "compared columns", headers[1:])
        assert_labels("comparison-table", "row labels",
                      [r[0] for r in d["rows"]])

        marks = {"yes", "no", "part"}
        for i, row in enumerate(d["rows"]):
            assert len(row) == len(headers), \
                (f"comparison-table: rows[{i}] has {len(row)} cells against "
                 f"{len(headers)} headers; the table renders a short row and "
                 f"every cell after the gap sits under the wrong heading")
            for cell in row[1:]:
                assert isinstance(cell, str) and cell, \
                    f"comparison-table: rows[{i}] has an empty cell"
                # The near-misses: anything that LOOKS like a mark but is not
                # spelled like one prints as text, which reads as a mistake.
                assert cell.lower() not in {"y", "n", "true", "false",
                                            "partial", "-"}, \
                    (f"comparison-table: rows[{i}] cell {cell!r} looks like a "
                     f"mark but only {sorted(marks)} render as one; this would "
                     f"print as literal text")

if __name__ == "__main__":
    print(ComparisonTableShowcaseController().build())
