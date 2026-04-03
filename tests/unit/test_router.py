from apps.orchestrator.router import IntentType, QueryRouter


def test_route_show_data() -> None:
    router = QueryRouter()
    intent = router.route_query("show data")
    assert intent.intent_type == IntentType.SHOW_STORED_DATA


def test_route_compare() -> None:
    router = QueryRouter()
    intent = router.route_query("compare cloudrift and deepinfra")
    assert intent.intent_type == IntentType.COMPARE_PROVIDERS