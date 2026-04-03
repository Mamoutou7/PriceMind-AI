from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.orchestrator.router import Intent, IntentType


@dataclass(frozen=True)
class PlanStep:
    tool_name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ExecutionPlan:
    steps: list[PlanStep]


class QueryPlanner:
    """Builds an execution plan from user intent."""

    def build_plan(self, intent: Intent) -> ExecutionPlan:
        if intent.intent_type == IntentType.SHOW_STORED_DATA:
            return ExecutionPlan(
                steps=[
                    PlanStep(
                        tool_name="get_latest_prices",
                        arguments={"limit": 10},
                    )
                ]
            )

        if intent.intent_type in {
            IntentType.PRICE_LOOKUP,
            IntentType.COMPARE_PROVIDERS,
        }:
            if not intent.providers or not intent.model_name:
                return ExecutionPlan(steps=[])

            steps: list[PlanStep] = []

            for provider in intent.providers:
                steps.extend(
                    [
                        PlanStep(
                            tool_name="scrape_provider",
                            arguments={
                                "provider_name": provider,
                                "url": self._provider_url(provider),
                            },
                        ),
                        PlanStep(
                            tool_name="get_raw_provider_content",
                            arguments={"provider_name": provider},
                        ),
                        PlanStep(
                            tool_name="parse_provider_content",
                            arguments={
                                "provider_name": provider,
                                "__from_previous__": "raw_content",
                            },
                        ),
                        PlanStep(
                            tool_name="store_parsed_prices",
                            arguments={
                                "__from_previous__": "parsed_prices",
                            },
                        ),
                    ]
                )

            if intent.intent_type == IntentType.COMPARE_PROVIDERS:
                steps.append(
                    PlanStep(
                        tool_name="compare_prices",
                        arguments={
                            "providers": intent.providers,
                            "model_name": intent.model_name,
                        },
                    )
                )
            else:
                steps.append(
                    PlanStep(
                        tool_name="compare_prices",
                        arguments={
                            "providers": intent.providers,
                            "model_name": intent.model_name,
                        },
                    )
                )

            return ExecutionPlan(steps=steps)

        return ExecutionPlan(steps=[])

    @staticmethod
    def _provider_url(provider_name: str) -> str:
        urls = {
            "cloudrift": "https://www.cloudrift.ai/pricing",
            "deepinfra": "https://deepinfra.com/pricing",
            "fireworks": "https://fireworks.ai/pricing",
            "groq": "https://groq.com/pricing",
        }
        return urls[provider_name]