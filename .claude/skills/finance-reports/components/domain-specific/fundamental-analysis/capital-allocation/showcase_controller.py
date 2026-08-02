"""Showcase controller for the `capital-allocation` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {use:str, cells:str[], cumulative:str, share:num}   source_line? {label, cells, cumulative}

THE SHARES SUM TO 100 across the uses, because every dollar of the
source went somewhere. A schedule where they do not is describing a different
pool of money than the one it names.
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


class CapitalAllocationShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["FY23", "FY24", "FY25"]

        rows = [
            {"use": "Capital expenditure", "cells": ["980", "1,180", "1,420"],
             "cumulative": "3,580", "share": 23.4},
            {"use": "Acquisitions", "cells": ["120", "340", "905"],
             "cumulative": "1,365", "share": 8.9},
            {"use": "Buybacks", "cells": ["1,640", "1,985", "2,640"],
             "cumulative": "6,265", "share": 40.9},
            {"use": "Debt repaid", "cells": ["720", "450", "860"],
             "cumulative": "2,030", "share": 13.3},
            {"use": "Cash retained", "cells": ["310", "1,184", "575"],
             "cumulative": "2,069", "share": 13.5},
        ]
        source_line = {"label": "Operating cash flow",
                       "cells": ["3,770", "5,139", "6,400"],
                       "cumulative": "15,309"}
        return {"periods": periods, "rows": rows, "source_line": source_line}

    def _validate_context(self, d):
        """Shares sum to 100 -- every dollar of the source went somewhere."""
        rows = d["rows"]
        assert_rows("capital-allocation", "rows", rows,
                    ("use", "cells", "cumulative", "share"))
        for i, r in enumerate(rows):
            assert len(r["cells"]) == len(d["periods"]), \
                f"capital-allocation: rows[{i}] has the wrong cell count"
            assert_numbers("capital-allocation", f"rows[{i}].share", [r["share"]])
        total = sum(r["share"] for r in rows)
        assert abs(total - 100) < 0.4, \
            (f"capital-allocation: shares sum to {total:.1f}, not 100; the "
             f"table would describe a pool of money other than the one its "
             f"source line names")

if __name__ == "__main__":
    print(CapitalAllocationShowcaseController().build())
