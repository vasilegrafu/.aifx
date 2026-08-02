"""Showcase controller for the `debt-maturity` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items[] {period:str, amount:str, share:num, rate:str, instrument:str} -- share is % of total debt

THE SHARES SUM TO 100 -- this is a decomposition of one debt stack,
so a schedule where they do not is describing part of it while labelling it as
the whole.
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


class DebtMaturityShowcaseController(ShowcaseController):

    def _build_context(self):
        items = [
            {"period": "FY26", "amount": "$180m", "share": 4.6,
             "rate": "3.9%", "instrument": "Revolving facility"},
            {"period": "FY27", "amount": "$750m", "share": 19.4,
             "rate": "2.95%", "instrument": "Senior notes"},
            {"period": "FY29", "amount": "$1,100m", "share": 28.4,
             "rate": "4.375%", "instrument": "Senior notes"},
            {"period": "FY32", "amount": "$1,241m", "share": 32.1,
             "rate": "3.75%", "instrument": "Senior notes"},
            {"period": "FY45", "amount": "$600m", "share": 15.5,
             "rate": "5.125%", "instrument": "Senior notes"},
        ]

        # A wall: one year carrying most of the stack, which is the shape the
        # component exists to make visible.
        wall = [
            {"period": "FY26", "amount": "$120m", "share": 4.0,
             "rate": "4.1%", "instrument": "Term loan"},
            {"period": "FY27", "amount": "$2,580m", "share": 86.0,
             "rate": "6.25%", "instrument": "Senior notes"},
            {"period": "FY30", "amount": "$300m", "share": 10.0,
             "rate": "5.5%", "instrument": "Senior notes"},
        ]
        return {"items": items, "wall": wall}

    def _validate_context(self, d):
        """Shares sum to 100 -- one debt stack, decomposed."""
        for key in ("items", "wall"):
            items = d[key]
            assert_rows("debt-maturity", key, items,
                        ("period", "amount", "share", "rate", "instrument"))
            for i, it in enumerate(items):
                assert_numbers("debt-maturity", f"{key}[{i}].share", [it["share"]])
                assert 0 <= it["share"] <= 100, \
                    (f"debt-maturity: {key}[{i}] share is {it['share']}; a "
                     f"PERCENT NUMBER, because it drives a bar width")
            total = sum(i["share"] for i in items)
            assert abs(total - 100) < 0.4, \
                (f"debt-maturity: {key} shares sum to {total:.1f}, not 100; the "
                 f"schedule would show part of the stack while labelling it "
                 f"as the whole")

if __name__ == "__main__":
    print(DebtMaturityShowcaseController().build())
