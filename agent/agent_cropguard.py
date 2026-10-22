from __future__ import annotations

import argparse

from cropguard.agent.guards import grounding_check, safe_fallback, validate_crop, validate_symptoms
from cropguard.agent.intent_router import classify_intent
from cropguard.agent.kb_answers import answer_crop_list, answer_prevention
from cropguard.mcp_server.tools.knowledge import get_crop_info, get_ipm_guidance, search_pest_disease
from cropguard.mcp_server.tools.weather import get_weather


def execute_tool_call(tool_name, **kwargs):
    tool_name = str(tool_name).strip()
    if tool_name == "get_crop_info":
        return get_crop_info(kwargs.get("crop"))
    if tool_name == "search_pest_disease":
        return search_pest_disease(kwargs.get("crop"), kwargs.get("symptoms", []))
    if tool_name == "get_ipm_guidance":
        return get_ipm_guidance(kwargs.get("crop"), kwargs.get("issue_id"))
    if tool_name == "get_weather":
        return get_weather(kwargs.get("location"), kwargs.get("days", 3))
    raise ValueError(f"Unsupported tool: {tool_name}")


def build_final_answer(crop, symptoms, match_result, weather_result, guidance_result, location=None):
    crop_ok, crop_value = validate_crop(crop)
    if not crop_ok:
        return safe_fallback(crop_value)

    symptom_ok, symptom_list = validate_symptoms(symptoms)
    if not symptom_ok:
        return safe_fallback("I need more information about the damage you are noticing.")

    if match_result.get("status") != "ok":
        return safe_fallback("I need more detail to narrow the diagnosis.")

    top = match_result["matches"][0]
    weather_summary = weather_result.get("summary", "Weather is variable.") if weather_result else "Weather is variable."
    guidance_steps = guidance_result.get("steps", []) if guidance_result else []
    location_note = f" in {location}" if location else ""
    lookalikes = top.get("lookalikes") or ["no clear alternative"]
    management_text = "; ".join(guidance_steps[:3]) if guidance_steps else "Monitor closely and collect more evidence."

    answer = (
        f"Based on your description, the symptoms are most consistent with {top['name']} on {crop_value}{location_note}. "
        f"The strongest match is {top['name']} (match score {top['score']}). "
        f"Lookalikes to rule out: {', '.join(lookalikes)}. "
        f"Weather context: {weather_summary} "
        f"Management: {management_text}."
    )

    evidence = {"disease_names": [top["name"]]}
    if grounding_check(answer, evidence):
        return answer
    return safe_fallback("I need more information to give a grounded recommendation.")


def answer_user(question, crop=None, location=None):
    intent = classify_intent(question)
    question_text = str(question or "").strip()

    if intent == "greeting":
        return "I can help diagnose crop issues and give management advice for tomato, wheat, or cotton."
    if intent == "list":
        return answer_crop_list()["message"]
    if intent == "prevention":
        crop_ok, crop_value = validate_crop(crop or "tomato")
        if not crop_ok:
            return safe_fallback(crop_value)
        return answer_prevention(crop_value, question_text)

    crop_ok, crop_value = validate_crop(crop)
    if not crop_ok:
        return "Which crop do you want diagnosed: tomato, wheat, or cotton?"

    symptom_ok, symptom_list = validate_symptoms(question_text)
    if not symptom_ok:
        return "Please tell me what symptoms you are seeing on the crop."

    match_result = search_pest_disease(crop_value, symptom_list)
    if match_result.get("status") != "ok":
        return safe_fallback("I need more information about the symptom pattern and crop.")

    weather_result = get_weather(location) if location else {"summary": "Current weather context is unavailable."}
    guidance_result = get_ipm_guidance(crop_value, match_result["matches"][0]["issue_id"])
    return build_final_answer(crop_value, symptom_list, match_result, weather_result, guidance_result, location)


def main():
    parser = argparse.ArgumentParser(description="CropGuard Version 1 CLI")
    parser.add_argument("--crop", help="Crop to diagnose: tomato, wheat, or cotton")
    parser.add_argument("--location", help="Location used for weather context")
    parser.add_argument("question", nargs="?", help="Question or symptom description")
    args = parser.parse_args()

    question = args.question or input("What do you need help with? ")
    print(answer_user(question, crop=args.crop, location=args.location))


if __name__ == "__main__":
    main()
