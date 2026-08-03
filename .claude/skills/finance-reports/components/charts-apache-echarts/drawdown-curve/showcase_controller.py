"""Showcase controller for the `drawdown-curve` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {date:str, value:num} -- running peak and drawdown derived in the macro

THE MACRO DERIVES THE DRAWDOWN. What it is handed is a LEVEL series
-- a price or an index -- and it computes the running peak and the decline from
it. Passing an already-negative drawdown series would be drawing the derivation
twice, which is the one way to get this component wrong.
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import assert_labels, assert_numbers    # noqa: E402
from components._showcase_controller import ShowcaseController     # noqa: E402


class ChartDrawdownCurveShowcaseController(ShowcaseController):

    def _build_context(self):
        # A LEVEL series, not a drawdown: the macro computes the running peak
        # and the decline from it. Two real-shaped episodes -- a long grind
        # down and a sharp one -- so the curve has more than one trough.
        months = [f"{y}-{m:02d}" for y in (2023, 2024, 2025) for m in range(1, 13)]
        levels = [100, 104, 108, 112, 109, 103, 96, 91, 88, 94, 99, 106,
                  111, 115, 118, 121, 117, 108, 99, 93, 89, 86, 92, 97,
                  103, 109, 114, 119, 124, 128, 125, 119, 122, 127, 133, 138]
        index = [{"date": m, "value": float(v)} for m, v in zip(months, levels)]

        # A shorter, single-episode series where the trough is unambiguous.
        quarters = [f"{y}-Q{q}" for y in (2024, 2025) for q in (1, 2, 3, 4)]
        fund = [{"date": q, "value": float(v)} for q, v in
                zip(quarters, [100, 106, 98, 89, 93, 101, 108, 114])]

        return {"index": index, "fund": fund}

    def _validate_context(self, d):
        """A LEVEL series, positive and in date order.

        The one way to get this component wrong is to hand it a drawdown
        series that is already negative -- the macro would then derive the
        drawdown OF the drawdown and draw a curve nobody can interpret."""
        for key in ("index", "fund"):
            series = d[key]
            assert series, f"drawdown-curve: {key} is empty"
            assert_labels("drawdown-curve", f"{key} dates", [p["date"] for p in series])
            values = [p["value"] for p in series]
            assert_numbers("drawdown-curve", f"{key} values", values)
            for i, v in enumerate(values):
                assert v > 0, \
                    (f"drawdown-curve: {key}[{i}] is {v}; this component takes "
                     f"a LEVEL series and derives the drawdown itself, so a "
                     f"non-positive value means the derivation was done twice")
            dates = [p["date"] for p in series]
            assert dates == sorted(dates), \
                (f"drawdown-curve: {key} dates are not in order; the running "
                 f"peak is computed left to right and would be wrong")

if __name__ == "__main__":
    print(ChartDrawdownCurveShowcaseController().build())
