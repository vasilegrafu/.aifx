"""Showcase controller for the `trace-id` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    id: str -- POSITIONAL AND REQUIRED; it becomes the element id, so it must be unique in the document

THE ARGUMENT BECOMES AN ELEMENT id, so the same trace id rendered
twice produces duplicate ids and every link to it lands on the first. That is
the entire hazard of this component and it is invisible in the rendered
page -- two identical spans look correct.
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


class TraceIdShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"ids": ["REQ-014", "REQ-021", "REQ-033"]}

    def _validate_context(self, d):
        """Distinct, and usable as URL fragments."""
        assert_all_drawn("trace-id", d, [("ids", ())])
        assert_labels("trace-id", "ids", d["ids"])
        for trace in d["ids"]:
            assert trace.replace("-", "").replace("_", "").isalnum(), \
                (f"trace-id: {trace!r} is not usable as a fragment; it is "
                 f"emitted directly as an element id")

if __name__ == "__main__":
    print(TraceIdShowcaseController().build())
