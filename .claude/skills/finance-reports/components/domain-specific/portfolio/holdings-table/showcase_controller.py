"""Showcase controller for the `holdings-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    headers: str[]   rows[] {name:str, weight:num, cells:str[], tone?:str}  total_row? {label, weight, cells} -- tone tints the LAST cell

`tone` TINTS THE LAST CELL ONLY, whichever column that happens to be.
Add a column and the tint silently moves with it, so the field means "colour
the rightmost thing" rather than "colour the return" -- put the column you
want tinted last, and check it again whenever the headers change.

Weights drive a bar as a percentage, so they must sum to 100 or the total row
is claiming a portfolio that does not exist.
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


class HoldingsTableShowcaseController(ShowcaseController):

    def _build_context(self):
        # One $2,450m strategy. Values are DERIVED from the weights, so the
        # column and the bars cannot disagree.
        aum = 2450.0
        positions = [
            ("Northwind Systems", 18.4, "Technology", "good", 24.1),
            ("Halcyon Industries", 15.2, "Industrials", "bad", -8.7),
            ("Pemberly Group", 13.7, "Financials", "good", 11.3),
            ("Vertex Data", 11.9, "Technology", "good", 31.6),
            ("Arden Healthcare", 9.8, "Healthcare", "neutral", 1.2),
            ("Calloway Energy", 8.3, "Energy", "bad", -14.5),
            ("Marchmont Retail", 7.1, "Consumer", "good", 6.9),
            ("Ashcombe Materials", 6.2, "Materials", "neutral", -0.4),
        ]
        rows = [{"name": name, "weight": weight, "tone": tone,
                 "cells": [sector, f"{aum * weight / 100:,.1f}",
                           f"{ret:+.1f}%"]}
                for name, weight, sector, tone, ret in positions]
        held = sum(p[1] for p in positions)
        cash = round(100 - held, 1)
        rows.append({"name": "Cash", "weight": cash, "tone": "neutral",
                     "cells": ["--", f"{aum * cash / 100:,.1f}", "--"]})

        total_row = {"label": "Total", "weight": "100.0%",
                     "cells": ["", f"{aum:,.1f}", "+9.8%"]}
        return {"headers": ["Sector", "Value ($m)", "Return"], "rows": rows,
                "total_row": total_row, "aum": aum}

    def _validate_context(self, d):
        """Weights sum to 100, every row is as wide as the headers, and the
        value column follows from the weight beside it."""
        assert_labels("holdings-table", "headers", d["headers"])
        assert_all_drawn("holdings-table", d,
                         [("headers", ("rows", "total_row", "aum"))])
        assert_rows("holdings-table", "rows", d["rows"],
                    ("name", "weight", "cells"), 2)
        assert_labels("holdings-table", "names",
                      [r["name"] for r in d["rows"]])

        weights = [r["weight"] for r in d["rows"]]
        assert_numbers("holdings-table", "weights", weights)
        assert abs(sum(weights) - 100) < 0.05, \
            (f"holdings-table: weights sum to {sum(weights):.1f}%, not 100%; "
             f"the total row prints 100% regardless and the bars are drawn "
             f"against a portfolio that does not exist")

        for r in d["rows"]:
            assert 0 <= r["weight"] <= 100, \
                (f"holdings-table: {r['name']!r} is {r['weight']}%; the bar "
                 f"computes past its track")
            assert len(r["cells"]) == len(d["headers"]), \
                (f"holdings-table: {r['name']!r} has {len(r['cells'])} cells "
                 f"against {len(d['headers'])} headers")
            if r.get("tone"):
                assert_enum("holdings-table", f"{r['name']!r}.tone", r["tone"],
                            {"good", "bad", "neutral"})
            value = float(r["cells"][1].replace(",", ""))
            expected = d["aum"] * r["weight"] / 100
            assert abs(value - expected) < 0.1, \
                (f"holdings-table: {r['name']!r} is {r['weight']}% of "
                 f"{d['aum']:,.0f} = {expected:,.1f}, but prints "
                 f"{r['cells'][1]}")

        assert len(d["total_row"]["cells"]) == len(d["headers"]), \
            "holdings-table: total_row does not span the headers"

if __name__ == "__main__":
    print(HoldingsTableShowcaseController().build())
