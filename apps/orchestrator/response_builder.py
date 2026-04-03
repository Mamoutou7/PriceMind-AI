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
        ]
        rows = [
            [
                str(record.get("provider_name", "unknown")),
                str(record.get("model_name", "unknown")),
                self._format_number(record.get("input_price_per_1m")),
                self._format_number(record.get("output_price_per_1m")),
                str(record.get("currency", "USD")),
            ]
            for record in records
        ]

        cheapest_input = self._find_cheapest(records, "input_price_per_1m")
        cheapest_output = self._find_cheapest(records, "output_price_per_1m")

        summary_lines = ["Price comparison", self._render_table(headers, rows)]

        if cheapest_input:
            summary_lines.append(
                "Cheapest input price: "
                f"{cheapest_input['provider_name']} "
                f"({self._format_number(cheapest_input['input_price_per_1m'])} "
                f"{cheapest_input.get('currency', 'USD')})"
            )

        if cheapest_output:
            summary_lines.append(
                "Cheapest output price: "
                f"{cheapest_output['provider_name']} "
                f"({self._format_number(cheapest_output['output_price_per_1m'])} "
                f"{cheapest_output.get('currency', 'USD')})"
            )

        return "\n".join(summary_lines)

    def _format_generic_payload(self, payload: Any) -> str:
        normalized_payload = self._normalize_payload(payload)

        if isinstance(normalized_payload, (dict, list)):
            return json.dumps(normalized_payload, indent=2, ensure_ascii=False)

        return str(normalized_payload)

    def _normalize_payload(self, payload: Any) -> Any:
        if payload is None:
            return None

        if isinstance(payload, (dict, list, str, int, float, bool)):
            return payload

        content = getattr(payload, "content", None)
        if content:
            text_fragments: list[str] = []

            for item in content:
                item_text = getattr(item, "text", None)
                if item_text:
                    text_fragments.append(item_text)

            if text_fragments:
                joined_text = "\n".join(text_fragments).strip()

                try:
                    return json.loads(joined_text)
                except json.JSONDecodeError:
                    return joined_text

        return str(payload)

    def _render_table(self, headers: list[str], rows: list[list[str]]) -> str:
        if not rows:
            return "No data available."

        string_rows = [[str(cell) for cell in row] for row in rows]
        widths = [
            max(len(headers[index]), *(len(row[index]) for row in string_rows))
            for index in range(len(headers))
        ]

        def make_border() -> str:
            return "+-" + "-+-".join("-" * width for width in widths) + "-+"

        def make_row(row: list[str]) -> str:
            cells = [
                row[index].ljust(widths[index]) for index in range(len(widths))
            ]
            return "| " + " | ".join(cells) + " |"

        lines = [
            make_border(),
            make_row(headers),
            make_border(),
        ]

        for row in string_rows:
            lines.append(make_row(row))

        lines.append(make_border())
        return "\n".join(lines)

    def _find_cheapest(
        self,
        records: list[dict[str, Any]],
        field_name: str,
    ) -> dict[str, Any] | None:
        valid_records: list[dict[str, Any]] = []

        for record in records:
            value = record.get(field_name)
            if value is None:
                continue

            try:
                Decimal(str(value))
            except (InvalidOperation, ValueError):
                continue

            valid_records.append(record)

        if not valid_records:
            return None

        return min(valid_records, key=lambda record: Decimal(str(record[field_name])))

    def _format_number(self, value: Any) -> str:
        if value is None:
            return "N/A"

        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return str(value)

        normalized = number.normalize()
        return format(normalized, "f").rstrip("0").rstrip(".") if "." in format(normalized, "f") else format(normalized, "f")