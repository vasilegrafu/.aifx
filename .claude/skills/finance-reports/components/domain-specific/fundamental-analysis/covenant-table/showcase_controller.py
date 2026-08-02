"""Showcase controller for the `covenant-table` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    rows[] {covenant:str, test:str, limit:str, actual:str, headroom:str, status:pass|tight|breach}

ALL THREE STATUSES APPEAR. A covenant table showing only passes
demonstrates the one state that needs no component -- the value is in how a
tight test and a breach read differently at a glance.
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


class CovenantTableShowcaseController(ShowcaseController):

    def _build_context(self):
        rows = [
            {"covenant": "Net leverage", "test": "Net debt / EBITDA",
             "limit": "≤ 3.50x", "actual": "0.42x", "headroom": "3.08x",
             "status": "pass"},
            {"covenant": "Interest cover", "test": "EBITDA / interest",
             "limit": "≥ 3.00x", "actual": "3.24x", "headroom": "0.24x",
             "status": "tight"},
            {"covenant": "Minimum liquidity", "test": "Cash + undrawn RCF",
             "limit": "≥ $2,000m", "actual": "$14,347m", "headroom": "$12,347m",
             "status": "pass"},
            {"covenant": "Capex limit", "test": "Annual capex",
             "limit": "≤ $1,250m", "actual": "$1,420m", "headroom": "-$170m",
             "status": "breach"},
        ]
        clean = [r for r in rows if r["status"] == "pass"]
        return {"rows": rows, "clean": clean}

    def _validate_context(self, d):
        """`status` is one of three, and the full table shows all three."""
        for key in ("rows", "clean"):
            rows = d[key]
            assert_rows("covenant-table", key, rows,
                        ("covenant", "test", "limit", "actual", "headroom",
                         "status"))
            for i, r in enumerate(rows):
                assert_enum("covenant-table", f"{key}[{i}].status", r["status"],
                            {"pass", "tight", "breach"})
        seen = {r["status"] for r in d["rows"]}
        assert seen == {"pass", "tight", "breach"}, \
            (f"covenant-table: the full table shows {sorted(seen)}; all three "
             f"statuses should appear, since a table of passes demonstrates "
             f"the one state that needs no component")

if __name__ == "__main__":
    print(CovenantTableShowcaseController().build())
