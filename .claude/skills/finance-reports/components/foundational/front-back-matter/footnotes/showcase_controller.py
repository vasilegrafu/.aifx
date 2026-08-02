"""Showcase controller for the `footnotes` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    notes: str[] -- rendered 1..n; pair each with its own <sup class="fn"> in the prose

THE LIST IS NUMBERED BY POSITION AND NOTHING LINKS IT TO THE PROSE.
The component renders notes 1..n and the report is responsible for putting a
matching <sup class="fn"><a id="fnref-N" href="#fn-N">N</a></sup> at each
reference point -- so INSERTING a note in the middle silently renumbers every
reference after it. The prose below carries real markers, which is the only
way to see whether the pairing works.
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


class FootnotesShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"notes": [
            "Segment revenue for FY24 restated onto the reporting lines "
            "introduced in FY25 Q1. Group totals are unchanged.",
            "Free cash flow is cash from operations less capital expenditure, "
            "before acquisitions.",
            "Peer median excludes the two companies that changed fiscal year "
            "end during the period.",
        ]}

    def _validate_context(self, d):
        """Notes are distinct, and each is a sentence rather than a fragment.

        Distinct because two identical notes mean one of the references in the
        prose is pointing at the wrong number."""
        assert_all_drawn("footnotes", d, [("notes", ())])
        assert_labels("footnotes", "notes", d["notes"])
        for i, note in enumerate(d["notes"], 1):
            assert note.strip().endswith("."), \
                f"footnotes: note {i} is not a complete sentence"

if __name__ == "__main__":
    print(FootnotesShowcaseController().build())
