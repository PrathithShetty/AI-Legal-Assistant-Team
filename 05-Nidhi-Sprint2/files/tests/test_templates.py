"""Member 3 - legal document templates: FR-17 to FR-19."""
from legal_assistant.doc_templates import fill_template


def test_templates_listed_with_purpose(client):  # FR-17, FR-18
    page = client.get("/templates").get_data(as_text=True)
    assert "RTI Application" in page
    assert "Rental Agreement" in page
    assert "Use this to ask a government office" in page


def test_template_detail_shows_purpose_and_form(client):  # FR-18, FR-19
    page = client.get("/templates/rti-application").get_data(as_text=True)
    assert "What is this for?" in page
    assert 'name="applicant_name"' in page


def test_generate_template(client):  # FR-19
    response = client.post("/templates/rti-application", data={"applicant_name": "Asha Rao", "information": "Status of my pension"})
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "I, Asha Rao, residing at" in page
    assert "Status of my pension" in page
    assert "[Office / department name and address]" in page


def test_fill_template_keeps_placeholders():
    fields = [{"name": "a", "label": "Field A"}, {"name": "b", "label": "Field B"}]
    assert fill_template("{{a}} and {{ b }}", fields, {"a": "x"}) == "x and [Field B]"


def test_generated_output_is_html_escaped(client):  # NFR-09
    page = client.post("/templates/rti-application", data={"applicant_name": "<script>alert(1)</script>"}).get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_unknown_template_404(client):
    assert client.get("/templates/does-not-exist").status_code == 404
