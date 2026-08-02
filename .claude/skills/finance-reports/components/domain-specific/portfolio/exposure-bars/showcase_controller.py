"""Showcase controller for the `exposure-bars` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {label:str, percent:num, value?:str} -- value is free text (amount, target, delta)

`value` IS FREE TEXT BESIDE A NUMBER THAT IS NOT. The bar and the
printed percentage both come from `percent`; `value` is whatever you put
there, sitting immediately beside them in the same cell. It is for the amount
or the target or the delta -- and it is also where a stale figure hides most
comfortably, because it looks like part of the same measurement.
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


class ExposureBarsShowcaseController(ShowcaseController):

    def _build_context(self):
        aum = 2450.0
        sectors = [("Technology", 30.3), ("Financials", 13.7),
                   ("Industrials", 15.2), ("Healthcare", 9.8),
                   ("Energy", 8.3), ("Consumer", 7.1),
                   ("Materials", 6.2), ("Cash", 9.4)]
        # `value` is derived, not typed: the amount has to follow the percent
        # it is printed against.
        items = [{"label": label, "percent": pct,
                  "value": f"${aum * pct / 100:,.0f}m"}
                 for label, pct in sectors]
        return {"items": items, "aum": aum}

    def _validate_context(self, d):
        """Percentages sum to 100, none leaves its track, and every `value`
        is the amount its own percentage implies."""
        assert_all_drawn("exposure-bars", d, [("items", ("aum",))])
        assert_rows("exposure-bars", "items", d["items"],
                    ("label", "percent"), 2)
        assert_labels("exposure-bars", "labels",
                      [i["label"] for i in d["items"]])
        percents = [i["percent"] for i in d["items"]]
        assert_numbers("exposure-bars", "percent", percents)
        assert abs(sum(percents) - 100) < 0.05, \
            (f"exposure-bars: exposures sum to {sum(percents):.1f}%, not "
             f"100%; a breakdown that does not add up is not one")
        for i in d["items"]:
            assert 0 <= i["percent"] <= 100, \
                (f"exposure-bars: {i['label']!r} is {i['percent']}%; outside "
                 f"0..100 the fill leaves its track")
            amount = float(i["value"].lstrip("$").rstrip("m").replace(",", ""))
            expected = d["aum"] * i["percent"] / 100
            assert abs(amount - expected) < 1.0, \
                (f"exposure-bars: {i['label']!r} is {i['percent']}% of "
                 f"{d['aum']:,.0f} = {expected:,.0f}, but prints {i['value']}")

if __name__ == "__main__":
    print(ExposureBarsShowcaseController().build())
