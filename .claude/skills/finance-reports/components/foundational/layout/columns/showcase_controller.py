"""Showcase controller for the `columns` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    columns()   -- no arguments; it holds `column` calls

COLUMNS WRAP AND STACK WHEN THE PAGE IS NARROW, which is why this is
a layout component and not a table. Anything whose meaning depends on cells
staying side by side is a table; anything that reads fine stacked belongs
here.
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


class ColumnsShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"cells": [
            {"title": "Bull", "body": "Migration lands on time; net retention "
                                      "returns above 110%."},
            {"title": "Base", "body": "Migration slips one quarter; retention "
                                      "flat at 104%."},
            {"title": "Bear", "body": "Covenant test failed at FY26 Q2; equity "
                                      "raised at a discount."},
        ]}

    def _validate_context(self, d):
        """Distinct titles and bodies."""
        assert_all_drawn("columns", d, [("cells", ())])
        assert_rows("columns", "cells", d["cells"], ("title", "body"), 2)
        assert_labels("columns", "titles", [x["title"] for x in d["cells"]])
        assert_labels("columns", "bodies", [x["body"] for x in d["cells"]])

if __name__ == "__main__":
    print(ColumnsShowcaseController().build())
