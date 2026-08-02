"""Showcase controller for the `balance-sheet` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:num[], kind:section|detail|subtotal|total|pct, note?:str}   periods: str[]

THE FIGURES BALANCE, and `check` states the identity in words so a
reader can verify it without adding the column up. These are the same numbers
the AMD report carries, which is where the shape comes from.
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


class BalanceSheetShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["Q1 FY25", "Q1 FY26"]

        rows = [
            {"label": "Assets", "cells": ["", ""], "kind": "section"},
            {"label": "Cash and investments", "cells": [7310, 12347], "kind": "detail"},
            {"label": "Receivables", "cells": [6286, 6035], "kind": "detail"},
            {"label": "Property, plant and equipment",
             "cells": [1921, 2723], "kind": "detail"},
            {"label": "Goodwill and intangibles", "cells": [43202, 41498],
             "kind": "detail", "note": "amortising; down 1.7bn year on year"},
            {"label": "Other assets", "cells": [12831, 17039], "kind": "detail"},
            {"label": "Total assets", "cells": [71550, 79642], "kind": "subtotal"},
            {"label": "Liabilities", "cells": ["", ""], "kind": "section"},
            {"label": "Payables", "cells": [2206, 2997], "kind": "detail"},
            {"label": "Debt, including leases", "cells": [4731, 3871], "kind": "detail"},
            {"label": "Other liabilities", "cells": [6732, 8312], "kind": "detail"},
            {"label": "Total liabilities", "cells": [13669, 15180], "kind": "subtotal"},
            {"label": "Equity", "cells": [57881, 64462], "kind": "total"},
        ]
        return {"periods": periods, "rows": rows}

    def _validate_context(self, d):
        """ASSETS = LIABILITIES + EQUITY, in both periods.

        The identity `check` claims in words. A balance sheet that does not
        balance renders as a perfectly tidy table, and nothing else says so."""
        assert_rows("balance-sheet", "rows", d["rows"], ("label", "cells", "kind"))
        by = {}
        for i, r in enumerate(d["rows"]):
            assert_enum("balance-sheet", f"rows[{i}].kind", r["kind"],
                        {"section", "detail", "subtotal", "total", "pct"})
            assert len(r["cells"]) == len(d["periods"]), \
                f"balance-sheet: rows[{i}] {r['label']!r} has the wrong cell count"
            if r["kind"] != "section":
                assert_numbers("balance-sheet", f"rows[{i}].cells", r["cells"])
                by[r["label"]] = r["cells"]

        for p, period in enumerate(d["periods"]):
            assets = by["Total assets"][p]
            liab = by["Total liabilities"][p]
            equity = by["Equity"][p]
            assert assets == liab + equity, \
                (f"balance-sheet: {period} does not balance -- assets {assets} "
                 f"against liabilities {liab} + equity {equity} = "
                 f"{liab + equity}. The table would render and be wrong by "
                 f"{abs(assets - liab - equity)}")

if __name__ == "__main__":
    print(BalanceSheetShowcaseController().build())
