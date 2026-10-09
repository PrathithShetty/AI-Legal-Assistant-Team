"""Project skeleton: app start-up, database, knowledge base and security basics (T-01, T-02, NFR-09, NFR-10, NFR-14)."""
import json
import re
import sqlite3

from legal_assistant import create_app
from legal_assistant.db import get_db, migrate


def test_home_page_loads_with_disclaimer(client):  # NFR-04
    page = client.get("/").get_data(as_text=True)
    assert "not legal advice" in page


def test_knowledge_base_is_seeded(app):
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM categories").fetchone()[0] >= 7
        assert db.execute("SELECT COUNT(*) FROM legal_references").fetchone()[0] >= 20
        assert db.execute("SELECT COUNT(*) FROM doc_templates").fetchone()[0] >= 5


def test_seeded_templates_use_only_defined_fields(app):
    with app.app_context():
        for row in get_db().execute("SELECT fields, content FROM doc_templates"):
            names = {f["name"] for f in json.loads(row["fields"])}
            used = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", row["content"]))
            assert used <= names, f"template uses undefined fields: {used - names}"


def test_admin_account_created_from_config(app):  # FR-04
    with app.app_context():
        row = get_db().execute("SELECT role FROM users WHERE email = 'admin@example.test'").fetchone()
    assert row["role"] == "admin"


def test_migration_adds_case_status_column(tmp_path):
    db = sqlite3.connect(tmp_path / "old.db")
    db.execute("CREATE TABLE queries (id INTEGER PRIMARY KEY, user_id INTEGER, query_text TEXT, category TEXT, "
               "response TEXT, created_at TEXT)")
    db.execute("INSERT INTO queries (user_id, query_text, response) VALUES (1, 'q', '{}')")
    migrate(db)
    assert db.execute("SELECT status FROM queries").fetchone()[0] == "open"
    db.close()


def test_csrf_required_for_unsafe_requests(app):  # NFR-09
    response = app.test_client().post("/", data={"anything": "1"})
    assert response.status_code == 400


def test_security_headers(client):  # NFR-09
    headers = client.get("/").headers
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"


def test_https_redirect_when_forced(tmp_path):  # NFR-10
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "h.db"), "FORCE_HTTPS": True, "AI_ENABLED": False})
    response = app.test_client().get("/")
    assert response.status_code == 301
    assert response.headers["Location"].startswith("https://")


def test_friendly_404_page(client):  # NFR-14
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert "Page not found" in response.get_data(as_text=True)
