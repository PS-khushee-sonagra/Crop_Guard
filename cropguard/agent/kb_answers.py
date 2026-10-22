from pathlib import Path
import json


def load_crop_data(crop):
    root = Path(__file__).resolve().parents[1]
    path = root / "knowledge" / f"{crop}.json"
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def answer_prevention(crop, question=None):
    data = load_crop_data(crop)
    prevention = data.get("prevention", [])
    if not prevention:
        return "General preventive practice: keep fields clean, avoid water stress, and monitor early symptoms."
    return "Prevention for " + crop + ": " + "; ".join(prevention[:3])


def answer_crop_list():
    return {
        "crops": ["tomato", "wheat", "cotton"],
        "message": "I cover tomato, wheat, and cotton diseases and management advice."
    }
