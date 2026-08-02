"""Showcase controller for the `working-capital` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {metric:str, cells:str[], kind?:total, dir:up|down|flat} -- pre-formatted strings

`dir` IS AN EDITORIAL JUDGEMENT, not a computed sign. Days sales
outstanding rising is bad; days payable outstanding rising is good. The
component cannot know which, so the caller says.
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
    assert_enum, assert_numbers, assert_rows)
from components._showcase_controller import ShowcaseController     # noqa: E402


class WorkingCapitalShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["FY23", "FY24", "FY25"]

        # `dir` says GOOD or BAD, not up or down in value: DPO rising is
        # favourable, DSO rising is not, and both rose.
        rows = [
            {"metric": "Days sales outstanding", "cells": ["52", "56", "61"],
             "dir": "up"},
            {"metric": "Days inventory outstanding", "cells": ["88", "84", "79"],
             "dir": "down"},
            {"metric": "Days payable outstanding", "cells": ["41", "44", "44"],
             "dir": "flat"},
            {"metric": "Cash conversion cycle", "cells": ["99", "96", "96"],
             "kind": "total", "dir": "flat"},
        ]
        return {"periods": periods, "rows": rows}

    def _validate_context(self, d):
        """Cells are PRE-FORMATTED strings, and `dir` is one of three words."""
        rows = d["rows"]
        assert_rows("working-capital", "rows", rows, ("metric", "cells", "dir"))
        for i, r in enumerate(rows):
            assert_enum("working-capital", f"rows[{i}].dir", r["dir"],
                        {"up", "down", "flat"})
            assert len(r["cells"]) == len(d["periods"]), \
                f"working-capital: rows[{i}] {r['metric']!r} has the wrong cell count"
            for j, c in enumerate(r["cells"]):
                assert isinstance(c, str), \
                    (f"working-capital: rows[{i}].cells[{j}] is {c!r}; this "
                     f"component takes PRE-FORMATTED strings and will not "
                     f"format a number for you")

if __name__ == "__main__":
    print(WorkingCapitalShowcaseController().build())
