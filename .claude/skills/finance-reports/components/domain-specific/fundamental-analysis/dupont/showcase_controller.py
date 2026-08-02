"""Showcase controller for the `dupont` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    factors[] {name:str, cells:str[]}   result? {label:str, cells:str[]} -- multiplicative drivers

THE FACTORS MULTIPLY to the result -- that is the whole point of a
DuPont decomposition, and it is the one thing the table can get wrong while
looking perfectly reasonable. Checked here on the underlying numbers.
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


class DupontShowcaseController(ShowcaseController):

    def _build_context(self):
        periods = ["FY23", "FY24", "FY25"]

        # ROE = margin x turnover x leverage. Kept as the numbers too, so
        # _validate_context can multiply them rather than trust the strings.
        self._raw = {
            "Net margin": [0.041, 0.069, 0.133],
            "Asset turnover": [0.36, 0.38, 0.48],
            "Equity multiplier": [1.22, 1.24, 1.24],
        }
        factors = [
            {"name": "Net margin", "cells": ["4.1%", "6.9%", "13.3%"]},
            {"name": "Asset turnover", "cells": ["0.36x", "0.38x", "0.48x"]},
            {"name": "Equity multiplier", "cells": ["1.22x", "1.24x", "1.24x"]},
        ]
        result = {"label": "Return on equity",
                  "cells": ["1.8%", "3.3%", "7.9%"]}

        return {"periods": periods, "factors": factors, "result": result}

    def _validate_context(self, d):
        """THE FACTORS MULTIPLY TO THE RESULT.

        A DuPont table whose factors do not reconstruct the headline is a
        decomposition of something else, and it renders identically."""
        assert_rows("dupont", "factors", d["factors"], ("name", "cells"))
        for i, f in enumerate(d["factors"]):
            assert len(f["cells"]) == len(d["periods"]), \
                f"dupont: factors[{i}] {f['name']!r} has the wrong cell count"

        for p, period in enumerate(d["periods"]):
            product = 1.0
            for name in self._raw:
                product *= self._raw[name][p]
            stated = float(d["result"]["cells"][p].rstrip("%")) / 100
            assert abs(product - stated) < 0.002, \
                (f"dupont: {period} factors multiply to {product:.4f} but the "
                 f"result says {stated:.4f}; the decomposition does not "
                 f"reconstruct its own headline")

if __name__ == "__main__":
    print(DupontShowcaseController().build())
