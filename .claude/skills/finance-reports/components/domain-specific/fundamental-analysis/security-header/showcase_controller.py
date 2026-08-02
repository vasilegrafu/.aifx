"""Showcase controller for the `security-header` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    facts[] {label:str, value:str} -- PRE-FORMATTED, because a price, a market cap and a sector name share no numeric format

VALUES ARE PRE-FORMATTED STRINGS, deliberately. These facts are
heterogeneous -- a price, a market cap, a sector -- and no single numeric
format fits them, so the caller formats and the component only places.
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


class SecurityHeaderShowcaseController(ShowcaseController):

    def _build_context(self):
        # Pre-formatted, and deliberately so: $476.15, $776B and "Technology"
        # have nothing in common that a `fmt` could express.
        facts = [
            {"label": "Price", "value": "$476.15"},
            {"label": "Market cap", "value": "$776B"},
            {"label": "Revenue Q1 FY2026", "value": "$10.3B"},
            {"label": "Net income Q1 FY2026", "value": "$1.4B"},
            {"label": "Sector", "value": "Technology"},
        ]

        # The minimum: a header still works with two facts, which is what an
        # early-stage or thinly-covered name usually has.
        sparse = [
            {"label": "Price", "value": "$12.08"},
            {"label": "Market cap", "value": "$1.9B"},
        ]
        return {"facts": facts, "sparse": sparse}

    def _validate_context(self, d):
        """Values are STRINGS. A raw number here would render unformatted.

        The component places what it is given; nothing downstream will turn
        776000000000 into "$776B"."""
        for key in ("facts", "sparse"):
            assert_rows("security-header", key, d[key], ("label", "value"))
            for i, f in enumerate(d[key]):
                assert isinstance(f["value"], str) and f["value"], \
                    (f"security-header: {key}[{i}] {f['label']!r} has value "
                     f"{f['value']!r}; these are PRE-FORMATTED strings, and a "
                     f"raw number would render exactly as it is")

if __name__ == "__main__":
    print(SecurityHeaderShowcaseController().build())
