"""Showcase controller for the `peer-comparison` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    headers[] str -- METRIC columns ONLY   formats[] str   rows[] {name:str, cells:num[], subject:bool}

HEADERS ARE THE METRIC COLUMNS ONLY. The macro emits the Company
column itself, and passing it again shifts every value one column left and
leaves the last blank -- a perfectly tidy wrong table. `formats` is per column,
because peers are compared on mixed units and one format for all would be a
lie. Both are asserted here.
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


class PeerComparisonShowcaseController(ShowcaseController):

    def _build_context(self):
        # METRIC columns only -- Company is emitted by the macro.
        headers = ["ROIC", "Capex / revenue", "R&D / revenue",
                   "SBC / revenue", "EV / EBITDA"]
        formats = ["pct", "pct", "pct", "pct", "num"]

        rows = [
            {"name": "Advanced Micro Devices", "subject": True,
             "cells": [5.4, 2.8, 23.4, 4.7, 47.85]},
            {"name": "NVDA", "subject": False,
             "cells": [62.9, 2.8, 8.6, 3.0, 31.43]},
            {"name": "INTC", "subject": False,
             "cells": [-0.1, 27.7, 26.1, 4.6, 14.50]},
            {"name": "QCOM", "subject": False,
             "cells": [28.4, 3.9, 19.8, 5.2, 13.10]},
        ]

        # One metric, two peers: the smallest table the component still suits,
        # where a reader is comparing a single number across a short list.
        narrow_headers = ["EV / EBITDA"]
        narrow_formats = ["num"]
        narrow_rows = [
            {"name": "Advanced Micro Devices", "cells": [47.85], "subject": True},
            {"name": "NVDA", "cells": [31.43], "subject": False},
            {"name": "INTC", "cells": [14.50], "subject": False},
        ]

        return {"headers": headers, "formats": formats, "rows": rows,
                "narrow_headers": narrow_headers, "narrow_formats": narrow_formats,
                "narrow_rows": narrow_rows}

    def _validate_context(self, d):
        """THE COLUMN COUNT, three ways -- the failure this component names.

        headers, formats and every row's cells must agree. One extra header
        shifts every value left and leaves the last column blank, and the table
        renders beautifully."""
        for hk, fk, rk in (("headers", "formats", "rows"),
                           ("narrow_headers", "narrow_formats", "narrow_rows")):
            headers, formats, rows = d[hk], d[fk], d[rk]
            assert headers, f"peer-comparison: {hk} is empty"
            assert len(formats) == len(headers), \
                (f"peer-comparison: {len(formats)} formats against "
                 f"{len(headers)} {hk}; peers are compared on mixed units and "
                 f"one format for all of them would be a lie")
            assert_rows("peer-comparison", rk, rows, ("name", "cells", "subject"))
            for i, r in enumerate(rows):
                assert_numbers("peer-comparison", f"{rk}[{i}].cells", r["cells"])
                assert len(r["cells"]) == len(headers), \
                    (f"peer-comparison: {rk}[{i}] {r['name']!r} has "
                     f"{len(r['cells'])} cells against {len(headers)} metric "
                     f"columns; the row would shift and the last cell blank")
                assert "Company" not in headers, \
                    ("peer-comparison: 'Company' is in headers; the macro emits "
                     "that column itself and passing it shifts every value")
            subjects = [r for r in rows if r["subject"]]
            assert len(subjects) == 1, \
                (f"peer-comparison: {len(subjects)} rows marked subject in {rk}; "
                 f"exactly one row is the company being written about")

if __name__ == "__main__":
    print(PeerComparisonShowcaseController().build())
