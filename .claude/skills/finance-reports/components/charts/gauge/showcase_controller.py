"""Showcase controller for the `gauge` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    value:num, minimum:num, maximum:num -- scalars, no collection

SCALARS, not a collection -- the only chart in the set without a
series. The unit is required because the value is read alone, against nothing.
SYMBOLS, not words: the macro builds its centre label as `"{value}" ~ unit`
with no separator, so unit="percent" renders as "78.4percent". The same string
is also passed to r.out() as the caption subtext, so a long unit appears twice.
Both are component behaviour, not choices made here.
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


class ChartGaugeShowcaseController(ShowcaseController):

    def _build_context(self):
        # Three different ranges, because the component's whole job is to
        # place ONE value inside a stated span -- and a span that is not 0..100
        # is where a misread minimum would show.
        return {
            "utilisation": {"value": 78.4, "minimum": 0, "maximum": 100},
            "coverage": {"value": 4.2, "minimum": 0, "maximum": 10},
            "payout": {"value": 31.5, "minimum": 0, "maximum": 60},
        }

    def _validate_context(self, d):
        """The value must sit INSIDE its range.

        A value past the maximum draws the needle pinned at the end, which
        reads as "at the limit" rather than "off the scale"."""
        for key in ("utilisation", "coverage", "payout"):
            g = d[key]
            assert_numbers("gauge", key, [g["value"], g["minimum"], g["maximum"]])
            assert g["minimum"] < g["maximum"], \
                (f"gauge: {key} has minimum {g['minimum']} not below maximum "
                 f"{g['maximum']}; the dial has no span to place a value in")
            assert g["minimum"] <= g["value"] <= g["maximum"], \
                (f"gauge: {key} value {g['value']} is outside "
                 f"{g['minimum']}..{g['maximum']}; the needle pins at the end "
                 f"and reads as 'at the limit' rather than 'off the scale'")

if __name__ == "__main__":
    print(ChartGaugeShowcaseController().build())
