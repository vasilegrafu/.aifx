"""Showcase controller for the `steps` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    items: str[]   -- POSITIONAL AND REQUIRED, steps(items)

STEPS ARE INSTRUCTIONS THE READER CARRIES OUT, so each one starts
with a verb. A step that describes rather than instructs belongs in
`numbered`; the two look alike and the difference is whether the reader is
supposed to do anything.
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


class StepsShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"items": [
            "Pull the latest filing with the report controller.",
            "Run the shape assertions and read every failure before fixing "
            "any of them.",
            "Rebuild the report and diff it against the published page.",
            "Bump the version, rebuild every showcase, then tag.",
        ]}

    def _validate_context(self, d):
        """Distinct items, each beginning with an imperative verb.

        The check is crude -- a capitalised first word that is not a noun
        phrase -- but it catches the common drift into description."""
        assert_all_drawn("steps", d, [("items", ())])
        assert_labels("steps", "items", d["items"])
        for item in d["items"]:
            first = item.split()[0]
            assert first[0].isupper() and not first.endswith("ing"), \
                (f"steps: {item[:40]!r} does not open with an instruction; a "
                 f"step the reader cannot carry out belongs in `numbered`")

if __name__ == "__main__":
    print(StepsShowcaseController().build())
