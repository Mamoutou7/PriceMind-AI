from __future__ import annotations

from typing import Any


class ComparisonService:
    """Builds a small analytics summary over provider price rows."""

    def summarize(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {
                "success": True,
                "row_count": 0,
                "cheapest_input": None,
                "cheapest_output": None,
            }

        input_candidates = [row for row in rows if row.get("input_price_per_1m") is not None]
        output_candidates = [row for row in rows if row.get("output_price_per_1m") is not None]

        cheapest_input = min(
            input_candidates,
            key=lambda row: float(row["input_price_per_1m"]),
            default=None,
        )
        cheapest_output = min(
            output_candidates,
            key=lambda row: float(row["output_price_per_1m"]),
            default=None,
        )

        return {
            "success": True,
            "row_count": len(rows),
            "cheapest_input": cheapest_input,
            "cheapest_output": cheapest_output,
        }