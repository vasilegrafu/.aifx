"""Showcase controller for the `sensitivity-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    cols: str[]   rows[] {row_head:str, cells[] {display:str, tone?:low|mid|high, base?:bool}}

MARK THE BASE CASE. A sensitivity grid without it is twenty-five
numbers with no claim attached -- the reader cannot tell which one the report
actually believes, and every cell looks equally endorsed. Exactly one cell
carries base=true below.

The grid is COMPUTED from one formula rather than typed, so it is monotone in
both directions by construction: a hand-typed sensitivity table that reverses
somewhere in the middle is the classic defect here, and no assertion in the
macro would catch it.
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


class SensitivityTableShowcaseController(ShowcaseController):

    def _build_context(self):
        # Gordon growth on free cash flow per share, chosen so the base case
        # lands on the $118 price target the rest of the library uses.
        fcf = 7.48
        waccs = [8.0, 8.5, 9.0, 9.5, 10.0]
        growths = [1.5, 2.0, 2.5, 3.0, 3.5]
        base = (9.0, 2.5)

        grid = {(w, g): fcf * (1 + g / 100) / ((w - g) / 100)
                for w in waccs for g in growths}
        low, high = min(grid.values()), max(grid.values())
        band = (high - low) / 3

        rows = []
        for w in waccs:
            cells = []
            for g in growths:
                value = grid[(w, g)]
                tone = ("low" if value < low + band
                        else "high" if value > high - band else "mid")
                cell = {"display": f"${value:,.0f}", "tone": tone}
                if (w, g) == base:
                    cell["base"] = True
                cells.append(cell)
            rows.append({"row_head": f"{w:.1f}%", "cells": cells})

        return {"cols": [f"{g:.1f}%" for g in growths], "rows": rows,
                "base": f"${grid[base]:,.0f}"}

    def _validate_context(self, d):
        """Exactly one base cell, a full rectangle, and monotone in both
        directions -- value rises with growth and falls as the discount rate
        rises, everywhere."""
        assert_labels("sensitivity-table", "cols", d["cols"])
        assert_all_drawn("sensitivity-table", d, [("cols", ("rows", "base"))])
        assert_rows("sensitivity-table", "rows", d["rows"],
                    ("row_head", "cells"), 2)
        assert_labels("sensitivity-table", "row heads",
                      [r["row_head"] for r in d["rows"]])

        values = []
        bases = 0
        for r in d["rows"]:
            assert len(r["cells"]) == len(d["cols"]), \
                (f"sensitivity-table: {r['row_head']!r} has "
                 f"{len(r['cells'])} cells against {len(d['cols'])} columns; "
                 f"the grid is a rectangle or it is misaligned")
            row_values = []
            for cell in r["cells"]:
                if cell.get("tone"):
                    assert_enum("sensitivity-table",
                                f"{r['row_head']!r} tone", cell["tone"],
                                {"low", "mid", "high"})
                bases += bool(cell.get("base"))
                row_values.append(
                    float(cell["display"].lstrip("$").replace(",", "")))
            assert row_values == sorted(row_values), \
                (f"sensitivity-table: row {r['row_head']!r} is {row_values}; "
                 f"value must rise with terminal growth across every row")
            values.append(row_values)

        assert bases == 1, \
            (f"sensitivity-table: {bases} cells marked base; a grid with none "
             f"makes no claim, and one with two makes two")
        for col in range(len(d["cols"])):
            column = [row[col] for row in values]
            assert column == sorted(column, reverse=True), \
                (f"sensitivity-table: column {d['cols'][col]!r} is {column}; "
                 f"value must fall as the discount rate rises")

if __name__ == "__main__":
    print(SensitivityTableShowcaseController().build())
