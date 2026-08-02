"""Showcase controller for the `five-forces` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    forces[] {name:str, rating:str, tone:good|neutral|bad, evidence:str}

EVERY FORCE CARRIES EVIDENCE. Without it the component is five
opinions in a coloured table, which is the failure mode of every strategy
framework ever put in a deck.
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


class FiveForcesShowcaseController(ShowcaseController):

    def _build_context(self):
        forces = [
            {"name": "Rivalry", "rating": "High", "tone": "bad",
             "evidence": "Two credible competitors at 3x and 0.4x the revenue, "
                         "both funding a full roadmap"},
            {"name": "Supplier power", "rating": "Very high", "tone": "bad",
             "evidence": "One foundry at the leading node; allocation is "
                         "negotiated annually and not contractually secured"},
            {"name": "Buyer power", "rating": "Moderate", "tone": "neutral",
             "evidence": "Top five customers are 38% of revenue, but switching "
                         "costs a design cycle of 18 months"},
            {"name": "Substitutes", "rating": "Low", "tone": "good",
             "evidence": "No general-purpose alternative at this performance "
                         "per watt; ASICs address narrow workloads only"},
            {"name": "New entrants", "rating": "Low", "tone": "good",
             "evidence": "$9bn of annual R&D and a decade of IP; three "
                         "well-funded attempts have exited since 2015"},
        ]
        return {"forces": forces}

    def _validate_context(self, d):
        """Every force needs EVIDENCE, and it must be a sentence, not a word.

        A rating with no evidence is an opinion in a coloured table."""
        forces = d["forces"]
        assert_rows("five-forces", "forces", forces,
                    ("name", "rating", "tone", "evidence"), minimum=5)
        for i, f in enumerate(forces):
            assert_enum("five-forces", f"forces[{i}].tone", f["tone"],
                        {"good", "neutral", "bad"})
            assert len(f["evidence"].split()) >= 6, \
                (f"five-forces: forces[{i}] {f['name']!r} has evidence "
                 f"{f['evidence']!r}; a rating with no argument under it is an "
                 f"opinion in a coloured table")

if __name__ == "__main__":
    print(FiveForcesShowcaseController().build())
