from __future__ import annotations

from apps.orchestrator.executor import ToolExecutor
from apps.orchestrator.llm_intent_resolver import LLMIntentResolver
from apps.orchestrator.planner import QueryPlanner
from apps.orchestrator.response_builder import ResponseBuilder


class AgentChatSession:
    """Interactive CLI loop driven by an LLM intent resolver."""

    def __init__(
        self,
        resolver: LLMIntentResolver,
        planner: QueryPlanner,
        executor: ToolExecutor,
        response_builder: ResponseBuilder,
    ) -> None:
        self._resolver = resolver
        self._planner = planner
        self._executor = executor
        self._response_builder = response_builder

    async def run(self) -> None:
        print("PriceMind AI CLI. Type 'exit' to quit.")

        while True:
            user_query = input("\n> ").strip()
            if user_query.lower() in {"exit", "quit"}:
                print("Goodbye.")
                break

            try:
                decision = self._resolver.resolve(user_query)
            except Exception as exc:
                print(f"\nLLM intent resolution failed: {exc}")
                continue

            if not decision.needs_tools:
                print(f"\n{decision.direct_answer or 'No tool needed.'}")
                continue

            plan = self._planner.build_plan(decision.intent)

            if not plan.steps:
                print("\nNo executable plan could be built for this request.")
                continue

            results = await self._executor.execute(plan)
            response = self._response_builder.build_response(results)

            print(f"\n{response}")
