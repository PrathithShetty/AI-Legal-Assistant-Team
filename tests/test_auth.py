"""Member 1 - registration and login: FR-01 to FR-04, NFR-07, NFR-11."""
from legal_assistant.auth import validate_registration
from legal_assistant.db import get_db

VALID = {"name": "Asha Rao", "email": "asha@example.test", "password": "secret123",
         "confirm_password": "secret123", "accept_disclaimer": "on"}


def test_register_creates_account_and_logs_in(client):  # FR-01
    response = client.register()
    assert response.status_code == 302
    assert "Hi, Asha" in client.get("/").get_data(as_text=True)


def test_validation_accepts_valid_input():  # FR-02
    assert validate_registration(VALID) == {}


def test_validation_rejects_bad_input():  # FR-02
    errors = validate_registration({"name": "A", "email": "not-an-email", "password": "short",
                                    "confirm_password": "different"})
    assert set(errors) == {"name", "email", "password", "confirm_password", "accept_disclaimer"}


def test_password_needs_letter_and_number():  # FR-02
    assert "password" in validate_registration(dict(VALID, password="abcdefgh", confirm_password="abcdefgh"))
    assert "password" in validate_registration(dict(VALID, password="12345678", confirm_password="12345678"))


def test_duplicate_email_rejected(client, make_client):  # FR-01
    client.register()
    response = make_client().register(email="ASHA@example.test")
    assert response.status_code == 400
    assert "already exists" in response.get_data(as_text=True)


def test_login_and_logout(client, make_client):  # FR-03
    client.register()
    other = make_client()
    assert other.login().status_code == 302
    assert "Hi, Asha" in other.get("/").get_data(as_text=True)
    other.logout()
    assert "Log in" in other.get("/").get_data(as_text=True)


def test_wrong_password_gives_generic_error(client, make_client):  # FR-03
    client.register()
    response = make_client().login(password="wrong-pass1")
    assert response.status_code == 401
    assert "Incorrect email or password" in response.get_data(as_text=True)


def test_password_is_hashed(app, client):  # NFR-11
    client.register()
    with app.app_context():
        stored = get_db().execute("SELECT password_hash FROM users WHERE email = ?", ("asha@example.test",)).fetchone()[0]
    assert stored != "secret123"
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_admin_can_log_in(client):  # FR-04
    assert client.login_admin().status_code == 302


def test_open_redirect_blocked(client):  # NFR-09
    client.register()
    client.logout()
    response = client.post("/login?next=//evil.example", data={"email": "asha@example.test", "password": "secret123"})
    assert "evil.example" not in response.headers["Location"]
