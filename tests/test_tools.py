from cropguard.mcp_server.tools.knowledge import search_pest_disease, get_crop_info, get_ipm_guidance


def test_get_crop_info_returns_supported_crop():
    result = get_crop_info("tomato")
    assert result["status"] == "ok"
    assert "tomato" in result["crop"].lower()
    assert len(result["issues"]) >= 1


def test_search_pest_disease_ranks_known_symptoms():
    result = search_pest_disease("tomato", ["dark rings", "yellow edges", "leaf spot"])
    assert result["status"] == "ok"
    assert result["matches"][0]["issue_id"] in {"early_blight", "septoria_leaf_spot"}


def test_get_ipm_guidance_returns_steps_for_issue():
    result = get_ipm_guidance("tomato", "early_blight")
    assert result["status"] == "ok"
    assert "steps" in result
    assert any("remove" in step.lower() or "mulch" in step.lower() for step in result["steps"])


def test_vague_symptoms_produce_not_found():
    result = search_pest_disease("tomato", ["issue"])
    assert result["status"] in {"not_found", "error"}
