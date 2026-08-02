"""Showcase controller for the `metric-trend` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {label:str, cells:num[], cagr:num|str, dir:up|down|flat}   periods: str[]

`dir` DRAWS THE ARROW AND NOTHING TIES IT TO THE CELLS. A row that
falls every year with dir="up" renders a green triangle over the decline.

A CAGR OVER A MARGIN IS MEANINGLESS -- a rate that goes from 53.1% to 49.5%
has not compounded at anything. The margin row below carries a point change
instead, passed as a string with cagr_fmt="raw", which is what that field is
for.
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


class MetricTrendShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["FY21", "FY22", "FY23", "FY24", "FY25"]
        revenue = [24100, 27400, 30900, 34200, 38549]
        gross = [12800, 14300, 15900, 17600, 19081]
        net = [3200, 3700, 4250, 4836, 5136]
        margin = [round(100 * g / r, 1) for g, r in zip(gross, revenue)]

        rows = [
            {"label": "Revenue", "cells": revenue,
             "cagr": self._cagr(revenue), "dir": "up", "fmt": "money"},
            {"label": "Gross profit", "cells": gross,
             "cagr": self._cagr(gross), "dir": "up", "fmt": "money"},
            {"label": "Net income", "cells": net,
             "cagr": self._cagr(net), "dir": "up", "fmt": "money"},
            # A rate, not a quantity: the CAGR column carries a point change.
            {"label": "Gross margin", "cells": margin,
             "cagr": f"{margin[-1] - margin[0]:+.1f}pt", "dir": "down",
             "fmt": "pct", "cagr_fmt": "raw"},
        ]
        return {"periods": periods, "rows": rows}

    @staticmethod
    def _cagr(values):
        """Compound annual rate over the whole series, in per cent."""
        years = len(values) - 1
        return round(100 * ((values[-1] / values[0]) ** (1 / years) - 1), 1)

    def _validate_context(self, d):
        """Every row spans the periods, `dir` agrees with the series it
        labels, and a CAGR is only claimed where compounding means something."""
        assert_labels("metric-trend", "periods", d["periods"])
        assert_all_drawn("metric-trend", d, [("periods", ("rows",))])
        assert_rows("metric-trend", "rows", d["rows"],
                    ("label", "cells", "cagr", "dir"), 2)
        assert_labels("metric-trend", "row labels",
                      [r["label"] for r in d["rows"]])

        for r in d["rows"]:
            assert_numbers("metric-trend", r["label"], r["cells"])
            assert len(r["cells"]) == len(d["periods"]), \
                (f"metric-trend: {r['label']!r} has {len(r['cells'])} values "
                 f"against {len(d['periods'])} periods; the row renders short "
                 f"and every value after the gap sits under the wrong year")
            assert_enum("metric-trend", f"{r['label']!r}.dir", r["dir"],
                        {"up", "down", "flat"})

            first, last = r["cells"][0], r["cells"][-1]
            change = (last - first) / abs(first)
            expected = "flat" if abs(change) < 0.01 else (
                "up" if change > 0 else "down")
            assert r["dir"] == expected, \
                (f"metric-trend: {r['label']!r} runs {first} to {last} but is "
                 f"marked {r['dir']!r}; the arrow is what a reader takes as "
                 f"the finding")

            if isinstance(r["cagr"], (int, float)):
                assert r.get("cagr_fmt") != "raw", \
                    f"metric-trend: {r['label']!r} numeric cagr wants a format"
                # A compound rate only means something for a quantity.
                assert r["fmt"] != "pct", \
                    (f"metric-trend: {r['label']!r} is a rate and carries a "
                     f"numeric CAGR; a margin that moves 53.1 -> 49.5 has not "
                     f"compounded at anything. Use a point change.")

if __name__ == "__main__":
    print(MetricTrendShowcaseController().build())
