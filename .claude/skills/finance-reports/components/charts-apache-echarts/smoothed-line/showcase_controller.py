"""Showcase controller for the `smoothed-line` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

The curve is the argument: it says READ THE TREND, not the ticks. So
every series here is noisy enough that the smoothing earns its place -- a
four-point series drawn smooth is just a line telling a small lie about the
values between its points.
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import assert_series_categories        # noqa: E402
from components._showcase_controller import ShowcaseController    # noqa: E402


class ChartSmoothedLineShowcaseController(ShowcaseController):

    def _build_context(self):
        months = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]

        # Noisy on purpose. Smoothing a series that is already smooth invents
        # nothing, but it also demonstrates nothing.
        _base = [42, 39, 45, 51, 48, 55, 61, 58, 64, 60, 67, 72,
                 69, 75, 71, 79, 84, 80, 88, 92, 87, 95, 99, 104]
        shipments = {"name": "Units shipped", "points": [float(v) for v in _base]}

        north = {"name": "North America", "points": [float(v) for v in _base]}
        emea = {"name": "EMEA",
                "points": [round(v * 0.62 + 4, 1) for v in _base]}

        utilisation = {"name": "Utilisation",
                       "points": [round(58 + (v % 17) * 1.4, 1) for v in _base]}

        return {
            "months": months,
            "shipments": shipments,
            "north": north,
            "emea": emea,
            "utilisation": utilisation,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("smoothed-line", d, (
            ("months", ("shipments",)),
            ("months", ("north", "emea")),
            ("months", ("utilisation",)),
        ))


if __name__ == "__main__":
    print(ChartSmoothedLineShowcaseController().build())
