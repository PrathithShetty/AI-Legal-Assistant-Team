"""Member 2 - legal query and structured response: FR-05 to FR-09, FR-11, FR-13 to FR-16 (via API), FR-20, NFR-01, NFR-04, NFR-14."""
from legal_assistant.query import validate_query


def test_submit_question_returns_structured_response(client):  # FR-05, FR-07, FR-08
    response = client.ask("I ordered a phone online and got a damaged product. The seller refuses a refund.")
    assert response.status_code == 200
    data = response.get_json()
    for key in ("summary", "category", "steps", "references", "professional_help", "emergency", "disclaimer"):
        assert key in data
    assert data["summary"]
    assert data["source"] == "knowledge-base"


def test_category_is_returned(client):  # FR-11
    data = client.ask("My employer has not paid my salary for two months").get_json()
    assert data["category"] == {"slug": "employment", "name": "Employment & Labour"}


def test_disclaimer_always_present(client):  # FR-09, NFR-04
    for question in ("My landlord kept my deposit after I left", "what is the weather today in delhi"):
        assert "not legal advice" in client.ask(question).get_json()["disclaimer"]


def test_validate_query_rules():  # FR-06
    assert validate_query("", 2000)
    assert validate_query("   ", 2000)
    assert validate_query("hi", 2000)
    assert validate_query("12345 67890 !!!", 2000)
    assert validate_query("x" * 2001, 2000)
    assert validate_query("My landlord kept my deposit", 2000) is None


def test_invalid_query_returns_400(client):  # FR-06, NFR-14
    response = client.ask("  ")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_missing_body_is_handled(client):  # NFR-14
    assert client.post("/api/query", json={}).status_code == 400


def test_unsupported_question_handled_gracefully(client):  # NFR-14
    data = client.ask("Which football team will win the match tomorrow?").get_json()
    assert data["category"] is None
    assert "could not match" in data["summary"]
    assert data["no_reference_message"]


def test_lawyer_notice_in_response(client):  # FR-13
    data = client.ask("I was arrested by the police yesterday, how do I get bail?").get_json()
    assert data["professional_help"]["reasons"]


def test_references_in_response(client):  # FR-14, FR-15
    data = client.ask("Someone stole my phone and the police refused to register an FIR").get_json()
    assert data["references"]
    for ref in data["references"]:
        assert ref["title"] and ref["kind"] and ref["source"] and ref["description"]


def test_guest_queries_not_stored(client):  # FR-20
    assert client.ask("My landlord kept my deposit after I left").get_json()["query_id"] is None


def test_registered_user_queries_stored(client):  # FR-20
    client.register()
    assert isinstance(client.ask("My landlord kept my deposit after I left").get_json()["query_id"], int)


def test_response_time_reported(client):  # NFR-01
    assert client.ask("My landlord kept my deposit after I left").get_json()["elapsed_ms"] < 2000


def test_home_page_has_question_form(client):  # FR-05
    page = client.get("/").get_data(as_text=True)
    assert 'id="ask-form"' in page and "Try an example" in page
