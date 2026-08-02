"""Showcase controller for the `valuation-range` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {method:str, low:num, high:num, label:str} -- offsets computed here; price marks the current level

EVERY METHOD IS A RANGE, and the point of the component is that the
ranges disagree. `price` marks where the stock actually trades, which is the
only number on the figure that is not somebody's estimate.
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


class ValuationRangeShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"method": "DCF, 9% WACC", "low": 98.0, "high": 132.0,
             "label": "$98 – $132"},
            {"method": "EV / EBITDA, peer median", "low": 74.0, "high": 105.0,
             "label": "$74 – $105"},
            {"method": "P/E, 5-year average", "low": 88.0, "high": 121.0,
             "label": "$88 – $121"},
            {"method": "Sum of the parts", "low": 110.0, "high": 156.0,
             "label": "$110 – $156"},
        ]

        # Two methods that barely overlap -- the case where the spread IS the
        # finding and a single "fair value" would be a fabrication.
        disputed = [
            {"method": "DCF, 9% WACC", "low": 98.0, "high": 132.0,
             "label": "$98 – $132"},
            {"method": "Liquidation value", "low": 41.0, "high": 58.0,
             "label": "$41 – $58"},
        ]
        # THE SCALE IS NOT OPTIONAL. It defaults to 0..100 in the macro, and
        # these ranges reach $156 -- anything past the maximum computes an
        # offset above 100% and the bar leaves its track entirely.
        return {"rows": rows, "disputed": disputed, "price": 118.4,
                "scale_min": 0, "scale_max": 160}

    def _validate_context(self, d):
        """low < high on every row, and the price is inside the overall span.

        An inverted range draws a bar of negative width, which the engine
        renders as nothing at all."""
        for key in ("rows", "disputed"):
            rows = d[key]
            assert_rows("valuation-range", key, rows,
                        ("method", "low", "high", "label"))
            for i, r in enumerate(rows):
                assert_numbers("valuation-range", f"{key}[{i}]", [r["low"], r["high"]])
                assert r["low"] < r["high"], \
                    (f"valuation-range: {key}[{i}] {r['method']!r} runs "
                     f"{r['low']}..{r['high']}; an inverted range draws a bar "
                     f"of negative width, which is to say nothing at all")
        assert_numbers("valuation-range", "price", [d["price"]])
        lo = min(r["low"] for r in d["rows"])
        hi = max(r["high"] for r in d["rows"])
        assert lo <= d["price"] <= hi, \
            (f"valuation-range: price {d['price']} is outside every range "
             f"({lo}..{hi}); the marker would sit off the end of the figure")

if __name__ == "__main__":
    print(ValuationRangeShowcaseController().build())
