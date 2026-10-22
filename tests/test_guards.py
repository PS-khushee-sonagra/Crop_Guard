from cropguard.agent.agent_cropguard import answer_user
from cropguard.agent.guards import validate_crop, validate_symptoms, grounding_check, safe_fallback


def test_answer_user_returns_farmer_friendly_grounded_response():
    response = answer_user("My tomato leaves have dark rings with yellow edges", crop="tomato", location="Nashik")
    assert "most consistent with Early blight" in response
    assert "Lookalikes to rule out" in response
    assert "Management:" in response


def test_validate_crop_rejects_missing_or_unknown_crop():
    assert validate_crop("tomato")[0] is True
    assert validate_crop("")[0] is False
    assert validate_crop("apple")[0] is False


def test_validate_symptoms_rejects_empty_or_null_lists():
    assert validate_symptoms(["yellow spots"])[0] is True
    assert validate_symptoms([])[0] is False
    assert validate_symptoms(None)[0] is False


def test_grounding_check_flags_ungrounded_disease_names():
    evidence = {"disease_names": ["early blight"]}
    assert grounding_check("Early blight is likely.", evidence) is True
    assert grounding_check("Powdery mildew is likely.", evidence) is False


def test_safe_fallback_uses_clear_message():
    answer = safe_fallback("Need more information")
    assert "need more information" in answer.lower()
