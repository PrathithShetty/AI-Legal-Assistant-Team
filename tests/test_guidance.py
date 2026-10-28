"""Member 3 - case guidance and recommendations: FR-12, FR-13, NFR-06."""
import json

from legal_assistant import guidance
from legal_assistant.db import KNOWLEDGE_DIR

CATEGORIES = json.loads((KNOWLEDGE_DIR / "categories.json").read_text(encoding="utf-8"))


def test_every_category_has_procedure_steps():  # FR-12
    for c in CATEGORIES:
        steps = guidance.procedure_steps({**c, "steps": json.dumps(c["steps"])})
        assert len(steps) >= 3, c["slug"]
    assert guidance.procedure_steps(None) == []


def test_serious_matters_flag_professional_help():  # FR-13
    needed, reasons = guidance.professional_help("I received a court summons yesterday", None)
    assert needed and reasons


def test_category_can_require_lawyer():  # FR-13
    needed, reasons = guidance.professional_help("question about family", {"name": "Family & Marriage", "needs_lawyer": 1})
    assert needed and "Family & Marriage" in reasons[0]


def test_simple_matters_not_flagged():  # FR-13
    needed, _ = guidance.professional_help("my refund is pending", {"name": "Consumer Protection", "needs_lawyer": 0})
    assert not needed


def test_reasons_are_not_repeated():  # FR-13
    _, reasons = guidance.professional_help("I was arrested and need bail", None)
    assert len(reasons) == len(set(reasons)) == 1


def test_lawyer_message_includes_legal_aid():  # NFR-06
    message = guidance.lawyer_message(["Arrest and bail matters need a lawyer quickly."])
    assert "15100" in message["advice"]
    assert guidance.lawyer_message([]) is None


def test_emergency_and_self_harm_notices():  # NFR-06
    assert any("112" in n for n in guidance.emergency_notices("my husband is beating me"))
    assert any("14416" in n for n in guidance.emergency_notices("i want to end my life"))
    assert guidance.emergency_notices("my refund is late") == []
