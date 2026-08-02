"""Showcase controller for the `income-statement` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:num[], kind:section|detail|subtotal|total, note?:str}

RAW NUMBERS, not strings -- the macro formats, and it colours a
negative cell itself. Passing "1,104" as text would defeat both. `kind` is what
the CSS reads to tell a section heading from a detail line from a total.
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


class IncomeStatementShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["FY24", "FY25"]

        # Ties to the sankey and waterfall showcases: same company, same year.
        rows = [
            {"label": "Revenue", "cells": [25785, 38549], "kind": "subtotal"},
            {"label": "Cost of revenue", "cells": [-13234, -19468], "kind": "detail"},
            {"label": "Gross profit", "cells": [12551, 19081], "kind": "subtotal"},
            {"label": "Operating expenses", "cells": ["", ""], "kind": "section"},
            {"label": "Research and development", "cells": [-6845, -9019],
             "kind": "detail",
             "note": "47% of gross profit, down from 55% the year before"},
            {"label": "Selling, general and administrative",
             "cells": [-2712, -3210], "kind": "detail"},
            {"label": "Other operating", "cells": [-902, -1104], "kind": "detail"},
            {"label": "Operating income", "cells": [2092, 5748], "kind": "subtotal"},
            {"label": "Tax", "cells": [-321, -612], "kind": "detail"},
            {"label": "Net income", "cells": [1771, 5136], "kind": "total"},
        ]

        # The short form: no section headings, no notes -- the same component
        # when there is nothing to group.
        summary = [
            {"label": "Revenue", "cells": [25785, 38549], "kind": "subtotal"},
            {"label": "Gross profit", "cells": [12551, 19081], "kind": "detail"},
            {"label": "Operating income", "cells": [2092, 5748], "kind": "detail"},
            {"label": "Net income", "cells": [1771, 5136], "kind": "total"},
        ]

        return {"periods": periods, "rows": rows, "summary": summary}

    def _validate_context(self, d):
        """`kind` drives the styling, and the cells must be RAW numbers.

        A pre-formatted string renders, right-aligns, and quietly loses the
        negative colouring the macro would have applied."""
        for key in ("rows", "summary"):
            rows = d[key]
            assert_rows("income-statement", key, rows, ("label", "cells", "kind"))
            for i, r in enumerate(rows):
                assert_enum("income-statement", f"{key}[{i}].kind", r["kind"],
                            {"section", "detail", "subtotal", "total"})
                cells = r["cells"]
                assert len(cells) == len(d["periods"]), \
                    (f"income-statement: {key}[{i}] {r['label']!r} has "
                     f"{len(cells)} cells against {len(d['periods'])} periods")
                if r["kind"] == "section":
                    continue        # a heading carries empty cells by design
                assert_numbers("income-statement", f"{key}[{i}].cells", cells)

if __name__ == "__main__":
    print(IncomeStatementShowcaseController().build())
