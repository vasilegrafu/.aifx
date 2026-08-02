"""Showcase controller for the `metadata-header` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    report_name: str -- the kicker above the title   title: str   BOTH POSITIONAL AND REQUIRED

THERE IS NO AUTHOR, DATE OR VERSION HERE, and the component header
explains why at length: a generated report can restate its own build date
endlessly, and that is the date the FILE was written rather than the date the
DATA was true. Only the second matters, so as-of dates belong in the body
where a reader will weigh them. This showcase does not add them back.
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


class MetadataHeaderShowcaseController(ShowcaseController):

    def _build_context(self):
        return {"report_name": "Equity research",
                "title": "Northwind Systems — FY25 Q2 review",
                "asof": "Figures as of FY25 Q2, filed 24 July 2026. "
                        "Price as of the close on 31 July 2026."}

    def _validate_context(self, d):
        """A kicker that is a category and a title that names the subject."""
        assert_all_drawn("metadata-header", d,
                         [("report_name", ("title", "asof"))])
        assert d["report_name"] != d["title"], \
            "metadata-header: the kicker repeats the title, so it says nothing"
        assert len(d["report_name"].split()) <= 4, \
            (f"metadata-header: report_name is {len(d['report_name'].split())} "
             f"words; it is a category label, not a sentence")
        # The point of the component header, kept true here.
        assert any(ch.isdigit() for ch in d["asof"]), \
            ("metadata-header: the as-of line carries no date, which is the "
             "one thing the cover deliberately leaves to the body")

if __name__ == "__main__":
    print(MetadataHeaderShowcaseController().build())
