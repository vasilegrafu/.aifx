"""Showcase controller for the `badge` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    label: str   variant: str -- one of the status tones in blocks.css

FOUR VARIANTS ARE STYLED: good, bad, info, warn. Anything else is
not an error -- it renders as the plain pill, which reads as deliberate
neutrality rather than as the typo it usually is. The bare form is included
below so the two are distinguishable on sight.
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


class BadgeShowcaseController(ShowcaseController):

    def _build_context(self):
        # The four the stylesheet actually styles, in the order a reader
        # meets them: the verdict, the objection, the fact, the caveat.
        variants = [
            {"label": "Buy", "variant": "good"},
            {"label": "Covenant breach", "variant": "bad"},
            {"label": "FY25 Q2", "variant": "info"},
            {"label": "Unaudited", "variant": "warn"},
        ]
        return {"variants": variants}

    def _validate_context(self, d):
        """Every variant is one the stylesheet knows.

        The check StrictUndefined cannot make: an unrecognised variant renders
        the plain pill, so a typo looks like a design decision."""
        assert_rows("badge", "variants", d["variants"], ("label", "variant"), 4)
        assert_all_drawn("badge", d, [("variants", ())])
        for b in d["variants"]:
            assert_enum("badge", f"variants[{b['label']!r}].variant",
                        b["variant"], {"good", "bad", "info", "warn"})
        assert_labels("badge", "variant names",
                      [b["variant"] for b in d["variants"]])

if __name__ == "__main__":
    print(BadgeShowcaseController().build())
