import re

ALLOWED_CROPS = {"tomato", "wheat", "cotton"}


def validate_crop(value):
    if value is None:
        return False, "Crop is required."
    crop = str(value).strip().lower()
    if not crop:
        return False, "Crop is required."
    if crop not in ALLOWED_CROPS:
        return False, f"Unsupported crop: {value}. We cover tomato, wheat, and cotton."
    return True, crop


def validate_symptoms(value):
    if value is None:
        return False, "Symptoms are required."
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        return False, "Symptoms should be a list of words or phrases."

    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return False, "Symptoms are required."
    return True, cleaned


def grounding_check(answer, evidence):
    if not answer:
        return False
    if not evidence:
        return False
    answer_text = answer.lower()
    disease_names = evidence.get("disease_names", [])
    if not disease_names:
        return False
    for name in disease_names:
        if str(name).lower() in answer_text:
            return True
    return False


def safe_fallback(message="I need more information to give a grounded recommendation."):
    base = message.strip()
    if "need more information" not in base.lower():
        base = f"I need more information. {base}"
    return base + " Please share the crop, the symptom details, and the conditions you are seeing."
