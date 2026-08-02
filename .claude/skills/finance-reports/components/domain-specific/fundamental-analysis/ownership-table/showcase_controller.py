"""Showcase controller for the `ownership-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    summary[] {label, value}   rows[] {holder:str, type:str, shares:str, stake:num, change:str, tone?:str}

`stake` IS A PERCENT NUMBER driving a bar; `shares` and `change` are
pre-formatted strings. Same split as aging-schedule, and the same place a
caller gets it wrong.
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


class OwnershipTableShowcaseController(ShowcaseController):

    def _build_context(self):
        summary = [
            {"label": "Institutional", "value": "68.4%"},
            {"label": "Insiders", "value": "1.2%"},
            {"label": "Retail and other", "value": "30.4%"},
            {"label": "Holders of record", "value": "2,841"},
        ]

        rows = [
            {"holder": "Vanguard Group", "type": "Index", "shares": "148.2m",
             "stake": 9.1, "change": "+0.4%"},
            {"holder": "BlackRock", "type": "Index", "shares": "132.6m",
             "stake": 8.2, "change": "+0.2%"},
            {"holder": "State Street", "type": "Index", "shares": "71.4m",
             "stake": 4.4, "change": "0.0%"},
            {"holder": "Fidelity", "type": "Active", "shares": "54.9m",
             "stake": 3.4, "change": "+2.8%", "tone": "good"},
            {"holder": "Capital Group", "type": "Active", "shares": "38.1m",
             "stake": 2.3, "change": "-6.1%", "tone": "bad"},
        ]
        return {"summary": summary, "rows": rows}

    def _validate_context(self, d):
        """`stake` is a PERCENT NUMBER; the string fields stay strings."""
        assert_rows("ownership-table", "summary", d["summary"], ("label", "value"))
        rows = d["rows"]
        assert_rows("ownership-table", "rows", rows,
                    ("holder", "type", "shares", "stake", "change"))
        for i, r in enumerate(rows):
            assert_numbers("ownership-table", f"rows[{i}].stake", [r["stake"]])
            assert 0 <= r["stake"] <= 100, \
                (f"ownership-table: rows[{i}] stake is {r['stake']}; a PERCENT "
                 f"NUMBER, because it drives a bar width")
            for field in ("shares", "change"):
                assert isinstance(r[field], str), \
                    (f"ownership-table: rows[{i}].{field} is {r[field]!r}; "
                     f"pre-formatted string, unlike `stake` beside it")
            if "tone" in r:
                assert_enum("ownership-table", f"rows[{i}].tone", r["tone"],
                            {"good", "neutral", "bad"})
        top = sum(r["stake"] for r in rows)
        assert top < 100, \
            (f"ownership-table: the listed holders total {top:.1f}%; this is a "
             f"TOP-N table, not a decomposition, so it must be under 100")
        # A per-row share does not sum to anything, so a single mis-scaled row
        # is indistinguishable from a genuinely tiny one -- 0.257 is a legal
        # value here. What IS catchable is the whole column arriving as
        # fractions, which is how this actually goes wrong.
        shares = [r["stake"] for r in d["rows"]]
        assert max(shares) >= 1.0,             (f"ownership-table: every stake is below 1 ({shares}); these are PERCENT "
             f"NUMBERS (25.7), and a column of fractions renders as a row of "
             f"bars too small to see rather than as an error")


if __name__ == "__main__":
    print(OwnershipTableShowcaseController().build())
