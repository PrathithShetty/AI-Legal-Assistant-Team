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
