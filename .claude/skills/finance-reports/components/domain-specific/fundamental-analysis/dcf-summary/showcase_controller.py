"""Showcase controller for the `dcf-summary` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:num[], kind?:str, note?:str}   assumptions[] {label:str, value:str}

THE ASSUMPTIONS ARE THE ARGUMENT. A DCF's output is a single number
that looks authoritative and moves violently with inputs nobody sees, so the
component takes them as a separate list and shows them beside the result.
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


class DcfSummaryShowcaseController(ShowcaseController):

    def _build_context(self):
        years = ["FY26E", "FY27E", "FY28E", "FY29E", "FY30E"]

        rows = [
            {"label": "Free cash flow", "cells": [5210, 6340, 7480, 8590, 9620],
             "kind": "detail"},
            {"label": "Discount factor", "cells": [0.92, 0.85, 0.78, 0.72, 0.66],
             "kind": "detail"},
            {"label": "Present value", "cells": [4793, 5389, 5834, 6185, 6349],
             "kind": "subtotal",
             "note": "sums to 28,550 before the terminal value"},
        ]

        # Deliberately explicit about the two inputs that dominate the answer.
        assumptions = [
            {"label": "WACC", "value": "9.0%"},
            {"label": "Terminal growth", "value": "2.5%"},
            {"label": "Terminal value", "value": "$151,200m"},
            {"label": "Net debt", "value": "-$8,476m"},
            {"label": "Shares outstanding", "value": "1,624m"},
            {"label": "Implied value per share", "value": "$115.20"},
        ]
        return {"years": years, "rows": rows, "assumptions": assumptions}

    def _validate_context(self, d):
        """Present value must equal free cash flow times the discount factor.

        The one arithmetic relation a DCF table can get wrong silently, and the
        one a reader is least able to check by eye."""
        rows = d["rows"]
        assert_rows("dcf-summary", "rows", rows, ("label", "cells"))
        for i, r in enumerate(rows):
            assert_numbers("dcf-summary", f"rows[{i}].cells", r["cells"])
            assert len(r["cells"]) == len(d["years"]), \
                f"dcf-summary: rows[{i}] {r['label']!r} has the wrong cell count"
        assert_rows("dcf-summary", "assumptions", d["assumptions"],
                    ("label", "value"))

        by = {r["label"]: r["cells"] for r in rows}
        for i, year in enumerate(d["years"]):
            expected = round(by["Free cash flow"][i] * by["Discount factor"][i])
            actual = by["Present value"][i]
            assert abs(expected - actual) <= 1, \
                (f"dcf-summary: {year} present value is {actual} but "
                 f"{by['Free cash flow'][i]} x {by['Discount factor'][i]} = "
                 f"{expected}; the discounting does not tie")

if __name__ == "__main__":
    print(DcfSummaryShowcaseController().build())
