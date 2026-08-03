"""Showcase controller for the `price-history` component.

The macro it feeds must match the {# data: ... #} header in component.html.j2:

    bars[] {date:str, open:num, close:num, low:num, high:num, volume:num}

A SIX-TUPLE IS THE WORST SHIFT RISK IN THE SET -- the component's own
data header says so, which is why the keys are named. _validate_context checks
the one relation that makes a candle a candle: low <= min(open, close) and
high >= max(open, close). Values are LITERAL, never generated: a controller
using random would rewrite showcase.html on every build and --check would
never pass twice.
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


class ChartPriceHistoryShowcaseController(ShowcaseController):

    def _build_context(self):
        # 24 monthly bars. Written out rather than generated: a random walk
        # would make this page differ on every build, and `--check` would fail
        # forever without anything being wrong.
        bars = [
            {"date": "2025-01", "open": 142.0, "close": 140.48, "low": 138.83, "high": 142.39, "volume": 42.2},
            {"date": "2025-02", "open": 140.48, "close": 141.21, "low": 140.33, "high": 142.14, "volume": 67.4},
            {"date": "2025-03", "open": 141.21, "close": 136.66, "low": 136.49, "high": 142.31, "volume": 43.3},
            {"date": "2025-04", "open": 136.66, "close": 136.23, "low": 135.93, "high": 138.69, "volume": 50.9},
            {"date": "2025-05", "open": 136.23, "close": 137.87, "low": 134.81, "high": 140.22, "volume": 61.0},
            {"date": "2025-06", "open": 137.87, "close": 143.14, "low": 135.74, "high": 143.26, "volume": 54.8},
            {"date": "2025-07", "open": 143.14, "close": 139.68, "low": 138.9, "high": 143.44, "volume": 85.3},
            {"date": "2025-08", "open": 139.68, "close": 136.68, "low": 135.11, "high": 141.14, "volume": 59.6},
            {"date": "2025-09", "open": 136.68, "close": 137.51, "low": 136.53, "high": 137.67, "volume": 49.9},
            {"date": "2025-10", "open": 137.51, "close": 139.71, "low": 136.73, "high": 140.79, "volume": 72.0},
            {"date": "2025-11", "open": 139.71, "close": 139.57, "low": 137.57, "high": 140.46, "volume": 78.5},
            {"date": "2025-12", "open": 139.57, "close": 137.24, "low": 135.94, "high": 141.01, "volume": 88.8},
            {"date": "2026-01", "open": 137.24, "close": 139.94, "low": 134.82, "high": 140.67, "volume": 44.8},
            {"date": "2026-02", "open": 139.94, "close": 139.43, "low": 139.05, "high": 141.85, "volume": 66.4},
            {"date": "2026-03", "open": 139.43, "close": 134.96, "low": 133.1, "high": 141.11, "volume": 71.2},
            {"date": "2026-04", "open": 134.96, "close": 139.1, "low": 133.27, "high": 139.89, "volume": 72.5},
            {"date": "2026-05", "open": 139.1, "close": 140.28, "low": 137.0, "high": 141.43, "volume": 92.8},
            {"date": "2026-06", "open": 140.28, "close": 140.36, "low": 140.13, "high": 142.04, "volume": 78.7},
            {"date": "2026-07", "open": 140.36, "close": 142.26, "low": 138.28, "high": 144.8, "volume": 54.5},
            {"date": "2026-08", "open": 142.26, "close": 141.4, "low": 141.34, "high": 143.97, "volume": 64.8},
            {"date": "2026-09", "open": 141.4, "close": 138.23, "low": 138.08, "high": 141.7, "volume": 82.6},
            {"date": "2026-10", "open": 138.23, "close": 134.73, "low": 133.78, "high": 138.85, "volume": 88.5},
            {"date": "2026-11", "open": 134.73, "close": 130.83, "low": 129.54, "high": 135.82, "volume": 89.2},
            {"date": "2026-12", "open": 130.83, "close": 134.29, "low": 130.17, "high": 136.38, "volume": 62.1},
        ]

        return {"bars": bars, "recent": bars[-12:]}

    def _validate_context(self, d):
        """OHLC BRACKETING -- what makes a candle a candle.

        A bar whose low sits above its open draws upside-down and ECharts says
        nothing about it."""
        for key in ("bars", "recent"):
            bars = d[key]
            assert bars, f"price-history: {key} is empty"
            assert_labels("price-history", f"{key} dates", [b["date"] for b in bars])
            for field in ("open", "close", "low", "high", "volume"):
                assert_numbers("price-history", f"{key}.{field}",
                               [b[field] for b in bars])
            for i, b in enumerate(bars):
                assert b["low"] <= min(b["open"], b["close"]), \
                    (f"price-history: {key}[{i}] {b['date']} has low {b['low']} "
                     f"above min(open, close); the candle would draw inverted")
                assert b["high"] >= max(b["open"], b["close"]), \
                    (f"price-history: {key}[{i}] {b['date']} has high {b['high']} "
                     f"below max(open, close); the candle would draw inverted")
                assert b["volume"] >= 0, \
                    (f"price-history: {key}[{i}] has negative volume "
                     f"{b['volume']}; the lower panel would draw below its axis")

if __name__ == "__main__":
    print(ChartPriceHistoryShowcaseController().build())
