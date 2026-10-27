"""Member 1 - cases, dashboard and profile: FR-20, FR-21, NFR-07, NFR-09, extras EX-01 and EX-02.

Cases are saved straight into the database here, so these tests do not depend on the question module.
The end-to-end test at the bottom runs once the question module (Member 2) is installed.
"""
import importlib.util
import json

import pytest

from legal_assistant.db import get_db
from legal_assistant.disclaimer import DISCLAIMER

CATEGORY_NAMES = {"property": "Property & Tenancy", "employment": "Employment & Labour"}


def _save_case(app, question="My landlord kept my deposit after I left", category="property", email="asha@example.test"):
    """Store a saved question (case) for the user, in the same format the question API uses (FR-20)."""
    response = {
        "question": question,
        "summary": "General information about this issue.",
        "source": "knowledge-base",
        "category": {"slug": category, "name": CATEGORY_NAMES[category]},
        "steps": ["Collect your documents.", "Raise the issue in writing."],
        "references": [],
        "no_reference_message": "No suitable legal reference was found for this question in our approved sources.",
        "professional_help": None,
        "emergency": [],
        "disclaimer": DISCLAIMER,
    }
    with app.app_context():
        db = get_db()
        user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]
        cur = db.execute("INSERT INTO queries (user_id, query_text, category, response) VALUES (?, ?, ?, ?)",
                         (user_id, question, category, json.dumps(response)))
        db.commit()
        return cur.lastrowid


def test_cases_and_dashboard_require_login(client):  # NFR-07
    for url in ("/history", "/dashboard", "/profile"):
        response = client.get(url)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_login_redirects_to_dashboard(client, make_client):
    client.register()
    assert make_client().login().headers["Location"] == "/dashboard"


def test_case_list_shows_own_questions(app, client):  # FR-20, FR-21
    client.register()
    _save_case(app)
    page = client.get("/history").get_data(as_text=True)
    assert "My landlord kept my deposit" in page
    assert "Property &amp; Tenancy" in page


def test_case_detail_shows_saved_answer(app, client):  # FR-21
    client.register()
    page = client.get(f"/history/{_save_case(app)}").get_data(as_text=True)
    assert "Property &amp; Tenancy" in page
    assert "Collect your documents." in page
    assert "not legal advice" in page


def test_empty_case_list(client):  # FR-21
    client.register()
    assert "You have no cases yet" in client.get("/history").get_data(as_text=True)


def test_users_cannot_see_each_others_cases(app, client, make_client):  # NFR-09
    client.register()
    query_id = _save_case(app)
    other = make_client()
    other.register(name="Ravi Kumar", email="ravi@example.test")
    assert other.get(f"/history/{query_id}").status_code == 404
    assert "My landlord kept" not in other.get("/history").get_data(as_text=True)


def test_dashboard_shows_counts_and_recent_cases(app, client):  # EX-02
    client.register()
    _save_case(app)
    _save_case(app, "My employer has not paid my salary for two months", "employment")
    page = client.get("/dashboard").get_data(as_text=True)
    assert "Welcome, Asha" in page
    assert "My employer has not paid" in page
    assert "Employment &amp; Labour" in page


def test_mark_case_resolved_and_reopen(app, client):  # EX-01
    client.register()
    query_id = _save_case(app)
    assert "Mark as resolved" in client.get(f"/history/{query_id}").get_data(as_text=True)
    client.post(f"/history/{query_id}/status", data={"status": "resolved"})
    assert "Reopen case" in client.get(f"/history/{query_id}").get_data(as_text=True)
    assert "My landlord kept" in client.get("/history?status=resolved").get_data(as_text=True)
    assert "My landlord kept" not in client.get("/history?status=open").get_data(as_text=True)
    client.post(f"/history/{query_id}/status", data={"status": "open"})
    assert "Mark as resolved" in client.get(f"/history/{query_id}").get_data(as_text=True)


def test_invalid_status_rejected(app, client):  # EX-01
    client.register()
    assert client.post(f"/history/{_save_case(app)}/status", data={"status": "deleted"}).status_code == 400


def test_cannot_change_someone_elses_case(app, client, make_client):  # NFR-09
    client.register()
    query_id = _save_case(app)
    other = make_client()
    other.register(name="Ravi Kumar", email="ravi@example.test")
    assert other.post(f"/history/{query_id}/status", data={"status": "resolved"}).status_code == 404
    assert "Mark as resolved" in client.get(f"/history/{query_id}").get_data(as_text=True)


def test_profile_update_name(client):  # EX-02
    client.register()
    response = client.post("/profile", data={"action": "details", "name": "Asha R. Rao"}, follow_redirects=True)
    assert "Your profile was updated" in response.get_data(as_text=True)
    assert client.post("/profile", data={"action": "details", "name": "A"}).status_code == 400


def test_change_password(client, make_client):  # EX-02, NFR-11
    client.register()
    assert client.post("/profile", data={"action": "password", "current_password": "wrong-pass1",
                                         "new_password": "newpass123", "confirm_password": "newpass123"}).status_code == 400
    assert client.post("/profile", data={"action": "password", "current_password": "secret123",
                                         "new_password": "short", "confirm_password": "short"}).status_code == 400
    response = client.post("/profile", data={"action": "password", "current_password": "secret123",
                                             "new_password": "newpass123", "confirm_password": "newpass123"})
    assert response.status_code == 302
    other = make_client()
    assert other.login(password="secret123").status_code == 401
    assert other.login(password="newpass123").status_code == 302


@pytest.mark.skipif(importlib.util.find_spec("legal_assistant.query") is None,
                    reason="needs the question module (Member 2)")
def test_question_asked_appears_in_my_cases(client):  # FR-20, FR-21 end to end
    client.register()
    query_id = client.ask("My landlord kept my deposit after I left").get_json()["query_id"]
    page = client.get(f"/history/{query_id}").get_data(as_text=True)
    assert "Property &amp; Tenancy" in page
