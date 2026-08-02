"""Showcase controller for the `requirement` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    id: str   title: str   priority: str   label: str   description: str   fit: str

`priority` IS THE CLASS AND `label` IS THE WORD, and nothing ties
them together. blocks.css styles priority-must, priority-should, priority-could
and priority-wont; a card with priority="must" and label="Should" renders the
must colour under the word Should. The pairs below are derived from one map.

`fit` MUST BE MEASURABLE. It is the field that decides whether the requirement
was met, and "works well" is how that decision gets made by whoever is in the
room.
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


class RequirementShowcaseController(ShowcaseController):

    def _build_context(self):
        # One map, so the styled class and the printed word cannot drift.
        PRIORITIES = {"must": "Must", "should": "Should",
                      "could": "Could", "wont": "Won't"}

        cards = [
            {"id": "REQ-014", "priority": "must",
             "title": "A report is regenerated, never edited",
             "description": "The controller rebuilds the whole page from source "
                            "data on every run. No published page is patched in "
                            "place.",
             "fit": "Rebuilding an unchanged report twice produces two "
                    "byte-identical files."},
            {"id": "REQ-021", "priority": "should",
             "title": "Every figure names the filing it came from",
             "description": "Each statement block carries the period and the "
                            "form type behind its numbers.",
             "fit": "A reader can trace any printed figure to a filing in one "
                    "step, without leaving the page."},
            {"id": "REQ-033", "priority": "wont",
             "title": "Intraday price updates",
             "description": "Reports are built against filings and close "
                            "prices. Live quotes are out of scope for this "
                            "release.",
             "fit": "No component reads a quote endpoint at render time."},
        ]
        for card in cards:
            card["label"] = PRIORITIES[card["priority"]]
        return {"cards": cards}

    def _validate_context(self, d):
        """The priority class and the printed label agree, and every fit
        criterion is stated as something checkable."""
        assert_rows("requirement", "cards", d["cards"],
                    ("id", "title", "priority", "label", "description", "fit"), 2)
        assert_all_drawn("requirement", d, [("cards", ())])
        assert_labels("requirement", "ids", [c["id"] for c in d["cards"]])
        expected = {"must": "Must", "should": "Should",
                    "could": "Could", "wont": "Won't"}
        for card in d["cards"]:
            assert_enum("requirement", f"{card['id']}.priority",
                        card["priority"], set(expected))
            assert card["label"] == expected[card["priority"]], \
                (f"requirement: {card['id']} is styled priority-"
                 f"{card['priority']} but printed {card['label']!r}; the "
                 f"colour and the word would disagree")
            assert len(card["fit"]) > 30, \
                (f"requirement: {card['id']} fit criterion is too short to be "
                 f"measurable; it is the field that decides whether the "
                 f"requirement was met")

if __name__ == "__main__":
    print(RequirementShowcaseController().build())
