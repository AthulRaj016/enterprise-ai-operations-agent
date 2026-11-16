from app.workflow import classify_request


def test_it_security_request_is_high_priority():
    result = classify_request("IT", "Urgent login access issue after a security alert")
    assert result == {"category": "it_support", "priority": "high"}


def test_policy_question_is_normal_priority():
    result = classify_request("HR", "Where can I find the leave policy?")
    assert result == {"category": "policy_question", "priority": "normal"}


def test_unrecognized_request_defaults_to_general():
    result = classify_request("Facilities", "Please replace a desk chair")
    assert result == {"category": "general_request", "priority": "normal"}
