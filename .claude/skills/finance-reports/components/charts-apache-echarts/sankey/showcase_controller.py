"""Showcase controller for the `sankey` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    nodes[] {name:str, role:source|stage|cost|retained}   links[] {source, target, value:num}

CONSERVATION IS THE CONTRACT. Inflows equal outflows at every
intermediate node, and _validate_context checks it here because nothing in the
rendering will: an unbalanced sankey draws perfectly and lies. The figures are
one company's income statement, so the arithmetic is a real identity rather
than numbers chosen to add up.
"""

import sys
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
# Why a marker and not a parent count: SKILL.md, "Adding a component showcase".
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from components._contracts import assert_labels, assert_numbers    # noqa: E402
from components._showcase_controller import ShowcaseController     # noqa: E402


class ChartSankeyShowcaseController(ShowcaseController):

    def _build_context(self):
        # An income statement, top to bottom. Every intermediate node
        # conserves -- see _validate_context, which proves it rather than
        # trusting it.
        nodes = [
            {"name": "Revenue", "role": "source"},
            {"name": "Cost of revenue", "role": "cost"},
            {"name": "Gross profit", "role": "stage"},
            {"name": "R&D", "role": "cost"},
            {"name": "SG&A", "role": "cost"},
            {"name": "Other operating", "role": "cost"},
            {"name": "Operating income", "role": "stage"},
            {"name": "Tax", "role": "cost"},
            {"name": "Net income", "role": "retained"},
        ]
        links = [
            {"source": "Revenue", "target": "Cost of revenue", "value": 19468},
            {"source": "Revenue", "target": "Gross profit", "value": 19081},
            {"source": "Gross profit", "target": "R&D", "value": 9019},
            {"source": "Gross profit", "target": "SG&A", "value": 3210},
            {"source": "Gross profit", "target": "Other operating", "value": 1104},
            {"source": "Gross profit", "target": "Operating income", "value": 5748},
            {"source": "Operating income", "target": "Tax", "value": 612},
            {"source": "Operating income", "target": "Net income", "value": 5136},
        ]

        # The same shape with one stage: the smallest sankey that is still a
        # sankey, and the one where a reader can check the arithmetic by eye.
        simple_nodes = [
            {"name": "Operating cash flow", "role": "source"},
            {"name": "Capital expenditure", "role": "cost"},
            {"name": "Free cash flow", "role": "retained"},
        ]
        simple_links = [
            {"source": "Operating cash flow", "target": "Capital expenditure",
             "value": 1420},
            {"source": "Operating cash flow", "target": "Free cash flow",
             "value": 4980},
        ]

        return {"nodes": nodes, "links": links,
                "simple_nodes": simple_nodes, "simple_links": simple_links}

    def _validate_context(self, d):
        """CONSERVATION, which is the one thing only this component can check.

        usage.md: "a sankey that does not balance is a chart that lies, and
        nothing in the rendering will tell you". So it is checked here, on
        every build, for both diagrams."""
        for nk, lk in (("nodes", "links"), ("simple_nodes", "simple_links")):
            nodes, links = d[nk], d[lk]
            names = [n["name"] for n in nodes]
            assert_labels("sankey", f"{nk} names", names)
            assert_numbers("sankey", f"{lk} values", [x["value"] for x in links])

            roles = {"source", "stage", "cost", "retained"}
            for n in nodes:
                assert n["role"] in roles, \
                    (f"sankey: {n['name']!r} has role {n['role']!r}; the four "
                     f"roles carry the colour, and a fifth would be uncoloured")
            for x in links:
                for end in ("source", "target"):
                    assert x[end] in names, \
                        (f"sankey: link {end} {x[end]!r} names no node; ECharts "
                         f"drops the ribbon and the diagram silently loses flow")

            # An intermediate node is one with flow both in and out. Its two
            # sides must agree, or the picture is not of a real decomposition.
            into, outof = {}, {}
            for x in links:
                into[x["target"]] = into.get(x["target"], 0) + x["value"]
                outof[x["source"]] = outof.get(x["source"], 0) + x["value"]
            for name in sorted(set(into) & set(outof)):
                assert into[name] == outof[name], \
                    (f"sankey: {name!r} takes in {into[name]} and sends out "
                     f"{outof[name]}; the diagram would draw and misstate the "
                     f"{abs(into[name] - outof[name])} difference")

if __name__ == "__main__":
    print(ChartSankeyShowcaseController().build())
