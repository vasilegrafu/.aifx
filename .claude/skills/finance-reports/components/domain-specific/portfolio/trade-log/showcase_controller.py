"""Showcase controller for the `trade-log` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {date:str, symbol:str, side:buy|sell, size:str, price:str, result:str, rationale?:str}

`side` IS LOWERCASED FOR THE CLASS AND PRINTED AS GIVEN, so "Buy"
and "buy" style identically but read differently down the column. Pick one
casing and keep it.

THE RATIONALE IS THE POINT OF THE COMPONENT. A trade log without it is a
brokerage statement; with it, it is a record of what was believed at the time,
which is the only thing that makes the log worth reviewing afterwards.
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


class TradeLogShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"date": "2026-07-14", "symbol": "Vertex Data", "side": "buy",
             "size": "42,000", "price": "$88.20", "result": "+12.4%",
             "rationale": "Net retention stabilised at 118% for two quarters "
                          "while the multiple compressed to a 3-year low."},
            {"date": "2026-06-02", "symbol": "Calloway Energy", "side": "sell",
             "size": "18,500", "price": "$61.40", "result": "-14.5%",
             "rationale": "Thesis broke: the Permian divestment closed at a "
                          "third below the price used in the sum of the parts."},
            {"date": "2026-05-19", "symbol": "Northwind Systems",
             "side": "buy", "size": "26,000", "price": "$104.10",
             "result": "+13.7%",
             "rationale": "Added on the guidance withdrawal, against the "
                          "rating cut, on the view that the migration risk "
                          "was already in the price."},
            {"date": "2026-04-08", "symbol": "Ashcombe Materials",
             "side": "sell", "size": "9,200", "price": "$27.85",
             "result": "-0.4%"},
        ]
        return {"rows": rows}

    def _validate_context(self, d):
        """Sides are consistently cased, dates run newest first, and most
        trades carry the rationale the component exists for."""
        assert_rows("trade-log", "rows", d["rows"],
                    ("date", "symbol", "side", "size", "price", "result"), 2)
        assert_all_drawn("trade-log", d, [("rows", ())])
        for r in d["rows"]:
            assert_enum("trade-log", f"{r['symbol']!r}.side", r["side"],
                        {"buy", "sell"})
            assert r["side"].islower(), \
                (f"trade-log: side {r['side']!r} is not lowercase; the class "
                 f"is lowercased but the text is printed as given, so casing "
                 f"varies down the column while the styling does not")

        dates = [r["date"] for r in d["rows"]]
        assert dates == sorted(dates, reverse=True), \
            "trade-log: trades are not newest-first"
        explained = sum(1 for r in d["rows"] if r.get("rationale"))
        assert explained >= len(d["rows"]) - 1, \
            (f"trade-log: only {explained} of {len(d['rows'])} trades carry a "
             f"rationale; without it this is a brokerage statement")

if __name__ == "__main__":
    print(TradeLogShowcaseController().build())
