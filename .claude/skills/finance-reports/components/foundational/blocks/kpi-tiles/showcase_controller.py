"""Showcase controller for the `kpi-tiles` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    tiles[] {value:str, label:str, dir:up|down|flat, delta:str}

`dir` COLOURS THE DELTA AND NOTHING CHECKS IT AGAINST THE DELTA
ITSELF. A tile reading -2.0pt with dir="up" renders green, which is the single
most misleading thing this small component can do. The validator below ties
the two together.

UP IS NOT GOOD. `dir` is the DIRECTION OF TRAVEL, not a verdict: gross margin
falling 2.0pt is dir="down" even though the revenue tile beside it rose.
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


class KpiTilesShowcaseController(ShowcaseController):

    def _build_context(self):
        # All five agree with the bridge and the income statement used across
        # this library: revenue 38,549 from 34,200; gross profit 19,081
        # (49.5%, from 51.5%); net income 5,136 from 4,836 (13.3%, from 14.1%).
        tiles = [
            {"value": "$38.5bn", "label": "FY25 revenue",
             "dir": "up", "delta": "+12.7%"},
            {"value": "49.5%", "label": "Gross margin",
             "dir": "down", "delta": "-2.0pt"},
            {"value": "$5.1bn", "label": "Net income",
             "dir": "up", "delta": "+6.2%"},
            {"value": "13.3%", "label": "Net margin",
             "dir": "down", "delta": "-0.8pt"},
            {"value": "1.24x", "label": "Net debt / EBITDA",
             "dir": "flat", "delta": "unchanged"},
        ]
        return {"tiles": tiles}

    def _validate_context(self, d):
        """`dir` agrees with the sign of the delta it colours.

        Read the leading sign where there is one; "unchanged" and its like
        must be flat, because a tile with no sign and a direction is claiming
        movement it does not show."""
        assert_rows("kpi-tiles", "tiles", d["tiles"],
                    ("value", "label", "dir", "delta"), 2)
        assert_all_drawn("kpi-tiles", d, [("tiles", ())])
        assert_labels("kpi-tiles", "tile labels",
                      [t["label"] for t in d["tiles"]])
        for t in d["tiles"]:
            assert_enum("kpi-tiles", f"tiles[{t['label']!r}].dir",
                        t["dir"], {"up", "down", "flat"})
            sign = t["delta"].lstrip()[:1]
            expected = {"+": "up", "-": "down"}.get(sign, "flat")
            assert t["dir"] == expected, \
                (f"kpi-tiles: {t['label']!r} shows {t['delta']!r} with "
                 f"dir={t['dir']!r}; the arrow and the colour would contradict "
                 f"the number, and the colour is what gets read first")

if __name__ == "__main__":
    print(KpiTilesShowcaseController().build())
