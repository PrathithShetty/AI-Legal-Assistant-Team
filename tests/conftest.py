import pytest

from legal_assistant import create_app

CSRF = "test-csrf-token"
ADMIN_EMAIL = "admin@example.test"
ADMIN_PASSWORD = "admin-pass-123"


@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db"),
        "SECRET_KEY": "test-secret",
        "AI_ENABLED": False,
        "ADMIN_EMAIL": ADMIN_EMAIL,
        "ADMIN_PASSWORD": ADMIN_PASSWORD,
    })


class Client:
    """Wraps the Flask test client and adds the CSRF token to every unsafe request."""

    def __init__(self, flask_client):
        self.c = flask_client

    def get(self, *args, **kwargs):
        return self.c.get(*args, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        # Login/logout clear the session (and its token), like a real browser that then reloads the page.
        with self.c.session_transaction() as s:
            s["csrf_token"] = CSRF
        if json is not None:
            return self.c.post(url, json=json, headers={"X-CSRF-Token": CSRF}, **kwargs)
        data = dict(data or {}, csrf_token=CSRF)
        return self.c.post(url, data=data, **kwargs)

    def register(self, name="Asha Rao", email="asha@example.test", password="secret123"):
        return self.post("/register", data={
            "name": name, "email": email, "password": password, "confirm_password": password,
            "accept_disclaimer": "on",
        })

    def login(self, email="asha@example.test", password="secret123"):
        return self.post("/login", data={"email": email, "password": password})

    def login_admin(self):
        return self.login(ADMIN_EMAIL, ADMIN_PASSWORD)

    def logout(self):
        return self.post("/logout")

    def ask(self, question):
        return self.post("/api/query", json={"question": question})


@pytest.fixture
def client(app):
    return Client(app.test_client())


@pytest.fixture
def make_client(app):
    return lambda: Client(app.test_client())
