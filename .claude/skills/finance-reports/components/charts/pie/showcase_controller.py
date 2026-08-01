"""Showcase controller for the `pie` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    slices[] {name:str, value:num}

A HANDFUL OF PARTS OF ONE WHOLE. Every set here is small enough to
read: past about six slices the small ones become unlabelled slivers and a
stacked-normalized bar or a table is the honest form.
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


class ChartPieShowcaseController(ShowcaseController):

    def _build_context(self):
        # Four slices. A pie stops working long before a bar chart does, so
        # nothing here has more than five.
        revenue_mix = [
            {"name": "Data Center", "value": 16635},
            {"name": "Client", "value": 14550},
            {"name": "Gaming", "value": 3910},
            {"name": "Embedded", "value": 3454},
        ]

        # Two slices: the one case where a pie beats every other form, because
        # the reader is comparing against a half.
        ownership = [
            {"name": "Institutional", "value": 68.4},
            {"name": "Retail and insider", "value": 31.6},
        ]

        return {"revenue_mix": revenue_mix, "ownership": ownership}

    def _validate_context(self, d):
        """Slices must be positive, and few enough to read.

        A zero or negative slice draws nothing at all and leaves its legend
        entry pointing at empty space."""
        for key in ("revenue_mix", "ownership"):
            slices = d[key]
            assert_labels("pie", f"{key} names", [s["name"] for s in slices])
            values = [s["value"] for s in slices]
            assert_numbers("pie", f"{key} values", values)
            for s in slices:
                assert s["value"] > 0, \
                    (f"pie: {key} slice {s['name']!r} is {s['value']}; a "
                     f"non-positive slice draws nothing and leaves its legend "
                     f"entry pointing at empty space")
            assert len(slices) <= 6, \
                (f"pie: {key} has {len(slices)} slices; past six the small ones "
                 f"are unlabelled slivers and stacked-normalized is the form")

if __name__ == "__main__":
    print(ChartPieShowcaseController().build())
