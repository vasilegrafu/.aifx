"""Showcase controller for the `cohort-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {cohort:str, size:str, cells[] {display:str, level:0-5}}

COHORTS ARE A TRIANGLE, NOT A RECTANGLE. The newest cohort has only
been observed for one period, so its row is short -- and the macro pads with
cohort-empty cells rather than zeros, which is the whole point: a blank is
"not yet known" and a 0 is "everybody left".

LEVEL IS 0..5 and content.css styles cohort-l0..cohort-l5. It is derived from
the same retention figure that is printed, so the shade cannot contradict the
number.
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


class CohortTableShowcaseController(ShowcaseController):

    def _build_context(self):
        # Retention per cohort, in per cent, by months since signup. Each
        # row is shorter than the one above it: that is what a cohort table
        # looks like when it is honest about how long it has been watching.
        periods = ["M0", "M3", "M6", "M9", "M12", "M18"]
        observed = [
            ("FY24 Q1", "3,180", [100, 82, 74, 69, 66, 61]),
            ("FY24 Q2", "3,640", [100, 84, 77, 72, 70]),
            ("FY24 Q3", "4,010", [100, 86, 80, 76]),
            ("FY24 Q4", "4,255", [100, 88, 83]),
            ("FY25 Q1", "4,720", [100, 89]),
            ("FY25 Q2", "5,090", [100]),
        ]
        rows = [{"cohort": cohort, "size": size,
                 "cells": [{"display": f"{v}%", "level": self._level(v)}
                           for v in values]}
                for cohort, size, values in observed]
        return {"periods": periods, "rows": rows}

    @staticmethod
    def _level(v):
        """Retention per cent -> a shade in 0..5, banded rather than linear."""
        for edge, level in ((90, 5), (80, 4), (70, 3), (60, 2), (45, 1)):
            if v >= edge:
                return level
        return 0

    def _validate_context(self, d):
        """Rows shorten monotonically, retention never rises, and every level
        is one content.css has a rule for."""
        assert_labels("cohort-table", "periods", d["periods"])
        assert_all_drawn("cohort-table", d, [("periods", ("rows",))])
        assert_rows("cohort-table", "rows", d["rows"],
                    ("cohort", "size", "cells"), 2)
        assert_labels("cohort-table", "cohorts",
                      [r["cohort"] for r in d["rows"]])

        lengths = [len(r["cells"]) for r in d["rows"]]
        assert lengths == sorted(lengths, reverse=True), \
            (f"cohort-table: row lengths {lengths} do not shorten; a newer "
             f"cohort cannot have been observed for longer than an older one")
        for r in d["rows"]:
            assert len(r["cells"]) <= len(d["periods"]), \
                (f"cohort-table: {r['cohort']!r} has more cells than periods; "
                 f"the surplus is dropped silently")
            values = [float(c["display"].rstrip("%")) for c in r["cells"]]
            assert values == sorted(values, reverse=True), \
                (f"cohort-table: {r['cohort']!r} retention {values} rises; a "
                 f"cohort cannot regain a customer it has already lost")
            for cell, v in zip(r["cells"], values):
                assert cell["level"] in range(0, 6), \
                    (f"cohort-table: {r['cohort']!r} cell {cell['display']!r} "
                     f"has level {cell['level']}; content.css styles "
                     f"cohort-l0..l5 and nothing else")
                assert cell["level"] == self._level(v), \
                    (f"cohort-table: {r['cohort']!r} prints {cell['display']} "
                     f"but is shaded at level {cell['level']}; the colour and "
                     f"the number disagree")

if __name__ == "__main__":
    print(CohortTableShowcaseController().build())
