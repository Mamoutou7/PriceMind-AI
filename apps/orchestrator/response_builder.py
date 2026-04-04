from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any


class ResponseBuilder:
    """Formats tool execution results into readable CLI output."""

    def build_response(self, execution_results: list[dict[str, Any]]) -> str:
        if not execution_results:
            return "No actions were executed."

        sections: list[str] = []

        for result in execution_results:
            tool_name = result["tool_name"]

            if not result["success"]:
                sections.append(f"✗ {tool_name} failed: {result['error']}")
                continue

            payload = result.get("data")

            if tool_name == "get_latest_prices":
                sections.append(self._format_latest_prices(payload))
            elif tool_name == "compare_prices":
                sections.append(self._format_price_comparison(payload))
            else:
                sections.append(
                    f"✓ {tool_name} executed successfully.\n"
                    f"{self._format_generic_payload(payload)}"
                )

        return "\n\n".join(section for section in sections if section.strip())

    def _format_latest_prices(self, payload: Any) -> str:
        normalized_payload = self._normalize_payload(payload)

        if not isinstance(normalized_payload, dict):
            return f"Unexpected response format: {normalized_payload}"

        records = normalized_payload.get("data", [])
        if not records:
            return "No pricing data available in the database."

        headers = [
            "Provider",
            "Model",
            "Input / 1M",
            "Output / 1M",
            "Currency",
            "Created At",
        ]
        rows = [
            [
                str(record.get("provider_name", "unknown")),
                str(record.get("model_name", "unknown")),
                self._format_number(record.get("input_price_per_1m")),
                self._format_number(record.get("output_price_per_1m")),
                str(record.get("currency", "USD")),
                str(record.get("created_at", "unknown")),
            ]
            for record in records
        ]

        return "Latest stored prices\n" + self._render_table(headers, rows)

    def _format_price_comparison(self, payload: Any) -> str:
        normalized_payload = self._normalize_payload(payload)

        if not isinstance(normalized_payload, dict):
            return f"Unexpected comparison response format: {normalized_payload}"

        records = normalized_payload.get("data", [])
        if not records:
            return "No comparison data available."

        headers = [
            "Provider",
            "Model",
            "Input / 1M",
            "Output / 1M",
            "Currency",
            "Created At",
        ]
        rows = [
            [
                str(record.get("provider_name", "unknown")),
                str(record.get("model_name", "unknown")),
                self._format_number(record.get("input_price_per_1m")),
                self._format_number(record.get("output_price_per_1m")),
                str(record.get("currency", "USD")),
                str(record.get("created_at", "unknown")),
            ]
            for record in records
        ]

        cheapest_input = self._find_cheapest(records, "input_price_per_1m")
        cheapest_output = self._find_cheapest(records, "output_price_per_1m")

        summary_lines: list[str] = []
        if cheapest_input:
            summary_lines.append(
                f"Cheapest input: {cheapest_input['provider_name']} ("
                f"{self._format_number(cheapest_input['input_price_per_1m'])} "
                f"{cheapest_input.get('currency', 'USD')})"
            )
        if cheapest_output:
            summary_lines.append(
                f"Cheapest output: {cheapest_output['provider_name']} ("
                f"{self._format_number(cheapest_output['output_price_per_1m'])} "
                f"{cheapest_output.get('currency', 'USD')})"
            )

        summary = "\n".join(summary_lines)
        table = self._render_table(headers, rows)
        return "Price comparison\n" + table + (f"\n{summary}" if summary else "")

    def _format_generic_payload(self, payload: Any) -> str:
        normalized_payload = self._normalize_payload(payload)

        if isinstance(normalized_payload, (dict, list)):
            return json.dumps(normalized_payload, indent=2, ensure_ascii=False)

        return str(normalized_payload)

    @staticmethod
    def _normalize_payload(payload: Any) -> Any:
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return payload
        return payload

    @staticmethod
    def _format_number(value: Any) -> str:
        if value is None:
            return "-"
        try:
            return f"{Decimal(str(value)):.4f}"
        except (InvalidOperation, ValueError):
            return str(value)

    @staticmethod
    def _find_cheapest(
        records: list[dict[str, Any]], field_name: str
    ) -> dict[str, Any] | None:
        candidates: list[dict[str, Any]] = []
        for record in records:
            value = record.get(field_name)
            if value is None:
                continue
            try:
                Decimal(str(value))
            except (InvalidOperation, ValueError):
                continue
            candidates.append(record)

        if not candidates:
            return None

        return min(candidates, key=lambda record: Decimal(str(record[field_name])))

    @staticmethod
    def _render_table(headers: list[str], rows: list[list[str]]) -> str:
        widths = [
            max(len(str(header)), *(len(str(row[index])) for row in rows))
            for index, header in enumerate(headers)
        ]

        def render_row(row: list[str]) -> str:
            return " | ".join(
                str(cell).ljust(widths[index]) for index, cell in enumerate(row)
            )

        divider = "-+-".join("-" * width for width in widths)

        return "\n".join(
            [
                render_row(headers),
                divider,
                *(render_row(row) for row in rows),
            ]
        )
