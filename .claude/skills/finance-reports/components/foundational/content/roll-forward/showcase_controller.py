"""Showcase controller for the `roll-forward` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:num[], kind:opening|movement|closing}   periods: str[]

OPENING PLUS MOVEMENTS MUST EQUAL CLOSING IN EVERY COLUMN. The
component header says nothing here checks it -- the report's own shape() does,
because only the report has the arithmetic. This showcase IS a report for that
purpose, so the check lives below and runs on every build.

The second thing worth checking is continuity: FY24's closing balance is FY25's
opening balance, and a roll-forward where those differ is describing two
different companies.
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


class RollForwardShowcaseController(ShowcaseController):

    def _build_context(self):
        # Net debt. Free cash flow REDUCES it, so it carries a minus.
        periods = ["FY24", "FY25"]
        opening = [8420, 7905]
        movements = [
            ("Free cash flow", [-2140, -2530]),
            ("Acquisitions", [1180, 1640]),
            ("Buybacks and dividends", [900, 1050]),
            ("FX translation", [-455, 120]),
        ]
        closing = [o + sum(m[1][i] for m in movements)
                   for i, o in enumerate(opening)]

        rows = [{"label": "Opening net debt", "cells": opening,
                 "kind": "opening"}]
        rows += [{"label": label, "cells": cells, "kind": "movement"}
                 for label, cells in movements]
        rows += [{"label": "Closing net debt", "cells": closing,
                  "kind": "closing"}]
        return {"periods": periods, "rows": rows}

    def _validate_context(self, d):
        """Every column closes, and each closing balance opens the next.

        This is the check the component header delegates to the report."""
        assert_labels("roll-forward", "periods", d["periods"])
        assert_all_drawn("roll-forward", d, [("periods", ("rows",))])
        assert_rows("roll-forward", "rows", d["rows"],
                    ("label", "cells", "kind"), 3)
        assert_labels("roll-forward", "row labels",
                      [r["label"] for r in d["rows"]])
        for r in d["rows"]:
            assert_numbers("roll-forward", r["label"], r["cells"])
            assert_enum("roll-forward", f"{r['label']!r}.kind", r["kind"],
                        {"opening", "movement", "closing"})
            assert len(r["cells"]) == len(d["periods"]), \
                (f"roll-forward: {r['label']!r} has {len(r['cells'])} values "
                 f"against {len(d['periods'])} periods")

        rows = d["rows"]
        assert rows[0]["kind"] == "opening" and rows[-1]["kind"] == "closing", \
            "roll-forward: the schedule must open on an opening balance and " \
            "close on a closing one"
        for i, period in enumerate(d["periods"]):
            opening = rows[0]["cells"][i]
            closing = rows[-1]["cells"][i]
            moved = sum(r["cells"][i] for r in rows[1:-1])
            assert abs(opening + moved - closing) < 0.01, \
                (f"roll-forward: {period} opens at {opening} and moves "
                 f"{moved:+}, which is {opening + moved}, but closes at "
                 f"{closing}; the column does not roll forward")

        # Continuity: last year's close is this year's open.
        for i in range(len(d["periods"]) - 1):
            assert rows[-1]["cells"][i] == rows[0]["cells"][i + 1], \
                (f"roll-forward: {d['periods'][i]} closes at "
                 f"{rows[-1]['cells'][i]} but {d['periods'][i + 1]} opens at "
                 f"{rows[0]['cells'][i + 1]}; these are two different "
                 f"companies side by side")

if __name__ == "__main__":
    print(RollForwardShowcaseController().build())
