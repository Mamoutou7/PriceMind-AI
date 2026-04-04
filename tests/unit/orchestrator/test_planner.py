import pytest

from apps.orchestrator.planner import QueryPlanner
from apps.orchestrator.router import Intent, IntentType

pytestmark = pytest.mark.unit


def test_plan_compare():
    planner = QueryPlanner()

    intent = Intent(
        intent_type=IntentType.COMPARE_PROVIDERS,
        user_query="compare",
        providers=["groq"],
        model_name="llama",
    )

    plan = planner.build_plan(intent)

    assert len(plan.steps) > 0
    assert plan.steps[-1].tool_name == "compare_prices"


def test_plan_show_data():
    planner = QueryPlanner()

    intent = Intent(
        intent_type=IntentType.SHOW_STORED_DATA,
        user_query="show data",
        providers=[],
        model_name=None,
    )

    plan = planner.build_plan(intent)

    assert plan.steps[0].tool_name == "get_latest_prices"