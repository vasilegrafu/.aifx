"""Showcase controller for the `aging-schedule` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {counterparty:str, cells:str[], total:str, overdue_share:num, tone?:str}   total_row? {label, cells}

`overdue_share` IS A PERCENT NUMBER and drives a bar; the cells are
pre-formatted strings. Two different conventions in one row, which is exactly
where a caller gets it wrong.
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


class AgingScheduleShowcaseController(ShowcaseController):

    def _build_context(self):
        buckets = ["Current", "1 – 30", "31 – 60", "61 – 90", "90+"]

        rows = [
            {"counterparty": "Distributor A", "cells": ["1,240", "310", "88", "24", "6"],
             "total": "1,668", "overdue_share": 25.7},
            {"counterparty": "Distributor B", "cells": ["880", "142", "36", "0", "0"],
             "total": "1,058", "overdue_share": 16.8},
            {"counterparty": "OEM C", "cells": ["610", "204", "155", "92", "71"],
             "total": "1,132", "overdue_share": 46.1, "tone": "bad"},
            {"counterparty": "OEM D", "cells": ["1,905", "58", "0", "0", "0"],
             "total": "1,963", "overdue_share": 3.0, "tone": "good"},
        ]
        total_row = {"label": "Total",
                     "cells": ["4,635", "714", "279", "116", "77"]}
        return {"buckets": buckets, "rows": rows, "total_row": total_row}

    def _validate_context(self, d):
        """Cells are strings; overdue_share is a PERCENT NUMBER, 0..100."""
        rows = d["rows"]
        assert_rows("aging-schedule", "rows", rows,
                    ("counterparty", "cells", "total", "overdue_share"))
        for i, r in enumerate(rows):
            assert len(r["cells"]) == len(d["buckets"]), \
                f"aging-schedule: rows[{i}] has the wrong cell count"
            for c in r["cells"]:
                assert isinstance(c, str), \
                    (f"aging-schedule: rows[{i}] cells are PRE-FORMATTED "
                     f"strings, but overdue_share is a NUMBER -- two "
                     f"conventions in one row, and {c!r} has the wrong one")
            assert_numbers("aging-schedule", f"rows[{i}].overdue_share",
                           [r["overdue_share"]])
            assert 0 <= r["overdue_share"] <= 100, \
                (f"aging-schedule: rows[{i}] overdue_share is "
                 f"{r['overdue_share']}; a PERCENT NUMBER between 0 and 100, "
                 f"because it drives a bar width")
            if "tone" in r:
                assert_enum("aging-schedule", f"rows[{i}].tone", r["tone"],
                            {"good", "neutral", "bad"})
        # A per-row share does not sum to anything, so a single mis-scaled row
        # is indistinguishable from a genuinely tiny one -- 0.257 is a legal
        # value here. What IS catchable is the whole column arriving as
        # fractions, which is how this actually goes wrong.
        shares = [r["overdue_share"] for r in d["rows"]]
        assert max(shares) >= 1.0,             (f"aging-schedule: every overdue_share is below 1 ({shares}); these are PERCENT "
             f"NUMBERS (25.7), and a column of fractions renders as a row of "
             f"bars too small to see rather than as an error")


        # AGREEMENT, which is the only check worth writing here: overdue_share
        # must be what the buckets say it is. Typed independently of the cells
        # it summarises, it is free to drift, and a drifted bar is still a bar.
        for i, r in enumerate(d["rows"]):
            cells = [float(c.replace(",", "")) for c in r["cells"]]
            total = float(r["total"].replace(",", ""))
            assert abs(sum(cells) - total) < 0.5, \
                (f"aging-schedule: rows[{i}] buckets sum to {sum(cells):,.0f} "
                 f"but total says {total:,.0f}")
            overdue = 100 * sum(cells[1:]) / total
            assert abs(overdue - r["overdue_share"]) < 0.15, \
                (f"aging-schedule: rows[{i}] {r['counterparty']!r} is "
                 f"{overdue:.1f}% overdue by its own buckets, but "
                 f"overdue_share says {r['overdue_share']}%; the bar would "
                 f"disagree with the numbers beside it")

        # And the total row must be the columns added up.
        for j, label in enumerate(d["buckets"]):
            column = sum(float(r["cells"][j].replace(",", "")) for r in d["rows"])
            stated = float(d["total_row"]["cells"][j].replace(",", ""))
            assert abs(column - stated) < 0.5, \
                (f"aging-schedule: {label!r} column sums to {column:,.0f} but "
                 f"the total row says {stated:,.0f}")


if __name__ == "__main__":
    print(AgingScheduleShowcaseController().build())
