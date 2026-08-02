"""Showcase controller for the `heatmap` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    cols: str[]   rows[] {row_head:str, cells[] {display:str, level:-3..3}}

LEVEL IS THE COLOUR, DISPLAY IS THE NUMBER, and nothing in the macro
makes them agree. A cell reading -4.1% with a level of +2 renders green, and
no assertion anywhere would notice. Both are derived from one return here, by
one function, so they cannot disagree.

blocks.css styles hm-p1..p3, hm-n1..n3 and hm-z0 -- a level outside -3..3
renders as an unstyled cell.
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


class HeatmapShowcaseController(ShowcaseController):

    def _build_context(self):
        # Monthly total return, in per cent. Level is DERIVED from the same
        # number that is printed, so the colour cannot contradict the text.
        returns = {
            "2023": [4.2, -1.8, 3.1, 0.4, -2.6, 5.7,
                     1.2, -0.3, -4.1, 2.8, 6.3, -1.1],
            "2024": [-3.4, 2.2, 0.9, 4.8, -0.2, 1.6,
                     -5.2, 3.3, 0.7, -2.9, 1.4, 2.0],
            "2025": [2.6, 0.1, -1.3, 3.9, 4.4, -0.8,
                     2.1, -3.7, 1.0, 0.5, -2.2, 5.1],
        }
        cols = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        rows = [{"row_head": year,
                 "cells": [{"display": f"{r:+.1f}", "level": self._level(r)}
                           for r in values]}
                for year, values in returns.items()]

        # A short row. The macro pads to the column count with hm-empty cells,
        # which is what a part-finished year should look like -- not a zero.
        partial = [{"row_head": "2026",
                    "cells": [{"display": f"{r:+.1f}", "level": self._level(r)}
                              for r in (1.9, -0.4, 3.2, 2.7)]}]
        return {"cols": cols, "rows": rows, "partial": partial,
                "returns": returns}

    @staticmethod
    def _level(r):
        """A return in per cent -> a colour step in -3..3.

        Bands, not a linear scale: the eye reads six steps, and a continuous
        ramp across twelve months of noise says nothing."""
        for edge, step in ((4.0, 3), (2.0, 2), (0.5, 1)):
            if abs(r) >= edge:
                return step if r > 0 else -step
        return 0

    def _validate_context(self, d):
        """Every level is in range and agrees in SIGN with the number printed.

        The disagreement this catches is silent: the cell is coloured by
        `level` and read by `display`, and a green cell over a negative number
        is simply believed."""
        assert_labels("heatmap", "cols", d["cols"])
        assert_all_drawn("heatmap", d,
                         [("cols", ("rows", "partial", "returns"))])
        for key in ("rows", "partial"):
            assert_rows("heatmap", key, d[key], ("row_head", "cells"))
            assert_labels("heatmap", f"{key} heads",
                          [r["row_head"] for r in d[key]])
            for r in d[key]:
                assert len(r["cells"]) <= len(d["cols"]), \
                    (f"heatmap: {r['row_head']!r} has {len(r['cells'])} cells "
                     f"against {len(d['cols'])} columns; the surplus is "
                     f"dropped without a word")
                for cell in r["cells"]:
                    level = cell["level"]
                    assert level in range(-3, 4), \
                        (f"heatmap: {r['row_head']!r} cell {cell['display']!r} "
                         f"has level {level}; outside -3..3 there is no rule "
                         f"in blocks.css and the cell renders unstyled")
                    value = float(cell["display"])
                    assert (value > 0) == (level > 0) or level == 0, \
                        (f"heatmap: {r['row_head']!r} shows {cell['display']} "
                         f"coloured at level {level}; the colour and the "
                         f"number disagree and the reader believes the colour")

if __name__ == "__main__":
    print(HeatmapShowcaseController().build())
