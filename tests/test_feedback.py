"""Member 4 - user feedback: FR-22."""
from legal_assistant.db import get_db


def test_feedback_api(client):  # FR-22
    response = client.post("/api/feedback", json={"rating": 5, "comment": "Very clear"})
    assert response.status_code == 200
    assert "Thank you" in response.get_json()["message"]


def test_feedback_validation(client):  # FR-22, NFR-14
    assert client.post("/api/feedback", json={"rating": 9}).status_code == 400
    assert client.post("/api/feedback", json={"rating": "abc"}).status_code == 400
    assert client.post("/api/feedback", json={"rating": 3, "comment": "x" * 1001}).status_code == 400


def test_feedback_form_page(client):  # FR-22
    response = client.post("/feedback", data={"rating": "4", "comment": "Good"}, follow_redirects=True)
    assert "Thank you for your feedback" in response.get_data(as_text=True)


def test_feedback_cannot_link_to_someone_elses_query(app, client, make_client):  # NFR-09
    client.register()
    query_id = client.ask("My landlord kept my deposit after I left").get_json()["query_id"]
    make_client().post("/api/feedback", json={"rating": 2, "query_id": query_id})
    with app.app_context():
        assert get_db().execute("SELECT query_id FROM feedback").fetchone()[0] is None
