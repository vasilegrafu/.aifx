"""Showcase controller for the `recommendation` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    facts[] {label:str, value:str}   tone: good|neutral|bad

THE TONE IS THE WHOLE COMPONENT -- it is the one place a report
states a view rather than a number. All three appear here, because a showcase
of one tone shows a third of it.
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


class RecommendationShowcaseController(ShowcaseController):

    def _build_context(self):
        buy = [
            {"label": "Rating", "value": "Add"},
            {"label": "Target", "value": "$132"},
            {"label": "Against last close", "value": "+11.5%"},
            {"label": "Horizon", "value": "12 months"},
        ]
        hold = [
            {"label": "Rating", "value": "Hold"},
            {"label": "Target", "value": "$118"},
            {"label": "Against last close", "value": "-0.3%"},
            {"label": "Horizon", "value": "12 months"},
        ]
        sell = [
            {"label": "Rating", "value": "Reduce"},
            {"label": "Target", "value": "$92"},
            {"label": "Against last close", "value": "-22.3%"},
            {"label": "Horizon", "value": "12 months"},
        ]
        return {"buy": buy, "hold": hold, "sell": sell}

    def _validate_context(self, d):
        """Three fact sets, one per tone, each with the same four labels.

        The comparison only works if the sets differ in VALUE and not in
        shape."""
        shapes = []
        for key in ("buy", "hold", "sell"):
            assert_rows("recommendation", key, d[key], ("label", "value"))
            shapes.append(tuple(f["label"] for f in d[key]))
        assert len(set(shapes)) == 1, \
            (f"recommendation: the three fact sets carry different labels "
             f"{shapes}; side by side they are meant to differ in value only, "
             f"so the tone is the variable under test")

if __name__ == "__main__":
    print(RecommendationShowcaseController().build())
