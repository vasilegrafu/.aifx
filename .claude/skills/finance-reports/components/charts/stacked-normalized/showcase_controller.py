"""Showcase controller for the `stacked-normalized` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

RAW VALUES, never pre-computed shares -- the macro converts at
compose time, and passing percentages that already sum to 100 would hide the
one bug this component can have. The totals here differ by an order of
magnitude between the first and last category, which is exactly the
information the form throws away.
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


class ChartStackedNormalizedShowcaseController(ShowcaseController):

    def _build_context(self):
        years = ["FY21", "FY22", "FY23", "FY24", "FY25"]
        peers = ["AMD", "NVDA", "INTC", "QCOM"]

        # RAW amounts. FY21 totals 16.4bn and FY25 totals 38.5bn -- the chart
        # will draw both columns the same height, which is the trade usage.md
        # names.
        cloud = {"name": "Cloud", "points": [4.1, 6.2, 9.8, 14.6, 21.4]}
        license_ = {"name": "License", "points": [8.9, 9.1, 9.4, 9.9, 10.2]}
        hardware = {"name": "Hardware", "points": [3.4, 3.1, 2.8, 2.6, 2.4]}
        services = {"name": "Services", "points": [2.1, 2.4, 2.9, 3.8, 4.5]}

        p_product = {"name": "Product", "points": [22.7, 47.5, 45.1, 30.1]}
        p_services = {"name": "Services", "points": [3.4, 13.6, 8.9, 8.7]}

        return {
            "years": years,
            "peers": peers,
            "cloud": cloud,
            "license": license_,
            "hardware": hardware,
            "services": services,
            "p_product": p_product,
            "p_services": p_services,
        }

    def _validate_context(self, d):
        """The shared contract, per <section> of showcase.html.j2.

        An entry here is a section there; the shared checks live in
        components/_contracts.py."""
        assert_series_categories("stacked-normalized", d, (
            ("peers", ("p_product", "p_services")),
            ("years", ("cloud", "license", "hardware", "services")),
        ))

        # The point of the component is that unequal totals draw equal. If the
        # totals were all alike the sections would still render, and would
        # demonstrate nothing about what this form costs.
        totals = [sum(d[k]["points"][i] for k in
                      ("cloud", "license", "hardware", "services"))
                  for i in range(len(d["years"]))]
        assert max(totals) > 2 * min(totals), \
            (f"stacked-normalized: column totals {totals} are too alike; this "
             f"showcase exists to show equal-height columns hiding unequal "
             f"totals, and needs totals that actually differ")


if __name__ == "__main__":
    print(ChartStackedNormalizedShowcaseController().build())
