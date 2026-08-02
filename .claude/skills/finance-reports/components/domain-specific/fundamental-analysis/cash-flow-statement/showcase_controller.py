"""Showcase controller for the `cash-flow-statement` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:num[], kind:section|detail|subtotal|total, note?:str}

THE SIGNS ARE THE MEANING. Cash in is positive, cash out negative,
and the macro colours by sign -- so capex must arrive as -1420, never as 1420
with a label that says it was spent.
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


class CashFlowStatementShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["FY24", "FY25"]

        rows = [
            {"label": "Operating", "cells": ["", ""], "kind": "section"},
            {"label": "Net income", "cells": [1771, 5136], "kind": "detail"},
            {"label": "Depreciation and amortisation",
             "cells": [3980, 4120], "kind": "detail"},
            {"label": "Working capital", "cells": [-612, -418], "kind": "detail"},
            {"label": "Operating cash flow", "cells": [5139, 6400],
             "kind": "subtotal"},
            {"label": "Investing", "cells": ["", ""], "kind": "section"},
            {"label": "Capital expenditure", "cells": [-1180, -1420],
             "kind": "detail", "note": "3.7% of revenue, fabless"},
            {"label": "Acquisitions, net", "cells": [-340, -905], "kind": "detail"},
            {"label": "Financing", "cells": ["", ""], "kind": "section"},
            {"label": "Buybacks", "cells": [-1985, -2640], "kind": "detail"},
            {"label": "Debt repaid", "cells": [-450, -860], "kind": "detail"},
            {"label": "Net change in cash", "cells": [1184, 575], "kind": "total"},
        ]
        return {"periods": periods, "rows": rows}

    def _validate_context(self, d):
        """The stated total must equal the sum of what is above it.

        A cash flow statement that does not add up is the same failure as a
        sankey that does not conserve: it draws, and nothing says so."""
        rows = d["rows"]
        assert_rows("cash-flow-statement", "rows", rows, ("label", "cells", "kind"))
        for i, r in enumerate(rows):
            assert_enum("cash-flow-statement", f"rows[{i}].kind", r["kind"],
                        {"section", "detail", "subtotal", "total"})
            if r["kind"] != "section":
                assert_numbers("cash-flow-statement", f"rows[{i}].cells", r["cells"])

        by = {r["label"]: r["cells"] for r in rows if r["kind"] != "section"}
        for p, period in enumerate(d["periods"]):
            parts = (by["Operating cash flow"][p] + by["Capital expenditure"][p]
                     + by["Acquisitions, net"][p] + by["Buybacks"][p]
                     + by["Debt repaid"][p])
            assert parts == by["Net change in cash"][p], \
                (f"cash-flow-statement: {period} lines sum to {parts} but the "
                 f"total says {by['Net change in cash'][p]}; the table would "
                 f"render and misstate the difference")

if __name__ == "__main__":
    print(CashFlowStatementShowcaseController().build())
