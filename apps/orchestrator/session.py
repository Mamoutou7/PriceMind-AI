from __future__ import annotations

import asyncio

from apps.orchestrator.executor import ToolExecutor
from apps.orchestrator.planner import QueryPlanner
from apps.orchestrator.response_builder import ResponseBuilder
from apps.orchestrator.router import QueryRouter


class ChatSession:
    """Coordinates routing, planning, execution and response formatting."""

    def __init__(
        self,
        router: QueryRouter,
        planner: QueryPlanner,
        executor: ToolExecutor,
        response_builder: ResponseBuilder,
    ) -> None:
        self._router = router
        self._planner = planner
        self._executor = executor
        self._response_builder = response_builder

    async def run(self) -> None:
        print("MCP Pricing Assistant started. Type 'exit' to quit.")

        while True:
            user_query = await asyncio.to_thread(input, "\n> ")
            user_query = user_query.strip()

            if user_query.lower() in {"exit", "quit"}:
                print("Goodbye.")
                break

            intent = self._router.route_query(user_query)
            plan = self._planner.build_plan(intent)
            results = await self._executor.execute(plan)

            response = self._response_builder.build_response(results)
            print(response)
