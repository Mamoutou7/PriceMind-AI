import pytest

from apps.orchestrator.router import IntentType, QueryRouter

pytestmark = pytest.mark.unit


def test_price_lookup_intent():
    router = QueryRouter()

    intent = router.route_query("price of llama 3.3 70b on groq")

    assert intent.intent_type == IntentType.PRICE_LOOKUP
    assert "groq" in intent.providers
    assert "llama" in intent.model_name


def test_compare_intent():
    router = QueryRouter()

    intent = router.route_query("compare groq and fireworks for llama")

    assert intent.intent_type == IntentType.COMPARE_PROVIDERS
    assert len(intent.providers) >= 2


def test_show_data_intent():
    router = QueryRouter()

    intent = router.route_query("show data")

    assert intent.intent_type == IntentType.SHOW_STORED_DATA


def test_unknown_intent():
    router = QueryRouter()

    intent = router.route_query("hello world")

    assert intent.intent_type == IntentType.UNKNOWN
