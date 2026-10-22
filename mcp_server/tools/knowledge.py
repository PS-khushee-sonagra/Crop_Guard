import json
import re
from pathlib import Path

from cropguard.mcp_server.validation import sanitize_crop, sanitize_symptoms


def _load_crop_data(crop):
    if not crop:
        return None
    root = Path(__file__).resolve().parents[2]
    file_path = root / "knowledge" / f"{crop}.json"
    if not file_path.exists():
        return None
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_crop_info(crop):
    crop_name, ok = sanitize_crop(crop)
    if not ok:
        return {"status": "error", "message": "Crop is missing or unsupported."}
    data = _load_crop_data(crop_name)
    if not data:
        return {"status": "not_found", "crop": crop_name, "message": "No crop knowledge available."}
    return {
        "status": "ok",
        "crop": crop_name,
        "issues": [issue["name"] for issue in data.get("issues", [])],
    }


def _tokenize(text):
    if not text:
        return set()
    return {token for token in re.findall(r"[a-z0-9]+", str(text).lower()) if token and token not in {"and", "the", "with", "from", "into", "over", "under"}}


def search_pest_disease(crop, symptoms):
    crop_name, ok = sanitize_crop(crop)
    if not ok:
        return {"status": "error", "message": "Crop is missing or unsupported."}

    cleaned, ok = sanitize_symptoms(symptoms)
    if not ok:
        return {"status": "error", "message": "Symptoms are required."}

    data = _load_crop_data(crop_name)
    if not data:
        return {"status": "not_found", "crop": crop_name, "message": "No crop knowledge file found."}

    symptom_tokens = set()
    for item in cleaned:
        symptom_tokens.update(_tokenize(item))

    matches = []
    for issue in data.get("issues", []):
        issue_tokens = set()
        issue_text = " ".join([issue.get("name", ""), *issue.get("symptoms", [])])
        issue_tokens.update(_tokenize(issue_text))
        score = 0
        for token in symptom_tokens:
            if token in issue_tokens:
                score += 2
        if score <= 0:
            continue
        matches.append(
            {
                "issue_id": issue["id"],
                "name": issue["name"],
                "score": score,
                "lookalikes": issue.get("lookalikes", []),
                "favorable_conditions": issue.get("favorable_conditions", [])[:2],
            }
        )

    if not matches:
        return {"status": "not_found", "crop": crop_name, "message": "No disease match for the provided symptoms."}

    ranked = sorted(matches, key=lambda item: item["score"], reverse=True)
    return {"status": "ok", "crop": crop_name, "matches": ranked[:3]}


def get_ipm_guidance(crop, issue_id):
    crop_name, ok = sanitize_crop(crop)
    if not ok:
        return {"status": "error", "message": "Crop is missing or unsupported."}
    data = _load_crop_data(crop_name)
    if not data:
        return {"status": "not_found", "crop": crop_name, "message": "No crop knowledge file found."}

    for issue in data.get("issues", []):
        if issue["id"] == issue_id:
            return {
                "status": "ok",
                "crop": crop_name,
                "issue_id": issue_id,
                "issue_name": issue["name"],
                "steps": issue.get("ipm_steps", []),
                "sources": issue.get("sources", []),
            }

    return {"status": "not_found", "crop": crop_name, "issue_id": issue_id, "message": "Issue not found in crop knowledge."}
