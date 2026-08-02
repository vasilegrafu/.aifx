"""Showcase controller for the `width` component.

This component takes a {% call %} BLOCK, not data -- which is why
component.html.j2 carries no {# data: #} header. The context supplies only the
arguments; the body lives in the view.

    width(w="24rem", align="left")   -- align adds width-center / width-right

`w` IS SET AS A CSS CUSTOM PROPERTY WITH NO VALIDATION. A bare number
is not a length, so `w="400"` is ignored by the browser and the block falls
back to its default width -- silently, and only in the rendered page.

`align` only emits a class when it is not "left", so "centre" spelled the
British way produces `width-centre`, which has no rule.
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


class WidthShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"w": "20rem", "aligns": ["left", "center", "right"],
                "body": "Net debt to EBITDA of 1.13x against a covenant of "
                        "2.5x, tested quarterly."}

    def _validate_context(self, d):
        """The width is a CSS length, and every alignment has a rule."""
        assert_all_drawn("width", d, [("w", ("aligns", "body"))])
        units = ("rem", "em", "px", "%", "ch", "vw")
        assert d["w"].endswith(units), \
            (f"width: w is {d['w']!r}, which is not a CSS length; the browser "
             f"drops it and the block silently keeps its default width")
        assert_labels("width", "aligns", d["aligns"])
        for align in d["aligns"]:
            assert_enum("width", "aligns", align, {"left", "center", "right"})

if __name__ == "__main__":
    print(WidthShowcaseController().build())
