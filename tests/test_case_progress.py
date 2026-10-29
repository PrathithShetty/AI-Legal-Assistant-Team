
"""Tests for Issue #49: case progress and document checklist."""

import json

from legal_assistant.db import execute, query_one


def create_saved_case(client, question="My landlord is not returning my security deposit after I vacated the flat."):
    """Register a user and create a saved legal case."""
    client.register()
    response = client.ask(question)
    assert response.status_code == 200
    query_id = response.get_json()["query_id"]
    assert query_id is not None
    return query_id


def test_case_progress_page_shows_steps_and_documents(client):
    query_id = create_saved_case(client)

    response = client.get(f"/cases/{query_id}/progress")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Procedure steps" in page
    assert "Document checklist" in page
    assert "0 of" in page


def test_step_completion_is_saved(client, app):
    query_id = create_saved_case(client)

    response = client.post(
        f"/cases/{query_id}/progress",
        data={
            "item_type": "step",
            "item_key": "0",
            "completed": "1",
        },
    )
    assert response.status_code == 302

    with app.app_context():
        saved = query_one(
            "SELECT completed FROM case_step_progress "
            "WHERE query_id = ? AND step_index = 0",
            (query_id,),
        )
    assert saved["completed"] == 1


def test_document_prepared_status_is_saved(client, app):
    query_id = create_saved_case(client)

    response = client.post(
        f"/cases/{query_id}/progress",
        data={
            "item_type": "document",
            "item_key": "Rent or lease agreement",
            "completed": "1",
        },
    )
    assert response.status_code == 302

    with app.app_context():
        saved = query_one(
            "SELECT prepared FROM case_documents "
            "WHERE query_id = ? AND document_name = ?",
            (query_id, "Rent or lease agreement"),
        )
    assert saved["prepared"] == 1


def test_user_cannot_view_another_users_case(client, make_client):
    query_id = create_saved_case(client)
    other = make_client()
    other.register(name="Ravi Kumar", email="ravi@example.test")

    response = other.get(f"/cases/{query_id}/progress")

    assert response.status_code == 404


def test_user_cannot_update_another_users_case(client, make_client, app):
    query_id = create_saved_case(client)
    other = make_client()
    other.register(name="Ravi Kumar", email="ravi@example.test")

    response = other.post(
        f"/cases/{query_id}/progress",
        data={
            "item_type": "step",
            "item_key": "0",
            "completed": "1",
        },
    )
    assert response.status_code == 404

    with app.app_context():
        saved = query_one(
            "SELECT COUNT(*) AS total FROM case_step_progress WHERE query_id = ?",
            (query_id,),
        )
    assert saved["total"] == 0


def test_guest_cannot_access_case_progress(client):
    response = client.get("/cases/1/progress")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_invalid_step_index_is_rejected(client):
    query_id = create_saved_case(client)

    response = client.post(
        f"/cases/{query_id}/progress",
        data={
            "item_type": "step",
            "item_key": "999",
            "completed": "1",
        },
    )
    assert response.status_code == 400


def test_unknown_document_is_rejected(client):
    query_id = create_saved_case(client)

    response = client.post(
        f"/cases/{query_id}/progress",
        data={
            "item_type": "document",
            "item_key": "Unknown document",
            "completed": "1",
        },
    )
    assert response.status_code == 400
