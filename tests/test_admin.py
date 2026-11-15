"""Member 4 - administration: FR-23 to FR-25, NFR-08."""
import json


def test_admin_dashboard(client):  # FR-23
    client.login_admin()
    page = client.get("/admin/").get_data(as_text=True)
    assert "Admin dashboard" in page and "Approved legal information" in page


def test_guests_redirected_from_admin(client):  # NFR-08
    assert client.get("/admin/").status_code == 302


def test_admin_pages_forbidden_for_normal_users(client):  # FR-04, NFR-08
    client.register()
    assert client.get("/admin/").status_code == 403
    assert client.post("/admin/categories/1/delete").status_code == 403


def test_admin_edits_legal_information(client):  # FR-23
    client.login_admin()
    response = client.post("/admin/categories/1/edit", data={
        "slug": "consumer", "name": "Consumer Protection", "description": "Updated description.",
        "keywords": "refund, toaster", "steps": "Step one\nStep two",
    })
    assert response.status_code == 302
    data = client.ask("My new toaster is broken and I want my money back").get_json()
    assert data["category"]["slug"] == "consumer"
    assert data["steps"] == ["Step one", "Step two"]


def test_admin_category_validation(client):  # FR-23, NFR-14
    client.login_admin()
    response = client.post("/admin/categories/new", data={"slug": "Bad Slug", "name": "", "description": "x",
                                                         "keywords": "x", "steps": "x"})
    page = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "lowercase letters" in page and "This field is required" in page


def test_duplicate_slug_rejected(client):  # FR-23
    client.login_admin()
    response = client.post("/admin/categories/new", data={"slug": "consumer", "name": "Copy", "description": "x",
                                                         "keywords": "x", "steps": "x"})
    assert response.status_code == 400
    assert "already used" in response.get_data(as_text=True)


# --- Sprint 2: references, templates and feedback review (FR-24, FR-25) ---

def test_admin_adds_reference_and_template(client):  # FR-24
    client.login_admin()
    assert client.post("/admin/references/new", data={
        "title": "Test Act, 2024", "category": "rti", "kind": "Act", "source": "India Code",
        "description": "Test description.", "url": "https://www.indiacode.nic.in",
    }).status_code == 302
    assert "Test Act, 2024" in client.get("/references").get_data(as_text=True)

    fields = json.dumps([{"name": "who", "label": "Name", "type": "text"}])
    assert client.post("/admin/templates/new", data={
        "slug": "test-template", "name": "Test Template", "category": "general",
        "description": "Purpose.", "fields": fields, "content": "Hello {{who}}",
    }).status_code == 302
    assert "Hello Asha" in client.post("/templates/test-template", data={"who": "Asha"}).get_data(as_text=True)


def test_admin_template_validation(client):  # FR-24, NFR-14
    client.login_admin()
    response = client.post("/admin/templates/new", data={
        "slug": "ok-slug", "name": "X", "category": "nowhere", "description": "x", "fields": "not json", "content": "x",
    })
    page = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Invalid JSON" in page and "valid option" in page


def test_admin_rejects_javascript_links(client):  # NFR-09
    client.login_admin()
    response = client.post("/admin/references/new", data={
        "title": "X", "category": "rti", "kind": "Act", "source": "Y", "description": "Z", "url": "javascript:alert(1)",
    })
    assert response.status_code == 400


def test_admin_deletes_item(client):  # FR-24
    client.login_admin()
    client.post("/admin/references/1/delete")
    assert "Consumer Protection Act, 2019" not in client.get("/references").get_data(as_text=True)


def test_admin_reviews_feedback(client):  # FR-25
    client.post("/api/feedback", json={"rating": 2, "comment": "Answer was confusing"})
    client.login_admin()
    assert "Answer was confusing" in client.get("/admin/feedback").get_data(as_text=True)
    client.post("/admin/feedback/1/review")
    assert "Answer was confusing" not in client.get("/admin/feedback?show=new").get_data(as_text=True)
    assert "Answer was confusing" in client.get("/admin/feedback?show=all").get_data(as_text=True)
