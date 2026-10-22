import re

ALLOWED_CROPS = {"tomato", "wheat", "cotton"}


def sanitize_crop(value):
    if value is None:
        return "", False
    crop = str(value).strip().lower()
    if not crop:
        return "", False
    crop = crop.replace(" ", "_")
    if re.search(r"[^a-z0-9_\-]", crop):
        return "", False
    if crop not in ALLOWED_CROPS:
        return crop, False
    return crop, True


def sanitize_symptoms(value):
    if value is None:
        return [], False
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        return [], False

    cleaned = []
    for item in values:
        text = str(item).strip()
        if not text:
            continue
        cleaned.append(text)

    if not cleaned:
        return [], False
    return cleaned, True
