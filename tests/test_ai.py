"""Member 2 - AI-written summary with safe fallback: FR-07, NFR-05, NFR-14."""
from unittest.mock import patch

from legal_assistant import ai


def test_ai_summary_used_when_enabled(app, client):  # FR-07
    app.config["AI_ENABLED"] = True
    with patch.object(ai, "ai_summary", return_value="AI written summary.") as mocked:
        data = client.ask("My landlord kept my deposit after I left").get_json()
    mocked.assert_called_once()
    assert data["summary"] == "AI written summary."
    assert data["source"] == "ai"


def test_falls_back_when_ai_fails(app, client):  # NFR-14
    app.config["AI_ENABLED"] = True
    with patch.object(ai, "ai_summary", side_effect=ai.AIUnavailable("timeout")):
        data = client.ask("My landlord kept my deposit after I left").get_json()
    assert data["source"] == "knowledge-base"
    assert data["summary"]


def test_prompt_contains_only_approved_information():  # FR-07, NFR-05
    category = {"name": "Consumer Protection", "description": "Problems with products."}
    prompt = ai.build_prompt("Refund refused", category, ["Write to the seller."],
                             [{"title": "Consumer Protection Act, 2019", "description": "Consumer rights."}])
    assert "Consumer Protection Act, 2019" in prompt
    assert "Write to the seller." in prompt


def test_system_prompt_safety_rules():  # NFR-05, BR-01, BR-02
    assert "guaranteed" in ai.SYSTEM_PROMPT
    assert "Bharatiya Nyaya Sanhita" in ai.SYSTEM_PROMPT
    assert "consult a qualified advocate" in ai.SYSTEM_PROMPT
