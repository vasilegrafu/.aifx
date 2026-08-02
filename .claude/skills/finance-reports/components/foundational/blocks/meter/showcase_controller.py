"""Showcase controller for the `meter` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    label: str   value: num   max: num   display: str -- overrides the printed value

THE FILL IS value/max, AND `display` IS FREE TEXT OVER THE TOP. That
is the trap: `display` can say anything at all while the bar says value/max,
so a meter reading "82% of target" over a 48% fill is a page nobody can
challenge. Every `display` here is derived from the same two numbers that
draw the bar.

A value above max computes a fill past 100% and the bar leaves its track.
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


class MeterShowcaseController(ShowcaseController):

    def _build_context(self):
        # display is BUILT from value and max, never written by hand, so the
        # words and the bar cannot drift apart.
        def meter(label, value, maximum, unit="%"):
            return {"label": label, "value": value, "max": maximum,
                    "display": f"{value}{unit} of {maximum}{unit}"}

        meters = [
            meter("Gross margin against FY25 target", 49.5, 60.0),
            meter("R&D as a share of revenue", 23.4, 30.0),
            meter("Covenant headroom consumed", 68.0, 100.0),
        ]

        # The two ends. Both are legitimate states a report has to be able to
        # draw, and both are where an off-by-one in the fill shows up.
        edges = [
            meter("Buyback authorisation used", 0.0, 100.0),
            meter("Revolving facility drawn", 100.0, 100.0),
        ]
        return {"meters": meters, "edges": edges}

    def _validate_context(self, d):
        """value is within 0..max, and `display` still contains both numbers.

        The second half is the one worth having: `display` overrides the
        printed value entirely, so nothing but this check keeps the words
        honest about the bar underneath them."""
        assert_all_drawn("meter", d, [("meters", ()), ("edges", ())])
        for key in ("meters", "edges"):
            rows = d[key]
            assert_rows("meter", key, rows, ("label", "value", "max", "display"))
            assert_labels("meter", f"{key} labels", [m["label"] for m in rows])
            for m in rows:
                assert_numbers("meter", m["label"], [m["value"], m["max"]])
                assert m["max"] > 0, \
                    f"meter: {m['label']!r} has max {m['max']}; the fill is 0"
                assert 0 <= m["value"] <= m["max"], \
                    (f"meter: {m['label']!r} is {m['value']} against a max of "
                     f"{m['max']}; the fill computes past 100% and the bar "
                     f"leaves its track")
                assert str(m["value"]) in m["display"], \
                    (f"meter: {m['label']!r} draws {m['value']}/{m['max']} but "
                     f"prints {m['display']!r}; display overrides the value "
                     f"entirely, so the words can outrun the bar")

if __name__ == "__main__":
    print(MeterShowcaseController().build())
