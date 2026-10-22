import re


def normalize_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def classify_intent(message):
    text = normalize_text(message)
    if not text:
        return "vague"
    if re.search(r"\b(hi|hello|hey|good morning|help|what can you do)\b", text):
        return "greeting"
    if re.search(r"\b(prevent|prevention|protect|avoid|manage|control|practice)\b", text):
        return "prevention"
    if re.search(r"\b(list|show|which crops|issues|diseases|pests)\b", text):
        return "list"
    if re.search(r"\b(spot|spots|yellow|brown|wilting|ring|rots?|rust|blight|mildew|lesion|curl|holes?|symptom|disease)\b", text):
        return "diagnosis"
    return "vague"
