"""Member 3 - legal references and case law: FR-14 to FR-16."""
from legal_assistant.references import find_references


def test_relevant_references_found(app):  # FR-14
    with app.test_request_context():
        titles = [r["title"] for r in find_references("criminal", "police refused to register my FIR")]
    assert "Lalita Kumari v. Government of Uttar Pradesh (2013)" in titles[:2]


def test_reference_details_present(app):  # FR-15
    with app.test_request_context():
        refs = find_references("cyber", "UPI fraud")
    assert refs
    for ref in refs:
        assert ref["title"] and ref["kind"] and ref["source"] and ref["description"]


def test_no_references_without_category(app):  # FR-16
    with app.test_request_context():
        assert find_references(None, "anything") == []


def test_references_limited(app):
    with app.test_request_context():
        assert len(find_references("family", "divorce", limit=3)) == 3


def test_references_page_filter_and_search(client):  # FR-15
    assert "Right to Information Act" in client.get("/references?category=rti").get_data(as_text=True)
    assert "Lalita Kumari" in client.get("/references?q=FIR").get_data(as_text=True)


def test_references_page_no_match_message(client):  # FR-16
    assert "No suitable legal reference" in client.get("/references?q=zzzz-nothing").get_data(as_text=True)
